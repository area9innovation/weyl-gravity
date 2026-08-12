# Migration-reviewed foundations intersection cube v2

**Result:** `FOUNDATIONAL_INTERSECTION_CUBE_V2`

## Outcome

V2 preserves the v1 6 × 6 × 16 axes and all **452** emitted coordinates. Migration review is complete for those coordinates: **0 pending**, including **88 reviewed no-transfer** cells whose coverage is now explicitly `NOT_MAPPED`.

Coverage is classified in **364** emitted cells. The other 88 do not inherit their broad parent's evidence and are not called scientific gaps.

## Coverage status

| Status | Cells |
|---|---:|
| `LITERATURE_RESULT` | 90 |
| `LOCAL_RESULT` | 85 |
| `NOT_MAPPED` | 88 |
| `PIECES_ONLY` | 158 |
| `PRIORITY_GAP` | 31 |

## Migration status

| Status | Cells | Meaning |
|---|---:|---|
| `CAPABILITY_QUALIFIED` | 257 | An explicit evidence capability supports the split child. |
| `EXACT_PARENT_TRANSFER` | 72 | The unsplit v0 obligation transfers exactly. |
| `REVIEWED_CHILD_GAP` | 24 | An evidence-free broad parent gap was decomposed into this explicit child gap. |
| `REVIEWED_NO_TRANSFER` | 88 | The named parent evidence was reviewed and does not support the child. |
| `REVIEWED_OVERLAY` | 11 | A child-specific v1 overlay supplies the classification. |

## Interpretation

A reviewed no-transfer decision answers only whether the named v0 parent evidence supports the refined child. It does not answer whether other literature supports the cell. A reviewed child gap is stronger: the formerly broad gap has been stated as a precise missing child object, but it is still a current-corpus programme gap rather than an impossibility result.

## Reproduction

```text
python3 foundations/refine_intersection_cube_v2.py --check
python3 foundations/check_refined_intersection_cube_v2.py
python3 foundations/verify_refined_intersection_cube_v2.py
```

## Boundaries

- This does not establish literature completeness.
- This does not establish coverage for the 88 reviewed-no-transfer coordinates.
- This does not establish that NOT_MAPPED means no literature exists.
- This does not establish that every Cartesian coordinate is coherent.
- This does not establish a weakest mathematical base.
- This does not establish a new Lorentzian-causal result.
