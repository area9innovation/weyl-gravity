"""Classify fixed-direction independent-node scaling on candidates 17/20."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_independent_node_scaling_contraction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate17_20_independent_node_scaling_contraction.schema.json"
INPUTS = {
    "moving_square": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction.json",
    "singular_locus": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json",
    "connected_hub": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_scaling_identities() -> dict[str, object]:
    a, b = sp.symbols("a b", positive=True)
    alpha, delta = sp.symbols("alpha delta", real=True)
    x, y, tau = sp.symbols("x y tau", real=True)
    x_star, y_star = sp.symbols("x_star y_star", real=True)

    coefficient = delta + a * x - b * y
    if sp.expand(coefficient.subs({x: 1, y: 1}) - alpha).subs(
        delta, alpha + b - a
    ) != 0:
        raise AssertionError("independent-scaling endpoint coefficient changed")

    # If an incidence point has c=M=0, affine linearity supplies both outer
    # segments of the three-stage contraction.
    first_x = (1 - tau) + tau * x_star
    first_y = (1 - tau) + tau * y_star
    first_c = sp.expand(coefficient.subs({x: first_x, y: first_y}))
    first_reduced = sp.expand(
        first_c.subs(delta, -a * x_star + b * y_star)
    )
    expected_first = sp.expand((1 - tau) * (delta + a - b)).subs(
        delta, -a * x_star + b * y_star
    )
    if sp.expand(first_reduced - expected_first) != 0:
        raise AssertionError("initial-to-incidence coefficient scaling changed")

    last_x = (1 - tau) * x_star
    last_y = (1 - tau) * y_star
    last_c = sp.expand(coefficient.subs({x: last_x, y: last_y}))
    last_reduced = sp.expand(last_c.subs(delta, -a * x_star + b * y_star))
    expected_last = sp.expand(tau * delta).subs(
        delta, -a * x_star + b * y_star
    )
    if sp.expand(last_reduced - expected_last) != 0:
        raise AssertionError("incidence-to-hub coefficient scaling changed")

    kappa = sp.symbols("kappa", positive=True)
    denominator = a * kappa - b
    y_collinear = sp.cancel(-delta / denominator)
    x_collinear = sp.cancel(kappa * y_collinear)
    if sp.factor((-x_collinear + kappa * y_collinear)) != 0:
        raise AssertionError("positive-ray moment incidence changed")
    if sp.factor(coefficient.subs({x: x_collinear, y: y_collinear})) != 0:
        raise AssertionError("positive-ray coefficient incidence changed")

    x_left_zero = sp.cancel(-delta / a)
    y_right_zero = sp.cancel(delta / b)
    if sp.factor(coefficient.subs({x: x_left_zero, y: 0})) != 0:
        raise AssertionError("left-zero incidence changed")
    if sp.factor(coefficient.subs({x: 0, y: y_right_zero})) != 0:
        raise AssertionError("right-zero incidence changed")

    return {
        "node_weights": "a=omega_minus*B_minus>0 and b=omega_plus*B_plus>0",
        "scaling_square": "(x,y) in [0,1]^2 are the squared amplitude fractions of the two fixed K nodes",
        "occupation_transfer": "A_minus(x)=A_minus+(1-x)*B_minus and A_plus(y)=A_plus+(1-y)*B_plus",
        "square_coefficient": "c(x,y)=delta+a*x-b*y",
        "endpoint_values": "c(1,1)=alpha and c(0,0)=delta, using delta=alpha+b-a",
        "weighted_kernel_moment": "M_K(x,y)=-x*U+y*V, with U=a*mu_f and V=b*mu_g fixed vectors in so(3)^*",
        "rotation_zero_equation": "M_K(x,y)+c(x,y)*mu_square=0 with mu_square in the closed unit Cartan moment ball",
        "strict_opposite_sign_bottleneck": "if alpha*delta<0, the intermediate-value theorem makes every continuous scaling path from (1,1) to (0,0) meet c=0; rotation zero there forces M_K=0",
        "incidence_set": "I={(x,y) in [0,1]^2:c(x,y)=0 and M_K(x,y)=0}",
    }


def incidence_classification() -> dict[str, object]:
    return {
        "both_weighted_moments_nonzero": {
            "positive_ray_case": "if V=kappa*U for kappa>0, I is the single candidate y_*=-delta/(a*kappa-b), x_*=kappa*y_*; it exists iff a*kappa!=b and 0<=y_*<=1 and 0<=x_*<=1",
            "all_other_directions": "if U and V do not lie on the same positive ray, M_K=0 with x,y>=0 forces x=y=0, which is incompatible with c=0 because delta!=0",
        },
        "U_zero_V_nonzero": "I exists iff x_*=-delta/a lies in [0,1], with y_*=0",
        "U_nonzero_V_zero": "I exists iff y_*=delta/b lies in [0,1], with x_*=0",
        "both_zero": "strict opposite signs and initial rotation zero force the initial square moment to vanish; this is already the certified phase-real sublocus and is excluded from the non-phase-real bottleneck",
        "genericity": "for nonzero U,V, failure of positive collinearity is open and dense in the product of moment directions, so the fixed-direction independent-scaling obstruction is generic",
    }


def contraction_construction() -> dict[str, object]:
    return {
        "necessity": "the intermediate-value theorem produces c=0, and the rotation-zero equation then requires an incidence point in I",
        "stage_1": "move linearly from (1,1) to (x_*,y_*); affine linearity gives c=(1-tau)*alpha and M_K=(1-tau)*M_K(1,1), so the initial square direction cancels throughout",
        "stage_2": "hold (x_*,y_*) fixed; because c=M_K=0, move the square moment continuously through the certified Cartan ball from its initial value to zero",
        "stage_3": "move linearly from (x_*,y_*) to (0,0); affine linearity gives M_K=0 and c=tau*delta, so a fixed phase-real square direction cancels throughout",
        "endpoint": "the K factor is at its vertex and the receiving square factor is phase-real, hence the path ends in the connected double-singular hub",
        "sufficiency": "every incidence point in I therefore gives an explicit three-stage contraction",
        "equivalence": "for alpha*delta<0, a fixed-direction independent-node-scaling contraction exists if and only if I is nonempty",
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    moving = records["moving_square"]["classification"]
    if not (
        moving["normalized_cartan_square_moment_image_closed_ball"]
        and moving["opposite_sign_interior_zero_obstruction_certified"]
        and moving["zero_alpha_complete_stratum_contracts_to_hub"]
        and not moving["nonuniform_scaling_classified"]
    ):
        raise AssertionError("moving-square input changed")
    singular = records["singular_locus"]["one_factor_singular_locus"]
    if singular["ambient_kernel"] != "K_T3={(f,g) in C^5 x C^5:T3(f,g)=0}, irreducible of complex dimension seven":
        raise AssertionError("third-transvectant kernel carrier changed")
    hub = records["connected_hub"]["classification"]
    if not (
        hub["candidate17_double_singular_rotation_zero_hub_connected"]
        and hub["candidate20_double_singular_rotation_zero_hub_connected"]
    ):
        raise AssertionError("connected endpoint hub changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate17-20-independent-node-scaling-contraction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_INDEPENDENT_NODE_SCALING_CONTRACTION",
        "result_state": "FIXED_DIRECTION_INDEPENDENT_NODE_SCALING_CLASSIFIED_BY_EXACT_BOTTLENECK_INCIDENCE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_FIXED_DIRECTION_INDEPENDENT_NODE_SCALING_ANSATZ_ON_STRICT_OPPOSITE_SIGN_STRATA",
        "scope": {
            **records["moving_square"]["scope"],
            "background": "candidates 17 and 20 separately; only their remaining alpha*delta<0 non-phase-real strata are newly classified",
            "carrier": "both complete fixed-positive-active-occupation singular components with fixed K-node directions, independent nonnegative squared node scales in [0,1], exact occupation transfer and arbitrary continuous motion of the receiving common-square direction",
        },
        "independent_scaling": exact_scaling_identities(),
        "bottleneck_incidence": incidence_classification(),
        "three_stage_contraction": contraction_construction(),
        "candidate_disposition": {
            "candidate17": "on the remaining alpha>0, delta<0 non-phase-real stratum, fixed-direction independent scaling contracts exactly on the explicit incidence locus I and is obstructed off I",
            "candidate20_off_balance": "on either remaining strict opposite-sign non-phase-real stratum, fixed-direction independent scaling contracts exactly on I and is obstructed off I",
            "previously_closed_strata": "delta=0, alpha*delta>0, alpha=0, phase-real points and square vertices retain their earlier contractions",
        },
        "classification": {
            "zero_alpha_uniform_scaling_repair_imported": True,
            "strict_opposite_sign_incidence_necessary": True,
            "strict_opposite_sign_incidence_sufficient": True,
            "fixed_direction_independent_node_scaling_ansatz_classified": True,
            "positive_collinear_incidence_formula_certified": True,
            "one_zero_moment_incidence_formulas_certified": True,
            "nonpositive_collinearity_obstructed_within_ansatz": True,
            "incidence_points_contract_to_connected_hub": True,
            "generic_fixed_direction_opposite_sign_points_obstructed": True,
            "candidate17_complete_singular_rotation_zero_fibre_connected": False,
            "candidate20_off_balance_complete_singular_rotation_zero_fibre_connected": False,
            "general_nonradial_no_go": False,
            "K_direction_deformation_classified": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Independent node scaling removes part, but not all, of the strict opposite-sign wall. The only way through is for the coefficient-zero line to meet the kernel-moment-zero locus inside the physical scaling square. That incidence is both necessary and sufficient: when present it supplies an explicit contraction, while generic fixed K directions miss it and remain obstructed. Deforming the K directions can still change the incidence and is the next genuine gate.",
        "next_gate": "allow the K-node directions to deform inside T3(f,g)=0 and determine whether every remaining off-incidence point can reach the positive-collinear incidence locus, or exhibit an invariant preventing that deformation",
        "claim_boundary": "This completely classifies the fixed-K-direction independent-node-scaling plus occupation-transfer ansatz. It is not a no-go for deformation of the K factor inside T3(f,g)=0 or for general nonradial paths, and it does not prove complete candidate-17 or candidate-20 off-balance connectedness or disconnection, glue occupations, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_independent_node_scaling_contraction --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_independent_node_scaling_contraction",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_independent_node_scaling_contraction",
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
        raise AssertionError("independent-node-scaling certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_INDEPENDENT_NODE_SCALING_CONTRACTION: PASS")


if __name__ == "__main__":
    main()
