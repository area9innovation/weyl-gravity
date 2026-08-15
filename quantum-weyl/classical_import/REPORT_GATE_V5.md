# Classical import Gate-A reconciliation v5

**Result:** `CLASSICAL_IMPORT_GATE_V5_RECONCILIATION`

**Lifecycle:** `CLASSIFIED`

**Gate A:** `FAIL_CLOSED`

## Outcome

The strict minimal carrier now has one explicit canonical pairing convention.
The source receiver convention was nilpotent but produced
**540 exact non-Bach cyclicity
defects**. The involution `c_star -> -c_star`,
`omega_star -> -omega_star` preserves q1 squared and all 18 q1q2 channels / 51
paths, and reduces the exact defect count to
**0**.

## Scoped promotions

| Obligation | Status | Established | Still required |
|---|---|---|---|
| `cyclic_pairing` | `RECEIVER_VERIFIED_SCOPED` | The canonical support-local odd cotangent pairing is serialized on all thirty independent components of the six minimal generators, has rank thirty, and makes translated q1/q2 cyclic. | Extend the pairing and sign convention to every nonminimal, auxiliary and residual common-snapshot row and replay SDR cyclic side conditions. |
| `q2_cyclic_compatibility` | `RECEIVER_VERIFIED_SCOPED` | Translated minimal q2 has zero exact cyclicity defects: 932 non-Bach coefficients vanish modulo integration by parts and the metric cubic is the symmetric third action variation. | Replay after extending the pairing and translated convention to the common full nonminimal/residual carrier. |

The pairing has dimension and rank **30**. The 932 non-Bach
coefficients are normalized modulo exact integration by parts. The Bach unary
and cubic sectors are the second and third variations of the pinned action.

## What remains

M4 is repaired only in the minimal sector. The sign convention, q1/q2 and
pairing must be extended to the nonminimal, auxiliary and residual rows on one
common carrier. General `cyclic_compatibility` remains blocked on the full
pairing and residual SDR.

M2 is now dominated by local `D`: its background-specific generator has not
been selected on the common carrier, and neither D identity has been replayed.
M1, M3, M5 and M6 still block all seven common snapshot hashes.

## Gate verdict

Gate A remains fail closed with zero accepted common snapshot hashes. This
repair authorizes no Lorentzian propagator, Hadamard state, renormalized
product, QME restoration or publishable quantum result.

## Reproduction

```bash
python3 quantum-weyl/classical_import/build_classical_import_gate_v5_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v5_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v5_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v5_reconciliation.py
```
