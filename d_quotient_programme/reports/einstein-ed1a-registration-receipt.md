# Einstein E-D1a registration receipt

The Einstein/boundary generator result is now registered under the exact
claim key

```text
(H_ESU, asymptotically_flat_full_Bach,
 fixed Minkowski conformal completion / full Bach phase space open,
 LORENTZIAN_CAUSAL)
```

with lifecycle status `PARTIAL` and dependency tags `LOCAL-ALGEBRAIC` and
`REDUCED-MODE`.  The lifecycle row names the causal problem; the evidence does
not carry a `LORENTZIAN-CAUSAL` dependency tag.  It therefore registers the
exact real generator dictionary and the fail-closed
`PHASE_SPACE_NOT_CLOSED` verdict without promoting a charge, causal-complex,
or scattering theorem.

The next gate is a boundary-preserving full Bach phase space followed by a
renormalized charge-and-flux calculation for the generator that actually
preserves it.

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| `python3 d_quotient_programme/verify_programme_status.py --emit` | 0.11 | PASS | 1 |
| `python3 d_quotient_programme/verify_programme_status.py --check --guards` | 0.11 | PASS (6 mutation guards) | 1 |
| `python3 -m unittest bridge.einstein_sector.tests.test_d_quotient_asymptotic_seed -v` | 0.78 | PASS (7 tests) | 2 |

`python3 -m py_compile d_quotient_programme/verify_programme_status.py` and
JSON parsing of the contribution, registries, schemas, and generated
certificate are the Tier-0 checks.  The Python environment does not provide
the optional `jsonschema` package, so the verifier enforces the contribution's
required scope and evidence fields directly.  Tier 3 is unnecessary because
this registration changes no shared algebra and promotes no Lorentzian causal
claim.
