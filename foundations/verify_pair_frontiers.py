#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.check_pair_frontiers import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_PAIR_FRONTIER_ANALYSIS_V0.json"
CUBE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
SCHEMA = ROOT / "foundations/schema/foundational-pair-frontier-analysis-v0.schema.json"
REPORT = ROOT / "foundations/reports/pair-frontier-analysis.md"
REQUEST = ROOT / "planning/forge-requests/foundations-scope-frontier-importer.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(
    *,
    result: dict[str, Any] | None = None,
    cube: dict[str, Any] | None = None,
    report: str | None = None,
    request: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    result = load(RESULT) if result is None else result
    cube = load(CUBE) if cube is None else cube
    report = REPORT.read_text() if report is None else report
    request = load(REQUEST) if request is None else request
    errors: list[str] = []
    checks: list[str] = []

    schema = load(SCHEMA)
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(result)
    except Exception as exc:  # jsonschema supplies the diagnostic in the receipt rail
        errors.append("schema " + str(exc).splitlines()[0])
    checks.append("Draft 2020-12 schema")

    if (
        result.get("result_id") != "FOUNDATIONAL_PAIR_FRONTIER_ANALYSIS_V0"
        or result.get("lifecycle") != "LITERATURE_SCOPED"
        or result.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]
    ):
        errors.append("identity/lifecycle/dependency tags")
    checker_errors, summary = check(result, cube)
    errors.extend("checker " + item for item in checker_errors)
    if summary.get("projections") != 108 or summary.get("assessed_open_cells") != 26:
        errors.append("expected projection/open-cell counts")
    checks.append("independent 108-projection reconstruction and score audit")

    inputs = result.get("provenance", {}).get("inputs", [])
    if len(inputs) != 1:
        errors.append("provenance input count")
    else:
        source = ROOT / inputs[0].get("path", "")
        if source != CUBE or not source.is_file() or inputs[0].get("sha256") != sha256(source):
            errors.append("cube provenance hash")
    checks.append("content-pinned cube input")

    flags = result.get("claim_flags", {})
    for key in ("all_108_pair_projections_computed", "ranking_is_deterministic"):
        if flags.get(key) is not True:
            errors.append("positive claim flag " + key)
    for key in (
        "ranking_is_scientific_evidence",
        "not_mapped_treated_as_gap",
        "automatic_forge_registration_complete",
        "new_mathematical_theorem",
        "new_physical_theorem",
        "new_lorentzian_claim",
    ):
        if flags.get(key) is not False:
            errors.append("boundary claim flag " + key)
    if result.get("forge_projection", {}).get("state") != "NOT_REGISTERED":
        errors.append("Forge registration boundary")
    checks.append("heuristic/evidence and Forge-registration boundaries")

    report_tokens = (
        "108 distinct products of two dimensions",
        "26 bridgeable pair frontiers",
        "25 important but unseeded pair gaps",
        "Not-mapped cells contribute nothing",
        "Highest-scoring pair frontiers",
        "Finite/discrete restriction × Finite exact algebra",
        "ZF with weakened Choice × Algebraic C*-system",
        "Recommended open cells",
        "Pairwise overview",
        "0 — important but unseeded",
        "Forge integration boundary",
        "not a probability of success",
    )
    for token in report_tokens:
        if token not in report:
            errors.append("report token " + token)
    checks.append("plain-language generated report and pairwise maps")

    body = request.get("body", {})
    if (
        request.get("id") != "sf:forge-request/foundations-scope-frontier-importer"
        or request.get("kind") != "work"
        or request.get("schema") != "work-v0"
        or body.get("state") not in ("REQUESTED", "ACCEPTED", "LANDED", "DECLINED", "OPEN")
        or body.get("depends_on") != []
    ):
        errors.append("Forge request identity/state")
    for token in (
        "typed Scope coordinates",
        "all 108 pair projections",
        "No node or absence claim for an unassessed coordinate",
        "no physics-specific foundation/carrier/obligation identifiers hard-coded",
        "no producer replay called independent verification",
    ):
        if token not in " ".join(str(body.get(key, "")) for key in ("objective", "stop_condition", "forbid")):
            errors.append("Forge request token " + token)
    checks.append("consumer-driven Forge capability request")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_PAIR_FRONTIER_ANALYSIS_V0: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
