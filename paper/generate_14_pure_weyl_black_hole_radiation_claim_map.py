#!/usr/bin/env python3
"""Generate Paper 14's corrected source map and append-only coverage overlay."""

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
SOURCE_BASELINE = "936d76dbd2a9149243e57a082fa3519f0cfa8724"

PAPER = ROOT / "paper/14-pure-weyl-black-hole-radiation.tex"
OUTPUT = ROOT / "paper/14-pure-weyl-black-hole-radiation-claim-map.json"
PARENT_COVERAGE = ROOT / "planning/paper-coverage/phase1-paper-coverage-overlay-2026-07-22.json"
COVERAGE_OUTPUT = ROOT / "planning/paper-coverage/paper14-corrected-x0-supersession-overlay-2026-07-22.json"

GENERIC_CERT = ROOT / "black_hole_programme/phase2/generic_l_synthesis/certificate.json"
GENERIC_RECEIPT = ROOT / "black_hole_programme/phase2/generic_l_synthesis/receipt.json"
GENERIC_REPORT = ROOT / "reports/phase2-black-hole-generic-l-disposition-2026-07-22.md"
CORRECTION_REQUEST = ROOT / "planning/paper-coverage/phase2-black-hole-paper-correction-request.json"
PHASE3_CERT = ROOT / "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json"
PHASE3_RECEIPT = ROOT / "black_hole_programme/phase3/axial_complete_reconstruction_repair/receipt.json"
PHASE3_REPORT = ROOT / "reports/phase3-black-hole-axial-complete-reconstruction-repair-2026-07-22.md"
PHASE3_ATLAS = ROOT / "residual_atlas/phase3-black-hole-axial-complete-reconstruction-repair-fragment-v1.json"
PHASE3_COMMIT = "d5d5d6de648795203604d62ce7bc4f4ce6fea510"
ENDPOINT_CERT = ROOT / "black_hole_programme/phase3/axial_null_flux_gram/certificate.json"
ENDPOINT_RECEIPT = ROOT / "black_hole_programme/phase3/axial_null_flux_gram/receipt.json"
ENDPOINT_REPORT = ROOT / "reports/phase3-black-hole-axial-null-flux-gram-2026-07-23.md"
ENDPOINT_ATLAS = ROOT / "residual_atlas/phase3-black-hole-axial-null-flux-gram-fragment-v1.json"
ENDPOINT_CONTENT_COMMIT = "332564286df69b0638aa8c618aa64e39581ab090"
ENDPOINT_LIFECYCLE_COMMIT = "0da46f3b0916e4e53f441df37077038892cf89c3"
GLOBAL_V5_CONTENT_COMMIT = "54670c5e371200ee1f08b88843cb3e67b3f17b3b"
GLOBAL_V5_LIFECYCLE_COMMIT = "b1eec02b2d04e585fddbf8f6f1c2ba1d0b96c6f1"
GLOBAL_V5_CERT = "black_hole_programme/phase3/axial_global_connection_matrix_v5/certificate.json"
GLOBAL_V5_REPORT = "reports/phase3-black-hole-axial-global-connection-matrix-v5-2026-07-23.md"
GLOBAL_V5_ATLAS = "residual_atlas/phase3-black-hole-axial-global-connection-matrix-v5-fragment-v1.json"
OUTGOING_POINT_CERT = ROOT / "black_hole_programme/phase3/axial_outgoing_population_point_half_v1/certificate.json"
OUTGOING_POINT_RECEIPT = ROOT / "black_hole_programme/phase3/axial_outgoing_population_point_half_v1/receipt.json"
OUTGOING_POINT_REPORT = ROOT / "reports/phase3-axial-outgoing-population-point-half-2026-07-24.md"
OUTGOING_CELL_CERT = ROOT / "black_hole_programme/phase3/axial_outgoing_population_cell_half_v1/certificate.json"
OUTGOING_CELL_RECEIPT = ROOT / "black_hole_programme/phase3/axial_outgoing_population_cell_half_v1/receipt.json"
OUTGOING_CELL_REPORT = ROOT / "reports/phase3-axial-outgoing-population-cell-half-2026-07-24.md"
EVANS_V7_CERT = ROOT / "black_hole_programme/phase3/axial_qnm_adaptive_dyadic_boundary_chunk_v7/certificate.json"
EVANS_V7B_CERT = ROOT / "black_hole_programme/phase3/axial_qnm_adaptive_dyadic_boundary_chunk_v7b/certificate.json"
EVANS_V8_CERT = ROOT / "black_hole_programme/phase3/axial_qnm_child_grid_boundary_chunk_v8/certificate.json"
EVANS_V9_CERT = ROOT / "black_hole_programme/phase3/axial_qnm_child_grid_boundary_chunk_v9/certificate.json"
EVANS_V9_RECEIPT = ROOT / "black_hole_programme/phase3/axial_qnm_child_grid_boundary_chunk_v9/receipt.json"
EVANS_V9_REPORT = ROOT / "black_hole_programme/phase3/axial_qnm_child_grid_boundary_chunk_v9/report.md"

ACTIVE_SOURCES = [
    "black_hole_programme/certificates/BH0_STATIC_SPHERICAL_BACKGROUND.json",
    "black_hole_programme/certificates/BH1A_NORMALIZED_GENERATOR.json",
    "black_hole_programme/certificates/BH1B_DYNAMICAL_EXTENSION.json",
    "black_hole_programme/certificates/BH2A_AXIAL_OPERATOR.json",
    "black_hole_programme/certificates/BH2A_HORIZON_REACH.json",
    "black_hole_programme/certificates/BH2A_FLUX_MATRIX.json",
    "black_hole_programme/certificates/BH2A_CROSS_FLUX.json",
    "black_hole_programme/certificates/BH2A_CAUSAL_DISPOSITION.json",
    "black_hole_programme/certificates/BH2B_POLAR_SPLIT.json",
    "black_hole_programme/certificates/BH2B_POLAR_REACH.json",
    "black_hole_programme/certificates/BH2B_POLAR_EINSTEIN.json",
    "black_hole_programme/certificates/BH2B_POLAR_FLUX.json",
    "black_hole_programme/certificates/BH2B_POLAR_CROSS_FLUX.json",
    "black_hole_programme/certificates/BH2B_POLAR_DISPOSITION.json",
    "black_hole_programme/certificates/BH4_HAWKING_MONODROMY.json",
    "black_hole_programme/certificates/BH2_OMEGA_ZERO.json",
    "black_hole_programme/certificates/BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION.json",
    "black_hole_programme/certificates/BH2_SYMBOLIC_CROSS_INVARIANT.json",
    "black_hole_programme/certificates/BH2_GENERAL_L_STRUCTURAL.json",
    "black_hole_programme/certificates/BH3_ANALYTIC_CONTINUATION_GATE.json",
    "black_hole_programme/certificates/BH3_NUMERICAL_VALIDATION_PROTOCOL.json",
    "black_hole_programme/phase2/general_l_axial_asymptotics/certificate.json",
    "black_hole_programme/phase2/general_l_axial_current/certificate.json",
    "black_hole_programme/phase2/general_l_axial_selection/certificate.json",
    "black_hole_programme/phase2/general_l_polar_extendible_current_closure/certificate.json",
    "black_hole_programme/phase2/generic_l_synthesis/certificate.json",
]

SUPERSEDED_EDGES = [
    "sf:coverage/edge/PURE_WEYL_BH2C_SYMBOLIC_FLUX_RADIATION_CLASS/paper-14/v1",
    "sf:coverage/edge/PURE_WEYL_BH_ENDPOINT_NONSELECTION_ASSEMBLY/paper-14/v1",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: str) -> str:
    repo_path = f"{PREFIX}/{path}" if PREFIX else path
    return subprocess.check_output(
        ["git", "rev-parse", f"{SOURCE_BASELINE}:{repo_path}"],
        cwd=REPO,
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def committed_digest(commit: str, path: str) -> str:
    repo_path = f"{PREFIX}/{path}" if PREFIX else path
    content = subprocess.check_output(
        ["git", "show", f"{commit}:{repo_path}"], cwd=REPO
    )
    return hashlib.sha256(content).hexdigest()


def encoded(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def write_or_check(path: Path, payload: dict, check: bool) -> None:
    wanted = encoded(payload)
    if check:
        if not path.exists() or path.read_bytes() != wanted:
            raise SystemExit(f"REFUSED: generated artifact drift: {path.relative_to(ROOT)}")
        print(f"PASS {path.relative_to(ROOT)}")
        return
    path.write_bytes(wanted)
    print(path.relative_to(ROOT))


def claim_map() -> dict:
    generic = json.loads(GENERIC_CERT.read_text())
    if generic["result_id"] != "PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1":
        raise SystemExit("REFUSED: wrong terminal generic-l authority")
    return {
        "schema": "paper-draft-source-map-v1",
        "paper_id": "PAPER_14_PURE_WEYL_BLACK_HOLE_RADIATION",
        "result_id": "PAPER_14_PHASE3_EVANS_PREFIX_127_512_UPDATE_V9",
        "lifecycle_state": "DRAFT_ALLOWED",
        "source_baseline": SOURCE_BASELINE,
        "manuscript": str(PAPER.relative_to(ROOT)),
        "paper_sha256": digest(PAPER),
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "terminal_supersession_authority": {
            "result_id": generic["result_id"],
            "result_token": generic["result_token"],
            "certificate": str(GENERIC_CERT.relative_to(ROOT)),
            "certificate_sha256": digest(GENERIC_CERT),
            "receipt": str(GENERIC_RECEIPT.relative_to(ROOT)),
            "receipt_sha256": digest(GENERIC_RECEIPT),
            "report": str(GENERIC_REPORT.relative_to(ROOT)),
            "report_sha256": digest(GENERIC_REPORT),
            "correction_request": str(CORRECTION_REQUEST.relative_to(ROOT)),
            "correction_request_sha256": digest(CORRECTION_REQUEST),
        },
        "phase3_axial_authority": {
            "result_id": "PURE_WEYL_PHASE3_AXIAL_COMPLETE_RECONSTRUCTION_REPAIR",
            "source_commit": PHASE3_COMMIT,
            "certificate": str(PHASE3_CERT.relative_to(ROOT)),
            "certificate_sha256": digest(PHASE3_CERT),
            "receipt": str(PHASE3_RECEIPT.relative_to(ROOT)),
            "receipt_sha256": digest(PHASE3_RECEIPT),
            "report": str(PHASE3_REPORT.relative_to(ROOT)),
            "report_sha256": digest(PHASE3_REPORT),
            "atlas": str(PHASE3_ATLAS.relative_to(ROOT)),
            "atlas_sha256": digest(PHASE3_ATLAS),
        },
        "phase3_endpoint_flux_authority": {
            "result_id": "PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1",
            "content_commit": ENDPOINT_CONTENT_COMMIT,
            "lifecycle_commit": ENDPOINT_LIFECYCLE_COMMIT,
            "certificate": str(ENDPOINT_CERT.relative_to(ROOT)),
            "certificate_sha256": digest(ENDPOINT_CERT),
            "receipt": str(ENDPOINT_RECEIPT.relative_to(ROOT)),
            "receipt_sha256": digest(ENDPOINT_RECEIPT),
            "report": str(ENDPOINT_REPORT.relative_to(ROOT)),
            "report_sha256": digest(ENDPOINT_REPORT),
            "atlas": str(ENDPOINT_ATLAS.relative_to(ROOT)),
            "atlas_sha256": digest(ENDPOINT_ATLAS),
        },
        "phase3_outgoing_population_point_half_authority": {
            "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_POINT_HALF",
            "scope": "M=1, axial ell=2, omega=1/2 only",
            "certificate": str(OUTGOING_POINT_CERT.relative_to(ROOT)),
            "certificate_sha256": digest(OUTGOING_POINT_CERT),
            "receipt": str(OUTGOING_POINT_RECEIPT.relative_to(ROOT)),
            "receipt_sha256": digest(OUTGOING_POINT_RECEIPT),
            "report": str(OUTGOING_POINT_REPORT.relative_to(ROOT)),
            "report_sha256": digest(OUTGOING_POINT_REPORT),
            "does_not_establish": (
                "explicit Tplus entries, interval-wide outgoing rank, "
                "time-domain stability or a quantum claim"
            ),
        },
        "phase3_outgoing_population_cell_half_authority": {
            "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_CELL_HALF",
            "scope": (
                "M=1, axial ell=2, real omega in "
                "[0.49995,0.50005] only"
            ),
            "certificate": str(OUTGOING_CELL_CERT.relative_to(ROOT)),
            "certificate_sha256": digest(OUTGOING_CELL_CERT),
            "receipt": str(OUTGOING_CELL_RECEIPT.relative_to(ROOT)),
            "receipt_sha256": digest(OUTGOING_CELL_RECEIPT),
            "report": str(OUTGOING_CELL_REPORT.relative_to(ROOT)),
            "report_sha256": digest(OUTGOING_CELL_REPORT),
            "does_not_establish": (
                "absence or location of isolated positive-real reflection "
                "zeros, explicit Tplus entries, complete-pilot pointwise "
                "outgoing rank, full time-domain stability or a quantum claim"
            ),
        },
        "phase3_evans_boundary_prefix_authority": {
            "result_id": "PURE_WEYL_PHASE3_AXIAL_QNM_EVANS_BOUNDARY_PREFIX_127_512",
            "scope": (
                "projective scalar Evans contour prefix through 127/512 "
                "only; no closed contour or root count"
            ),
            "v7_certificate": str(EVANS_V7_CERT.relative_to(ROOT)),
            "v7_certificate_sha256": digest(EVANS_V7_CERT),
            "v7b_certificate": str(EVANS_V7B_CERT.relative_to(ROOT)),
            "v7b_certificate_sha256": digest(EVANS_V7B_CERT),
            "v8_certificate": str(EVANS_V8_CERT.relative_to(ROOT)),
            "v8_certificate_sha256": digest(EVANS_V8_CERT),
            "certificate": str(EVANS_V9_CERT.relative_to(ROOT)),
            "certificate_sha256": digest(EVANS_V9_CERT),
            "receipt": str(EVANS_V9_RECEIPT.relative_to(ROOT)),
            "receipt_sha256": digest(EVANS_V9_RECEIPT),
            "report": str(EVANS_V9_REPORT.relative_to(ROOT)),
            "report_sha256": digest(EVANS_V9_REPORT),
            "does_not_establish": (
                "complete boundary nonvanishing, argument-principle root "
                "count, QNM location, Smith selector or EP2"
            ),
        },
        "phase3_global_connection_shortfall": {
            "result_id": "PURE_WEYL_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5",
            "lifecycle": "NUMERIC-ENCLOSURE",
            "disposition": "SHORTFALL",
            "content_commit": GLOBAL_V5_CONTENT_COMMIT,
            "lifecycle_commit": GLOBAL_V5_LIFECYCLE_COMMIT,
            "certificate": GLOBAL_V5_CERT,
            "certificate_sha256": committed_digest(GLOBAL_V5_CONTENT_COMMIT, GLOBAL_V5_CERT),
            "report": GLOBAL_V5_REPORT,
            "report_sha256": committed_digest(GLOBAL_V5_CONTENT_COMMIT, GLOBAL_V5_REPORT),
            "atlas": GLOBAL_V5_ATLAS,
            "atlas_sha256": committed_digest(GLOBAL_V5_CONTENT_COMMIT, GLOBAL_V5_ATLAS),
            "boundary": "The first-cell diagonal ranks and local lower solves close, but cumulative correlated lower transport does not. This is not a scientific obstruction or a global connection theorem.",
        },
        "certified_scope": {
            "static_laurent_family": True,
            "normalized_static_first_law": True,
            "linear_spherical_gauge_audit": True,
            "ricci_flat_ricci_bach_composition": True,
            "axial_l2_exact_sequence_onto_realized_ricci_image": True,
            "canonical_einstein_additional_direct_sum": False,
            "axial_horizon_reach_for_ricci_carrier": True,
            "full_metric_quotient_horizon_dimension": False,
            "axial_einstein_self_pairing_exactly_null": True,
            "axial_mixed_and_additional_pairing_controlled_fixtures": True,
            "axial_mixed_pairing_symbolic_or_interval_certified": True,
            "axial_tested_endpoint_nonselection": True,
            "axial_local_causal_truncation_no_go": False,
            "polar_ricci_bach_composition": True,
            "polar_causal_chain": True,
            "polar_einstein_two_dimensional_reduction": True,
            "polar_carrier_horizon_reach_modulo_conformal_gauge": True,
            "polar_einstein_self_pairing_exactly_null": True,
            "polar_conformal_direction_offshell_degeneracy": True,
            "polar_realized_image_closes_on_analytic_carrier_space": True,
            "polar_mixed_pairing_controlled_fixtures": True,
            "polar_tested_endpoint_nonselection": True,
            "carrier_self_pairing_invariant_sign_theory": False,
            "horizon_monodromy_temperature_reduced_mode": True,
            "omega_zero_static_sector_classified": True,
            "local_cauchy_truncation_selects_einstein_axial": True,
            "local_cauchy_truncation_polar_modulo_conformal_gauge": True,
            "axial_complex_frequency_meromorphic_continuation_exact_singular_set": True,
            "polar_complex_frequency_continuation_activated": False,
            "generic_l_axial_einstein_radial_finiteness": False,
            "generic_l_axial_corrected_x0_non_einstein_finite": False,
            "axial_l2_complete_six_dimensional_endpoint_module": True,
            "axial_l2_constraint_propagation_c_prime_minus_2c_over_r": True,
            "axial_l2_repaired_x0_fixed_representative_finite": True,
            "axial_l2_rate_zero_einstein_shear_finite": True,
            "axial_l2_oscillatory_einstein_shear_divergent": True,
            "axial_l2_unrestricted_representative_independence": False,
            "axial_l2_endpoint_trace_dimensions_three_three": True,
            "axial_l2_endpoint_flux_grams_action_derived": True,
            "axial_l2_endpoint_flux_grams_rank_three": True,
            "axial_l2_endpoint_flux_grams_radical_zero": True,
            "axial_l2_endpoint_flux_grams_inertia_one_two_zero_alpha_positive": True,
            "axial_l2_endpoint_flux_frequency_wall_absent_on_pilot": True,
            "axial_l2_endpoint_trace_limit_interchange": True,
            "axial_l2_endpoint_uniform_auxiliary_l2_bounds": True,
            "axial_l2_endpoint_scoped_trace_local_improvement_invariance": True,
            "axial_l2_endpoint_unrestricted_improvement_invariance": False,
            "axial_l2_endpoint_direction_globally_populated": False,
            "axial_incoming_full_trace_globally_populated_all_positive_frequencies": True,
            "axial_outgoing_full_trace_globally_populated_at_omega_half": True,
            "axial_outgoing_pullback_nonzero_inertia_one_two_zero_at_omega_half": True,
            "axial_scalar_spin_one_and_spin_two_reflection_nonzero_at_omega_half": True,
            "axial_outgoing_full_trace_globally_populated_on_cell_half": True,
            "axial_outgoing_pullback_nonzero_inertia_one_two_zero_on_cell_half": True,
            "axial_scalar_spin_one_and_spin_two_reflection_nonzero_on_cell_half": True,
            "axial_outgoing_generic_population_off_locally_finite_set": True,
            "axial_outgoing_cell_half_L2_multiplier_isomorphism": True,
            "axial_outgoing_compact_positive_band_dense_range": True,
            "axial_positive_real_reflection_zero_set_empty": False,
            "axial_outgoing_full_positive_axis_uniform_inverse_bound": False,
            "axial_qnm_projective_boundary_prefix_127_512": True,
            "axial_qnm_complete_closed_contour_nonzero": False,
            "axial_qnm_argument_principle_root_count": False,
            "axial_l2_endpoint_flux_positive_energy": False,
            "axial_l2_endpoint_flux_cpt_or_stability": False,
            "axial_global_connection_v5_method_shortfall_recorded": True,
            "legacy_axial_x0_derivative_defect": True,
            "polar_mixed_finite_line": True,
            "polar_q21_exceptional_wall": True,
            "polar_q21_legacy_fixture_nonzero": True,
            "formal_radial_einstein_only_selection": False,
            "finite_flux_class_fixture_einstein_selected": False,
            "polar_norm_selection_fixture_einstein_selected": False,
            "polar_composed_lift_power_enhanced_single_log": False,
            "composed_metric_log_tails": False,
            "axial_symbolic_frequency_finite_flux_einstein_selected": False,
            "invariant_einstein_extra_pairing_rank_signature": False,
            "one_ended_endpoint_selection_assembled": False,
            "additional_branch_outgoing_condition_logtail_obstructed": False,
            "global_horizon_to_infinity_matching": False,
            "asymptotic_tetrad_falloff_audit": False,
            "asymptotic_phase_space_charge_algebra": False,
            "complex_frequency_stability": False,
            "nonlinear_black_hole_theorem": False,
            "quantum_claim": False,
            "hawking_state_or_flux_balance": False,
            "numerical_validation_protocol_specified": True,
        },
        "known_source_scope_corrections": [
            {
                "source": "black_hole_programme/certificates/BH0_STATIC_SPHERICAL_BACKGROUND.json",
                "issue": "The legacy phrase Einstein iff gamma=0 applies only to the Mannheim-Kazanas sheet through w=1.",
                "manuscript_disposition": "On the complete Laurent locus the paper requires gamma=0 and w=1.",
            },
            {
                "source": "black_hole_programme/certificates/BH2A_CAUSAL_DISPOSITION.json",
                "issue": "The former causal-unavoidability interpretation exceeded its endpoint data.",
                "manuscript_disposition": "Only scoped endpoint nonselection is retained; local Cauchy selection is explicit.",
            },
            {
                "source": "black_hole_programme/certificates/BH2C_FLUX_CLASS.json",
                "issue": "The legacy axial X0 reconstruction omitted 2 r c'(r)/(r-2M).",
                "manuscript_disposition": "The Einstein-only radial-selection and X0 log-tail claims are superseded; the complete ell=2 all-row module is now the axial authority.",
            },
            {
                "source": "black_hole_programme/phase2/general_l_axial_selection/certificate.json",
                "issue": "The Phase-2 generic-angular metric lift omitted the independent v-phi Ricci row; its legacy E0 is not a complete Einstein solution.",
                "manuscript_disposition": "Only the Phase-3 ell=2 complete six-dimensional module and its scoped current audit are retained; generic-ell complete axial disposition is open.",
            },
            {
                "source": "black_hole_programme/certificates/BH2C_POLAR_FLUX_CLASS.json",
                "issue": "The shallow polar source-zero direction did not satisfy all seven Ricci rows.",
                "manuscript_disposition": "The parity-complete norm-selection claim is superseded by the restriction-stable mixed finite line and Q21 wall.",
            },
            {
                "source": "black_hole_programme/certificates/BH_ENDPOINT_NONSELECTION_ASSEMBLY.json",
                "issue": "Its compound infinity-selection half depended on superseded axial and polar fixtures.",
                "manuscript_disposition": "Independent horizon and leading-symbol statements are retained; the infinity-selection assembly is withdrawn.",
            },
            {
                "source": "black_hole_programme/certificates/BH3_EXTERIOR_BVP_WELLPOSEDNESS_GATE.json",
                "issue": "Its additional-log-tail boundary disposition depended on the defective reconstruction.",
                "manuscript_disposition": "Only the separately certified meromorphic axial continuation is retained; no exterior BVP theorem is claimed.",
            },
        ],
        "superseded_active_claims": [
            "axial or parity-complete Einstein-only finite radial selection",
            "legacy axial X0 logarithmic tail and divergent current",
            "generic-l complete axial X0 finite counterexample",
            "unrestricted representative independence under arbitrary Einstein shears",
            "legacy polar power-enhanced single-log lift and divergent composed-current table",
            "additional-branch outgoing-condition obstruction inferred from those tails",
        ],
        "sources": [
            {"path": path, "git_blob": git_blob(path)} for path in ACTIVE_SOURCES
        ],
        "next_gate": (
            "COMPLETE_PILOT_SCALAR_REFLECTION_NONVANISHING_OR_TYPED_"
            "PROJECTIVE_LOG_AMPLITUDE_TPLUS_AUDIT"
        ),
    }


def coverage(claim_payload: dict) -> dict:
    result_id = "sf:coverage/result/PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1"
    phase3_result_id = "sf:coverage/result/PURE_WEYL_PHASE3_AXIAL_COMPLETE_RECONSTRUCTION_REPAIR"
    endpoint_result_id = "sf:coverage/result/PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1"
    global_v5_result_id = "sf:coverage/result/PURE_WEYL_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5"
    outgoing_point_result_id = (
        "sf:coverage/result/"
        "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_POINT_HALF"
    )
    outgoing_cell_result_id = (
        "sf:coverage/result/"
        "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_CELL_HALF"
    )
    evans_prefix_result_id = (
        "sf:coverage/result/"
        "PURE_WEYL_PHASE3_AXIAL_QNM_EVANS_BOUNDARY_PREFIX_127_512"
    )
    paper_id = "paper:14-pure-weyl-black-hole-radiation"
    claim_id = f"{paper_id}/claim/phase2_generic_l_parity_disposition_v1"
    phase3_claim_id = f"{paper_id}/claim/phase3_axial_complete_reconstruction_repair"
    edge_id = "sf:coverage/edge/PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1/paper-14/v2"
    phase3_edge_id = "sf:coverage/edge/PURE_WEYL_PHASE3_AXIAL_COMPLETE_RECONSTRUCTION_REPAIR/paper-14/v1"
    endpoint_claim_id = f"{paper_id}/claim/phase3_axial_null_endpoint_flux_grams_v1"
    endpoint_edge_id = "sf:coverage/edge/PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1/paper-14/v1"
    global_v5_claim_id = f"{paper_id}/claim/phase3_axial_global_connection_matrix_v5_shortfall"
    global_v5_edge_id = "sf:coverage/edge/PURE_WEYL_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5/paper-14/v1"
    outgoing_point_claim_id = (
        f"{paper_id}/claim/phase3_axial_outgoing_population_point_half"
    )
    outgoing_point_edge_id = (
        "sf:coverage/edge/"
        "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_POINT_HALF/paper-14/v1"
    )
    outgoing_cell_claim_id = (
        f"{paper_id}/claim/phase3_axial_outgoing_population_cell_half"
    )
    outgoing_cell_edge_id = (
        "sf:coverage/edge/"
        "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_CELL_HALF/paper-14/v1"
    )
    evans_prefix_claim_id = (
        f"{paper_id}/claim/phase3_axial_qnm_evans_boundary_prefix_127_512"
    )
    evans_prefix_edge_id = (
        "sf:coverage/edge/"
        "PURE_WEYL_PHASE3_AXIAL_QNM_EVANS_BOUNDARY_PREFIX_127_512/"
        "paper-14/v1"
    )
    nodes = [
        {
            "kind": "materiality",
            "id": "sf:coverage/materiality/PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1/v1",
            "body": {
                "result_id": result_id,
                "materiality": "HEADLINE",
                "by": "Asger Alstrup Palm",
                "stamp": "2026-07-22",
                "version": 1,
                "rationale": "Terminal Phase-2 polar Q21 filtration retained after the axial half was superseded by the complete Phase-3 reconstruction.",
                "native": {"source_schema": "materiality-v0"},
            },
        },
        {
            "kind": "result",
            "id": result_id,
            "title": "PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1",
            "body": {
                "result_id": "PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1",
                "lifecycle": "CLASSIFIED",
                "boundary": "Generic-angular polar formal filtration only; the axial half is superseded by the Phase-3 all-row ell=2 repair. No global theorem.",
                "native": {
                    "source_kind": "phase2-terminal-certificate",
                    "certificate": str(GENERIC_CERT.relative_to(ROOT)),
                    "certificate_sha256": digest(GENERIC_CERT),
                },
            },
            "edges": [],
        },
        {
            "kind": "paper_claim",
            "id": claim_id,
            "body": {
                "paper": paper_id,
                "material": True,
                "asserts_lifecycle": "CLASSIFIED",
                "boundary": "Generic-angular polar formal filtration; global matching and asymptotic phase space remain open.",
                "cites": [result_id],
            },
        },
        {
            "kind": "result_paper_edge",
            "id": edge_id,
            "body": {
                "from": result_id,
                "to": paper_id,
                "claim": claim_id,
                "edge_kind": "SUPPORTING_POLAR_THEOREM",
                "stale": False,
                "version": 2,
                "stamp": "2026-07-22",
                "native": {"source_schema": "result-paper-edge-v0"},
            },
        },
        {
            "kind": "result",
            "id": phase3_result_id,
            "title": "PURE_WEYL_PHASE3_AXIAL_COMPLETE_RECONSTRUCTION_REPAIR",
            "body": {
                "result_id": "PURE_WEYL_PHASE3_AXIAL_COMPLETE_RECONSTRUCTION_REPAIR",
                "lifecycle": "CLASSIFIED",
                "boundary": "Complete axial ell=2 formal endpoint module on real omega in [1/2,3/4]; no convergence, global matching, scattering, stability, or CPT theorem.",
                "native": {
                    "source_kind": "phase3-terminal-certificate",
                    "certificate": str(PHASE3_CERT.relative_to(ROOT)),
                    "certificate_sha256": digest(PHASE3_CERT),
                },
            },
            "edges": [],
        },
        {
            "kind": "paper_claim",
            "id": phase3_claim_id,
            "body": {
                "paper": paper_id,
                "material": True,
                "asserts_lifecycle": "CLASSIFIED",
                "boundary": "Six-dimensional complete axial ell=2 formal module; repaired X0 finite only in the fixed/rate-zero class and divergent against oscillatory Einstein shears.",
                "cites": [phase3_result_id],
            },
        },
        {
            "kind": "result_paper_edge",
            "id": phase3_edge_id,
            "body": {
                "from": phase3_result_id,
                "to": paper_id,
                "claim": phase3_claim_id,
                "edge_kind": "PRIMARY_THEOREM_CORRECTION",
                "stale": False,
                "version": 1,
                "stamp": "2026-07-23",
                "native": {"source_schema": "result-paper-edge-v0"},
            },
        },
        {
            "kind": "materiality",
            "id": "sf:coverage/materiality/PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1/v1",
            "body": {
                "result_id": endpoint_result_id,
                "materiality": "HEADLINE",
                "by": "Asger Alstrup Palm",
                "stamp": "2026-07-23",
                "version": 1,
                "rationale": "First exact action-derived wave-packet flux forms on the axial null-endpoint trace spaces; global population remains open.",
                "native": {"source_schema": "materiality-v0"},
            },
        },
        {
            "kind": "result",
            "id": endpoint_result_id,
            "title": "PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1",
            "body": {
                "result_id": "PURE_WEYL_PHASE3_AXIAL_NULL_ENDPOINT_FLUX_GRAMS_V1",
                "lifecycle": "CLASSIFIED",
                "boundary": "Strict pure Weyl, M=1, axial ell=2, omega in [1/2,3/4]: exact three-dimensional L2 traces at both null ends with rank-three, radical-free flux Grams of inertia (1,2,0), explicit uniform auxiliary-L2 bounds, and scoped trace-local improvement invariance for alpha_W>0. No global population, unrestricted radial/corner improvement invariance, scattering, CPT or stability theorem.",
                "native": {
                    "source_kind": "phase3-terminal-certificate",
                    "certificate": str(ENDPOINT_CERT.relative_to(ROOT)),
                    "certificate_sha256": digest(ENDPOINT_CERT),
                    "content_commit": ENDPOINT_CONTENT_COMMIT,
                    "lifecycle_commit": ENDPOINT_LIFECYCLE_COMMIT,
                },
            },
            "edges": [],
        },
        {
            "kind": "paper_claim",
            "id": endpoint_claim_id,
            "body": {
                "paper": paper_id,
                "material": True,
                "asserts_lifecycle": "CLASSIFIED",
                "boundary": "Exact endpoint wave-packet flux only; no endpoint direction is proved to be populated by horizon-regular data.",
                "cites": [endpoint_result_id],
            },
        },
        {
            "kind": "result_paper_edge",
            "id": endpoint_edge_id,
            "body": {
                "from": endpoint_result_id,
                "to": paper_id,
                "claim": endpoint_claim_id,
                "edge_kind": "PRIMARY_ENDPOINT_THEOREM",
                "stale": False,
                "version": 1,
                "stamp": "2026-07-23",
                "native": {"source_schema": "result-paper-edge-v0"},
            },
        },
        {
            "kind": "result",
            "id": global_v5_result_id,
            "title": "PURE_WEYL_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5",
            "body": {
                "result_id": "PURE_WEYL_PHASE3_AXIAL_GLOBAL_CONNECTION_MATRIX_V5",
                "lifecycle": "NUMERIC-ENCLOSURE",
                "disposition": "SHORTFALL",
                "boundary": "Validated first-cell method shortfall: diagonal ranks and local lower solves close, but correlated cumulative lower transport does not. No scientific nonexistence or global connection claim.",
                "native": {
                    "source_kind": "phase3-terminal-shortfall",
                    "certificate": GLOBAL_V5_CERT,
                    "certificate_sha256": committed_digest(GLOBAL_V5_CONTENT_COMMIT, GLOBAL_V5_CERT),
                    "content_commit": GLOBAL_V5_CONTENT_COMMIT,
                    "lifecycle_commit": GLOBAL_V5_LIFECYCLE_COMMIT,
                },
            },
            "edges": [],
        },
        {
            "kind": "paper_claim",
            "id": global_v5_claim_id,
            "body": {
                "paper": paper_id,
                "material": True,
                "asserts_lifecycle": "NUMERIC-ENCLOSURE",
                "boundary": "Method/substrate SHORTFALL only; not evidence for or against existence of the Bach connection.",
                "cites": [global_v5_result_id],
            },
        },
        {
            "kind": "result_paper_edge",
            "id": global_v5_edge_id,
            "body": {
                "from": global_v5_result_id,
                "to": paper_id,
                "claim": global_v5_claim_id,
                "edge_kind": "METHOD_SHORTFALL",
                "stale": False,
                "version": 1,
                "stamp": "2026-07-23",
                "native": {"source_schema": "result-paper-edge-v0"},
            },
        },
        {
            "kind": "materiality",
            "id": (
                "sf:coverage/materiality/"
                "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_POINT_HALF/v1"
            ),
            "body": {
                "result_id": outgoing_point_result_id,
                "materiality": "HEADLINE",
                "by": "Asger Alstrup Palm",
                "stamp": "2026-07-24",
                "version": 1,
                "rationale": (
                    "First certified frequency at which all three outgoing "
                    "axial trace directions are globally populated."
                ),
                "native": {"source_schema": "materiality-v0"},
            },
        },
        {
            "kind": "result",
            "id": outgoing_point_result_id,
            "title": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_POINT_HALF",
            "body": {
                "result_id": (
                    "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_POINT_HALF"
                ),
                "lifecycle": "COEFFICIENT_COMPUTED",
                "boundary": (
                    "Strict pure Weyl, M=1, axial ell=2, omega=1/2 only: "
                    "both scalar outgoing factors are nonzero; boundary "
                    "devissage proves Tplus invertible and the outgoing "
                    "pullback nondegenerate with inertia (1,2,0). No explicit "
                    "Tplus entries or interval-wide rank theorem."
                ),
                "native": {
                    "source_kind": "phase3-point-certificate",
                    "certificate": str(OUTGOING_POINT_CERT.relative_to(ROOT)),
                    "certificate_sha256": digest(OUTGOING_POINT_CERT),
                    "receipt": str(OUTGOING_POINT_RECEIPT.relative_to(ROOT)),
                    "receipt_sha256": digest(OUTGOING_POINT_RECEIPT),
                },
            },
            "edges": [],
        },
        {
            "kind": "paper_claim",
            "id": outgoing_point_claim_id,
            "body": {
                "paper": paper_id,
                "material": True,
                "asserts_lifecycle": "COEFFICIENT_COMPUTED",
                "boundary": (
                    "Pointwise full outgoing population at omega=1/2; "
                    "explicit amplitudes and interval-wide rank remain open."
                ),
                "cites": [outgoing_point_result_id],
            },
        },
        {
            "kind": "result_paper_edge",
            "id": outgoing_point_edge_id,
            "body": {
                "from": outgoing_point_result_id,
                "to": paper_id,
                "claim": outgoing_point_claim_id,
                "edge_kind": "PRIMARY_POINTWISE_SCATTERING_THEOREM",
                "stale": False,
                "version": 1,
                "stamp": "2026-07-24",
                "native": {"source_schema": "result-paper-edge-v0"},
            },
        },
        {
            "kind": "materiality",
            "id": (
                "sf:coverage/materiality/"
                "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_CELL_HALF/v1"
            ),
            "body": {
                "result_id": outgoing_cell_result_id,
                "materiality": "HEADLINE",
                "by": "Asger Alstrup Palm",
                "stamp": "2026-07-24",
                "version": 1,
                "rationale": (
                    "First certified nonzero real-frequency interval on "
                    "which all three outgoing axial trace directions are "
                    "globally populated; holomorphy then gives generic "
                    "positive-real population and compact-band dense range."
                ),
                "native": {"source_schema": "materiality-v0"},
            },
        },
        {
            "kind": "result",
            "id": outgoing_cell_result_id,
            "title": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_CELL_HALF",
            "body": {
                "result_id": (
                    "PURE_WEYL_PHASE3_AXIAL_OUTGOING_POPULATION_CELL_HALF"
                ),
                "lifecycle": "COEFFICIENT_COMPUTED",
                "boundary": (
                    "Strict pure Weyl, M=1, axial ell=2, real omega in "
                    "[0.49995,0.50005]: both scalar outgoing factors are "
                    "uniformly nonzero; boundary devissage proves Tplus "
                    "invertible and the outgoing pullback nondegenerate "
                    "with inertia (1,2,0). Holomorphy gives invertibility "
                    "off a locally finite positive-real exceptional set, "
                    "a bounded L2 multiplier isomorphism on the cell and "
                    "dense range on every compact positive band. No "
                    "absence theorem for reflection zeros, explicit Tplus "
                    "entries or complete-pilot pointwise rank theorem."
                ),
                "native": {
                    "source_kind": "phase3-real-cell-certificate",
                    "certificate": str(OUTGOING_CELL_CERT.relative_to(ROOT)),
                    "certificate_sha256": digest(OUTGOING_CELL_CERT),
                    "receipt": str(OUTGOING_CELL_RECEIPT.relative_to(ROOT)),
                    "receipt_sha256": digest(OUTGOING_CELL_RECEIPT),
                },
            },
            "edges": [],
        },
        {
            "kind": "paper_claim",
            "id": outgoing_cell_claim_id,
            "body": {
                "paper": paper_id,
                "material": True,
                "asserts_lifecycle": "COEFFICIENT_COMPUTED",
                "boundary": (
                    "Full outgoing population and bounded L2 multiplier "
                    "isomorphism on [0.49995,0.50005]; generic "
                    "positive-real population and compact-band dense "
                    "range; isolated reflection-zero locations, explicit "
                    "amplitudes and complete-pilot pointwise rank remain open."
                ),
                "cites": [outgoing_cell_result_id],
            },
        },
        {
            "kind": "result_paper_edge",
            "id": outgoing_cell_edge_id,
            "body": {
                "from": outgoing_cell_result_id,
                "to": paper_id,
                "claim": outgoing_cell_claim_id,
                "edge_kind": "PRIMARY_REAL_CELL_SCATTERING_THEOREM",
                "stale": False,
                "version": 1,
                "stamp": "2026-07-24",
                "native": {"source_schema": "result-paper-edge-v0"},
            },
        },
        {
            "kind": "materiality",
            "id": (
                "sf:coverage/materiality/"
                "PURE_WEYL_PHASE3_AXIAL_QNM_EVANS_BOUNDARY_PREFIX_127_512/v1"
            ),
            "body": {
                "result_id": evans_prefix_result_id,
                "materiality": "SUPPORTING",
                "by": "Asger Alstrup Palm",
                "stamp": "2026-07-24",
                "version": 1,
                "rationale": (
                    "Extends the rigorously zero-free projective Evans "
                    "boundary prefix to 127/512 while retaining fail-closed "
                    "root, Smith and EP2 gates."
                ),
                "native": {"source_schema": "materiality-v0"},
            },
        },
        {
            "kind": "result",
            "id": evans_prefix_result_id,
            "title": (
                "PURE_WEYL_PHASE3_AXIAL_QNM_EVANS_BOUNDARY_PREFIX_127_512"
            ),
            "body": {
                "result_id": (
                    "PURE_WEYL_PHASE3_AXIAL_QNM_EVANS_BOUNDARY_PREFIX_127_512"
                ),
                "lifecycle": "CLASSIFIED",
                "boundary": (
                    "Projective scalar Evans boundary is certified nonzero "
                    "only on the exact contiguous prefix [0,127/512]. The "
                    "next gap starts at 254/1024. No closed-contour, "
                    "argument-principle, root-count, QNM, Smith or EP2 claim."
                ),
                "native": {
                    "source_kind": "phase3-evans-prefix-certificate",
                    "certificate": str(EVANS_V9_CERT.relative_to(ROOT)),
                    "certificate_sha256": digest(EVANS_V9_CERT),
                    "receipt": str(EVANS_V9_RECEIPT.relative_to(ROOT)),
                    "receipt_sha256": digest(EVANS_V9_RECEIPT),
                },
            },
            "edges": [],
        },
        {
            "kind": "paper_claim",
            "id": evans_prefix_claim_id,
            "body": {
                "paper": paper_id,
                "material": True,
                "asserts_lifecycle": "CLASSIFIED",
                "boundary": (
                    "Zero-free Evans boundary prefix through 127/512 only; "
                    "the remaining contour and every root/Smith gate remain "
                    "open."
                ),
                "cites": [evans_prefix_result_id],
            },
        },
        {
            "kind": "result_paper_edge",
            "id": evans_prefix_edge_id,
            "body": {
                "from": evans_prefix_result_id,
                "to": paper_id,
                "claim": evans_prefix_claim_id,
                "edge_kind": "SUPPORTING_EVANS_BOUNDARY_PREFIX",
                "stale": False,
                "version": 1,
                "stamp": "2026-07-24",
                "native": {"source_schema": "result-paper-edge-v0"},
            },
        },
    ]
    for old_edge in SUPERSEDED_EDGES:
        old_name = old_edge.rsplit("/", 3)[-3]
        nodes.append(
            {
                "kind": "coverage_correction",
                "id": f"sf:coverage/correction/{old_name}/paper-14/v2",
                "body": {
                    "target_edge": old_edge,
                    "action": "MARK_STALE_BY_APPEND_ONLY_SUPERSESSION",
                    "superseded_by": phase3_edge_id,
                    "reason": "The complete all-row ell=2 reconstruction supersedes the old axial infinity-selection and representative-independence readings; the separate polar filtration remains supporting evidence.",
                    "stamp": "2026-07-23",
                    "version": 3,
                },
            }
        )
    return {
        "ir": "science-forge-ir-v0",
        "schema": "paper14-phase3-evans-prefix-127-512-overlay-v9",
        "append_only_parent": str(PARENT_COVERAGE.relative_to(ROOT)),
        "append_only_parent_sha256": digest(PARENT_COVERAGE),
        "claim_map": str(OUTPUT.relative_to(ROOT)),
        "claim_map_sha256": hashlib.sha256(encoded(claim_payload)).hexdigest(),
        "nodes": sorted(nodes, key=lambda node: (node["kind"], node["id"])),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    claims = claim_map()
    write_or_check(OUTPUT, claims, args.check)
    write_or_check(COVERAGE_OUTPUT, coverage(claims), args.check)


if __name__ == "__main__":
    main()
