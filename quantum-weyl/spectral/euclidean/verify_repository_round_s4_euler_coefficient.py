#!/usr/bin/env python3
"""Independent verifier for the repository round-S4 Euler coefficient."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json

from jsonschema import Draft202012Validator

try:
    from .repository_round_s4_euler_coefficient import (
        LEDGER,
        OUTPUT,
        SCHEMA,
        STANDARD,
        build,
        validate_claim_boundary,
    )
except ImportError:
    from repository_round_s4_euler_coefficient import (
        LEDGER,
        OUTPUT,
        SCHEMA,
        STANDARD,
        build,
        validate_claim_boundary,
    )


def verify() -> dict[str, object]:
    payload = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if payload != build():
        raise ValueError("repository round-S4 Euler certificate does not reproduce")

    standard = json.loads(STANDARD.read_text())
    ledger = json.loads(LEDGER.read_text())
    contributions = {
        row["factor_id"]: Fraction(row["signed_a_contribution"])
        for row in standard["coefficient_calculation"][
            "constant_curvature_factor_ledger"
        ]
    }
    total = sum(
        contributions[row["target_factor_id"]]
        for row in ledger["standard_factor_map"]
    )
    if total != Fraction(87, 20):
        raise ValueError("independent repository Euler sum drifted")
    proof = hashlib.sha256(
        json.dumps(
            {key: value for key, value in payload.items() if key != "proof_sha256"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    if proof != payload["proof_sha256"]:
        raise ValueError("repository Euler proof digest drifted")
    mutant = deepcopy(payload)
    mutant["claim_flags"]["REPOSITORY_C2_COEFFICIENT_COMPUTED"] = True
    try:
        validate_claim_boundary(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("round-S4-only C2 overclaim was accepted")
    return {
        "result_id": payload["result_id"],
        "a": str(total),
        "E4_coordinate": str(-total),
        "C2_status": "NOT_DETERMINED_ON_ROUND_S4",
        "status": "INDEPENDENT_REPLAY_ACCEPTED",
    }


def main() -> int:
    print(json.dumps(verify(), indent=2, sort_keys=True))
    print("repository round-S4 Euler coefficient independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
