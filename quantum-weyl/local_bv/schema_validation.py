"""Deterministic validation for the JSON-Schema subset used by local receipts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _is_type(value: object, expected: str | list[str]) -> bool:
    if isinstance(expected, list):
        return any(_is_type(value, candidate) for candidate in expected)
    return {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }[expected](value)


def validate_instance(
    instance: object, schema: dict[str, Any], path: str = "$"
) -> list[str]:
    """Return sorted validation errors without requiring a third-party package."""

    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None and not _is_type(instance, expected_type):
        return [f"{path}: expected {expected_type}"]
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: value differs from const")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value is outside enum")

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in instance:
                errors.append(f"{path}.{name}: missing required property")
        additional = schema.get("additionalProperties", True)
        for name in sorted(instance):
            child_path = f"{path}.{name}"
            if name in properties:
                errors.extend(
                    validate_instance(instance[name], properties[name], child_path)
                )
            elif additional is False:
                errors.append(f"{child_path}: additional property is forbidden")
            elif isinstance(additional, dict):
                errors.extend(validate_instance(instance[name], additional, child_path))

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: array has too few items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: array has too many items")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True) for item in instance]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: array items are not unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(
                    validate_instance(item, item_schema, f"{path}[{index}]")
                )

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: string is too short")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None:
            errors.append(f"{path}: string does not match pattern")

    if isinstance(instance, int) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: integer is below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: integer is above maximum")

    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", type=Path)
    parser.add_argument("instance", type=Path)
    args = parser.parse_args()
    errors = validate_instance(
        json.loads(args.instance.read_text(encoding="utf-8")),
        json.loads(args.schema.read_text(encoding="utf-8")),
    )
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"{args.instance}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
