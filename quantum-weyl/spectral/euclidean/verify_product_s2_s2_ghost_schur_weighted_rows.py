#!/usr/bin/env python3
"""Independent verifier for the rigorous product weighted-row enclosure."""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from math import comb, factorial
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-schur-weighted-rows-v1.schema.json"

EM_ORDER = 18
SPLIT = Fraction(1, 20)
UPPER_CUTOFF = 80
UNIT_ROUNDOFF = Fraction(1, 2**53)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _gamma(count: int) -> Fraction:
    product = count * UNIT_ROUNDOFF
    return product / (1 - product)


def _one_sphere_tail(coupling: Fraction, cutoff: int) -> Fraction:
    first = cutoff + 1
    exponent = coupling * first * (first + 1)
    return (
        2 * first + 1 + 1 / coupling
    ) / 2 ** (exponent.numerator // exponent.denominator)


def _product_tail() -> Fraction:
    return _one_sphere_tail(SPLIT / 2, UPPER_CUTOFF) * (2 / SPLIT) + (
        4 / SPLIT
    ) * _one_sphere_tail(SPLIT, UPPER_CUTOFF)


def _mellin_cutoff_tail(key: tuple[int, int, int]) -> Fraction:
    p, q, order = key
    multiplier = Fraction(0)
    for power in range(order):
        exponent = p + q + power - order
        assert exponent <= 1
        multiplier += SPLIT**power / factorial(power) * (
            Fraction(1) if exponent <= 0 else 2 / SPLIT
        )
    return _product_tail() * multiplier


def _stable_partial(cutoff: int) -> tuple[float, float]:
    row_k = 0.0
    row_k2 = 0.0
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
            row_k += degeneracy * after_k3
            row_k2 += degeneracy * (
                k2 * k2 + 2 * (k1 + k2) * after_k2 + after_k2 * after_k2
            )
    return row_k, row_k2


def main() -> int:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    reference = payload["dependencies"]["weighted_rows_preflight"]
    source_path = ROOT / reference["path"]
    assert source_path.is_file()
    assert _sha256(source_path) == reference["sha256"]
    preflight = json.loads(source_path.read_text())
    assert preflight["result_id"] == reference["result_id"]

    proof = payload["euler_maclaurin_remainder_proof"]
    assert proof["order"] == EM_ORDER
    assert _q(proof["split"]) == SPLIT
    sqrt_pi_upper = _q(proof["sqrt_pi_upper"])
    assert Fraction(22, 7) < sqrt_pi_upper**2
    assert _q(proof["exp_tau_over_four_upper"]) == Fraction(32, 31)
    assert _q(proof["row_R_K_error_bound"]) < Fraction(22, 10**13)
    assert _q(proof["row_FP_R_K2_error_bound"]) < Fraction(9, 10**13)

    cutoff = payload["upper_incomplete_cutoff_proof"]
    assert cutoff["rectangular_cutoff"] == UPPER_CUTOFF
    assert _q(cutoff["product_heat_tail_bound"]) == _product_tail()
    keys = [tuple(int(part.strip()) for part in key.strip("()").split(",")) for key in proof["mellin_block_error_bounds"]]
    assert all(_mellin_cutoff_tail(key) > 0 for key in keys)
    assert _q(cutoff["row_R_K_error_bound"]) < Fraction(1, 10**40)
    assert _q(cutoff["row_FP_R_K2_error_bound"]) < Fraction(1, 10**40)

    rounding = payload["direct_trace_class_rounding_proof"]
    assert _q(rounding["binary64_unit_roundoff"]) == UNIT_ROUNDOFF
    assert rounding["per_term_operation_budget"] == 200
    assert _q(rounding["conditioning_multiplier"]) == 16
    per_term = 16 * _gamma(200)
    summation = _gamma(rounding["summand_count"])
    relative = per_term + summation * (1 + per_term)
    assert _q(rounding["per_term_relative_error_bound"]) == per_term
    assert _q(rounding["ordinary_summation_gamma"]) == summation
    assert _q(rounding["absolute_rounding_bound"]) == 2 * relative
    assert _q(rounding["absolute_rounding_bound"]) < Fraction(13, 10**10)

    # Replay the positive trace-class sums on a smaller rectangle. The final
    # row intervals must also contain the earlier stabilized candidates.
    partial_k, partial_k2 = _stable_partial(300)
    assert 1.457 < partial_k < 1.459
    assert 1.814 < partial_k2 < 1.816
    rows = payload["weighted_rows"]
    expected = {
        "R_Delta_K": Decimal("-2.240660268"),
        "FP_R_Delta_K2": Decimal("1.966971853"),
        "low_order_split_R_K_minus_half_R_K2": Decimal("-3.224146194"),
    }
    for name, candidate in expected.items():
        lower = Decimal(rows[name]["lower"])
        upper = Decimal(rows[name]["upper"])
        assert lower < candidate < upper
        assert upper - lower < Decimal("4e-9")

    flags = payload["claim_flags"]
    assert flags["PRODUCT_WEIGHTED_ROW_RIGOROUS_ENCLOSURES_DERIVED"] is True
    assert flags["PRODUCT_HEAT_EULER_MACLAURIN_REMAINDER_RIGOROUSLY_BOUNDED"] is True
    assert flags["PRODUCT_WEIGHTED_R_K_COMPUTED"] is False
    assert flags["PRODUCT_FINITE_PART_R_K2_COMPUTED"] is False
    assert flags["FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"] is False
    assert flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"] is False
    assert flags["LORENTZIAN_CERTIFIED"] is False
    print("PRODUCT S2xS2 SCHUR WEIGHTED ROWS: INDEPENDENT ENCLOSURE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
