#!/usr/bin/env python3
"""Independent, fail-closed verification of the Phase-1 coverage overlay."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable

from generate_phase1_paper_coverage_overlay import HUMAN, PAPERS, PREFIX, RESULTS, STAMP


def verify(payload: dict[str, Any]) -> None:
    assert payload["ir"] == "science-forge-ir-v0"
    assert payload["schema"] == "phase1-paper-coverage-overlay-v1"
    decision = payload["human_materiality_decision"]
    assert decision == {
        "by": HUMAN,
        "stamp": STAMP,
        "version": 1,
        "classified_results": 8,
        "policy": "All other discovered results remain explicitly unclassified and visible in REVIEW_QUEUE.",
    }
    nodes = payload["nodes"]
    by_id = {node["id"]: node for node in nodes}
    assert len(by_id) == len(nodes), "duplicate node id"
    papers = {n["id"]: n for n in nodes if n["kind"] == "paper"}
    assert set(PAPERS.values()) <= set(papers)
    for number in ("00", "98", "99"):
        assert papers[PAPERS[number]]["body"]["paper_class"] == "overview"
    for number in ("09", "10", "11", "12", "13", "14", "90", "91", "92"):
        assert papers[PAPERS[number]]["body"]["paper_class"] == "technical"

    materiality = [n for n in nodes if n["kind"] == "materiality"]
    assert len(materiality) == len(RESULTS) == 8
    assert {n["body"]["result_id"] for n in materiality} == {PREFIX + r for r in RESULTS}
    technical_pairs: set[tuple[str, str]] = set()
    overview_pairs: set[tuple[str, str]] = set()
    for raw, spec in RESULTS.items():
        rid = PREFIX + raw
        result = by_id[rid]
        assert result["kind"] == "result"
        assert result["body"]["lifecycle"] == "CERTIFIED"
        assert result["body"]["boundary"] == spec["boundary"]
        assert result["body"]["stale"] is False and result["body"]["superseded"] is False
        m = by_id[f"sf:coverage/materiality/{raw}/v1"]["body"]
        assert m["result_id"] == rid and m["materiality"] == spec["materiality"]
        assert m["by"] == HUMAN and m["stamp"] == STAMP and m["version"] == 1
        assert m["native"] == {"source_schema": "materiality-v0"}
        for number, edge_kind in spec["technical"]:
            eid = f"sf:coverage/edge/{raw}/paper-{number}/v1"
            edge = by_id[eid]["body"]
            pid = PAPERS[number]
            assert edge["from"] == rid and edge["to"] == pid
            assert edge["edge_kind"] == edge_kind and edge["stale"] is False
            claim = by_id[edge["claim"]]
            assert claim["kind"] == "paper_claim"
            assert claim["body"] == {
                "paper": pid,
                "material": True,
                "asserts_lifecycle": "CERTIFIED",
                "boundary": spec["boundary"],
                "cites": [rid],
            }
            technical_pairs.add((rid, pid))
        for number in spec["overview"]:
            edge = by_id[f"sf:coverage/edge/{raw}/paper-{number}/overview-v1"]["body"]
            assert edge["from"] == rid and edge["to"] == PAPERS[number]
            assert edge["edge_kind"] == "OVERVIEW_MENTION"
            overview_pairs.add((rid, PAPERS[number]))
    assert len(technical_pairs) == 11
    assert len(overview_pairs) == 6


def reject(payload: dict[str, Any], mutation: Callable[[dict[str, Any]], None]) -> None:
    candidate = copy.deepcopy(payload)
    mutation(candidate)
    try:
        verify(candidate)
    except (AssertionError, KeyError):
        return
    raise AssertionError("contradictory coverage mutation accepted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("overlay", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.overlay.read_text())
    verify(payload)
    mutations = [
        lambda p: p["human_materiality_decision"].update(by="AI agent"),
        lambda p: next(n for n in p["nodes"] if n["kind"] == "materiality")["body"].update(by="AI agent"),
        lambda p: next(n for n in p["nodes"] if n["kind"] == "result")["body"].update(lifecycle="OBSERVED"),
        lambda p: next(n for n in p["nodes"] if n["kind"] == "result_paper_edge" and n["body"]["edge_kind"] != "OVERVIEW_MENTION")["body"].update(stale=True),
        lambda p: next(n for n in p["nodes"] if n["kind"] == "paper_claim")["body"].update(cites=[]),
    ]
    for mutation in mutations:
        reject(payload, mutation)
    print(f"phase1 paper-coverage overlay: PASS ({len(mutations)} contradiction mutations rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
