#!/usr/bin/env python3
"""Independent replay of the repository Ricci-flat coefficient match."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json

from spectral.euclidean.coefficient_reconstruction import ricci_flat_operator_beta1
from spectral.euclidean.nonconformal_coefficient_match_receiver import (
    validate_nonconformal_coefficient_match,
)
from spectral.euclidean.repository_ricci_flat_coefficient_match import (
    BACKGROUND_OUTPUT,
    CALCULATION_OUTPUT,
    MEASURE_OUTPUT,
    OUTPUT,
    PARITY_OUTPUT,
    REGULATOR_OUTPUT,
    ROOT,
    ZERO_MODE_OUTPUT,
    build,
)


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _self_digest(value: dict) -> bool:
    payload = dict(value)
    expected = payload.pop("proof_sha256")
    return expected == _canonical_hash(payload)


def _fraction(value: dict) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> dict:
    paths = (
        BACKGROUND_OUTPUT, MEASURE_OUTPUT, REGULATOR_OUTPUT, ZERO_MODE_OUTPUT,
        PARITY_OUTPUT, CALCULATION_OUTPUT, OUTPUT,
    )
    values = tuple(json.loads(path.read_text()) for path in paths)
    if values != build():
        raise ValueError("repository Ricci-flat coefficient artifacts do not reproduce")
    if not all(_self_digest(value) for value in values[:-1]):
        raise ValueError("Ricci-flat supporting proof digest drifted")

    background, measure, regulator, zero_modes, parity, calculation, result = values
    invariants = background["exact_invariants"]
    if (
        _fraction(invariants["R"]) != 0
        or _fraction(invariants["Ricci_squared"]) != 0
        or _fraction(invariants["C2"]) != Fraction(3, 256)
        or _fraction(invariants["E4"]) != Fraction(3, 256)
    ):
        raise ValueError("independent Euclidean-Schwarzschild invariant replay failed")

    beta2, beta1, beta0 = (ricci_flat_operator_beta1(spin) for spin in (2, 1, 0))
    expected_beta = [beta2 - beta1, -beta0, beta2 - beta1, -(beta1 - beta0)]
    rows = calculation["factor_contributions"]
    if [_fraction(row["ricci_flat_beta1_contribution"]) for row in rows] != expected_beta:
        raise ValueError("independent Ricci-flat beta1 factor replay failed")
    totals = {
        name: sum((_fraction(row["coordinates"][name]) for row in rows), Fraction(0))
        for name in ("C2", "E4", "CdualC", "BoxR")
    }
    if totals != {
        "C2": Fraction(199, 30),
        "E4": Fraction(-87, 20),
        "CdualC": Fraction(0),
        "BoxR": Fraction(0),
    } or totals["C2"] + totals["E4"] != Fraction(137, 60):
        raise ValueError("independent repository coefficient sum failed")
    if (
        measure["nonminimal_quartet_superdeterminant"] != "1"
        or regulator["factor_count"] != 4
        or zero_modes["local_b4_modified_by_finite_zero_modes"] is not False
        or _fraction(parity["CdualC_coefficient"]) != 0
    ):
        raise ValueError("independent measure/regulator policy replay failed")
    receipt = validate_nonconformal_coefficient_match(result, repository_root=ROOT)
    print("repository Ricci-flat coefficient match independent verification: PASS")
    return receipt


if __name__ == "__main__":
    verify()
