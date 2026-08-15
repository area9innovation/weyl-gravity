# Strict 386-row full q1 component jet table v1

## Outcome

Yes. The artifact binds the already published 386-row basis and rank-386 odd pairing to all three Gate endpoint arrows, the repaired 36-row generalized-auxiliary differential, and all fourteen primal/cotangent mapping-cylinder arrows. Every coefficient is rational and indexed by a symmetrized covariant derivative multiindex. The endpoint contributes its independently matched 80 multiindex tables, the auxiliary block contributes its exact sparse matrix, and the 320-row cone contributes the full lower-order Ecurv, Ncurv and formal-adjoint tables plus incidence identities. Nilpotency replays sector by sector in the appropriate exact calculus, and every serialized coefficient satisfies q1^(T,formal) Omega R=Omega R D q1 with zero defects. This establishes a content-addressed unary snapshot, but it does not yet serialize the SDR, shear or Green actions and therefore does not pass classical import Gate A or promote any Hadamard/QME claim.

## Complete unary carrier

- Carrier: **386 rows**, split `30+36+320`.
- Operator tables: **18**.
- Symmetrized-covariant coefficient tables: **127**.
- Nonzero exact rational coefficients: **2193**.
- Endpoint / auxiliary / cone coefficients: `{'endpoint_30': 619, 'auxiliary_36': 30, 'mapping_cone_320': 1544}`.
- Maximum differential order: **4**.

The primitive differential is written in split coordinates.  The `T/A/B`
attachment is a separate degree-zero canonical shear and has not been
silently inserted as extra q1 arrows.

## Exact replays

- Full q1 squared: **True**.
- Cross-sector primitive arrows: **0**.
- Suspended cyclicity defects: **0** over
  **70** distinct derivative
  multiindices.
- Identity: `q1^(T,formal) Omega R = Omega R D q1`.

The endpoint uses the certified Gate suspension character.  On the 356-row
complement `R=+I`, so the same identity reduces to ordinary odd cyclicity.

## Unary snapshot

The basis, pairing, suspension and q1 bytes are bound by:

`34d0a3198d73a99111a1b91d9b642f8d890c4c479de00d056fe592c820f2e39a`

This is a unary snapshot, not yet the accepted common Gate-A snapshot.

## Does not establish

- component tables for H_alg, endpoint inclusion/projection, the canonical T/A/B shear, or advanced/retarded Green actions
- one accepted common Gate-A snapshot binding q1, q2, D, pairing, SDR and causal Green data
- q2 or local D on the same 386-row causal carrier
- a weakest-foundation calibration of the imported analytic Green theorem
- a Hadamard state, BRST Ward theorem, positivity result, renormalized Lorentzian products, QME restoration, residual transfer or Lorentzian quantum theory

## Next gate

Serialize H_alg, endpoint inclusion/projection, the degree-zero T/A/B shear and advanced/retarded Green actions against this unary snapshot, independently replay the SDR and suspended Green-adjoint identities componentwise, and only then accept a common Gate-A snapshot hash before binding q2 and local D.

## Reproduction

```text
PYTHONPATH=<repository-root>:<sympy-site> python3 quantum-weyl/classical_import/build_strict_386_full_q1_component_jet_table.py --check
PYTHONPATH=<repository-root>:<sympy-site> python3 quantum-weyl/classical_import/check_strict_386_full_q1_component_jet_table.py
PYTHONPATH=<repository-root>:<sympy-site> python3 quantum-weyl/classical_import/verify_strict_386_full_q1_component_jet_table.py
PYTHONPATH=<repository-root>:<sympy-site> python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_full_q1_component_jet_table.py
```
