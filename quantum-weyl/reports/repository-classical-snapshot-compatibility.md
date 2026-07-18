# Repository classical-snapshot compatibility

Dependency tag: `LOCAL-ALGEBRAIC`.

The physical analytic producer commit and the frozen local-BV cohomology
commit are distinct, but their classical content is now proven compatible.
The bridge compares five canonical hashes:

- minimal generators;
- local atoms;
- the classical BV differential;
- action and identity dependencies;
- grading and locality scope.

The local side is the independently replayed minimal-BV import. The analytic
side is the Git-tree attribution certificate proving that the producer commit
contains the byte-identical classical export. The strict compatibility
receiver accepts the bridge and rejects hash or proof-artifact mutations.

This removes only the snapshot-attribution blocker. The physical `C2`
coefficient, regulator and measure completion, Slavnov insertion, and QME
disposition remain open.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m classical_import.repository_classical_snapshot_compatibility --check
PYTHONPATH=quantum-weyl python3 -m classical_import.verify_repository_classical_snapshot_compatibility
PYTHONPATH=quantum-weyl python3 -m unittest classical_import.tests.test_repository_classical_snapshot_compatibility
```
