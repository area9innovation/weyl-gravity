# Strict 386-row hh/hv auxiliary cotangent lift v1

**Result:** `STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1`
**Dependency:** `LOCAL-ALGEBRAIC`

The receiver imports **1392** curved hh and **76** hv field
coefficients and combines them with the 22-coefficient vv sector.
Formal integration by parts produces **3411** hh-to-h-star,
**320** hv-to-h-star, and
**160** hv-to-v-star collected coefficients.  With the
16 vv partners, the combined cotangent table has
**3907** nonzero coefficients.  All 150 metric-jet and four
vector variational slices have zero formal-adjoint defect.  Of the 150 declared
metric two-jet slices, 122 are active and 28 are identically zero.

This completes the quadratic field/cotangent lift on the declared 386-row
carrier.  It does not complete the interaction theory: only
4 of seven required cubic
families are component-complete.  The three Diff representation families and
the exhaustive nonlinear Weyl/boost ghost-antifield census remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_hh_hv_auxiliary_cotangent_lift.py --check
python3 quantum-weyl/classical_import/check_strict_386_hh_hv_auxiliary_cotangent_lift.py
python3 quantum-weyl/classical_import/verify_strict_386_hh_hv_auxiliary_cotangent_lift.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_hh_hv_auxiliary_cotangent_lift
```
