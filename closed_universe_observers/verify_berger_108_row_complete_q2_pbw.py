#!/usr/bin/env python3
"""Independently verify the complete Berger 108-row q2 assembly."""

import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_complete_q2_pbw import (
    CERTIFICATE, GATES, PAYLOAD, PAYLOAD_SCHEMA, ROOT, SCHEMA, SOURCES,
    assemble, canonical_sha256,
)


def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value, payload = json.loads(CERTIFICATE.read_text()), json.loads(PAYLOAD.read_text())
    for path, document in ((SCHEMA, value), (PAYLOAD_SCHEMA, payload)):
        schema = json.loads(path.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(document)
    for name, ref in payload["source_payload_refs"].items():
        assert ref["path"] == str(SOURCES[name].relative_to(ROOT)) and ref["sha256"] == sha256(SOURCES[name])
    for name, ref in value["gate_refs"].items():
        assert ref["path"] == str(GATES[name].relative_to(ROOT)) and ref["sha256"] == sha256(GATES[name])
    rows, counts, audit = assemble()
    assert payload["rows"] == rows and payload["source_term_counts"] == counts and payload["assembly_audit"] == audit
    assert payload["canonical_sha256"] == canonical_sha256(rows) and value["payload_ref"]["sha256"] == sha256(PAYLOAD)
    assert audit["cross_source_operator_key_collision_count"] == 0
    print("BERGER_108_ROW_COMPLETE_Q2_PBW independent verification: PASS"); return 0


if __name__ == "__main__": raise SystemExit(main())
