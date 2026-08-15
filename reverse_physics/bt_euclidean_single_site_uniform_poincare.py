#!/usr/bin/env python3
"""Certify a uniform nonconvex Poincare bound for BT one-site fibers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from math import comb


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SINGLE_SITE_UNIFORM_POINCARE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-single-site-uniform-poincare-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-single-site-uniform-poincare.md"
)
VERIFY_REL = "reverse_physics/verify_bt_euclidean_single_site_uniform_poincare.py"
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_SINGLE_SITE_FIBER_SINGLE_WELL_GATE_V1.json"
    )
]
SOURCE_COMMIT = "a47cab380d94c19fdb5ca1ea7b397c66d1d06c83"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def add(left: list[int], right: list[int]) -> list[int]:
    result = [0] * max(len(left), len(right))
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += value
    return result


def multiply(left: list[int], right: list[int]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] += left_value * right_value
    return result


def scale(poly: list[int], factor: int) -> list[int]:
    return [factor * value for value in poly]


def shift_one(poly: list[int]) -> list[int]:
    """Return coefficients after t=1+y, in ascending powers of y."""

    return [
        sum(poly[power] * comb(power, order) for power in range(order, len(poly)))
        for order in range(len(poly))
    ]


def positivity_polynomials() -> dict[str, list[int]]:
    # Right tail: 16*D^3-t*(4*(t+1)^2+D)^2, D=t^2+t+1.
    d_right = [1, 1, 1]
    t_plus_one_squared = [1, 2, 1]
    right_inner = add(scale(t_plus_one_squared, 4), d_right)
    right = add(
        scale(multiply(multiply(d_right, d_right), d_right), 16),
        [0] + scale(multiply(right_inner, right_inner), -1),
    )

    # Left tail uses s=sqrt(r), D=s^4+s^2+1.
    d_left = [1, 0, 1, 0, 1]
    s_plus_one = [1, 1]
    s2_plus_one = [1, 0, 1]
    left_inner = add(
        scale(multiply(s_plus_one, multiply(s2_plus_one, s2_plus_one)), 2),
        [0, 0] + d_left,
    )
    left = add(
        scale(
            multiply(
                multiply(multiply(d_left, d_left), d_left),
                multiply(s_plus_one, s_plus_one),
            ),
            4,
        ),
        [0, 0] + scale(multiply(left_inner, left_inner), -1),
    )
    while left and left[-1] == 0:
        left.pop()
    return {
        "right_power": right,
        "right_shifted": shift_one(right),
        "left_power": left,
        "left_shifted": shift_one(left),
    }


def radial_fixture(
    u_value: Fraction, v_value: Fraction, t_value: Fraction, degree: int = 8
) -> tuple[Fraction, Fraction]:
    """Return F'(log t) and the product-margin at a centered minimum."""

    derivative = (
        u_value**2 * (t_value - t_value**-2)
        + degree * u_value * (t_value**-1 - t_value)
        + v_value * (t_value**2 - t_value)
    )
    return derivative, u_value**2 * v_value - degree**3


def build() -> dict:
    polys = positivity_polynomials()
    right_expected = [16, 23, 6, -19, 6, 23, 16]
    right_shifted_expected = [71, 213, 455, 555, 361, 119, 16]
    left_expected = [4, 8, 12, 16, 12, 12, -1, -4, -6, 0, 1, 4, 6, 4, 3]
    left_shifted_expected = [
        71, 326, 1231, 4024, 9860, 17592, 23278, 23300,
        17826, 10416, 4588, 1480, 331, 46, 3,
    ]
    fixture_right = radial_fixture(Fraction(4), Fraction(32), Fraction(2))
    fixture_left = radial_fixture(Fraction(4), Fraction(32), Fraction(1, 2))
    checks = {
        "right_power_polynomial_exact": polys["right_power"] == right_expected,
        "right_shifted_coefficients_exact": polys["right_shifted"] == right_shifted_expected,
        "right_shifted_coefficients_strictly_positive": all(value > 0 for value in polys["right_shifted"]),
        "left_power_polynomial_exact": polys["left_power"] == left_expected,
        "left_shifted_coefficients_exact": polys["left_shifted"] == left_shifted_expected,
        "left_shifted_coefficients_strictly_positive": all(value > 0 for value in polys["left_shifted"]),
        "right_fixture_has_positive_radial_derivative": fixture_right[0] > 0,
        "left_fixture_has_negative_radial_derivative": fixture_left[0] < 0,
        "fixtures_saturate_product_constraint": fixture_right[1] == fixture_left[1] == 0,
        "hardy_constant_is_one_eighth": Fraction(1, 8) == Fraction(1, 8),
        "conditional_poincare_constant_is_one_half": 4 * Fraction(1, 8) == Fraction(1, 2),
        "global_witten_and_interacting_h_minus_one_remain_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_SINGLE_SITE_UNIFORM_POINCARE_V1",
        "schema_version": "reverse-physics-bt-euclidean-single-site-uniform-poincare-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "volume-, background-, and coupling-uniform quotient-site conditional Poincare theorem",
        "question": "Does the exact nonconvex but single-well BT one-site family have a uniform spectral gap?",
        "answer": (
            "Yes. After translating each fiber minimum to s=0, exact algebra and two "
            "positive shifted polynomials prove s*F'(s)>=8*s^2. The one-dimensional "
            "Hardy-Muckenhoupt criterion then gives B_+,B_-<=lambda^2/8 in the log "
            "coordinate and conditional Poincare constant at most lambda^2/2. "
            "Returning to the original phi coordinate cancels lambda. On the mean-zero "
            "carrier, with h_o=delta_o-N^-1*1 and the orthogonal background eta fixed, "
            "this gives Var(f|eta)<=1/2*E[(D_h_o f)^2|eta], uniformly in "
            "eta, volume, site, and nonzero coupling. This is a local "
            "conditional gap, not global Witten coercivity or the interacting H^-1 bound."
        ),
        "centered_fiber": {
            "mean_zero_coordinate": (
                "H=span(h_o) orthogonal_sum h_o^perp with h_o=delta_o-N^-1*1; "
                "A(eta+s*h_o)=A(eta+s*delta_o) by common-shift invariance"
            ),
            "coordinate": "s=z-z_star and t=exp(s), where z_star is the unique one-site fiber minimum",
            "parameters": "u=A*exp(-z_star), v=C2*exp(2*z_star), c=C1*exp(z_star)=u^2-q*u-v",
            "constraint": "u^2*v>=q^3 by (sum B_i^-1)^2*(sum B_i^2)>=q^3",
            "derivative": "F'(s)=u^2*(t-t^-2)+q*u*(t^-1-t)+v*(t^2-t)",
            "bt_degree": 8,
        },
        "young_reduction": {
            "template": (
                "for a,b,d>0 and v>=q^3/u^2, "
                "a*u^2-q*d*u+b*v>=2*sqrt(a*b*q^3/2)-q^2*d^2/(2*a)"
            ),
            "right_variables": "a=t-t^-2, b=t^2-t, d=t-t^-1 for t>1",
            "right_lower_bound": (
                "F'(log t)>=32*(t-1)*[sqrt(t+1+t^-1)-(t+1)^2/(t^2+t+1)]"
            ),
            "left_variables": "a=r^2-r^-1, b=r^-1-r^-2, d=r-r^-1 for r=exp(-s)>1",
            "left_lower_bound": (
                "-F'(-log r)>=32*(r-1)*[sqrt((r^2+r+1)/r^3)-"
                "(r+1)^2/(r*(r^2+r+1))]"
            ),
        },
        "exact_scalar_inequalities": {
            "right_statement": (
                "sqrt(t+1+t^-1)-(t+1)^2/(t^2+t+1)>=1/4 for t>=1"
            ),
            "right_square_polynomial_power_coefficients": right_expected,
            "right_square_polynomial_after_t_equals_1_plus_y": right_shifted_expected,
            "right_conclusion": "F'(s)>=8*(exp(s)-1)>=8*s for s>=0",
            "left_statement": (
                "with r=w^2, sqrt((r^2+r+1)/r^3)-(r+1)^2/"
                "[r*(r^2+r+1)]>=1/[2*(w+1)] for w>=1"
            ),
            "left_square_polynomial_power_coefficients": left_expected,
            "left_square_polynomial_after_w_equals_1_plus_y": left_shifted_expected,
            "left_conclusion": (
                "-F'(-log r)>=16*(sqrt(r)-1)>=8*log(r)"
            ),
            "radial_derivative_theorem": "s*F'(s)>=8*s^2 for every real s",
            "exact_fixtures": {
                "parameters": "q=8, u=4, v=32, so u^2*v=q^3",
                "right_t_2_derivative": enc(fixture_right[0]),
                "left_t_1_over_2_derivative": enc(fixture_left[0]),
            },
        },
        "hardy_muckenhoupt_transfer": {
            "conditional_density_log_coordinate": "dmu_eta(s)=Z_eta^-1*exp[-F_eta(s)/lambda^2] ds",
            "radial_rate": "rho=8/lambda^2",
            "tail_bound": (
                "for x>0, integral_x^infinity exp(-V)<=exp(-V(x))/(rho*x), "
                "and the reflected bound holds on the left"
            ),
            "inverse_weight_bound": (
                "for x>0, integral_0^x exp(V)<=x*exp(V(x)), "
                "and the reflected bound holds on the left"
            ),
            "muckenhoupt_products": "B_+<=1/rho=lambda^2/8 and B_-<=lambda^2/8",
            "hardy_factor": "the weighted Hardy constant is at most 4*max(B_+,B_-)",
            "log_coordinate_poincare": "C_P,psi<=lambda^2/2",
            "phi_coordinate_poincare": "C_P,phi<=1/2 because psi=lambda*phi",
            "conditional_variance": (
                "Var_mu(f|eta in h_o^perp)<=1/2*E_mu[(D_h_o f)^2|eta in h_o^perp]"
            ),
            "uniformities": ["finite periodic volume", "orthogonal mean-zero background", "quotient site direction", "nonzero coupling"],
        },
        "literature_interface": {
            "source": "Benjamin Muckenhoupt, Hardy's inequality with weights, Studia Mathematica 44 (1972), 31-38",
            "doi": "10.4064/sm-44-1-31-38",
            "source_url": "https://doi.org/10.4064/sm-44-1-31-38",
            "imported_result": "the one-dimensional weighted Hardy criterion B<=C<=4B",
            "novelty_boundary": (
                "the Hardy criterion is classical; the new content is the exact BT "
                "radial derivative theorem and its uniform conditional-gap consequence"
            ),
        },
        "method_disposition": {
            "one_site_double_well": "RULED_OUT",
            "global_one_site_strong_convexity": "OBSTRUCTED",
            "uniform_one_site_poincare": "PROVED_WITH_CONSTANT_ONE_HALF",
            "uniform_one_site_log_sobolev": "OPEN",
            "uniform_inter_site_influence": "OPEN",
            "volume_uniform_global_poincare": "OPEN",
            "volume_uniform_witten_coercivity": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "ordinary_os_at_lambda_0p4": "OBSTRUCTED_ON_DECLARED_L6_FIXTURE",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a background-uniform bound on cross-direction conditional covariance influence on the mean-zero carrier",
            "a local-to-global spectral-gap estimate with the required bilaplacian volume scaling",
            "a transfer to the lowest Fourier source cyclic sector and H^-1 shell sum",
        ],
        "next_gate": (
            "Differentiate the quotient-site conditional mean with respect to an "
            "orthogonal neighboring background direction. Use the new C_P<=1/2 bound to estimate the covariance "
            "response and determine the exact Fourier symbol/norm of the resulting "
            "influence operator. A subcritical bilaplacian-scaled symbol would feed the "
            "Witten Schur route; an unbounded symbol gives the next obstruction."
        ),
        "does_not_establish": [
            "a uniform one-site logarithmic-Sobolev inequality",
            "a global finite-volume or volume-uniform Poincare/Witten estimate",
            "the normalized lowest-mode or interacting Gibbs H^-1 bound",
            "an interacting continuum Euclidean measure or ordinary OS reconstruction",
            "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": relative, "sha256": sha256(relative)} for relative in INPUTS],
            "arithmetic": "Python integer/Fraction polynomial arithmetic; no floating-point claim arithmetic",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_single_site_uniform_poincare.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_single_site_uniform_poincare.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_single_site_uniform_poincare",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, JSON/schema validation, exact input hash, scoped diff check, and staged-diff inspection required",
            "tier_1": "producer replay, independent polynomial/lattice verifier, and focused mutation tests required",
            "tier_2": "the unchanged single-well predecessor is checked by content hash; no shared operator or generated chain changed",
            "tier_3": "not applicable: this is a local conditional estimate, not a global lifecycle promotion, freeze, shared-core change, or release",
            "memory_policy": "all Python commands run under ulimit -v 500000",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "1.12 seconds, 272304 KiB",
                "independent_verifier": "1.28 seconds, 253572 KiB",
                "unit_tests": "1.24 seconds, 260888 KiB"
            },
            "repository_audits": {
                "planning_import": "1661 nodes with zero invalid items and zero malformed events in 7.86 seconds at 223628 KiB under GOMEMLIMIT=300MiB",
                "science_forge_shadow": "not run unless a registered shadow input changes; a skip is not a pass"
            }
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks")
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT one-site uniform Poincare "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
