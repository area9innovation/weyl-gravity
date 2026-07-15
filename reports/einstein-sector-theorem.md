# Einstein-sector theorem receipt

Date: 2026-07-15

## Result

Established the `LOCAL-ALGEBRAIC` theorem that every smooth
four-dimensional Einstein metric is Bach-flat, with the precise moduli-space
caveat that this gives a map to the conformally-Einstein pure-Weyl locus and
does not assert injectivity after the different gauge quotients.

Imported the existing `REDUCED-MODE` certificates to distinguish the local
helicity-`±2` one-particle module from its vanishing after the selected
closed-cylinder absolute residual quotient.  The result identifies Einstein
gravity as an exact, generally proper solution sector, not a global Weyl
gauge slice and not an automatic observable-algebra subtheory.

The next asymptotically flat theorem is commissioned under the
`LORENTZIAN-CAUSAL` tag with obligations `AF-E1` through `AF-E8`.  All remain
`OPEN`; no scattering, Cauchy, null-infinity, scale-generation, or quantum
claim was promoted.

## Provenance

Classical source commit:
`689d835ad2ff59b2de23b14d9610fe85dad24b95`.

The machine certificate records canonical SHA-256 hashes for:

- `bridge/certificates/free_bv_complex.json`;
- `bridge/certificates/metric_to_residual.json`;
- `bridge/certificates/cylinder_metric_preimages.json`;
- `covariant_completion/certificates/curved_helicity_two_channel.json`;
- `analytic_completion/certificates/completed_H4.json`.

All five inputs were unchanged in the working tree.  The verifier checks
their theorem-bearing fields as well as their recorded content hashes.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile bridge/einstein_sector/__init__.py bridge/einstein_sector/certificate.py bridge/einstein_sector/tests/test_certificate.py` | 0.03 s | PASS |
| 0 | `python3 -m json.tool bridge/certificates/einstein_sector_theorem.json` | 0.03 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.certificate --verify bridge/certificates/einstein_sector_theorem.json` | 0.04 s | PASS |
| 1 | `python3 -m unittest bridge.einstein_sector.tests.test_certificate` | 0.08 s | PASS (4 tests) |

The tests include fail-closed mutations of the one-particle residual rank and
of the asymptotically flat scattering flag.

Tier 2 was not run because no mathematical input, shared operator, schema, or
existing generated artifact changed; the unchanged content-addressed inputs
were checked by hash and imported field invariants.  Tier 3 was not run
because this change does not modify or promote an existing paper theorem or
quantum lifecycle state, alter shared core algebra, create a freeze/tag, or
prepare a release.

## Pre-existing shared-tree changes

The session began with unrelated modifications in the conformal paper,
publication notes, quantum local-BV/classical-import work, a GitHub workflow,
and files outside this subtree.  None is included in this theorem package.
