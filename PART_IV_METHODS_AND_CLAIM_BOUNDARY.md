# Part IV Methods and Claim Boundary

This companion holds the shared Part IV notation and the common minimum
evidence standard. Active manuscripts use it by reference and must provide
their own observable unit, proxy definitions, native model/baseline, data
source, time scale, and result.

## Shared notation

`Phi` is a declared driving flow or throughput. `C` is a measured active
constraint or capacity burden. `S` is a measured response, buffering, routing,
or reconfiguration process. `M_s` is a retained state that must be measured
independently of the present outcome. `Psi_s` is optional local bookkeeping,
usually written `(Phi / C) * S * M_s`; it is not a universal constant, a common
material mechanism, or a threshold transferable across domains.

Greek coefficients are local parameters only. They do not acquire a common
physical meaning from reuse between papers.

## Minimum comparison

1. Define proxies before fitting or inspecting the outcome.
2. Use a field-native baseline that can solve the named task without CDFD/AFL.
3. Hold out data chronologically or by an otherwise defensible independent
   split.
4. Report null results and uncertainty without changing proxy definitions after
   the comparison.
5. Treat a fitted composite as a candidate predictor, not a derivation of a
   material mechanism.

Runtime results test only the implementation. They do not substitute for
field, clinical, engineering, economic, astronomical, ecological, or social
data. The completed USGS hydrology check is a narrow negative prediction
result, documented in `Part_A_Earth_Systems/empirical_hydrology_study/`.

## Generic model and evidence template

The following form is a reusable candidate architecture, not a domain
derivation:

```text
Y(t) = Phi(t) S(t) / (epsilon + C(t))
dC/dt = alpha Phi(t) - beta S(t) C(t) + gamma L C(t)
dM_s/dt = eta C(t) - mu M_s(t)
```

Here `epsilon` is a numerical guard, `L` is a local spatial or network
operator, and all coefficients must be estimated or fixed within the domain.
No common threshold follows from the notation. A domain paper must therefore
declare its own causal sequence, scale, outcome, and data before using any
form of this template.

The default evidence sequence is: preregister a proxy audit; observe or apply
a load perturbation; compare recovery between matched histories; and compare a
minimal extension with a native baseline on held-out data. The extension fails
when it adds no predictive or explanatory value beyond the baseline. Correlation
does not identify a constraint mechanism, a fitted memory term does not prove a
cross-domain material identity, and a runtime cascade is not field evidence.

## Consolidation rule

Papers may be merged only when they can share the observational unit, outcome,
data family, and native baseline. Shared CDFD vocabulary alone is not a reason
to merge distinct disciplines.
