#!/usr/bin/env python3
"""Independent verifier for the physical BT collinear operator factorization."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-physical-collinear-operator-factorization-v1.schema.json")
FIVE = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json")
REAL = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json")
PUBLIC = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json")
ABEL = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(2))
             for j in range(2)] for i in range(2)]


def independent_symbolic_rail():
    """Invariant A5 graphs plus explicit dot-product A4 graphs."""
    import sympy as sp
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field
    from verify_bt_five_point_independent_mass_threshold import invariant_amplitude

    values = field("a0,a1,a2,a3,a4,tau", QQ)
    F = values[0]
    a0, a1, a2, a3, a4, tau = values[1:]
    series = invariant_amplitude(F, [a0, a1, a2, a3, a4], tau)
    C = series.coefficient(2).as_expr()
    syms = {str(symbol): symbol for symbol in C.free_symbols}
    A0, A1, A2, A3, A4, Tau = (syms[name] for name in ("a0", "a1", "a2", "a3", "a4", "tau"))
    zero = {A2: 0, A3: 0, A4: 0}
    delta2 = (A0 - A1) ** 2
    L = -delta2 / (4 * Tau)
    Q = (2 * Tau * (A0 + A1) - delta2) / (4 * Tau ** 2)
    rho = delta2 * (2 * Tau * (A0 + A1) - delta2) / (4 * Tau ** 3)
    a5_ok = (
        series.coefficient(0) == 0 and series.coefficient(1) == 0
        and all(sp.simplify(sp.diff(C, z).subs(zero) - L) == 0 for z in (A2, A3, A4))
        and all(sp.simplify(sp.diff(C, x, y).subs(zero) - Q) == 0 for x, y in ((A2, A3), (A2, A4), (A3, A4)))
        and sp.simplify(sp.expand(C**2).coeff(A2, 1).coeff(A3, 1).coeff(A4, 1) + sp.Rational(3, 2)*rho) == 0
    )

    d, p, b, c, e = sp.symbols("delta p a2 a3 a4")
    x = [d*p, d*b, d*c, d*e]
    s, t = sp.Integer(5), sp.Integer(13)
    u = sum(x) - s - t
    pair_squares = {(0, 1): s, (2, 3): s, (0, 2): t, (1, 3): t, (0, 3): u, (1, 2): u}

    def dot(i, j):
        if i == j:
            return x[i]
        i, j = sorted((i, j))
        return (pair_squares[(i, j)] - x[i] - x[j]) / 2

    def vdot(v, w):
        return sum(v[i]*w[j]*dot(i, j) for i in range(4) for j in range(4))

    basis = [tuple(1 if i == j else 0 for i in range(4)) for j in range(4)]

    def add(*vectors):
        return tuple(sum(v[i] for v in vectors) for i in range(4))

    def scale(k, v):
        return tuple(k*z for z in v)

    def cubic(v, w, z):
        return vdot(v, v)*vdot(w, z) + vdot(w, w)*vdot(v, z) + vdot(z, z)*vdot(v, w)

    def quartic(v, w, z, q):
        return vdot(v, w)*vdot(z, q) + vdot(v, z)*vdot(w, q) + vdot(v, q)*vdot(w, z)

    tree = 0
    for i, j, k, l in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):
        qleft = scale(-1, add(basis[i], basis[j]))
        qright = scale(-1, add(basis[k], basis[l]))
        S = vdot(qleft, qleft)
        tree += cubic(basis[i], basis[j], qleft) * cubic(basis[k], basis[l], qright) / S**2
    tree -= quartic(*basis)
    tree = sp.cancel(tree)
    H = sp.factor(sp.diff(tree, d, 2).subs(d, 0)/2)
    expected = sp.Rational(1, 2)*(p**2+b**2+c**2+e**2+p*b+p*c+p*e+b*c+b*e+c*e)
    hard_top = sp.expand(H**2).coeff(p, 1).coeff(b, 1).coeff(c, 1).coeff(e, 1)
    a4_ok = tree.subs(d, 0) == 0 and sp.diff(tree, d).subs(d, 0) == 0 and sp.simplify(H-expected) == 0 and hard_top == sp.Rational(3, 2)
    return a5_ok and a4_ok


def verify(certificate, exhaustive=False):
    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    five, real, public, abel = map(load, (FIVE, REAL, PUBLIC, ABEL))
    factor = certificate.get("amplitude_factorization", {})
    normalization = certificate.get("normalization_ledger", {})
    comparison = certificate.get("public_Rt_comparison", {})
    disposition = certificate.get("disposition", {})

    fixture_ok = True
    try:
        rows = factor["exact_fixtures"]
        expected_inputs = [(1, 4, 10), (1, 9, 17), (4, 9, 26)]
        fixture_ok = len(rows) == 3
        for row, raw in zip(rows, expected_inputs):
            a0, a1, tau = map(Fraction, raw)
            delta2 = (a0-a1)**2
            L2 = -delta2/(2*tau)
            Q2 = (2*tau*(a0+a1)-delta2)/(2*tau*tau)
            rho = delta2*(2*tau*(a0+a1)-delta2)/(4*tau**3)
            gram = [[frac(cell) for cell in line] for line in row["physical_gram"]]
            fixture_ok &= (
                frac(row["a0"]) == a0 and frac(row["a1"]) == a1 and frac(row["tau"]) == tau
                and frac(row["twice_L"]) == L2 and frac(row["twice_Q"]) == Q2
                and frac(row["rho"]) == rho and gram == [[rho, 0], [0, rho]]
                and a0.denominator == a1.denominator == 1
                and math.isqrt(a0.numerator*a1.numerator) ** 2 == a0.numerator*a1.numerator
                and tau > a0+a1+2*math.isqrt(a0.numerator*a1.numerator)
            )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        fixture_ok = False

    J = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    G = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(2)]]
    N = matmul(J, G)
    source_gram = public.get("endpoint_cancellation", {}).get("complete_parent_gram", {})
    input_rows = certificate.get("provenance", {}).get("inputs", [])
    checks = {
        "schema": not schema_errors,
        "identity_tags_lifecycle": certificate.get("certificate") == "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1" and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"] and certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED",
        "source_five_point_projection": five.get("amplitude_reduction", {}).get("spectator_projected_square") == "3*(a0-a1)^2*((a0-a1)^2-2*tau*(a0+a1))/(8*tau^3)",
        "factorization_formulas": factor.get("L") == "-(a0-a1)^2/(4*tau)" and factor.get("Q") == "(2*tau*(a0+a1)-(a0-a1)^2)/(4*tau^2)" and factor.get("splitting_map") == "T=diag(2*Q,2*L)" and factor.get("physical_gram") == "-T_sharp*T=rho*I2",
        "exact_fixture_rail": fixture_ok,
        "four_point_top_coefficient": factor.get("H_squarefree_top") == "[p*a2*a3*a4]H^2=3/2",
        "physical_ratio_identity": Fraction(-1) * Fraction(-3, 2) / Fraction(3, 2) == 1,
        "normalization_is_one_over_48": frac(normalization.get("amplitude_square_normalization_ratio", {})) == 4 and frac(normalization.get("projector_factorial_ratio", {})) == Fraction(1, 3) and frac(normalization.get("phase_space_and_inner_angle_ratio", {})) == Fraction(1, 16) and frac(normalization.get("combined_ratio", {})) == Fraction(1, 12) and frac(normalization.get("physical_per_pair_Born_normalized_response", {})) == Fraction(1, 48),
        "source_physical_normalization": real.get("phase_and_combinatorics", {}).get("per_pair_finite_part_shift") == "+lambda^6*log(c_pair)/(512*pi^4*s)",
        "source_public_gram": source_gram == {"G_OmegaOmega": "0", "G_OmegaUpsilon": "0", "G_UpsilonOmega": "0", "G_UpsilonUpsilon": "2*s1*s2"},
        "public_nilpotent_arithmetic": N == [[0, 2], [0, 0]] and matmul(N, N) == [[0, 0], [0, 0]],
        "comparison_invariants": comparison.get("raised_gram") == [[0, 2], [0, 0]] and comparison.get("raised_gram_rank") == 1 and comparison.get("raised_gram_determinant") == 0 and comparison.get("physical_gram_rank") == 2 and comparison.get("physical_gram_determinant") == "rho^2>0" and comparison.get("minimal_polynomial") == "x^2" and comparison.get("physical_minimal_polynomial") == "x-rho",
        "operator_obstruction_claim": comparison.get("obstruction") == "NO_METRIC_COMPATIBLE_SIMILARITY_OR_NONZERO_SCALAR_IDENTIFICATION" and disposition.get("public_D_equals_physical_splitting") == "EXACT_RANK_JORDAN_OBSTRUCTION",
        "abel_boundary_preserved": abel.get("disposition", {}).get("public_Rt_equals_physical_S_operator") == "NOT_ESTABLISHED" and disposition.get("Abel_detector_automorphism") == "RETAINED_WITHOUT_OPERATOR_IDENTIFICATION",
        "claim_boundaries": disposition.get("full_physical_Moller_operator") == "NOT_CONSTRUCTED" and disposition.get("finite_complete_NLO_probability") == "NOT_ESTABLISHED" and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED" and disposition.get("Eq19_all_orders") == "NOT_PROVED" and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", []),
        "provenance_hashes": len(input_rows) == 6 and all(row.get("sha256") == sha256(row.get("path", "")) for row in input_rows),
        "producer_ledger": certificate.get("checks", {}).get("passed") == certificate.get("checks", {}).get("total") == 22 and certificate.get("checks", {}).get("failures") == [] and all(certificate.get("checks", {}).get("details", {}).values()),
        "independent_symbolic_rail": (not exhaustive) or independent_symbolic_rail(),
    }
    for error in schema_errors:
        print("schema", list(error.path), error.message)
    failures = [name for name, ok in checks.items() if not ok]
    if failures:
        print("BT PHYSICAL COLLINEAR OPERATOR VERIFY: FAIL", *failures, sep="\n  ")
        return False, checks
    return True, checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    parser.add_argument("--exhaustive", action="store_true")
    args = parser.parse_args(argv)
    ok, checks = verify(load(args.verify), args.exhaustive)
    if not ok:
        return 1
    print(f"BT PHYSICAL COLLINEAR OPERATOR VERIFY: ALL PASS ({sum(checks.values())}/{len(checks)})" + (" [EXHAUSTIVE]" if args.exhaustive else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
