#!/usr/bin/env python3
"""Rigorous coefficient-computed weighted Schur rows on S2(1) x S2(2)."""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction
from math import comb, factorial
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp
from mpmath.libmp import to_rational
import sympy as sp

from .product_s2_s2_ghost_schur_weighted_rows_preflight import (
    MELLIN_KEYS,
    _moment_product_coefficients,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-schur-weighted-rows-v1.schema.json"
PREFLIGHT = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS_PREFLIGHT.json"

EM_ORDER = 18
SPLIT = Fraction(1, 20)
UPPER_CUTOFF = 80
SQRT_PI_UPPER = Fraction(1773, 1000)
EXP_QUARTER_UPPER = Fraction(32, 31)
TERM_OPERATION_BUDGET = 200
TERM_CONDITIONING_MULTIPLIER = Fraction(16)
BINARY64_UNIT_ROUNDOFF = Fraction(1, 2**53)
SUM_ENVELOPE = Fraction(2)
MP_IV_DPS = 70

TIER3_PROMOTION_RECEIPT = {
    "command": "PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl -p 'test_*.py' -q",
    "repository_head_at_start": "a08fbf2d3337d7a7a0f61889390fd0e69e28083f",
    "quantum_evidence_commit": "75ef69a24eb7ad7cd27fa05601270abff13aa947",
    "tests_run": 850,
    "test_elapsed_seconds": "658.135",
    "wall_elapsed_seconds": "660.46",
    "failures": 0,
    "errors": 0,
    "status": "PASSED",
    "scope_note": "quantum-weyl was committed; unrelated shared-workspace paths were dirty and are outside this promotion",
}

ROW_K_WEIGHTS = {
    (1, 0, 2): Fraction(2, 3),
    (0, 1, 2): Fraction(4, 3),
    (1, 0, 3): Fraction(4, 3),
    (0, 1, 3): Fraction(16, 3),
    (1, 0, 4): Fraction(8, 3),
    (0, 1, 4): Fraction(64, 3),
}
ROW_K2_WEIGHTS = {
    (2, 0, 4): Fraction(4, 9),
    (1, 1, 4): Fraction(16, 9),
    (0, 2, 4): Fraction(16, 9),
    (2, 0, 5): Fraction(16, 9),
    (1, 1, 5): Fraction(32, 3),
    (0, 2, 5): Fraction(128, 9),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _sp_fraction(value: sp.Expr) -> Fraction:
    value = sp.Rational(value)
    return Fraction(int(value.p), int(value.q))


def _ivq(value: Fraction | int | sp.Rational) -> Any:
    if isinstance(value, sp.Rational):
        return mp.iv.mpf(int(value.p)) / int(value.q)
    value = Fraction(value)
    return mp.iv.mpf(value.numerator) / value.denominator


def _endpoint(interval: Any, index: int) -> str:
    numerator, denominator = to_rational(interval._mpi_[index])
    with localcontext() as context:
        context.prec = MP_IV_DPS + 12
        context.rounding = ROUND_FLOOR if index == 0 else ROUND_CEILING
        return format(Decimal(numerator) / Decimal(denominator), "f")


def _gamma(count: int) -> Fraction:
    product = count * BINARY64_UNIT_ROUNDOFF
    return product / (1 - product)


def _full_em_heat_polynomial(order: int) -> dict[int, sp.Rational]:
    x, t = sp.symbols("x t")
    summand = (2 * x + 1) * sp.exp(-t * x * (x + 1))
    expression = 1 / t + sp.Rational(1, 2) * summand.subs(x, 0)
    for index in range(1, order + 1):
        expression -= (
            sp.bernoulli(2 * index)
            / sp.factorial(2 * index)
            * sp.diff(summand, x, 2 * index - 1).subs(x, 0)
        )
    expression = sp.expand(expression)
    return {
        power: sp.Rational(expression.coeff(t, power))
        for power in range(-1, 2 * order)
        if expression.coeff(t, power) != 0
    }


def _gaussian_monomial_integral_upper(power: int) -> Fraction:
    """Upper bound for integral_0^infinity u^power exp(-u^2) du."""

    if power % 2:
        return Fraction(factorial((power - 1) // 2), 2)
    half = power // 2
    return (
        Fraction(factorial(2 * half), 2 * 4**half * factorial(half))
        * SQRT_PI_UPPER
    )


def _gaussian_derivative_l1_upper(derivative: int, degree: int) -> Fraction:
    u = sp.symbols("u")
    polynomial = sp.Poly(
        sp.expand(
            sp.exp(u**2)
            * sp.diff(u**degree * sp.exp(-(u**2)), u, derivative)
        ),
        u,
    )
    return sum(
        (
            abs(_sp_fraction(coefficient))
            * _gaussian_monomial_integral_upper(power[0])
            for power, coefficient in polynomial.terms()
        ),
        Fraction(0),
    )


def _moment_em_error_constant(moment: int, tau_max: Fraction) -> Fraction:
    """C_p with |E_p(tau)| <= C_p tau^(r-p-1)."""

    derivative = 2 * EM_ORDER
    polynomial_bound = sum(
        (
            Fraction(comb(moment, index), 4 ** (moment - index))
            * tau_max ** (moment - index)
            * _gaussian_derivative_l1_upper(derivative, 2 * index + 1)
            for index in range(moment + 1)
        ),
        Fraction(0),
    )
    # |B_2r({x})|/(2r)! <= 2 zeta(2r)/(2 pi)^(2r) < 4/6^(2r).
    # The shifted summand contributes 2 exp(tau/4), bounded by 2*(32/31).
    return Fraction(8, 6 ** (2 * EM_ORDER)) * EXP_QUARTER_UPPER * polynomial_bound


def _moment_em_polynomial_bound(
    heat: dict[int, sp.Rational], moment: int, tau_max: Fraction
) -> Fraction:
    """B_p with |P_p(tau)| <= B_p tau^(-p-1)."""

    t = sp.symbols("t")
    expression = sum((coefficient * t**power for power, coefficient in heat.items()), sp.Integer(0))
    moment_expression = sp.expand((-1) ** moment * sp.diff(expression, t, moment))
    polynomial = sp.Poly(sp.expand(moment_expression * t ** (moment + 1)), t)
    return sum(
        (
            abs(_sp_fraction(coefficient)) * tau_max ** power[0]
            for power, coefficient in polynomial.terms()
        ),
        Fraction(0),
    )


def _mellin_em_error_bound(
    heat: dict[int, sp.Rational], key: tuple[int, int, int]
) -> Fraction:
    left_moment, right_moment, mellin_order = key
    tau_max = 2 * SPLIT
    c_left = _moment_em_error_constant(left_moment, tau_max)
    c_right_base = _moment_em_error_constant(right_moment, tau_max)
    b_left = _moment_em_polynomial_bound(heat, left_moment, tau_max)
    b_right_base = _moment_em_polynomial_bound(heat, right_moment, tau_max)
    # b=2m(m+1): 2^q P_q(2t) and 2^q E_q(2t).
    c_right = 2 ** (EM_ORDER - 1) * c_right_base
    b_right = b_right_base / 2
    first_power = mellin_order + EM_ORDER - left_moment - right_moment - 2
    second_power = mellin_order + 2 * EM_ORDER - left_moment - right_moment - 2
    if first_power <= 0 or second_power <= 0:
        raise AssertionError("Euler--Maclaurin product error is not Mellin integrable")
    error = (
        (c_left * b_right + c_right * b_left)
        * SPLIT**first_power
        / first_power
        + c_left * c_right * SPLIT**second_power / second_power
    ) / factorial(mellin_order - 1)
    return error


def _one_sphere_tail(coupling: Fraction, cutoff: int) -> Fraction:
    first = cutoff + 1
    exponent = coupling * first * (first + 1)
    exponential_upper = Fraction(1, 2 ** (exponent.numerator // exponent.denominator))
    return (2 * first + 1 + 1 / coupling) * exponential_upper


def _product_heat_cutoff_tail(split: Fraction, cutoff: int) -> Fraction:
    # After splitting exp(-lambda t) equally, the left/right couplings are
    # t/2 and t because b=2m(m+1). For 0<c<=1/2, H(c)<=2/c.
    left_tail = _one_sphere_tail(split / 2, cutoff)
    right_tail = _one_sphere_tail(split, cutoff)
    return left_tail * (2 / split) + (4 / split) * right_tail


def _upper_mellin_cutoff_tail(key: tuple[int, int, int]) -> Fraction:
    left_moment, right_moment, mellin_order = key
    product_tail = _product_heat_cutoff_tail(SPLIT, UPPER_CUTOFF)
    multiplier = Fraction(0)
    for power in range(mellin_order):
        lambda_power = left_moment + right_moment + power - mellin_order
        polynomial_bound = Fraction(1) if lambda_power <= 0 else 2 / SPLIT
        multiplier += SPLIT**power / factorial(power) * polynomial_bound
    return product_tail * multiplier


def _interval_mellin_value(
    heat: dict[int, sp.Rational], key: tuple[int, int, int]
) -> Any:
    left_moment, right_moment, mellin_order = key
    coefficients = _moment_product_coefficients(
        heat, left_moment, right_moment, 2 * EM_ORDER - 1
    )
    split_iv = _ivq(SPLIT)
    pole = sp.Rational(coefficients.get(-mellin_order, 0))
    regular = _ivq(pole) * mp.iv.log(split_iv)
    for power, coefficient in coefficients.items():
        if power == -mellin_order:
            continue
        regular += _ivq(coefficient) * split_iv ** (mellin_order + power) / (
            mellin_order + power
        )
    upper = mp.iv.mpf(0)
    for ell in range(UPPER_CUTOFF + 1):
        a = ell * (ell + 1)
        for emm in range(UPPER_CUTOFF + 1):
            b = 2 * emm * (emm + 1)
            lam = a + b
            if (
                lam == 0
                or (left_moment and a == 0)
                or (right_moment and b == 0)
            ):
                continue
            argument = _ivq(lam) * split_iv
            polynomial = sum(
                (argument**power / factorial(power) for power in range(mellin_order)),
                mp.iv.mpf(0),
            )
            upper += (
                (2 * ell + 1)
                * (2 * emm + 1)
                * a**left_moment
                * b**right_moment
                * factorial(mellin_order - 1)
                * mp.iv.exp(-argument)
                * polynomial
                / lam**mellin_order
            )
    regular += upper
    harmonic = sum((Fraction(1, value) for value in range(1, mellin_order)), Fraction(0))
    digamma = _ivq(harmonic) - mp.iv.euler
    return (regular - _ivq(pole) * digamma) / factorial(mellin_order - 1)


def _row_interval(values: dict[tuple[int, int, int], Any], weights: dict[tuple[int, int, int], Fraction], subtraction: int) -> Any:
    return sum((_ivq(weight) * values[key] for key, weight in weights.items()), mp.iv.mpf(0)) - subtraction


def _weighted_bound(bounds: dict[tuple[int, int, int], Fraction], weights: dict[tuple[int, int, int], Fraction]) -> Fraction:
    return sum((weight * bounds[key] for key, weight in weights.items()), Fraction(0))


def _direct_sum_rounding(preflight: dict[str, Any]) -> dict[str, Any]:
    remainder = preflight["trace_class_remainders"]
    count = int(remainder["bounds"]["summand_count"])
    per_term = TERM_CONDITIONING_MULTIPLIER * _gamma(TERM_OPERATION_BUDGET)
    summation = _gamma(count)
    relative = per_term + summation * (1 + per_term)
    observed = max(
        Fraction.from_float(float(remainder["R_K_partial"])),
        Fraction.from_float(float(remainder["FP_R_K2_partial"])),
    )
    if observed / (1 - relative) >= SUM_ENVELOPE:
        raise AssertionError("positive-sum bootstrap envelope failed")
    absolute = SUM_ENVELOPE * relative
    return {
        "binary64_unit_roundoff": _q(BINARY64_UNIT_ROUNDOFF),
        "per_term_operation_budget": TERM_OPERATION_BUDGET,
        "conditioning_multiplier": _q(TERM_CONDITIONING_MULTIPLIER),
        "conditioning_reason": "the regular complement has lambda>=6, hence 1-4/lambda>=1/3; the factor 16 dominates denominator conditioning and propagation across the positive expression tree",
        "per_term_relative_error_bound": _q(per_term),
        "summand_count": count,
        "ordinary_summation_gamma": _q(summation),
        "positive_exact_sum_envelope": _q(SUM_ENVELOPE),
        "bootstrap_inequality": "observed/(1-relative_error)<2",
        "absolute_rounding_bound": _q(absolute),
    }


def _fraction_from_q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def build() -> dict[str, Any]:
    preflight = json.loads(PREFLIGHT.read_text())
    if (
        preflight["claim_flags"]["PRODUCT_WEIGHTED_TRACE_POLES_REPLAYED"] is not True
        or preflight["claim_flags"]["PRODUCT_TRACE_CLASS_REMAINDER_TAILS_RIGOROUSLY_BOUNDED"] is not True
    ):
        raise ValueError("weighted-row preflight dependency drifted")
    mp.mp.dps = MP_IV_DPS + 30
    mp.iv.dps = MP_IV_DPS
    heat = _full_em_heat_polynomial(EM_ORDER)
    values = {key: _interval_mellin_value(heat, key) for key in MELLIN_KEYS}
    base_k = _row_interval(values, ROW_K_WEIGHTS, 6)
    base_k2 = _row_interval(values, ROW_K2_WEIGHTS, 2)
    em_bounds = {key: _mellin_em_error_bound(heat, key) for key in MELLIN_KEYS}
    cutoff_bounds = {key: _upper_mellin_cutoff_tail(key) for key in MELLIN_KEYS}
    row_em_k = _weighted_bound(em_bounds, ROW_K_WEIGHTS)
    row_em_k2 = _weighted_bound(em_bounds, ROW_K2_WEIGHTS)
    row_cutoff_k = _weighted_bound(cutoff_bounds, ROW_K_WEIGHTS)
    row_cutoff_k2 = _weighted_bound(cutoff_bounds, ROW_K2_WEIGHTS)
    rounding = _direct_sum_rounding(preflight)
    round_bound = _fraction_from_q(rounding["absolute_rounding_bound"])
    old_bounds = preflight["trace_class_remainders"]["bounds"]
    exterior_k = _fraction_from_q(old_bounds["R_K_exterior_tail_bound"])
    exterior_k2 = _fraction_from_q(old_bounds["FP_R_K2_exterior_tail_bound"])
    partial_k = Fraction.from_float(float(preflight["trace_class_remainders"]["R_K_partial"]))
    partial_k2 = Fraction.from_float(float(preflight["trace_class_remainders"]["FP_R_K2_partial"]))
    final_k = (
        base_k
        + _ivq(partial_k)
        + mp.iv.mpf([-_ivq(row_em_k + row_cutoff_k + round_bound), _ivq(row_em_k + row_cutoff_k + round_bound + exterior_k)])
    )
    final_k2 = (
        base_k2
        + _ivq(partial_k2)
        + mp.iv.mpf([-_ivq(row_em_k2 + row_cutoff_k2 + round_bound), _ivq(row_em_k2 + row_cutoff_k2 + round_bound + exterior_k2)])
    )
    final_split = final_k - final_k2 / 2
    result = {
        "schema": "quantum-weyl-product-s2-s2-ghost-schur-weighted-rows-v1",
        "result_id": "PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS",
        "result_state": "PRODUCT_WEIGHTED_ROWS_RIGOROUS_ENCLOSURES_COEFFICIENT_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": preflight["classical_commit"],
        "scope": preflight["scope"],
        "euler_maclaurin_remainder_proof": {
            "order": EM_ORDER,
            "split": _q(SPLIT),
            "full_polynomial_power_range": [-1, 2 * EM_ORDER - 1],
            "periodic_bernoulli_bound": "2*zeta(2r)/(2*pi)^(2r) < 4/6^(2r)",
            "sqrt_pi_upper": _q(SQRT_PI_UPPER),
            "sqrt_pi_proof": "pi<22/7<(1773/1000)^2",
            "exp_tau_over_four_upper": _q(EXP_QUARTER_UPPER),
            "exp_proof": "tau<=1/8 and exp(tau/4)<=1/(1-tau/4)<=32/31",
            "mellin_block_error_bounds": {str(key): _q(value) for key, value in em_bounds.items()},
            "row_R_K_error_bound": _q(row_em_k),
            "row_FP_R_K2_error_bound": _q(row_em_k2),
        },
        "upper_incomplete_cutoff_proof": {
            "rectangular_cutoff": UPPER_CUTOFF,
            "product_heat_tail_bound": _q(_product_heat_cutoff_tail(SPLIT, UPPER_CUTOFF)),
            "row_R_K_error_bound": _q(row_cutoff_k),
            "row_FP_R_K2_error_bound": _q(row_cutoff_k2),
            "proof_method": "split exp(-lambda*t) equally; use lambda^k exp(-lambda*t/2)<=(2k/t)^k for k=0,1, H(c)<=2/c, and a geometric 2^-floor(c(L+1)(L+2)) tail",
        },
        "direct_trace_class_rounding_proof": rounding,
        "direct_trace_class_exterior_bounds": {
            "R_K": _q(exterior_k),
            "FP_R_K2": _q(exterior_k2),
        },
        "directed_interval_base_values": {
            "R_K_meromorphic_block": {"lower": _endpoint(base_k, 0), "upper": _endpoint(base_k, 1)},
            "FP_R_K2_meromorphic_block": {"lower": _endpoint(base_k2, 0), "upper": _endpoint(base_k2, 1)},
            "arithmetic": f"mpmath interval arithmetic at {MP_IV_DPS} decimal digits",
        },
        "weighted_rows": {
            "R_Delta_K": {"lower": _endpoint(final_k, 0), "upper": _endpoint(final_k, 1)},
            "FP_R_Delta_K2": {"lower": _endpoint(final_k2, 0), "upper": _endpoint(final_k2, 1)},
            "low_order_split_R_K_minus_half_R_K2": {"lower": _endpoint(final_split, 0), "upper": _endpoint(final_split, 1)},
        },
        "claim_flags": {
            "PRODUCT_WEIGHTED_ROW_RIGOROUS_ENCLOSURES_DERIVED": True,
            "PRODUCT_HEAT_EULER_MACLAURIN_REMAINDER_RIGOROUSLY_BOUNDED": True,
            "PRODUCT_WEIGHTED_R_K_COMPUTED": True,
            "PRODUCT_FINITE_PART_R_K2_COMPUTED": True,
            "FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {
            "weighted_rows_preflight": {
                "path": str(PREFLIGHT.relative_to(ROOT)),
                "result_id": preflight["result_id"],
                "sha256": _sha256(PREFLIGHT),
            }
        },
        "tier3_promotion_receipt": TIER3_PROMOTION_RECEIPT,
        "next_gate": "ASSEMBLE_THE_PROMOTED_WEIGHTED_ROWS_WITH_THE_MATCHED_SCHUR_FACTOR_AND_MINIMAL_VECTOR_GHOST_DETERMINANT",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate rigorously computes directed enclosures for R_Delta(K) and FP R_Delta(K^2) on the declared S2(1) x S2(2) regular Schur complement. It proves a uniform periodic-Bernoulli Euler--Maclaurin remainder for every required product heat moment, bounds the upper-incomplete spectral cutoff, combines those bounds with a positive-sum binary64 proof and the previously certified trace-class exterior tails, and records the passing 850-test Tier-3 promotion receipt. The coefficient-computed lifecycle is restricted to these two special-background weighted rows. This is not the full coupled vector ghost determinant, a generic-background form factor, complete Gamma1/Q1, a restored QME, or a Lorentzian causal, Hadamard, state-space, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def emit(*, check: bool) -> None:
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit(f"stale weighted-row certificate: {OUTPUT}")
    else:
        OUTPUT.write_text(rendered)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.emit:
        emit(check=False)
    if args.check:
        emit(check=True)
    if not args.emit and not args.check:
        print(json.dumps(build(), indent=2, sort_keys=True))
    print("PRODUCT S2xS2 SCHUR WEIGHTED ROWS: RIGOROUS ENCLOSURE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
