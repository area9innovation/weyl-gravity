#!/usr/bin/env python3
"""Validate the frozen v6 channel handoff contract without inventing data."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "channel-handoff-v6.schema.json"
HANDOFF = HERE / "channel-handoff-v6.json"


def load_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate(document: dict) -> None:
    errors = sorted(load_validator().iter_errors(document), key=lambda e: list(e.path))
    if errors:
        path = ".".join(str(part) for part in errors[0].path) or "root"
        raise ValueError(f"{path}: {errors[0].message}")


def main() -> int:
    load_validator()
    if not HANDOFF.exists():
        print("PASS schema; HANDOFF_NOT_POPULATED")
        return 0
    try:
        validate(json.loads(HANDOFF.read_text()))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"REFUSED: {exc}")
        return 3
    print("PASS schema and populated handoff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
