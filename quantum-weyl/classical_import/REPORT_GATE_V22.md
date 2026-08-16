# Classical import Gate-A reconciliation v22

**Result:** `CLASSICAL_IMPORT_GATE_V22_RECONCILIATION`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

Direct M4R on the current 470-mode M3R target is obstructed.  All synthesis
columns land in degree-zero metric slots, so the degree-minus-one local BV
form pulls back to rank 0 with
nullity 470.

The exact 940-coordinate shifted-cotangent preflight has pairing rank
940, but its degree-one dual
comparison maps and action-pairing identification are not constructed.  Gate
A therefore inserts M3RC before M4R.  M1 remains the final common freeze; no
new top-level hash is accepted.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v22_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v22_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v22_reconciliation.py
```
