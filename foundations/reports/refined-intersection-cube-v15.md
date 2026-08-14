# Foundations cube v15: scalar biwave to Weyl BV delta

**Result:** `FOUNDATIONAL_INTERSECTION_CUBE_V15`

## Outcome

Cube v15 preserves all 576 v14 coordinates and their statuses. It adds the exact flat scalar biwave theorem to evolution and causality, then adds a fail-closed sixteen-gate dependency delta to the continuum gauge/BV gap.

The cube therefore gains depth without pretending to gain Weyl-BV coverage. The causal scalar result is real; the full continuum BV coordinate remains a priority gap.

Counts remain **127 local results**, **90 literature results**, **160 pieces-only cells**, **30 priority gaps**, **169 reviewed gaps**, and **0 not-mapped cells**.

## Reproduction

```text
python3 foundations/refine_intersection_cube_v15.py --check
python3 foundations/check_refined_intersection_cube_v15.py
python3 foundations/verify_refined_intersection_cube_v15.py
python3 -m unittest foundations.tests.test_refined_intersection_cube_v15
```

## Boundaries

- This does not establish a variable-coefficient or curved-spacetime tensor Green operator.
- This does not establish a full off-shell Lorentzian Weyl BV propagator.
- This does not establish a passed classical import freeze gate.
- This does not establish BRST-compatible causal homotopies.
- This does not establish a Hadamard state or microlocal spectrum theorem.
- This does not establish renormalized Lorentzian products, causal pAQFT, or a Lorentzian QME.
- This does not establish that scoped no-go results rule out neighboring architectures.
- This does not establish a weakest-base reversal.
- This does not establish empirical adequacy.
- This does not establish a complete physical theory.
