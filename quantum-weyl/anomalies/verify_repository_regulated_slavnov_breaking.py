#!/usr/bin/env python3
"""Independent replay of the coefficient-bearing repository Slavnov breaking."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json

from anomalies.regulated_slavnov_breaking_preflight import (
    RAW_BASIS,
    validate_regulated_breaking_export,
)
from anomalies.repository_regulated_slavnov_breaking import (
    ANTIFIELD_COMPLETION_OUTPUT,
    GAUGE_DEPENDENCE_OUTPUT,
    MEASURE_CONTOUR_OUTPUT,
    OUTPUT,
    QME_OUTPUT,
    REGULARIZATION_DEPENDENCE_OUTPUT,
    ROOT,
    SLAVNOV_ACTION_OUTPUT,
    TOTAL_DERIVATIVE_OUTPUT,
    WESS_ZUMINO_OUTPUT,
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
        MEASURE_CONTOUR_OUTPUT, SLAVNOV_ACTION_OUTPUT, TOTAL_DERIVATIVE_OUTPUT,
        GAUGE_DEPENDENCE_OUTPUT, REGULARIZATION_DEPENDENCE_OUTPUT,
        ANTIFIELD_COMPLETION_OUTPUT, WESS_ZUMINO_OUTPUT, QME_OUTPUT, OUTPUT,
    )
    values = tuple(json.loads(path.read_text()) for path in paths)
    if values != build():
        raise ValueError("regulated repository Slavnov artifacts do not reproduce")
    if not all(_self_digest(value) for value in values[:-1]):
        raise ValueError("regulated Slavnov supporting proof digest drifted")
    measure, action, total, gauge, regularization, antifield, wz, qme, result = values
    coefficients = result["coefficients"]
    observed = tuple(_fraction(coefficients[key]) for key in RAW_BASIS)
    if observed != (Fraction(199, 30), Fraction(-87, 20), Fraction(0), Fraction(0)):
        raise ValueError("regulated Slavnov coordinate replay failed")
    if (
        action["raw_coordinates"] != coefficients
        or action["top_form_insertion"] != "omega[(199/30) C2-(87/20) E4] vol_g"
        or total["quotient_remainder"] != "0"
        or gauge["status"] != "DEPENDENT_DECOMPOSED"
        or regularization["primitive"] != "(-1/12) R2 for omega BoxR in project conventions"
        or antifield["positive_antifield_components"] != []
        or wz["status"] != "VERIFIED"
        or qme["nonzero_nontrivial_coordinates"] != ["ANOM_OMEGA_C2", "ANOM_OMEGA_E4"]
        or qme["status"] != "OBSTRUCTED_STRICT_FIELD_CONTENT"
        or measure["global_phase"] != "OPEN_NOT_USED_FOR_LOCAL_SLAVNOV_CLASS"
    ):
        raise ValueError("independent Slavnov decomposition replay failed")
    receipt = validate_regulated_breaking_export(result, repository_root=ROOT)
    if receipt != {
        "cohomology_coordinates": [
            {"numerator": 199, "denominator": 30},
            {"numerator": -87, "denominator": 20},
            {"numerator": 0, "denominator": 1},
        ],
        "exact_coordinate": {"numerator": 0, "denominator": 1},
        "classification": "NONTRIVIAL",
        "qme_disposition": "OBSTRUCTED_STRICT_FIELD_CONTENT",
        "insertion_decomposition": "COMPLETE_RECEIVER_INPUT",
    }:
        raise ValueError("regulated Slavnov receiver receipt drifted")
    print("regulated repository Slavnov breaking independent verification: PASS")
    return receipt


if __name__ == "__main__":
    verify()
