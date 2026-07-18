#!/usr/bin/env python3
"""Independent verifier for the emitter stress/clock backreaction ledger."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_emitter_stress_clock_backreaction import (
    CERTIFICATE,
    DEPENDENCIES,
    SCHEMA,
    _sha256,
    cyclic_orbit_audit,
    reduced_noether_audit,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, path in DEPENDENCIES.items():
        reference = value["dependency_refs"][name]
        if reference["sha256"] != _sha256(path):
            raise AssertionError(f"dependency hash drifted: {name}")
        if reference["result_id"] != json.loads(path.read_text())["result_id"]:
            raise AssertionError(f"dependency result drifted: {name}")
    if reduced_noether_audit()["ward_defect_count"] != 0:
        raise AssertionError("reduced Noether identity failed")
    if cyclic_orbit_audit()["cyclicity_defect_count"] != 0:
        raise AssertionError("common-action cyclic orbit failed")
    if reduced_noether_audit(omit_clock_source=True)["ward_defect_count"] == 0:
        raise AssertionError("clock-source mutation was not detected")
    if cyclic_orbit_audit(omit_metric_output=True)["cyclicity_defect_count"] == 0:
        raise AssertionError("metric-output mutation was not detected")
    if cyclic_orbit_audit(omit_clock_output=True)["cyclicity_defect_count"] == 0:
        raise AssertionError("clock-output mutation was not detected")
    source_paths = {item["path"] for item in value["provenance"]["source_manifest"]}
    for required in (
        "closed_universe_observers/generate_berger_emitter_stress_clock_backreaction.py",
        "closed_universe_observers/verify_berger_emitter_stress_clock_backreaction.py",
        "closed_universe_observers/tests/test_berger_emitter_stress_clock_backreaction.py",
        "closed_universe_observers/schema/berger-emitter-stress-clock-backreaction-ledger-v1.schema.json",
        "closed_universe_observers/reports/berger-emitter-stress-clock-backreaction-ledger.md",
    ):
        if required not in source_paths:
            raise AssertionError(f"source manifest missing {required}")
    print("BERGER_EMITTER_STRESS_CLOCK_BACKREACTION_LEDGER verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
