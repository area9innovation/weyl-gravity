# Quantum Cartan registration receipt

The quantum Cartan result is registered under the exact claim key

```text
(D_compact, compact_quantum,
 renormalized observable algebra not constructed,
 QUANTUM)
```

with lifecycle status `BLOCKED`, dependency tag `LOCAL-ALGEBRAIC`, and a null
verdict.  The registered contribution records exact first-order Cartan
quotient mechanics, the complete intrinsic Euler descent, and hash-bound AFN0
closure witnesses.  It does not promote an anomaly coefficient, restored
QME, residual quantum transfer, or Lorentzian causal theorem.

The evidence is content-addressed at commit
`2aec6ed91793d136c9a6d80a0f74b2b233775d49`.  The producer and dossier both
verify its SHA-256 digest from Git, using project-relative evidence paths.

## Verification receipt

| Command | Status | Tier |
|---|---|---:|
| `PYTHONPATH=quantum-weyl python3 -m cartan.contribution --check` | PASS | 1 |
| `pytest -q quantum-weyl/cartan/tests` | PASS (33 tests) | 2 |
| `python3 d_quotient_programme/verify_programme_status.py --check --guards` | PASS | 1 |
| contribution plus dossier checks under hash seeds `1,7,123` | PASS; identical contribution hash `1c636698...` | 1 |
| `pytest -q quantum-weyl/local_bv/tests` | PASS (189 tests, 125 subtests) | 2 |

Tier 3 is unnecessary for this registration: it changes no shared algebra and
keeps the quantum lifecycle fail-closed.  The next gate remains completion of
the AFN0 lower-form total complex and the admissible bulk Cartan-obstruction
basis.
