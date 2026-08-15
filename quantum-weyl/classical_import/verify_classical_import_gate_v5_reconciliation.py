#!/usr/bin/env python3
"""Schema and deterministic report verifier for Gate-A reconciliation v5."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from build_classical_import_gate_v5_reconciliation import generated
from check_classical_import_gate_v5_reconciliation import check


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V5.md"
SCHEMA = HERE / "schema/classical-import-gate-v5-reconciliation-v1.schema.json"


def verify(value: dict | None = None, report: str | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    report = REPORT.read_text() if report is None else report
    errors = [
        "schema " + item.message
        for item in Draft202012Validator(
            json.loads(SCHEMA.read_text()), format_checker=FormatChecker()
        ).iter_errors(value)
    ]
    checker_errors, _ = check(value)
    errors.extend("checker " + item for item in checker_errors)
    result_bytes, report_bytes = generated()
    candidate = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
    if result_bytes != candidate:
        errors.append("deterministic result drift")
    if report_bytes != report.encode():
        errors.append("deterministic report drift")
    for token in (
        "540 exact non-Bach",
        "18 q1q2 channels / 51",
        "rank **30**",
        "second and third variations",
        "dominated by local `D`",
        "all seven common snapshot hashes",
        "Gate A remains fail closed",
        "no Lorentzian propagator",
    ):
        if token not in report:
            errors.append("report token " + token)
    return errors


def main() -> int:
    errors = verify()
    print("CLASSICAL_IMPORT_GATE_V5_RECONCILIATION_SCHEMA: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
