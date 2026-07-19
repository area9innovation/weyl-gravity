#!/usr/bin/env python3
"""Independently verify the six-rod metric q3 PBW row chunks."""

import gzip
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_rod_metric_q3_pbw import (
    CERTIFICATE,
    DEPENDENCIES,
    GENERATED,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
    action_audit,
    canonical_sha256,
    payload_bundle,
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
    rebuilt, encoded = payload_bundle()
    assert payload == rebuilt
    for chunk in payload["chunks"]:
        output = chunk["output"]
        path = GENERATED / f"row_{output:03d}.json.gz"
        assert path.read_bytes() == encoded[output]
        assert sha256(path) == chunk["file_sha256"]
        row = json.loads(gzip.decompress(path.read_bytes()))
        body = {"output": row["output"], "terms": row["terms"]}
        assert canonical_sha256(body) == row["canonical_sha256"] == chunk["canonical_sha256"]
    assert value["payload_ref"]["sha256"] == sha256(PAYLOAD)
    assert value["action_and_cyclicity_audit"] == action_audit()
    assert value["flags"]["COMPLETE_SCALAR_108_ROW_Q3_EXPORTED"] is False
    print("BERGER_108_ROW_ROD_METRIC_Q3_PBW independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
