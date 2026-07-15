# Branch A local-BV bootstrap receipt

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `INFRASTRUCTURE_VERIFIED`

Classical snapshot: `NOT_FROZEN`

Implemented an exact rational supercommutative coordinate-jet algebra and the
minimal Diff x Weyl BRST differential on `g`, `xi`, and `omega`.  The test
suite checks metadata validation, symmetric metric components, Koszul signs,
odd-jet nilpotence, the even total-derivative product rule, deterministic
canonical hashes, the odd graded Leibniz rule, and `Q_0^2=0` on all fifteen
independent four-dimensional minimal generators plus representative
derivative jets.

## Verification ledger

All commands were run from `physics/symplectic-reconstruction/` on 2026-07-15.

| Tier | Command | Elapsed | Status |
|---|---|---:|---|
| 0 | `PYTHONPATH=quantum-weyl python3 -m compileall -q quantum-weyl/local_bv` | 0.04 s | PASS |
| 0 | JSON parse command below | 0.12 s | PASS, 4 files |
| 1 | `PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl/local_bv/tests -v` | 1.81 s | PASS, 14 tests |
| 1 | `PYTHONPATH=quantum-weyl python3 -m local_bv.certificate --check` | 0.47 s | PASS |
| 1 | `python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json` | 0.03 s | PASS |

The exact Tier 0 structured-data parse command was:

```bash
for file in quantum-weyl/local_bv/schema/field_spec.schema.json quantum-weyl/local_bv/schema/bootstrap_certificate.schema.json quantum-weyl/local_bv/certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json quantum-weyl/certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json; do PYTHONPATH=quantum-weyl python3 -m json.tool "$file" >/dev/null || exit 1; done
```

Tier 2 was not run: no imported classical input, shared operator, spectral or
Lorentzian artifact is consumed by this bootstrap, so no existing transitive
certificate chain changed.  Tier 3 was not run: this is not a freeze, theorem
promotion, release, or change to an existing shared core algebra.

The receipt is fail-closed.  Antifield/nonminimal rows are `BLOCKED` on the
classical freeze.  Covariant canonical reduction, integration by parts,
Bianchi/Hodge relations, descent, the antifield spectral sequence, and full
counterterm/anomaly cohomology are `NOT_COMPUTED`.  No basis element or
anomaly coefficient is claimed.
