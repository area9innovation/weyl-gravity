#!/usr/bin/env python3
"""Independent verifier for the axial QNM infinity-tail negative gate."""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CERT = HERE / "certificate.json"
I = sp.I


def parse_fraction(text: str) -> Fraction:
    return Fraction(text)


def verify(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != "phase3-axial-qnm-infinity-tail-gate-v1":
        errors.append("schema mismatch")

    disk = document["disk"]
    cr = Fraction(disk["center_re"])
    ci = Fraction(disk["center_im"])
    rho = Fraction(disk["radius"])
    omega_upper = -cr + ci + 2 * rho
    omega_lower = -cr - rho
    if parse_fraction(disk["omega_modulus_l1_upper"]) != omega_upper:
        errors.append("omega upper bound mismatch")
    if parse_fraction(disk["omega_modulus_lower_from_real_part"]) != omega_lower:
        errors.append("omega lower bound mismatch")

    m, w = sp.symbols("m omega")
    p = m**2 - 4 * I * m * w + m + 8 * w**2 - 6
    recorded_p = sp.sympify(
        document["formal_recurrence"]["p_m"],
        locals={"m": m, "omega": w, "I": I},
    )
    if sp.factor(recorded_p - p) != 0:
        errors.append("p_m recurrence coefficient mismatch")

    gate = document["scaled_tail_gate"]
    order = int(gate["first_certified_expansive_order"])
    radius = int(gate["outer_radius"])
    lower = (
        Fraction(order * order + order - 6)
        - 4 * order * omega_upper
        - 8 * omega_upper * omega_upper
    )
    gain = lower / (2 * omega_upper * (order + 1) * radius)
    if parse_fraction(gate["gain_lower_at_first_order"]) != gain:
        errors.append("gain lower bound mismatch")
    if gain <= 1:
        errors.append("gain lower bound does not prove expansion")
    if parse_fraction(gate["gain_excess_over_one"]) != gain - 1:
        errors.append("gain excess mismatch")

    # Exact monotonicity after dividing the p bound by m+1.
    M = sp.symbols("Omega", real=True)
    L = m**2 + (1 - 4 * M) * m - 6 - 8 * M**2
    difference = sp.factor(L.subs(m, m + 1) / (m + 2) - L / (m + 1))
    numerator = sp.factor(difference * (m + 1) * (m + 2))
    expected = m**2 + 3 * m + 8 + 8 * M**2 - 4 * M
    if sp.factor(numerator - expected) != 0:
        errors.append("monotonicity identity failed")
    # 8*M^2-4*M = 8*(M-1/4)^2-1/2.
    if Fraction(gate["monotonicity_numerator_lower_bound"]) != Fraction(15, 2):
        errors.append("monotonicity floor mismatch")

    ecs = document["ecs_replacement"]
    delta = -(cr + rho) - (ci + rho)
    if parse_fraction(ecs["delta"]) != delta or delta <= 0:
        errors.append("ECS damping margin mismatch")

    flags = document["claim_flags"]
    required_true = (
        "formal_recurrence_rederived_exactly",
        "R45_forward_tail_noncontractive_uniformly",
        "pi_over_4_ecs_phase_uniformly_damped",
    )
    required_false = (
        "infinity_asymptotic_remainder_enclosed",
        "ecs_inverse_tortoise_branch_certified",
        "ecs_volterra_contraction_certified",
        "complex_ball_outgoing_initializer_constructed",
        "Evans_boundary_nonzero_certified",
        "QNM_root_count_certified",
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
    print("PASS exact R=45 infinity-tail noncontractivity gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
