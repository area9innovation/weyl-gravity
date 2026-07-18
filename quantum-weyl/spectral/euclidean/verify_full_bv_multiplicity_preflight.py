"""Independent verifier for the repository full-BV multiplicity preflight."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator

from .full_bv_multiplicity_preflight import (
    EXPORT_SCHEMA,
    OUTPUT,
    ROOT,
    SCHEMA,
    build,
    transverse_traceless_rank_4d,
    validate_claim_boundary,
)


def verify() -> dict:
    checked = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    export_schema = json.loads(EXPORT_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(export_schema)
    Draft202012Validator(schema).validate(checked)
    if checked != build():
        raise ValueError("full-BV multiplicity preflight does not reproduce")
    for path, expected in checked["provenance"]["source_sha256"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"full-BV multiplicity source drifted: {path}")

    if [transverse_traceless_rank_4d(spin) for spin in (2, 0, 2, 1)] != [
        5,
        1,
        5,
        3,
    ]:
        raise ValueError("independent TT-rank replay failed")
    rows = checked["standard_factor_multiplicities"]["rows"]
    if sum(row["determinant_sign"] * row["bundle_rank"] for row in rows) != 6:
        raise ValueError("independent signed-rank replay failed")
    receiver = checked["receiver_mechanics"]["receipt"]
    if (
        receiver["target_bundle_ranks"] != [5, 1, 5, 3]
        or receiver["target_signed_rank"] != 6
        or receiver["scalar_ghost_input_rank"] != 2
        or receiver["scalar_ghost_output_rank"] != 1
        or receiver["status"] != "SEMANTIC_RECEIVER_ACCEPTED"
    ):
        raise ValueError("multiplicity semantic receiver mechanics drifted")
    ranks = checked["exact_rank_decomposition"]
    if (
        ranks["scalar_ghost_candidate_rank"]
        - ranks["standard_scalar_ghost_factor_rank"]
        != ranks["unresolved_scalar_cancellation_rank"]
        != 1
    ):
        raise ValueError("independent scalar-gap replay failed")

    for flag in (
        "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
        "REPOSITORY_ELLIPTIC_COMPLEX_CERTIFIED",
        "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED",
        "QME_DISPOSITION",
    ):
        mutant = deepcopy(checked)
        mutant["claim_flags"][flag] = True
        try:
            validate_claim_boundary(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"multiplicity overclaim survived: {flag}")
    return checked


if __name__ == "__main__":
    verify()
    print("repository full-BV multiplicity preflight independent verifier: PASS")
