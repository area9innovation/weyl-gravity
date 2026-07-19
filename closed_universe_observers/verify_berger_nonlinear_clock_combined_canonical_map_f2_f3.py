#!/usr/bin/env python3
"""Independently verify the combined Berger clock canonical map."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_nonlinear_clock_combined_canonical_map_f2_f3 import (
    CERTIFICATE, DEPENDENCIES, ROOT, SCHEMA, build,
)


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
    rebuilt = build()
    assert rebuilt == value
    assert value["geometric_definition"]["restriction_audit"]["radial_restriction_defect_count"] == 0
    assert value["geometric_definition"]["restriction_audit"]["temporal_restriction_defect_count"] == 0
    assert value["field_payload"]["reconstruction_defect_counts"] == {"F2": 0, "F3": 0}
    assert value["canonical_audit"]["canonical_inverse_defects"]["degree_2"]["operator_key_count"] == 0
    assert value["canonical_audit"]["canonical_inverse_defects"]["degree_3"]["operator_key_count"] == 0
    assert value["cotangent_payload"]["reconstruction_defects"]["F2"]["operator_key_count"] == 0
    assert value["cotangent_payload"]["reconstruction_defects"]["F3"]["operator_key_count"] == 0
    print("BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
