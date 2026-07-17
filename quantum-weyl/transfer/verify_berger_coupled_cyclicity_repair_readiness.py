#!/usr/bin/env python3
"""Independent fail-closed verifier for coupled q2 repair readiness."""

from __future__ import annotations

from copy import deepcopy
import json

from jsonschema import Draft202012Validator
from local_bv.schema_validation import validate_instance

from .berger_coupled_cyclicity_repair_acceptance import INPUT_SCHEMA, _classify, evaluate
from .berger_coupled_cyclicity_repair_readiness import ACCEPTED_FIXTURE, FIXTURE, HERE, build
from .berger_coupled_cyclicity_repair_readiness_certificate import OUTPUT


SCHEMA = HERE / "schema/berger-coupled-cyclicity-repair-readiness-v1.schema.json"


def _validate_claim_state(value: dict) -> None:
    flags = value["claim_flags"]
    if (
        value["result_state"]
        != "CORRECTED_CLASSICAL_REPAIR_ACCEPTED_MIXED_Q3_INPUT_UNBLOCKED"
        or not flags["CORRECTED_CLASSICAL_INPUT_AVAILABLE"]
        or not flags["COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED"]
        or not flags["MIXED_Q3_UNBLOCKED"]
        or flags["QUANTUM_CLAIM"]
    ):
        raise ValueError("repair acceptance claim state drifted")


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    fixture = json.loads(FIXTURE.read_text())
    accepted_fixture = json.loads(ACCEPTED_FIXTURE.read_text())
    readiness_schema = json.loads(SCHEMA.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(readiness_schema)
    Draft202012Validator.check_schema(input_schema)
    errors = (
        validate_instance(certificate, readiness_schema)
        + validate_instance(fixture, input_schema)
        + validate_instance(accepted_fixture, input_schema)
    )
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    expected_certificate, expected_fixture, expected_accepted_fixture = build()
    if (
        certificate != expected_certificate
        or fixture != expected_fixture
        or accepted_fixture != expected_accepted_fixture
    ):
        raise ValueError("repair readiness does not reproduce")
    if evaluate(fixture)["verdict"] != "REJECTED_EXACT_ALGEBRAIC_DEFECT":
        raise ValueError("obstructed fixture escaped exact evaluator")
    accepted_result = evaluate(accepted_fixture)
    if accepted_result["verdict"] != "ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR":
        raise ValueError("landed corrected fixture failed exact evaluator")
    if accepted_result["diagnostics"] != certificate["accepted_candidate"]["diagnostics"]:
        raise ValueError("accepted diagnostics do not match exact evaluator")
    _validate_claim_state(certificate)
    for key in (
        "CORRECTED_CLASSICAL_INPUT_AVAILABLE",
        "COUPLED_Q2_CYCLIC_REPAIR_ACCEPTED",
        "MIXED_Q3_UNBLOCKED",
    ):
        mutant = deepcopy(certificate)
        mutant["claim_flags"][key] = False
        try:
            _validate_claim_state(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"accepted-state mutation escaped: {key}")
    quantum_mutant = deepcopy(certificate)
    quantum_mutant["claim_flags"]["QUANTUM_CLAIM"] = True
    try:
        _validate_claim_state(quantum_mutant)
    except ValueError:
        pass
    else:
        raise ValueError("quantum overclaim mutation accepted")
    causal_mutant = deepcopy(accepted_result["diagnostics"])
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
