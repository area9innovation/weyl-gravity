#!/usr/bin/env python3
"""Independently verify the radial nonlinear clock canonical map."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_nonlinear_clock_radial_canonical_map_f2_f3 import (
    CERTIFICATE, DEPENDENCIES, ROOT, SCHEMA, canonical_sha256, exact_chart_audit,
    taylor_entries,
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
    entries = taylor_entries()
    assert value["taylor_payload"]["F2"] == entries["F2"]
    assert value["taylor_payload"]["F3"] == entries["F3"]
    assert value["taylor_payload"]["canonical_sha256"] == canonical_sha256(entries)
    audit = exact_chart_audit()
    assert audit == value["radial_chart"]
    assert audit["metric_map_defect_count"] == 0
    assert audit["cotangent_lift"]["dR_coefficient_defect_count"] == 0
    assert exact_chart_audit(delete_cubic_trace=True)["metric_map_defect_count"] > 0
    assert exact_chart_audit(omit_radial_cotangent=True)["cotangent_lift"]["dR_coefficient_defect_count"] > 0
    print("BERGER_NONLINEAR_CLOCK_RADIAL_CANONICAL_MAP_F2_F3 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
