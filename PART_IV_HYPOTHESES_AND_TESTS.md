# Part IV Hypotheses and Tests

Part IV is a cross-domain modelling archive. The shared notation does not
derive a universal mechanism, threshold, or material law.

## Capacity-Overload Hypothesis

For a declared domain, increasing a measured driving flow `Phi` relative to a
measured limiting process `C` may precede nonlinear saturation, overload, or a
regime change. A threshold is a domain-specific estimand, not a transferred
constant.

Test: preregister the proxies, scale, normalization, baseline model, and
failure condition. The mapping fails when it does not improve held-out
prediction or explanation beyond the ordinary domain model.

## Memory-Retention Hypothesis

`M_s` is a candidate representation of history-dependent state. It is useful
only where an observable retained-state proxy can be specified.

Test: compare units with matched present load and different measured histories.
The hypothesis requires reproducible differences in recovery or residual
constraint after ordinary confounders are controlled.

## Cross-Domain Translation Test

Two domains may support comparable bookkeeping for flow, constraint, response,
and retained state without sharing a material mechanism. The translation must
preserve the ordinary theory and units of each domain.

Test: state the aggregation rule and normalization, then test whether the CDFD
extension adds out-of-sample value beyond domain baselines. Resemblance alone is
not evidence.

## Constraint-Relaxation Test

The model asks whether a measured recovery process changes the relationship
between load, peak constraint, and recovery time.

Test: under a declared perturbation, estimate recovery with and without a
candidate response term. Report uncertainty and reject the interpretation when
the added term adds no predictive value.

## Runtime Adapter Stress Test

The domain-adapter sweep is a model-level software test. It checks whether the
current runtime returns finite outputs, declared regimes, and stable artifacts
under standardized toy conditions.

Non-finite or uninterpretable outputs are runtime or modelling failures, not
discoveries. Finite outputs are not field validation.

## Network-Cascade Stress Test

The release diagnostic records the behavior of a localized high-drive hub under
declared toy parameters. It is not a claim about ecological, technical, social,
physical, or cognitive cascades.

Test: rerun `Part_E_Synthesis/supplementary/run_partiv_discovery.py` and report
the parameters, finite-value audit, and output record. Changes in drive,
threshold, relaxation, or topology should be interpreted only within that
model.
