# Classical import Gate-A reconciliation v21

**Result:** `CLASSICAL_IMPORT_GATE_V21_RECONCILIATION`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

M3R is complete in the represented D-finite global category.  The receiver
reconstructs 470 ordered W+/W- mode names at
energies two through six, checks a bijective E/A/L magnetic crosswalk, and
replays the retraction and both q0 chain identities with zero defects.

This does not make harmonic analysis support-local and does not supply raw
all-magnetic coordinate matrices or an all-energy smooth completion.  No new
top-level hash is accepted.  Gate A remains fail closed with M4R residual
cyclicity and M1 common freeze open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v21_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v21_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v21_reconciliation.py
```
