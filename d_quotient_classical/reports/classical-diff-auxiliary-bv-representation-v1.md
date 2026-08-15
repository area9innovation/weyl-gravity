# Classical Diff auxiliary BV representation v1

**Result:** `CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1`

**Dependency:** `LOCAL-ALGEBRAIC`

The exact curved shift is natural under diffeomorphisms.  Consequently
`f_hat` is a symmetric covariant tensor, while `v` and the odd shifted boost
ghost `eta` are covectors.  Their three Lie-derivative actions are therefore
source-forced rather than fitted.  This export contains
**168** collected rational field-action
coefficients through first jet order.

| Family | Field type | Ordered coefficients |
|---|---|---:|
| `DIFF_C_F_HAT_F_HAT_STAR` | symmetric covariant rank-two tensor | 104 |
| `DIFF_C_V_V_STAR` | covector | 32 |
| `DIFF_C_ETA_ETA_STAR` | odd covector ghost | 32 |

The source export deliberately stops before identifying tensor duals with the
receiver's 386-row antifield coordinates.  That receiver uses a non-diagonal
DeWitt-type auxiliary pairing, so the cotangent and Diff momentum-map rows
must be derived against those exact bytes.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_diff_auxiliary_bv_representation_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_diff_auxiliary_bv_representation_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_diff_auxiliary_bv_representation_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_diff_auxiliary_bv_representation_v1
```
