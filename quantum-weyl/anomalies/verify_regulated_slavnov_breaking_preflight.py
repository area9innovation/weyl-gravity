"""Independent verifier for the regulated Slavnov-breaking assembly preflight."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from jsonschema import Draft202012Validator

from .regulated_slavnov_breaking_preflight import (
    OUTPUT,
    ROOT,
    SCHEMA,
    build,
    validate_claim_boundary,
)


def verify() -> dict:
    checked = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(checked)
    if checked != build():
        raise ValueError("regulated Slavnov-breaking preflight does not reproduce")
    for path, expected in checked["provenance"]["source_sha256"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Slavnov-breaking preflight source drifted: {path}")
    entries = checked["cohomology_reduction"]["matrix_entries"]
    if [(row["row"], row["column"]) for row in entries] != [(0, 0), (1, 1), (2, 2)]:
        raise ValueError("relative-cohomology reduction is not the certified quotient map")
    missing = checked["minimal_missing_carrier_theorem"]
    if (
        missing.get("scalar_ghost_gap_rank") != 0
        or missing.get("full_BV_ledger_composer_ready") is not True
        or missing.get("physical_TT_dictionary_accepted") is not True
        or missing.get("physical_full_BV_multiplicity_ledger_accepted") is not True
        or missing.get("repository_round_S4_Euler_coefficient_computed") is not True
        or missing.get("repository_C2_coefficient_gap") is not True
        or missing.get("classical_snapshot_compatibility_bridge_gap") is not False
        or missing.get("physical_classical_snapshot_compatibility_accepted")
        is not True
        or missing.get("regulated_BV_insertion_v2_receiver_ready") is not True
        or missing.get("status") != "EXACT_REGULATED_BV_INSERTION_GAP"
    ):
        raise ValueError("regulated BV insertion gap was not isolated")
    physical = checked["repository_physical_input"]
    if (
        physical.get("round_S4_Euler_coefficient", {}).get("a")
        != {"numerator": 87, "denominator": 20}
        or physical.get("round_S4_C2_status") != "NOT_DETERMINED_ON_ROUND_S4"
        or physical.get("repository_BV_anomaly_vector_status") != "NOT_COMPUTED"
    ):
        raise ValueError("physical round-S4 coefficient boundary drifted")
    for flag in (
        "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED",
        "REGULATED_SLAVNOV_BREAKING_COMPUTED",
        "QME_OBSTRUCTED",
        "QME_RESTORED",
        "D_CARTAN_CLASSIFIED",
        "LORENTZIAN_QUANTUM_THEORY",
    ):
        mutant = deepcopy(checked)
        mutant["claim_flags"][flag] = True
        try:
            validate_claim_boundary(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"Slavnov-breaking overclaim survived: {flag}")
    mutant = deepcopy(checked)
    mutant["conditional_obstruction_theorem"]["activated"] = True
    try:
        validate_claim_boundary(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("unmatched conditional obstruction was activated")
    return checked


if __name__ == "__main__":
    verify()
    print("regulated Slavnov-breaking assembly verifier: PASS")
