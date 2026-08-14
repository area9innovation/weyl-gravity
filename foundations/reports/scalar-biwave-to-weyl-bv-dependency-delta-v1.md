# From scalar biwave to Lorentzian Weyl BV: fail-closed dependency delta

**Result:** `FOUNDATIONAL_SCALAR_BIWAVE_TO_WEYL_BV_DEPENDENCY_DELTA_V1`

## Outcome

The scalar construction supplies an exact causal fourth-order benchmark, not a transfer theorem. Sixteen typed gates separate it from the target. Two are proved only in the scalar source, one is a positive but background-scoped Nariai Weyl result, one is an open-but-seeded Berger route, two are scoped architectural no-go theorems, one is a forbidden particle reinterpretation, and the remaining target gates are missing or fail closed. The authoritative classical import gate itself remains pending, so no full-complex Lorentzian or quantum lifecycle promotion is permitted.

## What transfers, and what does not

| gate | scalar input | Weyl/BV requirement | status | exact missing object |
|---|---|---|---|---|
| `D01_SCALAR_FACTOR` | explicit flat scalar P Green maps | normally-hyperbolic factor Green maps on the target bundle | `PROVED_SCALAR` | variable-coefficient bundle factor theorem |
| `D02_FOURTH_ORDER_COMPOSITION` | canonical H=G o G for P^2 | factorization or direct Green theorem for the gauge-fixed fourth-order metric operator | `PROVED_SCALAR` | principal and lower-order Weyl operator identification |
| `D03_TENSOR_CARRIER` | scalar functions with scalar pairing | symmetric-tensor, ghost, antifield, and nonminimal bundles with graded pairing | `MISSING_CERTIFICATE` | complete degreewise carrier and nondegenerate graded pairing |
| `D04_GAUGE_FIXING` | no gauge symmetry | gauge fixing whose full kinetic complex is Green-hyperbolic | `MISSING_CERTIFICATE` | full off-shell gauge-fixed Weyl BV operator and gauge-fixing independence |
| `D05_CURVED_LOWER_ORDER` | zero lower-order couplings in flat space | curvature-dependent subprincipal and lower-order terms controlled on a globally hyperbolic background | `MISSING_CERTIFICATE` | bundle energy estimates and Volterra convergence for the chosen Weyl background |
| `D06_CONSTRAINT_PROPAGATION` | none | gauge constraints and subsidiary equations preserved by evolution | `MISSING_CERTIFICATE` | constraint-propagation chain theorem |
| `D07_DEGREEWISE_INVERSES` | B H=H B=id on scalar code domains | degreewise P_BV G=id and G P_BV=id on declared compact section domains | `MISSING_CERTIFICATE` | full-complex two-sided Green identities |
| `D08_BRST_COMPATIBILITY` | no BRST differential | [q,G]=0 or a certified causal homotopy identity compatible with the BV differential | `MISSING_CERTIFICATE` | BRST-compatible causal Green homotopy |
| `D09_SUPPORT_MICROLOCAL` | exact flat cone support | curved causal support plus wavefront-set and microlocal compatibility | `MISSING_CERTIFICATE` | full-complex support and microlocal spectrum certificate |
| `D10_CLASSICAL_FREEZE` | no classical BV import | nilpotency, contraction, chain maps, cyclicity, residual cohomology, and pairing independently frozen | `FAIL_CLOSED_IMPORT` | all missing exports and ten blocked checks listed by CLASSICAL_IMPORT_CERTIFICATE |
| `D11_NARIAI_POSITIVE_SLICE` | no curved example | complete four-row metric Bach BV Green homotopy on unit Nariai | `SCOPED_WEYL_RESULT` | extension from the certified four-row Nariai complex to the full off-shell metric BV complex |
| `D12_BERGER_ROUTE` | scalar composition suggests a factor route | Berger hybrid retained chain with convergent causal Volterra resolvent | `OPEN_SEEDED` | causal Volterra resolvent and full 26-row homotopy |
| `D13_24_FIELD_NO_GO` | scalar P^2 has a scalar principal symbol | 24-field pointwise-pairing first-order companion with scalar normally-hyperbolic symbol | `SCOPED_NO_GO` | a materially different bundle, gauge, pairing, or architecture |
| `D14_46_PARAMETER_NO_GO` | scalar factorization is semisimple | fixed-temporal cyclic 46-parameter first-order strongly-hyperbolic family | `SCOPED_NO_GO` | changed temporal normalization, incidence, scalar branch, or enlarged prolongation |
| `D15_RESIDUAL_CLASSES` | scalar solutions can be viewed as states only in the scalar model | [W_+^2] and [W_-^2] retain their certified deformation/vertex meaning | `FORBIDDEN_TRANSFER` | a separate one-particle cohomology and positivity construction |
| `D16_QUANTUM_CAUSAL` | classical scalar Green maps only | BRST-compatible Hadamard state, renormalized time-ordered products, causal pAQFT, and Lorentzian QME | `MISSING_CERTIFICATE` | all four quantum causal constructions in lifecycle order |

## The two live positive routes

- **Nariai control:** a genuine complete four-row metric Bach BV Green homotopy already exists on global unit Nariai. It proves feasibility in that scoped background and carrier.
- **Berger frontier:** the exact mixed-order contract and companion SDR exist, but causal Volterra convergence and the full 26-row homotopy do not.

## Why the gate is red

The authoritative classical import is `FAIL_CLOSED` with 10 blocked or failed checks and 17 missing or incomplete exports. Artifact integrity is not acceptance of the snapshot.

## Scoped no-go results

The 24-field scalar-symbol and fixed-temporal 46-parameter first-order architectures are ruled out only in their declared families. They do not refute the classical BRST complex, residual cohomology, or spectrum, and they do not close different gauge, bundle, temporal, or prolonged architectures.

## Reproduction

```text
python3 foundations/build_scalar_biwave_to_weyl_bv_delta.py --check
python3 foundations/check_scalar_biwave_to_weyl_bv_delta.py
python3 foundations/verify_scalar_biwave_to_weyl_bv_delta.py
python3 -m unittest foundations.tests.test_scalar_biwave_to_weyl_bv_delta
```

## Boundaries

- This does not establish a full off-shell Lorentzian Weyl metric BV propagator.
- This does not establish a BRST-compatible Hadamard state.
- This does not establish renormalized Lorentzian time-ordered products.
- This does not establish a causal perturbative AQFT construction.
- This does not establish a Lorentzian quantum-master-equation theorem.
- This does not establish a passed classical import freeze gate.
- This does not establish that the two scoped no-go theorems rule out other architectures.
- This does not establish that the centered Weyl-square deformation classes are particles.
- This does not establish a weakest-base reversal for curved tensor PDE.
- This does not establish empirical adequacy or a complete physical theory.
