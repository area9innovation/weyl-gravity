#!/usr/bin/env python3
"""Independently verify the physical massive-emitter q3 payload."""

import gzip
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_emitter_physical_q3_pbw import (
    CERTIFICATE,
    DEPENDENCIES,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
    action_audit,
    canonical_sha256,
    payload_bundle,
    serialize_tensor,
    merged_tensor,
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
    rebuilt_payload, encoded = payload_bundle()
    assert payload == rebuilt_payload
    assert value["payload_ref"]["sha256"] == sha256(PAYLOAD)
    assert value["second_jet_and_cyclicity_audit"] == action_audit()
    tensor = merged_tensor()
    row_hashes = {}
    for chunk in payload["chunks"]:
        path = ROOT / chunk["path"]
        output = chunk["output"]
        assert path.read_bytes() == encoded[output]
        assert chunk["file_sha256"] == sha256(path)
        document = json.loads(gzip.decompress(path.read_bytes()))
        row = {"output": document["output"], "terms": document["terms"]}
        assert document["canonical_sha256"] == canonical_sha256(row)
        expected = serialize_tensor({key: polynomial for key, polynomial in tensor.items() if key[0] == output})[0]
        assert row == expected
        row_hashes[output] = document["canonical_sha256"]
    assert payload["canonical_sha256"] == canonical_sha256(row_hashes)
    assert value["flags"]["COMPLETE_SCALAR_108_ROW_Q3_EXPORTED"] is False
    assert value["flags"]["TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED"] is False
    print("BERGER_108_ROW_EMITTER_PHYSICAL_Q3_PBW independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
