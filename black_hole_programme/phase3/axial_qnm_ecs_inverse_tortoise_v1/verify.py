#!/usr/bin/env python3
"""Independent verifier for the pi/4 ECS inverse-tortoise certificate."""
from __future__ import annotations

import json
import sys
import hashlib
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
TAIL = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_infinity_tail_gate_v1"
    / "certificate.json"
)


def f(text: str) -> Fraction:
    return Fraction(text)


def verify(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "phase3-axial-qnm-ecs-inverse-tortoise-v1":
        errors.append("schema mismatch")

    tail = json.loads(TAIL.read_text())
    imported = document["imports"]["infinity_tail_gate"]
    tail_hash = hashlib.sha256(TAIL.read_bytes()).hexdigest()
    if imported["sha256"] != tail_hash:
        errors.append("imported infinity-tail hash mismatch")

    disk = document["disk"]
    tail_disk = tail["disk"]
    if disk["center_re"] != tail_disk["center_re"]:
        errors.append("imported disk real center mismatch")
    if disk["center_im"] != tail_disk["center_im"]:
        errors.append("imported disk imaginary center mismatch")
    if disk["radius"] != tail_disk["radius"]:
        errors.append("imported disk radius mismatch")
    omega_lower = f(disk["omega_modulus_lower"])
    delta = f(disk["phase_delta"])
    if omega_lower != f(tail_disk["omega_modulus_lower_from_real_part"]):
        errors.append("imported omega lower bound mismatch")
    if delta != f(tail["ecs_replacement"]["delta"]):
        errors.append("imported phase margin mismatch")
    kappa = f(disk["phase_decay_rate_lower"])
    if kappa != Fraction(7, 5) * delta or kappa <= 0:
        errors.append("phase decay rate mismatch")
    if omega_lower <= 0:
        errors.append("omega lower bound must be positive")

    branch = document["inverse_tortoise_branch"]
    if f(branch["real_part_slope_rational_lower"]) != Fraction(2, 3):
        errors.append("radial slope bound mismatch")
    if 22 * 22 * 2 <= 31 * 31:
        errors.append("strict slope witness failed")
    if branch["distance_from_zero_lower"] != "45":
        errors.append("r=0 avoidance mismatch")
    if branch["distance_from_horizon_lower"] != "43":
        errors.append("r=2 avoidance mismatch")

    expected = {
        "spin_one": {
            "integral": Fraction(46, 225),
            "point": Fraction(94, 30375),
        },
        "spin_two": {
            "integral": Fraction(12559, 60750),
            "point": Fraction(4324, 1366875),
        },
    }
    channels = document["volterra"]["channels"]
    if len(channels) != 2:
        errors.append("expected two scalar channels")
    for channel in channels:
        name = channel["channel"]
        if name not in expected:
            errors.append(f"unexpected channel {name}")
            continue
        integral = f(channel["potential_integral_upper"])
        point = f(channel["potential_point_upper_at_t0"])
        weighted = point / kappa
        alpha = (integral + weighted) / (2 * omega_lower)
        margin = 1 - alpha
        if integral != expected[name]["integral"]:
            errors.append(f"{name} potential integral mismatch")
        if point != expected[name]["point"]:
            errors.append(f"{name} point potential mismatch")
        if f(channel["exponentially_weighted_integral_upper"]) != weighted:
            errors.append(f"{name} weighted integral mismatch")
        if f(channel["operator_norm_upper"]) != alpha:
            errors.append(f"{name} operator norm mismatch")
        if f(channel["contraction_margin_lower"]) != margin:
            errors.append(f"{name} contraction margin mismatch")
        if not (0 < alpha < 1):
            errors.append(f"{name} is not contractive")
        value_radius = alpha / margin
        derivative_radius = weighted / margin
        if f(channel["reduced_value_ball"]["radius"]) != value_radius:
            errors.append(f"{name} value radius mismatch")
        if f(channel["reduced_x_derivative_ball"]["radius"]) != derivative_radius:
            errors.append(f"{name} derivative radius mismatch")
        if value_radius >= 1:
            errors.append(f"{name} value ball fails to exclude zero")

    flags = document["claim_flags"]
    required_true = (
        "ecs_inverse_tortoise_branch_certified",
        "ecs_branch_avoids_r0_and_r2",
        "spin_one_ecs_volterra_contraction_certified",
        "spin_two_ecs_volterra_contraction_certified",
        "coarse_reduced_scalar_outgoing_initializer_constructed",
    )
    required_false = (
        "full_bach_outgoing_frame_constructed",
        "finite_interval_complex_transport_certified",
        "Evans_boundary_nonzero_certified",
        "QNM_root_count_certified",
        "QNM_or_EP2_certified",
    )
    for key in required_true:
        if flags.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in required_false:
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
    print("PASS exact pi/4 ECS inverse-tortoise and scalar Volterra gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
