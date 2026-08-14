# Foundations cube v11: observable reconstruction import

**Result:** `FOUNDATIONAL_INTERSECTION_CUBE_V11`

## Outcome

Cube v11 preserves the complete 576-coordinate v10 surface and changes exactly two weak-arithmetic Hilbert/operator coordinates. A declared rational detector is now a direct local kinematics/observable result, and its exact finite dyadic interpolants provide a direct local reconstruction result.

The reconstruction theorem is uniform on every rational bounded time interval and supplies the explicit cutoff `N(k)=k+ell(K)+1`. It reconstructs one smeared scalar-wave observable, not the full field, a causal Green operator, or an empirical prediction.

The surface contains **122 local results**, **90 literature results**, **162 pieces-only cells**, **30 priority gaps**, **172 reviewed gaps**, and **0 not-mapped cells**.

## Reproduction

```text
python3 foundations/refine_intersection_cube_v11.py --check
python3 foundations/check_refined_intersection_cube_v11.py
python3 foundations/verify_refined_intersection_cube_v11.py
python3 -m unittest foundations.tests.test_refined_intersection_cube_v11
```

## Boundaries

- This does not establish that RCA_0 is necessary or weakest.
- This does not establish a separating observable algebra from one detector profile.
- This does not establish full state or field reconstruction from one smeared observable.
- This does not establish representation invariance or a general finite-to-continuum theorem.
- This does not establish a localized weak spacetime equation or causal Green support.
- This does not establish a Weyl, Bateman-Turok, metric-BV, or interacting reconstruction theorem.
- This does not establish empirical calibration or observational agreement.
- This does not establish that all 576 coordinates are jointly realizable.
- This does not establish a complete physical theory or new LORENTZIAN-CAUSAL result.
