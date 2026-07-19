#!/usr/bin/env python3
"""Independently replay the Berger nonlinear clock second-jet unary gate."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers import berger_108_row_nonlinear_clock_second_jet as second_jet
from closed_universe_observers.generate_berger_108_row_nonlinear_clock_second_jet import (
    CERTIFICATE,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
    payload_document,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for schema_path, document in ((SCHEMA, value), (PAYLOAD_SCHEMA, payload)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    for dependency in value["dependency_refs"].values():
        assert sha256(ROOT / dependency["path"]) == dependency["sha256"]
    assert sha256(PAYLOAD) == value["payload_ref"]["sha256"]

    q1 = replay.load_q1()
    correction, parts = second_jet.candidate_completion(q1[(0, 0)], q1[(1, 0)])
    assert payload == payload_document(parts)
    assert all(replay.cyclicity_defect(operator) == {} for operator in parts.values())
    q1[(1, 0)] = replay.add_operators(q1[(1, 0)], correction)
    assert all(replay.cyclicity_defect(operator) == {} for operator in q1.values())
    squared = replay.q1_squared_coefficients(q1)
    assert squared[(0, 0)] == {}
    assert squared[(0, 1)] == {}
    assert squared[(1, 1)] == {}
    defects, summary = replay.quotient_defect(squared[(1, 0)])
    assert defects == {}
    assert summary == value["nilpotency_replay"]["epsilon_R_squared_background_quotient_summary"]
    print("BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
