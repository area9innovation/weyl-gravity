#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from foundations.check_full_surface_gap_audit import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-full-surface-gap-audit-v1.schema.json"
REPORT = ROOT / "foundations/reports/full-surface-gap-audit.md"


def load(path: Path):
    return json.loads(path.read_text())


def canonical_digest(value: dict) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def verify(*, result=None, report=None):
    r = load(RESULT) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors: list[str] = []
    errors.extend("schema " + e.message for e in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(r))
    checker_errors, summary = check(r)
    errors.extend("checker " + e for e in checker_errors)
    if summary["digest"] != r.get("independent_checker", {}).get("expected_digest"):
        errors.append("checker digest")
    if canonical_digest(r) != r.get("canonical_digest"):
        errors.append("canonical digest")
    for source in r.get("provenance", {}).get("inputs", []):
        path = ROOT / source.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source.get("sha256"):
            errors.append("source hash " + source.get("path", "missing"))
    flags = r.get("claim_flags", {})
    for name in ("all_175_remaining_coordinates_reviewed", "all_576_coordinates_formulated", "new_reviewed_gap_status_defined"):
        if flags.get(name) is not True:
            errors.append("positive flag " + name)
    for name in ("direct_results_added", "pieces_only_results_added", "priority_assignments_added", "literature_complete", "literature_absence_proved", "all_physical_obligations_solved", "complete_theory_identified", "new_lorentzian_claim"):
        if flags.get(name) is not False:
            errors.append("boundary flag " + name)
    for token in ("175 remaining coordinates", "51", "124", "REVIEWED_GAP", "reviewed open question", "not result", "not a replacement", "do not license evidence transfer", "literature-absence", "LORENTZIAN-CAUSAL"):
        if token not in text:
            errors.append("report token " + token)
    return errors


def main() -> int:
    errors = verify()
    print("FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
