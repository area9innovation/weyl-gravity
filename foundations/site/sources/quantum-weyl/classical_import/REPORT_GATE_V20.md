# Classical import Gate-A reconciliation v20

**Result:** `CLASSICAL_IMPORT_GATE_V20_RECONCILIATION`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

**Gate A:** `FAIL_CLOSED`

M4's local half is complete.  The common strict graph carrier has
386 rows, an exact rank-386
odd pairing with 410 ordered rational entries, and
zero combined local cyclicity defects for q1, the endpoint SDR, D, q2 and q3.

The former `M4_FULL_CYCLIC_PAIRING` requirement mixed two carrier types.  It is
replaced by completed `M4L_LOCAL_GRAPH_CYCLIC_PAIRING` and open
`M4R_TYPED_RESIDUAL_CYCLICITY`.  M4R depends on the still-missing M3R harmonic
comparison.  Gate A accepts no new top-level hash and remains fail closed with
M1, M3R and M4R open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v20_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v20_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v20_reconciliation.py
```
