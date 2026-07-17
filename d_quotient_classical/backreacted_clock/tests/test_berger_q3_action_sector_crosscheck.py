from __future__ import annotations

import json

import jsonschema

from d_quotient_classical.backreacted_clock import berger_q3_action_sector_crosscheck as theorem
from d_quotient_classical.backreacted_clock.verify_berger_q3_action_sector_crosscheck import (
    main as independent_verify,
)


def test_direct_action_sector_matches_frozen_q3() -> None:
    payload = theorem.build()
    theorem.verify(payload)
    assert len(payload["coefficients"]) == 8
    assert sum(entry["ordered_permutations_checked"] for entry in payload["coefficients"]) == 16
    assert payload["flags"]["BERGER_Q3_ACTION_SECTOR_CROSSCHECK"] is True
    assert payload["flags"]["FULL_INDEPENDENT_Q3_REDERIVATION"] is False


def test_crosscheck_schema_and_persisted_certificate() -> None:
    payload = theorem.build()
    schema = json.loads(theorem.SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert json.loads(theorem.CERTIFICATE.read_text()) == payload


def test_crosscheck_independent_consumer() -> None:
    assert independent_verify() == 0
