# Strict 386-row shifted-mass BV q2 lift v1

**Result:** `STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1`
**Dependency:** `LOCAL-ALGEBRAIC`

The 72 independent rational coefficients of the shifted
`h-f_hat-f_hat` action vertex now determine an exact BV `q2` on the fixed
386-row pairing.  Lowering the third action variation produces
**120** ordered `f_hat,f_hat -> h_star`
coefficients and **272**
ordered `h,f_hat -> f_hat_star` coefficients, including their graded-symmetric
mates.

The construction is not a guessed sign convention.  The already certified
unary table obeys `Omega(f_hat,q1(f_hat))=D^2 S_aux`; the same convention fixes
`Omega(x3,q2(x1,x2))=D^3 S_aux`.  Exact rational replay checks
3000 cyclic equalities and finds
**0 defects**.

This closes the shifted-mass family only.  The common union with minimal and
Diff rows—and especially its coupled `c/h/f_hat` arity-two identity—remains
fail closed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_shifted_mass_bv_q2_lift.py --check
python3 quantum-weyl/classical_import/check_strict_386_shifted_mass_bv_q2_lift.py
python3 quantum-weyl/classical_import/verify_strict_386_shifted_mass_bv_q2_lift.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_shifted_mass_bv_q2_lift
```
