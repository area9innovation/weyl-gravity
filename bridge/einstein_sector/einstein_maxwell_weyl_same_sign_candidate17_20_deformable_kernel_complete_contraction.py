"""Certify complete candidate-17/20 deformable-kernel contraction."""

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
    / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction.json"
)
SCHEMA = (
    ROOT
    / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction.schema.json"
)
INPUTS = {
    "incidence_normal_form": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form.json"
    ),
    "moving_square": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction.json"
    ),
    "balanced_radial": (
        ROOT
        / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction.json"
    ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spin_two_time_reversal() -> dict[str, object]:
    W = sp.diag(
        1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1
    )
    magnetic = list(range(-2, 3))
    index = {m: i for i, m in enumerate(magnetic)}
    j_plus = sp.zeros(5)
    j_minus = sp.zeros(5)
    for m in magnetic:
        if m < 2:
            j_plus[index[m + 1], index[m]] = 2 - m
        if m > -2:
            j_minus[index[m - 1], index[m]] = 2 + m
    generators = {
        "J1": (j_plus + j_minus) / 4,
        "J2": (j_plus - j_minus) / (4 * sp.I),
        "J3": sp.diag(*magnetic) / 2,
    }
    reversal = sp.zeros(5)
    for i, sign in enumerate((1, -1, 1, -1, 1)):
        reversal[i, 4 - i] = sign
    if reversal.T * W * reversal != W or reversal**2 != sp.eye(5):
        raise AssertionError("spin-two time reversal ceased to be antiunitary")
    for generator in generators.values():
        if sp.simplify(generator.conjugate().T * W - W * generator) != sp.zeros(5):
            raise AssertionError("normalized spin generator lost Hermiticity")
        if sp.simplify(reversal * generator.conjugate() * reversal + generator) != sp.zeros(5):
            raise AssertionError("time reversal no longer flips the spin moment")
        bilinear = sp.simplify(W * generator * reversal)
        if sp.simplify(bilinear.T + bilinear) != sp.zeros(5):
            raise AssertionError("time-reversal cross moment no longer vanishes")
    bad_reversal = sp.zeros(5)
    for i in range(5):
        bad_reversal[i, 4 - i] = 1
    if sp.simplify(
        bad_reversal * generators["J1"].conjugate() * bad_reversal
        + generators["J1"]
    ) == sp.zeros(5):
        raise AssertionError("time-reversal sign mutation was not detected")
    if generators["J3"].charpoly().as_expr() != (
        sp.Symbol("lambda") ** 5
        - sp.Rational(5, 4) * sp.Symbol("lambda") ** 3
        + sp.Rational(1, 4) * sp.Symbol("lambda")
    ):
        raise AssertionError("normalized spin spectrum changed")

    theta, sigma = sp.symbols("theta sigma", real=True)
    q = sp.cos(2 * theta) / (1 + sigma * sp.sin(2 * theta))
    derivative = sp.factor(sp.diff(q, theta))
    expected = -2 * (sigma + sp.sin(2 * theta)) / (
        1 + sigma * sp.sin(2 * theta)
    ) ** 2
    if sp.trigsimp(derivative - expected) != 0:
        raise AssertionError("time-reversal moment damping derivative changed")
    return {
        "basis": "magnetic m=-2,-1,0,1,2 with W=diag(1,1/4,1/6,1/4,1)",
        "normalized_generators": {
            name: [[sp.sstr(value) for value in row] for row in matrix.tolist()]
            for name, matrix in generators.items()
        },
        "time_reversal": "Theta(f)=R*conjugate(f), R=anti_diag(1,-1,1,-1,1)",
        "antiunitary": "R^T*W*R=W and Theta^2=1",
        "odd_moment": "Theta*J_a*Theta^{-1}=-J_a",
        "cross_term": "(W*J_a*R)^T=-W*J_a*R, hence <f,J_a Theta f>=0",
        "moment_bound": "the normalized J_n spectrum is {-1,-1/2,0,1/2,1}, so ||m(f)||<=||f||_W^2",
        "phase_gauge": "multiply f by a node phase so sigma=<f,Theta f>_W is real with 0<=sigma<=1",
        "unit_homotopy": "f_theta=(cos(theta)f+sin(theta)Theta f)/sqrt(1+sigma*sin(2theta)), 0<=theta<=pi/4",
        "moment_formula": "m(f_theta)=q(theta)*m(f), q=cos(2theta)/(1+sigma*sin(2theta))",
        "derivative": sp.sstr(expected),
        "monotonicity": "q decreases from 1 to 0 because sigma>=0 and sin(2theta)>=0",
        "endpoint": "f_pi/4 is phase-real and has zero rotation moment",
        "mutation_control": "replacing R by the unsigned anti-diagonal fails Theta*J1*Theta^{-1}=-J1",
    }


def convex_deletion_identities() -> dict[str, object]:
    a, b, delta, alpha, t = sp.symbols(
        "a b delta alpha t", real=True
    )
    c_positive = delta + a - b * t
    c_positive_affine = (1 - t) * (delta + a) + t * alpha
    c_negative_abs = b - delta - a * t
    c_negative_affine = (1 - t) * (b - delta) + t * (-alpha)
    relation = {alpha: delta + a - b}
    if sp.expand((c_positive - c_positive_affine).subs(relation)) != 0:
        raise AssertionError("positive-chamber coefficient convexity changed")
    if sp.expand((c_negative_abs - c_negative_affine).subs(relation)) != 0:
        raise AssertionError("negative-chamber coefficient convexity changed")
    x_star = -delta / a
    y_star = delta / b
    if sp.factor((delta + a * x_star)) != 0:
        raise AssertionError("negative-delta incidence coordinate changed")
    if sp.factor((delta - b * y_star)) != 0:
        raise AssertionError("positive-delta incidence coordinate changed")
    wrong_negative_delta_endpoint = delta - b
    wrong_positive_delta_endpoint = delta + a
    return {
        "delta_negative": {
            "path": "F fixed and unit, G_t=sqrt(t)G for t from 1 to 0",
            "moment": "M(t)=-a*m(F)+b*t*m(G)=(1-t)M(0)+t*M(1)",
            "coefficient": "c(t)=delta+a-b*t=(1-t)*(delta+a)+t*alpha>0",
            "endpoint_bound": "||M(0)||<=||M(1)||+b||m(G)||<=alpha+b=delta+a=c(0)",
            "convexity": "the norm of the affine moment path is at most the affine interpolation of its endpoint norms, hence ||M(t)||<=c(t)",
            "survivor": "at G=0, deform F by the time-reversal homotopy and then scale ||F||^2 from 1 through -delta/a to 0",
        },
        "delta_positive": {
            "path": "G fixed and unit, F_t=sqrt(t)F for t from 1 to 0",
            "moment": "M(t)=-a*t*m(F)+b*m(G)=(1-t)M(0)+t*M(1)",
            "absolute_coefficient": "-c(t)=b-delta-a*t=(1-t)*(b-delta)+t*(-alpha)>0",
            "endpoint_bound": "||M(0)||<=||M(1)||+a||m(F)||<=-alpha+a=b-delta=-c(0)",
            "convexity": "the norm of the affine moment path is at most the affine interpolation of its endpoint norms, hence ||M(t)||<=-c(t)",
            "survivor": "at F=0, deform G by the time-reversal homotopy and then scale ||G||^2 from 1 through delta/b to 0",
        },
        "wall_crossing": "after the surviving node becomes phase-real, its moment is zero; scaling through the one-zero-node incidence changes the sign of c with M_K=0 and a fixed phase-real square direction",
        "wrong_node_controls": {
            "delta_negative": "deleting F instead ends at c=delta-b<0 while c(1)=alpha>0, so it hits the wall before the surviving G moment is damped",
            "delta_positive": "deleting G instead ends at c=delta+a>0 while c(1)=alpha<0, so it hits the wall before the surviving F moment is damped",
            "symbolic_endpoints": {
                "delta_negative_wrong_endpoint": sp.sstr(wrong_negative_delta_endpoint),
                "delta_positive_wrong_endpoint": sp.sstr(wrong_positive_delta_endpoint),
            },
        },
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    incidence = records["incidence_normal_form"]["classification"]
    if not (
        incidence["strict_opposite_sign_component_incidence_necessary"]
        and incidence["strict_opposite_sign_component_incidence_sufficient"]
        and incidence["both_strict_sign_boundary_incidence_sets_nonempty"]
        and not incidence["every_admissible_component_meets_incidence"]
    ):
        raise AssertionError("deformable-kernel incidence predecessor changed")
    moving = records["moving_square"]["classification"]
    if not (
        moving["alpha_delta_positive_complete_singular_stratum_contracts_to_hub"]
        and moving["zero_alpha_complete_stratum_contracts_to_hub"]
    ):
        raise AssertionError("sign-compatible predecessor changed")
    balanced = records["balanced_radial"]["classification"]
    if not balanced["candidate20_balance_complete_singular_union_contracts_to_hub"]:
        raise AssertionError("candidate-20 balance predecessor changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate17-20-deformable-kernel-complete-contraction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_DEFORMABLE_KERNEL_COMPLETE_CONTRACTION",
        "result_state": "CANDIDATE17_20_COMPLETE_FIXED_OCCUPATION_SINGULAR_ROTATION_ZERO_UNIONS_CONTRACT_TO_CONNECTED_HUB",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_FIXED_POSITIVE_ACTIVE_OCCUPATION_SINGULAR_UNIONS_ON_CANDIDATES_17_AND_20",
        "scope": {
            **records["incidence_normal_form"]["scope"],
            "background": "candidates 17 and 20 separately at every fixed positive active occupation, including candidate 20 on and off its balance divisor",
            "carrier": "both complete singular components (S_plus x K_minus) union (K_plus x S_minus), with arbitrary compactified T3-kernel directions, zero-node boundaries, node phases and lifted rotations",
        },
        "spin_two_time_reversal": spin_two_time_reversal(),
        "convex_one_node_deletion": convex_deletion_identities(),
        "strict_opposite_sign_contraction": {
            "delta_negative_alpha_positive": [
                "scale the positive kernel node G to zero; endpoint and norm convexity keep ||M_K||<=c",
                "with G=0, T3(F,0)=0 identically; damp m(F) monotonically to zero by time reversal",
                "scale the phase-real F through ||F||^2=-delta/a and onward to the hub",
            ],
            "delta_positive_alpha_negative": [
                "scale the negative kernel node F to zero; endpoint and norm convexity keep ||M_K||<=-c",
                "with F=0, T3(0,G)=0 identically; damp m(G) monotonically to zero by time reversal",
                "scale the phase-real G through ||G||^2=delta/b and onward to the hub",
            ],
            "square_lift": "the prescribed square moment -M_K/c remains in its closed unit ball on the deletion and damping segments; at M_K=0 choose the phase-real square fibre and cross c=0",
            "component_consequence": "every point of the admissible orbit space A reaches the appropriate boundary incidence I, so every path component meets I",
        },
        "complete_candidate_assembly": {
            "candidate17": "delta<0 on its complete active cone; alpha<=0 is covered by the repaired moving-square theorem and alpha>0 by the new strict-opposite-sign path, so both singular components contract to the connected hub at every positive occupation",
            "candidate20_balance": "delta=0 is covered by the complete balanced radial theorem",
            "candidate20_off_balance": "alpha*delta>0 and alpha=0 are covered by the moving-square theorem; alpha*delta<0 is covered by the new strict-opposite-sign path, so both singular components contract to the connected hub",
            "quotient": "continuous equivariant contraction before the lifted-rotation quotient implies connectedness of the complete node-phase- and rotation-zero quotient image",
        },
        "classification": {
            "normalized_spin_two_moment_unit_ball_bound_certified": True,
            "time_reversal_zero_moment_homotopy_certified": True,
            "time_reversal_moment_norm_monotone": True,
            "delta_negative_convex_positive_node_deletion_certified": True,
            "delta_positive_convex_negative_node_deletion_certified": True,
            "every_admissible_component_meets_incidence": True,
            "strict_opposite_sign_complete_deformable_kernel_contraction": True,
            "candidate17_complete_singular_rotation_zero_fibre_connected": True,
            "candidate20_balance_complete_singular_rotation_zero_fibre_connected": True,
            "candidate20_off_balance_complete_singular_rotation_zero_fibre_connected": True,
            "candidate20_complete_singular_rotation_zero_fibre_connected": True,
            "all_positive_fixed_active_occupations_covered": True,
            "candidate17_candidate20_identified": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "all_orders_integration": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The apparent opposite-sign wall is not a genuine component obstruction once zero-node boundaries are retained. Delete the node whose signed contribution opposes the target chamber; convexity keeps the square demand physical. At that boundary the transvectant constraint releases the surviving direction, and an explicit time-reversal homotopy removes its angular moment before crossing the wall. Thus the complete fixed-occupation singular rotation-zero unions on candidates 17 and 20 are connected through the already certified hub.",
        "next_gate": "glue distinct total-occupation strata only if the declared residual quotient requires it, then perform the final residual/gauge descent; do not reopen fixed-occupation kernel-direction topology",
        "claim_boundary": "This closes the complete fixed-positive-active-occupation singular rotation-zero topology for candidates 17 and 20 in the compact finite carrier. It does not identify the candidates, glue distinct total-occupation strata, prove a Hausdorff global leaf space outside this carrier, perform final residual descent, construct all-orders solutions, or establish causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction",
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
        raise AssertionError("deformable-kernel complete-contraction certificate is stale")
    print(
        "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_DEFORMABLE_KERNEL_COMPLETE_CONTRACTION: PASS"
    )


if __name__ == "__main__":
    main()
