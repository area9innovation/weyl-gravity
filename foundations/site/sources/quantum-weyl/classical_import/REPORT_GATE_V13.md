# Classical import Gate-A reconciliation v13

**Result:** `CLASSICAL_IMPORT_GATE_V13_RECONCILIATION`

**Dependency:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

**Gate A:** `FAIL_CLOSED`

The primary source supplies the previously omitted nonlinear boost terms.
Exact replay shows that the Weyl/boost internal algebra is Abelian and the
shifted auxiliary tensor is invariant.  The scoped manifest has
3 nonzero ghost-antifield families and
0 additional
Weyl/boost families.  Consequently the seven serialized auxiliary cubic
families are now an exhaustive family census.

Gate A remains fail closed with
**0** accepted
common hashes.  Census completion is not source-q2 assembly: the combined
386-row payload and its `q1/q2`, cyclicity and `D` identities remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v13_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v13_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v13_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v13_reconciliation
```
