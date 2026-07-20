#!/usr/bin/env python3
"""Independently verify the complete source-labelled Berger q3 payload."""

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_complete_q3_pbw import CERTIFICATE, GATES, PAYLOAD, PAYLOAD_SCHEMA, ROOT, SCHEMA, SOURCES, canonical_sha256, payload_bundle


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="rebuild all source rows before comparison")
    args = parser.parse_args()
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for schema_path, document in ((SCHEMA, value), (PAYLOAD_SCHEMA, payload)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    for name, reference in value["gate_refs"].items():
        assert reference["path"] == str(GATES[name].relative_to(ROOT))
        assert reference["sha256"] == sha256(GATES[name])
    for name, reference in payload["source_payload_refs"].items():
        assert reference["path"] == str(SOURCES[name].relative_to(ROOT))
        assert reference["sha256"] == sha256(SOURCES[name])
    for source in value["provenance"]["source_manifest"]:
        assert source["sha256"] == sha256(ROOT / source["path"])
    assert value["payload_ref"]["sha256"] == sha256(PAYLOAD)
    row_hashes = {}
    operator_total = 0
    serialized_total = 0
    for chunk in payload["chunks"]:
        output = chunk["output"]
        path = ROOT / chunk["path"]
        assert chunk["file_sha256"] == sha256(path)
        row_hashes[output] = chunk["canonical_sha256"]
        operator_total += chunk["operator_key_count"]
        serialized_total += chunk["serialized_term_count"]
    assert payload["canonical_sha256"] == canonical_sha256(row_hashes)
    assert operator_total == payload["operator_key_count"]
    assert serialized_total == payload["serialized_term_count"]
    if args.full:
        rebuilt, encoded = payload_bundle()
        assert payload == rebuilt
        for chunk in payload["chunks"]:
            assert (ROOT / chunk["path"]).read_bytes() == encoded[chunk["output"]]
    assert value["flags"]["COMPLETE_SCALAR_108_ROW_Q3_EXPORTED"] is True
    assert value["flags"]["Q3_ADDITIVE_OVERLAPS_EXPLICIT"] is True
    assert value["flags"]["Q3_CROSS_SOURCE_OPERATOR_KEYS_DISJOINT"] is False
    assert value["flags"]["COMPONENT_ARITY_IDENTITIES_CERTIFIED"] is False
    assert value["flags"]["TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED"] is False
    mode = "full" if args.full else "fast"
    print(f"BERGER_108_ROW_COMPLETE_Q3_PBW independent verification ({mode}): PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
