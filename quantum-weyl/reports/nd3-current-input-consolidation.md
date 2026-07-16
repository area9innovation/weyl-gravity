# ND3 current-input consolidation

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

The exact ND3 recurrence engine was already live, but its checked-in input
ledger still read the original `bootstrap-v1` snapshot. That snapshot
predated the complete support-local 54-row `q2`, its independent exact
replay, the retained 26-row transfer, and the repaired causal D-Cartan
contraction through arity two.

The current ND3 receipt now consumes those three content-addressed quantum
imports directly. It records:

- complete support-local `q2` on all 54 rows, independently replayed;
- exact retained `q2_26`, with `q1/q2` and cyclic identities verified;
- the exact 54-to-26 causal SDR lift;
- the cyclic two-sided-causal `iota_D^(2)` on all 54 rows.

The lower-arity physical chain is therefore no longer the ND3 blocker. The
remaining input gate is a versioned support-local `q3` export together with
an explicit `L_D^(3)` declaration. A zero `L_D^(3)` is acceptable only when
the classical export certifies it rather than leaving it implicit. The
export must also carry the arity-three `Q^2` identity, `D` equivariance,
odd-Darboux cyclicity, complete field/ghost/antifield coverage, exact
coefficient-domain metadata, hashes, and classical provenance.

This is a gate consolidation, not an arity-three verdict. It does not compute
the physical Cartan source, construct `iota_D^(3)`, establish a quartic
mixing theorem, construct Hadamard data, restore a QME, or make a quantum
claim.

```text
python3 quantum-weyl/transfer/arity_three_cartan_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_arity_three_cartan_certificate.py -v
```

## Verification receipt

| Tier | Command | Elapsed | Result |
|---:|---|---:|---|
| 0 | Python compilation, JSON parse, and scoped `git diff --check` | 0.1 s | PASS |
| 0 | `npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/arity-three-cartan-engine-v1.schema.json -d quantum-weyl/transfer/certificates/ND3_ARITY_THREE_CARTAN_ENGINE.json` | 1.39 s | PASS |
| 2 | ND3, nonlinear aggregate, causal-v2, and Hadamard certificate checks plus 21 focused tests | 3.64 s | PASS |

Tier 3 was not run: this change consolidates content-addressed gate status and
does not alter shared core algebra, promote a new theorem, freeze a release,
or change a mathematical input.
