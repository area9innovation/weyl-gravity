#!/usr/bin/env python3
"""Validate quantum result records without an external JSON-Schema package."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SCHEMA_PATH = Path(__file__).with_name("result.schema.json")


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    raise ValueError(f"unsupported schema type: {expected}")


def validate_record(record: object, schema: dict[str, Any]) -> list[str]:
    """Return deterministic validation errors for one result record."""

    if not isinstance(record, dict):
        return ["$: expected object"]

    errors: list[str] = []
    required = schema["required"]
    properties = schema["properties"]
    for name in required:
        if name not in record:
            errors.append(f"$.{name}: missing required property")

    if schema.get("additionalProperties") is False:
        for name in sorted(set(record) - set(properties)):
            errors.append(f"$.{name}: additional property is forbidden")

    for name in sorted(set(record) & set(properties)):
        value = record[name]
        rule = properties[name]
        expected_type = rule.get("type")
        if expected_type is not None and not _matches_type(value, expected_type):
            errors.append(f"$.{name}: expected {expected_type}")
            continue
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"$.{name}: value is not in the declared enum")
        if isinstance(value, str):
            if len(value) < rule.get("minLength", 0):
                errors.append(f"$.{name}: string is too short")
            if "pattern" in rule and re.fullmatch(rule["pattern"], value) is None:
                errors.append(f"$.{name}: string does not match the declared pattern")
        if isinstance(value, int) and not isinstance(value, bool):
            if "minimum" in rule and value < rule["minimum"]:
                errors.append(f"$.{name}: value is below minimum")
            if "maximum" in rule and value > rule["maximum"]:
                errors.append(f"$.{name}: value is above maximum")
        if isinstance(value, list):
            if len(value) < rule.get("minItems", 0):
                errors.append(f"$.{name}: array has too few items")
            if rule.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
                errors.append(f"$.{name}: array items are not unique")
            item_rule = rule.get("items", {})
            for index, item in enumerate(value):
                if "type" in item_rule and not _matches_type(item, item_rule["type"]):
                    errors.append(f"$.{name}[{index}]: expected {item_rule['type']}")
                if "enum" in item_rule and item not in item_rule["enum"]:
                    errors.append(f"$.{name}[{index}]: value is not in the declared enum")

    lifecycle = record.get("lifecycle_status")
    tags = record.get("dependency_tags", [])
    if lifecycle == "COEFFICIENT_COMPUTED" and record.get("coefficient_status") != "COMPUTED":
        errors.append("$.coefficient_status: lifecycle requires COMPUTED")
    if lifecycle == "QME_RESTORED" and record.get("coefficient_status") != "COMPUTED":
        errors.append("$.coefficient_status: restored QME requires computed coefficients")
    if lifecycle == "RESIDUAL_TRANSFERRED" and record.get("residual_projection_status") != "COMPUTED":
        errors.append("$.residual_projection_status: residual transfer requires COMPUTED")
    if lifecycle == "LORENTZIAN_CERTIFIED" and "LORENTZIAN-CAUSAL" not in tags:
        errors.append("$.dependency_tags: Lorentzian certification requires LORENTZIAN-CAUSAL")

    return sorted(errors)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args()
    schema = json.loads(SCHEMA_PATH.read_text())
    failed = False
    for path in args.records:
        errors = validate_record(json.loads(path.read_text()), schema)
        if errors:
            failed = True
            for error in errors:
                print(f"{path}: {error}")
        else:
            print(f"{path}: PASS")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
