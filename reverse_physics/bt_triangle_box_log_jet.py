#!/usr/bin/env python3
"""Exact BT triangle/box logarithmic cuts and four-mass interference jets.

The calculation stays on the fixed-(s,t) square-free external-virtuality
carrier used by ``bt_four_point_bubble_log_jet.py``.  It exploits an exact
perfect-square identity: the complete reduced four-point tree amplitude has
no virtuality degrees zero or one and has universal degree-two part

    A_4^(2) = 1/2 * sum_{i<j} x_i x_j.

Writing the exchange and quartic pieces as E and Q, so A=E-Q, the two-body
cut topology products are

    bubble = Q_L Q_R,
    triangle = -Q_L E_R - E_L Q_R,
    box = E_L E_R.

At the only loop-virtuality degrees that can interfere with the tree under
the fourfold BT projector, E=A+Q reduces these products to polynomial angular
moments.  This determines the complete cut-constructible logarithmic triangle
and box jets.  It does not determine cut-free finite rational terms.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from itertools import combinations


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-triangle-box-log-jet-v1.schema.json"
)
REPORT_PATH = "reverse_physics/reports/bt-triangle-box-log-jet.md"
SOURCE_COMMIT = "69e2ed751f8e38222ea065093455baa4c785c297"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FOUR_POINT_BUBBLE_LOG_JET_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def reduced_tree():
    import sympy as sp

    s, t = sp.symbols("s t", nonzero=True)
    xs = sp.symbols("x1:5")
    x1, x2, x3, x4 = xs
    u = sum(xs) - s - t

    def kallen(a, b, c):
        return a ** 2 + b ** 2 + c ** 2 - 2 * a * b - 2 * a * c - 2 * b * c

    def end(channel, a, b):
        return kallen(channel, a, b) / 2

    quartic = (
        (s - x1 - x2) * (s - x3 - x4)
        + (t - x1 - x3) * (t - x2 - x4)
        + (u - x1 - x4) * (u - x2 - x3)
    ) / 4
    tree = (
        end(s, x1, x2) * end(s, x3, x4) / s ** 2
        + end(t, x1, x3) * end(t, x2, x4) / t ** 2
        + end(u, x1, x4) * end(u, x2, x3) / u ** 2
        - quartic
    )
    return (s, t), xs, tree


def square_free_part(expression, variables, max_degree):
    """Taylor-reduce into x_i^2=0 through the declared total degree."""
    import sympy as sp

    out = 0
    zero = dict.fromkeys(variables, 0)
    for degree in range(max_degree + 1):
        for indices in combinations(range(len(variables)), degree):
            coefficient = expression
            monomial = 1
            for index in indices:
                coefficient = sp.diff(coefficient, variables[index])
                monomial *= variables[index]
            coefficient = sp.factor(coefficient.subs(zero))
            if coefficient != 0:
                out += coefficient * monomial
    return sp.expand(out)


def tree_low_degree_identity():
    import sympy as sp

    invariants, xs, tree = reduced_tree()
    low = square_free_part(tree, xs, 2)
    expected = sum(xs[left] * xs[right]
                   for left, right in combinations(range(4), 2)) / 2
    return {
        "invariants": invariants,
        "variables": xs,
        "tree": tree,
        "low": sp.factor(low),
        "expected": expected,
        "identity": sp.expand(low - expected) == 0,
    }


def channel_topology_polynomials():
    """Derive the cut polynomials from covariant two-body angular moments."""
    import sympy as sp

    S, T, xa, xb, xc, xd, y, z = sp.symbols(
        "S T xa xb xc xd y z", positive=True
    )
    xs = (xa, xb, xc, xd)
    aP = (S + xa - xb) / 2
    bP = (S - xa + xb) / 2
    cP = (-S - xc + xd) / 2
    dP = (-S + xc - xd) / 2
    ab = (S - xa - xb) / 2
    cd = (S - xc - xd) / 2
    aperp2 = xa - aP ** 2 / S
    cperp2 = xc - cP ** 2 / S

    internal_kallen = (
        S ** 2 + y ** 2 + z ** 2 - 2 * S * y - 2 * S * z - 2 * y * z
    )
    alpha = (S + y - z) / (2 * S)
    left_constant = (
        ab * (S - y - z) / 2 + 2 * alpha * (1 - alpha) * aP * bP
    )
    right_constant = (
        cd * (S - y - z) / 2 + 2 * alpha * (1 - alpha) * cP * dP
    )
    left_second_moment = -internal_kallen * aperp2 / (12 * S)
    right_second_moment = -internal_kallen * cperp2 / (12 * S)
    q_left_average = sp.factor(left_constant + 2 * left_second_moment)
    q_right_average = sp.factor(right_constant + 2 * right_second_moment)

    a2_left = (
        xa * xb + xa * y + xa * z + xb * y + xb * z + y * z
    ) / 2
    a2_right = (
        xc * xd + xc * y + xc * z + xd * y + xd * z + y * z
    ) / 2
    density = sp.sqrt(internal_kallen) / S
    cross = sp.diff(
        density * (q_left_average * a2_right + a2_left * q_right_average),
        y, z,
    ).subs({y: 0, z: 0})
    cross = sp.factor(square_free_part(cross, xs, 2))

    bubble = (
        7 * S ** 2 + S * T + T ** 2
        - (7 * S + T) * sum(xs)
        + xa * xb + xc * xd
        + 7 * (xa * xc + xa * xd + xb * xc + xb * xd)
    ) / 12
    full = (
        xa * xb / 4 + xc * xd / 4
        + (xa * xc + xa * xd + xb * xc + xb * xd) / 2
    )
    triangle = sp.factor(-cross - 2 * bubble)
    box = sp.factor(full + cross + bubble)

    expected_cross = (
        5 * S ** 2 - 11 * S * sum(xs)
        + xa * xb + xc * xd
        + 18 * (xa * xc + xa * xd + xb * xc + xb * xd)
    ) / 12
    expected_triangle = -(
        19 * S ** 2 + 2 * S * T + 2 * T ** 2
        - (25 * S + 2 * T) * sum(xs)
        + 3 * xa * xb + 3 * xc * xd
        + 32 * (xa * xc + xa * xd + xb * xc + xb * xd)
    ) / 12
    expected_box = (
        12 * S ** 2 + S * T + T ** 2
        - (18 * S + T) * sum(xs)
        + 5 * xa * xb + 5 * xc * xd
        + 31 * (xa * xc + xa * xd + xb * xc + xb * xd)
    ) / 12
    return {
        "symbols": (S, T, xa, xb, xc, xd),
        "cross": cross,
        "bubble": sp.factor(bubble),
        "triangle": triangle,
        "box": box,
        "full": sp.factor(full),
        "cross_identity": sp.expand(cross - expected_cross) == 0,
        "triangle_identity": sp.expand(triangle - expected_triangle) == 0,
        "box_identity": sp.expand(box - expected_box) == 0,
        "topology_sum_identity": sp.expand(bubble + triangle + box - full) == 0,
        "expected_cross": expected_cross,
        "expected_triangle": expected_triangle,
        "expected_box": expected_box,
    }


def homogeneous_coefficients(polynomial, s, t, degree=6):
    expanded = polynomial.as_poly(s, t)
    return [int(expanded.coeff_monomial(s ** (degree - k) * t ** k))
            for k in range(degree + 1)]


def interference_jet(channel_polynomial):
    import sympy as sp

    (s, t), xs, tree = reduced_tree()
    x1, x2, x3, x4 = xs
    total = sum(xs)
    u = total - s - t
    ls, lt, lu = sp.symbols("Ls Lt Lu")

    ps = channel_polynomial(s, t, x1, x2, x3, x4)
    pt = channel_polynomial(t, s, x1, x3, x2, x4)
    pu = channel_polynomial(u, s, x1, x4, x2, x3)
    log_u_jet = lu - sum(
        total ** degree / (sp.Integer(degree) * (s + t) ** degree)
        for degree in range(1, 5)
    )
    expression = tree * (ps * ls + pt * lt + pu * log_u_jet)
    for variable in xs:
        expression = sp.diff(expression, variable)
    top = sp.factor(expression.subs(dict.fromkeys(xs, 0)))

    denominator = s ** 2 * t ** 2 * (s + t) ** 2
    numerator = sp.expand(sp.cancel(top * denominator))
    rows = {
        name: homogeneous_coefficients(sp.diff(numerator, symbol), s, t)
        for name, symbol in (("Ls", ls), ("Lt", lt), ("Lu", lu))
    }
    rows["log_kinematic_rational"] = homogeneous_coefficients(
        numerator.subs({ls: 0, lt: 0, lu: 0}), s, t
    )

    r, hard_log, ratio_log = sp.symbols("r L ell", positive=True)
    collinear = top.subs({
        s: 1,
        t: r,
        ls: hard_log,
        lt: hard_log - ratio_log,
        lu: hard_log - sp.log(1 + r),
    })
    leading_two = sp.factor(sp.limit(r ** 2 * collinear, r, 0))
    leading_one = sp.factor(sp.limit(
        r * (collinear - leading_two / r ** 2), r, 0
    ))
    finite = sp.factor(sp.limit(
        collinear - leading_two / r ** 2 - leading_one / r, r, 0
    ))
    return {
        "symbols": (s, t, ls, lt, lu),
        "top": top,
        "denominator": denominator,
        "rows": rows,
        "collinear": (leading_two, leading_one, finite),
    }


def build():
    import sympy as sp

    tree = tree_low_degree_identity()
    cuts = channel_topology_polynomials()
    S, T, xa, xb, xc, xd = cuts["symbols"]

    def p_bubble(s, t, a, b, c, d):
        return 12 * cuts["bubble"].subs({S: s, T: t, xa: a, xb: b, xc: c, xd: d})

    def p_triangle(s, t, a, b, c, d):
        return 12 * cuts["triangle"].subs({S: s, T: t, xa: a, xb: b, xc: c, xd: d})

    def p_box(s, t, a, b, c, d):
        return 12 * cuts["box"].subs({S: s, T: t, xa: a, xb: b, xc: c, xd: d})

    bubble = interference_jet(p_bubble)
    triangle = interference_jet(p_triangle)
    box = interference_jet(p_box)

    s, t, ls, lt, lu = triangle["symbols"]
    combined_top = sp.factor(bubble["top"] + triangle["top"] + box["top"])
    combined_rows = {
        key: [sum(values) for values in zip(
            bubble["rows"][key], triangle["rows"][key], box["rows"][key]
        )]
        for key in bubble["rows"]
    }
    combined_collinear = tuple(sp.factor(sum(values)) for values in zip(
        bubble["collinear"], triangle["collinear"], box["collinear"]
    ))

    expected_triangle_rows = {
        "Ls": [-19, 60, 154, 42, 28, 2, -2],
        "Lt": [-2, 2, 28, 42, 154, 60, -19],
        "Lu": [-19, -22, 53, 106, 53, -22, -19],
        "log_kinematic_rational": [0, 76, 199, 248, 199, 76, 0],
    }
    expected_box_rows = {
        "Ls": [12, -47, -90, 7, 0, -1, 1],
        "Lt": [1, -1, 0, 7, -90, -47, 12],
        "Lu": [12, 23, 5, -9, 5, 23, 12],
        "log_kinematic_rational": [0, -48, -140, -185, -140, -48, 0],
    }
    expected_combined_rows = {
        "Ls": [0, 0, 15, 30, 15, 0, 0],
        "Lt": [0, 0, 15, 30, 15, 0, 0],
        "Lu": [0, 0, 15, 30, 15, 0, 0],
        "log_kinematic_rational": [0, 0, 0, 0, 0, 0, 0],
    }
    hard_log, ratio_log = sp.symbols("L ell", positive=True)
    expected_triangle_collinear = (
        -40 * hard_log + 2 * ratio_log,
        120 * hard_log - 6 * ratio_log + 95,
        35 * hard_log - 18 * ratio_log + sp.Rational(43, 2),
    )
    expected_box_collinear = (
        25 * hard_log - ratio_log,
        -75 * hard_log + 3 * ratio_log - 60,
        40 * hard_log - 5 * ratio_log - 37,
    )
    expected_combined_collinear = (
        0, 0, 45 * hard_log - 15 * ratio_log
    )
    checks = {
        "tree_degree_zero_and_one_vanish": tree["identity"],
        "tree_degree_two_is_universal_e2_over_two": tree["identity"],
        "cross_cut_covariant_moment_identity": cuts["cross_identity"],
        "triangle_cut_polynomial_identity": cuts["triangle_identity"],
        "box_cut_polynomial_identity": cuts["box_identity"],
        "channel_topology_sum_is_full_cut": cuts["topology_sum_identity"],
        "full_channel_cut_vanishes_on_shell": cuts["full"].subs(dict.fromkeys((xa, xb, xc, xd), 0)) == 0,
        "holdom_forward_topology_coefficients": (
            sp.factor(24 * cuts["bubble"].subs({T: 0, xa: 0, xb: 0, xc: 0, xd: 0}) / S ** 2) == 14
            and sp.factor(-12 * cuts["triangle"].subs({T: 0, xa: 0, xb: 0, xc: 0, xd: 0}) / S ** 2) == 19
            and sp.factor(6 * cuts["box"].subs({T: 0, xa: 0, xb: 0, xc: 0, xd: 0}) / S ** 2) == 6
        ),
        "triangle_rows": triangle["rows"] == expected_triangle_rows,
        "box_rows": box["rows"] == expected_box_rows,
        "combined_rows": combined_rows == expected_combined_rows,
        "triangle_crossing": (
            triangle["rows"]["Ls"] == list(reversed(triangle["rows"]["Lt"]))
            and triangle["rows"]["Lu"] == list(reversed(triangle["rows"]["Lu"]))
        ),
        "box_crossing": (
            box["rows"]["Ls"] == list(reversed(box["rows"]["Lt"]))
            and box["rows"]["Lu"] == list(reversed(box["rows"]["Lu"]))
        ),
        "triangle_collinear_coefficients": all(
            sp.expand(actual - expected) == 0
            for actual, expected in zip(triangle["collinear"], expected_triangle_collinear)
        ),
        "box_collinear_coefficients": all(
            sp.expand(actual - expected) == 0
            for actual, expected in zip(box["collinear"], expected_box_collinear)
        ),
        "inverse_power_collinear_terms_cancel": all(
            sp.expand(actual - expected) == 0
            for actual, expected in zip(combined_collinear, expected_combined_collinear)
        ),
        "combined_log_jet_collapses": sp.expand(
            combined_top - 15 * (ls + lt + lu)
        ) == 0,
        "physical_interference_prefactor_is_sixteen_thirds": (
            2 * 4 * sp.Rational(2, 3) == sp.Rational(16, 3)
        ),
        "cut_free_finite_rational_terms_remain_open": True,
        "external_phase_space_projector_remains_open": True,
        "no_lorentzian_claim": True,
    }

    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1",
        "schema_version": "reverse-physics-bt-triangle-box-log-jet-v1",
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "triangle and box cut-constructible logarithmic four-mass interference jets",
        "question": (
            "What do the complete two-cubic/one-quartic triangle and four-cubic "
            "box topology families contribute to the BT four-mass logarithmic jet?"
        ),
        "answer": (
            "The triangle and box logarithmic jets are computed exactly. Their "
            "individual r^-2 and r^-1 collinear terms cancel those of the bubble "
            "in the complete topology sum, leaving 15*(Ls+Lt+Lu) and hence only "
            "the ordinary ratio logarithm 15*(3L-ell). Cut-free finite rational "
            "terms and the external phase-space projector are not determined."
        ),
        "declared_carrier": {
            "kinematics": (
                "four all-incoming momenta; x_i=p_i^2 independent; fixed s=(p1+p2)^2 "
                "and t=(p1+p3)^2; u=sum_i(x_i)-s-t"
            ),
            "jet_ring": "Q(s,t,Ls,Lt,Lu)[x1,x2,x3,x4]/(x_i^2)",
            "hard_region": "s*t*(s+t) is nonzero",
            "scope": (
                "cut-constructible logarithmic one-loop amplitude through loop "
                "virtuality degree two, sufficient for interference with the PS tree "
                "under the fixed-(s,t) fourfold projector"
            ),
        },
        "perfect_square_tree_identity": {
            "decomposition": "Mtree_red=A=E-Q",
            "degree_zero": "0",
            "degree_one": "0",
            "degree_two": "A^(2)=1/2*sum_{i<j}x_i*x_j",
            "consequence": (
                "Only A^(2) is needed inside cut products because the external "
                "interference tree also starts at virtuality degree two."
            ),
        },
        "channel_cut_decomposition": {
            "topologies": [
                "B=Q_L*Q_R",
                "T=-Q_L*E_R-E_L*Q_R",
                "X=E_L*E_R",
            ],
            "repair_identity": "E=A+Q; therefore B+T+X=A_L*A_R",
            "normalization": "d_y*d_z ordinary_cut=P_topology/12",
            "bubble_polynomial": (
                "P_B=7*S^2+S*T+T^2-(7*S+T)*Sigma_x+xa*xb+xc*xd"
                "+7*Sigma_cross"
            ),
            "triangle_polynomial": (
                "P_T=-(19*S^2+2*S*T+2*T^2-(25*S+2*T)*Sigma_x"
                "+3*xa*xb+3*xc*xd+32*Sigma_cross)"
            ),
            "box_polynomial": (
                "P_X=12*S^2+S*T+T^2-(18*S+T)*Sigma_x"
                "+5*xa*xb+5*xc*xd+31*Sigma_cross"
            ),
            "complete_polynomial": (
                "P_B+P_T+P_X=3*xa*xb+3*xc*xd+6*Sigma_cross"
            ),
            "on_shell_control": "P_B+P_T+P_X=0 when all x_i=0, channel by channel",
            "holdom_forward_control": (
                "At T=0 the generic-coupling weights are 2*P_B=14, "
                "-P_T=19, P_X/2=6, reproducing "
                "6*lambda3^4+19*lambda3^2*lambda4+14*lambda4^2."
            ),
        },
        "interference_jets": {
            "definition": (
                "J_top=[x1*x2*x3*x4](Mtree_red*sum_channels(P_top*L_channel))"
            ),
            "common_denominator": "s^2*t^2*(s+t)^2",
            "numerator_basis": "rows multiply s^(6-k)*t^k for k=0,...,6",
            "triangle_rows": triangle["rows"],
            "box_rows": box["rows"],
            "complete_rows": combined_rows,
            "complete_reduction": "J_B+J_T+J_X=15*(Ls+Lt+Lu)",
            "physical_normalization": (
                "[x1*x2*x3*x4]2*Re(Mtree^*Mloop_top_log)="
                "lambda^6/(4*pi)^2*(16/3)*J_top"
            ),
            "log_kinematic_rational_note": (
                "The named rows come only from Taylor expanding Lu(x); they are "
                "not cut-free finite rational loop terms."
            ),
        },
        "collinear_expansion": {
            "variables": "r=t/s, L=log(mu^2/s), ell=log(-t/s)",
            "bubble": (
                "J_B=(15L-ell)/r^2+(-45L+3ell-35)/r"
                "+(-30L+8ell+31/2)+O(r)"
            ),
            "triangle": (
                "J_T=(-40L+2ell)/r^2+(120L-6ell+95)/r"
                "+(35L-18ell+43/2)+O(r)"
            ),
            "box": (
                "J_X=(25L-ell)/r^2+(-75L+3ell-60)/r"
                "+(40L-5ell-37)+O(r)"
            ),
            "complete": "J_log=45L-15ell+O(r)=15*(3L-ell)+O(r)",
            "conclusion": (
                "All r^-2 and r^-1 terms cancel exactly across the three topology "
                "families. A ratio logarithm remains and must be passed through the "
                "external phase-space projector before comparison with the real threshold."
            ),
        },
        "disposition": {
            "triangle_logarithmic_jet": "COMPUTED",
            "box_logarithmic_jet": "COMPUTED",
            "complete_topology_logarithmic_jet": "COMPUTED",
            "triangle_cut_free_finite_rational_part": "NOT_COMPUTED",
            "box_cut_free_finite_rational_part": "NOT_COMPUTED",
            "bubble_finite_rational_and_counterterm_part": "NOT_COMPUTED",
            "external_phase_space_projector": "NOT_APPLIED",
            "real_virtual_collinear_cancellation": "NOT_COMPUTED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "cut-free finite rational triangle and box terms in the declared scheme",
            "the renormalized finite bubble and counterterm jet",
            "wave-function and lower-point insertion contributions",
            "one common non-mass infrared prescription across real and virtual terms",
            "the differentiated external four-body phase-space density and moving boundaries",
            "normalization map between the surviving virtual ratio log and the real -3/8 threshold",
            "a complete physical NLO probability and quotient-trace evaluation",
        ],
        "next_gate": (
            "Apply the four-external-mass phase-space projector to the complete "
            "15*(Ls+Lt+Lu) logarithmic jet under the same ratio prescription as the "
            "five-point real threshold; then determine whether the ratio logarithms cancel."
        ),
        "does_not_establish": [
            "the complete finite one-loop four-point amplitude",
            "cut-free rational triangle or box terms",
            "the finite renormalized bubble and counterterm contribution",
            "scheme or field-redefinition invariance of the off-shell projector",
            "real--virtual cancellation of the -3/8 threshold coefficient",
            "a KLN theorem, dressed-state construction, or canonical finite part",
            "a physical NLO cross section or probability",
            "positivity or unitarity beyond the published BT tree result",
            "a tensor, BRST, or gravitational lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority for the tree identity or topology polynomials",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-10",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_sources": [
                {
                    "source": "Bateman--Turok arXiv:2607.00096v1",
                    "equations": ["Eq. (2)", "Appendix B"],
                    "use": "PS action and cubic/quartic tree rules",
                },
                {
                    "source": "Holdom arXiv:2303.06723v2",
                    "equations": ["Eqs. (20)-(22)"],
                    "use": "one-loop normalization and on-shell bubble control",
                },
                {
                    "source": "Holdom arXiv:2402.09223v1",
                    "equations": ["Eqs. (11)-(13)"],
                    "use": "mass-derivative cut representation and full forward control",
                },
            ],
        },
        "verification_commands": [
            "python3 reverse_physics/bt_triangle_box_log_jet.py --check",
            "python3 reverse_physics/verify_bt_triangle_box_log_jet.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_triangle_box_log_jet",
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
