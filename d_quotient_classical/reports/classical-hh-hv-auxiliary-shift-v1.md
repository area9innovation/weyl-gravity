# Classical hh/hv auxiliary-shift jets v1

**Result:** `CLASSICAL_HH_HV_AUXILIARY_SHIFT_V1`
**Dependency:** `LOCAL-ALGEBRAIC`

The exact nonlinear shift was differentiated twice on the unit conformal
cylinder.  The hh table contains **1392**
nonzero rational output coefficients over 11325
symmetric metric two-jet input pairs.  The hv table contains
**76** nonzero rational coefficients.
Curvature-dependent order-zero hh terms are included; this is not merely a
flat principal-symbol calculation.

The source export stops before the BV cotangent lift.  The 386-row receiver
must independently import these bytes and construct the formal-adjoint
h-star/v-star partners before the full quadratic canonical map can be claimed.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_hh_hv_auxiliary_shift_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_hh_hv_auxiliary_shift_v1.py
python3 d_quotient_classical/nonminimal_identity/check_classical_hh_hv_auxiliary_shift_v1.py --exhaustive  # Tier 2
python3 d_quotient_classical/nonminimal_identity/verify_classical_hh_hv_auxiliary_shift_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_hh_hv_auxiliary_shift_v1
```
