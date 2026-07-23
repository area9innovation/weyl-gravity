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
PHASE3_RESULT = "PURE_WEYL_PHASE3_AXIAL_COMPLETE_RECONSTRUCTION_REPAIR"
PHASE3_COMMIT = "d5d5d6de648795203604d62ce7bc4f4ce6fea510"
ENDPOINT_RESULT = "PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1"
ENDPOINT_CONTENT_COMMIT = "3baef5e665228c747f78935a367c76bb9a00a9df"
ENDPOINT_LIFECYCLE_COMMIT = "0da46f3b0916e4e53f441df37077038892cf89c3"
GLOBAL_V5_RESULT = "PURE_WEYL_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5"
GLOBAL_V5_CONTENT_COMMIT = "54670c5e371200ee1f08b88843cb3e67b3f17b3b"
GLOBAL_V5_LIFECYCLE_COMMIT = "b1eec02b2d04e585fddbf8f6f1c2ba1d0b96c6f1"
EXPECTED_AUTHORITY_HASHES = {
    "certificate_sha256": "8a9914400f0929f37a63570b95383ebc4131cbf2928b5f923db0d002d0783d33",
    "receipt_sha256": "0888efb8f14518d38e40bd1b0a3926b8fab37ad729dce798c221a01d24aeabee",
    "report_sha256": "571fab0469b7bfde2b051b94bea657547570376b390a30a5b9ad6b6e93e92558",
    "correction_request_sha256": "308b27ba24076f7e439e36ebceb322442af1b1dcee225449d791cc105f403094",
}
EXPECTED_PHASE3_HASHES = {
    "certificate_sha256": "13a4077ee8c77cc5b99e379d35aa15afa09ebeea78c0df9a4771b4845c00c990",
    "receipt_sha256": "6aa563238027bc214e9a397c9ac67869695fd8ad2154ce45f5e9fafda1f070b0",
    "report_sha256": "29f6d7cbc8a10b9cf9f97c1a4b205e3e8a2ec7ab2bfc96e434fe6344e55ca30a",
    "atlas_sha256": "e6640a40089445cabef167153911407da61fed5764552292af252b6ae8883f4e",
}
EXPECTED_ENDPOINT_HASHES = {
    "certificate_sha256": "6158a259fcf4f5888df58a3da8ffe8fa0de40d6ae992f1c132a0726218f95162",
    "receipt_sha256": "35f7efd65893b3d534f5dacd79e15d72336e05a9fc615e9cd830e89fa9f826cd",
    "report_sha256": "27d7473135b578a73109f275ceac932728c45b1e003054ee03f6271b3e6b06c5",
    "atlas_sha256": "e24799dac989f714231c05deff18c16d294f6b3613e438909c2a7d7f38600962",
}
EXPECTED_GLOBAL_V5_HASHES = {
    "certificate_sha256": "1b1fbffe77f367b406cb029e64f2a91ec4620de2a5a52213b741e6bd38a6d953",
    "report_sha256": "2467879c12571bcb5e78ccb0c168359ccd3503979a2ed8e86f047a8fcdb23981",
    "atlas_sha256": "05949a2441523b4b4d7803ef6319192a669bb96d7b82109517684c186677241d",
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


def committed_bytes(commit: str, path: str) -> bytes:
    repo_path = f"{PREFIX}/{path}" if PREFIX else path
    return subprocess.check_output(["git", "show", f"{commit}:{repo_path}"], cwd=REPO)


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
    if claim_map.get("result_id") != "PAPER_14_PHASE3_ENDPOINT_FLUX_UPDATE_V3":
        fail("wrong Phase-3 paper result identity")
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

    phase3 = claim_map.get("phase3_axial_authority", {})
    if phase3.get("result_id") != PHASE3_RESULT:
        fail("Phase-3 axial result not authoritative")
    if phase3.get("source_commit") != PHASE3_COMMIT or git("cat-file", "-t", PHASE3_COMMIT) != "commit":
        fail("Phase-3 source commit drift")
    for field, wanted in EXPECTED_PHASE3_HASHES.items():
        if phase3.get(field) != wanted:
            fail(f"Phase-3 authority hash drift: {field}")
    for key, hash_key in [
        ("certificate", "certificate_sha256"),
        ("receipt", "receipt_sha256"),
        ("report", "report_sha256"),
        ("atlas", "atlas_sha256"),
    ]:
        path = ROOT / phase3[key]
        if digest(path) != phase3[hash_key]:
            fail(f"Phase-3 authority content drift: {key}")

    endpoint = claim_map.get("phase3_endpoint_flux_authority", {})
    if endpoint.get("result_id") != ENDPOINT_RESULT:
        fail("Phase-3 endpoint result not authoritative")
    if endpoint.get("content_commit") != ENDPOINT_CONTENT_COMMIT:
        fail("endpoint content commit drift")
    if endpoint.get("lifecycle_commit") != ENDPOINT_LIFECYCLE_COMMIT:
        fail("endpoint lifecycle commit drift")
    for commit in [ENDPOINT_CONTENT_COMMIT, ENDPOINT_LIFECYCLE_COMMIT]:
        if git("cat-file", "-t", commit) != "commit":
            fail("endpoint provenance pin is not a commit")
    for field, wanted in EXPECTED_ENDPOINT_HASHES.items():
        if endpoint.get(field) != wanted:
            fail(f"endpoint authority hash drift: {field}")
    for key, hash_key in [
        ("certificate", "certificate_sha256"),
        ("receipt", "receipt_sha256"),
        ("report", "report_sha256"),
        ("atlas", "atlas_sha256"),
    ]:
        path = ROOT / endpoint[key]
        if digest(path) != endpoint[hash_key]:
            fail(f"endpoint authority content drift: {key}")

    global_v5 = claim_map.get("phase3_global_connection_shortfall", {})
    if global_v5.get("result_id") != GLOBAL_V5_RESULT:
        fail("global v5 shortfall result mismatch")
    if global_v5.get("content_commit") != GLOBAL_V5_CONTENT_COMMIT:
        fail("global v5 content commit drift")
    if global_v5.get("lifecycle_commit") != GLOBAL_V5_LIFECYCLE_COMMIT:
        fail("global v5 lifecycle commit drift")
    for commit in [GLOBAL_V5_CONTENT_COMMIT, GLOBAL_V5_LIFECYCLE_COMMIT]:
        if git("cat-file", "-t", commit) != "commit":
            fail("global v5 provenance pin is not a commit")
    if global_v5.get("lifecycle") != "NUMERIC-ENCLOSURE":
        fail("global v5 lifecycle drift")
    if global_v5.get("disposition") != "SHORTFALL":
        fail("global v5 disposition overpromotion")
    for field, wanted in EXPECTED_GLOBAL_V5_HASHES.items():
        if global_v5.get(field) != wanted:
            fail(f"global v5 committed hash drift: {field}")
    for key, hash_key in [
        ("certificate", "certificate_sha256"),
        ("report", "report_sha256"),
        ("atlas", "atlas_sha256"),
    ]:
        if hashlib.sha256(
            committed_bytes(GLOBAL_V5_CONTENT_COMMIT, global_v5[key])
        ).hexdigest() != global_v5[hash_key]:
            fail(f"global v5 committed content drift: {key}")

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
    repair = json.loads((ROOT / phase3["certificate"]).read_text())
    if repair.get("result_id") != PHASE3_RESULT:
        fail("Phase-3 certificate result mismatch")
    if repair["complete_reconstruction"]["constraint"]["propagation"] != "dC/dr=-2*C/r":
        fail("axial constraint propagation drift")
    if repair["dimension_and_rank"]["complete_metric_dimension"] != 6:
        fail("complete axial module dimension drift")
    warning = repair["downstream_current_warning"]
    if warning["status"] != "EXACT ASYMPTOTIC COEFFICIENT AUDIT; not a finite-flux phase-space theorem":
        fail("current-audit scope drift")
    if warning["finite_rate_zero_table_at_p_minus_2"]["Xfull_cross_Xfull"] != (
        "32*I*pi*alpha_W*(540-omega^2)/(15*omega^3*(omega^2+4))"
    ):
        fail("repaired X0 finite coefficient drift")
    if "r^(3-4*I*omega)" not in warning["Eosc_cross_Xfull"]:
        fail("oscillatory divergent cross term drift")
    endpoint_result = json.loads((ROOT / endpoint["certificate"]).read_text())
    if endpoint_result.get("result_id") != ENDPOINT_RESULT:
        fail("endpoint certificate result mismatch")
    declaration = endpoint_result["declaration"]
    if declaration["background"] != "Schwarzschild exterior with M=1":
        fail("endpoint background drift")
    if declaration["sector"] != "axial ell=2":
        fail("endpoint sector drift")
    if declaration["frequency_interval"] != ["1/2", "3/4"]:
        fail("endpoint frequency interval drift")
    if declaration["completion"] != "L2([1/2,3/4];C^3)":
        fail("endpoint completion drift")
    verdict = endpoint_result["common_verdict"]
    if verdict["quotient_dimension"] != 3 or verdict["rank"] != 3:
        fail("endpoint dimension/rank drift")
    if verdict["radical_dimension"] != 0:
        fail("endpoint radical drift")
    if verdict["inertia_for_alpha_W_positive"] != [1, 2, 0]:
        fail("endpoint inertia drift")
    if verdict["frequency_walls"] != []:
        fail("endpoint frequency-wall drift")
    flags = endpoint_result["claim_flags"]
    if not all(
        flags[key]
        for key in [
            "Iminus_flux_Gram_certified",
            "Iplus_flux_Gram_certified",
            "action_current_pulled_back",
            "endpoint_rank_radical_inertia_certified",
            "trace_limit_interchange_proved",
        ]
    ):
        fail("endpoint certified flags drift")
    if any(
        flags[key]
        for key in [
            "global_connection_constructed",
            "horizon_to_infinity_matching_constructed",
            "scattering_channels_classified",
            "stability_or_CPT_established",
        ]
    ):
        fail("endpoint certificate overpromotes a global/physical claim")
    global_v5_result = json.loads(
        committed_bytes(GLOBAL_V5_CONTENT_COMMIT, global_v5["certificate"])
    )
    if global_v5_result.get("result_id") != GLOBAL_V5_RESULT:
        fail("global v5 certificate identity drift")
    if global_v5_result.get("stop_condition_disposition") != "SHORTFALL":
        fail("global v5 certificate no longer records SHORTFALL")
    v5_flags = global_v5_result["claim_flags"]
    if v5_flags["global_connection_certified"] or v5_flags["lower_lift_certified"]:
        fail("global v5 shortfall silently promoted")

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
        "axial_l2_complete_six_dimensional_endpoint_module",
        "axial_l2_constraint_propagation_c_prime_minus_2c_over_r",
        "axial_l2_repaired_x0_fixed_representative_finite",
        "axial_l2_rate_zero_einstein_shear_finite",
        "axial_l2_oscillatory_einstein_shear_divergent",
        "legacy_axial_x0_derivative_defect",
        "polar_mixed_finite_line",
        "polar_q21_exceptional_wall",
        "polar_q21_legacy_fixture_nonzero",
        "axial_l2_endpoint_trace_dimensions_three_three",
        "axial_l2_endpoint_flux_grams_action_derived",
        "axial_l2_endpoint_flux_grams_rank_three",
        "axial_l2_endpoint_flux_grams_radical_zero",
        "axial_l2_endpoint_flux_grams_inertia_one_two_zero_alpha_positive",
        "axial_l2_endpoint_flux_frequency_wall_absent_on_pilot",
        "axial_l2_endpoint_trace_limit_interchange",
        "axial_global_connection_v5_method_shortfall_recorded",
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
        "generic_l_axial_einstein_radial_finiteness",
        "generic_l_axial_corrected_x0_non_einstein_finite",
        "axial_l2_unrestricted_representative_independence",
        "global_horizon_to_infinity_matching",
        "asymptotic_tetrad_falloff_audit",
        "asymptotic_phase_space_charge_algebra",
        "axial_local_causal_truncation_no_go",
        "quantum_claim",
        "axial_l2_endpoint_direction_globally_populated",
        "axial_l2_endpoint_flux_positive_energy",
        "axial_l2_endpoint_flux_cpt_or_stability",
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
        "Scoped axial reconstruction and radial disposition",
        "C'=-\\frac2r C",
        "\\mathcal E_{\\rm Bach,ax}^{6}",
        "is not itself a complete Einstein solution",
        "under true rate-zero Einstein shears",
        "true oscillatory Einstein shears",
        "no representative-independent axial selection",
        "Generic polar formal radial disposition",
        "Q_{21}(6,9/25)=",
        "174226120816040380076641138108451235935620694016",
        "227373675443232059478759765625",
        "The previously recorded longer rational was \\(Q_{21}(6,81/625)\\)",
        "Whether one global solution",
        "Local Cauchy selection remains available",
        "Normalized static generator",
        "Analytic ingoing curvature family",
        "Exact Einstein isotropy",
        "Scoped axial null-endpoint flux",
        "\\mathcal X_{\\mathscr I^-}",
        "\\mathcal X_{\\mathscr I^+}",
        "\\det G_-",
        "\\operatorname{inertia}(G_-)",
        "not a global scattering theorem",
        "(XH0a,XH0b,EH0,XHplus,EHout,XHminus)",
        "raw future-regular columns \\(0,1,2\\)",
        "ended in \\textsc{shortfall}",
        "evidence that the Bach connection fails to exist",
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
        "Generic-\\(\\ell\\) axial Einstein radial finiteness",
        "Generic-\\(\\ell\\) axial Einstein-only selection counterexample",
        "corrected non-Einstein lift exists formally for every",
        "This remains finite under $X_0\\mapsto X_0+\\beta E_0$",
        "endpoint flux proves a physical ghost",
        "endpoint flux selects the Einstein sector",
        "a globally populated negative scattering channel is established",
        "v5 proves that no global connection exists",
    ]
    lower = text.lower()
    for phrase in forbidden_phrases:
        if phrase.lower() in lower:
            fail(f"superseded or overbroad manuscript phrase present: {phrase}")

    coverage = json.loads(coverage_path.read_text())
    if coverage.get("schema") != "paper14-phase3-endpoint-flux-overlay-v3":
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
    new_edge_id = "sf:coverage/edge/PURE_WEYL_PHASE3_AXIAL_COMPLETE_RECONSTRUCTION_REPAIR/paper-14/v1"
    for correction in corrections:
        body = correction["body"]
        if body.get("action") != "MARK_STALE_BY_APPEND_ONLY_SUPERSESSION":
            fail("legacy edge not marked stale by append-only correction")
        if body.get("superseded_by") != new_edge_id:
            fail("legacy edge correction points to wrong authority")
    new_edges = {node["id"]: node for node in nodes if node.get("kind") == "result_paper_edge"}
    expected_edges = {
        new_edge_id,
        "sf:coverage/edge/PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1/paper-14/v2",
        "sf:coverage/edge/PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1/paper-14/v1",
        "sf:coverage/edge/PURE_WEYL_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5/paper-14/v1",
    }
    if set(new_edges) != expected_edges:
        fail("Paper 14 Phase-2/Phase-3 result edges missing or duplicated")
    edge = new_edges[new_edge_id]["body"]
    if edge.get("stale") is not False or edge.get("edge_kind") != "PRIMARY_THEOREM_CORRECTION":
        fail("new Paper 14 coverage edge is stale or mistyped")
    polar_edge = new_edges["sf:coverage/edge/PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1/paper-14/v2"]["body"]
    if polar_edge.get("edge_kind") != "SUPPORTING_POLAR_THEOREM":
        fail("Phase-2 generic result was not demoted to polar supporting scope")
    endpoint_edge = new_edges[
        "sf:coverage/edge/PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1/paper-14/v1"
    ]["body"]
    if endpoint_edge.get("edge_kind") != "PRIMARY_ENDPOINT_THEOREM":
        fail("endpoint flux result edge is mistyped")
    global_v5_edge = new_edges[
        "sf:coverage/edge/PURE_WEYL_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5/paper-14/v1"
    ]["body"]
    if (
        global_v5_edge.get("edge_kind") != "METHOD_SHORTFALL"
        or global_v5_edge.get("asserts_lifecycle") is not None
    ):
        fail("global v5 shortfall edge is mistyped")

    print(
        "PASS: corrected Paper 14 semantics, terminal hashes, source pins, "
        "claim boundaries, and append-only coverage supersession"
    )


if __name__ == "__main__":
    main()
