# Classical quadratic auxiliary-elimination map v1

**Result:** `CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1`

The exact completion of the auxiliary square fixes the first nonlinear map:

`phi_hat=phi-A_g^-1 G^b`, with
`F_(2)(v)=v tensor v-(1/2)g v^2`.

On the pinned traceless fixture, the original source channel is
**-1** and the inverse-shift mass
cross term is **1**.
Their residual is **0**.

This constructs the quadratic correction demanded by the obstruction.  It is
finite-order, support local, pointwise algebraic in its only inverse, and has an
exact local BV canonical cotangent lift.  It does not yet identify every
metric-dependent auxiliary or antifield interaction with the trivial
stabilization.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_quadratic_auxiliary_elimination_map_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_quadratic_auxiliary_elimination_map_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_quadratic_auxiliary_elimination_map_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_quadratic_auxiliary_elimination_map_v1
```
