#!/usr/bin/env python3
"""Independently verify the complete Berger arity-two obstruction."""

import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import (
    CERTIFICATE, DEPENDENCIES, ROOT, SCHEMA, build, replay_audit,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value == build()
    assert value["arity_two_replay"] == replay_audit()
    for name, reference in value["dependency_refs"].items():
        path = DEPENDENCIES[name]
        assert reference["path"] == str(path.relative_to(ROOT))
        assert reference["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    print("BERGER_108_ROW_ARITY_TWO_OBSTRUCTION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
