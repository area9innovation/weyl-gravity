#!/usr/bin/env python3
"""Rigorous minimal-vector determinant enclosure, held behind Tier 3."""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction
from math import factorial
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp
from mpmath.libmp import to_rational
import sympy as sp

from .product_s2_s2_ghost_schur_weighted_rows import (
    _full_em_heat_polynomial,
    _mellin_em_error_bound,
    _upper_mellin_cutoff_tail,
)
from .product_s2_s2_ghost_schur_weighted_rows_preflight import _moment_product_coefficients


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_DETERMINANT_PRECERTIFICATE.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-minimal-vector-determinant-precertificate-v1.schema.json"
DEPENDENCIES = {
    "carrier": HERE / "certificates/PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_CARRIER.json",
    "schur_assembly": HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_MODIFIED_DETERMINANT_PRECERTIFICATE.json",
}

CUTOFF = 2400
UPPER_CUTOFF = 80
SPLIT = Fraction(1, 20)
EM_ORDER = 18
MP_IV_DPS = 70
UNIT_ROUNDOFF = Fraction(1, 2**53)
OPERATION_BUDGET = 200
CONDITIONING_RESERVE = Fraction(16)
SMALL_THRESHOLD = Fraction(1, 100)
SMALL_TAYLOR_ORDER = 8
LARGE_TAYLOR_ORDER = 120


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


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
    product = count * UNIT_ROUNDOFF
    return product / (1 - product)


def _det3_mode_bounds(x: Fraction, order: int) -> tuple[Fraction, Fraction]:
    lower = sum((x**power / power for power in range(3, order + 1)), Fraction(0))
    remainder = x ** (order + 1) / ((order + 1) * (1 - x))
    return lower, lower + remainder


def _lattice_tail(cutoff: int) -> tuple[Fraction, Fraction]:
    x0 = Fraction(2 * cutoff + 3, 2)
    sum_x3 = x0**-3 + Fraction(1, 2) * x0**-2
    sum_x4 = x0**-4 + Fraction(1, 3) * x0**-3
    lattice = (
        Fraction(1, 2) * sum_x3
        + Fraction(125, 162) * sum_x4
        + Fraction(1, 4) * sum_x3
        + Fraction(125, 432) * sum_x4
    )
    q_min = x0 * x0 + Fraction(1, 2)
    lambda_comparison = 1 - Fraction(3, 4) / q_min
    return lattice, lambda_comparison


def _det3_tail_bound(shift: int, cutoff: int) -> Fraction:
    lattice, comparison = _lattice_tail(cutoff)
    x0 = Fraction(2 * cutoff + 3, 2)
    lambda_min = x0 * x0 - Fraction(1, 4)
    return (
        Fraction(shift**3, 3)
        * lattice
        / comparison**3
        / (1 - Fraction(shift) / lambda_min)
    )


def _det3_enclosure(shift: int, component: str) -> tuple[Any, dict[str, Any]]:
    large_lower = Fraction(0)
    large_upper = Fraction(0)
    small_sum = 0.0
    small_x3 = 0.0
    small_count = 0
    large_count = 0
    for ell in range(CUTOFF + 1):
        a = ell * (ell + 1)
        for emm in range(CUTOFF + 1):
            active = ell > 0 if component == "first" else emm > 0
            exceptional = (ell, emm) == ((1, 0) if component == "first" else (0, 1))
            if not active or exceptional:
                continue
            lam = a + 2 * emm * (emm + 1)
            degeneracy = (2 * ell + 1) * (2 * emm + 1)
            x = Fraction(shift, lam)
            if x > SMALL_THRESHOLD:
                lower, upper = _det3_mode_bounds(x, LARGE_TAYLOR_ORDER)
                large_lower += degeneracy * lower
                large_upper += degeneracy * upper
                large_count += 1
            else:
                xf = float(x)
                power = xf**3
                value = power / 3
                for order in range(4, SMALL_TAYLOR_ORDER + 1):
                    power *= xf
                    value += power / order
                small_sum += degeneracy * value
                small_x3 += degeneracy * xf**3
                small_count += 1
    per_term = CONDITIONING_RESERVE * _gamma(OPERATION_BUDGET)
    summation = _gamma(small_count)
    relative = per_term + summation * (1 + per_term)
    sum_envelope = Fraction(1 if component == "first" else 4)
    x3_envelope = Fraction(20)
    if Fraction.from_float(small_sum) / (1 - relative) >= sum_envelope:
        raise AssertionError("minimal-vector det3 sum envelope failed")
    if Fraction.from_float(small_x3) / (1 - relative) >= x3_envelope:
        raise AssertionError("minimal-vector x3 envelope failed")
    rounding = sum_envelope * relative
    taylor = (
        SMALL_THRESHOLD ** (SMALL_TAYLOR_ORDER - 2)
        * x3_envelope
        / ((SMALL_TAYLOR_ORDER + 1) * (1 - SMALL_THRESHOLD))
    )
    exterior = _det3_tail_bound(shift, CUTOFF)
    positive = _ivq(large_lower) + mp.iv.mpf(Fraction.from_float(small_sum).numerator) / Fraction.from_float(small_sum).denominator
    positive += mp.iv.mpf([-_ivq(rounding), _ivq(rounding + taylor + exterior + (large_upper - large_lower))])
    log_det3 = -positive
    proof = {
        "component": component,
        "shift": shift,
        "rectangular_cutoff": CUTOFF,
        "large_mode_count": large_count,
        "large_taylor_order": LARGE_TAYLOR_ORDER,
        "small_mode_count": small_count,
        "small_taylor_order": SMALL_TAYLOR_ORDER,
        "small_sum_binary64": repr(small_sum),
        "small_x3_binary64": repr(small_x3),
        "per_term_relative_error_bound": _q(per_term),
        "summation_gamma": _q(summation),
        "rounding_bound": _q(rounding),
        "small_taylor_remainder_bound": _q(taylor),
        "exterior_tail_bound": _q(exterior),
    }
    return log_det3, proof


def _product_zeta_interval(heat: dict[int, sp.Rational], order: int) -> tuple[Any, Fraction, Fraction]:
    coefficients = _moment_product_coefficients(heat, 0, 0, 2 * EM_ORDER - 1)
    coefficients[0] = sp.Rational(coefficients.get(0, 0) - 1)
    split_iv = _ivq(SPLIT)
    pole = sp.Rational(coefficients.get(-order, 0))
    regular = _ivq(pole) * mp.iv.log(split_iv)
    for power, coefficient in coefficients.items():
        if power != -order:
            regular += _ivq(coefficient) * split_iv ** (order + power) / (order + power)
    upper = mp.iv.mpf(0)
    for ell in range(UPPER_CUTOFF + 1):
        a = ell * (ell + 1)
        for emm in range(UPPER_CUTOFF + 1):
            lam = a + 2 * emm * (emm + 1)
            if lam == 0:
                continue
            argument = _ivq(lam) * split_iv
            polynomial = sum((argument**power / factorial(power) for power in range(order)), mp.iv.mpf(0))
            upper += (
                (2 * ell + 1)
                * (2 * emm + 1)
                * factorial(order - 1)
                * mp.iv.exp(-argument)
                * polynomial
                / lam**order
            )
    harmonic = sum((Fraction(1, value) for value in range(1, order)), Fraction(0))
    value = (regular + upper - _ivq(pole) * (_ivq(harmonic) - mp.iv.euler)) / factorial(order - 1)
    em_error = _mellin_em_error_bound(heat, (0, 0, order))
    cutoff_error = _upper_mellin_cutoff_tail((0, 0, order))
    return value + mp.iv.mpf([-_ivq(em_error + cutoff_error), _ivq(em_error + cutoff_error)]), em_error, cutoff_error


def build() -> dict[str, Any]:
    inputs = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if (
        inputs["carrier"]["claim_flags"]["PRODUCT_MINIMAL_VECTOR_MODE_CARRIER_SUPPLIED"] is not True
        or inputs["schur_assembly"]["tier3_blocker"]["status"] != "FAILED_NOT_A_PASS"
    ):
        raise ValueError("minimal-vector determinant dependencies drifted")
    mp.mp.dps = MP_IV_DPS + 30
    mp.iv.dps = MP_IV_DPS
    heat = _full_em_heat_polynomial(EM_ORDER)
    product_1, em_1, cutoff_1 = _product_zeta_interval(heat, 1)
    product_2, em_2, cutoff_2 = _product_zeta_interval(heat, 2)
    left_fp_1 = 2 * mp.iv.euler - 1
    right_fp_1 = (left_fp_1 - mp.iv.log(2)) / 2
    first_zeta_1 = product_1 - right_fp_1 - _ivq(Fraction(3, 2))
    second_zeta_1 = product_1 - left_fp_1 - _ivq(Fraction(3, 4))
    first_zeta_2 = product_2 - _ivq(Fraction(1, 4)) - _ivq(Fraction(3, 4))
    second_zeta_2 = product_2 - 1 - _ivq(Fraction(3, 16))
    det3_first, proof_first = _det3_enclosure(2, "first")
    det3_second, proof_second = _det3_enclosure(4, "second")
    block_first = det3_first - 2 * first_zeta_1 - 2 * first_zeta_2
    block_second = det3_second - 4 * second_zeta_1 - 8 * second_zeta_2
    weighted_total = 2 * (block_first + block_second)
    zeta_total = weighted_total - 10
    schur = inputs["schur_assembly"]["directed_enclosures"]["coupled_schur_log"]
    full_weighted = weighted_total + mp.iv.mpf([schur["lower"], schur["upper"]])
    result = {
        "schema": "quantum-weyl-product-s2-s2-ghost-minimal-vector-determinant-precertificate-v1",
        "result_id": "PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_DETERMINANT_PRECERTIFICATE",
        "result_state": "MINIMAL_VECTOR_AND_FULL_WEIGHTED_GHOST_ENCLOSURES_DERIVED_TIER3_BLOCKED",
        "lifecycle_state": "PRECERTIFICATE_TIER3_FAILED_NO_PROMOTION",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": inputs["carrier"]["classical_commit"],
        "scope": inputs["carrier"]["scope"],
        "product_zeta_rows": {
            "FP_product_zeta_at_1": {"lower": _endpoint(product_1, 0), "upper": _endpoint(product_1, 1)},
            "FP_product_zeta_at_2": {"lower": _endpoint(product_2, 0), "upper": _endpoint(product_2, 1)},
            "EM_error_at_1": _q(em_1),
            "EM_error_at_2": _q(em_2),
            "upper_cutoff_error_at_1": _q(cutoff_1),
            "upper_cutoff_error_at_2": _q(cutoff_2),
            "sphere_subtractions": "FP zeta_S2(1)=2 EulerGamma-1, zeta_S2(2)=1, and zeta_(2 Delta)(s)=2^-s zeta_Delta(s)",
        },
        "active_zeta_rows": {
            "first_FP_zeta_1": {"lower": _endpoint(first_zeta_1, 0), "upper": _endpoint(first_zeta_1, 1)},
            "first_FP_zeta_2": {"lower": _endpoint(first_zeta_2, 0), "upper": _endpoint(first_zeta_2, 1)},
            "second_FP_zeta_1": {"lower": _endpoint(second_zeta_1, 0), "upper": _endpoint(second_zeta_1, 1)},
            "second_FP_zeta_2": {"lower": _endpoint(second_zeta_2, 0), "upper": _endpoint(second_zeta_2, 1)},
        },
        "det3_proofs": [proof_first, proof_second],
        "directed_enclosures": {
            "first_component_weighted_modified": {"lower": _endpoint(block_first, 0), "upper": _endpoint(block_first, 1)},
            "second_component_weighted_modified": {"lower": _endpoint(block_second, 0), "upper": _endpoint(block_second, 1)},
            "two_polarization_minimal_vector_weighted": {"lower": _endpoint(weighted_total, 0), "upper": _endpoint(weighted_total, 1)},
            "two_polarization_minimal_vector_zeta": {"lower": _endpoint(zeta_total, 0), "upper": _endpoint(zeta_total, 1)},
            "full_vector_plus_schur_weighted": {"lower": _endpoint(full_weighted, 0), "upper": _endpoint(full_weighted, 1)},
        },
        "claim_flags": {
            "MINIMAL_VECTOR_RIGOROUS_ENCLOSURE_DERIVED": True,
            "FULL_VECTOR_PLUS_SCHUR_WEIGHTED_ENCLOSURE_DERIVED": True,
            "MINIMAL_VECTOR_INFINITE_WEIGHTED_DETERMINANT_COMPUTED": False,
            "FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "tier3_blocker": inputs["schur_assembly"]["tier3_blocker"],
        "dependencies": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": inputs[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "next_gate": "RECONCILE_AND_PASS_TIER3_THEN_PROMOTE_THE_FULL_WEIGHTED_PRODUCT_GHOST_ENCLOSURE_AND_INSERT_IT_IN_THE_REMAINING_BV_LEDGER",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL precertificate rigorously derives the two active minimal-vector modified determinants, their two-polarization weighted and separately zeta-regularized totals, and the selected full vector-plus-Schur weighted enclosure on S2(1) x S2(2). The standard computed flags remain false because the inherited 830-test Tier-3 promotion run failed on stale receipts outside this spectral package. This special-background determinant is not a generic-background form factor, complete BV ledger, Gamma1/Q1, restored QME, or Lorentzian causal, Hadamard, state-space, particle, positivity, scattering or unitarity theorem."
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
            raise SystemExit(f"stale minimal-vector determinant precertificate: {OUTPUT}")
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
    print("PRODUCT S2xS2 GHOST MINIMAL VECTOR DETERMINANT: PRECERTIFICATE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
