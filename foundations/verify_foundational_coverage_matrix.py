#!/usr/bin/env python3
"""Independent structural verifier for the populated foundations matrix."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SEED_LEDGER_PATH = ROOT / "foundations/literature-ledger.json"
SUPPLEMENT_PATH = ROOT / "foundations/literature-supplement-known-attempts-v1.json"
RESULT_PATH = ROOT / "foundations/results/FOUNDATIONAL_COVERAGE_MATRIX_V0.json"
SCHEMA_PATH = ROOT / "foundations/schema/foundational-coverage-matrix-v0.schema.json"
REPORT_PATH = ROOT / "foundations/reports/foundational-coverage-and-low-hanging-fruit.md"

AXES = {
    "LOGIC",
    "SET_EXISTENCE",
    "INFINITY",
    "CARRIER_GEOMETRY",
    "PHYSICAL_POSTULATES",
    "TARGET_CLAIMS",
}
COVERAGE_STATUSES = {"DIRECT", "PARTIAL", "ADJACENT", "ABSENT", "UNKNOWN"}
EDGE_RELATIONS = {
    "USED_BY_DISPLAYED_PROOF",
    "SUFFICIENT_OVER_BASE",
    "NECESSARY_OVER_BASE",
    "EQUIVALENT_OVER_BASE",
    "AVOIDED_BY_REFORMULATION",
    "INDEPENDENT_OVER_BASE",
    "UNKNOWN",
}
QUANTUM_TAGS = {
    "LOCAL-ALGEBRAIC",
    "EUCLIDEAN-SPECTRAL",
    "REDUCED-MODE",
    "LORENTZIAN-CAUSAL",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_HASH = re.compile(r"^[0-9a-f]{40}$")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def verify(
    root: Path = ROOT,
    *,
    seed: dict[str, Any] | None = None,
    supplement: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
    report_text: str | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checks: list[str] = []

    if seed is None:
        seed = load_json(root / SEED_LEDGER_PATH.relative_to(ROOT))
    if supplement is None:
        supplement = load_json(root / SUPPLEMENT_PATH.relative_to(ROOT))
    if result is None:
        result = load_json(root / RESULT_PATH.relative_to(ROOT))
    if report_text is None:
        report_text = (root / REPORT_PATH.relative_to(ROOT)).read_text(encoding="utf-8")
    load_json(root / SCHEMA_PATH.relative_to(ROOT))
    checks.append("schema and all structured files parse")

    if supplement.get("schema_version") != "foundational-literature-supplement-v1":
        errors.append("supplement schema_version mismatch")
    if supplement.get("ledger_id") != "FOUNDATIONAL_LITERATURE_SUPPLEMENT_KNOWN_ATTEMPTS_V1":
        errors.append("supplement ledger id mismatch")
    base_commit = supplement.get("repository_base_commit", "")
    if not GIT_HASH.fullmatch(base_commit):
        errors.append("supplement base commit is not a full Git hash")
    if result.get("repository_base_commit") != base_commit:
        errors.append("result and supplement base commits differ")
    checks.append("supplement identity and base provenance")

    seed_entries = seed.get("entries", [])
    supplement_entries = supplement.get("entries", [])
    if len(seed_entries) < 10 or len(supplement_entries) < 8:
        errors.append("one of the literature corpora is too small")
    seed_ids = [entry.get("id") for entry in seed_entries]
    supplement_ids = [entry.get("id") for entry in supplement_entries]
    all_ids = seed_ids + supplement_ids
    if len(all_ids) != len(set(all_ids)):
        errors.append("source ids are not unique across the two ledgers")
    checks.append("cross-ledger source identities are unique")

    metadata_only = 0
    content_pinned = 0
    for entry in supplement_entries:
        sid = entry.get("id", "<missing>")
        if entry.get("source_kind") != "PRIMARY_RESEARCH":
            errors.append(f"{sid}: supplement source is not PRIMARY_RESEARCH")
        if not str(entry.get("stable_url", "")).startswith("https://"):
            errors.append(f"{sid}: stable URL is not HTTPS")
        if not set(entry.get("bears_on", [])) <= AXES or not entry.get("bears_on"):
            errors.append(f"{sid}: invalid bears_on axes")
        if not entry.get("supported_statements") or not entry.get("boundary"):
            errors.append(f"{sid}: source lacks statement or boundary")
        artifact = entry.get("artifact", {})
        status = artifact.get("status")
        digest = artifact.get("sha256")
        if status == "CONTENT_PINNED":
            content_pinned += 1
            if not isinstance(digest, str) or not SHA256.fullmatch(digest):
                errors.append(f"{sid}: bad SHA-256 pin")
        elif status == "METADATA_ONLY":
            metadata_only += 1
            if digest is not None:
                errors.append(f"{sid}: metadata-only SHA-256 is not null")
        else:
            errors.append(f"{sid}: unsupported artifact status")
    if content_pinned < 6 or metadata_only < 1:
        errors.append("supplement does not expose both pinned and unresolved sources")
    unresolved = supplement.get("unresolved", [])
    if not unresolved or not any("metadata-only" in item.lower() for item in unresolved):
        errors.append("metadata-only sources are not fail-closed in unresolved ledger")
    checks.append("supplement pins, metadata, statements, and boundaries")

    if result.get("result_id") != "FOUNDATIONAL_COVERAGE_MATRIX_V0":
        errors.append("result id mismatch")
    if result.get("result_kind") != "LITERATURE_COVERAGE_AND_TRIAGE":
        errors.append("result kind mismatch")
    if result.get("lifecycle") != "LITERATURE_SCOPED":
        errors.append("coverage result promoted past LITERATURE_SCOPED")
    tags = set(result.get("dependency_tags", []))
    if not tags or not tags <= QUANTUM_TAGS or tags != {"LOCAL-ALGEBRAIC"}:
        errors.append("coverage result must be LOCAL-ALGEBRAIC only")
    checks.append("result identity, lifecycle, and dependency boundary")

    method = result.get("method", {})
    if set(method.get("coverage_statuses", {})) != COVERAGE_STATUSES:
        errors.append("coverage status vocabulary mismatch")
    if set(method.get("axis_order", [])) != AXES:
        errors.append("axis vocabulary mismatch")
    scoring = method.get("scoring", {})
    if scoring.get("status") != "HEURISTIC_PRIORITY_NOT_EVIDENCE":
        errors.append("priority scoring is not marked heuristic")
    if not scoring.get("warning"):
        errors.append("priority scoring lacks warning")
    checks.append("coverage and scoring vocabularies")

    source_set = set(all_ids)
    attempts = result.get("attempts", [])
    attempt_ids = [attempt.get("id") for attempt in attempts]
    if len(attempts) < 15 or len(attempt_ids) != len(set(attempt_ids)):
        errors.append("attempt matrix is too small or has duplicate ids")
    direct_on_all = []
    for attempt in attempts:
        aid = attempt.get("id", "<missing>")
        refs = set(attempt.get("representative_sources", []))
        if not refs or not refs <= source_set:
            errors.append(f"{aid}: missing or unknown representative source")
        coverage = attempt.get("coverage", {})
        if set(coverage) != AXES:
            errors.append(f"{aid}: does not have exactly six coverage axes")
            continue
        statuses = []
        for axis, cell in coverage.items():
            status = cell.get("status")
            statuses.append(status)
            if status not in COVERAGE_STATUSES:
                errors.append(f"{aid}/{axis}: invalid coverage status")
            if not cell.get("note"):
                errors.append(f"{aid}/{axis}: missing coverage note")
        if all(status == "DIRECT" for status in statuses):
            direct_on_all.append(aid)
        if not attempt.get("unresolved_intersection") or not attempt.get("boundary"):
            errors.append(f"{aid}: missing intersection gap or boundary")
    if direct_on_all:
        errors.append(f"attempts promoted as DIRECT on all axes: {direct_on_all}")
    required_attempts = {
        "ATTEMPT-SECOND-ORDER-RM",
        "ATTEMPT-RM-BANACH-SEPARATION",
        "ATTEMPT-BISHOP-QM",
        "ATTEMPT-SDG-GR",
        "ATTEMPT-OPERATIONAL-QM",
        "ATTEMPT-KREIN-QUANTUM",
        "ATTEMPT-REPO-EXACT-BV",
        "ATTEMPT-REPO-GREEN",
    }
    if not required_attempts <= set(attempt_ids):
        errors.append("matrix omits a required cross-programme control")
    checks.append("attempt sources, six-axis cells, gaps, and no six-axis promotion")

    opportunities = result.get("opportunities", [])
    opportunity_ids = [opportunity.get("id") for opportunity in opportunities]
    ranks = [opportunity.get("rank") for opportunity in opportunities]
    if ranks != list(range(1, len(opportunities) + 1)):
        errors.append("opportunity ranks are not contiguous and ordered")
    if len(opportunity_ids) != len(set(opportunity_ids)) or len(opportunities) < 8:
        errors.append("opportunities are too few or have duplicate ids")
    priorities = []
    for opportunity in opportunities:
        oid = opportunity.get("id", "<missing>")
        scores = opportunity.get("scores", {})
        score_fields = (
            "scientific_leverage",
            "repository_readiness",
            "scope_boundedness",
            "literature_underexposure",
            "dependency_cost",
        )
        if any(not isinstance(scores.get(field), int) or not 1 <= scores[field] <= 5 for field in score_fields):
            errors.append(f"{oid}: invalid ordinal score")
            continue
        expected = sum(scores[field] for field in score_fields[:-1]) - scores["dependency_cost"]
        if scores.get("priority_score") != expected:
            errors.append(f"{oid}: priority score arithmetic mismatch")
        priorities.append(scores.get("priority_score"))
        if opportunity.get("candidate_relation") not in EDGE_RELATIONS:
            errors.append(f"{oid}: invalid candidate relation")
        if not opportunity.get("first_artifact") or not opportunity.get("stop_condition"):
            errors.append(f"{oid}: missing first artifact or stop condition")
    if priorities != sorted(priorities, reverse=True):
        errors.append("opportunities are not sorted by nonincreasing priority score")
    expected_top = [
        "OP-EXACT-BV-WEAK-BASELINE",
        "OP-KREIN-EXPLICIT-J-AUDIT",
        "OP-SEPARATION-WITNESS-CROSSWALK",
    ]
    if opportunity_ids[:3] != expected_top:
        errors.append("top-three low-hanging sequence drifted")
    checks.append("priority arithmetic, ordering, relations, and stop conditions")

    sequence = result.get("recommended_sequence", [])
    sequenced = [oid for phase in sequence for oid in phase.get("opportunities", [])]
    if not set(sequenced) <= set(opportunity_ids):
        errors.append("recommended sequence refers to unknown opportunities")
    if not set(expected_top) <= set(sequenced):
        errors.append("recommended sequence omits a top-three opportunity")
    checks.append("recommended phases reference ranked opportunities")

    hotspot_counts = {
        item.get("topic"): item.get("files")
        for item in result.get("repository_hotspots", {}).get("counts", [])
    }
    if hotspot_counts.get("Krein or fundamental symmetry", 0) < 500:
        errors.append("Krein hotspot no longer supports the recorded readiness claim")
    if hotspot_counts.get("Green operator or Green function", 0) < 200:
        errors.append("Green hotspot no longer supports the recorded readiness claim")
    if hotspot_counts.get("Hahn-Banach, Zorn, or axiom of choice") != 1:
        errors.append("foundational-vocabulary hotspot control drifted")
    if "not theorem evidence" not in result.get("repository_hotspots", {}).get("scope", ""):
        errors.append("hotspot counts are not bounded as navigation evidence")
    checks.append("repository hotspot controls and evidence boundary")

    flags = result.get("claim_flags", {})
    required_false = {
        "literature_review_complete",
        "formal_reverse_mathematics_result",
        "constructive_certificate_proved",
        "choice_free_krein_completion",
        "physical_postulate_implies_choice",
        "finite_physics_established",
        "lorentzian_claim",
    }
    for flag in required_false:
        if flags.get(flag) is not False:
            errors.append(f"claim flag {flag} must fail closed")
    if flags.get("coverage_matrix_populated") is not True or flags.get("priority_triage_recorded") is not True:
        errors.append("checkpoint flags are not true")
    checks.append("claim flags distinguish checkpoint from theorem")

    findings = result.get("coverage_findings", [])
    if len(findings) < 4:
        errors.append("too few coverage findings")
    for finding in findings:
        if finding.get("status") not in {"CORPUS_OBSERVATION", "HEURISTIC_TRIAGE"}:
            errors.append(f"{finding.get('id')}: promoted finding status")
        if not finding.get("does_not_establish"):
            errors.append(f"{finding.get('id')}: missing does_not_establish")
    if not result.get("does_not_establish") or not result.get("assumptions"):
        errors.append("result lacks global assumptions or boundaries")
    checks.append("finding and global honest boundaries")

    expected_ledgers = {
        "foundations/literature-ledger.json",
        "foundations/literature-supplement-known-attempts-v1.json",
    }
    if set(result.get("source_ledgers", [])) != expected_ledgers:
        errors.append("result source ledgers mismatch")
    if result.get("human_report") != "foundations/reports/foundational-coverage-and-low-hanging-fruit.md":
        errors.append("result human-report path mismatch")
    checks.append("machine result links both ledgers and report")

    for token in (
        "FOUNDATIONAL_COVERAGE_MATRIX_V0",
        "LITERATURE_SCOPED",
        "LOCAL-ALGEBRAIC",
        "SUFFICIENT_OVER_BASE",
        "AVOIDED_BY_REFORMULATION",
        "Hahn--Banach",
        "Krein `J`",
        "not evidence",
        "LORENTZIAN-CAUSAL",
    ):
        if token not in report_text:
            errors.append(f"report missing required token: {token}")
    checks.append("human report mirrors rankings, relations, and boundaries")

    return errors, checks


def main() -> int:
    errors, checks = verify()
    if errors:
        print("FOUNDATIONAL_COVERAGE_MATRIX_V0: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"FOUNDATIONAL_COVERAGE_MATRIX_V0: PASS ({len(checks)}/{len(checks)} checks)")
    for check in checks:
        print(f"  - {check}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
