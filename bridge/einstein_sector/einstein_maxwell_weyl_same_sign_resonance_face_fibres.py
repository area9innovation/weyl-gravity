"""Stratify the six same-sign resonance fibres over their scalar cones."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_resonance_face_fibres.schema.json"
INPUTS = {
    "scalar_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "cone_sections": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_cone_sections.json",
    "fibre_product": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json",
    "isolated": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "target_doublet_L3": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties.json",
    "scalar_L1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.json",
    "multiplicity_two_L3": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties.json",
    "regular_pencil_L4": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.json",
    "scalar_L4": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decomposition(record: dict, index: int) -> dict:
    value = record["decompositions"]
    rows = value if isinstance(value, list) else [item for item in value.values() if isinstance(item, dict)]
    return next(row for row in rows if row.get("candidate_index") == index)


def node(branch: str, momentum: int) -> str:
    return f"{branch}_n{momentum}"


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    scalar = records["scalar_rays"]
    if not scalar["classification"]["all_positive_rho_same_sign_scalar_cones_have_four_extreme_rays"]:
        raise AssertionError("scalar-cone theorem changed")
    if not records["cone_sections"]["classification"]["all_six_complete_scalar_cones_have_bounded_amplitude_sections"]:
        raise AssertionError("real section theorem changed")
    if not records["fibre_product"]["classification"]["all_six_bounded_cones_have_exact_necessary_and_sufficient_equational_formulas"]:
        raise AssertionError("bounded fibre-product theorem changed")

    supports = {row["ray_id"]: set(row["support"]) for row in scalar["extreme_rays"]}
    isolated = records["isolated"]["candidate_ledger"]["rows"]
    source_key = {
        16: "target_doublet_L3",
        17: "scalar_L1",
        18: "multiplicity_two_L3",
        19: "regular_pencil_L4",
        20: "scalar_L1",
        21: "scalar_L4",
    }
    rows = []
    for index in range(16, 22):
        collision = isolated[index - 1]
        first_node = node(collision["first_branch"], 1)
        second_node = node(collision["second_branch"], 2)
        always_positive = {"q_minus_n1", "q_minus_n2"}
        optional = [item for item in (first_node, second_node) if item not in always_positive]
        if len(optional) > 1:
            raise AssertionError("same-sign isolated pair acquired two optional nodes")
        automatic_rays = (
            [ray_id for ray_id, support in supports.items() if optional[0] not in support]
            if optional
            else []
        )

        source = records[source_key[index]]
        entry = decomposition(source, index)
        zero = entry.get("zero_variety", entry)
        if index == 19:
            components = zero["irreducible_components_over_C"]
            active = [item for item in components if item["component_id"].startswith("mixed_eigenline_")]
            active_description = "four real-supported mixed pencil-eigenline components"
            ambient = zero["ambient_dimension_over_C"]
            dimension = 10
            full_components = len(components)
            automatic_component = "doublet_fibre_zero"
        elif index == 21:
            components = entry["irreducible_components_over_C"]
            active = [item for item in components if item["component_id"].startswith("mixed_")]
            active_description = "two real mixed parity-proportionality components"
            ambient = entry["ambient_dimension_over_C"]
            dimension = 10
            full_components = len(components)
            automatic_component = "first_fibre_zero"
        else:
            active = [{"component_id": "irreducible_resonance_variety"}]
            active_description = zero.get("description", zero.get("factorization", "irreducible all-m resonance variety"))
            ambient = zero["ambient_dimension_over_C"]
            dimension = zero["dimension_over_C"]
            full_components = zero["irreducible_components_over_C"]
            automatic_component = "contained one-sided locus" if optional else "origin only"

        if optional:
            automatic_face = {
                "condition": f"{optional[0]} occupation = 0",
                "ray_generators": automatic_rays,
                "resonance_constraint": "IDENTICALLY_ZERO_BECAUSE_ONE_BILINEAR_FACTOR_VANISHES",
                "component_location": automatic_component,
            }
            active_condition = f"{optional[0]} occupation > 0; both resonant norms are nonzero"
        else:
            automatic_face = {
                "condition": "scalar-cone origin only",
                "ray_generators": [],
                "resonance_constraint": "TRIVIAL_AT_THE_ORIGIN_ONLY",
                "component_location": automatic_component,
            }
            active_condition = "every nonzero scalar-cone point; both q_minus resonant norms are strictly positive"

        rows.append(
            {
                "candidate_index": index,
                "rho": scalar["candidate_rows"][index - 16]["rho"],
                "collision": {
                    "first_node": first_node,
                    "second_node": second_node,
                    "target_branch": collision["target_branch"],
                    "output_ell": collision["output_ell"],
                    "temporal_channel": collision["admissible_temporal_channel"],
                },
                "automatic_zero_face": automatic_face,
                "active_stratum": {
                    "condition": active_condition,
                    "ambient_complex_dimension": ambient,
                    "resonance_complex_dimension": dimension,
                    "active_component_count_over_C": len(active),
                    "active_components": active,
                    "description": active_description,
                    "intersect_with": "the prescribed absolute-current norm level and mu_J=0 in the imported exact bounded fibre-product formula",
                },
                "full_resonance_component_count_over_C": full_components,
                "real_nonemptiness": "CERTIFIED_BY_THE_AXISYMMETRIC_SCALAR_CONE_SECTION",
            }
        )

    expected_faces = {
        16: [],
        17: ["R1", "R2"],
        18: ["R2", "R4"],
        19: ["R2", "R4"],
        20: ["R1", "R3"],
        21: ["R1", "R3"],
    }
    if {row["candidate_index"]: row["automatic_zero_face"]["ray_generators"] for row in rows} != expected_faces:
        raise AssertionError("scalar-face incidence changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-resonance-face-fibres-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_RESONANCE_FACE_FIBRES",
        "result_state": "COMPLETE_COMPLEX_RESONANCE_FACE_STRATIFICATION_ON_SIX_SCALAR_CONES",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_RESONANCE_FACE_FIBRES_ON_SIX_DISTINCT_COLLISION_BACKGROUNDS",
        "scope": {
            **scalar["scope"],
            "background": "six distinct collision candidates 16--21, retained separately",
            "carrier": "complete complex positive-frequency phase/parity resonance fibre over every face of each same-sign scalar occupation cone",
        },
        "face_rows": rows,
        "classification": {
            "all_six_resonance_fibres_stratified_over_complete_scalar_cones": True,
            "all_optional_branch_zero_faces_identified": True,
            "all_active_complex_component_ledgers_complete": True,
            "real_nonempty_section_on_every_scalar_cone_point": True,
            "bounded_fibre_product_formula_imported": True,
            "full_real_connected_component_decomposition": False,
            "rotation_moment_map_reduction_completed": False,
            "complete_real_bounded_component_decomposition": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The exact bounded fibre-product formula is now refined face by face: optional-branch-zero faces are automatic, and the active strata inherit the certified all-m complex components. What remains is the real connected-component and singular-stratum decomposition after fixing norms and imposing the lifted rotations, not another collision, occupation or sufficiency calculation.",
        "next_gate": "intersect each active real norm-level stratum with mu_J1=mu_J2=mu_J3=0 and classify real connected components; do not merge the six circumference backgrounds",
        "claim_boundary": "This is a complete complex resonance-fibre face stratification inside the imported exact bounded fibre-product formula. It is not a real connected-component or singular-stratum decomposition, an all-orders theorem, or a causal, residual, observational or quantum classification.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_resonance_face_fibres --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_resonance_face_fibres",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_resonance_face_fibres",
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
        raise AssertionError("same-sign resonance-face-fibre certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_RESONANCE_FACE_FIBRES: PASS")


if __name__ == "__main__":
    main()
