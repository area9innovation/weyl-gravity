#!/usr/bin/env python3
"""Validate a generated residual-atlas fragment and its evidence links."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_id(payload: dict) -> str:
    value = payload.get("result_id") or payload.get("certificate_id") or payload.get("schema")
    return str(value) if value is not None else "UNIDENTIFIED"


def validate(fragment: Path) -> None:
    value = json.loads(fragment.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    identifiers: set[str] = set()
    for entry in value["entries"]:
        if entry["id"] in identifiers:
            raise AssertionError(f"duplicate atlas identifier: {entry['id']}")
        identifiers.add(entry["id"])
        for evidence in entry["evidence"]:
            path = ROOT / evidence["path"]
            payload = json.loads(path.read_text(encoding="utf-8"))
            if _sha256(path) != evidence["sha256"]:
                raise AssertionError(f"evidence hash mismatch: {entry['id']} -> {path}")
            if _artifact_id(payload) != evidence["result_id"]:
                raise AssertionError(f"evidence result-id mismatch: {entry['id']} -> {path}")
        if not entry["evidence"] and "crosswalk" not in entry["id"]:
            statuses = set(entry["descriptions"].values())
            if statuses - {"OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"}:
                raise AssertionError(f"unsupported positive atlas claim: {entry['id']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fragment", type=Path)
    args = parser.parse_args()
    validate(args.fragment)
    print(f"RESIDUAL_ATLAS_FRAGMENT_V1: PASS {args.fragment}")


if __name__ == "__main__":
    main()
