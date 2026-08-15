# Strict 386-row shifted-mass BV q3 lift v1

**Result:** `STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1`

**Dependency:** `LOCAL-ALGEBRAIC`

The authoritative classical `h-h-f_hat-f_hat` tensor has now been lowered
through the fixed 386-row odd pairing.  It produces
**2736** ordered
`q3(h,f_hat,f_hat) -> h_star` coefficients and
**3216** ordered
`q3(h,h,f_hat) -> f_hat_star` coefficients: **5952**
in total.

This is a variational lift, not a fitted receiver operation.  Exact replay
checks all 10000 component slots from all
four cyclic receiver positions—40000
equalities—and finds **0 defects**.  All inputs are
even and the serialized operation has exact `S3` symmetry.

The auxiliary family is complete, but Gate A remains fail closed until it is
assembled with minimal `q3`, the quartic source-family census is closed, and
the full arity-three identity is replayed on common bytes.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_shifted_mass_bv_q3_lift.py --check
python3 quantum-weyl/classical_import/check_strict_386_shifted_mass_bv_q3_lift.py
python3 quantum-weyl/classical_import/verify_strict_386_shifted_mass_bv_q3_lift.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_shifted_mass_bv_q3_lift
```
