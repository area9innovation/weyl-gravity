# Foundations cube v13: named H2 weak-test completion

**Result:** `FOUNDATIONAL_INTERSECTION_CUBE_V13`

## Outcome

Cube v13 preserves the full 576-coordinate v12 surface and augments exactly four weak-arithmetic smooth/distributional cells. State representation and evolution/well-posedness become scoped direct local results; kinematics remains a direct local result with the larger named carrier, while reconstruction remains pieces-only.

The crucial scope is representation-sensitive: density holds in the declared fixed-slab H2 completion because the fast name is supplied. The result does not reconstruct the unrestricted classical LF test topology or prove uniqueness among arbitrary distributions.

The surface contains **125 local results**, **90 literature results**, **162 pieces-only cells**, **30 priority gaps**, **169 reviewed gaps**, and **0 not-mapped cells**.

## Reproduction

```text
python3 foundations/refine_intersection_cube_v13.py --check
python3 foundations/check_refined_intersection_cube_v13.py
python3 foundations/verify_refined_intersection_cube_v13.py
python3 -m unittest foundations.tests.test_refined_intersection_cube_v13
```

## Boundaries

- This does not establish a uniform H2 name constructor for every bare extensional smooth test.
- This does not establish the unrestricted LF topology of compactly supported smooth tests.
- This does not establish uniqueness among arbitrary distributional weak solutions.
- This does not establish strict finite propagation or causal Green support.
- This does not establish an advanced or retarded Green operator.
- This does not establish a Weyl, Bateman-Turok, metric-BV, or interacting equation.
- This does not establish empirical calibration or observational agreement.
- This does not establish that all 576 coordinates are jointly realizable.
- This does not establish a complete physical theory or new LORENTZIAN-CAUSAL result.
