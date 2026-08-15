# Strict minimal-BV cyclic sign reconciliation v1

**Result:** `STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1`

**State:** `MINIMAL_Q1_Q2_CANONICALLY_CYCLIC_D_AND_FULL_CARRIER_OPEN`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The missing minimal-sector pairing was not a clerical omission. Lowering the
landed q2 rows with the canonical odd cotangent pairing exposes
**540 exact
coefficients in 8
ordered field-content sectors**. The first normalized witness has coefficient
`4`. Thus the source receiver
convention is nilpotent but not canonically cyclic as written.

The defect is repaired by one explicit involutive coordinate translation:

```text
T(h,c,omega,h_star,c_star,omega_star)
  = (h,c,omega,h_star,-c_star,-omega_star).
```

This changes `q1_cstar_hstar`, `q1_omegastar_hstar` and `q2_cstar_hhstar__forward`, `q2_cstar_hhstar__reverse`, `q2_omegastar_hhstar__forward`, `q2_omegastar_hhstar__reverse`; every other q1/q2 component is
unchanged. Because the translated operations are exact conjugates, q1 squared
and the complete 18-channel/51-path q1q2 identity are preserved. The exact
component receiver then finds **0
cyclicity defects** among all 932 expanded non-Bach coefficients.

## Canonical pairing

The portable minimal carrier has thirty independent component coordinates and
the canonical support-local odd pairing has rank thirty. Symmetric off-diagonal
metric components carry multiplicity two; the vector and scalar ghost pairs
carry multiplicity one. One pairing argument is compactly supported, so every
formal integration-by-parts boundary term vanishes.

## Why the Bach rows are included without a 19,401-term transpose

The action normalization is pinned. Its linear Bach Euler operator is the
second variation of the local Weyl action, hence formally self-adjoint. The
trilinear metric vertex is its third variation, so
`integral h3 K_g(h1,h2)` is symmetric in all three directions. This exact
variational theorem completes the q1 and q2 metric sectors; it is not replaced
by a finite-background sample.

## Checks

| Check | Status | Evidence or boundary |
|---|---|---|
| `canonical_pairing_nondegenerate` | `VERIFIED` | thirty independent component rows, thirty nonzero ordered entries and exact rank thirty |
| `sign_translation_involutive_and_typed` | `VERIFIED` | T is diagonal, T^2=1, and preserves every generator degree, parity, tensor type and support |
| `q1_squared_zero` | `VERIFIED_BY_EXACT_CONJUGATION` | q1'=T q1 T^-1 and the pinned source q1 squared is zero |
| `q1_q2_arity_two_nilpotency` | `VERIFIED_BY_EXACT_CONJUGATION` | q2'=T q2(T^-1,T^-1), so the pinned eighteen-channel/fifty-one-path identity is transported exactly |
| `BV_cyclicity_q1` | `VERIFIED` | the translated Noether rows are the negative formal adjoints of the Diff/Weyl gauge maps and the Bach Hessian is the second variation of the pinned action |
| `BV_cyclicity_q2` | `VERIFIED` | all 932 expanded non-Bach coefficients have zero defect modulo exact integration by parts; the hhh sector is the symmetric third variation of the pinned local Weyl action |
| `D_q1_commutator_zero` | `NOT_REPLAYED` | no background-specific full local D action is selected |
| `D_q2_derivation` | `NOT_REPLAYED` | no background-specific full local D action is selected |

## Gate boundary

This closes the canonical pairing and q1/q2 cyclicity only on the strict
six-generator minimal carrier. Local D, nonminimal and auxiliary pairing rows,
the continuum residual SDR, common snapshot hashes, Lorentzian Green data,
Hadamard and QME remain open. Gate A remains fail closed.

## Reproduction

```bash
python3 quantum-weyl/classical_import/build_strict_minimal_bv_cyclic_sign_reconciliation.py --check
python3 quantum-weyl/classical_import/check_strict_minimal_bv_cyclic_sign_reconciliation.py
python3 quantum-weyl/classical_import/verify_strict_minimal_bv_cyclic_sign_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_minimal_bv_cyclic_sign_reconciliation.py
```
