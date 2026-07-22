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

POST_PHASE1_INPUTS = [
    {
        "key": "generic_l_schwarzschild",
        "result_id": "PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1",
        "path": "black_hole_programme/phase2/generic_l_synthesis/certificate.json",
        "sha256": "8a9914400f0929f37a63570b95383ebc4131cbf2928b5f923db0d002d0783d33",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "edge_kind": "SUPPORTING_POLAR_THEOREM",
        "paper_location": "Result card C",
        "relationship": "Retains the generic-angular polar Q21 filtration; its axial metric disposition is superseded by the Phase-3 all-row ell=2 repair.",
    },
    {
        "key": "phase3_axial_complete_reconstruction",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_COMPLETE_RECONSTRUCTION_REPAIR",
        "path": "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json",
        "sha256": "13a4077ee8c77cc5b99e379d35aa15afa09ebeea78c0df9a4771b4845c00c990",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "edge_kind": "PRIMARY_THEOREM_CORRECTION",
        "paper_location": "Result card C",
        "relationship": "Supersedes the Phase-2 generic-ell axial metric and representative-independence claims while retaining the separate polar filtration.",
    },
    {
        "key": "compact_pt_cpt",
        "result_id": "PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1",
        "path": "quantum-weyl/pt_cpt/synthesis/certificates/PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1.json",
        "sha256": "516415604952c1f835ea0d46095d8fa82b07fe36de3dc33d641e34f0b938223c",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "edge_kind": "SUPPORTING_EVIDENCE",
        "paper_location": "Result cards A and E",
        "relationship": "Adds positive-metric feasibility, BRST-chain obstruction, and quartet negative control without promoting a full state.",
    },
    {
        "key": "berger_hadamard",
        "result_id": "PHASE2_BRST_HADAMARD_STRETCH_OBSTRUCTION_V1",
        "path": "quantum-weyl/pt_cpt/hadamard_stretch/certificates/PHASE2_BRST_HADAMARD_STRETCH_OBSTRUCTION_V1.json",
        "sha256": "cb705de9f5ba2589ebe514304709f175846307a20f0ea671a78711490e152e8c",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL", "REDUCED-MODE"],
        "edge_kind": "LIMITATION",
        "paper_location": "Appendix: Berger Hadamard-covariance gate",
        "relationship": "Pins the missing full-carrier obstruction and does not claim nonexistence.",
    },
    {
        "key": "nariai_sign_mechanism",
        "result_id": "NARIAI_SIGN_MECHANISM_V2",
        "path": "d_quotient_classical/phase2/nariai_sign_mechanism_v2/NARIAI_SIGN_MECHANISM_V2.json",
        "sha256": "abc73ddf5ada84dfe93d7891411f7134c7c2906ec3f70550fe50e1a6c542b4f8",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "edge_kind": "PRIMARY_THEOREM",
        "paper_location": "Result card A discussion",
        "relationship": "Adds a scoped relative-residue mechanism without identifying background families or absolute signs.",
    },
    {
        "key": "dyonic_flat_preflight",
        "result_id": "DYONIC_FLAT_FAMILY_PREFLIGHT_V1",
        "path": "bridge/phase2/dyonic_flat_family_preflight/DYONIC_FLAT_FAMILY_PREFLIGHT_V1.json",
        "sha256": "db0baaa808b131389de09adcbe02d423d210201f96290f94bea0f25be05fdfc2",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "edge_kind": "NEGATIVE_RESULT",
        "paper_location": "Appendix: dyonic stationary-family preflight",
        "relationship": "Prevents promotion of a fixed-coupling stationary sign-family scan.",
    },
]

GENERIC_L_TERMINAL_RECEIPTS = [
    {
        "path": "black_hole_programme/phase2/generic_l_synthesis/receipt.json",
        "sha256": "0888efb8f14518d38e40bd1b0a3926b8fab37ad729dce798c221a01d24aeabee",
    },
    {
        "path": "reports/phase2-black-hole-generic-l-disposition-2026-07-22.md",
        "sha256": "571fab0469b7bfde2b051b94bea657547570376b390a30a5b9ad6b6e93e92558",
    },
    {
        "path": "planning/paper-coverage/phase2-black-hole-paper-correction-request.json",
        "sha256": "308b27ba24076f7e439e36ebceb322442af1b1dcee225449d791cc105f403094",
    },
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ledger = json.loads(LEDGER.read_text())
    claims = {claim["claim_id"]: claim for claim in ledger["claims"]}
    required = {claim for ids in CARD_CLAIMS.values() for claim in ids}
    missing = sorted(required - claims.keys())
    if missing:
        raise SystemExit(f"missing frozen claims: {missing}")

    for item in POST_PHASE1_INPUTS + GENERIC_L_TERMINAL_RECEIPTS:
        path = ROOT / item["path"]
        if digest(path) != item["sha256"]:
            raise SystemExit(f"post-Phase-1 input hash drift: {item['path']}")

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
        "schema": "paper15-phase1-synthesis-claim-map-v4",
        "result_id": "PAPER15_FOUR_LEVEL_PHASE1_SYNTHESIS_WITH_PHASE3_UPDATE_V4",
        "result_state": "PUBLICATION_SYNTHESIS_OF_FROZEN_CLAIMS",
        "paper": str(PAPER.relative_to(ROOT)),
        "paper_sha256": digest(PAPER),
        "authoritative_ledger": str(LEDGER.relative_to(ROOT)),
        "authoritative_ledger_sha256": digest(LEDGER),
        "authoritative_result_id": ledger["result_id"],
        "theorem_cards": cards,
        "post_phase1_updates": POST_PHASE1_INPUTS,
        "generic_l_terminal_receipts": GENERIC_L_TERMINAL_RECEIPTS,
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
                "native": {"source_kind": "paper15-additive-phase1-synthesis-with-phase3-v4"},
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
    for item in POST_PHASE1_INPUTS:
        raw = item["result_id"]
        result_id = f"sf:result/{raw}"
        claim_id = f"paper:15-four-level-ghost-classification-phase1-synthesis/claim/update-{item['key']}"
        coverage_nodes.extend(
            [
                {
                    "kind": "result",
                    "id": result_id,
                    "title": raw,
                    "source": {"path": item["path"], "sha256": item["sha256"]},
                    "body": {
                        "lifecycle": "CLASSIFIED",
                        "boundary": {
                            "dependency_tags": item["dependency_tags"],
                            "relationship": item["relationship"],
                        },
                    },
                    "edges": [],
                },
                {
                    "kind": "paper_claim",
                    "id": claim_id,
                    "body": {
                        "paper": "paper:15-four-level-ghost-classification-phase1-synthesis",
                        "material": True,
                        "asserts_lifecycle": "CLASSIFIED",
                        "boundary": {
                            "dependency_tags": item["dependency_tags"],
                            "paper_location": item["paper_location"],
                            "relationship": item["relationship"],
                        },
                        "cites": [result_id],
                    },
                },
                {
                    "kind": "result_paper_edge",
                    "id": f"sf:coverage/edge/{raw}/paper-15/post-phase1-update-v4",
                    "body": {
                        "from": result_id,
                        "to": "paper:15-four-level-ghost-classification-phase1-synthesis",
                        "claim": claim_id,
                        "edge_kind": item["edge_kind"],
                        "stale": False,
                        "version": 4,
                        "stamp": "2026-07-23",
                        "native": {"source_schema": "result-paper-edge-v0"},
                    },
                },
            ]
        )
    coverage = {
        "ir": "science-forge-ir-v0",
        "schema": "paper15-phase1-synthesis-overlay-v4",
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
