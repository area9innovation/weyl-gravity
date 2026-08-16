# Strict residual zero-mode payload v1

**Result:** `STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**Gate A:** `FAIL_CLOSED`

The previously hidden exact residual coefficients are now portable.  The
certificate exports the fifteen primal conformal-Killing modes and fifteen
dual endpoint representatives in the canonical order

```text
D, R01, R02, R03, R12, R13, R23, K+_0, K+_1, K+_2, K+_3, K-_0, K-_1, K-_2, K-_3
```

It also exports the complete `15^3` conformal
structure tensor (120 nonzero ordered entries),
all fifteen adjoint/cotangent representation matrices on the 30-dimensional
residual carrier, and the zero unary matrix `q_res^(0)`.

An independent consumer deserializes only the printed rational entries and
replays the kernel, quotient, cyclic-adjoint, Jacobi, representation,
coadjoint-pairing and nilpotency identities.  No producer success flag is
used as evidence.

This closes the coefficient construction called
`M5_RESIDUAL_EXACT_PAYLOAD`.  Gate A remains fail closed because the payload
has not yet been bound to the common full support-local freeze; the residual
SDR, full cyclic contraction and centered H3/H4/H5 representatives remain
separate obligations.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_residual_zero_mode_payload.py --check
python3 quantum-weyl/classical_import/check_strict_residual_zero_mode_payload.py
python3 -m unittest discover -s quantum-weyl/classical_import/tests -p 'test_strict_residual_zero_mode_payload.py'
```
