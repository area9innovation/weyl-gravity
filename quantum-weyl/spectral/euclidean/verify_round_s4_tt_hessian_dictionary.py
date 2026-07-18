#!/usr/bin/env python3
"""Independent replay of the physical round-S4 TT Hessian dictionary."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from jsonschema import Draft202012Validator

try:
    from .tt_hessian_dictionary_receiver import (
        ROOT,
        SCHEMA,
        proof_hash,
        validate_tt_hessian_dictionary,
    )
except ImportError:
    from tt_hessian_dictionary_receiver import (
        ROOT,
        SCHEMA,
        proof_hash,
        validate_tt_hessian_dictionary,
    )


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json"
READINESS = HERE / "certificates/REPOSITORY_TT_HESSIAN_NORMALIZATION_READINESS.json"


def verify() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text())
    readiness = json.loads(READINESS.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    # Replay equation (2.22) without importing the producer.
    shifts = [2 - (k - 1) * (k + 2) for k in (0, 1)]
    if shifts != [4, 2]:
        raise ValueError("independent spin-two factor specialization failed")
    lower, upper = sorted(shifts)
    monic = (Fraction(lower * upper), Fraction(lower + upper), Fraction(1))
    kappa = Fraction(1, 2)
    normalized = tuple(kappa * coefficient for coefficient in monic)
    if monic != (Fraction(8), Fraction(6), Fraction(1)) or normalized != (
        Fraction(4),
        Fraction(3),
        Fraction(1, 2),
    ):
        raise ValueError("independent normalized polynomial replay failed")

    action = readiness["repository_action_normalization"]
    if not (
        action["curvature_identity"]["verified"] is True
        and action["unit_coefficient_verified"] is True
        and payload["flat_tt_leading_symbol"]["Hessian_leading_coefficient"]
        == {"numerator": normalized[2].numerator, "denominator": normalized[2].denominator}
    ):
        raise ValueError("independent repository action convention replay failed")
    if not (
        payload["operator_dictionary"]["lower_factor"]
        == f"Delta_2_perp({lower})"
        and payload["operator_dictionary"]["upper_factor"]
        == f"Delta_2_perp({upper})"
        and payload["proof_sha256"] == proof_hash(payload)
    ):
        raise ValueError("independent dictionary or proof digest replay failed")

    receipt = validate_tt_hessian_dictionary(
        payload,
        repository_root=ROOT,
        expected_classical_commit=readiness["classical_commit"],
    )
    if receipt["status"] != "SEMANTIC_RECEIVER_ACCEPTED":
        raise ValueError("strict TT Hessian receiver did not accept physical dictionary")
    return {
        "result_id": payload["result_id"],
        "classical_commit": payload["classical_commit"],
        "source_shifts_by_depth": shifts,
        "normalized_polynomial_ascending": [str(value) for value in normalized],
        "proof_digest_verified": True,
        "strict_receiver_status": receipt["status"],
        "status": "INDEPENDENT_REPLAY_ACCEPTED",
    }


def main() -> int:
    value = verify()
    print(json.dumps(value, indent=2, sort_keys=True))
    print("repository round-S4 TT Hessian independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
