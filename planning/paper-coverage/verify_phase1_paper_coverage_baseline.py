#!/usr/bin/env python3
"""Independent verification of the Phase-1 paper-coverage baseline artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(census_path: Path, report_path: Path, overlay_path: Path, graph_path: Path | None) -> None:
    census = json.loads(census_path.read_text())
    report = json.loads(report_path.read_text())
    overlay = json.loads(overlay_path.read_text())
    assert census["schema"] == "programme-paper-coverage-baseline-v1"
    assert census["result_id"] == "PROGRAMME_GLOBAL_PAPER_COVERAGE_BASELINE_V1"
    assert census["result_state"] == "NONVACUOUS_ADVISORY_BASELINE_REVIEWED_SLATE_COVERED"
    assert census["mode"] == report["mode"] == "advisory"
    assert census["counts"]["results"] == report["summary"]["results"] == 1408
    assert census["counts"]["classified"] == report["summary"]["classified"] == 8
    assert census["counts"]["review_queue"] == report["summary"]["review_queue"] == 1400
    assert census["counts"]["paper_claims"] == report["summary"]["paper_claims"] == 11
    assert census["counts"]["typed_result_paper_edges"] == 17
    assert census["counts"]["blocking"] == 0
    for key in ("uncovered_material", "overview_only", "superseded_evidence", "claim_no_evidence", "lifecycle_disagreement"):
        assert census["counts"][key] == report["summary"][key] == 0
    assert len(report["flags"]) == 1400
    assert {flag["class"] for flag in report["flags"]} == {"REVIEW_QUEUE"}
    reviewed = {"sf:coverage/result/" + raw for raw in census["human_materiality"]["classified_result_ids"]}
    queued = {flag["subject"] for flag in report["flags"]}
    assert reviewed.isdisjoint(queued)
    assert census["human_materiality"]["by"] == "Asger Alstrup Palm"
    assert overlay["human_materiality_decision"]["by"] == "Asger Alstrup Palm"
    assert sha(overlay_path) == census["inputs"]["typed_overlay_sha256"]
    if graph_path is not None:
        graph = json.loads(graph_path.read_text())
        assert sha(graph_path) == census["inputs"]["adapted_graph_sha256"]
        assert len(graph["nodes"]) == census["counts"]["coverage_graph_nodes"] == 1496
        by_kind: dict[str, int] = {}
        for node in graph["nodes"]:
            by_kind[node["kind"]] = by_kind.get(node["kind"], 0) + 1
        assert by_kind["result"] == 1408
        assert by_kind["materiality"] == 8
        assert by_kind["paper_claim"] == 11
        assert by_kind["result_paper_edge"] == 17
    assert "not publication debt" in census["interpretation"]["unclassified_remainder"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--overlay", required=True, type=Path)
    parser.add_argument("--graph", type=Path)
    args = parser.parse_args()
    verify(args.census, args.report, args.overlay, args.graph)
    print("PROGRAMME_GLOBAL_PAPER_COVERAGE_BASELINE_V1 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
