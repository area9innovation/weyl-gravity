#!/usr/bin/env python3
"""Independently verify the Berger q3 structural-zero ledger."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_q3_structural_zero_ledger import CERTIFICATE, DEPENDENCIES, ROOT, SCHEMA, audits, build, canonical_sha256


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, dependency in value["dependency_refs"].items():
        assert dependency["path"] == str(DEPENDENCIES[name].relative_to(ROOT))
        assert dependency["sha256"] == sha256(DEPENDENCIES[name])
    for source in value["provenance"]["source_manifest"]:
        assert source["sha256"] == sha256(ROOT / source["path"])
    assert value == build()
    assert value["source_audits"] == audits()
    assert all(not audit["structural_zero_certified"] for audit in audits(mutate=True))
    payload = {"shape": [108, 108, 108, 108], "rows": [], "operator_key_count": 0, "serialized_term_count": 0}
    assert value["empty_q3_payload"]["canonical_sha256"] == canonical_sha256(payload)
    print("BERGER_108_ROW_Q3_STRUCTURAL_ZERO_LEDGER independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
