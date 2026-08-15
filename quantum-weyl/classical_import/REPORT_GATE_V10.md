# Classical import Gate-A reconciliation v10

**Result:** `CLASSICAL_IMPORT_GATE_V10_RECONCILIATION`
**Dependency:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

## Outcome

The receiver now knows **7** required
cubic block families.  The exact tables contain **72**
nonzero `h-f_hat-f_hat` source coefficients, **22**
vv field-map coefficients and **16**
cotangent-partner coefficients.  All **4** vv
canonicality slices have **0** defects.

This closes the vv BV-lift sector.  The hh/hv and three Diff component families
remain open, and the nonlinear Weyl/boost ghost-antifield manifest is not yet
exhaustive.  The 72-to-zero shifted-mass comparison proves that the vv shift
alone is insufficient; it does not obstruct a further normalization.

Gate A remains fail closed with **0**
accepted hashes.  M1 and M3--M6 remain independent blockers.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v10_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v10_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v10_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v10_reconciliation
```
