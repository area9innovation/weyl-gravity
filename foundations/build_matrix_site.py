#!/usr/bin/env python3
"""Build the self-contained foundations matrix explorer.

The browser receives a normalized projection of authoritative JSON artifacts.
It never owns a second, hand-maintained copy of a scientific claim.  The build
also materializes every un-emitted Cartesian coordinate as NOT_MAPPED with an
explicit non-absence boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

# The unversioned command is the canonical deployment entry point.  V1 remains
# importable below for historical artifact reconstruction; direct execution
# delegates to the migration-reviewed current builder.
if __name__ == "__main__":
    _ROOT = Path(__file__).resolve().parents[1]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))
    from foundations.build_matrix_site_v2 import main as _current_main
    raise SystemExit(_current_main())

ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
ASSETS = FOUNDATIONS / "matrix_site_assets"
SITE = FOUNDATIONS / "site"
RESULT = FOUNDATIONS / "results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V1.json"
REPORT = FOUNDATIONS / "reports/matrix-explorer-site.md"
CUBE = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json"
LADDER = FOUNDATIONS / "results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json"
LEDGERS = [
    FOUNDATIONS / "literature-ledger.json",
    FOUNDATIONS / "literature-supplement-known-attempts-v1.json",
    FOUNDATIONS / "literature-expansion-v2.json",
]
CREATED = "2026-08-12"
BASE_COMMIT = "448435587a0e7fe80e8f746328b427f2e0e42df7"

GROUPS = [
    {"id": "STATES", "label": "States and probability", "obligations": ["STATE_EXISTENCE", "STATE_REPRESENTATION", "PROBABILITY_RULE", "PHYSICAL_STATE_SELECTION"]},
    {"id": "DYNAMICS", "label": "Dynamics and causality", "obligations": ["GENERATOR_SPECTRAL_DYNAMICS", "EVOLUTION_WELLPOSEDNESS", "CAUSAL_PROPAGATION_GREEN"]},
    {"id": "GAUGE", "label": "Kinematics and gauge", "obligations": ["KINEMATICS_OBSERVABLES", "GAUGE_BV_COHOMOLOGY"]},
    {"id": "QUANTUM", "label": "Interaction and quantum consistency", "obligations": ["INTERACTION_CONSTRUCTION", "COUNTERTERM_CLASSIFICATION", "ANOMALY_CLASSIFICATION", "RENORMALIZED_PRODUCTS", "QME_RESTORATION", "RESIDUAL_QUANTUM_TRANSFER"]},
    {"id": "LIMITS", "label": "Reconstruction and limits", "obligations": ["RECONSTRUCTION_LIMITS"]},
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def site_link(path: str) -> str:
    return "sources/" + Path(path).as_posix()


def normalize_literature(entry: dict[str, Any], ledger: Path) -> dict[str, Any]:
    artifact = entry.get("artifact", {})
    return {
        "id": entry["id"],
        "kind": "LITERATURE",
        "citation": entry.get("citation", entry["id"]),
        "year": entry.get("year"),
        "source_kind": entry.get("source_kind", "PRIMARY_RESEARCH"),
        "stable_url": entry.get("stable_url"),
        "artifact_status": artifact.get("status", entry.get("artifact_status", "METADATA_ONLY")),
        "artifact_sha256": artifact.get("sha256"),
        "supported_statements": entry.get("supported_statements", [entry.get("supported_statement")] if entry.get("supported_statement") else []),
        "boundary": entry.get("boundary", "No boundary supplied."),
        "ledger": rel(ledger),
        "ledger_link": site_link(rel(ledger)),
    }


def evidence_registry(cube: dict[str, Any], ladder: dict[str, Any]) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for path in sorted((FOUNDATIONS / "results").glob("*.json")):
        if path == RESULT:
            continue
        item = load(path)
        evidence_id = item.get("result_id")
        if not evidence_id:
            continue
        report = item.get("human_report")
        registry[evidence_id] = {
            "id": evidence_id,
            "kind": "LOCAL_RESULT",
            "result_kind": item.get("result_kind"),
            "lifecycle": item.get("lifecycle"),
            "dependency_tags": item.get("dependency_tags", []),
            "claim_flags": item.get("claim_flags", {}),
            "does_not_establish": item.get("does_not_establish", []),
            "result_path": rel(path),
            "result_link": site_link(rel(path)),
            "report_path": report,
            "report_link": site_link(report) if report else None,
            "sha256": sha(path),
        }
    for ledger in LEDGERS:
        for entry in load(ledger)["entries"]:
            registry[entry["id"]] = normalize_literature(entry, ledger)
    # The two newly reviewed records live in the ladder pending ledger v3.
    for entry in ladder["literature_dependencies"]:
        registry[entry["id"]] = normalize_literature(entry, LADDER)
    used = {evidence for cell in cube["cells"] for evidence in cell["evidence"]}
    missing = sorted(used - registry.keys())
    if missing:
        raise ValueError("unresolved evidence IDs: " + ", ".join(missing))
    return {key: registry[key] for key in sorted(used)}


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
                        "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
                        "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
                        "emitted": False,
                    })
    return cells


def canonical_digest(dataset: dict[str, Any]) -> str:
    projection = {
        "axes": dataset["axes"],
        "cells": dataset["cells"],
        "evidence": dataset["evidence"],
        "ladder": dataset["ladder"],
        "graph": dataset["graph"],
    }
    return sha_bytes(json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def build_dataset() -> dict[str, Any]:
    cube, ladder = load(CUBE), load(LADDER)
    cells = complete_surface(cube)
    evidence = evidence_registry(cube, ladder)
    counts: dict[str, int] = {}
    for cell in cells:
        counts[cell["status"]] = counts.get(cell["status"], 0) + 1
    dataset = {
        "schema_version": "foundational-matrix-explorer-data-v1",
        "title": "Reverse Mathematics × Physics Atlas",
        "created": CREATED,
        "dependency_tags": cube["dependency_tags"],
        "axes": cube["axes"],
        "groups": GROUPS,
        "statuses": cube["cell_statuses"] + [{"id": "NOT_MAPPED", "meaning": "This coordinate has not been assessed; no absence or incoherence is inferred."}],
        "counts": {
            "cartesian_total": cube["dimensions"]["cartesian_total"],
            "emitted": cube["dimensions"]["migrated_or_overlaid_cells"],
            "qualified": cube["dimensions"]["qualified_cells"],
            "migration_unresolved": cube["dimensions"]["migration_unresolved_cells"],
            "not_mapped": counts["NOT_MAPPED"],
            "status_counts": dict(sorted(counts.items())),
            "evidence_records": len(evidence),
        },
        "cells": cells,
        "evidence": evidence,
        "ladder": ladder["ladder"],
        "graph": ladder["typed_relation_graph"],
        "boundaries": {
            "cube": cube["does_not_establish"],
            "ladder": ladder["does_not_establish"],
            "navigation": [
                "Colors classify evidence state, not truth or scientific importance.",
                "NOT_MAPPED and MIGRATION_UNRESOLVED are not literature-absence claims.",
                "Neighbor counts and candidate views are navigation aids, not theorem rankings.",
            ],
        },
        "source_links": {
            "cube": site_link(rel(CUBE)),
            "ladder": site_link(rel(LADDER)),
            "cube_report": site_link("foundations/reports/refined-intersection-cube.md"),
            "ladder_report": site_link("foundations/reports/cylinder-wave-strength-ladder.md"),
        },
    }
    dataset["canonical_digest"] = canonical_digest(dataset)
    return dataset


def render_report(result: dict[str, Any]) -> str:
    return f"""# Static foundations matrix explorer

**Result:** `{result['result_id']}`

**Lifecycle:** `{result['lifecycle']}`

**Dependency tags:** {', '.join(f'`{x}`' for x in result['dependency_tags'])}

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

""" + "\n".join(f"- {item}" for item in result["does_not_establish"]) + "\n"


def generated() -> dict[Path, bytes]:
    dataset = build_dataset()
    data_json = (json.dumps(dataset, indent=2, ensure_ascii=False) + "\n").encode()
    outputs: dict[Path, bytes] = {
        SITE / "index.html": (ASSETS / "index.html").read_bytes(),
        SITE / "styles.css": (ASSETS / "styles.css").read_bytes(),
        SITE / "app.js": (ASSETS / "app.js").read_bytes(),
        SITE / "data.json": data_json,
        SITE / "data.js": b"window.MATRIX_EXPLORER_DATA = " + data_json.rstrip() + b";\n",
    }
    local_evidence_paths = [ROOT / item["result_path"] for item in dataset["evidence"].values() if item["kind"] == "LOCAL_RESULT"]
    local_report_paths = [ROOT / item["report_path"] for item in dataset["evidence"].values() if item["kind"] == "LOCAL_RESULT" and item.get("report_path")]
    bundled_sources = sorted(set([CUBE, LADDER, *LEDGERS, *local_evidence_paths, *local_report_paths, FOUNDATIONS / "reports/refined-intersection-cube.md", FOUNDATIONS / "reports/cylinder-wave-strength-ladder.md"]))
    for source in bundled_sources:
        outputs[SITE / "sources" / source.relative_to(ROOT)] = source.read_bytes()
    input_paths = [Path(__file__).resolve(), *bundled_sources, ASSETS / "index.html", ASSETS / "styles.css", ASSETS / "app.js"]
    input_paths = sorted(set(input_paths))
    manifest = {
        "schema_version": "foundational-matrix-explorer-manifest-v1",
        "created": CREATED,
        "generator": rel(Path(__file__).resolve()),
        "canonical_data_digest": dataset["canonical_digest"],
        "inputs": [{"path": rel(path), "sha256": sha(path)} for path in input_paths],
        "outputs": [{"path": rel(path), "sha256": sha_bytes(content), "bytes": len(content)} for path, content in sorted(outputs.items())],
    }
    manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode()
    outputs[SITE / "manifest.json"] = manifest_bytes
    result = {
        "schema_version": "foundational-matrix-explorer-site-v1",
        "result_id": "FOUNDATIONAL_MATRIX_EXPLORER_SITE_V1",
        "result_kind": "STATIC_EVIDENCE_EXPLORER",
        "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
        "created": CREATED,
        "repository_base_commit": BASE_COMMIT,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "scope": "Deterministic static exploration surface over the refined foundations cube and cylinder implication ladder.",
        "counts": dataset["counts"],
        "features": ["sixteen 6x6 heatmaps", "multi-select filters", "full-text search", "cell inspector", "one-axis neighbors", "two-cell comparison", "URL permalinks", "filtered JSON and CSV export", "research-brief export", "typed implication graph", "strength ladder", "evidence catalogue"],
        "provenance": {"manifest": rel(SITE / "manifest.json"), "manifest_sha256": sha_bytes(manifest_bytes), "canonical_data_digest": dataset["canonical_digest"]},
        "independent_checker": {"path": "foundations/check_matrix_site.py", "expected_cells": 576, "expected_emitted": 452, "expected_not_mapped": 124, "expected_evidence_records": 51, "expected_digest": dataset["canonical_digest"]},
        "claim_flags": {"static_site_generated": True, "all_cartesian_coordinates_visible": True, "all_used_evidence_resolved": True, "scientific_claims_duplicated_by_hand": False, "literature_complete": False, "unmapped_means_absent": False, "priority_score_is_theorem": False, "new_lorentzian_claim": False},
        "does_not_establish": ["literature completeness", "that every Cartesian coordinate is scientifically coherent", "that NOT_MAPPED means no literature exists", "that MIGRATION_UNRESOLVED is a scientific gap", "a weakest mathematical base", "a theorem ranking from interface order or neighbor counts", "a new Lorentzian-causal result"],
        "human_report": "foundations/reports/matrix-explorer-site.md",
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
            print("FOUNDATIONAL_MATRIX_EXPLORER_SITE_V1: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_MATRIX_EXPLORER_SITE_V1: generated artifacts current")
        return 0
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(f"FOUNDATIONAL_MATRIX_EXPLORER_SITE_V1: wrote {len(outputs)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
