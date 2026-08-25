# Claim Status

This note keeps the Part IV modelling language separate from what has actually
been measured.

## Framework Definitions

Part IV uses these CDFD/AFL terms:

- `Phi`: flow intensity or driver.
- `C`: constraint or capacity burden.
- `S`: surface responsiveness.
- `M_s`: structural memory or hysteresis.
- `Psi_s`: adaptive operating ratio, usually `(Phi / C) * S * M_s`.
- `Lambda`: used when the Part II Life Number is being discussed.

These terms are useful only after a paper gives them observable proxies.

## Model Diagnostics

The supplementary scripts are small diagnostics. They test whether the current
runtime can produce finite overload, memory locking, constraint relaxation, and
cross-domain adapter responses. They do not replace climate data, engineering
measurements, economic records, immunology experiments, astrophysical
observations, linguistic evidence, or AI-system benchmarks.

## Completed Empirical Check

The first completed field-data check is recorded under
`Part_A_Earth_Systems/empirical_hydrology_study/`. A same-session frozen
analysis registration compared a native lagged-discharge and seasonal baseline
with fixed CDFD/AFL-style transformations for next-day discharge at USGS site
01646500. In the chronological 2022--2024 holdout, the extension reduced RMSE
by 0.045%, below the predeclared 1% threshold, and the 14-day moving-block
bootstrap lower bound for mean squared-error reduction was negative. The
result is **no demonstrated predictive improvement**. It is one gauge record,
does not measure the material proxies named in Paper A-04, and cannot validate
or falsify CDFD/AFL outside the narrowly declared prediction task.

## Candidate Constructs

Part IV uses several candidate constructs:

- Capacity-overload hypothesis: sustained high flow against a measured,
  slow-relaxing constraint may precede nonlinear overload in a named domain.
- Memory-retention hypothesis: unresolved prior load may persist as an observable
  retained state, making later stress harder to clear.
- Cross-domain translation test: different domains may support comparable
  flow-constraint-memory bookkeeping without sharing a material mechanism.
- Adapter Stress Response: runtime domain adapters can expose overload,
  balanced, or constrained regimes under standardized toy conditions.

These constructs need domain-specific proxy definition, calibration,
independent data, and failure conditions before they become empirical claims.

## Stronger Claim Standard

A Part IV claim is stronger when it gives:

- the measurable proxy for `Phi`, `C`, `S`, or `M_s`;
- the expected direction of change;
- the relevant spatial and temporal scale;
- a dataset or experimental system that could test it;
- a condition under which the AFL interpretation would fail;
- how the claim differs from an existing domain model.

The shared Part IV equations are a candidate architecture, not evidence that
Earth, engineered, socioeconomic, biological, cosmic, and cognitive systems
share one material mechanism. A cross-domain result requires declared
normalization, aggregation, and scale rules, followed by comparison against the
best ordinary model in each domain.

## Falsification Standard

The cross-domain Part IV framing weakens if a domain cannot be mapped into the
flow-constraint-memory form without adding unrelated hidden variables, if
predicted overload or recovery behavior is absent under measurable stress, or
if a better calibrated domain model explains the same data without the CDFD/AFL
variables.

## Boundary

No manuscript in this archive is operational advice for infrastructure,
finance, policy, medicine, climate intervention, or AI safety. Applied use would
need ordinary domain validation, expert review, and independent replication.
