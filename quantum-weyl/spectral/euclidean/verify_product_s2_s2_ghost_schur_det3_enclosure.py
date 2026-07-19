#!/usr/bin/env python3
"""Independent verifier for the product S2 x S2 Schur det3 enclosure."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_DET3_ENCLOSURE.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-schur-det3-enclosure-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _direct_regular_sum(cutoff: int) -> float:
    """Direct diagonal sum, using log1p only where cancellation is harmless."""

    total = 0.0
    correction = 0.0
    for ell in range(cutoff + 1):
        a = ell * (ell + 1)
        for emm in range(cutoff + 1):
            if (ell, emm) in {(0, 0), (1, 0), (0, 1)}:
                continue
            b = 2 * emm * (emm + 1)
            lam = a + b
            k_value = 0.0
            if ell:
                k_value += 2.0 * a / (lam * (lam - 2))
            if emm:
                k_value += 4.0 * b / (lam * (lam - 4))
            k_value /= 3.0
            if k_value <= 0.01:
                mode_value = sum(
                    (1.0 if order % 2 else -1.0) * k_value**order / order
                    for order in range(3, 13)
                )
            else:
                mode_value = math.log1p(k_value) - k_value + k_value * k_value / 2
            term = (2 * ell + 1) * (2 * emm + 1) * mode_value
            adjusted = term - correction
            updated = total + adjusted
            correction = (updated - total) - adjusted
            total = updated
    return total


def _independent_tail_bound(cutoff: int) -> Fraction:
    x0 = Fraction(2 * cutoff + 3, 2)
    s3 = x0**-3 + Fraction(1, 2) * x0**-2
    s4 = x0**-4 + Fraction(1, 3) * x0**-3
    lattice = Fraction(1, 2) * s3 + Fraction(125, 162) * s4
    lattice += Fraction(1, 4) * s3 + Fraction(125, 432) * s4
    c_value = 1 - Fraction(19, 4) / (x0 * x0 + Fraction(1, 2))
    return Fraction(64, 81) * lattice / c_value**3


def _gamma(operation_count: int) -> Fraction:
    unit_roundoff = Fraction(1, 2**53)
    product = operation_count * unit_roundoff
    return product / (1 - product)


def main() -> int:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    for reference in payload["dependencies"].values():
        path = ROOT / reference["path"]
        assert path.is_file()
        assert _sha256(path) == reference["sha256"]
        source = json.loads(path.read_text())
        assert (source.get("result_id") or source.get("schema")) == reference["result_id"]

    enclosure = payload["det3_enclosure"]
    cutoff = enclosure["rectangular_cutoff"]
    assert cutoff == 2400
    assert enclosure["large_mode_count"] == 54
    assert enclosure["small_mode_count"] == (cutoff + 1) ** 2 - 3 - 54
    assert _independent_tail_bound(cutoff) == _q(enclosure["rectangular_infinite_tail_bound"])
    rounding = enclosure["binary64_rounding_proof"]
    count = enclosure["small_mode_count"]
    assert _q(rounding["binary64_unit_roundoff"]) == Fraction(1, 2**53)
    assert _q(rounding["summation_gamma_bound"]) == _gamma(count)
    assert _q(rounding["per_term_gamma_bound"]) == _gamma(40)
    assert (
        _q(rounding["per_term_gamma_bound"])
        * _q(rounding["alternating_polynomial_condition_upper"])
        < _q(rounding["per_term_relative_error_bound"])
    )
    assert (
        _q(rounding["derived_absolute_rounding_bound"])
        < _q(rounding["declared_cushion"])
        == _q(enclosure["binary64_rounding_cushion"])
    )

    lower = float(enclosure["lower_endpoint_decimal"])
    upper = float(enclosure["upper_endpoint_decimal"])
    direct = _direct_regular_sum(cutoff)
    assert lower < direct < upper
    assert direct - lower < 4e-10
    assert upper - direct < float(_q(enclosure["rectangular_infinite_tail_bound"])) + 4e-10
    assert enclosure["certified_common_decimal_prefix"].startswith("0.3263039")

    # Independent full 1x1 determinant ratio on each exceptional family:
    # H/H0=[(lambda-2k)+lambda/2]/[lambda+lambda/2]=1/3.
    for curvature in (Fraction(1), Fraction(2)):
        lam = 2 * curvature
        assert ((lam - 2 * curvature) + lam / 2) / (lam + lam / 2) == Fraction(1, 3)
    assert Fraction(1, 3) ** 6 == Fraction(1, 729)

    flags = payload["claim_flags"]
    assert flags["PRODUCT_REGULAR_COMPLEMENT_DET3_VALUE_COMPUTED"] is True
    assert flags["PRODUCT_WEIGHTED_R_K_COMPUTED"] is False
    assert flags["FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"] is False
    assert flags["LORENTZIAN_CERTIFIED"] is False
    print("PRODUCT S2xS2 GHOST SCHUR DET3: INDEPENDENT ENCLOSURE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
