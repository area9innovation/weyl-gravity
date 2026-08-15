# Classical import Gate-A reconciliation v9

**Result:** `CLASSICAL_IMPORT_GATE_V9_RECONCILIATION`

**Lifecycle:** `CLASSIFIED`

**Gate A:** `FAIL_CLOSED`

## Outcome

The first nonlinear correction is now constructed.  The exact component
`F_(2)(v)=v tensor v-(1/2)g v^2` contributes **1**
to the source value **-1** in
`Omega(f_hat,q2(v,v))`.  The transformed source and candidate are both
**0**, with residual **0**.

This closes one necessary channel.  It does not serialize the complete 386-row
BV cotangent lift or replay all source q2/q3 channels.  The metric-dependent
`h-f_hat-f_hat` and ghost/antifield families remain explicit obligations.

Gate A remains fail closed with **0**
accepted hashes.  M1 and M3--M6 remain independent blockers.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v9_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v9_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v9_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v9_reconciliation
```
