# Classical import Gate-A reconciliation v11

**Result:** `CLASSICAL_IMPORT_GATE_V11_RECONCILIATION`
**Dependency:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

## Outcome

The curved quadratic auxiliary transformation now has
**1392 hh**, **76 hv**, and
**22 vv** field coefficients.  Formal adjunction on
the 386-row pairing produces **3907** collected
cotangent coefficients with **0** defects over
150 metric and 4
vector variational slices.

This completes the quadratic BV cotangent lift, not the interacting import.
The three Diff auxiliary representation families and exhaustive nonlinear
Weyl/boost ghost-antifield census remain open.  No source q2/q3 hash is accepted,
and Gate A remains fail closed with
**0** accepted hashes.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v11_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v11_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v11_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v11_reconciliation
```
