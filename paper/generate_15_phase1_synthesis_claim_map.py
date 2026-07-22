#!/usr/bin/env python3
"""Generate the deterministic claim map for Paper 15."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/15-four-level-ghost-classification-phase1-synthesis.tex"
LEDGER = ROOT / "reports/phase1-closure-claims-ledger-2026-07-22.json"
OUTPUT = ROOT / "paper/15-four-level-ghost-classification-phase1-synthesis-claim-map.json"
COVERAGE_SOURCE = ROOT / "planning/paper-coverage/phase1-paper-coverage-overlay-2026-07-22.json"
COVERAGE_OUTPUT = ROOT / "planning/paper-coverage/paper15-phase1-synthesis-overlay-2026-07-22.json"

CARD_CLAIMS = {
    "A": ["phase1.einstein_extra.structure"],
    "B": ["phase1.taub_kuranishi.structure"],
    "C": ["phase1.black_hole.companion"],
    "D": ["phase1.quantum.strict", "phase1.quantum.compensator"],
    "E": [
        "phase1.counterflow.causal_parent",
        "phase1.counterflow.physical_viability",
        "phase1.counterflow.clock_charge",
    ],
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ledger = json.loads(LEDGER.read_text())
    claims = {claim["claim_id"]: claim for claim in ledger["claims"]}
    required = {claim for ids in CARD_CLAIMS.values() for claim in ids}
    missing = sorted(required - claims.keys())
    if missing:
        raise SystemExit(f"missing frozen claims: {missing}")

    cards = []
    for card, ids in CARD_CLAIMS.items():
        cards.append(
            {
                "card": card,
                "claim_ids": ids,
                "lifecycles": {claim_id: claims[claim_id]["lifecycle"] for claim_id in ids},
                "limitations": {claim_id: claims[claim_id]["limitation"] for claim_id in ids},
            }
        )

    payload = {
        "schema": "paper15-phase1-synthesis-claim-map-v2",
        "result_id": "PAPER15_FOUR_LEVEL_PHASE1_SYNTHESIS_V2",
        "result_state": "PUBLICATION_SYNTHESIS_OF_FROZEN_CLAIMS",
        "paper": str(PAPER.relative_to(ROOT)),
        "paper_sha256": digest(PAPER),
        "authoritative_ledger": str(LEDGER.relative_to(ROOT)),
        "authoritative_ledger_sha256": digest(LEDGER),
        "authoritative_result_id": ledger["result_id"],
        "theorem_cards": cards,
        "supporting_claim_ids": [
            "phase1.interaction.disposition",
            "phase1.observer.disposition",
        ],
        "does_not_establish": ledger["does_not_establish"],
        "scope_rule": "Every scientific statement inherits the exact mathematical scope (theory, spacetime, background fields, gauge group, function or phase space, and boundary/support class) of its frozen source claim; dependency tags, evidence state, and limitation are recorded separately.",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(OUTPUT.relative_to(ROOT))

    frozen_coverage = json.loads(COVERAGE_SOURCE.read_text())
    result_nodes = sorted(
        (node for node in frozen_coverage["nodes"] if node.get("kind") == "result"),
        key=lambda node: node["id"],
    )
    coverage_nodes = [
        {
            "kind": "paper",
            "id": "paper:15-four-level-ghost-classification-phase1-synthesis",
            "title": "15-four-level-ghost-classification-phase1-synthesis",
            "source": {"path": str(PAPER.relative_to(ROOT))},
            "body": {
                "paper_class": "overview",
                "native": {"source_kind": "paper15-additive-phase1-synthesis-v2"},
            },
            "edges": [],
        }
    ]
    for result in result_nodes:
        raw = result["id"].rsplit("/", 1)[-1]
        claim_id = f"paper:15-four-level-ghost-classification-phase1-synthesis/claim/{raw.lower()}"
        coverage_nodes.extend(
            [
                {
                    "kind": "paper_claim",
                    "id": claim_id,
                    "body": {
                        "paper": "paper:15-four-level-ghost-classification-phase1-synthesis",
                        "material": True,
                        "asserts_lifecycle": result["body"]["lifecycle"],
                        "boundary": result["body"]["boundary"],
                        "cites": [result["id"]],
                    },
                },
                {
                    "kind": "result_paper_edge",
                    "id": f"sf:coverage/edge/{raw}/paper-15/phase1-synthesis-v2",
                    "body": {
                        "from": result["id"],
                        "to": "paper:15-four-level-ghost-classification-phase1-synthesis",
                        "claim": claim_id,
                        "edge_kind": "OVERVIEW_SYNTHESIS",
                        "stale": False,
                        "version": 2,
                        "stamp": "2026-07-22",
                        "native": {"source_schema": "result-paper-edge-v0"},
                    },
                },
            ]
        )
    coverage = {
        "ir": "science-forge-ir-v0",
        "schema": "paper15-phase1-synthesis-overlay-v2",
        "append_only_parent": str(COVERAGE_SOURCE.relative_to(ROOT)),
        "append_only_parent_sha256": digest(COVERAGE_SOURCE),
        "claim_map": str(OUTPUT.relative_to(ROOT)),
        "claim_map_sha256": digest(OUTPUT),
        "nodes": sorted(coverage_nodes, key=lambda node: (node["kind"], node["id"])),
    }
    COVERAGE_OUTPUT.write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n")
    print(COVERAGE_OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
