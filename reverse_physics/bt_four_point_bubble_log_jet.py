#!/usr/bin/env python3
"""Exact BT two-quartic bubble logarithm and four-mass interference jet.

The logarithmic coefficient is reconstructed from the double-pole cut by
differentiating an ordinary massive two-body cut once in each internal mass.
It is then combined with the complete PS tree amplitude on a declared fixed
(s,t) external-virtuality carrier.  No triangle, box, finite rational part, or
phase-space boundary is included.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-four-point-bubble-log-jet-v1.schema.json"
)
REPORT_PATH = "reverse_physics/reports/bt-four-point-bubble-log-jet.md"
SOURCE_COMMIT = "91ed8128a0ee1e98ecf0be7b6f4b63c4a0cddba7"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def channel_cut_derivation():
    """Covariant angular moments followed by two internal-mass derivatives."""
    import sympy as sp

    S, T, xa, xb, xc, xd, y, z = sp.symbols(
        "S T xa xb xc xd y z", positive=True
    )
    aP = (S + xa - xb) / 2
    bP = (S - xa + xb) / 2
    cP = (-S - xc + xd) / 2
    dP = (-S + xc - xd) / 2
    A = (S - xa - xb) / 2
    C = (S - xc - xd) / 2
    ac = (T - xa - xc) / 2
    aperp2 = xa - aP ** 2 / S
    cperp2 = xc - cP ** 2 / S
    aperp_cperp = ac - aP * cP / S

    kallen_internal = (
        S ** 2 + y ** 2 + z ** 2 - 2 * S * y - 2 * S * z - 2 * y * z
    )
    alpha = (S + y - z) / (2 * S)
    left_constant = (
        A * (S - y - z) / 2 + 2 * alpha * (1 - alpha) * aP * bP
    )
    right_constant = (
        C * (S - y - z) / 2 + 2 * alpha * (1 - alpha) * cP * dP
    )
    left_linear = (2 * alpha - 1) * (aP - bP)
    right_linear = (2 * alpha - 1) * (cP - dP)

    aa = -kallen_internal * aperp2 / (12 * S)
    cc = -kallen_internal * cperp2 / (12 * S)
    ac_moment = -kallen_internal * aperp_cperp / (12 * S)
    fourth = (
        kallen_internal ** 2
        * (aperp2 * cperp2 + 2 * aperp_cperp ** 2)
        / (240 * S ** 2)
    )
    angular_average = sp.expand(
        left_constant * right_constant
        + 2 * right_constant * aa
        + 2 * left_constant * cc
        + left_linear * right_linear * ac_moment
        + 4 * fourth
    )
    ordinary_cut = sp.sqrt(kallen_internal) * angular_average / S
    double_pole_cut = sp.diff(ordinary_cut, y, z).subs({y: 0, z: 0})
    double_pole_cut = sp.factor(double_pole_cut)
    polynomial = sp.factor(12 * double_pole_cut)
    expected = (
        7 * S ** 2 + S * T + T ** 2
        - (7 * S + T) * (xa + xb + xc + xd)
        + xa * xb + xc * xd
        + 7 * (xa * xc + xa * xd + xb * xc + xb * xd)
    )
    return {
        "symbols": (S, T, xa, xb, xc, xd),
        "polynomial": polynomial,
        "expected": expected,
        "identity": sp.expand(polynomial - expected) == 0,
        "on_shell": sp.factor(polynomial.subs(
            {xa: 0, xb: 0, xc: 0, xd: 0}
        )),
    }


def interference_jet_derivation():
    """Sequential exact differentiation of tree times bubble logarithms."""
    import sympy as sp

    s, t = sp.symbols("s t", nonzero=True)
    x1, x2, x3, x4 = sp.symbols("x1 x2 x3 x4")
    xs = (x1, x2, x3, x4)
    total = sum(xs)
    u = total - s - t

    def kallen(a, b, c):
        return a ** 2 + b ** 2 + c ** 2 - 2 * a * b - 2 * a * c - 2 * b * c

    def cubic_end(channel, a, b):
        return kallen(channel, a, b) / 2

    quartic = (
        (s - x1 - x2) * (s - x3 - x4)
        + (t - x1 - x3) * (t - x2 - x4)
        + (u - x1 - x4) * (u - x2 - x3)
    ) / 4
    tree = (
        cubic_end(s, x1, x2) * cubic_end(s, x3, x4) / s ** 2
        + cubic_end(t, x1, x3) * cubic_end(t, x2, x4) / t ** 2
        + cubic_end(u, x1, x4) * cubic_end(u, x2, x3) / u ** 2
        - quartic
    )

    def cut_poly(S, T, a, b, c, d):
        return (
            7 * S ** 2 + S * T + T ** 2
            - (7 * S + T) * (a + b + c + d)
            + a * b + c * d + 7 * (a * c + a * d + b * c + b * d)
        )

    ps = cut_poly(s, t, x1, x2, x3, x4)
    pt = cut_poly(t, s, x1, x3, x2, x4)
    pu = cut_poly(u, s, x1, x4, x2, x3)
    ls, lt, lu = sp.symbols("Ls Lt Lu")
    log_u_jet = lu - sum(
        total ** degree / (sp.Integer(degree) * (s + t) ** degree)
        for degree in range(1, 5)
    )
    bubble_logs = ps * ls + pt * lt + pu * log_u_jet
    top = tree * bubble_logs
    for variable in xs:
        top = sp.diff(top, variable)
    top = sp.factor(top.subs(dict.fromkeys(xs, 0)))

    denominator = s ** 2 * t ** 2 * (s + t) ** 2
    numerator = sp.expand(top * denominator)
    return {
        "symbols": (s, t, ls, lt, lu),
        "tree": tree,
        "tree_on_shell": sp.factor(tree.subs(dict.fromkeys(xs, 0))),
        "top": top,
        "denominator": denominator,
        "numerator": numerator,
    }


def homogeneous_coefficients(polynomial, s, t):
    expanded = polynomial.as_poly(s, t)
    degree = expanded.total_degree()
    return [int(expanded.coeff_monomial(s ** (degree - k) * t ** k))
            for k in range(degree + 1)]


def build():
    import sympy as sp

    cut = channel_cut_derivation()
    jet = interference_jet_derivation()
    s, t, ls, lt, lu = jet["symbols"]
    numerator = jet["numerator"]
    log_rows = {
        "Ls": homogeneous_coefficients(sp.diff(numerator, ls), s, t),
        "Lt": homogeneous_coefficients(sp.diff(numerator, lt), s, t),
        "Lu": homogeneous_coefficients(sp.diff(numerator, lu), s, t),
        "rational": homogeneous_coefficients(
            numerator.subs({ls: 0, lt: 0, lu: 0}), s, t
        ),
    }
    expected_rows = {
        "Ls": [7, -13, -49, -19, -13, -1, 1],
        "Lt": [1, -1, -13, -19, -49, -13, 7],
        "Lu": [7, -1, -43, -67, -43, -1, 7],
        "rational": [0, -28, -59, -63, -59, -28, 0],
    }
    r, hard_log, ratio_log = sp.symbols("r L ell")
    collinear = jet["top"].subs({
        s: 1,
        t: r,
        ls: hard_log,
        lt: hard_log - ratio_log,
        lu: hard_log - sp.log(1 + r),
    })
    leading_two = sp.limit(r ** 2 * collinear, r, 0)
    leading_one = sp.limit(
        r * (collinear - leading_two / r ** 2), r, 0
    )
    finite = sp.limit(
        collinear - leading_two / r ** 2 - leading_one / r, r, 0
    )
    collinear_coefficients = [
        sp.factor(leading_two), sp.factor(leading_one), sp.factor(finite)
    ]
    expected_collinear = [
        15 * hard_log - ratio_log,
        -45 * hard_log + 3 * ratio_log - 35,
        8 * ratio_log - 30 * hard_log + sp.Rational(31, 2),
    ]
    physical_interference_prefactor = (
        2 * 4 * (sp.Rational(1, 4) * sp.Rational(8, 3))
    )
    channel_expected = cut["expected"]
    channel_polynomial = str(channel_expected).replace("**", "^").replace(" ", "")

    checks = {
        "covariant_double_mass_derivative_gives_channel_polynomial": cut["identity"],
        "on_shell_channel_matches_holdom": str(cut["on_shell"]) == "7*S**2 + S*T + T**2",
        "ps_tree_amplitude_vanishes_on_shell": jet["tree_on_shell"] == 0,
        "jet_denominator_is_expected": jet["denominator"] == s ** 2 * t ** 2 * (s + t) ** 2,
        "Ls_numerator_coefficients": log_rows["Ls"] == expected_rows["Ls"],
        "Lt_numerator_coefficients": log_rows["Lt"] == expected_rows["Lt"],
        "Lu_numerator_coefficients": log_rows["Lu"] == expected_rows["Lu"],
        "rational_numerator_coefficients": log_rows["rational"] == expected_rows["rational"],
        "collinear_expansion_coefficients": all(
            sp.expand(actual - expected) == 0
            for actual, expected in zip(collinear_coefficients, expected_collinear)
        ),
        "crossing_Ls_Lt_coefficients_reverse": log_rows["Ls"] == list(reversed(log_rows["Lt"])),
        "Lu_coefficients_are_s_t_symmetric": log_rows["Lu"] == list(reversed(log_rows["Lu"])),
        "rational_coefficients_are_s_t_symmetric": log_rows["rational"] == list(reversed(log_rows["rational"])),
        "physical_interference_prefactor_is_sixteen_thirds": (
            physical_interference_prefactor == sp.Rational(16, 3)
        ),
        "bubble_is_not_full_one_loop_answer": True,
        "real_virtual_matching_remains_open": True,
        "no_lorentzian_claim": True,
    }

    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1",
        "schema_version": "reverse-physics-bt-four-point-bubble-log-jet-v1",
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "two-quartic one-loop logarithmic interference jet",
        "question": (
            "What four-external-mass logarithmic jet is supplied by the complete "
            "two-quartic bubble sector of the PS one-loop four-point amplitude?"
        ),
        "answer": (
            "The arbitrary-mass double-pole cut is a compact quadratic polynomial. "
            "Combining its three crossed logarithms with the exact PS tree amplitude "
            "gives a nonzero closed four-mass interference jet. It is singular in the "
            "collinear limit, so triangle and box sectors must participate before any "
            "comparison with the real -3/8 threshold coefficient."
        ),
        "declared_carrier": {
            "kinematics": (
                "four all-incoming external momenta; x_i=p_i^2 independent; s=(p1+p2)^2 "
                "and t=(p1+p3)^2 fixed; u=sum_i(x_i)-s-t"
            ),
            "jet_ring": "Q(s,t,Ls,Lt,Lu)[x1,x2,x3,x4]/(x1^2,x2^2,x3^2,x4^2)",
            "logarithms": [
                "Ls=log(mu^2/s)",
                "Lt=log(-mu^2/t)",
                "Lu=log(mu^2/(s+t)) at x_i=0",
            ],
            "hard_region": "s*t*(s+t) is nonzero",
            "scope": "fixed-(s,t) amplitude/interference jet before external phase-space differentiation",
        },
        "double_pole_cut": {
            "construction": (
                "Start with internal masses y,z, integrate the ordinary two-body "
                "angular polynomial, include sqrt(Kallen(S,y,z))/S, then apply d_y d_z at y=z=0."
            ),
            "channel_assignment": (
                "(a,b)|(c,d), S=(a+b)^2=(c+d)^2, T=(a+c)^2, xj=pj^2"
            ),
            "channel_polynomial": (
                "P=7*S^2+S*T+T^2-(7*S+T)*(xa+xb+xc+xd)+xa*xb+xc*xd"
                "+7*(xa*xc+xa*xd+xb*xc+xb*xd)"
            ),
            "producer_canonical_polynomial": channel_polynomial,
            "cut_normalization": "d_y*d_z ordinary_cut = P/12 for physical S>0",
            "on_shell_control": "P|x=0=7*S^2+S*T+T^2",
            "holdom_log_calibration": (
                "Gamma_bubble_log=lambda4^2/(4*pi)^2*(8/3)*sum_channels(P_channel*L_channel)"
            ),
        },
        "ps_tree_amplitude": {
            "reduced_definition": (
                "Mtree_red=sum_channels[Kallen(S,xa,xb)*Kallen(S,xc,xd)/(4*S^2)]-Q4"
            ),
            "physical_normalization": "Mtree=4*lambda^2*Mtree_red",
            "on_shell_value": "0",
        },
        "bubble_log_interference_jet": {
            "definition": "J=[x1*x2*x3*x4](Mtree_red*(Ps*Ls+Pt*Lt+Pu*Lu(x)))",
            "denominator": "s^2*t^2*(s+t)^2",
            "numerator_basis": "coefficient lists multiply s^(6-k)*t^k for k=0,...,6",
            "numerator_coefficients": log_rows,
            "physical_normalization": (
                "[x1*x2*x3*x4] 2*Re(Mtree^* Mloop_bubble_log)"
                "=lambda^6/(4*pi)^2*(16/3)*J"
            ),
            "nonzero": True,
        },
        "collinear_expansion": {
            "variables": (
                "r=t/s, L=log(mu^2/s), ell=log(-t/s); Lt=L-ell, Lu=L-log(1+r)"
            ),
            "reduced_J": (
                "J=(15*L-ell)/r^2+(-45*L+3*ell-35)/r"
                "+(8*ell-30*L+31/2)+O(r)"
            ),
            "physical_prefactor": "multiply by 16/3 and lambda^6/(4*pi)^2",
            "interpretation": (
                "The bubble sector alone contains collinear logarithms enhanced by "
                "r^-2 and r^-1; it cannot be compared directly with the integrated real threshold."
            ),
        },
        "disposition": {
            "arbitrary_mass_bubble_log_polynomial": "COMPUTED",
            "fixed_st_four_mass_bubble_interference_jet": "COMPUTED",
            "bubble_finite_rational_part": "NOT_COMPUTED",
            "triangle_sector": "NOT_COMPUTED",
            "box_sector": "NOT_COMPUTED",
            "external_phase_space_projector": "NOT_APPLIED",
            "real_virtual_collinear_cancellation": "NOT_COMPUTED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "the two-cubic one-quartic triangle logarithmic and finite jet",
            "the four-cubic box logarithmic and finite jet",
            "the bubble finite rational and counterterm jet",
            "wave-function and lower-point insertion contributions to the connected amplitude",
            "one common non-mass infrared prescription across real and virtual terms",
            "the differentiated external phase-space density and moving boundaries",
            "the complete virtual coefficient in the real threshold normalization",
        ],
        "next_gate": (
            "Compute the triangle logarithmic four-mass jet and test whether its "
            "r^-2 and r^-1 coefficients cancel the bubble values before attempting the finite box."
        ),
        "does_not_establish": [
            "the complete renormalized one-loop four-point PS amplitude",
            "the finite bubble sector",
            "the triangle or box contribution",
            "cancellation of the bubble's collinear powers",
            "a virtual coefficient opposite to the real reduced coefficient -3/8",
            "a KLN cancellation, canonical finite part, or physical NLO probability",
            "positivity or unitarity beyond tree level",
            "a common regulator, resummation, or dressed asymptotic state",
            "a tensor/BRST gravitational lift or anything LORENTZIAN-CAUSAL",
            "literature priority for the off-shell bubble polynomial",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-09",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_sources": [
                {
                    "source": "Bateman--Turok arXiv:2607.00096v1",
                    "equations": ["Eq. (2)", "Eqs. (24)-(26)"],
                    "use": "PS action, cubic/quartic vertices, and tree graph signs",
                },
                {
                    "source": "Holdom arXiv:2303.06723",
                    "equations": ["Eq. (22)"],
                    "use": "on-shell two-quartic logarithm and normalization control",
                },
                {
                    "source": "Holdom arXiv:2402.09223",
                    "equations": ["Eqs. (8)-(12)"],
                    "use": "mass-derivative representation of double propagators and cuts",
                },
            ],
        },
        "verification_commands": [
            "python3 reverse_physics/bt_four_point_bubble_log_jet.py --check",
            "python3 reverse_physics/verify_bt_four_point_bubble_log_jet.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_four_point_bubble_log_jet",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT_PATH,
        "schema": SCHEMA_PATH,
    }
    return certificate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CERT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] recorded_certificate: {exc}")
            return 1
        ok = recorded == certificate
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(f"RESULT: {'PASS' if ok else 'FAIL'} "
              f"({certificate['checks']['passed']}/{certificate['checks']['total']})")
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
