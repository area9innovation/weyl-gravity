#!/usr/bin/env python3
"""Independent semantic and provenance verifier for corrected Paper 14."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], cwd=ROOT, text=True
    ).strip()
)
PREFIX = ROOT.relative_to(REPO).as_posix()
DEFAULT_PAPER = ROOT / "paper/14-pure-weyl-black-hole-radiation.tex"
DEFAULT_MAP = ROOT / "paper/14-pure-weyl-black-hole-radiation-claim-map.json"
DEFAULT_COVERAGE = ROOT / "planning/paper-coverage/paper14-corrected-x0-supersession-overlay-2026-07-22.json"
PARENT_COVERAGE = ROOT / "planning/paper-coverage/phase1-paper-coverage-overlay-2026-07-22.json"

SOURCE_BASELINE = "936d76dbd2a9149243e57a082fa3519f0cfa8724"
GENERIC_RESULT = "PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1"
EXPECTED_AUTHORITY_HASHES = {
    "certificate_sha256": "8a9914400f0929f37a63570b95383ebc4131cbf2928b5f923db0d002d0783d33",
    "receipt_sha256": "0888efb8f14518d38e40bd1b0a3926b8fab37ad729dce798c221a01d24aeabee",
    "report_sha256": "571fab0469b7bfde2b051b94bea657547570376b390a30a5b9ad6b6e93e92558",
    "correction_request_sha256": "308b27ba24076f7e439e36ebceb322442af1b1dcee225449d791cc105f403094",
}
OLD_EDGES = {
    "sf:coverage/edge/PURE_WEYL_BH2C_SYMBOLIC_FLUX_RADIATION_CLASS/paper-14/v1",
    "sf:coverage/edge/PURE_WEYL_BH_ENDPOINT_NONSELECTION_ASSEMBLY/paper-14/v1",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"REFUSED: {message}")


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True, stderr=subprocess.STDOUT
    ).strip()


def resolve(value: Path) -> Path:
    return value if value.is_absolute() else ROOT / value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--claim-map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    args = parser.parse_args()

    paper = resolve(args.paper)
    map_path = resolve(args.claim_map)
    coverage_path = resolve(args.coverage)
    claim_map = json.loads(map_path.read_text())

    if claim_map.get("schema") != "paper-draft-source-map-v1":
        fail("wrong source-map schema")
    if claim_map.get("paper_id") != "PAPER_14_PURE_WEYL_BLACK_HOLE_RADIATION":
        fail("wrong paper identity")
    if claim_map.get("result_id") != "PAPER_14_CORRECTED_X0_SUPERSESSION_V1":
        fail("wrong corrected-paper result identity")
    if claim_map.get("lifecycle_state") != "DRAFT_ALLOWED":
        fail("Paper 14 lifecycle overpromotion")
    if claim_map.get("source_baseline") != SOURCE_BASELINE:
        fail("wrong terminal evidence baseline")
    if git("cat-file", "-t", SOURCE_BASELINE) != "commit":
        fail("source baseline is not a commit")
    if claim_map.get("paper_sha256") != digest(paper):
        fail("paper hash drift")

    authority = claim_map.get("terminal_supersession_authority", {})
    if authority.get("result_id") != GENERIC_RESULT:
        fail("terminal generic-l result not authoritative")
    for field, wanted in EXPECTED_AUTHORITY_HASHES.items():
        if authority.get(field) != wanted:
            fail(f"terminal authority hash drift: {field}")
    for key, hash_key in [
        ("certificate", "certificate_sha256"),
        ("receipt", "receipt_sha256"),
        ("report", "report_sha256"),
        ("correction_request", "correction_request_sha256"),
    ]:
        path = ROOT / authority[key]
        if digest(path) != authority[hash_key]:
            fail(f"terminal authority content drift: {key}")

    generic = json.loads((ROOT / authority["certificate"]).read_text())
    if generic.get("result_id") != GENERIC_RESULT:
        fail("generic-l certificate result mismatch")
    physical = generic["q21_exceptional_frequency_count"]["physical_triangular_harmonics"]
    expected_counts = [
        ("2", 0, 0),
        ("3", 3, 6),
        ("4..10", 1, 2),
        ("11..40", 3, 6),
        (">=41", 1, 2),
    ]
    got_counts = [
        (row["ell"], row["positive_x_roots"], row["real_omega_roots"])
        for row in physical
    ]
    if got_counts != expected_counts:
        fail("Q21 harmonic root-count drift")
    fixture = generic["q21_exceptional_frequency_count"]["legacy_fixture"]
    expected_fixture = (
        "-174226120816040380076641138108451235935620694016/"
        "227373675443232059478759765625"
    )
    if fixture.get("omega_squared") != "9/25" or fixture.get("Q21_value") != expected_fixture:
        fail("Q21 legacy fixture drift")
    if generic["joint_disposition"]["einstein_only_selection"] != (
        "FALSE_IN_THE_DECLARED_FORMAL_RADIAL_CLASS_BY_AXIAL_X0"
    ):
        fail("axial counterexample disposition drift")

    sources = claim_map.get("sources", [])
    if len(sources) < 20:
        fail("active source ledger unexpectedly short")
    seen: set[str] = set()
    for source in sources:
        path = source["path"]
        if path in seen:
            fail(f"duplicate source pin: {path}")
        seen.add(path)
        repo_path = f"{PREFIX}/{path}" if PREFIX else path
        actual = git("rev-parse", f"{SOURCE_BASELINE}:{repo_path}")
        if actual != source["git_blob"]:
            fail(f"source blob drift: {path}")

    scope = claim_map.get("certified_scope", {})
    required_true = {
        "static_laurent_family",
        "normalized_static_first_law",
        "ricci_flat_ricci_bach_composition",
        "axial_horizon_reach_for_ricci_carrier",
        "axial_einstein_self_pairing_exactly_null",
        "polar_ricci_bach_composition",
        "polar_carrier_horizon_reach_modulo_conformal_gauge",
        "horizon_monodromy_temperature_reduced_mode",
        "local_cauchy_truncation_selects_einstein_axial",
        "generic_l_axial_einstein_radial_finiteness",
        "generic_l_axial_corrected_x0_non_einstein_finite",
        "legacy_axial_x0_derivative_defect",
        "polar_mixed_finite_line",
        "polar_q21_exceptional_wall",
        "polar_q21_legacy_fixture_nonzero",
    }
    required_false = {
        "formal_radial_einstein_only_selection",
        "finite_flux_class_fixture_einstein_selected",
        "polar_norm_selection_fixture_einstein_selected",
        "polar_composed_lift_power_enhanced_single_log",
        "composed_metric_log_tails",
        "axial_symbolic_frequency_finite_flux_einstein_selected",
        "invariant_einstein_extra_pairing_rank_signature",
        "one_ended_endpoint_selection_assembled",
        "additional_branch_outgoing_condition_logtail_obstructed",
        "global_horizon_to_infinity_matching",
        "asymptotic_tetrad_falloff_audit",
        "asymptotic_phase_space_charge_algebra",
        "axial_local_causal_truncation_no_go",
        "quantum_claim",
    }
    for key in required_true:
        if scope.get(key) is not True:
            fail(f"required retained/corrected claim not true: {key}")
    for key in required_false:
        if scope.get(key) is not False:
            fail(f"superseded/open claim promoted: {key}")

    text = paper.read_text()
    required_phrases = [
        "M_{\\rm BH}\\omega=3/5",
        "Generic-\\(\\ell\\) axial Einstein radial finiteness",
        "Generic-\\(\\ell\\) axial Einstein-only selection counterexample",
        "Generic polar formal radial disposition",
        "\\frac{2r c'(r)}{r-2m}",
        "c'(r)S_\\ell",
        "S_2/2+O(r^{-2})",
        "Q_{21}(6,9/25)=",
        "174226120816040380076641138108451235935620694016",
        "227373675443232059478759765625",
        "The previously recorded longer rational was \\(Q_{21}(6,81/625)\\)",
        "Whether one global solution",
        "Local Cauchy selection remains available",
        "Normalized static generator",
        "Analytic ingoing curvature family",
        "Exact Einstein isotropy",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"required corrected or preserved phrase missing: {phrase}")
    forbidden_phrases = [
        "finite-slice-norm asymptotic class of the sphere-integrated presymplectic density contains exactly the Einstein sector",
        "every pair involving a composed mode diverges",
        "symplectic-norm finiteness at infinity does",
        "additional-branch outgoing condition is certified",
        "parity complete at the fixture level",
        "well-posed away from the discrete zeros of its connection Wronskian",
        "the finite-flux phase space the additional solution",
        "a global horizon-to-infinity solution is established",
        "Q_{21}(6,81/625)=0",
    ]
    lower = text.lower()
    for phrase in forbidden_phrases:
        if phrase.lower() in lower:
            fail(f"superseded or overbroad manuscript phrase present: {phrase}")

    coverage = json.loads(coverage_path.read_text())
    if coverage.get("schema") != "paper14-corrected-x0-supersession-overlay-v1":
        fail("wrong coverage overlay schema")
    if coverage.get("append_only_parent_sha256") != digest(PARENT_COVERAGE):
        fail("coverage parent hash drift")
    if coverage.get("claim_map_sha256") != digest(map_path):
        fail("coverage-to-claim-map hash drift")
    parent_ids = {node["id"] for node in json.loads(PARENT_COVERAGE.read_text())["nodes"]}
    if not OLD_EDGES <= parent_ids:
        fail("superseded parent edge missing")
    nodes = coverage.get("nodes", [])
    corrections = [node for node in nodes if node.get("kind") == "coverage_correction"]
    if {node["body"].get("target_edge") for node in corrections} != OLD_EDGES:
        fail("append-only supersession set incomplete")
    new_edge_id = "sf:coverage/edge/PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1/paper-14/v2"
    for correction in corrections:
        body = correction["body"]
        if body.get("action") != "MARK_STALE_BY_APPEND_ONLY_SUPERSESSION":
            fail("legacy edge not marked stale by append-only correction")
        if body.get("superseded_by") != new_edge_id:
            fail("legacy edge correction points to wrong authority")
    new_edges = [node for node in nodes if node.get("kind") == "result_paper_edge"]
    if len(new_edges) != 1 or new_edges[0]["id"] != new_edge_id:
        fail("new Paper 14 result edge missing or duplicated")
    edge = new_edges[0]["body"]
    if edge.get("stale") is not False or edge.get("edge_kind") != "PRIMARY_THEOREM_CORRECTION":
        fail("new Paper 14 coverage edge is stale or mistyped")

    print(
        "PASS: corrected Paper 14 semantics, terminal hashes, source pins, "
        "claim boundaries, and append-only coverage supersession"
    )


if __name__ == "__main__":
    main()
