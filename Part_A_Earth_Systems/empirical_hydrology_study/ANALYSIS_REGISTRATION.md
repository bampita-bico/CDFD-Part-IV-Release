# Hydrology Held-Out Test: Analysis Registration

**Frozen:** 2026-08-18 (before this package downloads the analysis record)  
**Status:** Same-session analysis registration, not an independently timestamped preregistration.

## Question

For a single observed river record, do explicitly declared CDFD/AFL-inspired
state transformations improve one-day-ahead discharge prediction beyond a
native autoregressive-and-seasonal baseline? This is a narrow empirical utility
test for Paper A-04, not a test of a universal CDFD law or a derivation of
hydrological mechanism.

## Domain and data

* **Domain:** daily river discharge at USGS site `01646500`, Potomac River near
  Washington, DC.
* **Record:** USGS National Water Information System (NWIS) daily mean
  discharge, parameter `00060`, statistic `00003`, 2010-01-01 through
  2024-12-31, in cubic feet per second.
* **Endpoint:**
  `https://waterservices.usgs.gov/nwis/dv/?format=json&sites=01646500&parameterCd=00060&statCd=00003&startDT=2010-01-01&endDT=2024-12-31`
* **Source boundary:** USGS daily values are gauge summaries, not direct
  measures of catchment-wide rainfall, channel capacity, floodplain storage,
  or geomorphic change. The test must not identify those mechanisms from this
  record alone.

## Frozen target and split

The target is `log1p(discharge[t+1])`. Rows dated 2010-01-07 through
2021-12-31 are the training period. Rows dated 2022-01-01 through 2024-12-30
are the chronological held-out test period. The final target on 2024-12-31 is
unavailable by design. No row is shuffled and no test observation is used to
fit a scaling, quantile, or model coefficient.

## Frozen proxies

All features use information available no later than day `t`.

| Name | Definition | Role and limitation |
| --- | --- | --- |
| `log_q_lag_0` to `log_q_lag_6` | `log1p(Q[t-k])` | Native discharge persistence/recession features. |
| `sin_doy`, `cos_doy` | annual day-of-year harmonics | Native seasonal climatology. |
| `phi_proxy` | `log1p(Q[t])` | Observed throughput proxy; it is not precipitation forcing. |
| `c_proxy` | 95th percentile of `log1p(Q)` computed on training dates only | A fixed event-scale normalization, **not** measured channel capacity. |
| `s_proxy` | `abs(log1p(Q[t])-log1p(Q[t-1]))` | Recent response magnitude, **not** a direct measure of adaptation. |
| `m_proxy` | trailing 7-day mean of `log1p(Q)`, ending at `t` | Antecedent discharge state, **not** an independently measured structural memory. |
| `psi_proxy` | `(phi_proxy / c_proxy) * (1 + s_proxy) * m_proxy` | Predeclared composite bookkeeping feature, not a dimensionless physical operating ratio. |

The CDFD/AFL extension contains `phi_proxy / c_proxy`, `s_proxy`, `m_proxy`,
and `psi_proxy`; it never changes the baseline feature set. This construction
tests only whether the declared nonlinear transformations add predictive
information after ordinary lagged discharge and seasonality are already
available.

## Models and decision rule

Both models are linear ridge regressions (`alpha=1.0`) after standardization
fit on training data only. No hyperparameter search is performed.

1. **Native baseline:** the seven lagged log-discharge features and the two
   seasonal features.
2. **CDFD/AFL extension:** the native baseline plus the four frozen terms
   above.

The primary metric is held-out RMSE on `log1p(Q[t+1])`; MAE and R-squared are
secondary descriptive metrics. The extension counts as an empirical
improvement only if both conditions are met:

* held-out RMSE is at least 1% lower than the native baseline; and
* a seed-fixed (`20260818`) 2,000-replicate moving-block bootstrap (14-day
  blocks) has a one-sided 95% lower bound above zero for the mean squared-error
  reduction (`baseline - extension`).

Otherwise the result is recorded as no demonstrated held-out improvement. A
positive result would still be a single-site prediction result, not evidence
that the proxy meanings or material mechanisms generalize.

## Reproduction

Run from the Part IV release root:

```bash
/home/bampita/Projects/CDFD/.venv/bin/python \\
  Part_A_Earth_Systems/empirical_hydrology_study/run_heldout_test.py --download
```

The command saves the raw response, its SHA-256 digest, a cleaned daily table,
and a results report. Re-running without `--download` uses the saved raw
response and refuses to silently retrieve a changed series.
