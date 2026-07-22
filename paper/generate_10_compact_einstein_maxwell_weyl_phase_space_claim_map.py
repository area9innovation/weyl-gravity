#!/usr/bin/env python3
"""Generate the scoped claim map for Paper 10 deterministically."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper/10-compact-einstein-maxwell-weyl-phase-space-claim-map.json"

INPUTS = [
    "bridge/certificates/einstein_maxwell_product_incidence.json",
    "bridge/certificates/einstein_maxwell_chevreton_tangent.json",
    "bridge/certificates/einstein_maxwell_chevreton_formal_linearization.json",
    "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json",
    "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
    "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
    "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
    "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
    "bridge/certificates/einstein_maxwell_weyl_mixed_block_orthogonality.json",
    "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
    "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "bridge/certificates/einstein_maxwell_weyl_axial_reduced_action_hessian.json",
    "bridge/certificates/einstein_maxwell_weyl_axial_extra_detector.json",
    "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "bridge/certificates/EINSTEIN_MAXWELL_FOUR_DERIVATIVE_ACTION_RESPONSE_V1.json",
    "bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json",
    "bridge/phase1/BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_claim_map() -> dict[str, object]:
    return {
        "schema": "compact-linear-paper-claim-map-v1",
        "result_id": "COMPACT_EINSTEIN_MAXWELL_WEYL_LINEAR_PAPER_A",
        "result_state": "SCOPED_MATHEMATICAL_CLAIMS_THEOREM_FROZEN_EXTERNAL_SPECIALIST_REVIEW_PENDING",
        "lifecycle_state": "THEOREM_FROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "manuscript": "paper/10-compact-einstein-maxwell-weyl-phase-space.tex",
        "scope": {
            "background": "R_t x S1_L x S2, unit magnetic product fixture, fixed compact U(1) bundle P_N with N=2",
            "standard_einstein_maxwell_image": "complete axial and polar harmonic tangent including regular radiation, physical ell=1 quotient, homogeneous generalized block, and axial twist",
            "extra_weyl_maxwell_target": "complete generic axial and polar ell>=2 branches, classified independently",
            "quotient_stage": "after local gauge reduction and before any optional background-stabilizer/moment-map or final residual quotient",
        },
        "freeze_disposition": {
            "mathematical_claims": "THEOREM_FROZEN",
            "next_review": "external specialist review of the dual-number Chevreton bridge, exceptional harmonic reduction, and direct axial and polar Lee-Wald normalizations",
            "human_accountability": "final human verification of the manuscript, deterministic certificates, citations, and authorship disclosure remains required before submission",
            "additional_internal_major_calculation_required_before_circulation": False,
        },
        "certified_claims": {
            "linear_solution_quotient_inclusion_injective": True,
            "formal_linear_inclusion_covers_nonintegrable_jacobi_fields": True,
            "target_pullback_nondegenerate_on_complete_standard_image": True,
            "identity_inclusion_symplectic": False,
            "regular_radiative_relative_inertia_per_real_spatial_harmonic": [2, 2],
            "generic_axial_extra_module_on_every_physical_fiber": "(K_ell_n[omega]/(omega^2-k^2-lambda+2/3))^2",
            "all_compact_momenta_including_k_zero_certified": True,
            "generic_axial_extra_positive_frequency_current_inertia": [2, 0],
            "complete_generic_axial_positive_frequency_current_inertia": [3, 1],
            "generic_polar_extra_module_classified": True,
            "generic_polar_extra_positive_frequency_current_inertia": [2, 0],
            "complete_generic_polar_positive_frequency_current_inertia": [3, 1],
            "axial_polar_representatives_identified": False,
            "extra_spectral_coefficient_extractor_before_residual_descent": True,
            "connected_background_stabilizer_dimension": 5,
            "full_SO42_is_background_stabilizer": False,
            "generic_primary_modules_and_Lee_Wald_form_stabilizer_invariant": True,
            "stabilizer_generators_universally_presymplectically_null": False,
            "complete_parity_even_four_derivative_action_response_classified": True,
            "minimal_reduced_source_action_repair_four_derivative_lift_exists": False,
            "nonzero_four_derivative_deformation_with_zero_q_to_p_cross_response_exists": False,
        },
        "explicit_nonclaims": {
            "final_residual_descent_complete": False,
            "background_stabilizer_moment_map_descent_complete": False,
            "literal_four_dimensional_action_density_second_expansion_complete": False,
            "explicit_off_shell_chevreton_row_factorization_constructed": False,
            "global_multivariate_unimodular_smith_transformations_constructed": False,
            "nonlinear_einstein_sector_closed": False,
            "positive_frequency_hilbert_space_constructed": False,
            "particle_interpretation_constructed": False,
            "linear_or_nonlinear_stability_theorem": False,
            "quantum_ghost_or_unitarity_theorem": False,
            "asymptotically_flat_scattering_constructed": False,
            "lorentzian_causal_bv_complex_certified": False,
        },
        "inputs": {path: sha256(ROOT / path) for path in INPUTS},
        "verification_commands": [
            "python3 paper/generate_10_compact_einstein_maxwell_weyl_phase_space_claim_map.py --check",
            "python3 paper/verify_10_compact_einstein_maxwell_weyl_phase_space_claim_map.py",
            "pdflatex -interaction=nonstopmode -halt-on-error -output-directory paper paper/10-compact-einstein-maxwell-weyl-phase-space.tex",
            "pdflatex -interaction=nonstopmode -halt-on-error -output-directory paper paper/10-compact-einstein-maxwell-weyl-phase-space.tex",
            "pdflatex -interaction=nonstopmode -halt-on-error -output-directory paper paper/10-compact-einstein-maxwell-weyl-phase-space.tex",
        ],
        "claim_boundary": (
            "This manuscript assembles exact LOCAL-ALGEBRAIC/REDUCED-MODE compact linear results. "
            "The complete standard Einstein-Maxwell image is parity-complete. The complementary generic "
            "ell>=2 Weyl-Maxwell extra blocks are independently classified in the axial and polar sectors "
            "on the local-gauge-reduced solution module before final residual descent; each extra block has "
            "inertia (2,0) and each complete generic parity block has inertia (3,1). No axial/polar "
            "representative identification is made. The actual five-generator product-background stabilizer "
            "and its generic primary-module action are certified. A complete parity-even four-derivative "
            "action-response calculation gives a scoped no-lift theorem for the minimal reduced source-action "
            "repair, including a full-rank q-to-p zero-cross obstruction; it does not exclude higher-derivative, "
            "nonlocal or auxiliary-field repairs. No moment-map-zero or final residual quotient, nonlinear, "
            "causal, scattering, particle, stability, positive-frequency Hilbert, QME, determinant, ghost, "
            "unitarity, or other quantum theorem is promoted."
        ),
    }


def encoded() -> bytes:
    return (json.dumps(build_claim_map(), indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = encoded()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != expected:
            raise SystemExit(f"stale generated claim map: {OUTPUT.relative_to(ROOT)}")
        print("PASS: Paper 10 claim map is deterministic and current")
        return 0
    OUTPUT.write_bytes(expected)
    print(f"wrote {OUTPUT.relative_to(ROOT)} sha256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
