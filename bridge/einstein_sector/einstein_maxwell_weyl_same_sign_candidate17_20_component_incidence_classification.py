"""Classify candidate-17/20 admissible components and incidence strata."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_component_incidence_classification.json"
)
SCHEMA = (
    ROOT
    / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate17_20_component_incidence_classification.schema.json"
)
INPUTS = {
    "incidence_normal_form": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form.json"
    ),
    "complete_contraction": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction.json"
    ),
    "moving_square": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction.json"
    ),
    "balanced_radial": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction.json"
    ),
    "connected_hub": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre.json"
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_incidence_algebra() -> dict[str, object]:
    a, b, delta = sp.symbols("a b delta", nonzero=True, real=True)
    x, y, s = sp.symbols("x y s", nonnegative=True, real=True)
    c = delta + a * x - b * y
    negative_delta_x = sp.cancel(-delta / a)
    positive_delta_y = sp.cancel(delta / b)
    if sp.factor(c.subs({x: negative_delta_x, y: 0})) != 0:
        raise AssertionError("negative-delta boundary incidence changed")
    if sp.factor(c.subs({x: 0, y: positive_delta_y})) != 0:
        raise AssertionError("positive-delta boundary incidence changed")
    radial = sp.factor(
        c.subs({x: s * x, y: s * y}).subs(delta, -a * x + b * y)
    )
    if radial != sp.factor((1 - s) * (-a * x + b * y)):
        raise AssertionError("incidence-to-hub radial identity changed")
    return {
        "coefficient": "c=delta+a*x-b*y",
        "negative_delta_incidence": {
            "stratum": "G_zero",
            "coordinates": "x=-delta/a, y=0",
            "identity": sp.sstr(c.subs({x: negative_delta_x, y: 0})),
        },
        "positive_delta_incidence": {
            "stratum": "F_zero",
            "coordinates": "x=0, y=delta/b",
            "identity": sp.sstr(c.subs({x: 0, y: positive_delta_y})),
        },
        "incidence_to_hub": {
            "path": "(x,y)->(s*x,s*y)",
            "coefficient": sp.sstr(radial),
            "kernel_moment": "M_K(s)=s*M_K=0",
        },
    }


def occupation_strata() -> list[dict[str, object]]:
    return [
        {
            "id": "interior",
            "condition": "x>0 and y>0",
            "transvectant": "T3(F,G)=0",
            "forced_stabilizer": "none beyond the actual projective pair stabilizer H_[F,G]",
            "closure_meets": ["F_zero", "G_zero", "origin"],
        },
        {
            "id": "F_zero",
            "condition": "x=0 and y>0",
            "transvectant": "T3(0,G)=0 identically",
            "forced_stabilizer": "U(1)_F is contained in Stab(F,G)",
            "closure_meets": ["origin"],
        },
        {
            "id": "G_zero",
            "condition": "x>0 and y=0",
            "transvectant": "T3(F,0)=0 identically",
            "forced_stabilizer": "U(1)_G is contained in Stab(F,G)",
            "closure_meets": ["origin"],
        },
        {
            "id": "origin",
            "condition": "x=0 and y=0",
            "transvectant": "T3(0,0)=0 identically",
            "forced_stabilizer": "U(1)_F x U(1)_G x SO(3)_lifted fixes the kernel pair",
            "closure_meets": [],
        },
    ]


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    incidence = records["incidence_normal_form"]
    complete = records["complete_contraction"]
    moving = records["moving_square"]
    balanced = records["balanced_radial"]
    hub = records["connected_hub"]
    incidence_flags = incidence["classification"]
    complete_flags = complete["classification"]
    if not (
        incidence_flags["compactified_T3_kernel_moduli_defined"]
        and incidence_flags["singular_stabilizers_and_boundary_occupations_retained"]
        and incidence_flags["strict_opposite_sign_component_incidence_necessary"]
        and incidence_flags["strict_opposite_sign_component_incidence_sufficient"]
    ):
        raise AssertionError("incidence-normal-form dependency changed")
    if not (
        complete_flags["every_admissible_component_meets_incidence"]
        and complete_flags["candidate17_complete_singular_rotation_zero_fibre_connected"]
        and complete_flags["candidate20_complete_singular_rotation_zero_fibre_connected"]
        and complete_flags["all_positive_fixed_active_occupations_covered"]
    ):
        raise AssertionError("complete-contraction dependency changed")
    if not (
        moving["classification"][
            "alpha_delta_positive_complete_singular_stratum_contracts_to_hub"
        ]
        and moving["classification"]["zero_alpha_complete_stratum_contracts_to_hub"]
        and balanced["classification"][
            "candidate20_balance_complete_singular_union_contracts_to_hub"
        ]
        and hub["classification"][
            "candidate17_double_singular_rotation_zero_hub_connected"
        ]
        and hub["classification"][
            "candidate20_double_singular_rotation_zero_hub_connected"
        ]
    ):
        raise AssertionError("candidate assembly dependency changed")

    candidate_components = {
        "candidate17": {
            "candidate_id": 17,
            "candidate_scope": "rho_17; delta<0 on the complete nonzero active cone",
            "strict_opposite_sign_chamber": "delta<0<alpha",
            "component_count": 1,
            "components": [
                {
                    "id": "candidate17_hub_component",
                    "contains": "every admissible orbit in A_17",
                    "meets_incidence": True,
                    "incidence_stratum": "G_zero",
                    "incidence_coordinates": "x=-delta/a in (0,1), y=0",
                    "path": "delete G by convexity, time-reverse F to zero moment, cross I, then scale to the connected candidate-17 hub",
                }
            ],
            "nonincident_components": [],
        },
        "candidate20_negative_delta": {
            "candidate_id": 20,
            "candidate_scope": "rho_20 off balance with delta<0",
            "strict_opposite_sign_chamber": "delta<0<alpha",
            "component_count": 1,
            "components": [
                {
                    "id": "candidate20_negative_delta_hub_component",
                    "contains": "every admissible orbit in A_20^-",
                    "meets_incidence": True,
                    "incidence_stratum": "G_zero",
                    "incidence_coordinates": "x=-delta/a in (0,1), y=0",
                    "path": "delete G by convexity, time-reverse F to zero moment, cross I, then scale to the connected candidate-20 hub",
                }
            ],
            "nonincident_components": [],
        },
        "candidate20_positive_delta": {
            "candidate_id": 20,
            "candidate_scope": "rho_20 off balance with delta>0",
            "strict_opposite_sign_chamber": "alpha<0<delta",
            "component_count": 1,
            "components": [
                {
                    "id": "candidate20_positive_delta_hub_component",
                    "contains": "every admissible orbit in A_20^+",
                    "meets_incidence": True,
                    "incidence_stratum": "F_zero",
                    "incidence_coordinates": "x=0, y=delta/b in (0,1)",
                    "path": "delete F by convexity, time-reverse G to zero moment, cross I, then scale to the connected candidate-20 hub",
                }
            ],
            "nonincident_components": [],
        },
    }

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate17-20-component-incidence-classification-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_COMPONENT_INCIDENCE_CLASSIFICATION",
        "result_state": "CANDIDATE17_20_STRICT_SIGN_ADMISSIBLE_QUOTIENTS_HAVE_ONE_INCIDENT_COMPONENT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_CANDIDATE_SPECIFIC_PI0_AND_STRATUM_DISPOSITION",
        "scope": {
            **complete["scope"],
            "background": "candidate 17 and candidate 20 retained as separate rho_17 and rho_20 scopes; candidate-20 positive- and negative-delta chambers are also retained separately",
            "carrier": "the compact admissible orbit spaces A in the strict alpha*delta<0 chambers, with the complete four occupation strata and every compact orbit type retained",
        },
        "exact_incidence_algebra": exact_incidence_algebra(),
        "quotient": {
            "prequotient": incidence["compactified_moduli"]["prequotient"],
            "group": incidence["compactified_moduli"]["group"],
            "admissible_prequotient": incidence["moment_map_and_admissible_base"][
                "admissible_prequotient"
            ],
            "admissible_orbit_space": incidence["moment_map_and_admissible_base"][
                "admissible_orbit_space"
            ],
            "zero_wall_incidence": incidence["moment_map_and_admissible_base"][
                "zero_wall_incidence"
            ],
            "component_logic": "the certified path from every admissible point to the same connected candidate-specific hub lies in A and crosses I in the strict-sign chambers; therefore pi_0(A) is a singleton and its unique component meets I",
        },
        "occupation_strata": occupation_strata(),
        "orbit_type_refinement": {
            "definition": "for every conjugacy class (H) actually realized in G=U(1)_F x U(1)_G x SO(3)_lifted, refine each occupation stratum by A_(H)={z:Stab_G(z) is conjugate to H}/G",
            "generic_and_nonfree": "the union over all realized (H) is exact and disjoint; H is not assumed trivial, finite or constant, and no nonfree orbit is deleted",
            "zero_node_forced_isotropy": {
                "F_zero": "H contains U(1)_F",
                "G_zero": "H contains U(1)_G",
                "origin": "H contains the full kernel-pair action U(1)_F x U(1)_G x SO(3)_lifted",
            },
            "path_rule": "the component theorem is a theorem of the whole compact stratified quotient; its paths may cross orbit-type frontiers and are lifted through compact-group slices, so no freeness or fixed-orbit-type assumption enters",
            "component_disposition": "every realized occupation/orbit-type stratum is contained in the unique candidate-specific hub component",
        },
        "candidate_components": candidate_components,
        "complete_candidate_assembly": {
            "candidate17": {
                "alpha_less_equal_zero": "already contracts by the repaired moving-square theorem",
                "alpha_positive": "is the unique incident strict-sign component classified here",
                "fixed_positive_occupation_component_count": 1,
            },
            "candidate20": {
                "delta_zero": "the balance divisor contracts by the radial theorem",
                "off_balance_alpha_delta_positive_or_alpha_zero": "contracts by the repaired moving-square theorem",
                "off_balance_alpha_delta_negative": "the negative- and positive-delta chambers each have the unique incident component classified here",
                "fixed_positive_occupation_component_count": 1,
            },
            "intersection": "the two singular components meet in the separately certified connected double-singular hub",
        },
        "independence_witnesses": {
            "negative_delta": {
                "fixture": "a=3, b=1, delta=-1, alpha=1",
                "incidence": "x=1/3, y=0",
                "wrong_node_endpoint": "deleting F gives c=delta-b=-2<0 and crosses the wall prematurely",
            },
            "positive_delta": {
                "fixture": "a=1, b=3, delta=1, alpha=-1",
                "incidence": "x=0, y=1/3",
                "wrong_node_endpoint": "deleting G gives c=delta+a=2>0 and crosses the wall prematurely",
            },
            "candidate_separation": "candidate identifiers, coefficients, momenta and atlas scopes remain distinct even though the invariant proof template is shared",
        },
        "classification": {
            "candidate17_strict_sign_component_count_one": True,
            "candidate20_negative_delta_strict_sign_component_count_one": True,
            "candidate20_positive_delta_strict_sign_component_count_one": True,
            "every_strict_sign_component_meets_incidence": True,
            "nonincident_component_exists": False,
            "four_occupation_strata_exhaustive_and_disjoint": True,
            "zero_node_boundaries_retained": True,
            "nonfree_orbit_types_retained": True,
            "singular_stabilizers_retained": True,
            "candidate17_candidate20_identified": False,
            "fixed_positive_occupation_complete_candidate17_connected": True,
            "fixed_positive_occupation_complete_candidate20_connected": True,
            "occupation_strata_glued_across_distinct_total_occupations": False,
            "final_residual_descent": False,
            "all_mixed_cones_or_evolution_claim": False,
            "causal_observer_or_quantum_claim": False,
        },
        "interpretation": "There is no hidden disconnected deformable-kernel branch in either candidate. In each strict opposite-sign chamber the admissible compact quotient has exactly one path component, and that component reaches the appropriate one-zero-node incidence. Zero occupations and enhanced stabilizers are boundary/orbit-type strata inside the same component, not discarded exceptional cases. This remains a fixed-positive-active-occupation finite-carrier result.",
        "next_gate": "do not reopen component incidence; decide separately whether the intended final residual quotient requires gluing distinct total-occupation fibres, then export the fixed-occupation result through the same-background relative bridge",
        "claim_boundary": "This classifies pi_0 and zero-wall incidence only for the candidate-17 and candidate-20 compact fixed-positive-active-occupation singular carriers, with candidate scopes separate and all occupation/orbit-type strata retained. It does not glue distinct total occupations, prove a global Hausdorff leaf space outside this carrier, perform final residual descent, solve all mixed cones or evolution, or establish causal, observer or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_component_incidence_classification --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_component_incidence_classification",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_component_incidence_classification",
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
        raise AssertionError("component-incidence classification certificate is stale")
    print(
        "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_COMPONENT_INCIDENCE_CLASSIFICATION: PASS"
    )


if __name__ == "__main__":
    main()
