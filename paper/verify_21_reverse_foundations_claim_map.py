#!/usr/bin/env python3
"""Independent structural checker for the paper 21 claim map."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAIM_MAP = ROOT / "paper/21-reverse-foundations-of-physics-claim-map.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_without_self(data: dict) -> str:
    body = dict(data)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    data = json.loads(CLAIM_MAP.read_text())
    require(data["result_id"] == "PAPER21_REVERSE_FOUNDATIONS_INTRODUCTION_V1", "wrong result id")
    require(data["lifecycle"] == "WORKING_DRAFT", "paper must remain a working draft")
    require(data["canonical_digest"] == digest_without_self(data), "canonical digest mismatch")

    for name, authority in data["authorities"].items():
        path = ROOT / authority["path"]
        require(path.is_file(), f"missing authority {name}: {path}")
        require(sha256(path) == authority["sha256"], f"authority hash drift: {name}")
        source = json.loads(path.read_text())
        require(source["result_id"] == authority["result_id"], f"authority result drift: {name}")
        require(source["lifecycle"] == authority["lifecycle"], f"authority lifecycle drift: {name}")
        require(source.get("dependency_tags", []) == authority["dependency_tags"], f"authority tag drift: {name}")

    cube = json.loads((ROOT / data["authorities"]["intersection_cube"]["path"]).read_text())
    site = json.loads((ROOT / data["authorities"]["explorer_snapshot"]["path"]).read_text())
    dims = cube["dimensions"]
    atlas = data["atlas_snapshot"]
    require(atlas["axis_sizes"] == [6, 6, 16], "unexpected axis sizes")
    require(atlas["cartesian_total"] == 576, "unexpected Cartesian total")
    require(atlas["emitted_cells"] == dims["emitted_cells"] == 452, "emitted-cell mismatch")
    require(atlas["coverage_classified_cells"] == dims["coverage_classified_cells"] == 371, "classified-cell mismatch")
    require(sum(atlas["emitted_status_counts"].values()) == atlas["emitted_cells"], "status counts do not cover emitted cells")
    require(atlas["synthetic_complements"] == 124, "synthetic complement mismatch")
    require(atlas["total_not_mapped_in_explorer"] == site["counts"]["not_mapped"] == 205, "explorer not-mapped mismatch")
    require(atlas["evidence_records"] == site["counts"]["evidence_records"] == 69, "evidence-record mismatch")
    require(atlas["migration_pending_cells"] == 0, "migration must remain fully reviewed")

    allowed_tags = {"LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"}
    claim_ids = set()
    for claim in data["claims"]:
        require(claim["claim_id"] not in claim_ids, f"duplicate claim id {claim['claim_id']}")
        claim_ids.add(claim["claim_id"])
        require(set(claim["dependency_tags"]) <= allowed_tags, f"invalid dependency tag in {claim['claim_id']}")
        for authority in claim["authorities"]:
            require(authority in data["authorities"], f"unknown authority in {claim['claim_id']}")
    require(claim_ids == {f"RF-{n:02d}-{suffix}" for n, suffix in [
        (1, "TYPED-JUDGEMENT"),
        (2, "NAVIGATIONAL-ATLAS"),
        (3, "EXPLICIT-KREIN-ZF"),
        (4, "STATE-SELECTION-SPLIT"),
        (5, "CODED-WAVE-RCA0"),
        (6, "EVOLUTION-CAUSALITY-SPLIT"),
        (7, "FINITE-CONTINUUM-SPLIT"),
        (8, "FINITE-BV-BOUNDARY"),
    ]}, "claim set drift")

    flags = data["claim_flags"]
    require(flags["static_atlas_appendix_generated"] is True, "static atlas appendix flag is not certified")
    for false_flag in [
        "weakest_foundation_proved",
        "global_physics_implies_choice_theorem",
        "axes_independent_proved",
        "atlas_exhaustive",
        "literature_complete",
        "new_lorentzian_claim",
        "quantum_lifecycle_promoted",
    ]:
        require(flags[false_flag] is False, f"fail-closed flag promoted: {false_flag}")

    paper_path = ROOT / data["paper"]["path"]
    require(sha256(paper_path) == data["paper"]["sha256"], "paper source hash drift")
    appendix_record = data["paper"]["appendix"]
    appendix_path = ROOT / appendix_record["path"]
    atlas_data_path = ROOT / appendix_record["source_path"]
    appendix_generator_path = ROOT / appendix_record["generator_path"]
    require(appendix_path.is_file(), "generated paper appendix is missing")
    require(sha256(appendix_path) == appendix_record["sha256"], "generated appendix hash drift")
    require(sha256(atlas_data_path) == appendix_record["source_sha256"], "appendix atlas-source hash drift")
    require(sha256(appendix_generator_path) == appendix_record["generator_sha256"], "appendix generator hash drift")
    atlas_data = json.loads(atlas_data_path.read_text())
    require(atlas_data["canonical_digest"] == appendix_record["source_canonical_digest"], "appendix atlas-source digest drift")
    require(atlas["axis_options"] == sum(len(axis["keys"]) for axis in atlas_data["axes"]) == 28, "appendix axis-option mismatch")
    require(atlas["implication_nodes"] == len(atlas_data["graph"]["nodes"]) == 12, "appendix implication-node mismatch")
    require(atlas["implication_edges"] == len(atlas_data["graph"]["edges"]) == 10, "appendix implication-edge mismatch")
    require(atlas["strength_ladder_levels"] == len(atlas_data["ladder"]) == 6, "appendix ladder-level mismatch")

    appendix = appendix_path.read_text()
    require(r"All obligations & 88 & 93 & 160 & 30 & 205 & 576" in appendix, "appendix coverage totals drift")
    require("contains 69 evidence records: 18 local result records and 51 literature records" in appendix, "appendix evidence summary drift")
    for axis in atlas_data["axes"]:
        for option in axis["keys"]:
            require(option["label"] in appendix, f"axis option missing from appendix: {option['id']}")
    for edge in atlas_data["graph"]["edges"]:
        fragment = edge["meaning"].replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")
        require(fragment in appendix, f"implication edge missing from appendix: {edge['from']} -> {edge['to']}")
    for step in atlas_data["ladder"]:
        require(rf"\cert{{{step['level']}}}" in appendix, f"ladder gate missing from appendix: {step['level']}")
    linked_evidence = {
        evidence_id
        for edge in atlas_data["graph"]["edges"]
        for evidence_id in edge.get("evidence", [])
    } | {step["source"] for step in atlas_data["ladder"] if step.get("source")}
    for evidence_id in linked_evidence:
        require(rf"\cert{{{evidence_id}}}" in appendix, f"linked evidence missing from appendix: {evidence_id}")

    paper = paper_path.read_text()
    prose = " ".join(paper.split())
    for phrase in [
        r"L+S+M+\Enc(P)",
        r"The cube is not an ontology",
        r"State existence is not state selection",
        r"Weak wave evolution is not causal Green theory",
        r"Exact finite causality is not continuum causality",
        r"none of the case studies constructs a complete Lorentzian off-shell",
        r"reverse-foundations-of-physics-appendices.tex",
    ]:
        require(phrase in prose, f"required boundary missing from paper: {phrase}")
    for citation in [
        "CarcassiAidala2022",
        "Simpson2009",
        "Hardy2001",
        "Chiribella2011",
        "BlackadarFarahKaragila2023",
        "CoquandSpitters2009",
        "HeunenLandsmanSpitters2009",
        "GibbonsHoffmanWootters2004",
        "Baer2015",
        "Pischke2025",
    ]:
        require(f"bibitem{{{citation}}}" in paper, f"missing bibliography entry: {citation}")

    print("PASS paper 21 claim map, authority hashes, atlas counts, and claim boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
