#!/usr/bin/env python3
"""Verify schema, deterministic generation, independent fit, pins, and exposition."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from foundations.build_ngc3198_common_fit_comparison import build, canonical_digest, report
from foundations.check_ngc3198_common_fit_comparison import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json"
REPORT = ROOT / "foundations/reports/ngc3198-common-fit-comparison-v1.md"
SCHEMA = ROOT / "foundations/schema/foundational-ngc3198-common-fit-comparison-v1.schema.json"


def verify(*, value: dict[str, Any] | None = None, text: str | None = None) -> tuple[list[str], list[str]]:
    result = json.loads(RESULT.read_text()) if value is None else value
    human = REPORT.read_text() if text is None else text
    errors = ["schema " + item.message for item in Draft202012Validator(json.loads(SCHEMA.read_text()), format_checker=FormatChecker()).iter_errors(result)]
    checks = ["Draft 2020-12 schema"]
    if result.get("canonical_digest") != canonical_digest(result): errors.append("canonical digest")
    checks.append("canonical digest")
    fresh = build()
    if fresh != result: errors.append("deterministic result drift")
    if report(result) != human: errors.append("deterministic report drift")
    checks.append("deterministic producer and report")
    checker_errors, _ = check(result)
    errors.extend("checker " + item for item in checker_errors)
    checks.append("independent C++ Bessel and Nelder--Mead fit")
    protocol = ROOT / result.get("protocol", "")
    if not protocol.is_file() or hashlib.sha256(protocol.read_bytes()).hexdigest() != result.get("protocol_sha256"): errors.append("protocol pin")
    checks.append("content-addressed protocol")
    for token in ("same 39 SPARC", "baryons alone", "Mannheim", "GR+NFW", "AICc", "single-galaxy", "does not establish"):
        if token.lower() not in human.lower(): errors.append("report token " + token)
    checks.append("plain-language result and boundaries")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1: " + ("PASS" if not errors else "FAIL"))
    for item in errors if errors else checks: print("  - " + item)
    return bool(errors)


if __name__ == "__main__": raise SystemExit(main())
