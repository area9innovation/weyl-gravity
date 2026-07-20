"""Certify the restricted Lee--Wald current on candidate 16's active component."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_active_restricted_current.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate16_active_restricted_current.schema.json"
INPUTS = {
    "resonance_faces": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "target_doublet": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties.json",
    "scalar_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    face = next(row for row in records["resonance_faces"]["face_rows"] if row["candidate_index"] == 16)
    if face["collision"] != {
        "first_node": "q_minus_n1",
        "second_node": "q_minus_n2",
        "output_ell": 3,
        "target_branch": "p_extra",
        "temporal_channel": "SUM",
    }:
        raise AssertionError("candidate-16 collision carrier changed")
    active = face["active_stratum"]
    if (active["active_component_count_over_C"], active["ambient_complex_dimension"], active["resonance_complex_dimension"]) != (1, 20, 12):
        raise AssertionError("candidate-16 active resonance variety changed")

    target = next(row for row in records["target_doublet"]["decompositions"] if row["candidate_index"] == 16)
    if target["zero_variety"] != {
        "ambient_dimension_over_C": 20,
        "dimension_over_C": 12,
        "irreducible_components_over_C": 1,
    }:
        raise AssertionError("candidate-16 target-doublet decomposition changed")
    if "rank-at-most-one determinantal cone" not in records["target_doublet"]["representation_theorem"]:
        raise AssertionError("candidate-16 determinantal representation changed")

    nodes = {row["id"]: row for row in records["scalar_rays"]["moment_curve_reduction"]["ordered_nodes"]}
    if nodes["q_minus_n1"]["current_sign"] != -1 or nodes["q_minus_n2"]["current_sign"] != -1:
        raise AssertionError("candidate-16 same-sign current input changed")
    if records["axial_current"]["full_solution_pairing"]["Einstein_branch_signature_for_lambda_ge_6"] != [1, 1]:
        raise AssertionError("axial Einstein-primary current changed")
    if records["polar_current"]["shell_pairing"]["Einstein_block_inertia"] != [1, 1]:
        raise AssertionError("polar Einstein-primary current changed")

    affine_dimension = target["zero_variety"]["dimension_over_C"]
    projective_dimension = affine_dimension - 2
    if projective_dimension != 10:
        raise AssertionError("candidate-16 projective dimension changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate16-active-restricted-current-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE16_ACTIVE_RESTRICTED_CURRENT",
        "result_state": "CANDIDATE16_ACTIVE_RESONANCE_VARIETY_HAS_STRATUMWISE_NONDEGENERATE_RESTRICTED_CURRENT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_RESTRICTED_CURRENT_ON_ONE_ACTIVE_CANDIDATE",
        "scope": {
            **records["resonance_faces"]["scope"],
            "background": "candidate 16 only at rho=17*(79+51*sqrt(3))/132",
            "carrier": "the complete irreducible candidate-16 q_minus(n=1) x q_minus(n=2) active resonance variety after fixing both nonzero node norms and quotienting both node phases",
            "parity": "complete axial and polar q-minus current spaces",
            "omega": "positive-frequency q-minus plus q-minus SUM collision into the L=3 p-extra target",
        },
        "component": {
            "component_id": "candidate16_irreducible_target_doublet_L3_variety",
            "affine_ambient_complex_dimension": 20,
            "affine_resonance_complex_dimension": 12,
            "projective_ambient": "CP^9 x CP^9",
            "projective_resonance_complex_dimension": projective_dimension,
            "irreducible_components_over_C": 1,
            "factorization": records["target_doublet"]["target_reduction"]["factorization"],
            "active_norm_condition": "both q-minus node norms are strictly positive at every nonzero candidate-16 scalar-cone point",
        },
        "restricted_current_theorem": {
            "node_current_signs": {"q_minus_n1": -1, "q_minus_n2": -1},
            "node_internal_complex_dimensions": {"q_minus_n1": 10, "q_minus_n2": 10},
            "ambient_phase_quotient_form": "-c1*omega_FS(H1) direct_sum -c2*omega_FS(H2), with c1,c2>0 and H1,H2 positive definite",
            "proof_identity": "for every nonzero complex tangent vector v=(v1,v2), g(v,v)=-c1*H1(v1,v1)-c2*H2(v2,v2)<0",
            "smooth_stratum_inertia": "negative definite of complex rank equal to the stratum dimension",
            "smooth_locus_generic_real_symplectic_rank": 20,
            "every_complex_smooth_stratum_restricted_current_nondegenerate": True,
            "singular_points_treated_as_smooth_manifold_points": False,
        },
        "classification": {
            "candidate16_active_restricted_current_gate_closed": True,
            "same_sign_definite_restriction_proof": True,
            "complete_axial_polar_internal_spaces_included": True,
            "every_complex_smooth_stratum_symplectic": True,
            "projective_active_variety_compact_and_irreducible": True,
            "rotation_zero_fibre_connected": False,
            "singular_stratum_moment_map_topology_classified": False,
            "candidates17_through21_restricted_currents_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Candidate 16 is the unique active same-sign collision whose two resonant input nodes both carry negative q-minus current. The action-derived current therefore restricts as a definite negative Kahler form on every complex smooth stratum; degeneracy cannot be created by the resonance equations. The remaining candidate-16 problem is singular Hamiltonian topology, not current degeneracy.",
        "next_gate": "classify the singular projective strata and the lifted-rotation zero fibre for candidate 16; separately compute the indefinite restricted currents on candidates 17 through 21",
        "claim_boundary": "This certifies stratumwise current nondegeneracy only for candidate 16 after fixed norms and node-phase quotient. It does not declare the singular projective variety an orbifold, prove connectedness of its rotation-zero fibre, classify candidates 17--21, or promote all-orders, causal, residual, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate16_active_restricted_current --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate16_active_restricted_current",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate16_active_restricted_current",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("candidate-16 active restricted-current certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE16_ACTIVE_RESTRICTED_CURRENT: PASS")


if __name__ == "__main__":
    main()
