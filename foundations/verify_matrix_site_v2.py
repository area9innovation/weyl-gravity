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

from foundations.build_matrix_site_v2 import generated
from foundations.check_matrix_site_v2 import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json"
SCHEMA = ROOT / "foundations/schema/foundational-matrix-explorer-site-v2.schema.json"
REPORT = ROOT / "foundations/reports/matrix-explorer-site-v2.md"
MANIFEST = ROOT / "foundations/site/manifest.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def verify(*, result=None, report=None) -> tuple[list[str], list[str]]:
    value = load(RESULT) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors: list[str] = []
    checks: list[str] = []
    errors.extend("schema " + error.message for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(value))
    checks.append("Draft 2020-12 result schema")
    checker_errors, summary = check()
    errors.extend("checker " + error for error in checker_errors)
    expected_summary = {
        "digest": value.get("provenance", {}).get("canonical_data_digest"),
        "cells": 576,
        "emitted": 452,
        "synthetic_not_mapped": 124,
        "total_not_mapped": 205,
        "coverage_classified": 371,
        "migration_reviewed": 452,
        "migration_pending": 0,
        "reviewed_no_transfer": 88,
        "evidence_records": 70,
        "graph_edges": 10,
        "ladder_levels": 6,
        "theory_profiles": 36,
        "carrier_envelopes": 6,
        "pareto_profiles": 2,
        "prototype_assemblies": 7,
        "assembly_interfaces": 49,
        "empirical_comparisons": 0,
        "certified_cross_cell_interfaces": 1,
        "certified_assembly_interface_instances": 2,
        "dual_direct_cells": 7,
        "mark_counts": {"G": 30, "L": 76, "LR": 7, "Lr": 6, "P": 20, "Pl": 75, "Plr": 13, "Pr": 51, "R": 90, "Rl": 3, "\u00b7": 205},
    }
    if summary != expected_summary:
        errors.append("expected independent summary")
    checks.append("independent full-surface, migration, and evidence audit")
    for path, content in generated().items():
        if not path.is_file() or path.read_bytes() != content:
            errors.append("deterministic drift " + str(path.relative_to(ROOT)))
    checks.append("deterministic static build")
    if hashlib.sha256(MANIFEST.read_bytes()).hexdigest() != value.get("provenance", {}).get("manifest_sha256"):
        errors.append("manifest pin")
    checks.append("content-addressed manifest")
    flags = value.get("claim_flags", {})
    for key in ("static_site_generated", "all_cartesian_coordinates_visible", "all_emitted_migrations_reviewed", "coverage_and_migration_separated", "all_used_evidence_resolved", "theory_profiles_generated", "theory_assembly_atlas_generated", "at_least_one_cross_cell_interface_certified", "composition_and_observation_rails_separated"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("scientific_claims_duplicated_by_hand", "literature_complete", "unmapped_means_absent", "reviewed_no_transfer_means_absent", "priority_score_is_theorem", "complete_observationally_valid_theory_identified", "new_lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    checks.append("fail-closed claim flags")
    for token in ("576", "452", "reviewed", "0 pending", "88", "81", "124", "371", "two weak-arithmetic", "five carefully typed evidence overlays", "CONDITIONAL_BRIDGE", "five explicit hypotheses", "NOT_MAPPED", "not a literature-absence claim", "separate coverage and migration", "Earlier cubes remain unchanged", "does not establish"):
        if token not in text:
            errors.append("report token " + token)
    checks.append("human-readable migration and deployment report")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
