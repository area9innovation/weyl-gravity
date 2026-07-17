from __future__ import annotations

import json

import jsonschema

from d_quotient_classical.backreacted_clock import paper_09_claim_table as theorem
from d_quotient_classical.backreacted_clock.verify_paper_09_claim_table import main as independent_verify


def test_paper_09_claim_table_is_complete_and_fail_closed() -> None:
    payload = theorem.build()
    theorem.verify(payload)
    assert payload["claim_ids_complete"] == [f"P09-C{index}" for index in range(1, 11)]
    assert payload["theorem_frozen"] is False
    assert payload["required_signoffs"]["nonlinear_team"].startswith("PENDING")
    assert payload["independent_cross_checks"][0]["supports_claim"] == "P09-C8"
    assert payload["independent_cross_checks"][1]["certificate_result_id"] == "BERGER_GENERATOR_CONJUGATION_AUDIT"


def test_paper_09_claim_table_schema_and_persisted_output() -> None:
    payload = theorem.build()
    schema = json.loads(theorem.SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert json.loads(theorem.OUTPUT.read_text()) == payload


def test_paper_09_independent_consumer() -> None:
    assert independent_verify() == 0
