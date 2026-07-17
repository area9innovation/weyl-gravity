#!/usr/bin/env python3
"""Independent fail-closed verifier for coupled q2 repair readiness."""

from __future__ import annotations

from copy import deepcopy
import json

from jsonschema import Draft202012Validator
from local_bv.schema_validation import validate_instance

from .berger_coupled_cyclicity_repair_acceptance import INPUT_SCHEMA, _classify, evaluate
from .berger_coupled_cyclicity_repair_readiness import FIXTURE, HERE, build
from .berger_coupled_cyclicity_repair_readiness_certificate import OUTPUT


SCHEMA = HERE / "schema/berger-coupled-cyclicity-repair-readiness-v1.schema.json"


def _rejects_overclaim(value: dict) -> None:
    flags = value["claim_flags"]
    if (
        value["result_state"]
        != "INPUT_BLOCKED_CORRECTED_CLASSICAL_COMMIT_NOT_SUPPLIED"
        or flags["CORRECTED_CLASSICAL_INPUT_AVAILABLE"]
        or flags["COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED"]
        or flags["MIXED_Q3_UNBLOCKED"]
        or flags["QUANTUM_CLAIM"]
    ):
        raise ValueError("repair readiness was over-promoted")


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    fixture = json.loads(FIXTURE.read_text())
    readiness_schema = json.loads(SCHEMA.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(readiness_schema)
    Draft202012Validator.check_schema(input_schema)
    errors = validate_instance(certificate, readiness_schema) + validate_instance(
        fixture, input_schema
    )
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    expected_certificate, expected_fixture = build()
    if certificate != expected_certificate or fixture != expected_fixture:
        raise ValueError("repair readiness does not reproduce")
    if evaluate(fixture)["verdict"] != "REJECTED_EXACT_ALGEBRAIC_DEFECT":
        raise ValueError("obstructed fixture escaped exact evaluator")
    _rejects_overclaim(certificate)
    for key in (
        "CORRECTED_CLASSICAL_INPUT_AVAILABLE",
        "COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED",
        "MIXED_Q3_UNBLOCKED",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = True
        try:
            _rejects_overclaim(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation accepted: {key}")
    accepted = deepcopy(certificate["obstructed_baseline"]["diagnostics"])
    for key in tuple(accepted):
        if key.endswith("_defect_count") or key.startswith("transfer_") and key.endswith("_coefficient_count"):
            accepted[key] = 0
    accepted["causal_unary_flags_preserved"] = True
    accepted["producer_cyclicity_claim_consistent"] = True
    if _classify(accepted) != "ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR":
        raise ValueError("all-zero exact acceptance predicate did not accept")
    causal_mutant = deepcopy(accepted)
    causal_mutant["causal_unary_flags_preserved"] = False
    if _classify(causal_mutant) != "REJECTED_CAUSAL_UNARY_REGRESSION":
        raise ValueError("causal regression mutation accepted")
    return certificate


def main() -> int:
    verify()
    print("BERGER COUPLED Q2 repair-acceptance readiness independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
