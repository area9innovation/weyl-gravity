# Standard GR solar-system prediction assembly: field equations to Cassini

**Result:** `FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1`

**Lifecycle:** `MODEL_SCOPED_EMPIRICAL_COMPARISON_REGISTERED`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Outcome

This is the first model-scoped end-to-end prediction assembly in the
foundations atlas. It uses one declared model throughout: four-dimensional
standard GR in the static, asymptotically flat vacuum exterior of the Sun,
with minimally coupled radio photons. Within that bounded scope the assembly
is complete and empirically supported. It is not a complete theory.

## Exact prediction rail

1. `G_mu_nu=0` reduces in the static spherical ansatz to
   `(r f' + f - 1)/r^2=0`, so `(r f)'=1` and
   `f(r)=1-2m/r` after Newtonian normalization.
2. The exact isotropic map `r=rho(1+m/(2rho))^2` gives
   `g_tt=-1+2U-2U^2+...` and `g_ij=(1+2U+...)delta_ij`.
3. Comparison with the PPN template gives exact `beta=gamma=1`.
4. The null condition gives `dt/dl=1+(1+gamma)U+...`, hence the
   standard-GR delay coefficient `gamma+1=2`.

All coefficients are generated with exact rational formal-series arithmetic.

## Typed empirical rail

The publisher reports `gamma=1+(2.1+/-2.3)e-5`. The
exact prediction `gamma-1=0` lies in the displayed reported plus-minus band
and has absolute standardized distance `21/23`.
This is a literature-scoped comparison: the Cassini reduction and likelihood
are not reproduced.

## Applicability mask

| Atlas obligation | Applicability | Reason |
|---|---|---|
| `KINEMATICS_OBSERVABLES` | `IN_SCOPE_REQUIRED` | The metric, null paths, PPN gamma, and radio time/frequency response are the declared configurations and observables. |
| `STATE_EXISTENCE` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `STATE_REPRESENTATION` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `PROBABILITY_RULE` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `PHYSICAL_STATE_SELECTION` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `GENERATOR_SPECTRAL_DYNAMICS` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `EVOLUTION_WELLPOSEDNESS` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `CAUSAL_PROPAGATION_GREEN` | `TOUCHED_NOT_REQUIRED` | A null-geodesic propagation law is used, but no retarded/advanced Green operator or Cauchy-support theorem is required or established. |
| `GAUGE_BV_COHOMOLOGY` | `TOUCHED_NOT_REQUIRED` | Areal and isotropic coordinate gauges are related exactly, but no BV complex or gauge cohomology is required or established. |
| `INTERACTION_CONSTRUCTION` | `IN_SCOPE_REQUIRED` | The nonlinear Einstein vacuum field equation and its exact Schwarzschild exterior solution define the gravitational model used by the prediction. |
| `COUNTERTERM_CLASSIFICATION` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `ANOMALY_CLASSIFICATION` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `RENORMALIZED_PRODUCTS` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `QME_RESTORATION` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `RESIDUAL_QUANTUM_TRANSFER` | `OUT_OF_SCOPE` | This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation. |
| `RECONSTRUCTION_LIMITS` | `IN_SCOPE_REQUIRED` | The isotropic weak-field map identifies the formal metric coefficient with the operational PPN gamma fitted by Cassini. |

## Composed stages

| Stage | Status | Establishes |
|---|---|---|
| Vacuum Einstein equations | `CERTIFIED_EXACT` | The declared model uses G_mu_nu=0 in the exterior sector. |
| Static spherical exterior | `CERTIFIED_EXACT` | The field equations integrate to f(r)=1-2m/r under the declared boundary normalization. |
| Isotropic weak-field reduction | `CERTIFIED_EXACT` | Exact coordinate translation and formal series give beta=gamma=1. |
| Null-delay observable | `CERTIFIED_EXACT` | The first-order delay coefficient is 1+gamma=2. |
| Cassini fitted parameter | `LITERATURE_SCOPED` | The publisher abstract identifies bending/delay and the measured frequency shift with gamma+1. |
| Published Cassini comparison | `SUPPORTED_REPORTED_BAND` | The exact prediction gamma-1=0 lies inside the displayed reported plus-minus band. |

## Boundaries

- This does not establish the Einstein equations outside the declared four-dimensional local metric and vacuum exterior assumptions.
- This does not establish solar interior structure, multipoles, rotation, plasma physics, spacecraft dynamics, or the Cassini data-reduction pipeline.
- This does not establish a retarded or advanced Green operator, full Cauchy well-posedness theorem, or BV gauge construction.
- This does not establish reproduction of the Cassini likelihood, covariance analysis, or systematic-error budget.
- This does not establish robustness against a second or held-out solar-system dataset.
- This does not establish agreement of standard GR in the other five benchmark families.
- This does not establish a complete classical, quantum, cosmological, or ultraviolet theory.
- This does not establish any empirical support for Mannheim--Kazanas or another Weyl-gravity model.

## Verification

```bash
python3 foundations/build_gr_cassini_assembly.py --check
python3 foundations/check_gr_cassini_assembly.py
python3 foundations/verify_gr_cassini_assembly.py
python3 -m unittest foundations.tests.test_gr_cassini_assembly
```

Canonical digest: `bdbe75d140525fa6b1a83c4ca1d5ca9298fb9ce2cbf5322e32869361ee4f2603`
