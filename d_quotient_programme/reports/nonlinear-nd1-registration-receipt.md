# Nonlinear ND1 registration receipt

The nonlinear ND1 result is registered under the exact claim key

```text
(D_compact, compact_selected_residual_HT1,
 closed cylinder / selected endpoint-projected HT1 BFV q2 domain,
 INTERACTING)
```

with lifecycle status `PARTIAL`.  The registration does not change the
separate `compact_interacting` verdict, which remains `INPUT_GATE_BLOCKED`.

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| `python3 d_quotient_programme/verify_programme_status.py --emit` | 0.12 | PASS | 1 |
| `python3 d_quotient_programme/verify_programme_status.py --check --guards` | 0.13 | PASS (5 mutation guards) | 1 |
| `python3 quantum-weyl/transfer/d_derivation_certificate.py --check` | 3.57 | PASS | 2 |

`python3 -m py_compile d_quotient_programme/verify_programme_status.py` and
built-in JSON parsing of the contribution, registries, schemas, and generated
certificate are the Tier-0 syntax checks.  Tier 3 is unnecessary because this
registration changes no shared algebra, freezes no programme phase, and
promotes neither an interacting theorem nor a quantum or Lorentzian claim.
