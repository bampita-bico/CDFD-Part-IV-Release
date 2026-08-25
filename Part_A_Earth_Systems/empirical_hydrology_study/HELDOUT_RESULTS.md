# Hydrology Held-Out Results

**Run date:** 2026-08-18  
**Verdict:** **NOT DEMONSTRATED**

## Locked analysis

The specification is frozen in [ANALYSIS_REGISTRATION.md](ANALYSIS_REGISTRATION.md).
The raw USGS response was downloaded after that file was created, saved locally,
and hashed as `66ebaa3aa527676ec0a56cf5cc19cc774abd6de0599faefcc11c031c67abb60e`. The analysis has no external timestamped
preregistration; it is a same-session, reproducible analysis registration.

* USGS site: `01646500` (Potomac River near Washington, DC)
* Source daily values: 5479 from 2010-01-01 to 2024-12-31
* Feature-ready training rows: 4377; held-out rows: 1095
* Target: next-day `log1p(discharge_cfs)`
* Evaluation: chronological 2022-01-01 through 2024-12-30 holdout

## Held-Out metrics

| Model | RMSE | MAE | R-squared |
| --- | ---: | ---: | ---: |
| Native lagged-discharge + season baseline | 0.199313 | 0.123303 | 0.956617 |
| Baseline + frozen CDFD/AFL transformations | 0.199223 | 0.122460 | 0.956657 |

The CDFD/AFL extension changes held-out RMSE by **0.045%** (positive
means lower error). The 14-day moving-block bootstrap mean reduction in
squared error is `0.00003584`, with a one-sided 95% lower bound of
`-0.00016735` and upper 95% quantile of `0.00023091`.

## Decision

The predeclared improvement criterion requires at least 1% lower held-out RMSE
and a positive one-sided 95% bootstrap lower bound for mean squared-error
reduction. **The predeclared CDFD/AFL extension does not clear the held-out decision rule; this analysis supplies no evidence of predictive value beyond the native baseline.**

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
/home/bampita/Projects/CDFD/.venv/bin/python \
  Part_A_Earth_Systems/empirical_hydrology_study/run_heldout_test.py
```
