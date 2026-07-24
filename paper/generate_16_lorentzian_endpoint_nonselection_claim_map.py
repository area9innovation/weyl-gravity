#!/usr/bin/env python3
"""Generate Paper 16's claim map and append-only coverage overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/16-lorentzian-endpoint-nonselection-pure-weyl.tex"
OUTPUT = ROOT / "paper/16-lorentzian-endpoint-nonselection-pure-weyl-claim-map.json"
COVERAGE = ROOT / "planning/paper-coverage/phase4-paper16-endpoint-nonselection-overlay-2026-07-24.json"

AUTHORITIES = {
    "axial_operator": "black_hole_programme/certificates/BH2A_AXIAL_OPERATOR.json",
    "factor_filtration": "black_hole_programme/phase3/axial_rw_lx_triangular_preflight/certificate.json",
    "endpoint_flux": "black_hole_programme/phase3/axial_null_flux_gram/certificate.json",
    "incoming_global": "black_hole_programme/phase3/axial_incoming_extended_domain_audit/certificate.json",
    "no_growth": "black_hole_programme/phase3/axial_boundary_devissage_no_growth/certificate.json",
    "outgoing_cell": "black_hole_programme/phase3/axial_outgoing_population_cell_half_v1/certificate.json",
    "finite_flux": "black_hole_programme/phase3/axial_global_finite_flux_channel_classification_v3/certificate.json",
    "threshold": "black_hole_programme/phase4/axial_threshold_exact_structure_v1/certificate.json",
    "all_ell_threshold": "black_hole_programme/phase4/axial_all_ell_threshold_structure_v1/certificate.json",
    "universal_hessian_intertwiner": "black_hole_programme/phase4/axial_universal_hessian_intertwiner_v1/certificate.json",
    "covariant_einstein_maxwell_carrier": "black_hole_programme/phase4/covariant_einstein_maxwell_carrier_v1/certificate.json",
    "weyl_euler_current_transgression": "black_hole_programme/phase4/weyl_euler_current_transgression_v1/certificate.json",
    "second_order_parent_flux": "black_hole_programme/phase4/second_order_parent_flux_v1/certificate.json",
    "parent_resolvent_krein_obstructions": "black_hole_programme/phase4/parent_resolvent_krein_obstructions_v1/certificate.json",
    "static_normalized_control": "black_hole_programme/certificates/BH1A_NORMALIZED_GENERATOR.json",
    "qnm_winding": "black_hole_programme/phase3/axial_qnm_projective_evans_contour_completion/full_contour_winding_v1/certificate.json",
    "qnm_selector": "black_hole_programme/phase3/axial_qnm_projective_evans_contour_completion/local_selector_v1/certificate.json",
    "qnm_spin_one_unit": "black_hole_programme/phase3/axial_qnm_spin_one_local_unit_v1/certificate.json",
    "polar_reach": "black_hole_programme/certificates/BH2B_POLAR_REACH.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def authority_map() -> dict:
    result = {}
    for name, relative in AUTHORITIES.items():
        path = ROOT / relative
        payload = json.loads(path.read_text())
        result[name] = {
            "path": relative,
            "sha256": digest(path),
            "result_id": payload.get("result_id"),
            "status": payload.get("status"),
            "result_token": payload.get("result_token"),
        }
    return result


def claim_map() -> dict:
    return {
        "schema": "paper-draft-source-map-v1",
        "paper_id": "PAPER_16_LORENTZIAN_ENDPOINT_NONSELECTION",
        "result_id": "PAPER16_FOCUSED_ENDPOINT_NONSELECTION_WITH_CONNECTION_EP2",
        "lifecycle_state": "DRAFT_ALLOWED",
        "manuscript": str(PAPER.relative_to(ROOT)),
        "paper_sha256": digest(PAPER),
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "authorities": authority_map(),
        "certified_scope": {
            "universal_ricci_flat_bulk_hessian_factorization": True,
            "schouten_einstein_carrier_factorization": True,
            "target_gauge_maxwell_equation_and_wrong_sign_action": True,
            "second_order_parent_action_and_factorized_current": True,
            "parent_block_inverse_exact": True,
            "rank_one_double_coefficient_algebra_exact": True,
            "canonical_source_target_null_lift": True,
            "einstein_wave_packet_total_isotropy": True,
            "einstein_subspace_isotropic_but_nonradical": True,
            "nondegenerate_einstein_containing_restriction_indefinite": True,
            "axial_l2_factor_filtration": True,
            "no_rational_spin_one_spin_two_intertwiner_positive_real": True,
            "no_generic_rational_branch_resolving_C": True,
            "simple_self_extension_involution_lemma_exact": True,
            "no_uniformly_positive_einstein_containing_subspace": True,
            "cotangent_type_endpoint_duality_exact": True,
            "incoming_gram_inertia_1_2_0_all_positive_real": True,
            "Tminus_invertible_all_positive_real": True,
            "outgoing_population_on_declared_cell": True,
            "generic_outgoing_population_off_discrete_set": True,
            "band_limited_pseudo_isometry": True,
            "no_growing_separated_axial_mode": True,
            "exact_scalar_threshold_nonresonance": True,
            "all_ell_spin_one_spin_two_threshold_nonresonance": True,
            "one_connection_level_smith_0_0_2": True,
            "qnm_divisor_count_2N2_plus_N1": True,
            "polar_local_horizon_nonselection": True,
        },
        "fail_closed_scope": {
            "literal_endpoint_current_free_of_euler_corner_terms": False,
            "monochromatic_einstein_current_pointwise_zero": False,
            "unconditional_endpoint_packet_limit_interchange": False,
            "mixed_einstein_additional_pairing_euler_exact": False,
            "absence_of_nonlocal_spin_intertwiners": False,
            "mannheim_dynamical_C_constructed_or_excluded": False,
            "generic_rw_module_simplicity": False,
            "only_plus_minus_identity_on_bach_spin_two": False,
            "explicit_Tplus_band": False,
            "all_positive_real_Tplus_invertibility": False,
            "punctured_threshold_Tplus_interval": False,
            "physical_fredholm_realization": False,
            "green_resolvent_second_order_pole": False,
            "parent_overlap_equals_radial_overlap": False,
            "generic_radial_nonsplitting_is_time_jordan": False,
            "complete_polar_parent_gram": False,
            "generalized_ringdown": False,
            "time_domain_stability": False,
            "schwarzschild_retarded_convolution_evolution": False,
            "polar_global_connection": False,
            "quantum_positivity_or_unitarity": False,
        },
        "split": {
            "mathematical_structure": "paper/17-pure-weyl-schwarzschild-extension-structure.tex",
            "static_sector": "paper/18-static-bach-flat-black-hole-thermodynamics.tex",
            "computational_supplement": "paper/16-endpoint-nonselection-computational-supplement.tex",
            "source_archive": "paper/14-pure-weyl-black-hole-radiation.tex",
        },
    }


def coverage(claim_sha: str) -> dict:
    claims = [
        (
            "universal-null-einstein-sector",
            "Modulo the Euler boundary/corner term, the pure-Weyl bulk Hessian factors through linearized Ricci curvature on every four-dimensional Ricci-flat background.",
            "LOCAL-ALGEBRAIC",
        ),
        (
            "einstein-line-positivity-obstruction",
            "Every nondegenerate restriction of the inherited endpoint form that contains the null Einstein line is indefinite.",
            "LOCAL-ALGEBRAIC",
        ),
        (
            "schouten-einstein-maxwell-carrier",
            "The trace-adjusted Ricci carrier obeys a constrained linearized Einstein equation; its target-gauge sector is Maxwell with the opposite conventional bulk kinetic sign.",
            "LOCAL-ALGEBRAIC",
        ),
        (
            "second-order-parent-flux",
            "Modulo the Euler transgression, the quadratic Weyl system has an auxiliary-tensor parent action whose current is the off-diagonal linearized-Einstein Green pairing.",
            "LOCAL-ALGEBRAIC",
        ),
        (
            "parent-resolvent-and-conditional-pole",
            "The parent Hessian has an exact block inverse and exact rank-one Laurent algebra; a physical QNM double pole remains conditional on the analytic Fredholm and bounded-insertion gates.",
            "LOCAL-ALGEBRAIC",
        ),
        (
            "endpoint-positive-graph-cotangent",
            "No uniformly positive closed endpoint subspace contains the pure Einstein channel, and the hyperbolic spin-two quotient is canonically dual to the Einstein line.",
            "LOCAL-ALGEBRAIC",
        ),
        (
            "euler-cut-and-packet-isotropy",
            "The literal Einstein self-current is an Euler cut current and has zero integrated finite-radius flux on the declared smooth compact-frequency packet core.",
            "REDUCED-MODE",
        ),
        (
            "no-rational-spin-intertwiner",
            "For every positive real frequency, the axial spin-one and spin-two factors admit no nonzero rational differential intertwiner in either direction.",
            "REDUCED-MODE",
        ),
        (
            "incoming-populated-krein-space",
            "Every positive-real incoming axial trace direction is populated; the action Gram has inertia (1,2,0).",
            "LORENTZIAN-CAUSAL",
        ),
        (
            "outgoing-band-and-genericity",
            "Outgoing population is certified on the declared cell and generic off a locally finite positive-real set.",
            "REDUCED-MODE",
        ),
        (
            "no-growing-separated-mode",
            "The complete filtered axial system has no growing separated mode in the declared half-plane convention.",
            "LORENTZIAN-CAUSAL",
        ),
        (
            "connection-ep2",
            "One enclosed damped QNM has complete connection Smith valuations (0,0,2).",
            "REDUCED-MODE",
        ),
        (
            "threshold-nonresonance",
            "For every integer ell at least two, the spin-one and spin-two scalar factors have exact horizon-regular zero modes and no bounded zero-energy resonance.",
            "LOCAL-ALGEBRAIC",
        ),
    ]
    return {
        "ir": "science-forge-ir-v0",
        "claim_map": str(OUTPUT.relative_to(ROOT)),
        "claim_map_sha256": claim_sha,
        "nodes": [
            {
                "id": f"paper:16-lorentzian-endpoint-nonselection/claim/{slug}",
                "kind": "paper_claim",
                "body": {
                    "paper": "paper:16-lorentzian-endpoint-nonselection",
                    "asserts_lifecycle": "CLASSIFIED",
                    "dependency_tag": tag,
                    "boundary": text,
                    "material": True,
                },
            }
            for slug, text, tag in claims
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    claims = claim_map()
    claim_bytes = encoded(claims)
    claim_sha = hashlib.sha256(claim_bytes).hexdigest()
    write_or_check(OUTPUT, claims, args.check)
    write_or_check(COVERAGE, coverage(claim_sha), args.check)


if __name__ == "__main__":
    main()
