#!/usr/bin/env python3
"""Independent verifier for stationary-generator import readiness."""

from __future__ import annotations

from copy import deepcopy
import json

from jsonschema import Draft202012Validator

from local_bv.schema_validation import validate_instance

from .berger_retained_stationary_generator_acceptance import INPUT_SCHEMA, MATRIX_SCHEMA
from .berger_retained_stationary_generator_readiness import READINESS_SCHEMA, build
from .berger_retained_stationary_generator_readiness_certificate import OUTPUT


def _rejects_overclaim(value: dict) -> None:
    flags = value["claim_flags"]
    if (
        value["result_state"] != "CONSUMER_READY_STATIONARY_CARRIER_INPUT_NOT_SUPPLIED"
        or flags["STATIONARY_GENERATOR_INPUT_AVAILABLE"]
        or flags["STATIONARY_GENERATOR_ACCEPTED"]
        or flags["ZERO_FREQUENCY_LEDGER_COMPUTED"]
        or flags["GLOBAL_BRST_HADAMARD_STATE"]
        or flags["QUANTUM_CLAIM"]
        or value["analytic_separation"]["finite_PBW_import_can_decide_zero_is_isolated"]
    ):
        raise ValueError("stationary-generator readiness was over-promoted")


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schemas = [
        json.loads(path.read_text())
        for path in (INPUT_SCHEMA, MATRIX_SCHEMA, READINESS_SCHEMA)
    ]
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
    errors = validate_instance(certificate, schemas[-1])
    if errors:
        raise ValueError("strict stationary readiness schema failure: " + "; ".join(errors))
    if certificate != build():
        raise ValueError("stationary-generator readiness does not reproduce")
    _rejects_overclaim(certificate)
    for key in (
        "STATIONARY_GENERATOR_INPUT_AVAILABLE",
        "STATIONARY_GENERATOR_ACCEPTED",
        "ZERO_FREQUENCY_LEDGER_COMPUTED",
        "GLOBAL_BRST_HADAMARD_STATE",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = True
        try:
            _rejects_overclaim(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"stationary readiness overclaim mutation accepted: {key}")
    analytic_mutant = deepcopy(certificate)
    analytic_mutant["analytic_separation"][
        "finite_PBW_import_can_decide_zero_is_isolated"
    ] = True
    try:
        _rejects_overclaim(analytic_mutant)
    except ValueError:
        pass
    else:
        raise ValueError("finite PBW carrier was allowed to claim spectral isolation")
    return certificate


def main() -> int:
    verify()
    print("BERGER stationary-generator import readiness independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
