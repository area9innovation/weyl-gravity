#!/usr/bin/env python3
"""Independently verify the two-channel memory-transport q3 payload."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_memory_transport_q3_pbw import (
    CERTIFICATE, DEPENDENCIES, PAYLOAD, PAYLOAD_SCHEMA, ROOT, SCHEMA,
    action_audit, canonical_sha256, direct_action_blocks, merge_blocks,
    payload_document, serialize_tensor,
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
    for name, dependency in value["dependency_refs"].items():
        assert dependency["path"] == str(DEPENDENCIES[name].relative_to(ROOT))
        assert dependency["sha256"] == sha256(DEPENDENCIES[name])
    for source in value["provenance"]["source_manifest"]:
        assert source["sha256"] == sha256(ROOT / source["path"])
    rebuilt = serialize_tensor(merge_blocks(direct_action_blocks()))
    assert payload == payload_document()
    assert payload["rows"] == rebuilt
    assert payload["canonical_sha256"] == canonical_sha256(rebuilt)
    assert value["payload_ref"]["sha256"] == sha256(PAYLOAD)
    assert value["velocity_and_cyclicity_audit"] == action_audit()
    assert value["flags"]["COMPLETE_SCALAR_108_ROW_Q3_EXPORTED"] is False
    print("BERGER_108_ROW_MEMORY_TRANSPORT_Q3_PBW independent verification: PASS")
    return 0


if __name__ == "__main__": raise SystemExit(main())
