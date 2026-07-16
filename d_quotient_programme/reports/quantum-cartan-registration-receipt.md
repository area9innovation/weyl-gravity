# Quantum Cartan registration receipt

The quantum Cartan result is registered under the exact claim key

```text
(D_compact, compact_quantum,
 renormalized observable algebra not constructed,
 QUANTUM)
```

with lifecycle status `BLOCKED`, dependency tag `LOCAL-ALGEBRAIC`, and a null
verdict. The registered contribution now records complete even and odd AFN0
Weyl-ghost candidate quotients, the zero direct local bulk pullback to
`D_compact` on the closed vacuum cylinder, and the exact source/target degree
audit. The zero follows from `sigma_D=0`; it is not promoted to a vanishing
degree-zero Cartan defect.

The missing arrow is named explicitly: a renormalized local Ward insertion
constructed from an actual `Q_1`, `iota_D,1`, and `L_D,1` on the admissible
observable algebra. The registration does not promote the standard
Euclidean background coefficient to a BV Slavnov-breaking coefficient, and
does not claim a restored QME, residual quantum transfer, boundary result, or
Lorentzian causal theorem.

The evidence is content-addressed at commit
`db533d49e7644fc2482f472a8ed2f41e06469314`. The producer and dossier both
verify its SHA-256 digest from Git, using project-relative evidence paths.

## Verification receipt

| Command | Status | Tier |
|---|---|---:|
| `PYTHONPATH=quantum-weyl python3 -m cartan.contribution --check` | PASS | 1 |
| `PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/cartan/tests/test_contribution.py -q` | PASS (5 tests) | 1 |
| `PYTHONPATH=quantum-weyl python3 -m cartan.local_anomaly_comparison_certificate --check` | PASS | 2 |
| `python3 d_quotient_programme/verify_programme_status.py --emit` | DEFERRED: concurrent Berger update leaves the classical scalar-clock scope guard stale before quantum ingestion | 2 |
| odd quotient + basis-gap + even direct consumer | PASS (15 tests) | 2 |

Tier 3 is unnecessary for this registration: it changes no shared algebra and
keeps the quantum lifecycle fail-closed. The next gate is the full classical
antifield/Koszul--Tate and D-action import, followed by the regulated Slavnov
breaking and the renormalized Ward-insertion map.

The quantum contribution itself is committed, content-addressed, and passes
its producer/consumer tests. The consolidated dossier was deliberately not
overwritten after the new Berger classical input tripped its pre-existing
`classical scalar-clock obstruction scope drifted` guard; the classical team
can regenerate the aggregate once that independent guard is updated.
