#!/usr/bin/env python3
"""Produce a fail-closed uniform inward scalar transport certificate."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ECS = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_ecs_inverse_tortoise_v1"
    / "certificate.json"
)
TAIL = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_infinity_tail_gate_v1"
    / "certificate.json"
)
COCYCLE = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_projective_cocycle_v1"
    / "certificate.json"
)
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md",
    "report.md",
    "schema.json",
    "produce.py",
    "verify.py",
    "test_ecs_inward_transport.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def produce() -> dict:
    ecs = json.loads(ECS.read_text())
    tail = json.loads(TAIL.read_text())
    cocycle = json.loads(COCYCLE.read_text())

    omega_upper = Fraction(tail["disk"]["omega_modulus_l1_upper"])
    omega_lower = Fraction(ecs["disk"]["omega_modulus_lower"])
    if omega_upper <= 0 or omega_lower <= 0:
        raise RuntimeError("invalid imported frequency bounds")

    outer_radius = 45
    match_radius = 4
    # x(45)-x(4)=41+2 log(43/2), and log(43/2)<4.  The latter follows
    # from exp(4)>1+4+4^2/2+4^3/6=71/3>43/2.
    exp4_partial_sum = Fraction(71, 3)
    if exp4_partial_sum <= Fraction(43, 2):
        raise RuntimeError("tortoise-length comparison failed")
    x_length_upper = 49

    # For X=(v,v_x), X_x=A X with A=[[0,1],[V,2*i*omega]].
    # On r in [4,45], both scalar potentials obey |V|<=6/r^2<=3/8.
    potential_upper = Fraction(3, 8)
    generator_norm_upper = 2 * omega_upper + potential_upper
    if generator_norm_upper <= 1:
        raise RuntimeError("unexpected generator norm branch")
    exponent_upper = x_length_upper * generator_norm_upper
    exponent_ceiling = 69
    if exponent_upper >= exponent_ceiling:
        raise RuntimeError("declared Gronwall exponent ceiling failed")
    # exp(1)<3, so exp(exponent_upper)<3^69.
    transfer_norm_upper = 3**exponent_ceiling

    transported_channels = []
    for channel in ecs["volterra"]["channels"]:
        initial_value_radius = Fraction(channel["reduced_value_ball"]["radius"])
        initial_derivative_radius = Fraction(
            channel["reduced_x_derivative_ball"]["radius"]
        )
        initial_norm_upper = max(
            1 + initial_value_radius, initial_derivative_radius
        )
        final_norm_upper = transfer_norm_upper * initial_norm_upper
        transported_channels.append(
            {
                "channel": channel["channel"],
                "initial_state": (
                    "(v(45),v_x(45)) in "
                    "Ball(1,value_radius) x Ball(0,derivative_radius)"
                ),
                "initial_value_radius": text(initial_value_radius),
                "initial_derivative_radius": text(initial_derivative_radius),
                "initial_infinity_norm_upper": text(initial_norm_upper),
                "matching_state_ball": {
                    "center": ["0", "0"],
                    "common_radius": text(final_norm_upper),
                    "radius_decimal_order": (
                        len(str(final_norm_upper.numerator))
                        - len(str(final_norm_upper.denominator))
                    ),
                    "excludes_zero_vector": False,
                },
            }
        )

    apparent_divisor_lower = match_radius * omega_lower
    if apparent_divisor_lower <= 0:
        raise RuntimeError("apparent divisor margin failed")

    return {
        "schema": "phase3-axial-qnm-ecs-inward-transport-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "UNIFORM_ANALYTIC_SCALAR_INWARD_TRANSPORT_EXISTS_BUT_COARSE_"
            "GRONWALL_BALL_IS_NOT_EVANS_USABLE_TANGENT_TAIL_OPEN"
        ),
        "imports": {
            "ecs_initializer": {
                "path": str(ECS.relative_to(ROOT)),
                "sha256": sha256(ECS),
                "authority": "certified reduced scalar balls at r=45",
            },
            "frequency_tail_gate": {
                "path": str(TAIL.relative_to(ROOT)),
                "sha256": sha256(TAIL),
                "authority": "exact disk-wide omega upper bound",
            },
            "projective_cocycle": {
                "path": str(COCYCLE.relative_to(ROOT)),
                "sha256": sha256(COCYCLE),
                "authority": (
                    "exact intrinsic tangent source and its rational divisors"
                ),
            },
        },
        "transport_interval": {
            "radial_path": "real r from 45 down to 4",
            "outer_radius": outer_radius,
            "matching_radius": match_radius,
            "tortoise_length_exact": "41+2*log(43/2)",
            "tortoise_length_upper": x_length_upper,
            "length_witness": (
                "exp(4)>1+4+4**2/2+4**3/6=71/3>43/2"
            ),
            "coefficient_poles_avoided": ["r=0", "r=2"],
        },
        "scalar_transport": {
            "state": "X=(v,dv/dx)",
            "equation": "dX/dx=[[0,1],[V_s(r),2*I*omega]]*X",
            "potential_uniform_upper": text(potential_upper),
            "omega_modulus_l1_upper": text(omega_upper),
            "generator_infinity_norm_upper": text(generator_norm_upper),
            "gronwall_exponent_upper": text(exponent_upper),
            "integer_exponent_ceiling": exponent_ceiling,
            "transfer_norm_upper": str(transfer_norm_upper),
            "analytic_frequency_dependence": True,
            "analyticity_reason": (
                "the compact real radial path avoids r=0,2; coefficients are "
                "rational in r and polynomial in omega; Picard iteration is "
                "uniform on the closed disk"
            ),
            "channels": transported_channels,
            "conclusion": (
                "Both certified ECS scalar initializer sets transport "
                "analytically to r=4. The exact Gronwall enclosure has radius "
                "of order 10^33 and is therefore not useful for an Evans "
                "boundary nonvanishing test."
            ),
        },
        "tangent_gate": {
            "source_available_exactly": True,
            "source_convention": cocycle["scalarization"]["source_convention"],
            "s1": cocycle["scalarization"]["s1"],
            "s0": cocycle["scalarization"]["s0"],
            "real_path_apparent_divisor": "r*omega-2*I",
            "real_path_apparent_divisor_modulus_lower": text(
                apparent_divisor_lower
            ),
            "finite_path_source_analytic": True,
            "ecs_tangent_initializer_constructed": False,
            "b_over_a_boundary_function_constructed": False,
            "quantified_blocker": (
                "The exact tangent source is analytic on r in [4,45], with "
                f"|r*omega-2*I|>={text(apparent_divisor_lower)}. "
                "What remains is a correlated ECS tail enclosure for the "
                "tau-derivative column at r=45; the scalar base balls alone "
                "do not determine that inhomogeneous boundary datum."
            ),
        },
        "claim_flags": {
            "scalar_inward_transport_to_r4_certified": True,
            "scalar_frequency_analyticity_preserved": True,
            "transported_ball_quantitatively_evans_usable": False,
            "tangent_source_regular_on_real_transport_path": True,
            "ecs_tangent_initializer_constructed": False,
            "b_over_a_on_contour_constructed": False,
            "Evans_boundary_nonzero_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "next_gates": [
            (
                "replace the global Gronwall ball by panelwise complex-ball "
                "Taylor or Lohner transport retaining a nontrivial center"
            ),
            (
                "differentiate the ECS scalar Volterra fixed point with "
                "respect to the intrinsic tau source to enclose the tangent "
                "initializer at r=45"
            ),
            (
                "propagate base and tangent columns in one correlated "
                "Taylor/dual-number rail and evaluate b/a on the contour"
            ),
        ],
        "does_not_establish": [
            "an Evans-usable scalar outgoing enclosure at r=4",
            "the intrinsic tangent Jost column or b/a on the contour",
            "the mixed four-state or full six-state Bach outgoing frame",
            "Evans-function boundary nonvanishing",
            "an argument-principle QNM count",
            "a defective Smith fibre, QNM or EP2",
        ],
    }


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-ecs-inward-transport-receipt-v1",
        "producer": "produce.py",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "input_sha256": {
            "ecs_initializer": sha256(ECS),
            "frequency_tail_gate": sha256(TAIL),
            "projective_cocycle": sha256(COCYCLE),
        },
        "artifact_sha256": {
            name: sha256(HERE / name) for name in ARTIFACTS
        },
        "commands": [
            (
                "python3 -m black_hole_programme.phase3."
                "axial_qnm_ecs_inward_transport_v1.produce"
            ),
            (
                "python3 -m black_hole_programme.phase3."
                "axial_qnm_ecs_inward_transport_v1.verify"
            ),
            (
                "python3 -m unittest -v black_hole_programme.phase3."
                "axial_qnm_ecs_inward_transport_v1."
                "test_ecs_inward_transport"
            ),
            (
                "python3 -m py_compile black_hole_programme/phase3/"
                "axial_qnm_ecs_inward_transport_v1/produce.py "
                "black_hole_programme/phase3/"
                "axial_qnm_ecs_inward_transport_v1/verify.py "
                "black_hole_programme/phase3/"
                "axial_qnm_ecs_inward_transport_v1/"
                "test_ecs_inward_transport.py"
            ),
        ],
        "tier_2_not_run": (
            "No shared operator changed; this is a successor bound over three "
            "content-addressed reduced-mode inputs."
        ),
        "tier_3_not_run": "Not a freeze, release or physical theorem promotion.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
