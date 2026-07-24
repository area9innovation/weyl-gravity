#!/usr/bin/env python3
"""Independent verifier for the intrinsic tangent ECS initializer."""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
ECS = ROOT / "black_hole_programme/phase3/axial_qnm_ecs_inverse_tortoise_v1/certificate.json"
TAIL = ROOT / "black_hole_programme/phase3/axial_qnm_infinity_tail_gate_v1/certificate.json"
COCYCLE = ROOT / "black_hole_programme/phase3/axial_qnm_projective_cocycle_v1/certificate.json"


def f(text: str) -> Fraction:
    return Fraction(text)


def verify(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "phase3-axial-qnm-ecs-tangent-initializer-v1":
        errors.append("schema mismatch")
    for key, path in (
        ("ecs_base_initializer", ECS),
        ("frequency_tail_gate", TAIL),
        ("projective_cocycle", COCYCLE),
    ):
        if document["imports"][key]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append(f"{key} hash mismatch")

    ecs = json.loads(ECS.read_text())
    tail = json.loads(TAIL.read_text())
    spin2 = next(x for x in ecs["volterra"]["channels"] if x["channel"] == "spin_two")
    omega_upper = f(tail["disk"]["omega_modulus_l1_upper"])
    omega_lower = f(ecs["disk"]["omega_modulus_lower"])
    kappa = f(ecs["disk"]["phase_decay_rate_lower"])
    alpha = f(spin2["operator_norm_upper"])
    jv = f(spin2["exponentially_weighted_integral_upper"])
    o2 = omega_upper**2
    r0 = 45
    iq = Fraction(1, 1) / (5 * omega_lower * Fraction(2, 3)) * (
        2 * o2 / r0
        + (7 * o2 + 12) / (2 * r0**2)
        + (6 * o2 + 24) / (3 * r0**3)
    )
    q0 = Fraction(1, 1) / (5 * omega_lower) * (
        2 * o2 / r0**2
        + (7 * o2 + 12) / r0**3
        + (6 * o2 + 24) / r0**4
    )
    jq = q0 / kappa
    kq = (iq + jq) / (2 * omega_lower)
    base = 1 / (1 - alpha)
    value = kq / (1 - alpha) ** 2
    derivative = jv * value + jq * base
    bounds = document["source_bounds"]
    if f(bounds["source_integral_upper"]) != iq:
        errors.append("source integral mismatch")
    if f(bounds["source_point_upper_at_r45"]) != q0:
        errors.append("source point mismatch")
    if f(bounds["source_exponentially_weighted_integral_upper"]) != jq:
        errors.append("weighted source mismatch")
    if f(bounds["source_volterra_kernel_norm_upper"]) != kq:
        errors.append("source kernel mismatch")
    tangent = document["tangent_initializer"]
    if f(tangent["base_solution_norm_upper"]) != base:
        errors.append("base norm mismatch")
    if f(tangent["value_ball"]["radius"]) != value:
        errors.append("tangent value radius mismatch")
    if f(tangent["x_derivative_ball"]["radius"]) != derivative:
        errors.append("tangent derivative radius mismatch")

    flags = document["claim_flags"]
    for key in (
        "canonical_projective_tangent_ecs_initializer_certified",
        "tangent_initializer_frequency_analytic",
    ):
        if flags.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in (
        "manuscript_factor_frame_b_initializer_certified",
        "b_over_a_on_contour_constructed",
        "Evans_boundary_nonzero_certified",
        "QNM_root_count_certified",
        "QNM_or_EP2_certified",
    ):
        if flags.get(key) is not False:
            errors.append(f"{key} must remain false")
    return errors


def main() -> int:
    errors = verify(json.loads(CERT.read_text()))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS intrinsic projective tangent ECS initializer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
