#!/usr/bin/env python3
"""Verify schema, independent numerics, provenance, and report boundaries."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.build_mannheim_ngc3198_assembly import generated
from foundations.check_mannheim_ngc3198_assembly import check


RESULT = ROOT / "foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json"
REPORT = ROOT / "foundations/reports/mannheim-ngc3198-model-assembly-v1.md"
SCHEMA = ROOT / "foundations/schema/foundational-mannheim-ngc3198-model-assembly-v1.schema.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def verify(*, value: dict[str, Any] | None = None, report: str | None = None) -> tuple[list[str], list[str]]:
    result = load(RESULT) if value is None else value
    text = REPORT.read_text() if report is None else report
    errors = ["schema " + item.message for item in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(result)]
    checks = ["Draft 2020-12 model-assembly schema"]
    if result.get("canonical_digest") != canonical_digest(result):
        errors.append("canonical digest")
    checks.append("canonical result digest")

    checker_errors, _ = check(result)
    errors.extend("checker " + item for item in checker_errors)
    checks.append("independent C++17 Bessel, source-pin, applicability, interface, and gate audit")

    result_bytes, report_bytes = generated()
    if (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode() != result_bytes:
        errors.append("deterministic result drift")
    if text.encode() != report_bytes:
        errors.append("deterministic report drift")
    checks.append("deterministic result and report")

    for item in result.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append("provenance " + item.get("path", ""))
    checks.append("content-addressed local authorities and extracted observations")

    for token in (
        "first model-scoped Mannheim", "seven-stage chain", "153.",
        "coarse reproduction", "SPARC", "No parameter is refitted",
        "reduced chi-squared", "fails", "partial", "does not establish",
    ):
        if token.lower() not in text.lower():
            errors.append("report token " + token)
    checks.append("human-readable mixed result and complete claim boundary")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
