#!/usr/bin/env python3
"""Generate the fail-closed claim map for Paper 17."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure.tex"
OUTPUT = ROOT / "paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json"

AUTHORITIES = {
    "factor_filtration": (
        "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
    "projective_cocycle": (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_cocycle_v1/certificate.json"
    ),
    "simplicity_endomorphisms": (
        "black_hole_programme/phase4/"
        "rw_maxwell_simplicity_endomorphisms_v1/certificate.json"
    ),
    "local_commutant": (
        "black_hole_programme/phase4/"
        "axial_local_commutant_spectral_c_v1/certificate.json"
    ),
    "qnm_winding": (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_evans_contour_completion/"
        "full_contour_winding_v1/certificate.json"
    ),
    "qnm_selector": (
        "black_hole_programme/phase3/"
        "axial_qnm_projective_evans_contour_completion/"
        "local_selector_v1/certificate.json"
    ),
    "spin_one_unit": (
        "black_hole_programme/phase3/"
        "axial_qnm_spin_one_local_unit_v1/certificate.json"
    ),
    "fredholm_promotion": (
        "black_hole_programme/phase4/"
        "axial_qnm_fredholm_promotion_v1/certificate.json"
    ),
    "metric_reconstruction": (
        "black_hole_programme/phase3/"
        "axial_complete_reconstruction_repair/certificate.json"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


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


def payload() -> dict:
    return {
        "schema": "paper-draft-source-map-v1",
        "paper_id": "PAPER_17_PURE_WEYL_EXTENSION_RESONANCE",
        "result_id": "PAPER17_NONSPLIT_RW_EXTENSION_DEFECTIVE_RESONANCE",
        "lifecycle_state": "DRAFT_ALLOWED",
        "manuscript": str(PAPER.relative_to(ROOT)),
        "paper_sha256": digest(PAPER),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "authorities": authority_map(),
        "exact_identities": {
            "bach_cocycle_normal_form": {
                "q": "-I*(15*r + 13 + 12/r + 9/r**2)/(120*omega)",
                "representative": "I*omega*(r-2)/(2*r)",
                "parameter_domain": "omega != 0",
            },
            "triangular_gauge": {
                "operator": "q*D - D(q)/2",
                "commutator_on_kernel": "-K_U(q)/2",
                "gauge_for_K_U_q": "Q(2*q)",
            },
            "period_matrix": [
                ["y1*y2", "y2**2"],
                ["-y1**2", "-y1*y2"],
            ],
            "generalized_root": {
                "geometric_root": "[1,0]",
                "carrier_quotient": "-a1/b0",
                "assumptions": "a1 != 0 and b0 != 0",
            },
            "resonant_evaluation": {
                "selector": "b0/a1",
                "normalized_overlap": "beta/alpha",
                "resonance_velocity": "-kappa",
                "carrier_quotient": "-1/kappa",
                "fredholm_principal_coefficient": "-kappa/alpha",
            },
            "green_principal_coefficient": {
                "connection": "-b0/a1**2",
                "outgoing_green": "b0/a1**2",
                "rank": 1,
            },
        },
        "certified_scope": {
            "axial_l2_rw_rw_maxwell_filtration": True,
            "exact_partial_jet_realization": True,
            "axial_l2_nonsplit_all_positive_real": True,
            "bach_cocycle_normal_form_exact": True,
            "triangular_gauge_commutator_exact": True,
            "symmetric_square_period_matrix_exact": True,
            "spin2_local_commutant_dual_numbers": True,
            "unique_simple_spin_two_qnm_in_disk": True,
            "full_connection_smith_0_0_2": True,
            "resonant_evaluation_identity_exact": True,
            "resonant_functional_descends_to_extension_class": True,
            "generalized_root_carrier_nonzero": True,
            "finite_interval_radial_green_double_pole": True,
            "green_principal_coefficient_rank_one": True,
            "local_metric_reconstruction_nonzero": True,
        },
        "fail_closed_scope": {
            "physical_mass_parameter_identified": False,
            "parent_radial_overlap_operator_identity": False,
            "massive_qnm_slope_identified": False,
            "causal_exterior_spacetime_resolvent": False,
            "retarded_inverse_transform": False,
            "t_exp_iomega_t_ringdown_term": False,
            "time_domain_stability": False,
            "all_ell_bach_nonsplitting": False,
            "full_six_state_commutant_dual_numbers": False,
            "complete_complex_reducibility_locus": False,
            "quantum_positivity_or_unitarity": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    wanted = encoded(payload())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != wanted:
            raise SystemExit(f"REFUSED: generated artifact drift: {OUTPUT}")
        print(f"PASS {OUTPUT.relative_to(ROOT)}")
        return
    OUTPUT.write_bytes(wanted)
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
