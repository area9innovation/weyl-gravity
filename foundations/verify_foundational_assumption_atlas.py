#!/usr/bin/env python3
"""Independent structural verifier for the reverse-foundations seed atlas."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "foundations/literature-ledger.json"
RESULT_PATH = ROOT / "foundations/results/FOUNDATIONAL_ASSUMPTION_ATLAS_V0.json"
SCHEMA_PATH = ROOT / "foundations/schema/foundational-literature-ledger-v1.schema.json"
REPORT_PATH = ROOT / "foundations/reports/foundational-assumption-atlas.md"
WORK_PATH = ROOT / "planning/work-items/reverse-foundations-assumption-atlas.json"

AXES = {
    "LOGIC",
    "SET_EXISTENCE",
    "INFINITY",
    "CARRIER_GEOMETRY",
    "PHYSICAL_POSTULATES",
    "TARGET_CLAIMS",
}
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


def git_blob(path: Path, root: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path)], cwd=root, text=True
    ).strip()


def verify(
    root: Path = ROOT,
    *,
    ledger: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
    report_text: str | None = None,
    work: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checks: list[str] = []

    if ledger is None:
        ledger = load_json(root / LEDGER_PATH.relative_to(ROOT))
    if result is None:
        result = load_json(root / RESULT_PATH.relative_to(ROOT))
    if report_text is None:
        report_text = (root / REPORT_PATH.relative_to(ROOT)).read_text(encoding="utf-8")
    if work is None:
        work = load_json(root / WORK_PATH.relative_to(ROOT))
    load_json(root / SCHEMA_PATH.relative_to(ROOT))
    checks.append("schema and structured files parse")

    if ledger.get("schema_version") != "foundational-literature-ledger-v1":
        errors.append("ledger schema_version mismatch")
    if ledger.get("ledger_id") != "FOUNDATIONAL_LITERATURE_LEDGER_V1":
        errors.append("ledger id mismatch")
    checks.append("ledger identity")

    base_commit = ledger.get("repository_base_commit", "")
    if not GIT_HASH.fullmatch(base_commit):
        errors.append("ledger repository_base_commit is not a full Git hash")
    if result.get("repository_base_commit") != base_commit:
        errors.append("result and ledger base commits differ")
    checks.append("base provenance agrees")

    entries = ledger.get("entries", [])
    if len(entries) < 10:
        errors.append("seed corpus has fewer than ten sources")
    source_ids = [entry.get("id") for entry in entries]
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate source id")
    checks.append("source ids unique and corpus nontrivial")

    for entry in entries:
        sid = entry.get("id", "<missing>")
        if entry.get("source_kind") not in {
            "PRIMARY_RESEARCH",
            "AUTHORITATIVE_MONOGRAPH",
            "LOCAL_CERTIFIED_REPORT",
        }:
            errors.append(f"{sid}: invalid source_kind")
        if not str(entry.get("stable_url", "")).startswith("https://"):
            errors.append(f"{sid}: stable_url is not HTTPS")
        bears_on = set(entry.get("bears_on", []))
        if not bears_on or not bears_on <= AXES:
            errors.append(f"{sid}: invalid or empty bears_on axes")
        if not entry.get("supported_statements"):
            errors.append(f"{sid}: no supported statements")
        if not entry.get("boundary"):
            errors.append(f"{sid}: missing boundary")
    checks.append("source metadata, axes, statements, and boundaries")

    metadata_only = 0
    for entry in entries:
        sid = entry.get("id", "<missing>")
        artifact = entry.get("artifact", {})
        status = artifact.get("status")
        digest = artifact.get("sha256")
        if status == "CONTENT_PINNED":
            if not isinstance(digest, str) or not SHA256.fullmatch(digest):
                errors.append(f"{sid}: content-pinned source lacks SHA-256")
        elif status == "GIT_BLOB_PINNED":
            locator = artifact.get("locator", "")
            expected = artifact.get("git_blob", "")
            local_path = root / locator
            if not local_path.is_file():
                errors.append(f"{sid}: pinned local artifact is missing")
            elif not GIT_HASH.fullmatch(expected):
                errors.append(f"{sid}: invalid Git blob hash")
            elif git_blob(local_path, root) != expected:
                errors.append(f"{sid}: local Git blob has drifted")
            if digest is not None:
                errors.append(f"{sid}: Git-pinned artifact must use null sha256")
        elif status == "METADATA_ONLY":
            metadata_only += 1
            if digest is not None:
                errors.append(f"{sid}: metadata-only source must use null sha256")
        else:
            errors.append(f"{sid}: unknown artifact status")
    checks.append("content and Git artifact pins")

    unresolved = ledger.get("unresolved", [])
    if not unresolved:
        errors.append("missing unresolved-source ledger")
    if metadata_only and not any("metadata" in item.lower() for item in unresolved):
        errors.append("metadata-only source is not called out as unresolved")
    checks.append("fail-closed unresolved-source ledger")

    if result.get("result_id") != "FOUNDATIONAL_ASSUMPTION_ATLAS_V0":
        errors.append("result id mismatch")
    if result.get("result_kind") != "RESEARCH_ATLAS":
        errors.append("result kind is not RESEARCH_ATLAS")
    if result.get("lifecycle") != "LITERATURE_SCOPED":
        errors.append("seed atlas promoted past LITERATURE_SCOPED")
    checks.append("non-theorem lifecycle")

    tags = set(result.get("dependency_tags", []))
    if not tags or not tags <= QUANTUM_TAGS:
        errors.append("result has missing or invalid dependency tags")
    if tags != {"LOCAL-ALGEBRAIC"}:
        errors.append("literature atlas must remain LOCAL-ALGEBRAIC only")
    checks.append("quantum dependency boundary")

    result_axes = {axis.get("id") for axis in result.get("axes", [])}
    if result_axes != AXES:
        errors.append("result does not contain the exact six-axis decomposition")
    for axis in result.get("axes", []):
        if not axis.get("warning"):
            errors.append(f"axis {axis.get('id')}: missing warning")
    checks.append("six-axis decomposition and warnings")

    if set(result.get("edge_relations", [])) != EDGE_RELATIONS:
        errors.append("edge-relation vocabulary mismatch")
    checks.append("implication-status vocabulary")

    source_set = set(source_ids)
    findings = result.get("seed_findings", [])
    if len(findings) < 5:
        errors.append("too few seed findings")
    for finding in findings:
        fid = finding.get("id", "<missing>")
        refs = set(finding.get("evidence_sources", []))
        if not refs or not refs <= source_set:
            errors.append(f"{fid}: missing or unknown evidence source")
        if not finding.get("does_not_establish"):
            errors.append(f"{fid}: missing does_not_establish")
        if finding.get("status") not in {"LITERATURE_SCOPED", "PROGRAMME_RULE"}:
            errors.append(f"{fid}: promoted status")
    checks.append("finding provenance and honest boundaries")

    flags = result.get("claim_flags", {})
    required_false = {
        "literature_review_complete",
        "formal_reverse_mathematics_result",
        "physical_postulate_implies_choice",
        "choice_free_weyl_theory",
        "constructive_weyl_qft",
        "lorentzian_claim",
    }
    for flag in required_false:
        if flags.get(flag) is not False:
            errors.append(f"claim flag {flag} must fail closed")
    if flags.get("foundations_programme_started") is not True:
        errors.append("programme-started flag is not true")
    checks.append("claim flags fail closed")

    if not result.get("does_not_establish") or not result.get("next_gates"):
        errors.append("result lacks boundaries or next gates")
    checks.append("result boundaries and successors")

    if result.get("source_ledger") != "foundations/literature-ledger.json":
        errors.append("result source-ledger path mismatch")
    checks.append("result-to-ledger link")

    for token in (
        "FOUNDATIONAL_ASSUMPTION_ATLAS_V0",
        "LITERATURE_SCOPED",
        "LOCAL-ALGEBRAIC",
        "L + S + M + Enc(P) |- O",
        "USED_BY_DISPLAYED_PROOF",
        "EQUIVALENT_OVER_BASE",
        "AVOIDED_BY_REFORMULATION",
    ):
        if token not in report_text:
            errors.append(f"report missing required token: {token}")
    checks.append("human report mirrors result and edge statuses")

    body = work.get("body", {})
    if work.get("id") != "sf:program/work/reverse-foundations-assumption-atlas":
        errors.append("work-item id mismatch")
    if body.get("stream") != "reverse-foundations":
        errors.append("work-item stream mismatch")
    allowed = set(body.get("allowed_paths", []))
    expected_allowed = {
        "foundations/",
        "planning/work-items/reverse-foundations-assumption-atlas.json",
        "planning/events/",
    }
    if allowed != expected_allowed:
        errors.append("work-item allowed_paths mismatch")
    for field in ("objective", "current_gate", "stop_condition", "forbid"):
        if not body.get(field):
            errors.append(f"work item missing {field}")
    checks.append("Science Forge work-item scope and stop boundary")

    if "physical_postulate_implies_choice" not in flags:
        errors.append("physical-to-Choice claim has no explicit flag")
    if "Krein" not in " ".join(result.get("does_not_establish", [])):
        errors.append("Krein/Hilbert non-implication is not explicit")
    checks.append("two central negative controls")

    return errors, checks


def main() -> int:
    errors, checks = verify()
    if errors:
        print("FOUNDATIONAL_ASSUMPTION_ATLAS_V0: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"FOUNDATIONAL_ASSUMPTION_ATLAS_V0: PASS ({len(checks)}/{len(checks)} checks)")
    for check in checks:
        print(f"  - {check}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
