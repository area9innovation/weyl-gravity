# Cross-programme contribution

The quantum Cartan rail contributes to the shared `D`-quotient dossier using
the exact claim key

```text
(quantum, vacuum_cylinder, D_compact, compact_quantum, QUANTUM)
```

The current contribution is `BLOCKED` and has `verdict: null`.  Its evidence
is the Cartan precertificate at commit
`04e9d20c2c5dd7b2d3fa62492fdc7e12e2fe1f61`; the generator verifies that the
certificate bytes at that commit reproduce the stored SHA-256 digest and are
identical to the working certificate.

Reproduce it from the repository root:

```bash
PYTHONPATH=quantum-weyl python3 -m cartan.contribution --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/cartan/tests/test_contribution.py -v
```

The machine record is
[`QUANTUM_CARTAN_BLOCKED.json`](QUANTUM_CARTAN_BLOCKED.json).
