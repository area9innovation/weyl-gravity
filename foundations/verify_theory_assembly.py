#!/usr/bin/env python3
"""Independent fail-closed verifier for the theory assembly atlas."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "foundations/site/data.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-theory-assembly-atlas-v1.schema.json"
REPORT = ROOT / "foundations/reports/theory-assembly-atlas-v1.md"
SITE_JSON = ROOT / "foundations/site/assemblies.json"
SITE_JS = ROOT / "foundations/site/assemblies.js"
DIRECT = {"LOCAL_RESULT", "LITERATURE_RESULT"}
RANK = {"NOT_MAPPED": 0, "PRIORITY_GAP": 1, "PIECES_ONLY": 2, "LITERATURE_RESULT": 3, "LOCAL_RESULT": 3}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _selection_key(cell: dict[str, Any], assembly: dict[str, Any]) -> tuple[int, int, int, int, int]:
    roles = set(cell.get("evidence_roles", {}).values())
    return (
        RANK[cell["status"]],
        len(roles & {"DIRECT_LOCAL", "DIRECT_LITERATURE"}),
        cell["status"] == "LOCAL_RESULT",
        len(cell.get("evidence", [])),
        -(assembly["foundations"].index(cell["foundation"]) * 10 + assembly["carriers"].index(cell["carrier"])),
    )


def verify(*, value: dict[str, Any] | None = None) -> tuple[list[str], list[str]]:
    atlas = load(ATLAS)
    result = load(RESULT) if value is None else value
    errors: list[str] = []
    checks: list[str] = []
    errors.extend("schema " + item.message for item in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(result))
    checks.append("Draft 2020-12 assembly schema")
    if digest(result) != result.get("canonical_digest") or result.get("source_atlas_digest") != atlas.get("canonical_digest"):
        errors.append("content digest or source-atlas pin")
    checks.append("content-addressed assembly and source atlas")

    obligations = [item["id"] for axis in atlas["axes"] if axis["id"] == "REFINED_OBLIGATION" for item in axis["keys"]]
    cell_map = {(item["foundation"], item["carrier"], item["obligation"]): item for item in atlas["cells"]}
    assemblies = result.get("assemblies", [])
    certified_records = atlas.get("cross_cell_interfaces", [])
    if result.get("certified_interface_records") != certified_records or [item.get("id") for item in certified_records] != ["STATE_TO_PROBABILITY", "SELECTION_TO_DYNAMICS"]:
        errors.append("certified interface record projection")
    if len(assemblies) != 7 or len({item.get("id") for item in assemblies}) != 7:
        errors.append("seven unique prototype assemblies")
    for assembly in assemblies:
        selected = {item.get("obligation"): item for item in assembly.get("selected_cells", [])}
        if set(selected) != set(obligations):
            errors.append("obligation closure " + assembly.get("id", "?"))
            continue
        for obligation in obligations:
            candidates = [cell_map[(foundation, carrier, obligation)] for foundation in assembly["foundations"] for carrier in assembly["carriers"]]
            expected = max(candidates, key=lambda item: _selection_key(item, assembly))
            actual = selected[obligation]
            for field in ("foundation", "carrier", "status", "evidence", "evidence_roles"):
                if actual.get(field) != expected.get(field):
                    errors.append(f"independent selected cell {assembly['id']}/{obligation}/{field}")
                    break
        direct = sum(item["status"] in DIRECT for item in selected.values())
        assessed = sum(item["status"] != "NOT_MAPPED" for item in selected.values())
        if assembly.get("coverage") != {"direct": direct, "assessed": assessed, "total": 16, "complete_direct": direct == 16}:
            errors.append("coverage recomputation " + assembly["id"])
        for interface in assembly.get("interfaces", []):
            source_coordinates = [
                {"foundation": selected[item]["foundation"], "carrier": selected[item]["carrier"], "obligation": item}
                for item in interface.get("source_obligations", [])
            ]
            target_coordinates = [
                {"foundation": selected[item]["foundation"], "carrier": selected[item]["carrier"], "obligation": item}
                for item in interface.get("target_obligations", [])
            ]
            expected = next((item for item in certified_records if item.get("id") == interface.get("id") and item.get("source_coordinates") == source_coordinates and item.get("target_coordinates") == target_coordinates), None)
            if expected:
                if interface.get("relation") != expected.get("relation") or interface.get("certification_status") != "CERTIFIED" or interface.get("evidence") != expected.get("evidence"):
                    errors.append("certified interface projection " + assembly["id"] + "/" + interface.get("id", "?"))
            elif interface.get("relation") != "NOT_ASSESSED" or interface.get("certification_status") != "NOT_ASSESSED" or interface.get("evidence"):
                errors.append("fail-closed interface " + assembly["id"] + "/" + interface.get("id", "?"))
        if len(assembly.get("interfaces", [])) != 7:
            errors.append("interface closure " + assembly["id"])
        gates = {item.get("id"): item.get("status") for item in assembly.get("hard_gates", [])}
        expected_gates = {
            "OBLIGATION_COVERAGE": "SATISFIED" if direct == 16 else "OPEN",
            "CROSS_CELL_COMPOSITION": "BLOCKED",
            "PREDICTION_DERIVATION": "BLOCKED",
            "OBSERVABLE_IDENTIFICATION": "BLOCKED",
            "EMPIRICAL_COMPARISON": "NO_RECORDS",
            "ROBUSTNESS_OUT_OF_SAMPLE": "NO_RECORDS",
        }
        if gates != expected_gates or assembly.get("complete_theory") is not False or assembly.get("empirically_supported") is not False:
            errors.append("hard-gate closure " + assembly["id"])
    certified_instances = sum(interface.get("certification_status") == "CERTIFIED" for assembly in assemblies for interface in assembly.get("interfaces", []))
    if certified_instances != 4:
        errors.append("four assembly projections of two certified relations")
    checks.append("independent cell selection, certified-interface projection, coverage, and hard gates")

    ledger = result.get("empirical_ledger", {})
    if ledger.get("records") != [] or len(ledger.get("benchmarks", [])) != 6 or any(item.get("status") != "NOT_REGISTERED" for item in ledger.get("benchmarks", [])):
        errors.append("empty empirical ledger and benchmark closure")
    flags = result.get("claim_flags", {})
    for name in ("prototype_assemblies_generated", "selected_cells_content_addressed", "interface_and_coverage_states_separated", "at_least_one_cross_cell_interface_certified", "empirical_record_schema_declared"):
        if flags.get(name) is not True:
            errors.append("positive flag " + name)
    for name in ("cross_cell_composability_established", "prediction_chain_established", "empirical_agreement_assessed", "complete_observationally_valid_theory_identified"):
        if flags.get(name) is not False:
            errors.append("fail-closed flag " + name)
    checks.append("empty empirical ledger and fail-closed claim flags")

    if value is None:
        if SITE_JSON.read_bytes() != RESULT.read_bytes():
            errors.append("site/result assembly parity")
        if SITE_JS.read_bytes() != b"window.THEORY_ASSEMBLY_DATA = " + SITE_JSON.read_bytes().rstrip() + b";\n":
            errors.append("offline assembly assignment")
        combined = (ROOT / "foundations/site/index.html").read_text() + (ROOT / "foundations/site/app.js").read_text()
        for token in ("Assemblies", "assembliesView", "Assembly hard-gate chain", "Typed interface ledger", "Empirical benchmark ledger", "NOT_ASSESSED"):
            if token not in combined + SITE_JS.read_text():
                errors.append("interface token " + token)
        for token in ("seven", "coverage envelope", "NOT_ASSESSED", "empty", "does not establish"):
            if token not in REPORT.read_text():
                errors.append("report token " + token)
    checks.append("offline assembly interface, parity, and report")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
