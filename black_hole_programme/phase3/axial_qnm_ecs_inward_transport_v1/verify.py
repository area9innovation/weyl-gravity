#!/usr/bin/env python3
"""Independent verifier for the ECS inward scalar transport gate."""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
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


def f(text: str) -> Fraction:
    return Fraction(text)


def verify(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "phase3-axial-qnm-ecs-inward-transport-v1":
        errors.append("schema mismatch")

    for key, path in (
        ("ecs_initializer", ECS),
        ("frequency_tail_gate", TAIL),
        ("projective_cocycle", COCYCLE),
    ):
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        if document["imports"][key]["sha256"] != expected:
            errors.append(f"{key} hash mismatch")

    ecs = json.loads(ECS.read_text())
    tail = json.loads(TAIL.read_text())
    scalar = document["scalar_transport"]
    omega_upper = f(tail["disk"]["omega_modulus_l1_upper"])
    potential = Fraction(3, 8)
    generator = 2 * omega_upper + potential
    exponent = 49 * generator
    if f(scalar["potential_uniform_upper"]) != potential:
        errors.append("potential bound mismatch")
    if f(scalar["generator_infinity_norm_upper"]) != generator:
        errors.append("generator norm mismatch")
    if f(scalar["gronwall_exponent_upper"]) != exponent:
        errors.append("Gronwall exponent mismatch")
    if not exponent < 69:
        errors.append("integer exponent ceiling failed")
    if int(scalar["transfer_norm_upper"]) != 3**69:
        errors.append("transfer norm mismatch")

    source_channels = {
        channel["channel"]: channel for channel in ecs["volterra"]["channels"]
    }
    for channel in scalar["channels"]:
        source = source_channels[channel["channel"]]
        value_radius = f(source["reduced_value_ball"]["radius"])
        derivative_radius = f(
            source["reduced_x_derivative_ball"]["radius"]
        )
        initial = max(1 + value_radius, derivative_radius)
        final = 3**69 * initial
        if f(channel["initial_value_radius"]) != value_radius:
            errors.append(f"{channel['channel']} value radius drift")
        if f(channel["initial_derivative_radius"]) != derivative_radius:
            errors.append(f"{channel['channel']} derivative radius drift")
        if f(channel["initial_infinity_norm_upper"]) != initial:
            errors.append(f"{channel['channel']} initial norm mismatch")
        if f(channel["matching_state_ball"]["common_radius"]) != final:
            errors.append(f"{channel['channel']} final ball mismatch")

    omega_lower = f(ecs["disk"]["omega_modulus_lower"])
    divisor = 4 * omega_lower
    if f(
        document["tangent_gate"][
            "real_path_apparent_divisor_modulus_lower"
        ]
    ) != divisor:
        errors.append("tangent apparent divisor margin mismatch")

    flags = document["claim_flags"]
    for key in (
        "scalar_inward_transport_to_r4_certified",
        "scalar_frequency_analyticity_preserved",
        "tangent_source_regular_on_real_transport_path",
    ):
        if flags.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in (
        "transported_ball_quantitatively_evans_usable",
        "ecs_tangent_initializer_constructed",
        "b_over_a_on_contour_constructed",
        "Evans_boundary_nonzero_certified",
        "QNM_root_count_certified",
        "QNM_or_EP2_certified",
    ):
        if flags.get(key) is not False:
            errors.append(f"{key} must remain false")
    return errors


def main() -> int:
    document = json.loads(CERT.read_text())
    errors = verify(document)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS uniform analytic ECS scalar inward-transport shortfall gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
