# Classical import Gate-A reconciliation v19

**Result:** `CLASSICAL_IMPORT_GATE_V19_RECONCILIATION`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

M3L is complete.  The common local endpoint manifest binds
386 graph rows to 30 local
endpoint species, contracts 356 rows, pins
10 source artifacts and records
17 canonical object hashes.  All
15 cross-certificate compatibility
links agree and the projected exact defect total is
0.

This is a scoped integration result, not a new residual map.  The global
W+/W- harmonic comparison remains M3R and must stay typed `REDUCED-MODE`.
Residual cyclicity remains M4.  No new top-level Gate-A hash is accepted, so
the gate remains fail closed with one of seven hashes and three missing
packages: M1, M3R and M4.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v19_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v19_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v19_reconciliation.py
```
