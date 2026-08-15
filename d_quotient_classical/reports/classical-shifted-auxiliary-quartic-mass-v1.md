# Classical shifted-auxiliary quartic mass v1

**Result:** `CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1`

**Dependency:** `LOCAL-ALGEBRAIC`

The authoritative shifted auxiliary action has a nonzero next metric Taylor
coefficient.  Exact rational expansion of its mass density gives
**321** nonzero independent
`h-h-f_hat-f_hat` monomials among
3025 possibilities,
or **912** nonzero ordered
fourth-variation coefficients.

This is tied to the already certified cubic vertex: all
550 first-variation component checks
agree.  The four-dimensional conformal Ward recursion contributes
55 pure-trace and
550 mixed checks, with zero defects.
An independent checker reconstructs the same table using a square-free exact
jet algebra, determinant expansion, and algebraic matrix inversion.

This certificate exports the classical action tensor only.  It does not yet
call the tensor `q3`: that requires the fixed odd pairing, every Koszul mate,
the minimal-sector union, cyclicity, and the complete arity-three identity.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_shifted_auxiliary_quartic_mass_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_shifted_auxiliary_quartic_mass_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_shifted_auxiliary_quartic_mass_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_shifted_auxiliary_quartic_mass_v1
```
