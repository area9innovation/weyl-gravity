#!/usr/bin/env python3
"""Build the migration-reviewed v2 static foundations explorer."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from foundations import build_matrix_site as v1

ROOT = v1.ROOT
FOUNDATIONS = v1.FOUNDATIONS
ASSETS = v1.ASSETS
V2_ASSETS = FOUNDATIONS / "matrix_site_v2_assets"
SITE = FOUNDATIONS / "site-v2"
RESULT = FOUNDATIONS / "results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json"
REPORT = FOUNDATIONS / "reports/matrix-explorer-site-v2.md"
CUBE = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V2.json"
AUDIT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json"
LADDER = v1.LADDER
LEDGERS = v1.LEDGERS
CREATED = "2026-08-12"
BASE_COMMIT = "24e988693bd9ee6874bedf9de476202c949a2e7e"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def site_link(path: str) -> str:
    return "sources/" + Path(path).as_posix()


def evidence_registry(cube: dict[str, Any], ladder: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Reuse the v1 resolver, but include evidence reviewed only for migration."""
    registry_cube = dict(cube)
    registry_cube["cells"] = [
        {**cell, "evidence": list(dict.fromkeys([*cell["evidence"], *cell.get("migration_evidence", [])]))}
        for cell in cube["cells"]
    ]
    return v1.evidence_registry(registry_cube, ladder)


def complete_surface(cube: dict[str, Any]) -> list[dict[str, Any]]:
    axes = {axis["id"]: axis for axis in cube["axes"]}
    foundations = [x["id"] for x in axes["FOUNDATION"]["keys"]]
    carriers = [x["id"] for x in axes["CARRIER"]["keys"]]
    obligations = [x["id"] for x in axes["REFINED_OBLIGATION"]["keys"]]
    emitted = {(x["foundation"], x["carrier"], x["obligation"]): x for x in cube["cells"]}
    cells: list[dict[str, Any]] = []
    for obligation in obligations:
        for foundation in foundations:
            for carrier in carriers:
                coordinate = (foundation, carrier, obligation)
                if coordinate in emitted:
                    cells.append({**emitted[coordinate], "emitted": True})
                else:
                    cells.append({
                        "foundation": foundation,
                        "carrier": carrier,
                        "obligation": obligation,
                        "status": "NOT_MAPPED",
                        "evidence": [],
                        "parent_obligation": None,
                        "migration_relation": "NOT_EMITTED",
                        "migration_status": "NOT_REVIEWED",
                        "migration_evidence": [],
                        "migration_rationale": "This coordinate was not emitted by cube v2, so no parent-evidence migration decision exists.",
                        "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
                        "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
                        "emitted": False,
                    })
    return cells


def build_dataset() -> dict[str, Any]:
    cube, audit, ladder = v1.load(CUBE), v1.load(AUDIT), v1.load(LADDER)
    cells = complete_surface(cube)
    evidence = evidence_registry(cube, ladder)
    status_counts: dict[str, int] = {}
    migration_counts: dict[str, int] = {}
    for cell in cells:
        status_counts[cell["status"]] = status_counts.get(cell["status"], 0) + 1
        migration_counts[cell["migration_status"]] = migration_counts.get(cell["migration_status"], 0) + 1
    dataset = {
        "schema_version": "foundational-matrix-explorer-data-v2",
        "title": "Reverse Mathematics × Physics Atlas",
        "created": CREATED,
        "dependency_tags": cube["dependency_tags"],
        "axes": cube["axes"],
        "groups": v1.GROUPS,
        "statuses": cube["cell_statuses"],
        "migration_statuses": cube["migration_statuses"] + [{"id": "NOT_REVIEWED", "meaning": "The coordinate was not emitted by cube v2, so no migration review was required."}],
        "counts": {
            "cartesian_total": cube["dimensions"]["cartesian_total"],
            "emitted": cube["dimensions"]["emitted_cells"],
            "coverage_classified": cube["dimensions"]["coverage_classified_cells"],
            "qualified": cube["dimensions"]["coverage_classified_cells"],
            "migration_reviewed": cube["dimensions"]["migration_reviewed_cells"],
            "migration_pending": cube["dimensions"]["migration_pending_cells"],
            "migration_unresolved": cube["dimensions"]["migration_pending_cells"],
            "reviewed_no_transfer": cube["dimensions"]["reviewed_no_transfer_cells"],
            "not_mapped": status_counts["NOT_MAPPED"],
            "synthetic_not_mapped": sum(not cell["emitted"] for cell in cells),
            "status_counts": dict(sorted(status_counts.items())),
            "migration_status_counts": dict(sorted(migration_counts.items())),
            "evidence_records": len(evidence),
        },
        "cells": cells,
        "evidence": evidence,
        "ladder": ladder["ladder"],
        "graph": ladder["typed_relation_graph"],
        "boundaries": {
            "cube": cube["does_not_establish"],
            "migration_audit": audit["does_not_establish"],
            "ladder": ladder["does_not_establish"],
            "navigation": [
                "Coverage status and migration-review status answer different questions.",
                "REVIEWED_NO_TRANSFER and NOT_MAPPED are not literature-absence claims.",
                "The 124 synthetic coordinates have not received the migration review applied to the 452 emitted coordinates.",
                "Neighbor counts and candidate views are navigation aids, not theorem rankings.",
            ],
        },
        "source_links": {
            "cube": site_link(rel(CUBE)),
            "migration_audit": site_link(rel(AUDIT)),
            "ladder": site_link(rel(LADDER)),
            "cube_report": site_link("foundations/reports/refined-intersection-cube-v2.md"),
            "migration_audit_report": site_link("foundations/reports/intersection-cube-migration-audit-v2.md"),
            "ladder_report": site_link("foundations/reports/cylinder-wave-strength-ladder.md"),
        },
    }
    dataset["canonical_digest"] = v1.canonical_digest(dataset)
    return dataset


def render_report(result: dict[str, Any]) -> str:
    counts = result["counts"]
    return f"""# Migration-reviewed static foundations matrix explorer v2

**Result:** `{result['result_id']}`

**Lifecycle:** `{result['lifecycle']}`

**Dependency tags:** {', '.join(f'`{x}`' for x in result['dependency_tags'])}

## Outcome

`foundations/site-v2/index.html` presents all **576** Cartesian coordinates.
The **452** cube-emitted coordinates now have separate coverage and migration
review fields: **{counts['migration_reviewed']} reviewed**, **{counts['migration_pending']} pending**.
Of those, **{counts['reviewed_no_transfer']}** parent-evidence reviews found no
licensed transfer to the refined child. Their coverage is `NOT_MAPPED`, which
is not a literature-absence claim. The remaining **{counts['synthetic_not_mapped']}**
coordinates are browser-visible complements that have not been assessed.

Coverage is classified for **{counts['coverage_classified']}** emitted cells.
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

Serve `foundations/site-v2/` from any static host, or open `index.html` directly.
All source links resolve inside the standalone directory; no remote code is used.

## Boundaries

This site does not establish:

""" + "\n".join(f"- {item}" for item in result["does_not_establish"]) + "\n"


def generated() -> dict[Path, bytes]:
    dataset = build_dataset()
    data_json = (json.dumps(dataset, indent=2, ensure_ascii=False) + "\n").encode()
    index = (ASSETS / "index.html").read_text().replace(
        '<script src="app.js"></script>',
        '<script src="app.js"></script>\n  <script src="app-v2.js"></script>',
    ).encode()
    outputs: dict[Path, bytes] = {
        SITE / "index.html": index,
        SITE / "styles.css": (ASSETS / "styles.css").read_bytes(),
        SITE / "app.js": (ASSETS / "app.js").read_bytes(),
        SITE / "app-v2.js": (V2_ASSETS / "app-v2.js").read_bytes(),
        SITE / "data.json": data_json,
        SITE / "data.js": b"window.MATRIX_EXPLORER_DATA = " + data_json.rstrip() + b";\n",
    }
    local_evidence_paths = [ROOT / item["result_path"] for item in dataset["evidence"].values() if item["kind"] == "LOCAL_RESULT"]
    local_report_paths = [ROOT / item["report_path"] for item in dataset["evidence"].values() if item["kind"] == "LOCAL_RESULT" and item.get("report_path")]
    reports = [
        FOUNDATIONS / "reports/refined-intersection-cube-v2.md",
        FOUNDATIONS / "reports/intersection-cube-migration-audit-v2.md",
        FOUNDATIONS / "reports/cylinder-wave-strength-ladder.md",
    ]
    bundled_sources = sorted(set([CUBE, AUDIT, LADDER, *LEDGERS, *local_evidence_paths, *local_report_paths, *reports]))
    for source in bundled_sources:
        outputs[SITE / "sources" / source.relative_to(ROOT)] = source.read_bytes()
    input_paths = sorted(set([Path(__file__).resolve(), *bundled_sources, ASSETS / "index.html", ASSETS / "styles.css", ASSETS / "app.js", V2_ASSETS / "app-v2.js"]))
    manifest = {
        "schema_version": "foundational-matrix-explorer-manifest-v2",
        "created": CREATED,
        "generator": rel(Path(__file__).resolve()),
        "canonical_data_digest": dataset["canonical_digest"],
        "inputs": [{"path": rel(path), "sha256": v1.sha(path)} for path in input_paths],
        "outputs": [{"path": rel(path), "sha256": v1.sha_bytes(content), "bytes": len(content)} for path, content in sorted(outputs.items())],
    }
    manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode()
    outputs[SITE / "manifest.json"] = manifest_bytes
    result = {
        "schema_version": "foundational-matrix-explorer-site-v2",
        "result_id": "FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2",
        "result_kind": "STATIC_EVIDENCE_EXPLORER",
        "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
        "created": CREATED,
        "repository_base_commit": BASE_COMMIT,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "scope": "Deterministic static exploration surface over the migration-reviewed foundations cube and cylinder implication ladder.",
        "counts": dataset["counts"],
        "features": ["sixteen 6x6 heatmaps", "separate coverage and migration-review states", "migration evidence inspector", "multi-select filters", "full-text search", "cell inspector", "one-axis neighbors", "two-cell comparison", "URL permalinks", "filtered JSON and CSV export", "research-brief export", "typed implication graph", "strength ladder", "evidence catalogue"],
        "provenance": {"manifest": rel(SITE / "manifest.json"), "manifest_sha256": v1.sha_bytes(manifest_bytes), "canonical_data_digest": dataset["canonical_digest"]},
        "independent_checker": {"path": "foundations/check_matrix_site_v2.py", "expected_cells": 576, "expected_emitted": 452, "expected_synthetic_not_mapped": 124, "expected_total_not_mapped": 212, "expected_evidence_records": 51, "expected_digest": dataset["canonical_digest"]},
        "claim_flags": {"static_site_generated": True, "all_cartesian_coordinates_visible": True, "all_emitted_migrations_reviewed": True, "coverage_and_migration_separated": True, "all_used_evidence_resolved": True, "scientific_claims_duplicated_by_hand": False, "literature_complete": False, "unmapped_means_absent": False, "reviewed_no_transfer_means_absent": False, "priority_score_is_theorem": False, "new_lorentzian_claim": False},
        "does_not_establish": ["literature completeness", "coverage for the 88 reviewed-no-transfer coordinates", "that NOT_MAPPED means no literature exists", "that the 124 synthetic coordinates are coherent", "a weakest mathematical base", "a theorem ranking from interface order or neighbor counts", "a new Lorentzian-causal result"],
        "human_report": "foundations/reports/matrix-explorer-site-v2.md",
    }
    outputs[RESULT] = (json.dumps(result, indent=2) + "\n").encode()
    outputs[REPORT] = render_report(result).encode()
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated artifacts differ")
    args = parser.parse_args()
    outputs = generated()
    stale = [rel(path) for path, content in outputs.items() if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2: generated artifacts current")
        return 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2: wrote {len(outputs)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
