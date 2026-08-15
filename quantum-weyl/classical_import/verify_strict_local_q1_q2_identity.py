#!/usr/bin/env python3
"""Schema and report-boundary verifier for the local q1/q2 identity."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from check_strict_local_q1_q2_identity import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
SCHEMA = HERE / "schema/strict-local-q1-q2-identity-v1.schema.json"
REPORT = HERE / "REPORT_STRICT_LOCAL_Q1_Q2_IDENTITY_V1.md"


def verify(value: dict[str, Any], report: str) -> list[str]:
    errors = check(value, replay_exact=False)
    try:
        jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    except jsonschema.ValidationError as exc:
        errors.append(f"schema rejection: {exc.message}")
    for phrase in (
        "18 channels",
        "51 composable paths",
        "three examples are not treated as a",
        "Gate A remains fail closed",
        "## Does not establish",
        "Lorentzian quantum theory",
    ):
        if phrase not in report:
            errors.append(f"report missing boundary phrase: {phrase}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = verify(value, REPORT.read_text())
    print("STRICT_LOCAL_Q1_Q2_IDENTITY_V1_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
