# Quantum Cartan registration receipt

The quantum Cartan result is registered under the exact claim key

```text
(D_compact, compact_quantum,
 renormalized observable algebra not constructed,
 QUANTUM)
```

with lifecycle status `BLOCKED`, dependency tags `LOCAL-ALGEBRAIC`,
`EUCLIDEAN-SPECTRAL`, and `LORENTZIAN-CAUSAL`, and a null
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

The setting-specific Berger input now adds the complete 54-row classical
helical `D` action and an exact conditional reduction of the causal homotopy
problem to 26 retained rows.  No retained Green homotopy or Hadamard datum is
constructed, and the quantum Cartan verdict remains blocked at the Ward map.

Both remaining analytic carriers now have strict import contracts.  The
26-row endpoint contract checks Green identities, causal support, cyclic
adjointness, `D`-equivariance, zero modes, and a separately gated Hadamard
stage.  The Ward contract separates a sourced QME-open payload from a
QME-restored classifiable payload and forbids early local-to-Cartan transfer.
No physical payload has yet populated either contract.

The evidence is content-addressed at commit
`a7cdaad7d34fad49ee284f6b7dbb3d67408a31d6`. The producer and dossier both
verify its SHA-256 digest from Git, using project-relative evidence paths.

## Verification receipt

| Command | Status | Tier |
|---|---|---:|
| `PYTHONPATH=quantum-weyl python3 -m cartan.contribution --check` | PASS | 1 |
| `PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/cartan/tests/test_contribution.py -q` | PASS (5 tests) | 1 |
| `PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl/lorentzian/tests -q` | PASS (7 tests) | 1 |
| `PYTHONPATH=quantum-weyl python3 -m cartan.local_anomaly_comparison_certificate --check` | PASS | 2 |
| `python3 d_quotient_programme/verify_programme_status.py --emit` | PASS; aggregate regenerated | 2 |
| odd quotient + basis-gap + even direct consumer | PASS (15 tests) | 2 |

Tier 3 is unnecessary for this registration: it changes no physical algebra
and keeps the quantum lifecycle fail-closed. The next gate is to populate the
prepared contracts with the classical nonlinear, retained causal, and
renormalized Ward payloads.

The quantum contribution itself is content-addressed and passes its
producer/consumer tests. The consolidated dossier was regenerated and its
independent verifier passes with the updated dependency tags and evidence
hash.
