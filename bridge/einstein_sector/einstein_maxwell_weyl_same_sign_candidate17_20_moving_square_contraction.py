"""Classify the candidate-17/20 moving-square radial-contraction ansatz."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction.schema.json"
INPUTS = {
    "radial_contraction": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction.json",
    "common_square": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient.json",
    "singular_locus": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cartan_moment_ball() -> dict[str, object]:
    u, y = sp.symbols("u y", positive=True)
    radius = 3 * u / (2 + u**2)
    derivative = sp.factor(sp.diff(radius, u))
    expected_derivative = 3 * (2 - u**2) / (2 + u**2) ** 2
    if sp.factor(derivative - expected_derivative) != 0:
        raise AssertionError("normalized Cartan-square moment radius changed")
    inverse = (3 - sp.sqrt(9 - 8 * y**2)) / (2 * y)
    if sp.simplify(y * inverse**2 - 3 * inverse + 2 * y) != 0:
        raise AssertionError("Cartan-square moment-radius inverse changed")
    if sp.simplify(radius.subs(u, 1) - 1) != 0:
        raise AssertionError("Cartan-square moment radius no longer reaches one")
    return {
        "cartan_model": "S(z)=z*z^T-(z^T*z/3)I",
        "phase_gauge": "write z=x+i*y with x dot y=0 and |x|^2+|y|^2=1",
        "radial_parameter": "u=2*|x|*|y| in [0,1]",
        "normalized_moment_radius": "F(u)=3*u/(2+u^2)",
        "strict_monotonicity": "F'(u)=3*(2-u^2)/(2+u^2)^2>0 on [0,1]",
        "inverse_radius": "u(F)=(3-sqrt(9-8*F^2))/(2*F), with u(0)=0",
        "direction_orbits": "the moment direction is the oriented line x cross y, and SO(3) acts transitively on its unit sphere",
        "image": "the normalized Cartan-square moment map CP2 -> so(3)^* has the complete closed unit ball as its image",
        "continuous_scaling": "for every initial square direction and r in [0,1], a continuous direction path exists with mu_square(r)=r*mu_square(1)",
    }


def moving_square_identity() -> dict[str, object]:
    alpha, delta, s = sp.symbols("alpha delta s", real=True)
    coefficient = sp.expand(s * alpha + (1 - s) * delta)
    r = sp.cancel(s * alpha / coefficient)
    residual = sp.factor(-s * alpha + coefficient * r)
    if residual != 0:
        raise AssertionError("moving-square cancellation identity changed")
    derivative = sp.factor(sp.diff(r, s))
    if sp.factor(derivative - alpha * delta / coefficient**2) != 0:
        raise AssertionError("moving-square monotonicity identity changed")
    zero_crossing = sp.cancel(-delta / (alpha - delta))
    if sp.simplify(coefficient.subs(s, zero_crossing)) != 0:
        raise AssertionError("opposite-sign zero crossing changed")
    return {
        "occupation_fraction": "s=t^2 in [0,1]",
        "square_coefficient": "c(s)=s*alpha+(1-s)*delta",
        "initial_square_coefficient": "alpha=omega_plus*A_plus-omega_minus*A_minus",
        "total_coefficient": "delta=omega_plus*N_plus-omega_minus*N_minus",
        "initial_kernel_moment": "M_K=-alpha*mu_0",
        "required_moment_scale": "r(s)=s*alpha/c(s)",
        "moment_scale_derivative": "dr/ds=alpha*delta/c(s)^2",
        "exact_cancellation": "-s*alpha*mu_0+c(s)*r(s)*mu_0=0",
        "sign_compatible_case": "if alpha*delta>0 then c(s) never vanishes and r(s) lies in [0,1], with r(0)=0 and r(1)=1",
        "endpoint": "at s=0 the K factor is at its vertex and the square direction is phase-real, so the endpoint lies in the connected double-singular hub",
        "opposite_sign_zero": "if alpha*delta<0 then s_0=-delta/(alpha-delta) lies in (0,1), c(s_0)=0, and the remaining kernel moment -s_0*alpha*mu_0 is nonzero when mu_0 is nonzero",
        "zero_alpha_two_stage_contraction": "if alpha=0 then initial rotation zero gives M_K=0; first keep s=1 and move the coefficient-zero square direction continuously to a phase-real direction, then uniformly scale the K factor with mu_square=0",
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    radial = records["radial_contraction"]["classification"]
    if not (
        radial["candidate20_balance_complete_singular_union_contracts_to_hub"]
        and radial["candidate17_phase_real_common_square_sublocus_contracts_to_hub"]
        and not radial["off_balance_nonradial_contraction_no_go"]
    ):
        raise AssertionError("radial-contraction input changed")
    common = records["common_square"]["classification"]
    if not (
        common["candidate17_rotation_coefficient_strictly_negative_on_complete_nonzero_active_cone"]
        and common["candidate20_rotation_balance_divisor_nonempty"]
    ):
        raise AssertionError("frequency-weighted common-square input changed")
    singular = records["singular_locus"]["two_parity_product"]
    if singular["singular_locus"] != "(S_plus x K_minus) union (K_plus x S_minus)":
        raise AssertionError("singular carrier input changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate17-20-moving-square-contraction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_MOVING_SQUARE_CONTRACTION",
        "result_state": "UNIFORM_KERNEL_SCALING_WITH_ARBITRARY_MOVING_SQUARE_DIRECTION_CLASSIFIED_AFTER_ZERO_ALPHA_REPAIR",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_UNIFORM_SCALING_MOVING_SQUARE_ANSATZ_ON_BOTH_SINGULAR_COMPONENTS",
        "scope": {
            **records["radial_contraction"]["scope"],
            "background": "candidates 17 and 20 separately; candidate 20 balance, candidatewise off-balance sign-compatible strata and the complementary ansatz obstruction are retained separately",
            "carrier": "both complete fixed-positive-active-occupation singular components under uniform scaling of the arbitrary K factor, arbitrary continuous motion of the receiving common-square direction, and exact occupation transfer",
        },
        "cartan_square_moment_ball": cartan_moment_ball(),
        "moving_square_ansatz": moving_square_identity(),
        "complete_ansatz_disposition": {
            "delta_zero": "all points contract by the previously certified fixed-direction balance theorem",
            "mu_zero_or_square_vertex": "all points contract through a phase-real square direction",
            "alpha_delta_positive": "all points contract by the moving-square path because the required normalized moment scale stays in [0,1]",
            "alpha_delta_negative_with_mu_nonzero": "OBSTRUCTED within this ansatz at the unique interior zero of c(s)",
            "alpha_zero": "all points contract by a coefficient-zero square pre-rotation followed by the phase-real uniform contraction",
            "outside_ansatz": "nonuniform node scaling, deformation of the K factor beyond scalar multiplication, and general nonradial paths remain OPEN",
        },
        "candidate_disposition": {
            "candidate17": "delta<0 everywhere; the complete alpha<=0 stratum contracts, while alpha>0 with mu_0 nonzero meets the interior coefficient-zero obstruction",
            "candidate20_balance": "the complete singular union remains connected by the earlier theorem",
            "candidate20_off_balance": "the alpha*delta>0 and alpha=0 strata contract; the opposite-sign non-phase-real stratum is obstructed only within the declared ansatz",
        },
        "classification": {
            "normalized_cartan_square_moment_image_closed_ball": True,
            "uniform_kernel_scaling_moving_square_ansatz_classified": True,
            "alpha_delta_positive_complete_singular_stratum_contracts_to_hub": True,
            "candidate17_alpha_negative_complete_singular_stratum_contracts_to_hub": True,
            "candidate20_off_balance_alpha_same_sign_delta_stratum_contracts_to_hub": True,
            "square_factor_vertex_off_balance_contracts_to_hub": True,
            "opposite_sign_interior_zero_obstruction_certified": True,
            "zero_alpha_complete_stratum_contracts_to_hub": True,
            "candidate17_complete_singular_rotation_zero_fibre_connected": False,
            "candidate20_off_balance_complete_singular_rotation_zero_fibre_connected": False,
            "general_nonradial_no_go": False,
            "nonuniform_scaling_classified": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The fixed-direction residual is partly removable: the Cartan-square moment can move through a complete ball and cancels the scaled kernel moment whenever alpha and delta have the same sign. The alpha=0 boundary also contracts after a coefficient-zero pre-rotation; the former endpoint-continuity claim omitted this admissible first segment and is withdrawn. The remaining opposite-sign crossing is a genuine zero-coefficient obstruction to the entire repaired uniform-scaling/moving-square ansatz, but not to paths that deform the K factor or scale its two nodes nonuniformly.",
        "next_gate": "on the remaining alpha*delta<0 non-phase-real strata, apply the independent K-node-scaling successor and then allow deformation inside T3(f,g)=0, or construct an invariant that survives those enlarged paths",
        "claim_boundary": "This completely classifies only the uniform K-factor scaling plus occupation-transfer ansatz with an arbitrary moving common-square direction. It does not establish candidate-17 or candidate-20 off-balance complete-singular connectedness or disconnection, classify nonuniform K-node scaling or general nonradial paths, glue occupations, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction",
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
        raise AssertionError("moving-square contraction certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_MOVING_SQUARE_CONTRACTION: PASS")


if __name__ == "__main__":
    main()
