# Classical shifted-auxiliary cubic inventory v1

**Result:** `CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1`
**Dependency:** `LOCAL-ALGEBRAIC`

The exact shifted auxiliary mass is not interaction-inert.  Its
`h-f_hat-f_hat` cubic vertex has **72**
nonzero rational monomials among 550
possible component monomials.  All 55 pure-trace
metric checks vanish, as required by four-dimensional Weyl invariance.

The already constructed vector part of the nonlinear shift has **22** nonzero
component coefficients.  Together these results enumerate seven currently
required cubic block families, but only 1
is coefficient-complete in this classical export.  The vv cotangent partner,
the hh/hv shift tables, the three Diff representation vertices, and the full
nonlinear Weyl/boost ghost manifest remain separate obligations.

Consequently the vv shift repairs the old `f_hat-v-v` mismatch, but the exact
auxiliary shift alone does **not** identify the source with an interaction-inert
trivial stabilization.  This is not a no-go for a further metric-dependent
canonical or cyclic L-infinity normalization.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_shifted_auxiliary_cubic_inventory_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_shifted_auxiliary_cubic_inventory_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_shifted_auxiliary_cubic_inventory_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_shifted_auxiliary_cubic_inventory_v1
```
