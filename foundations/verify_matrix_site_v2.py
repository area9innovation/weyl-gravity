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
        "emitted": 576,
        "synthetic_not_mapped": 0,
        "total_not_mapped": 0,
        "coverage_classified": 576,
        "migration_reviewed": 576,
        "migration_pending": 0,
        "reviewed_no_transfer": 88,
        "evidence_records": 83,
        "graph_edges": 10,
        "ladder_levels": 6,
        "completion_branches": 7,
        "completion_stages": 11,
        "completion_cells": 77,
        "completion_routes": 9,
        "completion_decisions": 11,
        "theory_profiles": 36,
        "carrier_envelopes": 6,
        "pareto_profiles": 4,
        "prototype_assemblies": 9,
        "assembly_interfaces": 63,
        "empirical_comparisons": 0,
        "calibration_comparisons": 4,
        "calibration_benchmark_families": 3,
        "model_scoped_assemblies": 2,
        "model_scoped_stages": 13,
        "model_scoped_interfaces": 11,
        "bounded_complete_assemblies": 1,
        "certified_cross_cell_interfaces": 2,
        "certified_carrier_interfaces": 1,
        "numerical_reproduction_records": 1,
        "certified_assembly_interface_instances": 5,
        "dual_direct_cells": 8,
        "mark_counts": {"G": 28, "Gl": 2, "L": 112, "LR": 8, "Lr": 7, "Ol": 169, "P": 19, "Pl": 78, "Plr": 12, "Pr": 51, "R": 87, "Rl": 3},
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
    for key in ("static_site_generated", "all_cartesian_coordinates_visible", "all_cartesian_coordinates_assessed", "zero_not_mapped", "reviewed_gaps_distinguished_from_results", "all_emitted_migrations_reviewed", "coverage_and_migration_separated", "all_used_evidence_resolved", "theory_profiles_generated", "theory_assembly_atlas_generated", "bounded_observable_reconstruction_exposed", "localized_coefficient_weak_wave_exposed", "named_h2_test_completion_exposed", "smooth_to_h2_translator_exposed", "support_indexed_test_comparison_exposed", "scalar_green_choice_audit_exposed", "strict_candidate_q2_green_first_response_exposed", "strict_candidate_q2_green_foundations_exposed", "at_least_one_cross_cell_interface_certified", "composition_and_observation_rails_separated", "new_lorentzian_claim"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    if flags.get("completion_atlas_exposed") is not True:
        errors.append("positive flag completion_atlas_exposed")
    for key in ("scientific_claims_duplicated_by_hand", "literature_complete", "unmapped_means_absent", "reviewed_gap_means_absent", "reviewed_no_transfer_means_absent", "priority_score_is_theorem", "complete_observationally_valid_theory_identified", "strict_authoritative_q2_green_compatibility_exposed", "strict_recursive_nonlinear_green_trees_exposed"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    checks.append("fail-closed claim flags")
    for token in ("576", "169 `REVIEWED_GAP`", "0\n`NOT_MAPPED`", "not a result", "selected priority", "literature-absence claim", "all 401 prior", "51 emitted blanks", "124", "without transferring evidence", "exactly twenty additional empty cells", "seventeen", "three pieces-only", "classification before QME restoration", "none of those toy-model statements is a Weyl-BV promotion", "two certified", "CONDITIONAL_BRIDGE", "unique normal", "coarse numerical reproduction", "not empirical validation", "conditional bridges remain open", "N(k)=k+ell(K)+1", "not the full field", "rank-10", "coefficient by coefficient", "not a theorem for\nevery smooth test function", "named H2 completion", "nonmetrizable LF test topology", "representation-to-causality", "retarded and\nadvanced Green maps", "scalar benchmark", "separate coverage and migration", "Earlier cubes remain unchanged", "does not establish"):
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
