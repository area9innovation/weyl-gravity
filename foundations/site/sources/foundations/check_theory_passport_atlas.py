#!/usr/bin/env python3
"""Independent fail-closed checker for the end-to-end theory passports."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_END_TO_END_THEORY_PASSPORT_ATLAS_V1.json"
STAGE_IDS = ["FOUNDATIONAL_ASSUMPTIONS", "STATE_SPACE", "DYNAMICS", "OBSERVABLE", "PREDICTION", "EMPIRICAL_BENCHMARK"]
READY = {"ESTABLISHED_EXACT", "ESTABLISHED_SCOPED", "ESTABLISHED_NUMERIC", "EMPIRICAL_PASS"}
ASSESSED = READY | {"EMPIRICAL_FAIL", "PARTIAL"}
STATUSES = READY | {"EMPIRICAL_FAIL", "PARTIAL", "OPEN", "NOT_REACHED"}
EXPECTED = {
    "STANDARD_GR_CASSINI": (["ESTABLISHED_SCOPED", "ESTABLISHED_SCOPED", "ESTABLISHED_EXACT", "ESTABLISHED_EXACT", "ESTABLISHED_EXACT", "EMPIRICAL_PASS"], "SUPPORTED_IN_DECLARED_SCOPE"),
    "NEWTONIAN_BARYONS_NGC3198": (["ESTABLISHED_SCOPED", "ESTABLISHED_SCOPED", "ESTABLISHED_SCOPED", "ESTABLISHED_SCOPED", "ESTABLISHED_NUMERIC", "EMPIRICAL_FAIL"], "FAILED_DECLARED_GATE"),
    "GR_NFW_NGC3198": (["ESTABLISHED_SCOPED", "ESTABLISHED_SCOPED", "ESTABLISHED_SCOPED", "ESTABLISHED_SCOPED", "ESTABLISHED_NUMERIC", "EMPIRICAL_PASS"], "SUPPORTED_IN_DECLARED_SCOPE"),
    "MANNHEIM_NGC3198": (["ESTABLISHED_SCOPED", "ESTABLISHED_SCOPED", "ESTABLISHED_SCOPED", "ESTABLISHED_SCOPED", "ESTABLISHED_NUMERIC", "EMPIRICAL_FAIL"], "FAILED_DECLARED_GATE"),
    "BATEMAN_TUROK_EUCLIDEAN": (["ESTABLISHED_SCOPED", "ESTABLISHED_EXACT", "PARTIAL", "PARTIAL", "PARTIAL", "OPEN"], "NOT_TESTED"),
    "KREIN_FREE_MODE": (["ESTABLISHED_SCOPED", "ESTABLISHED_EXACT", "ESTABLISHED_EXACT", "OPEN", "NOT_REACHED", "NOT_REACHED"], "NOT_TESTED"),
    "CONSTRUCTIVE_CODED_WAVE": (["ESTABLISHED_EXACT", "ESTABLISHED_SCOPED", "ESTABLISHED_EXACT", "ESTABLISHED_EXACT", "OPEN", "NOT_REACHED"], "NOT_TESTED"),
    "PURE_WEYL_BV_CAUSAL": (["ESTABLISHED_EXACT", "PARTIAL", "ESTABLISHED_EXACT", "OPEN", "NOT_REACHED", "NOT_REACHED"], "NOT_TESTED"),
}
EXPECTED_SOURCES = {
    "GR_CASSINI": ("foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json", "FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1"),
    "NGC3198_COMMON": ("foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json", "FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1"),
    "MANNHEIM_NGC3198": ("foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json", "FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1"),
    "BT_EUCLIDEAN": ("foundations/results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json", "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"),
    "KREIN_FREE": ("foundations/results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json", "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"),
    "CODED_WAVE": ("foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json", "FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1"),
    "PURE_WEYL": ("foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49.json", "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49"),
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def pointer(value: Any, path: str) -> Any:
    current = value
    if not path:
        return current
    for raw in path.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def expected_summary(stages: list[dict[str, Any]], empirical: str) -> dict[str, Any]:
    ready_through = None
    first = None
    for item in stages:
        if item["status"] in READY:
            ready_through = item["id"]
        else:
            first = item["id"]
            break
    furthest = next((item["id"] for item in reversed(stages) if item["status"] in ASSESSED), None)
    return {
        "contiguous_ready_through": ready_through,
        "first_blocker_or_failure": first,
        "furthest_stage_with_evidence": furthest,
        "ready_stage_count": sum(item["status"] in READY for item in stages),
        "assessed_stage_count": sum(item["status"] in ASSESSED for item in stages),
        "reaches_empirical_benchmark": stages[-1]["status"] in {"EMPIRICAL_PASS", "EMPIRICAL_FAIL"},
        "empirical_disposition": empirical,
        "complete_theory": False,
    }


def expected_join(left: str, right: str) -> str:
    if left in READY and right in READY:
        return "CLOSED"
    if left in READY and right == "EMPIRICAL_FAIL":
        return "CLOSED_WITH_NEGATIVE_OUTCOME"
    if right == "NOT_REACHED":
        return "NOT_REACHED"
    return "OPEN"


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    result = load(RESULT) if value is None else value
    errors: list[str] = []
    if result.get("result_id") != "FOUNDATIONAL_END_TO_END_THEORY_PASSPORT_ATLAS_V1":
        errors.append("result identity")
    if result.get("canonical_digest") != digest(result):
        errors.append("canonical digest")

    sources = result.get("sources", {})
    source_values: dict[str, dict[str, Any]] = {}
    if set(sources) != set(EXPECTED_SOURCES):
        errors.append("source registry closure")
    for source_id, (relative, result_id) in EXPECTED_SOURCES.items():
        entry = sources.get(source_id, {})
        path = ROOT / relative
        if entry.get("path") != relative or entry.get("result_id") != result_id:
            errors.append("source identity " + source_id)
            continue
        if not path.is_file() or entry.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("source pin " + source_id)
            continue
        source_values[source_id] = load(path)
        if source_values[source_id].get("result_id") != result_id:
            errors.append("source content identity " + source_id)

    stage_vocab = result.get("stage_vocabulary", [])
    if [item.get("id") for item in stage_vocab] != STAGE_IDS or any(not item.get("label") or not item.get("question") for item in stage_vocab):
        errors.append("six-stage vocabulary")
    status_vocab = result.get("status_vocabulary", [])
    if {item.get("id") for item in status_vocab} != STATUSES or any(not item.get("plain_meaning") for item in status_vocab):
        errors.append("status vocabulary")
    if {item.get("id") for item in status_vocab if item.get("counts_as_ready")} != READY:
        errors.append("ready-status semantics")

    passports = result.get("passports", [])
    by_id = {item.get("id"): item for item in passports}
    if len(passports) != len(EXPECTED) or set(by_id) != set(EXPECTED):
        errors.append("passport registry closure")
    assertion_count = 0
    for passport_id, (statuses, empirical) in EXPECTED.items():
        item = by_id.get(passport_id)
        if not item:
            continue
        stages = item.get("stages", [])
        if [stage.get("id") for stage in stages] != STAGE_IDS:
            errors.append("stage order " + passport_id)
            continue
        actual_statuses = [stage.get("status") for stage in stages]
        if actual_statuses != statuses:
            errors.append("independent status contract " + passport_id)
        for stage in stages:
            if not stage.get("summary") or not stage.get("boundary"):
                errors.append("plain stage explanation " + passport_id + " " + str(stage.get("id")))
            assertions = stage.get("source_assertions", [])
            if not assertions:
                errors.append("unseeded stage " + passport_id + " " + str(stage.get("id")))
            for claim in assertions:
                assertion_count += 1
                source_id = claim.get("source")
                if source_id not in source_values:
                    errors.append("unknown assertion source " + str(source_id))
                    continue
                try:
                    actual = pointer(source_values[source_id], claim.get("pointer", ""))
                except (KeyError, IndexError, TypeError, ValueError):
                    errors.append("unresolved assertion " + passport_id + " " + str(claim.get("pointer")))
                    continue
                if actual != claim.get("expected"):
                    errors.append("source assertion drift " + passport_id + " " + str(claim.get("pointer")))
        if item.get("journey_summary") != expected_summary(stages, empirical):
            errors.append("derived journey summary " + passport_id)
        joins = item.get("joins", [])
        if len(joins) != 5:
            errors.append("join count " + passport_id)
        else:
            for index, join in enumerate(joins):
                if join.get("from") != STAGE_IDS[index] or join.get("to") != STAGE_IDS[index + 1] or join.get("status") != expected_join(statuses[index], statuses[index + 1]):
                    errors.append("derived join " + passport_id + " " + str(index))
        if not item.get("highest_value_next_step") or item.get("journey_summary", {}).get("complete_theory") is not False:
            errors.append("next-step or complete-theory boundary " + passport_id)

    summary = result.get("atlas_summary", {})
    expected_atlas = {
        "passport_count": 8,
        "benchmark_groups": ["CASSINI_SOLAR_SYSTEM", "NGC3198_COMMON_PROTOCOL", "NO_EMPIRICAL_BENCHMARK"],
        "empirical_dispositions": ["FAILED_DECLARED_GATE", "NOT_TESTED", "SUPPORTED_IN_DECLARED_SCOPE"],
        "reaches_empirical_benchmark": 4,
        "passes_declared_empirical_gate": 2,
        "fails_declared_empirical_gate": 2,
        "not_yet_empirically_tested": 4,
        "complete_theories": 0,
    }
    if summary != expected_atlas:
        errors.append("atlas summary")
    flags = result.get("claim_flags", {})
    for key in ("fixed_six_stage_crosswalk_complete", "all_stage_promotions_source_asserted", "common_ngc3198_protocol_exposed", "scoped_empirical_pass_and_failure_distinguished", "stage_local_evidence_distinguished_from_end_to_end_composition"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("complete_theory_selected", "matrix_cell_grades_promoted", "new_empirical_analysis_performed"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    if len(result.get("does_not_establish", [])) < 7:
        errors.append("does-not-establish ledger")
    return errors, {
        "passports": len(passports),
        "stages": sum(len(item.get("stages", [])) for item in passports),
        "joins": sum(len(item.get("joins", [])) for item in passports),
        "source_assertions": assertion_count,
        "empirical_passes": summary.get("passes_declared_empirical_gate"),
        "empirical_failures": summary.get("fails_declared_empirical_gate"),
        "not_tested": summary.get("not_yet_empirically_tested"),
    }


def main() -> int:
    errors, summary = check()
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, **summary}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
