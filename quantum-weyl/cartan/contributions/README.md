# Cross-programme contribution

The quantum Cartan rail contributes to the shared `D`-quotient dossier using
the exact claim key

```text
(quantum, vacuum_cylinder, D_compact, compact_quantum, QUANTUM)
```

The current contribution is `BLOCKED` and has `verdict: null`.  Its evidence
is the Cartan comparison certificate at commit
`faceb39e5427443320395f961107ba74b4800890`; the generator verifies that the
certificate bytes at that commit reproduce the stored SHA-256 digest and are
identical to the working certificate.

The receipt now includes the setting-specific 54-row Berger classical
`D` action and the conditional 54-to-26 causal reduction.  It therefore
carries `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, and `LORENTZIAN-CAUSAL`
dependency tags.  The retained Green/Hadamard endpoint and the quantum Ward
map remain open, so this does not change the null verdict.

The shared programme dossier consumes this record directly.  Its evidence
path is relative to the `symplectic-reconstruction` project root, matching the
portable convention used by the other registered team contributions.

Reproduce it from the repository root:

```bash
PYTHONPATH=quantum-weyl python3 -m cartan.contribution --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/cartan/tests/test_contribution.py -v
```

The machine record is
[`QUANTUM_CARTAN_BLOCKED.json`](QUANTUM_CARTAN_BLOCKED.json).
