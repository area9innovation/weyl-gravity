"""Certify active linear-sheet currents and rotation links on candidates 19 and 21."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_linear_sheet_rotation_links.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_active_linear_sheet_rotation_links.schema.json"
INPUTS = {
    "resonance_faces": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "regular_pencil": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.json",
    "scalar_L4": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.json",
    "scalar_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "fibre_product": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "standard_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decomposition(record: dict[str, object], index: int) -> dict[str, object]:
    rows = record["decompositions"]
    if isinstance(rows, dict):
        rows = [row for row in rows.values() if isinstance(row, dict)]
    return next(row for row in rows if row.get("candidate_index") == index)


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    faces = {row["candidate_index"]: row for row in records["resonance_faces"]["face_rows"]}
    fibre_flags = records["fibre_product"]["classification"]
    if not (
        fibre_flags["all_six_bounded_cones_have_exact_necessary_and_sufficient_equational_formulas"]
        and fibre_flags["all_three_rotation_moment_maps_retained_in_formula"]
    ):
        raise AssertionError("bounded fibre-product theorem changed")
    if records["stabilizer"]["background_stabilizer"]["connected_lie_algebra"] != "R*H direct-sum R*P_x direct-sum so(3)":
        raise AssertionError("lifted rotation stabilizer changed")

    nodes = {
        row["id"]: row
        for row in records["scalar_rays"]["moment_curve_reduction"]["ordered_nodes"]
    }
    expected_signs = {"q_minus_n2": -1, "p_extra_n1": 1, "q_plus_n1": 1}
    if {node: nodes[node]["current_sign"] for node in expected_signs} != expected_signs:
        raise AssertionError("candidate-19/21 current signs changed")
    standard = records["standard_current"]["theorem"]["block_table"][0]
    if "common parity-independent branch weights" not in standard["pullback_relative_operator"]:
        raise AssertionError("q-primary parity-independent current theorem changed")
    if records["axial_current"]["full_solution_pairing"]["extra_branch_signature_for_lambda_ge_6"] != [2, 0]:
        raise AssertionError("axial p-primary current changed")
    if records["polar_current"]["shell_pairing"]["extra_positive_frequency_inertia"] != [2, 0]:
        raise AssertionError("polar p-primary current changed")

    pencil = decomposition(records["regular_pencil"], 19)
    pencil_components = [
        row
        for row in pencil["zero_variety"]["irreducible_components_over_C"]
        if row["component_id"].startswith("mixed_eigenline_")
    ]
    if len(pencil_components) != 4 or not pencil["zero_variety"]["all_mixed_components_real_supported"]:
        raise AssertionError("candidate-19 real linear sheets changed")

    scalar = decomposition(records["scalar_L4"], 21)
    scalar_components = [
        row
        for row in scalar["irreducible_components_over_C"]
        if row["component_id"].startswith("mixed_")
    ]
    if len(scalar_components) != 2 or not scalar["r_squared_interval"]["positive"]:
        raise AssertionError("candidate-21 real linear sheets changed")

    definitions = {
        19: {
            "components": pencil_components,
            "positive_node": "p_extra_n1",
            "negative_node": "q_minus_n2",
            "positive_subspace": "one real pencil eigenline in the four-dimensional p-extra internal current space tensor V_2",
            "negative_subspace": "the real graph S_axial+z_i*S_polar=0 in the two-dimensional q-minus parity space tensor V_2",
        },
        21: {
            "components": scalar_components,
            "positive_node": "q_plus_n1",
            "negative_node": "q_minus_n2",
            "positive_subspace": "the real graph A_polar=r*A_axial in the q-plus parity space tensor V_2",
            "negative_subspace": "the real graph B_polar=s*B_axial in the q-minus parity space tensor V_2",
        },
    }
    rows = []
    for index in (19, 21):
        face = faces[index]
        source = definitions[index]
        component_rows = []
        for component in source["components"]:
            if component["dimension_over_C"] != 10:
                raise AssertionError(f"candidate-{index} sheet dimension changed")
            component_rows.append(
                {
                    "component_id": component["component_id"],
                    "affine_complex_dimension": 10,
                    "resonant_node_subspaces": {
                        source["positive_node"]: source["positive_subspace"],
                        source["negative_node"]: source["negative_subspace"],
                    },
                    "restricted_Hermitian_current_inertia": [5, 5, 0],
                    "fixed_resonant_norm_phase_quotient": "CP^4 x CP^4 with one positive and one negative weighted Fubini--Study factor",
                    "fixed_resonant_norm_real_symplectic_dimension": 16,
                    "rotation_zero_link": "NONEMPTY_AND_CONNECTED",
                }
            )
        rows.append(
            {
                "candidate_index": index,
                "rho": face["rho"],
                "active_condition": face["active_stratum"]["condition"],
                "positive_node": source["positive_node"],
                "negative_node": source["negative_node"],
                "active_component_count": len(component_rows),
                "components": component_rows,
                "spectator_extension": "Every occupied spectator node contributes its full definite current projective factor. Direct-sum nondegeneracy, compactness and connectedness therefore persist on every fixed-occupation support stratum over the active scalar-cone region.",
                "distinctness": "The nonzero active-norm condition prevents passage between distinct real sheets through a one-sided component; node phases do not change a parity ratio or pencil eigenline.",
                "verdict": "ALL_ACTIVE_LINEAR_SHEET_ROTATION_LINKS_CONNECTED_COMPONENTWISE",
            }
        )

    return {
        "schema": "einstein-maxwell-weyl-same-sign-active-linear-sheet-rotation-links-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_LINEAR_SHEET_ROTATION_LINKS",
        "result_state": "CANDIDATES_19_AND_21_ACTIVE_LINEAR_SHEETS_HAVE_NONDEGENERATE_CURRENT_AND_CONNECTED_ROTATION_LINKS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_ALL_SIX_ACTIVE_LINEAR_SHEETS_ON_CANDIDATES_19_AND_21",
        "scope": {
            **records["resonance_faces"]["scope"],
            "background": "candidates 19 and 21 only, retained as distinct compact Plebanski--Hacyan collision backgrounds",
            "carrier": "the four real pencil-eigenline active sheets of candidate 19 and the two real parity-proportional active sheets of candidate 21, at every fixed nonzero active occupation and every spectator support stratum",
            "parity": "complete axial/polar graph or pencil-eigenline subspaces on the resonant nodes; complete axial/polar spaces on occupied spectators",
            "omega": "candidate-specific positive-frequency SUM collisions into L=4, with conjugate reality completion",
        },
        "restricted_current_theorem": {
            "orthogonal_spectral_sum": "Distinct branch/momentum nodes are Lee--Wald orthogonal after the S1 and stationary harmonic integrations.",
            "definite_subspace_lemma": "The restriction of a positive- or negative-definite Hermitian form to any nonzero complex linear subspace is definite and nondegenerate.",
            "active_core_inertia": "Each ten-complex-dimensional active sheet is the direct sum of one positive C^5 node graph/eigenline and one negative C^5 node graph/eigenline, hence has Hermitian inertia (5,5,0).",
            "spectator_stability": "Adding full definite spectator-node blocks preserves nondegeneracy on every fixed-occupation support stratum.",
            "all_six_active_linear_sheets_restricted_current_nondegenerate": True,
        },
        "rotation_link_theorem": {
            "projective_model": "The active resonant core at fixed node norms and after its two phase quotients is CP^4 x CP^4 with a signed nondegenerate Fubini--Study form; occupied spectators add projective factors.",
            "Hamiltonian_action": "The diagonal lifted SO(3) action preserves every real sheet and has moment map (mu_J1,mu_J2,mu_J3).",
            "nonemptiness": "Choose the spin-two m=0 vector in every angular factor and the certified real internal graph/eigenline; arbitrary prescribed positive node norms are obtained by scaling.",
            "connectedness": "Each projective product is compact and connected, so Lerman--Meinrenken--Tolman--Woodward Theorem 1.1(b) gives a connected zero fibre; the connected node-phase torus preimage is connected.",
            "component_counts": {"candidate_19": 4, "candidate_21": 2},
            "all_fixed_occupation_rotation_zero_links_nonempty": True,
            "all_fixed_occupation_rotation_zero_links_connected_componentwise": True,
        },
        "candidate_rows": rows,
        "classification": {
            "candidate19_four_active_linear_sheets_classified": True,
            "candidate21_two_active_linear_sheets_classified": True,
            "all_six_restricted_currents_nondegenerate": True,
            "all_six_fixed_occupation_rotation_zero_links_connected_componentwise": True,
            "spectator_support_strata_included": True,
            "candidate16_singular_active_variety_classified_here": False,
            "candidates17_18_20_active_varieties_classified": False,
            "different_active_sheets_identified_by_residual_symmetry": False,
            "occupation_strata_glued": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The first indefinite active resonance carriers do not acquire a Lee--Wald radical. Their positive and negative directions live on different definite node factors, while the resonance equations select linear internal subspaces. Each of the six resulting real sheets has one connected lifted-rotation zero link at every fixed occupation. This is componentwise topology, not an identification of the four candidate-19 sheets or the two candidate-21 sheets.",
        "next_gate": "compute restricted currents on the nonlinear active varieties of candidates 17, 18 and 20, and classify the singular Hamiltonian strata of candidate 16; keep occupation gluing separate",
        "claim_boundary": "This theorem covers only the six smooth real linear active sheets on candidates 19 and 21. It does not identify distinct sheets, classify candidates 16--18 or 20, glue occupation strata, perform final residual descent, prove all-orders integration, or construct causal, observational or quantum maps.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_active_linear_sheet_rotation_links --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_active_linear_sheet_rotation_links",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_active_linear_sheet_rotation_links",
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
        raise AssertionError("active linear-sheet rotation-link certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_LINEAR_SHEET_ROTATION_LINKS: PASS")


if __name__ == "__main__":
    main()
