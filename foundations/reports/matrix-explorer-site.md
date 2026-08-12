# Static foundations matrix explorer

**Result:** `FOUNDATIONAL_MATRIX_EXPLORER_SITE_V1`

**Lifecycle:** `VERIFIED_NAVIGATION_ARTIFACT`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Outcome

`foundations/site/index.html` is a self-contained static research interface over
the refined foundations cube. It exposes all **576** Cartesian coordinates:
452 emitted evidence classifications and 124 synthesized `NOT_MAPPED` entries
whose boundary explicitly forbids interpreting them as literature absence.

The interface provides sixteen coordinated 6 × 6 heatmaps, multi-select axis
and status filters, full-text evidence search, URL permalinks, a detailed cell
inspector, one-axis neighbors, two-cell comparison, filtered JSON/CSV export,
research-brief export, a typed implication graph, the cylinder strength ladder,
and a searchable 51-record evidence catalogue.

## Build and verification

```text
python3 foundations/build_matrix_site.py
python3 foundations/build_matrix_site.py --check
python3 foundations/check_matrix_site.py
python3 foundations/verify_matrix_site.py
python3 -m unittest foundations.tests.test_matrix_site
```

The build fails closed on unresolved evidence IDs. Scientific text is projected
from the authoritative cube, ladder, local results, and literature ledgers;
the browser assets contain no separately maintained cell claims.

## Deployment

Serve `foundations/site/` from any static host, or open `index.html` directly.
The data are loaded from a generated JavaScript assignment, so `file://` use
does not depend on browser permission to fetch local files. Exact evidence
JSON, reports, and literature ledgers referenced by the interface are copied
into `site/sources/`, so provenance links survive standalone deployment.

## Boundaries

This site does not establish:

- literature completeness
- that every Cartesian coordinate is scientifically coherent
- that NOT_MAPPED means no literature exists
- that MIGRATION_UNRESOLVED is a scientific gap
- a weakest mathematical base
- a theorem ranking from interface order or neighbor counts
- a new Lorentzian-causal result
