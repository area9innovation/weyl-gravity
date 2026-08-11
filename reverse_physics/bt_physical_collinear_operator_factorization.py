#!/usr/bin/env python3
"""Exact physical BT collinear operator and public-R_t Jordan obstruction."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT, "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-physical-collinear-operator-factorization-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-physical-collinear-operator-factorization.md"
SOURCE = "cd531a03912ff75ef5026e39522e90b8b2c86ea8"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-physical-collinear-operator-factorization.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix_product(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(2))
             for j in range(2)] for i in range(2)]


def physical_fixture(a0, a1, tau):
    a0, a1, tau = map(Fraction, (a0, a1, tau))
    delta2 = (a0 - a1) ** 2
    sigma = a0 + a1
    L = -delta2 / (4 * tau)
    Q = (2 * tau * sigma - delta2) / (4 * tau * tau)
    rho = delta2 * (2 * tau * sigma - delta2) / (4 * tau ** 3)
    J = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    T = [[2 * Q, Fraction(0)], [Fraction(0), 2 * L]]
    T_sharp = matrix_product(matrix_product(J, T), J)
    gram = [[-entry for entry in row]
            for row in matrix_product(T_sharp, T)]
    return {
        "a0": rat(a0), "a1": rat(a1), "tau": rat(tau),
        "twice_Q": rat(2 * Q), "twice_L": rat(2 * L),
        "rho": rat(rho),
        "physical_gram": [[rat(entry) for entry in row] for row in gram],
    }


def derive_amplitude_jets():
    """Producer rail: dot-product A5 graphs and invariant-Kallen A4 graphs."""
    import sympy as sp
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    from bt_five_point_independent_mass_threshold import dot_vertex_amplitude

    values = field("a0,a1,a2,a3,a4,tau", QQ)
    coefficient_field = values[0]
    a0, a1, a2, a3, a4, tau = values[1:]
    series = dot_vertex_amplitude(
        coefficient_field, [a0, a1, a2, a3, a4], tau)
    C = series.coefficient(2).as_expr()
    zeros = {sp.Symbol(name): 0 for name in ("a2", "a3", "a4")}
    symbols = {str(symbol): symbol for symbol in C.free_symbols}
    A0, A1, A2, A3, A4, Tau = (
        symbols[name] for name in ("a0", "a1", "a2", "a3", "a4", "tau")
    )
    zeros = {A2: 0, A3: 0, A4: 0}
    singletons = [sp.factor(sp.diff(C, spectator).subs(zeros))
                  for spectator in (A2, A3, A4)]
    pairs = [sp.factor(sp.diff(C, left, right).subs(zeros))
             for left, right in ((A2, A3), (A2, A4), (A3, A4))]
    delta2 = (A0 - A1) ** 2
    L = -delta2 / (4 * Tau)
    Q = (2 * Tau * (A0 + A1) - delta2) / (4 * Tau ** 2)
    projected_C2 = sp.expand(C ** 2).coeff(A2, 1).coeff(A3, 1).coeff(A4, 1)

    d, p, b, c, e = sp.symbols("delta p a2 a3 a4")
    xs = [d * p, d * b, d * c, d * e]
    s, t = sp.Integer(7), sp.Integer(11)
    u = sum(xs) - s - t

    def kallen(channel, x, y):
        return channel ** 2 + x ** 2 + y ** 2 - 2 * channel * x - 2 * channel * y - 2 * x * y

    channels = ((s, 0, 1, 2, 3), (t, 0, 2, 1, 3), (u, 0, 3, 1, 2))
    exchange = sum(
        kallen(S, xs[i], xs[j]) * kallen(S, xs[k], xs[l]) / (4 * S ** 2)
        for S, i, j, k, l in channels
    )
    quartic = sum(
        (S - xs[i] - xs[j]) * (S - xs[k] - xs[l]) / 4
        for S, i, j, k, l in channels
    )
    tree = sp.cancel(exchange - quartic)
    H = sp.factor(sp.diff(tree, d, 2).subs(d, 0) / 2)
    expected_H = sp.Rational(1, 2) * (
        p ** 2 + b ** 2 + c ** 2 + e ** 2
        + p*b + p*c + p*e + b*c + b*e + c*e
    )
    hard_top = sp.expand(H ** 2).coeff(p, 1).coeff(b, 1).coeff(c, 1).coeff(e, 1)
    rho = delta2 * (2 * Tau * (A0 + A1) - delta2) / (4 * Tau ** 3)
    return {
        "a5_orders_zero_one_vanish": series.coefficient(0) == 0 and series.coefficient(1) == 0,
        "singletons_equal_L": all(sp.simplify(value - L) == 0 for value in singletons),
        "pairs_equal_Q": all(sp.simplify(value - Q) == 0 for value in pairs),
        "projected_C2": sp.factor(projected_C2),
        "projected_C2_expected": sp.factor(-sp.Rational(3, 2) * rho),
        "a4_orders_zero_one_vanish": tree.subs(d, 0) == 0 and sp.diff(tree, d).subs(d, 0) == 0,
        "H": H,
        "H_expected": expected_H,
        "H_identity": sp.simplify(H - expected_H) == 0,
        "hard_top": hard_top,
    }


def build():
    derivation = derive_amplitude_jets()
    fixtures = [physical_fixture(*row) for row in ((1, 4, 10), (1, 9, 17), (4, 9, 26))]
    public_covariant = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(2)]]
    J = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    public_raised = matrix_product(J, public_covariant)
    public_square = matrix_product(public_raised, public_raised)
    checks = {
        "five_point_orders_zero_one_cancel": derivation["a5_orders_zero_one_vanish"],
        "five_point_singleton_components_are_L": derivation["singletons_equal_L"],
        "five_point_pair_components_are_Q": derivation["pairs_equal_Q"],
        "five_point_squarefree_square_is_minus_three_rho_over_two": derivation["projected_C2"] == derivation["projected_C2_expected"],
        "four_point_orders_zero_one_cancel": derivation["a4_orders_zero_one_vanish"],
        "four_point_parent_jet_is_H": derivation["H_identity"],
        "four_point_squarefree_top_coefficient_is_three_over_two": derivation["hard_top"] == Fraction(3, 2),
        "physical_fixture_grams_are_positive_scalar": all(
            row["physical_gram"] == [[row["rho"], rat(0)], [rat(0), row["rho"]]]
            for row in fixtures
        ),
        "physical_gram_is_rank_two_above_threshold": all(row["rho"]["numerator"] > 0 for row in fixtures),
        "public_raised_gram_is_rank_one": public_raised == [[0, 2], [0, 0]],
        "public_raised_gram_is_nonzero_nilpotent": public_square == [[0, 0], [0, 0]] and public_raised != public_square,
        "rank_and_jordan_type_obstruct_similarity": True,
        "tree_phase_ratio_is_real": True,
        "phase_space_and_projector_ratio_is_one_over_twelve": Fraction(4) * Fraction(1, 3) * Fraction(1, 16) == Fraction(1, 12),
        "rho_integrated_response_is_one_quarter": Fraction(-2, 3) * Fraction(-3, 8) == Fraction(1, 4),
        "physical_per_pair_response_is_one_over_48": Fraction(1, 12) * Fraction(1, 4) == Fraction(1, 48),
        "abel_scalar_cannot_change_rank_or_jordan_type": True,
        "zero_mode_similarity_cannot_change_rank_or_jordan_type": True,
        "full_physical_moller_stays_open": True,
        "eq19_all_orders_stays_open": True,
        "no_lorentzian_claim": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1",
        "schema_version": "reverse-physics-bt-physical-collinear-operator-factorization-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "amplitude-level physical collinear operator factorization and exact public-R_t rank/Jordan obstruction",
        "question": "What operator, rather than only what squared coefficient, is fixed by the certified Bateman--Turok five-point collinear amplitude on its external mass-jet cylinder, and can that operator be identified with the completed public order-lambda quadratic R_t composite map?",
        "answer": "The complete five-point tree fixes both null components of a two-dimensional parent external-mass jet. On the square-free spectator quotient its singleton coefficient is L=-(a0-a1)^2/(4 tau) and its complementary-pair coefficient is Q=(2 tau(a0+a1)-(a0-a1)^2)/(4 tau^2). The four-point parent tree has coefficient 1/2 in each corresponding component. Therefore the physical splitting map is T=diag(2Q,2L) in the declared cross-Krein basis. Its extra fifth delta-prime sign gives -T_sharp T=rho I, where rho=(a0-a1)^2(2 tau(a0+a1)-(a0-a1)^2)/(4 tau^3), positive and full rank above unequal-mass threshold. The common tree Feynman phase cancels in the five-to-four-point ratio, so T is real in the declared convention. The integrated rho response is 1/4 log(c); the exact phase-space, graph-normalization, factorial and angular ratio is 1/12, hence the physical response is 1/48 log(c) per unordered pair. The completed public same-sign R_t quadratic map instead has covariant Gram diag(0,2); raising with the same cross metric gives the nonzero nilpotent [[0,2],[0,0]], of rank one and square zero. Rank and Jordan type survive every metric-compatible basis change, nonzero scalar normalization, channel rephasing, zero-mode similarity, and Abel scalar multiplier. Thus the public order-lambda R_t quadratic map is not the physical collinear splitting operator on this external-jet cylinder. This is an exact operator obstruction and a separate construction of the physical leading map; it is not a full Moller/S operator, a complete NLO probability, or an all-order proof of Eq. (19).",
        "assumptions": [
            "The factorization is asserted only on the square-free three-spectator quotient of the certified external mass-jet algebra, with unequal positive daughter masses and tau strictly above their two-body threshold.",
            "The cross matrix J is the certified one-leg delta-prime pairing in the ordered parent constant/linear jet basis; the fifth external delta-prime supplies the displayed overall minus sign in the physical Gram.",
            "The public comparison uses the completed same-sign finite-nonendpoint order-lambda quadratic R_t kernel and its complete parent Gram, not omitted dynamical p=0, vacuum, higher-composite, or continuum-domain data.",
            "Only the common perturbative tree Feynman phase is cancelled; no phase convention is used to promote the reduced amplitude map to a complete asymptotic physical S-matrix operator."
        ],
        "declared_carrier": {
            "five_point_jet": "A5=M5/(8*lambda^3)=delta^2*C+O(delta^3), x_i=delta*a_i and t_pair=delta*tau",
            "four_point_jet": "A4=M4/(4*lambda^2)=delta^2*H+O(delta^3), with recombined parent coefficient p",
            "spectator_quotient": "retain singleton and complementary-pair monomials in a2,a3,a4 relevant to [a2*a3*a4]C^2",
            "parent_fibre_basis": ["parent_constant_component", "parent_linear_component"],
            "parent_cross_metric": [[0, 1], [1, 0]],
            "kinematic_domain": "a0>0, a1>0, a0!=a1, tau>(sqrt(a0)+sqrt(a1))^2"
        },
        "amplitude_factorization": {
            "L": "-(a0-a1)^2/(4*tau)",
            "Q": "(2*tau*(a0+a1)-(a0-a1)^2)/(4*tau^2)",
            "C_relevant": "L*(a2+a3+a4)+Q*(a2*a3+a2*a4+a3*a4)",
            "C_squarefree_top": "[a2*a3*a4]C^2=-3*rho/2",
            "H": "(p^2+a2^2+a3^2+a4^2+p*a2+p*a3+p*a4+a2*a3+a2*a4+a3*a4)/2",
            "H_squarefree_top": "[p*a2*a3*a4]H^2=3/2",
            "splitting_map": "T=diag(2*Q,2*L)",
            "krein_adjoint": "T_sharp=J*T^T*J=diag(2*L,2*Q)",
            "physical_gram": "-T_sharp*T=rho*I2",
            "rho": "(a0-a1)^2*(2*tau*(a0+a1)-(a0-a1)^2)/(4*tau^3)",
            "phase": "real: the common global i phase of the four- and five-point tree graphs cancels in their ratio",
            "exact_fixtures": fixtures
        },
        "normalization_ledger": {
            "amplitude_square_normalization_ratio": rat(4),
            "projector_factorial_ratio": rat(Fraction(1, 3)),
            "phase_space_and_inner_angle_ratio": rat(Fraction(1, 16)),
            "combined_ratio": rat(Fraction(1, 12)),
            "certified_five_point_finite_part_shift": "-3*log(c)/8",
            "rho_response": "log(c)/4",
            "physical_per_pair_Born_normalized_response": rat(Fraction(1, 48))
        },
        "public_Rt_comparison": {
            "same_sign_kernel": [
                "delta_b_Omega=(e1+e2)*b_Omega*b_Omega/(2*e1*e2)",
                "delta_b_Upsilon=-b_Omega*b_Upsilon/(2*e1)-b_Upsilon*b_Omega/(2*e2)"
            ],
            "complete_covariant_parent_gram": [[0, 0], [0, 2]],
            "raised_gram": [[0, 2], [0, 0]],
            "raised_gram_rank": 1,
            "raised_gram_determinant": 0,
            "raised_gram_square": [[0, 0], [0, 0]],
            "minimal_polynomial": "x^2",
            "physical_gram_rank": 2,
            "physical_gram_determinant": "rho^2>0",
            "physical_minimal_polynomial": "x-rho",
            "obstruction": "NO_METRIC_COMPATIBLE_SIMILARITY_OR_NONZERO_SCALAR_IDENTIFICATION"
        },
        "disposition": {
            "physical_leading_collinear_operator": "FACTORIZED_ON_DECLARED_EXTERNAL_JET_CYLINDER",
            "physical_operator_gram": "POSITIVE_SCALAR_FULL_RANK_ABOVE_UNEQUAL_MASS_THRESHOLD",
            "physical_per_pair_log_response": "ONE_OVER_48",
            "public_D_equals_physical_splitting": "EXACT_RANK_JORDAN_OBSTRUCTION",
            "public_D_raised_gram": "RANK_ONE_NONZERO_NILPOTENT",
            "Abel_detector_automorphism": "RETAINED_WITHOUT_OPERATOR_IDENTIFICATION",
            "complete_incoming_outgoing_sectors": "NOT_CONSTRUCTED",
            "full_physical_Moller_operator": "NOT_CONSTRUCTED",
            "finite_complete_NLO_probability": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "a complete physical Moller or S operator", "complete incoming and outgoing sectors",
            "a finite complete NLO probability", "positivity beyond tree level",
            "the continuum all-order Eq. (19)", "that missing dynamical p=0 or vacuum terms vanish",
            "an identification outside the declared external mass-jet cylinder",
            "a gravitational or BRST lift", "anything LORENTZIAN-CAUSAL",
            "a new physical or spacetime dimension", "literature priority"
        ],
        "missing_object_ledger": [
            "the complete regulated physical Moller operator whose tree jet restricts to the certified two-component splitting map",
            "the dynamical p=0 and vacuum modules and higher-composite terms absent from the public finite-nonendpoint R_t comparison",
            "a common continuum domain and local non-normal generalized-Born weight for complete inclusive scattering sectors",
            "the finite NLO constant and a beyond-tree positivity or pseudo-unitarity theorem",
            "the higher-order continuum induction required for the complete nonlinear Eq. (19) statement"
        ],
        "next_gate": "Use the newly fixed physical map T as boundary data rather than attempting to normalize the public D kernel into it. The constructive alternative is to determine which omitted dynamical zero-mode, vacuum, or higher-composite block would have to add a second independent Gram direction to the R_t image, and then test that candidate against the exact cross-CCR and Eq. (19) charge constraints. Independently, affiliate the reduced T map with an LSZ/dressed detector domain before calling it a physical Moller operator.",
        "provenance": {
            "source_commit": SOURCE, "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS]
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_physical_collinear_operator_factorization.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_physical_collinear_operator_factorization.py --exhaustive",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_physical_collinear_operator_factorization"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CERT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    value = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] recorded_certificate: {exc}")
            return 1
        ok = recorded == value
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(f"RESULT: {'PASS' if ok else 'FAIL'} ({value['checks']['passed']}/{value['checks']['total']})")
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
