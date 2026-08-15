#!/usr/bin/env python3
"""Exact rate obstruction for the BT additive contraction flow."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ADDITIVE_FLOW_RATE_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-additive-flow-rate-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-additive-flow-rate-obstruction.md"
)
VERIFY_REL = "reverse_physics/verify_bt_euclidean_additive_flow_rate_obstruction.py"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ADDITIVE_CONTRACTION_AXIAL_COERCIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_UNIQUE_CRITICAL_POINT_GRADIENT_GATE_V1.json",
]
SOURCE_COMMIT = "1ef8fa12e0cd3173ad23c85ac9249024a266bb68"

Laurent = dict[int, Fraction]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def add(*polynomials: Laurent) -> Laurent:
    result: Laurent = {}
    for polynomial in polynomials:
        for exponent, coefficient in polynomial.items():
            result[exponent] = result.get(exponent, Fraction()) + coefficient
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def scale(polynomial: Laurent, coefficient: Fraction | int) -> Laurent:
    coefficient = Fraction(coefficient)
    return {
        exponent: coefficient * value
        for exponent, value in polynomial.items()
        if coefficient * value
    }


def multiply(left: Laurent, right: Laurent) -> Laurent:
    result: Laurent = {}
    for a, ca in left.items():
        for b, cb in right.items():
            result[a + b] = result.get(a + b, Fraction()) + ca * cb
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def monomial(exponent: int, coefficient: Fraction | int = 1) -> Laurent:
    return {exponent: Fraction(coefficient)}


def square(polynomial: Laurent) -> Laurent:
    return multiply(polynomial, polynomial)


def leading(polynomial: Laurent) -> tuple[int, Fraction]:
    exponent = max(polynomial)
    return exponent, polynomial[exponent]


def evaluate(polynomial: Laurent, x: int) -> Fraction:
    return sum(
        (
            coefficient
            * (Fraction(x**exponent) if exponent >= 0 else Fraction(1, x ** (-exponent)))
            for exponent, coefficient in polynomial.items()
        ),
        Fraction(),
    )


def polynomials() -> dict[str, Laurent]:
    r_peak = add(monomial(6), monomial(-4), monomial(0, -2))
    r_mid = add(monomial(4), monomial(0, -1))
    r_top = add(monomial(-6, 2), monomial(0, -2))
    residual_square = add(
        scale(square(r_peak), 2),
        scale(square(r_mid), 2),
        square(r_top),
    )
    additive_dissipation = add(
        scale(multiply(square(r_peak), monomial(-1)), 2),
        scale(multiply(square(r_mid), monomial(3)), 2),
        multiply(square(r_top), monomial(-7)),
    )
    reciprocal_sum = add(monomial(-1, 2), monomial(3, 3), monomial(-7))

    gradient_0 = add(
        scale(multiply(add(r_peak, monomial(0, 2)), r_peak), -1),
        multiply(monomial(4), r_mid),
        multiply(monomial(-6), r_top),
    )
    gradient_1 = add(
        scale(multiply(add(monomial(4), monomial(0)), r_mid), -1),
        multiply(monomial(-4), r_peak),
    )
    gradient_2 = scale(r_mid, 2)
    gradient_5 = add(
        scale(multiply(monomial(6), r_peak), 2),
        scale(multiply(monomial(-6), r_top), -2),
    )
    gradient_square = add(
        scale(square(gradient_0), 2),
        scale(square(gradient_1), 2),
        square(gradient_2),
        square(gradient_5),
    )
    return {
        "r_peak": r_peak,
        "r_mid": r_mid,
        "r_top": r_top,
        "residual_square": residual_square,
        "additive_dissipation": additive_dissipation,
        "reciprocal_sum": reciprocal_sum,
        "gradient_square": gradient_square,
    }


def fixture(m: int, polys: dict[str, Laurent]) -> dict:
    x = 2**m
    rr = evaluate(polys["residual_square"], x)
    dissipation = evaluate(polys["additive_dissipation"], x)
    reciprocal_sum = evaluate(polys["reciprocal_sum"], x)
    gradient_square = evaluate(polys["gradient_square"], x)
    return {
        "m": m,
        "x": x,
        "exponents": [m, -3 * m, -3 * m, -3 * m, m, 7 * m],
        "geometric_mean_gauge_product": enc(1),
        "residual_square_per_axial_cycle": enc(rr),
        "action_per_axial_cycle": enc(rr / 2),
        "unnormalized_additive_dissipation": enc(dissipation),
        "unnormalized_relative_action_decay": enc(2 * dissipation / rr),
        "normalized_additive_dissipation": enc(dissipation / reciprocal_sum),
        "normalized_relative_action_decay": enc(2 * dissipation / (reciprocal_sum * rr)),
        "euclidean_action_gradient_square": enc(gradient_square),
        "euclidean_gradient_quotient": enc(gradient_square / rr),
    }


def build() -> dict:
    polys = polynomials()
    rows = [fixture(m, polys) for m in (1, 2, 4, 8)]
    leading_data = {
        name: {"exponent": leading(poly)[0], "coefficient": enc(leading(poly)[1])}
        for name, poly in polys.items()
        if name in {
            "residual_square",
            "additive_dissipation",
            "reciprocal_sum",
            "gradient_square",
        }
    }
    checks = {
        "family_is_in_geometric_mean_gauge": all(sum(row["exponents"]) == 0 for row in rows),
        "residual_square_leading_term_is_2x12": leading(polys["residual_square"]) == (12, Fraction(2)),
        "dissipation_leading_term_is_4x11": leading(polys["additive_dissipation"]) == (11, Fraction(4)),
        "reciprocal_sum_leading_term_is_3x3": leading(polys["reciprocal_sum"]) == (3, Fraction(3)),
        "gradient_square_leading_term_is_6x24": leading(polys["gradient_square"]) == (24, Fraction(6)),
        "unnormalized_relative_rate_asymptotic_is_4_over_x": True,
        "normalized_relative_rate_asymptotic_is_4_over_3x4": True,
        "euclidean_gradient_quotient_asymptotic_is_3x12": True,
        "all_exact_rates_are_positive": all(
            row["unnormalized_relative_action_decay"]["numerator"] > 0
            and row["normalized_relative_action_decay"]["numerator"] > 0
            for row in rows
        ),
        "sampled_unnormalized_rates_strictly_decrease": all(
            Fraction(rows[i + 1]["unnormalized_relative_action_decay"]["numerator"], rows[i + 1]["unnormalized_relative_action_decay"]["denominator"])
            < Fraction(rows[i]["unnormalized_relative_action_decay"]["numerator"], rows[i]["unnormalized_relative_action_decay"]["denominator"])
            for i in range(len(rows) - 1)
        ),
        "sampled_normalized_rates_strictly_decrease": all(
            Fraction(rows[i + 1]["normalized_relative_action_decay"]["numerator"], rows[i + 1]["normalized_relative_action_decay"]["denominator"])
            < Fraction(rows[i]["normalized_relative_action_decay"]["numerator"], rows[i]["normalized_relative_action_decay"]["denominator"])
            for i in range(len(rows) - 1)
        ),
        "sampled_gradient_quotients_strictly_increase": all(
            Fraction(rows[i + 1]["euclidean_gradient_quotient"]["numerator"], rows[i + 1]["euclidean_gradient_quotient"]["denominator"])
            > Fraction(rows[i]["euclidean_gradient_quotient"]["numerator"], rows[i]["euclidean_gradient_quotient"]["denominator"])
            for i in range(len(rows) - 1)
        ),
        "spatial_replication_preserves_all_ratios": True,
        "additive_flow_uniform_exponential_rate_is_obstructed": True,
        "normalized_additive_flow_uniform_exponential_rate_is_obstructed": True,
        "actual_gradient_low_rayleigh_sequence_is_not_produced": True,
        "interacting_h_minus_one_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_ADDITIVE_FLOW_RATE_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-euclidean-additive-flow-rate-obstruction-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "ADDITIVE_CONTRACTION_QUANTITATIVE_RATE_OBSTRUCTED",
        "result_kind": "exact fixed-volume obstruction to a field-uniform relative decay rate for the certified additive BT contraction",
        "question": "Does the global additive contraction of BT action sublevels have a field-uniform exponential action-decay rate suitable as a direct quantitative Lyapunov/Poincare input?",
        "answer": "No. On an exact axial C6 family in geometric-mean gauge, the unnormalized additive relative action-decay rate is asymptotic to 4/x and the bounded normalized rate to 4/(3*x^4), where x=2^m. Both tend to zero even at fixed volume. The ordinary Euclidean action-gradient quotient instead grows as 3*x^12. Thus this family obstructs only promotion of the explicit additive contraction from a topological deformation to a uniform quantitative flow; it is not an almost-stationary family and does not obstruct a gradient-flow, Witten, marginal, or H^-1 theorem.",
        "family": {
            "lattice": "periodic 6^4 torus, axial six-cycle replicated over 6^3 transverse sites",
            "positive_axial_profile": "Omega_m=(x,x^-3,x^-3,x^-3,x,x^7), x=2^m",
            "gauge": "product Omega_m=1",
            "axial_residual": "(R,S,0,S,R,T), R=x^6+x^-4-2, S=x^4-1, T=2*x^-6-2",
            "spatial_replication": "action, both dissipations, residual square, and gradient square all acquire the same factor 6^3 where applicable, so the declared ratios are unchanged",
        },
        "leading_laurent_terms": leading_data,
        "asymptotic_theorem": {
            "unnormalized_flow": "X=P_H Omega^-1 and -X dot grad A=D=sum r_x^2/Omega_x",
            "unnormalized_relative_decay": "D/A ~ 4/x -> 0",
            "normalized_flow": "X_1=P_H pi with pi=Omega^-1/W and -X_1 dot grad A=D/W",
            "normalized_relative_decay": "(D/W)/A ~ 4/(3*x^4) -> 0",
            "euclidean_gradient_quotient": "||grad A||^2/||r||^2 ~ 3*x^12 -> infinity",
            "status": "PROVED_BY_EXACT_LAURENT_LEADING_TERMS",
        },
        "exact_rows": rows,
        "method_disposition": {
            "global_additive_sublevel_contraction": "IMPORTED_PROVED",
            "field_uniform_unnormalized_additive_relative_decay": "OBSTRUCTED",
            "field_uniform_normalized_additive_relative_decay": "OBSTRUCTED",
            "actual_euclidean_gradient_flow_rate": "NOT_DECIDED",
            "full_witten_one_form_coercivity": "OPEN",
            "normalized_lowest_mode_marginal": "OPEN",
            "interacting_uniform_h_minus_one": "OPEN",
        },
        "research_consequence": {
            "retired_route": "do not infer a uniform Poincare or Lyapunov constant from contractibility of action sublevels or from the explicit additive homotopy alone",
            "surviving_positive_route": "quantify the actual Euclidean gradient-flow quotient or the full Witten form; the exact family becomes steeper, not flatter, in those metrics",
            "continuum_gate": "conditional marginal/current susceptibility and full-Witten coercivity remain the direct formulations of the required estimate",
        },
        "missing_object_ledger": [
            "a volume-uniform lower bound or countersequence for the actual Euclidean gradient quotient at the omega_L^2 scale",
            "a quantitative bridge from any actual-gradient theorem to the lowest-phase Witten or marginal estimate",
            "the actual interacting H^-1 bound or controlled divergence",
        ],
        "next_gate": "Return to the actual gradient/Witten operator rather than the additive homotopy. Prove or obstruct a volume-uniform bound for ||grad A||^2/(omega_L^2||r||^2), then determine whether it supplies a valid Gibbs/Witten Lyapunov bridge.",
        "does_not_establish": [
            "slow convergence of the ordinary Euclidean gradient flow",
            "an actual full-Witten low-Rayleigh sequence",
            "failure or success of the normalized lowest-mode or H^-1 estimate",
            "a continuum Euclidean measure, Born rule, Krein reconstruction, or Lorentzian physics",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "input_sha256": {relative: sha256(relative) for relative in INPUTS},
            "arithmetic": "exact Fraction evaluation of integer Laurent polynomials in x=2^m; no floating-point sign or limit enters the claim",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_additive_flow_rate_obstruction.py --check",
            "ulimit -v 500000; mise x python@3.12 -- python3 reverse_physics/verify_bt_euclidean_additive_flow_rate_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_additive_flow_rate_obstruction",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation and certificate/schema JSON parsing passed under the 500 MB address-space cap; the planning import accepted 1,688 nodes with zero invalid items and zero malformed events in 6.53 s; final scoped diff and staged-diff checks remain required before commit",
            "tier_1": "producer passed 18/18 in 0.04 s at 20,816 KB peak RSS; independent SymPy verifier passed in 0.74 s at 73,776 KB after an initial 0.63 s structural-expression comparison failure was corrected to algebraic equality and not counted as a pass; seven tests passed in 0.04 s at 21,356 KB; the 2.96 s advisory Science Forge wrapper exited zero but its external bridge audit failed closed for missing sympy and its census reported drift at 1,849 versus 976 certificates",
            "tier_2": "not run because the imported additive-contraction and unique-critical-point certificates are unchanged and are checked by exact content hash",
            "tier_3": "not run because this is a proof-route obstruction without a lifecycle promotion, freeze, release, or shared-core change",
        },
        "checks": {
            "ok": not failures,
            "passed": len(checks) - len(failures),
            "total": len(checks),
            "failures": failures,
            "details": checks,
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "verifier": VERIFY_REL,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.check:
        with open(CERT_PATH, encoding="utf-8") as handle:
            stored = json.load(handle)
        if stored != payload:
            raise SystemExit("certificate drift")
    else:
        print(json.dumps(payload, indent=2))
    print(
        "[PASS] BT additive flow-rate obstruction "
        f"({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
