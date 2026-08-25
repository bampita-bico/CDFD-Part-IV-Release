#!/usr/bin/env python3
"""Run the frozen one-site hydrology held-out comparison from ANALYSIS_REGISTRATION.md."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_PATH = DATA_DIR / "usgs_01646500_daily_discharge_2010_2024.json"
CLEAN_PATH = DATA_DIR / "usgs_01646500_daily_discharge_2010_2024.csv"
RESULT_PATH = ROOT / "HELDOUT_RESULTS.md"
URL = (
    "https://waterservices.usgs.gov/nwis/dv/?format=json&sites=01646500"
    "&parameterCd=00060&statCd=00003&startDT=2010-01-01&endDT=2024-12-31"
)
TRAIN_END = pd.Timestamp("2021-12-31")
TEST_START = pd.Timestamp("2022-01-01")
SEED = 20260818
BOOTSTRAPS = 2000
BLOCK = 14


def download_raw() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with urlopen(URL, timeout=90) as response:
        payload = response.read()
    RAW_PATH.write_bytes(payload)


def load_discharge() -> pd.DataFrame:
    payload = json.loads(RAW_PATH.read_text())
    series = payload["value"]["timeSeries"]
    if len(series) != 1:
        raise RuntimeError(f"Expected one time series, received {len(series)}")
    values = series[0]["values"][0]["value"]
    frame = pd.DataFrame(values)
    frame["date"] = pd.to_datetime(frame["dateTime"]).dt.tz_localize(None).dt.normalize()
    frame["discharge_cfs"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.loc[frame["discharge_cfs"].notna(), ["date", "discharge_cfs"]]
    frame = frame.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    expected = pd.date_range("2010-01-01", "2024-12-31", freq="D")
    frame = frame.set_index("date").reindex(expected)
    frame.index.name = "date"
    if frame["discharge_cfs"].isna().any():
        missing = int(frame["discharge_cfs"].isna().sum())
        raise RuntimeError(f"Daily record has {missing} missing dates; no imputation is allowed.")
    if (frame["discharge_cfs"] < 0).any():
        raise RuntimeError("Negative discharge values are invalid for this analysis.")
    frame = frame.reset_index()
    frame.to_csv(CLEAN_PATH, index=False)
    return frame


def make_features(discharge: pd.DataFrame) -> pd.DataFrame:
    frame = discharge.copy()
    frame["log_q"] = np.log1p(frame["discharge_cfs"])
    for lag in range(7):
        frame[f"log_q_lag_{lag}"] = frame["log_q"].shift(lag)
    frame["sin_doy"] = np.sin(2 * np.pi * frame["date"].dt.dayofyear / 365.25)
    frame["cos_doy"] = np.cos(2 * np.pi * frame["date"].dt.dayofyear / 365.25)
    frame["phi_proxy"] = frame["log_q"]
    frame["s_proxy"] = frame["log_q"].diff().abs()
    frame["m_proxy"] = frame["log_q"].rolling(7, min_periods=7).mean()
    c_proxy = frame.loc[frame["date"] <= TRAIN_END, "log_q"].quantile(0.95)
    frame["c_proxy"] = c_proxy
    frame["psi_proxy"] = (frame["phi_proxy"] / c_proxy) * (1 + frame["s_proxy"]) * frame["m_proxy"]
    frame["target"] = frame["log_q"].shift(-1)
    return frame.dropna().reset_index(drop=True)


def moving_block_ci(loss_delta: np.ndarray) -> tuple[float, float, float]:
    rng = np.random.default_rng(SEED)
    n = len(loss_delta)
    starts = np.arange(n - BLOCK + 1)
    draws = np.empty(BOOTSTRAPS)
    blocks_needed = int(np.ceil(n / BLOCK))
    for i in range(BOOTSTRAPS):
        picked = rng.choice(starts, size=blocks_needed, replace=True)
        indices = np.concatenate([np.arange(start, start + BLOCK) for start in picked])[:n]
        draws[i] = loss_delta[indices].mean()
    return float(loss_delta.mean()), float(np.quantile(draws, 0.05)), float(np.quantile(draws, 0.95))


def fit_predict(train: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> np.ndarray:
    model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    model.fit(train[features], train["target"])
    return model.predict(test[features])


def metrics(y: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    return {
        "rmse": float(np.sqrt(mean_squared_error(y, prediction))),
        "mae": float(mean_absolute_error(y, prediction)),
        "r2": float(r2_score(y, prediction)),
    }


def render_report(raw_digest: str, source: pd.DataFrame, frame: pd.DataFrame, baseline: dict[str, float], extension: dict[str, float], mean: float, lower: float, upper: float) -> str:
    reduction = 100 * (baseline["rmse"] - extension["rmse"]) / baseline["rmse"]
    passes = reduction >= 1 and lower > 0
    verdict = "DEMONSTRATED" if passes else "NOT DEMONSTRATED"
    conclusion = (
        "The predeclared CDFD/AFL extension clears both decision criteria on this one-site held-out record."
        if passes else
        "The predeclared CDFD/AFL extension does not clear the held-out decision rule; this analysis supplies no evidence of predictive value beyond the native baseline."
    )
    return f"""# Hydrology Held-Out Results

**Run date:** 2026-08-18  
**Verdict:** **{verdict}**

## Locked analysis

The specification is frozen in [ANALYSIS_REGISTRATION.md](ANALYSIS_REGISTRATION.md).
The raw USGS response was downloaded after that file was created, saved locally,
and hashed as `{raw_digest}`. The analysis has no external timestamped
preregistration; it is a same-session, reproducible analysis registration.

* USGS site: `01646500` (Potomac River near Washington, DC)
* Source daily values: {len(source)} from {source['date'].min().date()} to {source['date'].max().date()}
* Feature-ready training rows: {int((frame['date'] <= TRAIN_END).sum())}; held-out rows: {int((frame['date'] >= TEST_START).sum())}
* Target: next-day `log1p(discharge_cfs)`
* Evaluation: chronological 2022-01-01 through 2024-12-30 holdout

## Held-Out metrics

| Model | RMSE | MAE | R-squared |
| --- | ---: | ---: | ---: |
| Native lagged-discharge + season baseline | {baseline['rmse']:.6f} | {baseline['mae']:.6f} | {baseline['r2']:.6f} |
| Baseline + frozen CDFD/AFL transformations | {extension['rmse']:.6f} | {extension['mae']:.6f} | {extension['r2']:.6f} |

The CDFD/AFL extension changes held-out RMSE by **{reduction:.3f}%** (positive
means lower error). The 14-day moving-block bootstrap mean reduction in
squared error is `{mean:.8f}`, with a one-sided 95% lower bound of
`{lower:.8f}` and upper 95% quantile of `{upper:.8f}`.

## Decision

The predeclared improvement criterion requires at least 1% lower held-out RMSE
and a positive one-sided 95% bootstrap lower bound for mean squared-error
reduction. **{conclusion}**

## Interpretation boundary

This test does not measure precipitation, channel capacity, floodplain
storage, or geomorphic memory. Its `C`, `S`, and `M_s` labels are explicitly
limited statistical proxies defined in the registration. The native baseline
already has seven discharge lags and seasonal structure; failure to improve is
the expected result if the added composite is merely a re-expression of those
features. A positive one-site result would still require out-of-basin
replication and comparison with hydrologic rainfall-runoff models before any
mechanistic claim.

## Reproduce

```bash
/home/bampita/Projects/CDFD/.venv/bin/python \\
  Part_A_Earth_Systems/empirical_hydrology_study/run_heldout_test.py
```
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Fetch and freeze the public USGS response.")
    args = parser.parse_args()
    if args.download:
        download_raw()
    if not RAW_PATH.exists():
        raise SystemExit(f"Raw response missing: rerun with --download ({RAW_PATH})")
    discharge = load_discharge()
    frame = make_features(discharge)
    train = frame.loc[frame["date"] <= TRAIN_END].copy()
    test = frame.loc[frame["date"] >= TEST_START].copy()
    if train.empty or test.empty:
        raise RuntimeError("The frozen date split created an empty training or test set.")
    native_features = [f"log_q_lag_{lag}" for lag in range(7)] + ["sin_doy", "cos_doy"]
    extension_features = native_features + ["phi_proxy", "s_proxy", "m_proxy", "psi_proxy"]
    y_test = test["target"].to_numpy()
    baseline_prediction = fit_predict(train, test, native_features)
    extension_prediction = fit_predict(train, test, extension_features)
    baseline_metrics = metrics(y_test, baseline_prediction)
    extension_metrics = metrics(y_test, extension_prediction)
    loss_delta = (y_test - baseline_prediction) ** 2 - (y_test - extension_prediction) ** 2
    mean, lower, upper = moving_block_ci(loss_delta)
    digest = hashlib.sha256(RAW_PATH.read_bytes()).hexdigest()
    RESULT_PATH.write_text(render_report(digest, discharge, frame, baseline_metrics, extension_metrics, mean, lower, upper))
    print(RESULT_PATH)


if __name__ == "__main__":
    main()
