#!/usr/bin/env python3
"""Freeze the nonvacuous advisory Phase-1 publication-coverage baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-07-22"
CLASSIFIED = [
    "BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1",
    "CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1",
    "EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1",
    "NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1",
    "PAPER09_COUNTERFLOW_HEALTH_NONACTIVATION_FREEZE_V1",
    "PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1",
    "PURE_WEYL_BH2C_SYMBOLIC_FLUX_RADIATION_CLASS",
    "PURE_WEYL_BH_ENDPOINT_NONSELECTION_ASSEMBLY",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def build(shadow: Path, discovery: Path, graph: Path, report: Path, overlay: Path) -> dict[str, Any]:
    shadow_data = json.loads(shadow.read_text())
    discovery_data = json.loads(discovery.read_text())
    graph_data = json.loads(graph.read_text())
    report_data = json.loads(report.read_text())
    overlay_data = json.loads(overlay.read_text())
    summary = report_data["summary"]
    kinds: dict[str, int] = {}
    for node in graph_data["nodes"]:
        kinds[node["kind"]] = kinds.get(node["kind"], 0) + 1
    assert summary == {
        "results": 1408,
        "classified": 8,
        "unclassified": 1400,
        "papers": 52,
        "paper_claims": 11,
        "review_queue": 1400,
        "uncovered_material": 0,
        "overview_only": 0,
        "superseded_evidence": 0,
        "claim_no_evidence": 0,
        "lifecycle_disagreement": 0,
        "deferred_ok": 0,
        "blocking": 0,
    }
    assert {flag["class"] for flag in report_data["flags"]} == {"REVIEW_QUEUE"}
    assert overlay_data["human_materiality_decision"]["by"] == "Asger Alstrup Palm"
    assert overlay_data["human_materiality_decision"]["classified_results"] == 8
    assert kinds["materiality"] == 8 and kinds["paper_claim"] == 11
    assert kinds["result_paper_edge"] == 17
    discovery_papers = sum(n.get("kind") == "paper" for n in discovery_data["nodes"])
    shadow_certs = sum(n.get("kind") == "certificate" for n in shadow_data["nodes"])
    assert discovery_papers == 47 and shadow_certs == 1404
    return {
        "schema": "programme-paper-coverage-baseline-v1",
        "result_id": "PROGRAMME_GLOBAL_PAPER_COVERAGE_BASELINE_V1",
        "result_state": "NONVACUOUS_ADVISORY_BASELINE_REVIEWED_SLATE_COVERED",
        "stamp": STAMP,
        "mode": "advisory",
        "human_materiality": {
            "by": "Asger Alstrup Palm",
            "version": 1,
            "classified_result_ids": CLASSIFIED,
        },
        "counts": {
            **summary,
            "shadow_certificates": shadow_certs,
            "discovery_papers_before_markdown_overlay": discovery_papers,
            "typed_result_paper_edges": kinds["result_paper_edge"],
            "coverage_graph_nodes": len(graph_data["nodes"]),
        },
        "inputs": {
            "shadow_import_sha256": sha(shadow),
            "discovery_graph_sha256": sha(discovery),
            "typed_overlay": str(overlay.resolve().relative_to(ROOT)),
            "typed_overlay_sha256": sha(overlay),
            "adapted_graph_sha256": sha(graph),
            "advisory_report_sha256": sha(report),
        },
        "commands": [
            "s-f shadow-import-all . /home/alstrup/area9/tango/forge shadow.json shadow-ledger.json",
            "python3 /home/alstrup/area9/tango/forge/tools/science-forge/discover/mine_evidence.py --physics-root . --out-dir <scratch>",
            "python3 planning/paper-coverage/generate_phase1_paper_coverage_overlay.py --discovery <scratch>/evidence_graph.json --output planning/paper-coverage/phase1-paper-coverage-overlay-2026-07-22.json",
            "s-f coverage-adapt <scratch>/shadow.json --overlay planning/paper-coverage/phase1-paper-coverage-overlay-2026-07-22.json -o <scratch>/coverage-graph.json",
            "s-f paper-coverage <scratch>/coverage-graph.json --mode advisory --stamp 2026-07-22 -o <scratch>/coverage-report.json",
        ],
        "interpretation": {
            "reviewed_slice": "All eight human-classified recent/headline Phase-1 results have current technical coverage; all eleven typed reverse paper claims pass.",
            "unclassified_remainder": "The other 1,400 discovered result candidates remain visibly queued for human materiality review. Their count is inventory, not publication debt and not a no-paper disposition.",
            "release_status": "This is an advisory baseline, not a release-mode all-corpus coverage pass.",
        },
        "does_not_establish": [
            "that all 1,400 unclassified result candidates are publication-relevant",
            "that every prose theorem statement in every manuscript has been converted to a typed paper_claim",
            "that an overview mention counts as technical coverage",
            "that Phase 1 establishes a viable theory, particles, scattering, positivity, unitarity, or complete quantum gravity",
        ],
    }


def markdown(census: dict[str, Any]) -> str:
    c = census["counts"]
    return f"""# Programme-wide paper-coverage baseline close-out — {STAMP}

## Outcome

The first nonvacuous bidirectional publication audit is established in advisory mode.
The adapted graph contains **{c['results']} results** and **{c['papers']} papers**.
Human coordinator Asger Alstrup Palm classified eight current Phase-1 results; all
eight reach a technical paper, and all **{c['paper_claims']}** typed reverse paper
claims pass their evidence, lifecycle, and boundary checks.

The remaining **{c['review_queue']}** result candidates are explicitly retained in
`REVIEW_QUEUE`. This is a visible human-review inventory, not an assertion that each
item deserves a paper and not a claim that it needs no paper.

## Exact audit summary

| Check | Count |
|---|---:|
| Shadow-imported certificates | {c['shadow_certificates']} |
| Coverage results after typed overlay | {c['results']} |
| Human-classified results | {c['classified']} |
| Unclassified, visible review queue | {c['unclassified']} |
| Papers (including Markdown publications) | {c['papers']} |
| Typed technical paper claims | {c['paper_claims']} |
| Typed result-to-paper edges | {c['typed_result_paper_edges']} |
| Uncovered classified material results | {c['uncovered_material']} |
| Overview-only classified results | {c['overview_only']} |
| Claims without current evidence | {c['claim_no_evidence']} |
| Lifecycle disagreements | {c['lifecycle_disagreement']} |
| Superseded/stale evidence claims | {c['superseded_evidence']} |

## Scope

This closes the Phase-1 baseline gate: the reviewed recent/headline slate is covered,
the reverse typed claims are current, and the unreviewed remainder is impossible to
mistake for a clean or empty audit. It does **not** claim release-mode coverage of the
entire historical corpus. The exact hashes and reproduction commands are recorded in
`planning/paper-coverage/phase1-paper-coverage-baseline-2026-07-22.json`.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shadow", required=True, type=Path)
    parser.add_argument("--discovery", required=True, type=Path)
    parser.add_argument("--graph", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--overlay", required=True, type=Path)
    parser.add_argument("--census-output", required=True, type=Path)
    parser.add_argument("--report-output", required=True, type=Path)
    parser.add_argument("--closeout-output", required=True, type=Path)
    args = parser.parse_args()
    census = build(args.shadow, args.discovery, args.graph, args.report, args.overlay)
    dump(args.census_output, census)
    dump(args.report_output, json.loads(args.report.read_text()))
    args.closeout_output.parent.mkdir(parents=True, exist_ok=True)
    args.closeout_output.write_text(markdown(census))
    print(f"froze {census['counts']['classified']} classified and {census['counts']['unclassified']} queued results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
