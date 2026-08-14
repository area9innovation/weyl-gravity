# BT Euclidean lattice: foundational import

**Result:** `FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1`

## Established

The certified BT lattice supplies five direct capabilities in the `FINITE_DISCRETE × SMOOTH_DISTRIBUTIONAL` cell family: explicit kinematics and observables, existence of a normalized finite-volume Gibbs state, a measure representation of that state, Euclidean statistical probabilities, and a nonlinear interaction.

The state-existence statement is finite-dimensional and exact: after the constant mode is removed, the action is coercive and its partition function is finite. The interaction is not merely inferred numerically; on a two-site mean-zero direction the exact action contains `(28/3) lambda^2 t^4` when `lambda != 0`.

## Numerical rail

HMC and an independently implemented local Metropolis chain agree at the declared coarse four-standard-error gate, but not at a two-standard-error precision gate. The L=4 to L=6 interaction-proxy change remains unresolved. This is a `COARSE_REPRODUCTION_ONLY` numerical record, not empirical validation.

## Carrier interface

The positive-`Omega` Euclidean lattice measure is not identical to the all-real-`Omega` two-field BT/Krein path integral. The certified relation is therefore `INCOMPATIBLE` only for full nonperturbative identity. A conditional perturbative, reflection-positive, or analytic-continuation bridge remains an open construction problem.

## Foundations consequence

The five direct cells become local results. `RECONSTRUCTION_LIMITS` stays a priority gap: the finite construction and its two-volume preflight provide supporting evidence, but no topology, uniform bound, limit identification, reflection positivity, Lorentzian map, or observable matching.

## Reproduction

```text
python3 foundations/build_bt_euclidean_lattice_import.py --check
python3 foundations/check_bt_euclidean_lattice_import.py
python3 foundations/verify_bt_euclidean_lattice_import.py
python3 -m unittest foundations.tests.test_bt_euclidean_lattice_import
```

## Boundaries

- This does not establish a finite exact carrier or finite probability sample space.
- This does not establish a physical-state-selection theorem from zero-mode fixing.
- This does not establish reflection positivity or Osterwalder-Schrader reconstruction.
- This does not establish a continuum or infinite-volume limit.
- This does not establish analytic continuation to the BT Krein theory.
- This does not establish a Born rule, scattering probability, or laboratory event rate.
- This does not establish empirical validation or out-of-sample robustness.
- This does not establish a graviton or full Weyl-gravity lattice theory.
- This does not establish a new physical dimension.
- This does not establish anything LORENTZIAN-CAUSAL.
