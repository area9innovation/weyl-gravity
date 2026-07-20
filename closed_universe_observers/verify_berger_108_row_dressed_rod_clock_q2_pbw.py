#!/usr/bin/env python3
"""Independently verify the dressed six-rod clock q2 correction."""

import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_dressed_rod_clock_q2_pbw import (
    CERTIFICATE,
    DEPENDENCIES,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
    build,
    payload_document,
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for path, document in ((SCHEMA, value), (PAYLOAD_SCHEMA, payload)):
        schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    assert payload == payload_document()
    assert value["clock_dressing_audit"]["unary_conjugation_defect_summary"]["operator_key_count"] == 0
    assert value["payload_ref"]["sha256"] == sha256(PAYLOAD)
    for name, ref in value["dependency_refs"].items():
        assert ref["path"] == str(DEPENDENCIES[name].relative_to(ROOT))
        assert ref["sha256"] == sha256(DEPENDENCIES[name])
    rebuilt = build(payload=payload, payload_hash=sha256(PAYLOAD))
    assert rebuilt["payload_ref"] == value["payload_ref"]
    print("BERGER_108_ROW_DRESSED_ROD_CLOCK_Q2_PBW independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
