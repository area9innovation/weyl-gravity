# Migration-reviewed static foundations matrix explorer v2

**Result:** `FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2`

**Lifecycle:** `VERIFIED_NAVIGATION_ARTIFACT`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Outcome

`foundations/site/index.html` presents all **576** Cartesian coordinates.
The **452** cube-emitted coordinates now have separate coverage and migration
review fields: **452 reviewed**, **0 pending**.
Of those, **88** parent-evidence reviews found no
licensed transfer to the refined child. Their coverage is `NOT_MAPPED`, which
is not a literature-absence claim. The remaining **124**
coordinates are browser-visible complements that have not been assessed.

Coverage is classified for **364** emitted cells.
The cell inspector exposes coverage evidence separately from migration-review
evidence and links to the explicit 112-decision audit ledger.

## Build and verification

```text
python3 foundations/build_matrix_site_v2.py
python3 foundations/build_matrix_site_v2.py --check
python3 foundations/check_matrix_site_v2.py
python3 foundations/verify_matrix_site_v2.py
python3 -m unittest foundations.tests.test_matrix_site_v2
```

The v1 cube and v1 site remain unchanged as historical artifacts. The v2 build
fails closed on unresolved evidence IDs and projects scientific text from the
cube, migration audit, strength ladder, local results, and literature ledgers.

## Deployment

Serve `foundations/site/` from any static host, or open `index.html` directly.
All source links resolve inside the standalone directory; no remote code is used.

## Boundaries

This site does not establish:

- literature completeness
- coverage for the 88 reviewed-no-transfer coordinates
- that NOT_MAPPED means no literature exists
- that the 124 synthetic coordinates are coherent
- a weakest mathematical base
- a theorem ranking from interface order or neighbor counts
- a new Lorentzian-causal result
