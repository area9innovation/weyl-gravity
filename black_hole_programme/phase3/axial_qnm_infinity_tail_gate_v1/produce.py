#!/usr/bin/env python3
"""Produce the exact noncontractivity witness for the formal infinity tail."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ENDPOINT = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_endpoint_germ_divisor_v1"
    / "certificate.json"
)
SEED = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_contour_seed_preflight_v1"
    / "qnm_contour_diagnostic.json"
)
SEED_SHOOTER = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_contour_seed_preflight_v1"
    / "qnm_mpmath_shooting_preflight.py"
)
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md",
    "report.md",
    "schema.json",
    "produce.py",
    "verify.py",
    "test_infinity_tail_gate.py",
)

I = sp.I
M, W = sp.symbols("m omega")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(sp.cancel(sp.together(value))))


def frac_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def produce() -> dict:
    endpoint = json.loads(ENDPOINT.read_text())
    seed = json.loads(SEED.read_text())
    infinity = endpoint["infinity_germ"]

    a = [sp.sympify(item) for item in infinity["A_coefficients_low_to_high"]]
    b = [
        sp.sympify(item, locals={"omega": W, "I": I})
        for item in infinity["B_coefficients_low_to_high"]
    ]
    c = [
        sp.sympify(item, locals={"omega": W, "I": I})
        for item in infinity["C_coefficients_low_to_high"]
    ]
    if a != [0, 0, 1, -4, 4]:
        raise RuntimeError("infinity A polynomial drift")

    p = sp.factor(a[2] * M * (M - 1) + b[1] * M + c[0])
    q = sp.factor(
        a[3] * (M - 1) * (M - 2) + b[2] * (M - 1) + c[1]
    )
    s = sp.factor(
        a[4] * (M - 2) * (M - 3) + b[3] * (M - 2) + c[2]
    )
    expected_p = M**2 - 4 * I * M * W + M + 8 * W**2 - 6
    if sp.factor(p - expected_p) != 0:
        raise RuntimeError("nearest-coefficient recurrence drift")

    center_re = Fraction(seed["center"][0])
    center_im = Fraction(seed["center"][1])
    radius = Fraction(seed["radius"])
    if not (center_re < 0 < center_im):
        raise RuntimeError("unexpected seed-disk quadrant")

    # An exact L1 upper bound for |omega| on the closed disk.
    omega_upper = -center_re + center_im + 2 * radius
    omega_lower = -center_re - radius
    if omega_lower <= 0:
        raise RuntimeError("disk does not stay left of the imaginary axis")

    outer_radius = 45
    first_order = 49

    def p_lower(order: int) -> Fraction:
        return (
            Fraction(order * order + order - 6)
            - 4 * order * omega_upper
            - 8 * omega_upper * omega_upper
        )

    def gain_lower(order: int) -> Fraction:
        return p_lower(order) / (
            2 * omega_upper * (order + 1) * outer_radius
        )

    gain_49 = gain_lower(first_order)
    if gain_49 <= 1:
        raise RuntimeError("declared noncontractivity order is not proved")

    # F_m=L_m/(m+1) is strictly increasing because
    # F_(m+1)-F_m has the positive numerator below.
    monotonic_numerator = sp.factor(
        8 * W**2 - 4 * W + M**2 + 3 * M + 8
    )
    # For real x, 8*x^2-4*x >= -1/2, so this is >= 15/2 at m>=0.
    monotonic_floor = Fraction(15, 2)

    # On theta=pi/4, Im(omega*exp(i theta)) is uniformly negative.
    ecs_margin = -(center_re + radius) - (center_im + radius)
    if ecs_margin <= 0:
        raise RuntimeError("pi/4 ECS angle is not uniformly damped")

    document = {
        "schema": "phase3-axial-qnm-infinity-tail-gate-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "EXACT_NAIVE_INFINITY_RECURRENCE_NONCONTRACTIVE_"
            "ECS_REPLACEMENT_SPECIFIED_NO_REMAINDER_BOUND"
        ),
        "imports": {
            "endpoint_germ_certificate": {
                "path": str(ENDPOINT.relative_to(ROOT)),
                "sha256": sha256(ENDPOINT),
                "authority": "exact formal recurrence input",
            },
            "noncertifying_seed_geometry": {
                "path": str(SEED.relative_to(ROOT)),
                "sha256": sha256(SEED),
                "authority": "exact disk geometry only",
            },
            "noncertifying_shooting_source": {
                "path": str(SEED_SHOOTER.relative_to(ROOT)),
                "sha256": sha256(SEED_SHOOTER),
                "authority": (
                    "provenance for the practical R=45 initializer only; "
                    "its numerical output is not evidence"
                ),
            },
        },
        "disk": {
            "center_re": str(center_re),
            "center_im": str(center_im),
            "radius": str(radius),
            "omega_modulus_l1_upper": frac_text(omega_upper),
            "omega_modulus_lower_from_real_part": frac_text(omega_lower),
        },
        "formal_recurrence": {
            "equation": (
                "2*I*omega*(m+1)*g_(m+1)"
                "+p_m*g_m+q_m*g_(m-1)+s_m*g_(m-2)=0"
            ),
            "p_m": encode(p),
            "q_m": encode(q),
            "s_m": encode(s),
            "normalization": "g_0=1 and g_k=0 for k<0",
            "series_kind": "formal Gevrey-type inverse-r asymptotic recurrence",
        },
        "scaled_tail_gate": {
            "outer_radius": outer_radius,
            "scaled_terms": "t_m=g_m/R**m",
            "direct_gain": (
                "alpha_m=-p_m/(2*I*omega*(m+1)*R)"
            ),
            "p_modulus_lower_bound": (
                "m**2+m-6-4*m*Omega-8*Omega**2"
            ),
            "Omega": frac_text(omega_upper),
            "first_certified_expansive_order": first_order,
            "gain_lower_at_first_order": frac_text(gain_49),
            "gain_excess_over_one": frac_text(gain_49 - 1),
            "all_later_orders_expansive": True,
            "monotonicity_identity": (
                "L_(m+1)/(m+2)-L_m/(m+1)"
                "=(m**2+3*m+8+8*Omega**2-4*Omega)"
                "/((m+1)*(m+2))"
            ),
            "monotonicity_numerator_symbolic": encode(monotonic_numerator),
            "monotonicity_numerator_lower_bound": frac_text(monotonic_floor),
            "conclusion": (
                "At R=45 the independent forward recurrence for the scaled "
                "tail has |alpha_m|>1 uniformly on the disk for every m>=49. "
                "It cannot supply an all-order geometric contraction tail."
            ),
        },
        "ecs_replacement": {
            "contour": "x=r_* = x_0+exp(I*pi/4)*t, t>=0",
            "factored_unknown": "y=exp(-I*omega*x)*v",
            "volterra_equation": (
                "v(x)=1+integral_x^infinity "
                "(1-exp(2*I*omega*(x-s)))/(2*I*omega)"
                "*V(s)*v(s) ds"
            ),
            "uniform_phase_bound": (
                "|exp(-2*I*omega*exp(I*pi/4)*t)|"
                "<=exp(-sqrt(2)*delta*t)"
            ),
            "delta": frac_text(ecs_margin),
            "angle_uniformly_damped": True,
            "remaining_validation_gates": [
                (
                    "construct one analytic inverse-tortoise branch r(x) on "
                    "the pi/4 ray from the selected finite matching point"
                ),
                "prove that branch avoids r=0 and r=2",
                (
                    "enclose the complex potential integral and certify the "
                    "Volterra operator norm is below one"
                ),
                (
                    "bound the truncated-contour tail and transport the "
                    "resulting complex ball back to the matching radius"
                ),
            ],
        },
        "claim_flags": {
            "formal_recurrence_rederived_exactly": True,
            "R45_forward_tail_noncontractive_uniformly": True,
            "pi_over_4_ecs_phase_uniformly_damped": True,
            "infinity_asymptotic_remainder_enclosed": False,
            "ecs_inverse_tortoise_branch_certified": False,
            "ecs_volterra_contraction_certified": False,
            "complex_ball_outgoing_initializer_constructed": False,
            "Evans_boundary_nonzero_certified": False,
            "QNM_root_count_certified": False,
        },
        "does_not_establish": [
            (
                "divergence of every particular formal coefficient orbit; "
                "the theorem is a noncontractivity result for the naive "
                "independent forward-tail enclosure"
            ),
            "an infinity asymptotic remainder at R=45 or any other radius",
            "an exterior-complex-scaled analytic branch or Volterra contraction",
            "a complex-ball outgoing initializer or finite-interval transport",
            "Evans-function nonvanishing, a root count, a QNM or an EP2",
        ],
    }
    return document


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-infinity-tail-gate-receipt-v1",
        "producer": "produce.py",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "input_sha256": {
            "endpoint_germ_certificate": sha256(ENDPOINT),
            "noncertifying_seed_geometry": sha256(SEED),
            "noncertifying_shooting_source": sha256(SEED_SHOOTER),
        },
        "artifact_sha256": {
            name: sha256(HERE / name) for name in ARTIFACTS
        },
        "commands": [
            "python3 produce.py",
            "python3 verify.py",
            "python3 -m unittest -v test_infinity_tail_gate.py",
            "python3 -m py_compile produce.py verify.py test_infinity_tail_gate.py",
        ],
        "tier_2_not_run": (
            "No shared operator changed; the package independently audits "
            "one imported exact recurrence and disk geometry."
        ),
        "tier_3_not_run": "Not a freeze, release or physical theorem promotion.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
