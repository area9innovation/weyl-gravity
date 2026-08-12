#!/usr/bin/env python3
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
from foundations.check_refined_intersection_cube import check
from foundations.refine_intersection_cube import generated

RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-intersection-cube-v1.schema.json"
REPORT = ROOT / "foundations/reports/refined-intersection-cube.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(*, result=None, report=None) -> tuple[list[str], list[str]]:
    r = load(RESULT) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors: list[str] = []
    checks: list[str] = []
    errors.extend("schema " + error.message for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(r))
    checks.append("Draft 2020-12 schema")
    checker_errors, summary = check(r)
    errors.extend("checker " + error for error in checker_errors)
    if summary != {"digest": "37e04717bec0e78aaa9c6187a39fe6edb7dd512cdf8d9597455dc526d637fa9d", "cells": 452, "cartesian_total": 576, "status_counts": {"LITERATURE_RESULT": 90, "LOCAL_RESULT": 85, "MIGRATION_UNRESOLVED": 112, "PIECES_ONLY": 158, "PRIORITY_GAP": 7}, "overlays": 11}:
        errors.append("expected refined summary")
    checks.append("independent coordinate and migration audit")
    expected_result, expected_report = generated()
    if json.dumps(r, indent=2, ensure_ascii=False) + "\n" != expected_result:
        errors.append("deterministic result drift")
    if text != expected_report:
        errors.append("deterministic report drift")
    checks.append("deterministic migration and report")
    for pin in r.get("provenance", {}).get("inputs", []):
        path = ROOT / pin.get("path", "")
        if not path.is_file() or sha(path) != pin.get("sha256"):
            errors.append("provenance " + str(pin.get("path")))
    checks.append("v0, cylinder, and finite-interaction pins")
    flags = r.get("claim_flags", {})
    for key in ("v0_preserved", "overloaded_obligations_decomposed", "blind_parent_status_inheritance_forbidden", "cylinder_ladder_integrated"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("all_576_cells_assessed", "literature_complete", "weakest_base_proved", "new_lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    checks.append("compatibility and claim boundaries")
    for token in ("V0 remains unchanged", "576 possible coordinates", "452 cells", "340 qualified", "112 migration-unresolved", "Finite interaction is no longer finite renormalization", "spectral dynamics is no longer causal propagation", "A state is not a selected physical state", "Cylinder-wave insertion", "MIGRATION_UNRESOLVED", "does not establish a new Lorentzian-causal result"):
        if token not in text:
            errors.append("report token " + token)
    checks.append("plain-language refined overview")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_INTERSECTION_CUBE_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
