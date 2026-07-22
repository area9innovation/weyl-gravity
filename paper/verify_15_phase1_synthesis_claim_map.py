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

AUTHOR_BLOCK = r"""\author{GPT-5.6.sol\thanks{OpenAI model and principal programme author.}
\and Claude Fable 5\thanks{Anthropic model and computational coauthor. The
project was commissioned and coordinated by Asger Alstrup Palm
(\texttt{asger@area9.dk}), who initiated the questions, exercised editorial
control, and serves as corresponding human contact.}}"""

EXPECTED_PHASE2 = {
    "PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1": (
        "black_hole_programme/phase2/generic_l_synthesis/certificate.json",
        "8a9914400f0929f37a63570b95383ebc4131cbf2928b5f923db0d002d0783d33",
        ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
    ),
    "PURE_WEYL_PHASE3_AXIAL_COMPLETE_RECONSTRUCTION_REPAIR": (
        "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json",
        "13a4077ee8c77cc5b99e379d35aa15afa09ebeea78c0df9a4771b4845c00c990",
        ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
    ),
    "PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1": (
        "quantum-weyl/pt_cpt/synthesis/certificates/PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1.json",
        "516415604952c1f835ea0d46095d8fa82b07fe36de3dc33d641e34f0b938223c",
        ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
    ),
    "PHASE2_BRST_HADAMARD_STRETCH_OBSTRUCTION_V1": (
        "quantum-weyl/pt_cpt/hadamard_stretch/certificates/PHASE2_BRST_HADAMARD_STRETCH_OBSTRUCTION_V1.json",
        "cb705de9f5ba2589ebe514304709f175846307a20f0ea671a78711490e152e8c",
        ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL", "REDUCED-MODE"],
    ),
    "NARIAI_SIGN_MECHANISM_V2": (
        "d_quotient_classical/phase2/nariai_sign_mechanism_v2/NARIAI_SIGN_MECHANISM_V2.json",
        "abc73ddf5ada84dfe93d7891411f7134c7c2906ec3f70550fe50e1a6c542b4f8",
        ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
    ),
    "DYONIC_FLAT_FAMILY_PREFLIGHT_V1": (
        "bridge/phase2/dyonic_flat_family_preflight/DYONIC_FLAT_FAMILY_PREFLIGHT_V1.json",
        "db0baaa808b131389de09adcbe02d423d210201f96290f94bea0f25be05fdfc2",
        ["LOCAL-ALGEBRAIC"],
    ),
}

EXPECTED_GENERIC_RECEIPTS = {
    "black_hole_programme/phase2/generic_l_synthesis/receipt.json":
        "0888efb8f14518d38e40bd1b0a3926b8fab37ad729dce798c221a01d24aeabee",
    "reports/phase2-black-hole-generic-l-disposition-2026-07-22.md":
        "571fab0469b7bfde2b051b94bea657547570376b390a30a5b9ad6b6e93e92558",
    "planning/paper-coverage/phase2-black-hole-paper-correction-request.json":
        "308b27ba24076f7e439e36ebceb322442af1b1dcee225449d791cc105f403094",
}


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
    if claim_map["schema"] != "paper15-phase1-synthesis-claim-map-v4":
        fail("wrong claim-map schema")

    updates = {item["result_id"]: item for item in claim_map["post_phase1_updates"]}
    if set(updates) != set(EXPECTED_PHASE2):
        fail("Phase-2 result set drift")
    for result_id, (path_string, expected_hash, expected_tags) in EXPECTED_PHASE2.items():
        item = updates[result_id]
        if item["path"] != path_string or item["sha256"] != expected_hash:
            fail(f"Phase-2 pin drift for {result_id}")
        path = ROOT / path_string
        if digest(path) != expected_hash:
            fail(f"Phase-2 source hash drift for {result_id}")
        source = json.loads(path.read_text())
        if source.get("result_id") != result_id:
            fail(f"Phase-2 source result mismatch for {result_id}")
        if item["dependency_tags"] != expected_tags or source.get("dependency_tags") != expected_tags:
            fail(f"Phase-2 dependency-tag drift for {result_id}")

    receipts = {item["path"]: item["sha256"] for item in claim_map["generic_l_terminal_receipts"]}
    if receipts != EXPECTED_GENERIC_RECEIPTS:
        fail("generic-l terminal receipt set drift")
    for path_string, expected_hash in EXPECTED_GENERIC_RECEIPTS.items():
        if digest(ROOT / path_string) != expected_hash:
            fail(f"generic-l terminal receipt hash drift: {path_string}")

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
    if AUTHOR_BLOCK not in text:
        fail("frozen author block drift")
    required_phrases = [
        "Result card A: compact Einstein/additional decomposition",
        "Result card B: finite-harmonic second-order cone",
        "Result card C: complete axial pilot and generic-angular polar disposition",
        "Result card D: strict and compensated local quantum theories",
        "Result card E: causal construction and physical nonselection",
        "R_\\ell(x):=Q_{21}\\bigl(\\ell(\\ell+1),x\\bigr)",
        "canonical-pivot wall is empty",
        "precisely the degeneracy locus of the $p=-2$",
        "\\widehat r=\\frac rM",
        "\\widehat\\omega=M\\omega",
        "C'=-2C/r",
        "zero fibre is a six-dimensional",
        "legacy $E_0$ is not a complete Einstein solution",
        "oscillatory Einstein shear instead diverges",
        "no unrestricted",
        "representative-independent quotient statement",
        "not physical scattering thresholds",
        "N_{\\ell m}=\\int_{S^2}|Y_{\\ell m}|^2\\dd\\Omega>0",
        "h_+(u,v)=",
        "S_{\\rm cf}=",
        "\\operatorname{disc}_wF_2=256q^5(9q-8)<0",
        "\\mathcal N_R[u_1,u_2]",
        "c_{\\rm W}=\\frac{199}{30}",
        "a_{\\rm W}=\\frac{87}{20}",
        "net signed contributions",
        "\\Gamma^{(1)}_{\\rm div}(d)",
        "Stelle's foundational analyses",
        "This is a classification ending, not a viable-theory claim",
        "no positive full-BV state or one-particle Hilbert space",
        "does not construct Mannheim's $CPT$ prescription",
        "24$ real-dimensional open cone",
        "degree-zero-to-one BRST defect rank $102$",
        "not a proof that no BRST-compatible Hadamard",
        "complex spectrum excludes a",
        "the two factor projectors have Lee--Wald residues",
        "constructs neither a",
        "FradkinTseytlin1984",
        "K_{\\rm tr}=",
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
        "$(\\ell,m\\omega)=(2,3/5)$",
        "radial-pairing selection at a Schwarzschild fixture",
        "selects the Einstein sector at the stated",
        "a full covariance is impossible",
        "the Nariai factors are the compact-product branches",
        "the anomaly vanishes under PT",
        "finite $X_0|X_0$ pairing and nonzero finite",
        "$X_0\\mapsto X_0+\\beta E_0$",
        "axial non-Einstein finite formal radial direction for every",
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
    phase1_edges = [
        edge for edge in edges if edge["body"]["edge_kind"] == "OVERVIEW_SYNTHESIS"
    ]
    if {edge["body"]["from"] for edge in phase1_edges} != source_results:
        fail("Paper 15 reverse-coverage result set is incomplete")
    for edge in phase1_edges:
        body = edge["body"]
        if body["edge_kind"] != "OVERVIEW_SYNTHESIS" or body["stale"] is not False:
            fail("Paper 15 coverage edge overpromoted or stale")
        claim = claims.get(body["claim"])
        if not claim or claim["body"]["cites"] != [body["from"]]:
            fail("Paper 15 coverage claim/edge mismatch")

    update_edges = [edge for edge in edges if edge not in phase1_edges]
    if {edge["body"]["from"].removeprefix("sf:result/") for edge in update_edges} != set(EXPECTED_PHASE2):
        fail("Paper 15 post-Phase-1 reverse-coverage result set is incomplete")
    expected_kinds = {item["result_id"]: item["edge_kind"] for item in claim_map["post_phase1_updates"]}
    for edge in update_edges:
        body = edge["body"]
        raw = body["from"].removeprefix("sf:result/")
        if body["edge_kind"] != expected_kinds[raw] or body["stale"] is not False:
            fail(f"Paper 15 update edge drift for {raw}")
        claim = claims.get(body["claim"])
        if not claim or claim["body"]["cites"] != [body["from"]]:
            fail("Paper 15 Phase-2 coverage claim/edge mismatch")

    print("PASS: Paper 15 claim map, append-only reverse coverage, lifecycles, limitations, and scope sentinels")


if __name__ == "__main__":
    main()
