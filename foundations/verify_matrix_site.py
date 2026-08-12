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
from foundations.build_matrix_site import generated
from foundations.check_matrix_site import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-matrix-explorer-site-v1.schema.json"
REPORT = ROOT / "foundations/reports/matrix-explorer-site.md"
MANIFEST = ROOT / "foundations/site/manifest.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def verify() -> tuple[list[str], list[str]]:
    result = load(RESULT)
    errors: list[str] = []
    checks: list[str] = []
    errors.extend("schema " + error.message for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(result))
    checks.append("Draft 2020-12 result schema")
    checker_errors, summary = check()
    errors.extend("checker " + error for error in checker_errors)
    if summary != {"digest": result.get("provenance", {}).get("canonical_data_digest"), "cells": 576, "emitted": 452, "not_mapped": 124, "evidence_records": 51, "graph_nodes": 12, "graph_edges": 10, "ladder_levels": 6}:
        errors.append("expected independent summary")
    checks.append("independent full-surface and evidence audit")
    for path, content in generated().items():
        if not path.is_file() or path.read_bytes() != content:
            errors.append("deterministic drift " + str(path.relative_to(ROOT)))
    checks.append("deterministic static build")
    if hashlib.sha256(MANIFEST.read_bytes()).hexdigest() != result.get("provenance", {}).get("manifest_sha256"):
        errors.append("manifest pin")
    checks.append("content-addressed manifest")
    flags = result.get("claim_flags", {})
    for key in ("static_site_generated", "all_cartesian_coordinates_visible", "all_used_evidence_resolved"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("scientific_claims_duplicated_by_hand", "literature_complete", "unmapped_means_absent", "priority_score_is_theorem", "new_lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    checks.append("fail-closed claim flags")
    report = REPORT.read_text()
    for token in ("576", "452", "124", "NOT_MAPPED", "51-record", "multi-select", "permalinks", "typed implication graph", "file://", "does not establish"):
        if token not in report:
            errors.append("report token " + token)
    checks.append("human-readable deployment and boundary report")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_MATRIX_EXPLORER_SITE_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
