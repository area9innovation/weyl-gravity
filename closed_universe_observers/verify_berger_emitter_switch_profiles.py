#!/usr/bin/env python3
"""Independent verifier for exact normalized emitter clock switches."""

from __future__ import annotations

import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_emitter_switch_profiles import (
    CERTIFICATE,
    DEPENDENCIES,
    INPUT,
    SCHEMA,
    _sha256,
    bump_audit,
    switch_audit,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    data = json.loads(INPUT.read_text())
    if value["authoritative_input"]["sha256"] != _sha256(INPUT):
        raise AssertionError("switch input hash drifted")
    for name, path in DEPENDENCIES.items():
        dependency = json.loads(path.read_text())
        reference = value["dependency_refs"][name]
        if reference["sha256"] != _sha256(path) or reference["result_id"] != dependency["result_id"]:
            raise AssertionError(f"dependency drifted: {name}")
    if not switch_audit(data)["strict_causal_order"] or not bump_audit()["unit_clock_integral"]:
        raise AssertionError("base switch audit failed")
    if switch_audit(data, mutation="move_h1_before_D0")["strict_causal_order"]:
        raise AssertionError("causal-order mutation not detected")
    if bump_audit(omit_radius_normalization=True)["unit_clock_integral"]:
        raise AssertionError("normalization mutation not detected")
    if bump_audit(use_nonflat_polynomial=True)["C_infinity_compact_support"]:
        raise AssertionError("smoothness mutation not detected")
    print("BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
