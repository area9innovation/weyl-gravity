# Foundations cube v12: localized coefficient-weak wave import

**Result:** `FOUNDATIONAL_INTERSECTION_CUBE_V12`

## Outcome

Cube v12 preserves the full 576-coordinate v11 surface and augments exactly three weak-arithmetic smooth/distributional cells. The localized-test kinematics cell becomes a direct local result. Reconstruction moves from a reviewed gap to pieces-only, while distributional well-posedness remains pieces-only.

The imported theorem has an exact rank-10 localized measurement matrix for ten labelled finite chiral coefficients and proves the weak transport and scalar wave identities coefficient by coefficient against ten rational localized tests. It does not cover every smooth test, forget the chiral labels, prove causal support, or construct a Green operator.

The surface contains **123 local results**, **90 literature results**, **163 pieces-only cells**, **30 priority gaps**, **170 reviewed gaps**, and **0 not-mapped cells**.

## Reproduction

```text
python3 foundations/refine_intersection_cube_v12.py --check
python3 foundations/check_refined_intersection_cube_v12.py
python3 foundations/verify_refined_intersection_cube_v12.py
python3 -m unittest foundations.tests.test_refined_intersection_cube_v12
```

## Boundaries

- This does not establish a weak equation against every smooth compactly supported test.
- This does not establish separation of arbitrary scalar distributions or gauge classes.
- This does not establish full state or representation-independent field reconstruction.
- This does not establish well-posedness in a distribution topology from coefficient compatibility alone.
- This does not establish strict finite propagation or causal Green support.
- This does not establish an advanced or retarded Green operator.
- This does not establish a Weyl, Bateman-Turok, metric-BV, or interacting equation.
- This does not establish empirical calibration or observational agreement.
- This does not establish that all 576 coordinates are jointly realizable.
- This does not establish a complete physical theory or new LORENTZIAN-CAUSAL result.
