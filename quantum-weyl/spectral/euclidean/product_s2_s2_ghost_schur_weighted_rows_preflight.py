#!/usr/bin/env python3
"""Numerical preflight for the weighted Schur rows on S2(1) x S2(2)."""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from math import factorial
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS_PREFLIGHT.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-schur-weighted-rows-preflight-v1.schema.json"
DEPENDENCIES = {
    "product_spectrum": HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_SPECTRAL_CARRIER.json",
    "product_det3": HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_DET3_ENCLOSURE.json",
    "weighted_trace_scale": HERE / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
}

CUTOFF = 2400
BINARY64_UNIT_ROUNDOFF = Fraction(1, 2**53)
TERM_RELATIVE_ERROR_BOUND = Fraction(1, 10**12)
REMAINDER_SUM_ENVELOPE = Fraction(2)
REMAINDER_ROUNDING_CUSHION = Fraction(1, 500_000_000)
BASE_VALIDATION_CUSHION = Decimal("1e-12")
HEAT_ORDER = 18
MP_DPS = 50
MELLIN_KEYS = (
    (1, 0, 2), (0, 1, 2),
    (1, 0, 3), (0, 1, 3),
    (2, 0, 4), (1, 1, 4), (0, 2, 4),
    (1, 0, 4), (0, 1, 4),
    (2, 0, 5), (1, 1, 5), (0, 2, 5),
)
SETTINGS = ((Fraction(1, 20), 10), (Fraction(1, 16), 12), (Fraction(1, 25), 10))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _gamma(count: int) -> Fraction:
    product = count * BINARY64_UNIT_ROUNDOFF
    return product / (1 - product)


def _sphere_heat_coefficients(order: int) -> dict[int, sp.Rational]:
    """Generate H(t)=sum_l(2l+1)e^{-t l(l+1)} by Euler--Maclaurin."""

    x, t = sp.symbols("x t")
    summand = (2 * x + 1) * sp.exp(-t * x * (x + 1))
    series = 1 / t + sp.Rational(1, 2) * summand.subs(x, 0)
    for index in range(1, order + 4):
        series -= (
            sp.bernoulli(2 * index)
            / sp.factorial(2 * index)
            * sp.diff(summand, x, 2 * index - 1).subs(x, 0)
        )
    expanded = sp.series(series, t, 0, order + 1).removeO().expand()
    return {
        power: sp.Rational(expanded.coeff(t, power))
        for power in range(-1, order + 1)
    }


def _moment_product_coefficients(
    heat: dict[int, sp.Rational], left_moment: int, right_moment: int, max_power: int
) -> dict[int, sp.Rational]:
    result: dict[int, sp.Rational] = {}
    for left_power, left_coefficient in heat.items():
        left_falling = sp.prod(left_power - offset for offset in range(left_moment))
        if left_falling == 0:
            continue
        for right_power, right_coefficient in heat.items():
            right_falling = sp.prod(right_power - offset for offset in range(right_moment))
            if right_falling == 0:
                continue
            power = left_power - left_moment + right_power - right_moment
            if power > max_power:
                continue
            coefficient = (
                (-1) ** (left_moment + right_moment)
                * left_coefficient
                * right_coefficient
                * sp.Rational(2) ** right_power
                * left_falling
                * right_falling
            )
            result[power] = sp.Rational(result.get(power, 0) + coefficient)
    return result


def _upper_incomplete_mellin_sum(
    left_moment: int, right_moment: int, mellin_order: int, split: mp.mpf, cutoff: int = 80
) -> mp.mpf:
    total = mp.mpf(0)
    prefactor = mp.mpf(factorial(mellin_order - 1))
    for ell in range(cutoff + 1):
        a = ell * (ell + 1)
        for emm in range(cutoff + 1):
            b = 2 * emm * (emm + 1)
            lam = a + b
            if lam == 0 or (left_moment and a == 0) or (right_moment and b == 0):
                continue
            argument = mp.mpf(lam) * split
            polynomial = sum(
                argument**power / factorial(power)
                for power in range(mellin_order)
            )
            total += (
                (2 * ell + 1)
                * (2 * emm + 1)
                * mp.mpf(a) ** left_moment
                * mp.mpf(b) ** right_moment
                * prefactor
                * mp.exp(-argument)
                * polynomial
                / mp.mpf(lam) ** mellin_order
            )
    return total


def _mellin_value(
    heat: dict[int, sp.Rational], key: tuple[int, int, int], split: Fraction, max_power: int
) -> tuple[mp.mpf, Fraction]:
    left_moment, right_moment, mellin_order = key
    coefficients = _moment_product_coefficients(
        heat, left_moment, right_moment, max_power
    )
    split_mp = mp.mpf(split.numerator) / split.denominator
    pole = sp.Rational(coefficients.get(-mellin_order, 0))
    pole_coefficient = Fraction(int(pole.p), int(pole.q))
    regular = mp.mpf(pole_coefficient.numerator) / pole_coefficient.denominator * mp.log(split_mp)
    for power, coefficient in coefficients.items():
        if power == -mellin_order:
            continue
        coefficient_mp = mp.mpf(int(coefficient.p)) / int(coefficient.q)
        regular += coefficient_mp * split_mp ** (mellin_order + power) / (
            mellin_order + power
        )
    regular += _upper_incomplete_mellin_sum(
        left_moment, right_moment, mellin_order, split_mp
    )
    finite_part = (
        regular
        - mp.digamma(mellin_order)
        * mp.mpf(pole_coefficient.numerator)
        / pole_coefficient.denominator
    ) / factorial(mellin_order - 1)
    residue = pole_coefficient / factorial(mellin_order - 1)
    return finite_part, residue


def _base_blocks(heat: dict[int, sp.Rational], split: Fraction, max_power: int) -> dict[str, Any]:
    values: dict[tuple[int, int, int], mp.mpf] = {}
    residues: dict[tuple[int, int, int], Fraction] = {}
    for key in MELLIN_KEYS:
        values[key], residues[key] = _mellin_value(heat, key, split, max_power)
    r_k = (
        mp.mpf(2) / 3 * (values[(1, 0, 2)] + 2 * values[(0, 1, 2)])
        + mp.mpf(4) / 3 * (values[(1, 0, 3)] + 4 * values[(0, 1, 3)])
        + mp.mpf(8) / 3 * (values[(1, 0, 4)] + 8 * values[(0, 1, 4)])
        - 6
    )
    r_k2 = (
        mp.mpf(4) / 9
        * (values[(2, 0, 4)] + 4 * values[(1, 1, 4)] + 4 * values[(0, 2, 4)])
        + mp.mpf(16) / 9
        * (values[(2, 0, 5)] + 6 * values[(1, 1, 5)] + 8 * values[(0, 2, 5)])
        - 2
    )
    residue_k = (
        Fraction(2, 3) * (residues[(1, 0, 2)] + 2 * residues[(0, 1, 2)])
        + Fraction(4, 3) * (residues[(1, 0, 3)] + 4 * residues[(0, 1, 3)])
    )
    residue_k2 = Fraction(4, 9) * (
        residues[(2, 0, 4)]
        + 4 * residues[(1, 1, 4)]
        + 4 * residues[(0, 2, 4)]
    )
    if residue_k != Fraction(19, 9) or residue_k2 != Fraction(14, 27):
        raise AssertionError("product weighted-trace pole replay drifted")
    return {
        "split": _q(split),
        "heat_max_power": max_power,
        "base_R_K": mp.nstr(r_k, 48),
        "base_FP_R_K2": mp.nstr(r_k2, 48),
        "residue_R_K": _q(residue_k),
        "residue_R_K2": _q(residue_k2),
    }


def _stable_remainder_partial(cutoff: int) -> tuple[float, float, int]:
    r_k = 0.0
    r_k2 = 0.0
    count = 0
    for ell in range(cutoff + 1):
        a = ell * (ell + 1)
        for emm in range(cutoff + 1):
            if (ell, emm) in {(0, 0), (1, 0), (0, 1)}:
                continue
            b = 2 * emm * (emm + 1)
            lam = a + b
            k1 = (2.0 / 3.0) * (a + 2 * b) / lam**2
            k2 = (4.0 / 3.0) * (a + 4 * b) / lam**3
            after_k2 = 0.0
            after_k3 = 0.0
            if ell:
                after_k2 += (a / lam) * (2 / lam) ** 3 / (1 - 2 / lam)
                after_k3 += (a / lam) * (2 / lam) ** 4 / (1 - 2 / lam)
            if emm:
                after_k2 += (b / lam) * (4 / lam) ** 3 / (1 - 4 / lam)
                after_k3 += (b / lam) * (4 / lam) ** 4 / (1 - 4 / lam)
            after_k2 /= 3
            after_k3 /= 3
            degeneracy = (2 * ell + 1) * (2 * emm + 1)
            r_k += degeneracy * after_k3
            r_k2 += degeneracy * (
                k2 * k2 + 2 * (k1 + k2) * after_k2 + after_k2 * after_k2
            )
            count += 1
    return r_k, r_k2, count


def _power_four_lattice_tail(cutoff: int) -> Fraction:
    x0 = Fraction(2 * cutoff + 3, 2)
    sum_5 = x0**-5 + Fraction(1, 4) * x0**-4
    sum_6 = x0**-6 + Fraction(1, 5) * x0**-5
    vertical = Fraction(1, 3) * sum_5 + Fraction(2, 3) * sum_6
    horizontal = Fraction(1, 12) * sum_5 + Fraction(1, 12) * sum_6
    return vertical + horizontal


def _remainder_bounds(cutoff: int, count: int, observed: tuple[float, float]) -> dict[str, Any]:
    x0 = Fraction(2 * cutoff + 3, 2)
    q_min = x0 * x0 + Fraction(1, 2)
    lam_min = q_min - Fraction(3, 4)
    comparison = 1 - Fraction(3, 4) / q_min
    lattice = _power_four_lattice_tail(cutoff)
    c_after_k3 = Fraction(1, 3) * (
        Fraction(16) / (1 - Fraction(2) / lam_min)
        + Fraction(256) / (1 - Fraction(4) / lam_min)
    )
    c_after_k2 = Fraction(1, 3) * (
        Fraction(8) / (1 - Fraction(2) / lam_min)
        + Fraction(64) / (1 - Fraction(4) / lam_min)
    )
    c_after_k1 = Fraction(1, 3) * (
        Fraction(4) / (1 - Fraction(2) / lam_min)
        + Fraction(16) / (1 - Fraction(4) / lam_min)
    )
    c_k2_remainder = Fraction(8, 3) * c_after_k2 + c_after_k1**2
    tail_k = c_after_k3 * lattice / comparison**4
    tail_k2 = c_k2_remainder * lattice / comparison**4
    summation_gamma = _gamma(count)
    per_sum_rounding_bound = REMAINDER_SUM_ENVELOPE * (
        summation_gamma * (1 + TERM_RELATIVE_ERROR_BOUND)
        + TERM_RELATIVE_ERROR_BOUND
    )
    if (
        max(observed) >= float(REMAINDER_SUM_ENVELOPE)
        or per_sum_rounding_bound >= REMAINDER_ROUNDING_CUSHION
    ):
        raise AssertionError("remainder rounding envelope drifted")
    return {
        "binary64_unit_roundoff": _q(BINARY64_UNIT_ROUNDOFF),
        "summand_count": count,
        "ordinary_summation_gamma": _q(summation_gamma),
        "per_term_relative_error_bound": _q(TERM_RELATIVE_ERROR_BOUND),
        "exact_sum_envelope": _q(REMAINDER_SUM_ENVELOPE),
        "derived_rounding_bound": _q(per_sum_rounding_bound),
        "declared_rounding_cushion": _q(REMAINDER_ROUNDING_CUSHION),
        "power_four_lattice_tail": _q(lattice),
        "R_K_exterior_tail_bound": _q(tail_k),
        "FP_R_K2_exterior_tail_bound": _q(tail_k2),
    }


def _candidate_intervals(
    settings: list[dict[str, Any]], partial: tuple[float, float], bounds: dict[str, Any]
) -> dict[str, Any]:
    base_k = [Decimal(row["base_R_K"]) for row in settings]
    base_k2 = [Decimal(row["base_FP_R_K2"]) for row in settings]
    round_cushion = Decimal(bounds["declared_rounding_cushion"]["numerator"]) / Decimal(
        bounds["declared_rounding_cushion"]["denominator"]
    )
    tail_k = Decimal(bounds["R_K_exterior_tail_bound"]["numerator"]) / Decimal(
        bounds["R_K_exterior_tail_bound"]["denominator"]
    )
    tail_k2 = Decimal(bounds["FP_R_K2_exterior_tail_bound"]["numerator"]) / Decimal(
        bounds["FP_R_K2_exterior_tail_bound"]["denominator"]
    )
    with localcontext() as context:
        context.prec = 50
        partial_k = Decimal.from_float(partial[0])
        partial_k2 = Decimal.from_float(partial[1])
        lower_k = min(base_k) - BASE_VALIDATION_CUSHION + partial_k - round_cushion
        upper_k = max(base_k) + BASE_VALIDATION_CUSHION + partial_k + round_cushion + tail_k
        lower_k2 = min(base_k2) - BASE_VALIDATION_CUSHION + partial_k2 - round_cushion
        upper_k2 = max(base_k2) + BASE_VALIDATION_CUSHION + partial_k2 + round_cushion + tail_k2
        split_lower = lower_k - upper_k2 / 2
        split_upper = upper_k - lower_k2 / 2
    return {
        "R_Delta_K": {"lower": format(lower_k, "f"), "upper": format(upper_k, "f")},
        "FP_R_Delta_K2": {"lower": format(lower_k2, "f"), "upper": format(upper_k2, "f")},
        "low_order_split_R_K_minus_half_R_K2": {
            "lower": format(split_lower, "f"),
            "upper": format(split_upper, "f"),
        },
        "status": "NUMERICAL_VALIDATION_INTERVAL_NOT_RIGOROUS_HEAT_REMAINDER_ENCLOSURE",
    }


def build() -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if (
        dependencies["product_spectrum"]["primed_mode_policy"]["total_exceptional_correction"] != "3^-6"
        or dependencies["product_det3"]["claim_flags"]["PRODUCT_REGULAR_COMPLEMENT_DET3_VALUE_COMPUTED"] is not True
        or dependencies["weighted_trace_scale"]["claim_flags"]["SCHUR_SCALE_COEFFICIENT_COMPUTED"] is not True
    ):
        raise ValueError("weighted-row dependency drifted")
    mp.mp.dps = MP_DPS
    heat = _sphere_heat_coefficients(HEAT_ORDER)
    settings = [_base_blocks(heat, split, max_power) for split, max_power in SETTINGS]
    partial_k, partial_k2, count = _stable_remainder_partial(CUTOFF)
    bounds = _remainder_bounds(CUTOFF, count, (partial_k, partial_k2))
    intervals = _candidate_intervals(settings, (partial_k, partial_k2), bounds)
    result = {
        "schema": "quantum-weyl-product-s2-s2-ghost-schur-weighted-rows-preflight-v1",
        "result_id": "PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS_PREFLIGHT",
        "result_state": "PRODUCT_WEIGHTED_ROWS_NUMERICALLY_STABILIZED_RIGOROUS_HEAT_REMAINDER_OPEN",
        "lifecycle_state": "NUMERICAL_PRECERTIFICATE_NOT_COEFFICIENT_COMPUTED",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": dependencies["product_spectrum"]["classical_commit"],
        "scope": {
            "background": "S2(1) x S2(2)",
            "weight": "Q=Delta_0 on the regular complement at mu_0=1",
            "exceptional_policy": "subtract (0,0),(1,0),(0,1) from every low-order product-zeta block; retain coupled factor 3^-6 separately",
        },
        "exact_subtraction_identity": {
            "K1": "2(a+2b)/(3 lambda^2)",
            "K2": "4(a+4b)/(3 lambda^3)",
            "K3": "8(a+8b)/(3 lambda^4)",
            "R_K_trace_class_remainder": "K-K1-K2-K3",
            "R_K2_meromorphic_block": "K1^2+2 K1 K2",
            "R_K2_trace_class_remainder": "K^2-K1^2-2 K1 K2",
            "exceptional_subtractions": "6 from K1+K2+K3 and 2 from K1^2+2K1K2",
        },
        "exact_pole_replay": {
            "Res_R_K": _q(Fraction(19, 9)),
            "half_Wres_K": _q(Fraction(19, 9)),
            "Res_R_K2": _q(Fraction(14, 27)),
            "half_Wres_K2": _q(Fraction(14, 27)),
        },
        "heat_subtraction_settings": settings,
        "base_validation_cushion": "1e-12 (empirical setting-stability allowance; not an Euler--Maclaurin remainder theorem)",
        "trace_class_remainders": {
            "rectangular_cutoff": CUTOFF,
            "R_K_partial": repr(partial_k),
            "FP_R_K2_partial": repr(partial_k2),
            "bounds": bounds,
        },
        "numerical_candidate_intervals": intervals,
        "claim_flags": {
            "PRODUCT_WEIGHTED_R_K_NUMERICAL_CANDIDATE": True,
            "PRODUCT_FINITE_PART_R_K2_NUMERICAL_CANDIDATE": True,
            "PRODUCT_WEIGHTED_TRACE_POLES_REPLAYED": True,
            "PRODUCT_TRACE_CLASS_REMAINDER_TAILS_RIGOROUSLY_BOUNDED": True,
            "PRODUCT_HEAT_EULER_MACLAURIN_REMAINDER_RIGOROUSLY_BOUNDED": False,
            "PRODUCT_WEIGHTED_R_K_COMPUTED": False,
            "PRODUCT_FINITE_PART_R_K2_COMPUTED": False,
            "FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "PROVE_A_UNIFORM_EULER_MACLAURIN_REMAINDER_FOR_THE_PRODUCT_HEAT_MOMENTS_THEN_PROMOTE_THE_TWO_WEIGHTED_ROWS",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL preflight derives the exact meromorphic/trace-class split for the two S2(1) x S2(2) Schur weighted rows, reproduces both Wodzicki pole residues, rigorously bounds the direct trace-class exterior tails and produces stable numerical candidates for R_Delta(K) and FP R_Delta(K^2). The displayed intervals are validation intervals, not rigorous coefficient enclosures, because the small-t Euler--Maclaurin heat remainder is not yet uniformly bounded. Accordingly both coefficient-computed flags remain false. This is not the full coupled ghost determinant, a generic-background form factor, Gamma1/Q1, a Lorentzian QME, state, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    true_flags = {
        "PRODUCT_WEIGHTED_R_K_NUMERICAL_CANDIDATE",
        "PRODUCT_FINITE_PART_R_K2_NUMERICAL_CANDIDATE",
        "PRODUCT_WEIGHTED_TRACE_POLES_REPLAYED",
        "PRODUCT_TRACE_CLASS_REMAINDER_TAILS_RIGOROUSLY_BOUNDED",
    }
    for name, flag in value["claim_flags"].items():
        if flag is not (name in true_flags):
            raise ValueError(f"claim flag crossed boundary: {name}")


def emit(*, check: bool) -> None:
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit(f"stale weighted-row preflight: {OUTPUT}")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
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
    print("PRODUCT S2xS2 SCHUR WEIGHTED ROWS: NUMERICAL PREFLIGHT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
