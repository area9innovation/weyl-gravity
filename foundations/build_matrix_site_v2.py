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
SITE = FOUNDATIONS / "site"
RESULT = FOUNDATIONS / "results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json"
REPORT = FOUNDATIONS / "reports/matrix-explorer-site-v2.md"
CUBE = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json"
AUDIT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json"
LADDER = FOUNDATIONS / "results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json"
LEDGERS = v1.LEDGERS
CREATED = "2026-08-12"
BASE_COMMIT = "24e988693bd9ee6874bedf9de476202c949a2e7e"

PLAIN_AXIS_GUIDE = {
    "FOUNDATION": {
        "question": "Which rules of reasoning and mathematical existence are we allowing?",
        "plain_name": "Mathematical regime",
        "CLASSICAL_STANDARD": "Mainstream mathematics: classical logic, completed infinite structures, and ordinary analysis, with Choice available unless a proof explicitly avoids it.",
        "WEAK_ARITHMETIC": "Use a deliberately small formal system and ask exactly how much arithmetic or set existence the proof needs.",
        "WEAK_CHOICE_ZF": "Keep classical set theory but remove or isolate principles that choose objects from infinitely many sets at once.",
        "CONSTRUCTIVE_COMPUTABLE": "An existence claim must provide a witness, construction, or algorithm—not only show that nonexistence would be contradictory.",
        "TOPOS_INTERNAL": "Do the mathematics inside an alternative logical universe, where truth may be local and classical either/or reasoning may fail.",
        "FINITE_DISCRETE": "Replace an infinite or continuous system by finite exact data or finitely many modes. This is not automatically the same as rejecting infinity as a foundation.",
    },
    "CARRIER": {
        "question": "What kind of mathematical object holds the states, fields, and observables?",
        "plain_name": "Mathematical carrier",
        "FINITE_EXACT": "Finite matrices, rational arrays, or other finite algebraic data that can be checked exactly.",
        "HILBERT_OPERATOR": "The positive-norm vector spaces and operators used in standard quantum mechanics and spectral theory.",
        "KREIN_INDEFINITE": "A vector space whose inner product can be positive, negative, or zero, as often occurs before unphysical gauge directions are removed.",
        "ALGEBRAIC_CSTAR": "Start from an algebra of observable quantities; a state is a rule assigning expectation values rather than primarily a wavefunction.",
        "SMOOTH_DISTRIBUTIONAL": "Continuum fields on space or spacetime, including derivatives, PDEs, Sobolev spaces, generalized functions, and Green operators.",
        "LOCALIC_SYNTHETIC": "Describe spaces through regions, logical relations, or internal geometry instead of beginning with a set of individual points.",
    },
    "REFINED_OBLIGATION": {
        "question": "Which physical job must the theory perform?",
        "plain_name": "Physical obligation",
        "KINEMATICS_OBSERVABLES": "Say what the possible configurations and measurable quantities are before specifying how they evolve.",
        "STATE_EXISTENCE": "Show that at least one mathematically valid state actually exists.",
        "STATE_REPRESENTATION": "Explain how an abstract state is encoded—for example by a vector, density matrix, measure, valuation, or GNS construction.",
        "PROBABILITY_RULE": "Turn states and events into normalized probabilities, such as a Born-type prediction rule.",
        "PHYSICAL_STATE_SELECTION": "Explain why a particular vacuum, thermal, Hadamard, or other state should count as physically distinguished.",
        "GENERATOR_SPECTRAL_DYNAMICS": "Construct what generates time evolution and, where relevant, identify its allowed frequencies or energy spectrum.",
        "EVOLUTION_WELLPOSEDNESS": "Show that admissible initial data produce a solution that exists, is unique, and changes stably or computably with the data.",
        "CAUSAL_PROPAGATION_GREEN": "Show that disturbances propagate within the permitted causal region and construct retarded or advanced response maps.",
        "GAUGE_BV_COHOMOLOGY": "Handle redundant gauge descriptions consistently and identify the quantities or states that remain physically meaningful.",
        "INTERACTION_CONSTRUCTION": "Build a genuine coupling or nonlinear theory rather than only a collection of free, noninteracting fields.",
        "COUNTERTERM_CLASSIFICATION": "List every local correction that quantum calculations are allowed to require before attempting to calculate its coefficient.",
        "ANOMALY_CLASSIFICATION": "List the possible ways a classical symmetry or consistency condition could fail after quantization.",
        "RENORMALIZED_PRODUCTS": "Define products and correlation functions that would otherwise be singular when fields meet at the same spacetime point.",
        "QME_RESTORATION": "Repair the quantum master equation, the BV consistency condition that encodes quantum gauge symmetry.",
        "RESIDUAL_QUANTUM_TRANSFER": "After quantum consistency is restored, transfer the correction to the smaller complex that represents the surviving physical content.",
        "RECONSTRUCTION_LIMITS": "Connect the formulation back to operational predictions, a continuum or standard theory, or a demonstrated notion of empirical equivalence.",
    },
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def site_link(path: str) -> str:
    return "sources/" + Path(path).as_posix()


def guided_axes(source_axes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    axes: list[dict[str, Any]] = []
    for source_axis in source_axes:
        guide = PLAIN_AXIS_GUIDE[source_axis["id"]]
        axes.append({
            **source_axis,
            "plain_name": guide["plain_name"],
            "guide_question": guide["question"],
            "keys": [{**key, "plain_meaning": guide[key["id"]]} for key in source_axis["keys"]],
        })
    return axes


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
                        "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
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
        "axes": guided_axes(cube["axes"]),
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
            "cube_report": site_link("foundations/reports/refined-intersection-cube-v4.md"),
            "migration_audit_report": site_link("foundations/reports/intersection-cube-migration-audit-v2.md"),
            "ladder_report": site_link("foundations/reports/cylinder-wave-strength-ladder-v2.md"),
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

`foundations/site/index.html` presents all **576** Cartesian coordinates.
The **452** cube-emitted coordinates now have separate coverage and migration
review fields: **{counts['migration_reviewed']} reviewed**, **{counts['migration_pending']} pending**.
Of those, **{counts['reviewed_no_transfer']}** parent-evidence reviews found no
licensed transfer to the refined child. Seven now have independent child-specific
coverage; **81 remain `NOT_MAPPED`**, which is not a literature-absence claim.
The remaining **{counts['synthetic_not_mapped']}**
coordinates are browser-visible complements that have not been assessed.

Coverage is classified for **{counts['coverage_classified']}** emitted cells. The
coded-wave pass promotes two weak-arithmetic Hilbert/operator cells from pieces
to local results and adds five carefully typed evidence overlays.
The cell inspector exposes coverage evidence separately from migration-review
evidence and links to the explicit 112-decision audit ledger.

The **Dimensions guide** explains the 6 mathematical regimes, 6 carriers, and
16 physical obligations in non-specialist language while retaining each
technical definition in an expandable detail block.

## Build and verification

```text
python3 foundations/build_matrix_site_v2.py
python3 foundations/build_matrix_site_v2.py --check
python3 foundations/check_matrix_site_v2.py
python3 foundations/verify_matrix_site_v2.py
python3 -m unittest foundations.tests.test_matrix_site_v2
```

Earlier cubes remain unchanged as historical artifacts. The existing-site build
fails closed on unresolved evidence IDs and projects scientific text from the
cube, migration audit, strength ladder, local results, and literature ledgers.

## Deployment

Serve `foundations/site/` from any static host, or open `index.html` directly.
All source links resolve inside the standalone directory; no remote code is used.

## Boundaries

This site does not establish:

""" + "\n".join(f"- {item}" for item in result["does_not_establish"]) + "\n"


def generated() -> dict[Path, bytes]:
    dataset = build_dataset()
    data_json = (json.dumps(dataset, indent=2, ensure_ascii=False) + "\n").encode()
    index = (ASSETS / "index.html").read_text().replace(
        '<script src="app.js"></script>',
        '<script src="app.js"></script>\n  <script src="migration-review.js"></script>',
    ).encode()
    outputs: dict[Path, bytes] = {
        SITE / "index.html": index,
        SITE / "styles.css": (ASSETS / "styles.css").read_bytes(),
        SITE / "app.js": (ASSETS / "app.js").read_bytes(),
        SITE / "migration-review.js": (V2_ASSETS / "app-v2.js").read_bytes(),
        SITE / "data.json": data_json,
        SITE / "data.js": b"window.MATRIX_EXPLORER_DATA = " + data_json.rstrip() + b";\n",
    }
    local_evidence_paths = [ROOT / item["result_path"] for item in dataset["evidence"].values() if item["kind"] == "LOCAL_RESULT"]
    local_report_paths = [ROOT / item["report_path"] for item in dataset["evidence"].values() if item["kind"] == "LOCAL_RESULT" and item.get("report_path")]
    reports = [
        FOUNDATIONS / "reports/refined-intersection-cube-v4.md",
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
        "features": ["sixteen 6x6 heatmaps", "plain-language guide for all 28 axis options", "separate coverage and migration-review states", "migration evidence inspector", "multi-select filters", "full-text search", "cell inspector", "one-axis neighbors", "two-cell comparison", "URL permalinks", "filtered JSON and CSV export", "research-brief export", "typed implication graph", "strength ladder", "evidence catalogue"],
        "provenance": {"manifest": rel(SITE / "manifest.json"), "manifest_sha256": v1.sha_bytes(manifest_bytes), "canonical_data_digest": dataset["canonical_digest"]},
        "independent_checker": {"path": "foundations/check_matrix_site_v2.py", "expected_cells": 576, "expected_emitted": 452, "expected_synthetic_not_mapped": 124, "expected_total_not_mapped": 205, "expected_evidence_records": 69, "expected_digest": dataset["canonical_digest"]},
        "claim_flags": {"static_site_generated": True, "all_cartesian_coordinates_visible": True, "all_emitted_migrations_reviewed": True, "coverage_and_migration_separated": True, "all_used_evidence_resolved": True, "scientific_claims_duplicated_by_hand": False, "literature_complete": False, "unmapped_means_absent": False, "reviewed_no_transfer_means_absent": False, "priority_score_is_theorem": False, "new_lorentzian_claim": False},
        "does_not_establish": ["literature completeness", "coverage for the 81 still-unmapped reviewed-no-transfer coordinates", "that NOT_MAPPED means no literature exists", "that the 124 synthetic coordinates are coherent", "a weakest mathematical base", "a theorem ranking from interface order or neighbor counts", "a new Lorentzian-causal result"],
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
