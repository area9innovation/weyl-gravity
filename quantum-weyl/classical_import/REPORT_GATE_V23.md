# Classical import Gate-A reconciliation v23

**Result:** `CLASSICAL_IMPORT_GATE_V23_RECONCILIATION`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

The unchanged 4490-coordinate
D-finite source has H0 dimension 470
and H1 dimension 0; it cannot
retract to a 940-coordinate residual carrier.

M3RC-A is nevertheless exact after a declared formal cotangent completion.
The 8980-coordinate doubled source
retracts onto 940 residual
coordinates, with full and residual odd-pairing ranks
8980 and
940 and zero declared defects.

M3RC-B remains open: no support/topology choice or harmonic integration theorem
identifies this algebraic dual with the action-derived BV dual.  M4R therefore
remains blocked, M1 remains last, and no new top-level hash is accepted.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v23_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v23_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v23_reconciliation.py
```
