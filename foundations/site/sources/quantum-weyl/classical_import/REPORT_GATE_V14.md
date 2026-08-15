# Classical import Gate-A reconciliation v14

**Result:** `CLASSICAL_IMPORT_GATE_V14_RECONCILIATION`
**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

The arity-two source operation is now one accepted common object.  It binds
22 minimal operations and
**2064 auxiliary component
coefficients**, then transports them through the exact canonical graph shear.
The accepted q2 hash is `0f1e23a5653db0666cbd02dea49f8961927d03ff4c72ed402fd24ba8f2ba4800`.

The graph-coordinate `q1/q2`, cyclicity and `D/q2` defect counts are
**0 / 0 / 0**.
The audit also retains the rejected convention: V1 left 336 exact defects;
the certified V2 `c_star` translation leaves zero.

Gate A remains fail closed.  Only one of seven top-level hashes is accepted,
the metric-dependent auxiliary `q3` is not assembled, and the final common
cyclic contraction is still blocked.  No causal Green, Hadamard or QME claim
is promoted.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v14_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v14_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v14_reconciliation.py
python3 -m unittest quantum-weyl.classical_import.tests.test_classical_import_gate_v14_reconciliation
```
