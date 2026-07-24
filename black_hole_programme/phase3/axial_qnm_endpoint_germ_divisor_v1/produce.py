#!/usr/bin/env python3
"""Produce exact scalar RW endpoint recurrences and seed-disk divisor audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md",
    "report.md",
    "schema.json",
    "produce.py",
    "verify.py",
    "test_endpoint_germs.py",
)
INPUTS = {
    "rw_factor": (
        ROOT / "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
    "noncertifying_seed": (
        ROOT / "black_hole_programme/phase3/"
        "axial_qnm_contour_seed_preflight_v1/"
        "qnm_contour_diagnostic.json"
    ),
}

Q, R, W = sp.symbols("q r omega")
I = sp.I


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(sp.together(value)))


def encode(value: sp.Expr) -> str:
    return sp.sstr(exact(value))


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def coefficients(value: sp.Expr) -> list[str]:
    poly = sp.Poly(sp.expand(value), Q)
    degree = poly.degree()
    return [encode(poly.nth(index)) for index in range(degree + 1)]


def conjugated_equation(
    d_coefficient: sp.Expr,
    logarithmic_derivative: sp.Expr,
    potential: sp.Expr,
    multiplier: sp.Expr,
) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """Return coefficients of P'', P', P after y=hP and multiplication."""
    g = d_coefficient
    ell = logarithmic_derivative
    a = exact(multiplier * g**2)
    b = exact(multiplier * (g * sp.diff(g, Q) + 2 * g**2 * ell))
    c = exact(
        multiplier
        * (
            g * sp.diff(g, Q) * ell
            + g**2 * (sp.diff(ell, Q) + ell**2)
            + potential
        )
    )
    return a, b, c


def produce() -> dict:
    rw_document = json.loads(INPUTS["rw_factor"].read_text())
    rw = rw_document["operators"]["L_RW"]
    f_r = (R - 2) / R
    potential_r = 6 * (R - 2) * (R - 1) / R**4
    expected_a = exact(sp.diff(f_r, R) / f_r + 2 * I * W / f_r)
    expected_b = exact(-potential_r / f_r**2)
    if exact(parse(rw["a"]) - expected_a) != 0:
        raise RuntimeError("imported RW first-derivative coefficient drift")
    if exact(parse(rw["b"]) - expected_b) != 0:
        raise RuntimeError("imported RW potential coefficient drift")

    seed = json.loads(INPUTS["noncertifying_seed"].read_text())
    center_re = sp.Rational(seed["center"][0])
    center_im = sp.Rational(seed["center"][1])
    radius = sp.Rational(seed["radius"])
    re_margin = exact(-center_re - radius)
    im_margin = exact(center_im - radius)
    if not (re_margin > 0 and im_margin > 0):
        raise RuntimeError("seed disk is not strictly in quadrant II")

    # Horizon coordinate q=1-2/r, D=q(1-q)^2/2 d_q, and
    # y=q^(2 i omega) P_H(q).
    r_h = 2 / (1 - Q)
    u_h = exact(W**2 - potential_r.subs(R, r_h))
    g_h = Q * (1 - Q)**2 / 2
    ell_h = 2 * I * W / Q
    a_h, b_h, c_h = conjugated_equation(
        g_h, ell_h, u_h, 4 / Q
    )

    # Infinity coordinate q=1/r, D=-(1-2q)q^2 d_q, and
    # y=exp(-i omega/q) q^(2 i omega) P_I(q).
    r_i = 1 / Q
    u_i = exact(W**2 - potential_r.subs(R, r_i))
    g_i = -(1 - 2 * Q) * Q**2
    ell_i = I * W / Q**2 + 2 * I * W / Q
    a_i, b_i, c_i = conjugated_equation(
        g_i, ell_i, u_i, 1 / Q**2
    )

    n = sp.symbols("n", integer=True, nonnegative=True)
    horizon_divisor = exact(
        sp.Poly(a_h, Q).nth(1) * (n + 1) * n
        + sp.Poly(b_h, Q).nth(0) * (n + 1)
    )
    infinity_divisor = exact(
        sp.Poly(a_i, Q).nth(1) * (n + 1) * n
        + sp.Poly(b_i, Q).nth(0) * (n + 1)
    )
    if horizon_divisor != (n + 1) * (n + 1 + 4 * I * W):
        raise RuntimeError("horizon recurrence divisor drift")
    if infinity_divisor != 2 * I * W * (n + 1):
        raise RuntimeError("infinity recurrence divisor drift")

    document = {
        "schema": "phase3-axial-qnm-endpoint-germ-divisor-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "EXACT_RECURRENCES_AND_DIVISOR_CLEARANCE_"
            "NO_GERM_REMAINDER_NO_ROOT_COUNT"
        ),
        "scope": {
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2 scalar spin-two Regge-Wheeler factor",
            "time_convention": "exp(+I*omega*t)",
            "operator": "D**2+(omega**2-V2)",
            "D": "((r-2)/r)*D_r",
            "V2": "6*(r-2)*(r-1)/r**4",
        },
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
                "authority": (
                    "exact input"
                    if name == "rw_factor"
                    else "noncertifying contour geometry only"
                ),
            }
            for name, path in INPUTS.items()
        },
        "seed_disk": {
            "center_re": str(center_re),
            "center_im": str(center_im),
            "radius": str(radius),
            "closed_disk": "|omega-(center_re+I*center_im)|<=radius",
            "strict_left_half_plane_margin": str(re_margin),
            "strict_upper_half_plane_margin": str(im_margin),
            "proof": (
                "Re(omega)<=center_re+radius=-left_margin<0 and "
                "Im(omega)>=center_im-radius=upper_margin>0"
            ),
        },
        "horizon_germ": {
            "coordinate": "q=1-2/r",
            "factor": "q**(2*I*omega)",
            "branch": "real q>0 with the real logarithm",
            "reduced_equation": "A*P''+B*P'+C*P=0",
            "A": encode(a_h),
            "B": encode(b_h),
            "C": encode(c_h),
            "A_coefficients_low_to_high": coefficients(a_h),
            "B_coefficients_low_to_high": coefficients(b_h),
            "C_coefficients_low_to_high": coefficients(c_h),
            "coefficient_rule": (
                "sum_j A_j*(m-j+2)*(m-j+1)*h_(m-j+2)"
                "+sum_j B_j*(m-j+1)*h_(m-j+1)"
                "+sum_j C_j*h_(m-j)=0; h_k=0 for k<0"
            ),
            "solved_coefficient": "h_(m+1)",
            "divisor": encode(horizon_divisor),
            "zero_locus": "omega=I*(n+1)/4, n>=0",
            "uniform_modulus_lower_bound": (
                f"(n+1)*4*({re_margin})"
            ),
            "lower_bound_reason": (
                "|n+1+4*I*omega|>=4*|Re(omega)|"
            ),
            "analytic_status": (
                "nonresonant local Frobenius germ exists uniquely after "
                "fixing h_0; no quantitative tail enclosure is supplied"
            ),
        },
        "infinity_germ": {
            "coordinate": "q=1/r",
            "factor": "exp(-I*omega/q)*q**(2*I*omega)",
            "branch": "real q>0 with the real logarithm",
            "reduced_equation": "A*P''+B*P'+C*P=0",
            "A": encode(a_i),
            "B": encode(b_i),
            "C": encode(c_i),
            "A_coefficients_low_to_high": coefficients(a_i),
            "B_coefficients_low_to_high": coefficients(b_i),
            "C_coefficients_low_to_high": coefficients(c_i),
            "coefficient_rule": (
                "sum_j A_j*(m-j+2)*(m-j+1)*g_(m-j+2)"
                "+sum_j B_j*(m-j+1)*g_(m-j+1)"
                "+sum_j C_j*g_(m-j)=0; g_k=0 for k<0"
            ),
            "solved_coefficient": "g_(m+1)",
            "divisor": encode(infinity_divisor),
            "zero_locus": "omega=0",
            "uniform_modulus_lower_bound": (
                f"2*(n+1)*({re_margin})"
            ),
            "lower_bound_reason": "|2*I*omega*(n+1)|>=2*(n+1)*|Re(omega)|",
            "series_kind": "formal outgoing inverse-r asymptotic series",
        },
        "noncollision_audit": {
            "purely_imaginary_events_excluded_by_left_margin": [
                "omega=0",
                "omega=I*(n+1)/4 for every integer n>=0",
                "omega=I/4",
                "omega=I/2",
                "omega=I",
                "omega=2*I",
            ],
            "projective_witness_events_excluded": [
                "omega**2=3 because Im(omega)>0 and Re(omega)<0",
                "omega**2=-4 because Re(omega)<0",
            ],
            "moving_radial_divisor": "r*omega-2*I",
            "moving_radial_divisor_domain": "real r>=2",
            "moving_radial_divisor_lower_bound": (
                f"r*({re_margin})"
            ),
            "moving_radial_divisor_proof": (
                "|r*omega-2*I|>=r*|Re(omega)|"
            ),
            "frame_factors": {
                "2*omega-I": f">=2*({re_margin})",
                "4*omega-I": f">=4*({re_margin})",
                "omega-I": f">=({re_margin})",
            },
        },
        "claim_flags": {
            "endpoint_reduced_equations_exact": True,
            "endpoint_formal_recurrence_divisors_exact": True,
            "seed_disk_divisor_noncollision_exact": True,
            "horizon_nonresonant_frobenius_germ_exists": True,
            "horizon_convergent_germ_remainder_enclosed": False,
            "infinity_asymptotic_remainder_enclosed": False,
            "complex_ball_endpoint_columns_constructed": False,
            "Evans_boundary_nonzero_certified": False,
            "QNM_root_count_certified": False,
            "QNM_enclosed": False,
            "beta_or_EP2_established": False,
        },
        "does_not_establish": [
            "convergence or a tail bound for the horizon recurrence",
            "an outgoing infinity germ with a validated asymptotic remainder",
            "a complex-ball ODE transport or matching determinant",
            "nonvanishing of an Evans function on the seed contour",
            "an argument-principle root count or a simple QNM",
            "the intrinsic tangent b, beta_n, a Smith branch or an EP2",
        ],
    }
    return document


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-endpoint-germ-divisor-receipt-v1",
        "producer": "produce.py",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "input_sha256": {
            name: sha256(path) for name, path in INPUTS.items()
        },
        "artifact_sha256": {
            name: sha256(HERE / name) for name in ARTIFACTS
        },
        "commands": [
            "python3 produce.py",
            "python3 verify.py",
            "python3 -m unittest -v test_endpoint_germs.py",
        ],
        "tier_2_not_run": (
            "No mathematical input or shared operator changed; this package "
            "audits an existing exact scalar factor and noncertifying disk."
        ),
        "tier_3_not_run": "Not a freeze, theorem promotion, or release.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
