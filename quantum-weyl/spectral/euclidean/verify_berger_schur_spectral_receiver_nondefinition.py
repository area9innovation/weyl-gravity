#!/usr/bin/env python3
"""Independent exact replay of the Berger receiver nondefinition theorem."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator, ValidationError


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/BERGER_SCHUR_SPECTRAL_RECEIVER_NONDEFINITION_V1.json"
SCHEMA = HERE / "schema/berger-schur-spectral-receiver-nondefinition-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(row: dict[str, int]) -> Fraction:
    return Fraction(row["numerator"], row["denominator"])


def verify(certificate: dict | None = None) -> None:
    if certificate is None:
        certificate = json.loads(CERTIFICATE.read_text())
    try:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(certificate)
    except ValidationError as exc:
        raise ValueError("Berger receiver schema rejected payload") from exc

    for reference in certificate["dependencies"].values():
        assert _sha256(ROOT / reference["path"]) == reference["sha256"]
    for request in certificate["external_math_requests"].values():
        assert _sha256(ROOT / request["path"]) == request["sha256"]
        assert request["status"] == "ACCEPTED_NOT_LANDED"

    receiver = certificate["receiver"]
    matrix = sp.Matrix(receiver["ambiguity_matrix"])
    assert matrix.shape == (10, 10)
    assert matrix.rank() == 10 == receiver["ambiguity_rank"]
    assert len(matrix.T.nullspace()) == 0 == receiver["transpose_kernel_dimension"]

    expected_groups = {
        "I10": ["I10_123"],
        "I24": ["I24_123", "I24_213", "I24_312"],
        "I25": ["I25_123", "I25_213", "I25_312"],
        "I28": ["I28_123", "I28_132"],
        "I29": ["I29_123"],
    }
    observed_groups = {row["carrier"]: row["coordinates"] for row in receiver["carrier_ledger"]}
    assert observed_groups == expected_groups
    flattened = [coordinate for coordinates in expected_groups.values() for coordinate in coordinates]
    assert flattened == receiver["coordinate_order"]
    assert [row["coordinate"] for row in receiver["coordinate_ledger"]] == flattened
    assert all(row["complete_coordinate_status"] == "NONDEFINED" for row in receiver["coordinate_ledger"])
    assert all(row["complete_function_status"] == "NONDEFINED" for row in receiver["carrier_ledger"])
    assert receiver["complete_function_count"] == 0

    local = certificate["independent_local_scale_replay"]
    scalar = _fraction(local["scalar_curvature"])
    ricci2 = _fraction(local["ricci_squared"])
    assert _fraction(local["Wres_K_density_without_(4pi)^-2"]) == (scalar * scalar + 4 * ricci2) / 9 == Fraction(8, 3)
    assert _fraction(local["Wres_K2_density_without_(4pi)^-2"]) == (scalar * scalar + 2 * ricci2) / 27 == Fraction(4, 9)
    assert _fraction(local["dlogmu_logDet3_density_without_(4pi)^-2"]) == (5 * scalar * scalar + 22 * ricci2) / 54 == Fraction(22, 9)

    high_ref = certificate["dependencies"]["high_mode_obstruction"]
    high = json.loads((ROOT / high_ref["path"]).read_text())
    assert high["trace_ideal_disposition"]["first_insertion_absolute_trace_majorant"] == "DOES_NOT_EXIST"
    assert high["claim_flags"]["GLOBAL_DETERMINANT_OR_FINITE_TRACE_COMPUTED"] is False

    flags = certificate["claim_flags"]
    assert flags["SCALAR_SURROGATE_USED"] is False
    assert flags["M21_OR_M23_GLOBAL_PAYLOAD_LANDED"] is False
    assert flags["COMPLETE_FIVE_FUNCTIONS_COMPUTED"] is False
    assert flags["GLOBAL_DETERMINANT_OR_FINITE_TRACE_COMPUTED"] is False
    assert flags["QME_OR_LORENTZIAN_HADAMARD_PROMOTED"] is False
    assert certificate["paper12_disposition"] == "NO_UPDATE_COEFFICIENT_LIFECYCLE_UNCHANGED"
    print("Berger Schur spectral receiver nondefinition: PASS")


if __name__ == "__main__":
    verify()
