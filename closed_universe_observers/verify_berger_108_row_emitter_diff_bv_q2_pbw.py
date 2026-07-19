#!/usr/bin/env python3
"""Independently verify the emitter Diff--BV q2 PBW payload."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_emitter_diff_bv_q2_pbw import (
    CERTIFICATE,
    DEPENDENCIES,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
    canonical_sha256,
    cartan_audit,
    emitter_tensor,
    graded_symmetry_defects,
    scalar_template_audit,
    serialize_tensor,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for path, document in ((SCHEMA, value), (PAYLOAD_SCHEMA, payload)):
        schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    for name, dependency in value["dependency_refs"].items():
        assert dependency["path"] == str(DEPENDENCIES[name].relative_to(ROOT))
        assert dependency["sha256"] == sha256(DEPENDENCIES[name])
    tensor, _ = emitter_tensor()
    rebuilt = serialize_tensor(tensor)
    assert payload["rows"] == rebuilt
    assert payload["canonical_sha256"] == canonical_sha256(rebuilt)
    assert value["payload_ref"]["sha256"] == sha256(PAYLOAD)
    assert cartan_audit()["Cartan_formula_defect_count"] == 0
    assert scalar_template_audit()["scalar_BV_template_recovery_defect_count"] == 0
    assert graded_symmetry_defects(tensor) == 0
    print("BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
