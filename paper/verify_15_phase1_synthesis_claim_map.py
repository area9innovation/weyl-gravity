#!/usr/bin/env python3
"""Independent scope verifier for Paper 15 and its generated claim map."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPER = ROOT / "paper/15-four-level-ghost-classification-phase1-synthesis.tex"
DEFAULT_MAP = ROOT / "paper/15-four-level-ghost-classification-phase1-synthesis-claim-map.json"
LEDGER = ROOT / "reports/phase1-closure-claims-ledger-2026-07-22.json"
COVERAGE_SOURCE = ROOT / "planning/paper-coverage/phase1-paper-coverage-overlay-2026-07-22.json"
COVERAGE = ROOT / "planning/paper-coverage/paper15-phase1-synthesis-overlay-2026-07-22.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"REFUSED: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--claim-map", type=Path, default=DEFAULT_MAP)
    args = parser.parse_args()

    paper = args.paper if args.paper.is_absolute() else ROOT / args.paper
    claim_map_path = args.claim_map if args.claim_map.is_absolute() else ROOT / args.claim_map
    claim_map = json.loads(claim_map_path.read_text())
    ledger = json.loads(LEDGER.read_text())
    ledger_claims = {claim["claim_id"]: claim for claim in ledger["claims"]}

    if claim_map["paper_sha256"] != digest(paper):
        fail("paper hash drift")
    if claim_map["authoritative_ledger_sha256"] != digest(LEDGER):
        fail("authoritative ledger hash drift")
    if claim_map["authoritative_result_id"] != "PURE_WEYL_PROGRAMME_PHASE1_CLASSIFICATION_ENDING_V1":
        fail("wrong Phase-1 authority")

    mapped = set()
    for card in claim_map["theorem_cards"]:
        for claim_id in card["claim_ids"]:
            mapped.add(claim_id)
            if claim_id not in ledger_claims:
                fail(f"unknown claim {claim_id}")
            if card["lifecycles"][claim_id] != ledger_claims[claim_id]["lifecycle"]:
                fail(f"lifecycle drift for {claim_id}")
            if card["limitations"][claim_id] != ledger_claims[claim_id]["limitation"]:
                fail(f"limitation drift for {claim_id}")

    required_ids = {
        "phase1.einstein_extra.structure",
        "phase1.taub_kuranishi.structure",
        "phase1.black_hole.companion",
        "phase1.quantum.strict",
        "phase1.quantum.compensator",
        "phase1.counterflow.causal_parent",
        "phase1.counterflow.physical_viability",
        "phase1.counterflow.clock_charge",
    }
    if mapped != required_ids:
        fail(f"theorem-card coverage mismatch: {sorted(mapped ^ required_ids)}")

    text = paper.read_text()
    required_phrases = [
        "Result card A: compact Einstein/additional decomposition",
        "Result card B: finite-harmonic second-order cone",
        "Result card C: radial-pairing selection at a Schwarzschild fixture",
        "Result card D: strict and compensated local quantum theories",
        "Result card E: causal construction and physical nonselection",
        "(2,3/5)",
        "h_+(u,v)=",
        "S_{\\rm cf}=",
        "\\operatorname{disc}_wF_2=256q^5(9q-8)<0",
        "\\mathcal N_R[u_1,u_2]",
        "c_{\\rm W}=\\frac{199}{30}",
        "a_{\\rm W}=\\frac{87}{20}",
        "\\Gamma^{(1)}_{\\rm div}(d)",
        "This is a classification ending, not a viable-theory claim",
        "No positive full-BV state has been constructed",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"required scope phrase missing: {phrase}")

    forbidden_phrases = [
        "smooth tangent cone",
        "causal truncation no-go",
        "ordinary local causal boundary conditions cannot remove",
        "strict pure Weyl gravity is anomaly-free",
        "counterflow theory is physically viable",
        "Lee--Wald inertia",
        "exact 70-component causal BV parent",
    ]
    for phrase in forbidden_phrases:
        if phrase.lower() in text.lower():
            fail(f"overbroad phrase present: {phrase}")

    coverage = json.loads(COVERAGE.read_text())
    if coverage["append_only_parent_sha256"] != digest(COVERAGE_SOURCE):
        fail("frozen coverage parent hash drift")
    if coverage["claim_map_sha256"] != digest(claim_map_path):
        fail("coverage-to-claim-map hash drift")
    source_results = {
        node["id"]
        for node in json.loads(COVERAGE_SOURCE.read_text())["nodes"]
        if node.get("kind") == "result"
    }
    nodes = coverage["nodes"]
    edges = [node for node in nodes if node["kind"] == "result_paper_edge"]
    claims = {node["id"]: node for node in nodes if node["kind"] == "paper_claim"}
    if {edge["body"]["from"] for edge in edges} != source_results:
        fail("Paper 15 reverse-coverage result set is incomplete")
    for edge in edges:
        body = edge["body"]
        if body["edge_kind"] != "OVERVIEW_SYNTHESIS" or body["stale"] is not False:
            fail("Paper 15 coverage edge overpromoted or stale")
        claim = claims.get(body["claim"])
        if not claim or claim["body"]["cites"] != [body["from"]]:
            fail("Paper 15 coverage claim/edge mismatch")

    print("PASS: Paper 15 claim map, append-only reverse coverage, lifecycles, limitations, and scope sentinels")


if __name__ == "__main__":
    main()
