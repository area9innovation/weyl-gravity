# Full-surface foundations cube v9

**Result:** `FOUNDATIONAL_INTERSECTION_CUBE_V9`

**Lifecycle:** `FULL_CARTESIAN_SURFACE_ASSESSED`

## Outcome

Cube v9 emits the exact **6 × 6 × 16 = 576** Cartesian surface and records an assessment for every coordinate. It preserves all 401 previously classified cube-v8 cells, revises the 51 emitted `NOT_MAPPED` cells, and adds the 124 previously browser-only complements.

The surface contains **115 local results**, **93 literature results**, **163 pieces-only cells**, **30 priority gaps**, **175 reviewed open gaps**, and **0 not-mapped cells**.

`REVIEWED_GAP` is a complete assessment state, not a completed scientific result. Each such cell has a coherent research question and a typed missing certificate, but no direct local or literature result. The 30 `PRIORITY_GAP` cells remain the selected programme priorities.

The 124 new coordinates use `DIRECT_COORDINATE_REVIEW`: they were assessed directly rather than inherited from a broad parent. Already classified one-axis neighbors remain navigation only and do not license evidence transfer.

## Reproduction

```text
python3 foundations/refine_intersection_cube_v9.py --check
python3 foundations/check_refined_intersection_cube_v9.py
python3 foundations/verify_refined_intersection_cube_v9.py
python3 -m unittest foundations.tests.test_refined_intersection_cube_v9
```

## Boundaries

- This does not establish a result for any REVIEWED_GAP coordinate.
- This does not establish that a reviewed gap is a programme priority.
- This does not establish literature completeness or absence.
- This does not establish that all 576 coordinates are jointly realizable.
- This does not establish evidence transfer from a one-axis neighbor.
- This does not establish impossibility, independence, inconsistency, or a no-go theorem.
- This does not establish a weakest foundation or equivalence of carrier categories.
- This does not establish a continuum limit or empirical equivalence.
- This does not establish a complete Weyl theory or quantum completion.
- This does not establish a new LORENTZIAN-CAUSAL conclusion.
