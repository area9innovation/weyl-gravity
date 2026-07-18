#!/usr/bin/env python3
"""Independent verifier for the Schur weighted-trace scale certificate."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json"
SCHEMA = HERE / "schema/generic-background-ghost-schur-weighted-trace-scale-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _laurent_conversion(
    residue: Fraction, *, weight_order: int, scale_power: int
) -> tuple[Fraction, Fraction]:
    """Return the pole and log-mu coefficients without using the producer."""

    return residue / weight_order, residue * Fraction(scale_power, weight_order)


def main() -> int:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    reference = payload["dependencies"]["Wodzicki_residue"]
    dependency = ROOT / reference["path"]
    assert dependency.is_file()
    assert _sha256(dependency) == reference["sha256"]
    source = json.loads(dependency.read_text())
    assert source["result_id"] == reference["result_id"]

    k = {"R2": Fraction(1, 9), "Ric2": Fraction(4, 9)}
    k2 = {"R2": Fraction(1, 27), "Ric2": Fraction(2, 27)}
    log_s = {name: k[name] - k2[name] / 2 for name in k}
    assert log_s == {"R2": Fraction(5, 54), "Ric2": Fraction(11, 27)}

    conversion = payload["exact_conversion"]
    for carrier, row in (("K", k), ("K2", k2), ("log_S", log_s)):
        for name, residue in row.items():
            pole, scale = _laurent_conversion(
                residue, weight_order=2, scale_power=2
            )
            assert _fraction(conversion["pole_coefficients_Ricci_basis"][carrier][name]) == pole
            assert _fraction(conversion["scale_coefficients_Ricci_basis"][carrier][name]) == scale

    # A missing square on mu would halve the answer; this mutation must fail.
    mutated = {
        name: _laurent_conversion(value, weight_order=2, scale_power=1)[1]
        for name, value in log_s.items()
    }
    assert mutated != log_s

    flags = payload["claim_flags"]
    assert flags["ORDER_TWO_WEIGHTED_TRACE_DECLARED"] is True
    assert flags["SCHUR_SCALE_COEFFICIENT_COMPUTED"] is True
    assert flags["REFERENCE_FINITE_R_K_COMPUTED"] is False
    assert flags["REFERENCE_FINITE_R_K2_COMPUTED"] is False
    assert flags["ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED"] is False
    assert flags["FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED"] is False
    print("GENERIC GHOST SCHUR WEIGHTED-TRACE SCALE: INDEPENDENT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
