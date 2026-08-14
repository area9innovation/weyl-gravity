#!/usr/bin/env python3
"""Independent structural checker for the paper 21 claim map."""

from __future__ import annotations

import hashlib
import json
import collections
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


def tex(value: object) -> str:
    text = str(value)
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("×", r"\(\times\)"),
        ("→", r"\(\rightarrow\)"),
        ("—", "---"),
        ("–", "--"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def scientific_tex(value: object) -> str:
    text = tex(value)
    for plain, formula in [
        (r"G\_mu\_nu=0", r"\(G_{\mu\nu}=0\)"),
        ("f(r)=1-2m/r", r"\(f(r)=1-2m/r\)"),
        ("beta=gamma=1", r"\(\beta=\gamma=1\)"),
        ("gamma-1=0", r"\(\gamma-1=0\)"),
        ("1+gamma=2", r"\(1+\gamma=2\)"),
        ("gamma+1", r"\(\gamma+1\)"),
    ]:
        text = text.replace(plain, formula)
    return text


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
        require(source.get("result_id", source.get("certificate")) == authority["result_id"], f"authority result drift: {name}")
        require(source.get("lifecycle", source.get("lifecycle_state")) == authority["lifecycle"], f"authority lifecycle drift: {name}")
        require(source.get("dependency_tags", []) == authority["dependency_tags"], f"authority tag drift: {name}")

    cube = json.loads((ROOT / data["authorities"]["intersection_cube"]["path"]).read_text())
    site = json.loads((ROOT / data["authorities"]["explorer_snapshot"]["path"]).read_text())
    gr_cassini = json.loads((ROOT / data["authorities"]["gr_cassini_assembly"]["path"]).read_text())
    bt_euclidean = json.loads((ROOT / data["authorities"]["bt_euclidean_import"]["path"]).read_text())
    bt_free_obstruction = json.loads((ROOT / data["authorities"]["bt_free_reconstruction_obstruction"]["path"]).read_text())
    dims = cube["dimensions"]
    atlas = data["atlas_snapshot"]
    require(atlas["axis_sizes"] == [6, 6, 16], "unexpected axis sizes")
    require(atlas["cartesian_total"] == 576, "unexpected Cartesian total")
    require(atlas["emitted_cells"] == dims["emitted_cells"] == 576, "emitted-cell mismatch")
    require(atlas["coverage_classified_cells"] == dims["coverage_classified_cells"] == 576, "classified-cell mismatch")
    require(sum(atlas["emitted_status_counts"].values()) == atlas["emitted_cells"], "status counts do not cover emitted cells")
    require(atlas["synthetic_complements"] == 0, "synthetic complement mismatch")
    require(atlas["total_not_mapped_in_explorer"] == site["counts"]["not_mapped"] == 0, "explorer not-mapped mismatch")
    require(atlas["reviewed_open_gaps"] == site["counts"]["reviewed_gap"] == 172, "reviewed-gap mismatch")
    require(atlas["evidence_records"] == site["counts"]["evidence_records"] == 75, "evidence-record mismatch")
    require(atlas["literature_records"] == 51, "literature-record mismatch")
    require(atlas["local_result_records"] == 24, "local-result-record mismatch")
    require(atlas["content_pinned_literature"] == 39, "content-pinned literature mismatch")
    require(atlas["metadata_only_literature"] == 12, "metadata-only literature mismatch")
    require(atlas["evidence_records_used_by_matrix"] == 75, "matrix evidence usage is incomplete")
    require(atlas["migration_pending_cells"] == 0, "migration must remain fully reviewed")
    require(atlas["all_cells_assessed"] is True, "full-surface assessment flag is not certified")
    require(atlas["bt_euclidean_direct_capabilities"] == 5, "BT direct-capability count mismatch")
    require(atlas["bt_euclidean_reconstruction_status"] == "PRIORITY_GAP", "BT reconstruction boundary mismatch")
    require(atlas["bt_euclidean_numerical_status"] == "COARSE_REPRODUCTION_ONLY", "BT numerical status mismatch")
    require(atlas["bt_euclidean_carrier_relation"] == "INCOMPATIBLE", "BT carrier relation mismatch")
    require(bt_euclidean["claim_flags"]["continuum_reconstruction_established"] is False, "BT continuum claim promoted")
    require(atlas["bt_free_os_reflected_norm"] == {"numerator": -1, "denominator": 1296}, "BT reflected norm drift")
    require(atlas["bt_free_os_near_zero_status"] == "OBSTRUCTED_ON_SOME_OPEN_INTERVAL", "BT near-zero OS status drift")
    require(atlas["bt_free_os_lambda_0p4_status"] == "OPEN", "BT lambda=0.4 status promoted")
    require(atlas["bt_free_h_minus_one_bound"] == {"numerator": 15, "denominator": 32}, "BT H^-1 bound drift")
    require(atlas["bt_free_l2_status"] == "OBSTRUCTED", "BT L2 obstruction drift")
    require(bt_free_obstruction["disposition"]["continuum_limit"] == "NOT_ESTABLISHED", "BT free estimate promoted to continuum")

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
        (9, "GR-CASSINI-ASSEMBLY"),
        (10, "BT-EUCLIDEAN-LATTICE"),
        (11, "BT-FREE-RECONSTRUCTION-OBSTRUCTION"),
    ]}, "claim set drift")

    flags = data["claim_flags"]
    require(flags["static_atlas_appendix_generated"] is True, "static atlas appendix flag is not certified")
    require(flags["complete_evidence_register_generated"] is True, "complete evidence register flag is not certified")
    require(flags["complete_literature_register_generated"] is True, "complete literature register flag is not certified")
    require(flags["evidence_usage_crosswalk_generated"] is True, "evidence crosswalk flag is not certified")
    require(flags["model_scoped_end_to_end_assembly_generated"] is True, "model-scoped assembly flag is not certified")
    require(flags["bounded_empirical_comparison_registered"] is True, "bounded empirical comparison flag is not certified")
    require(flags["bt_euclidean_finite_capabilities_imported"] is True, "BT finite import flag is not certified")
    require(flags["bt_euclidean_coarse_reproduction_separated"] is True, "BT numerical separation flag is not certified")
    require(flags["bt_free_os_obstruction_certified"] is True, "BT OS obstruction flag is not certified")
    require(flags["bt_free_h_minus_one_estimate_certified"] is True, "BT free uniform estimate flag is not certified")
    require(flags["bt_lambda_0p4_os_status_decided"] is False, "BT lambda=0.4 OS status promoted")
    require(flags["research_programme_lenses_explained"] is True, "research-programme exposition flag is not certified")
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
    assembly_data_path = ROOT / appendix_record["assembly_source_path"]
    appendix_generator_path = ROOT / appendix_record["generator_path"]
    require(appendix_path.is_file(), "generated paper appendix is missing")
    require(sha256(appendix_path) == appendix_record["sha256"], "generated appendix hash drift")
    require(sha256(atlas_data_path) == appendix_record["source_sha256"], "appendix atlas-source hash drift")
    require(sha256(assembly_data_path) == appendix_record["assembly_source_sha256"], "appendix assembly-source hash drift")
    require(sha256(appendix_generator_path) == appendix_record["generator_sha256"], "appendix generator hash drift")
    atlas_data = json.loads(atlas_data_path.read_text())
    assembly_data = json.loads(assembly_data_path.read_text())
    require(atlas_data["canonical_digest"] == appendix_record["source_canonical_digest"], "appendix atlas-source digest drift")
    require(assembly_data["canonical_digest"] == appendix_record["assembly_source_canonical_digest"], "appendix assembly-source digest drift")
    require(atlas["axis_options"] == sum(len(axis["keys"]) for axis in atlas_data["axes"]) == 28, "appendix axis-option mismatch")
    require(atlas["implication_nodes"] == len(atlas_data["graph"]["nodes"]) == 12, "appendix implication-node mismatch")
    require(atlas["implication_edges"] == len(atlas_data["graph"]["edges"]) == 10, "appendix implication-edge mismatch")
    require(atlas["strength_ladder_levels"] == len(atlas_data["ladder"]) == 6, "appendix ladder-level mismatch")
    require(atlas["prototype_assemblies"] == len(assembly_data["assemblies"]) == 9, "appendix assembly-count mismatch")
    require(atlas["research_programme_lenses"] == 9, "research-programme lens metadata mismatch")
    require(atlas["model_scoped_assemblies"] == len(assembly_data["model_scoped_assemblies"]) == 1, "model-scoped assembly-count mismatch")
    model = assembly_data["model_scoped_assemblies"][0]
    require(model["result_id"] == gr_cassini["result_id"], "GR/Cassini model assembly identity drift")
    require(model["canonical_digest"] == gr_cassini["canonical_digest"], "GR/Cassini embedded assembly digest drift")
    require(atlas["gr_cassini_stages"] == len(gr_cassini["stages"]) == 6, "GR/Cassini stage-count mismatch")
    require(atlas["gr_cassini_interfaces"] == len(gr_cassini["interfaces"]) == 5, "GR/Cassini interface-count mismatch")
    require(atlas["gr_cassini_required_obligations"] == gr_cassini["applicability_summary"]["required"] == 3, "GR/Cassini applicability count mismatch")
    require(atlas["gr_cassini_required_obligations_satisfied"] == 3, "GR/Cassini required obligations are not closed")
    require(atlas["gr_cassini_bounded_complete"] is gr_cassini["assembly_disposition"]["complete_within_declared_scope"] is True, "GR/Cassini bounded completion is not certified")
    require(atlas["gr_cassini_prediction_inside_reported_band"] is gr_cassini["empirical_comparison_rail"]["prediction_inside_reported_band"] is True, "GR/Cassini comparison is not supported in the reported band")
    require(gr_cassini["assembly_disposition"]["complete_theory"] is False, "bounded GR assembly promoted to complete theory")
    require(gr_cassini["claim_flags"]["raw_cassini_data_reanalysed"] is False, "Cassini literature comparison promoted to raw-data reanalysis")
    standard = next(item for item in assembly_data["assemblies"] if item["id"] == "STANDARD_MIXED_REFERENCE")
    require(atlas["standard_reference_direct_obligations"] == standard["coverage"]["direct"] == 16, "classical reference coverage mismatch")
    control = assembly_data["calibration_controls"][0]
    require(atlas["external_calibration_records"] == len(control["records"]) == 4, "calibration record mismatch")
    require(atlas["external_calibration_benchmark_families"] == sum(item["status"] == "SUPPORTED_CONTROL" for item in control["benchmark_coverage"]) == 3, "calibration benchmark mismatch")

    appendix = appendix_path.read_text()
    for token in ("Bateman--Turok", "Mannheim conformal-gravity programme", "Pure-Weyl BV--BFV"):
        require(token in appendix, f"research-programme lens missing from appendix: {token}")
    require(r"All obligations & 120 & 91 & 163 & 30 & 172 & 0 & 576" in appendix, "appendix coverage totals drift")
    require("contains 75 evidence records: 24 local result records and 51 literature records" in appendix, "appendix evidence summary drift")
    require("BT positive Euclidean lattice programme" in appendix, "BT Euclidean prototype missing")
    require("COARSE REPRODUCTION ONLY" in appendix, "BT numerical boundary missing")
    require("The classical-standard mixed-carrier reference has complete direct coverage" in appendix, "classical reference calibration missing")
    require("First bounded end-to-end assembly" in appendix, "model-scoped GR/Cassini appendix section missing")
    require("The six typed stages of the standard-GR solar-exterior assembly" in appendix, "GR/Cassini stage table missing")
    require(tex(gr_cassini["assembly_disposition"]["status"].replace("_", " ").lower()) in appendix, "GR/Cassini bounded disposition missing")
    require("applicability mask requires 3" in appendix, "GR/Cassini applicability summary missing")
    for stage in gr_cassini["stages"]:
        require(tex(stage["label"]) in appendix, f"GR/Cassini stage missing: {stage['id']}")
        require(scientific_tex(stage["establishes"]) in appendix, f"GR/Cassini stage boundary missing: {stage['id']}")
    for record in control["records"]:
        require(tex(record["citation"]) in appendix, f"calibration citation missing: {record['id']}")
        require(tex(record["boundary"]) in appendix, f"calibration boundary missing: {record['id']}")
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

    evidence = atlas_data["evidence"]
    require(appendix.count(r"\hypertarget{atlas-evidence-") == 75, "evidence-register anchor count drift")
    require(appendix.count(r"\hyperlink{atlas-evidence-") == 75, "evidence-crosswalk link count drift")
    cell_usage = {evidence_id: [] for evidence_id in evidence}
    for cell in atlas_data["cells"]:
        for evidence_id in cell.get("evidence", []):
            require(evidence_id in evidence, f"cell references unknown evidence: {evidence_id}")
            cell_usage[evidence_id].append(cell)
    graph_usage = collections.defaultdict(list)
    for edge_number, edge in enumerate(atlas_data["graph"]["edges"], start=1):
        for evidence_id in edge.get("evidence", []):
            require(evidence_id in evidence, f"graph references unknown evidence: {evidence_id}")
            graph_usage[evidence_id].append(edge_number)
    ladder_usage = collections.defaultdict(list)
    for step in atlas_data["ladder"]:
        if step.get("source"):
            require(step["source"] in evidence, f"ladder references unknown evidence: {step['source']}")
            ladder_usage[step["source"]].append(step["level"])
    status_order = ["LOCAL_RESULT", "LITERATURE_RESULT", "PIECES_ONLY", "PRIORITY_GAP", "REVIEWED_GAP", "NOT_MAPPED"]
    status_short = {
        "LOCAL_RESULT": "Local",
        "LITERATURE_RESULT": "Literature",
        "PIECES_ONLY": "Pieces",
        "PRIORITY_GAP": "Priority gap",
        "REVIEWED_GAP": "Reviewed gap",
        "NOT_MAPPED": "Not mapped",
    }

    for number, (evidence_id, entry) in enumerate(sorted(evidence.items()), start=1):
        anchor = f"atlas-evidence-{number}"
        require(
            rf"\hypertarget{{{anchor}}}{{\cert{{{evidence_id}}}}}" in appendix,
            f"evidence register entry missing: {evidence_id}",
        )
        require(
            rf"\hyperlink{{{anchor}}}{{\cert{{{evidence_id}}}}}" in appendix,
            f"evidence crosswalk entry missing: {evidence_id}",
        )
        require(cell_usage[evidence_id], f"evidence record has no matrix usage: {evidence_id}")
        status_counts = collections.Counter(cell["status"] for cell in cell_usage[evidence_id])
        status_summary = ", ".join(
            f"{status_short[status]} {status_counts[status]}"
            for status in status_order
            if status_counts[status]
        )
        matrix_use = f"{len(cell_usage[evidence_id])} coordinates ({status_summary})."
        target = rf"\hyperlink{{{anchor}}}{{\cert{{{evidence_id}}}}}"
        target += " (literature)" if entry["kind"] == "LITERATURE" else " (local)"
        require(
            f"{target} & {tex(matrix_use)} &" in appendix,
            f"matrix usage count missing: {evidence_id}",
        )
        if graph_usage[evidence_id]:
            require(
                "graph edges " + ", ".join(map(str, graph_usage[evidence_id])) in appendix,
                f"graph crosswalk missing: {evidence_id}",
            )
        if ladder_usage[evidence_id]:
            require(
                tex("ladder " + ", ".join(ladder_usage[evidence_id])) in appendix,
                f"ladder crosswalk missing: {evidence_id}",
            )
        if entry["kind"] == "LITERATURE":
            for field in ["citation", "source_kind", "artifact_status", "stable_url", "supported_statements", "boundary"]:
                require(field in entry, f"literature record lacks {field}: {evidence_id}")
            require(tex(entry["citation"]) in appendix, f"literature citation missing: {evidence_id}")
            require(rf"\url{{{entry['stable_url']}}}" in appendix, f"literature URL missing: {evidence_id}")
            require(rf"\cert{{{entry['artifact_status']}}}" in appendix, f"artifact status missing: {evidence_id}")
            for statement in entry["supported_statements"]:
                require(tex(statement) in appendix, f"supported statement missing: {evidence_id}")
            require(tex(entry["boundary"]) in appendix, f"literature boundary missing: {evidence_id}")
        else:
            for field in ["result_path", "report_path", "result_kind", "lifecycle", "dependency_tags", "claim_flags", "does_not_establish"]:
                require(field in entry, f"local record lacks {field}: {evidence_id}")
            require(rf"\cert{{{entry['result_path']}}}" in appendix, f"result locator missing: {evidence_id}")
            require(rf"\cert{{{entry['report_path']}}}" in appendix, f"report locator missing: {evidence_id}")
            for tag in entry["dependency_tags"]:
                require(tag in appendix, f"local dependency tag missing: {evidence_id} / {tag}")
            for exclusion in entry["does_not_establish"]:
                require(tex(exclusion) in appendix, f"local boundary item missing: {evidence_id}")
            for flag, enabled in entry["claim_flags"].items():
                if enabled:
                    require(tex(flag.replace("_", " ")) in appendix, f"local positive flag missing: {evidence_id} / {flag}")

    paper = paper_path.read_text()
    prose = " ".join(paper.split())
    for phrase in [
        r"L+S+M+\Enc(P)",
        r"The cube is not an ontology",
        r"State existence is not state selection",
        r"Weak wave evolution is not causal Green theory",
        r"Exact finite causality is not continuum causality",
        r"none of the case studies constructs a complete Lorentzian off-shell",
        r"bounded prediction assembly",
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
        "Bertotti2003",
        "Kramer2021",
        "LVKGWTC32021",
        "AbbottGW1708172017",
    ]:
        require(f"bibitem{{{citation}}}" in paper, f"missing bibliography entry: {citation}")

    print("PASS paper 21 claim map, authority hashes, atlas counts, and claim boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
