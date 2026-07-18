# Analytic-operator classical-snapshot attribution

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The accepted round-`S4` TT dictionary, physical full-BV multiplicity ledger,
and Euler coefficient name analytic producer commit `318589ff...`. That is a
producer commit, not a new classical BV datum.

The exact Git tree at that commit contains the same
`CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2` blob as the current repository.
The export identifies classical snapshot `3e15eafa...`, and all five canonical
generator, atom, differential, dependency, and scope hashes agree with the
independently replayed local-BV import. The certificate records both the Git
blob SHA-1 and byte SHA-256 and binds all three physical analytic artifacts by
content hash.

This closes snapshot attribution only. It does not determine the `C2`
coefficient, construct a regulator, compute a Slavnov insertion, or decide the
QME.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m classical_import.analytic_operator_snapshot_attribution --check
PYTHONPATH=quantum-weyl python3 -m classical_import.verify_analytic_operator_snapshot_attribution
PYTHONPATH=quantum-weyl python3 -m unittest classical_import.tests.test_analytic_operator_snapshot_attribution
```
