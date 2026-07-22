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
        "result_id": "PAPER_14_CORRECTED_X0_SUPERSESSION_V1",
        "lifecycle_state": "DRAFT_ALLOWED",
        "source_baseline": SOURCE_BASELINE,
        "manuscript": str(PAPER.relative_to(ROOT)),
        "paper_sha256": digest(PAPER),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
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
            "generic_l_axial_einstein_radial_finiteness": True,
            "generic_l_axial_corrected_x0_non_einstein_finite": True,
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
                "manuscript_disposition": "The Einstein-only radial-selection and X0 log-tail claims are superseded by the corrected generic-l counterexample.",
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
            "legacy polar power-enhanced single-log lift and divergent composed-current table",
            "additional-branch outgoing-condition obstruction inferred from those tails",
        ],
        "sources": [
            {"path": path, "git_blob": git_blob(path)} for path in ACTIVE_SOURCES
        ],
        "next_gate": "GLOBAL_HORIZON_TO_INFINITY_CONNECTION_PLUS_DIFFERENTIABLE_ASYMPTOTIC_PHASE_SPACE",
    }


def coverage(claim_payload: dict) -> dict:
    result_id = "sf:coverage/result/PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1"
    paper_id = "paper:14-pure-weyl-black-hole-radiation"
    claim_id = f"{paper_id}/claim/phase2_generic_l_parity_disposition_v1"
    edge_id = "sf:coverage/edge/PURE_WEYL_PHASE2_GENERIC_L_PARITY_DISPOSITION_V1/paper-14/v2"
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
                "rationale": "Terminal correction of Paper 14's formal-infinity disposition after the generic-l axial counterexample and polar Q21 filtration.",
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
                "boundary": "Formal radial modes in a fixed Lee-Wald representative; no horizon-to-infinity phase space, scattering, stability, particles, positivity, or quantum theorem.",
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
                "boundary": "Formal radial modes in a fixed Lee-Wald representative; global matching and asymptotic phase space remain open.",
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
                "edge_kind": "PRIMARY_THEOREM_CORRECTION",
                "stale": False,
                "version": 2,
                "stamp": "2026-07-22",
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
                    "superseded_by": edge_id,
                    "reason": "The corrected axial X0 lift and restriction-stable polar module invalidate the old Einstein-only infinity-selection reading while preserving independent horizon and Einstein-current components.",
                    "stamp": "2026-07-22",
                    "version": 2,
                },
            }
        )
    return {
        "ir": "science-forge-ir-v0",
        "schema": "paper14-corrected-x0-supersession-overlay-v1",
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
