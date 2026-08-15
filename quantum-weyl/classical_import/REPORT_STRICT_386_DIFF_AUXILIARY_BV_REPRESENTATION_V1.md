# Strict 386-row Diff auxiliary BV representation v1

**Result:** `STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1`

**Dependency:** `LOCAL-ALGEBRAIC`

The receiver imports all three source-forced auxiliary Lie actions and derives
their cotangent and Diff momentum-map rows against the exact 386-row odd
pairing.  This matters in the symmetric-tensor sector, whose DeWitt-type
pairing is non-diagonal.  Independent formal variation has
**0** defects, and the suspended input
tables have **0** Koszul defects.

| Family | Master density | Field outputs | Antifield outputs | `c_star` outputs |
|---|---:|---:|---:|---:|
| `DIFF_C_F_HAT_F_HAT_STAR` | 200 | 208 | 472 | 544 |
| `DIFF_C_V_V_STAR` | 32 | 64 | 80 | 80 |
| `DIFF_C_ETA_ETA_STAR` | 32 | 64 | 80 | 80 |

All seven currently known required cubic families are now component-complete.
This is not an exhaustive family theorem: the nonlinear Weyl/conformal-boost
ghost-antifield manifest remains absent.  The complete source `q2` assembly
and its `q1/q2` identity therefore remain fail-closed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_diff_auxiliary_bv_representation.py --check
python3 quantum-weyl/classical_import/check_strict_386_diff_auxiliary_bv_representation.py
python3 quantum-weyl/classical_import/verify_strict_386_diff_auxiliary_bv_representation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_diff_auxiliary_bv_representation
```
