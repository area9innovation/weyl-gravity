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
CONTROL = ROOT / "foundations/standard-gr-observational-control-v1.json"
CONTROL_SCHEMA = ROOT / "foundations/schema/standard-gr-observational-control-v1.schema.json"
MODEL_ASSEMBLY = ROOT / "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json"
REPORT = ROOT / "foundations/reports/theory-assembly-atlas-v1.md"
SITE_JSON = ROOT / "foundations/site/assemblies.json"
SITE_JS = ROOT / "foundations/site/assemblies.js"
DIRECT = {"LOCAL_RESULT", "LITERATURE_RESULT"}
RANK = {"NOT_MAPPED": 0, "REVIEWED_GAP": 1, "PRIORITY_GAP": 1, "PIECES_ONLY": 2, "LITERATURE_RESULT": 3, "LOCAL_RESULT": 3}


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
    control = load(CONTROL)
    errors.extend("control schema " + item.message for item in Draft202012Validator(load(CONTROL_SCHEMA), format_checker=FormatChecker()).iter_errors(control))
    if result.get("calibration_controls") != [control] or result.get("calibration_source") != {
        "path": "foundations/standard-gr-observational-control-v1.json",
        "sha256": hashlib.sha256(CONTROL.read_bytes()).hexdigest(),
    }:
        errors.append("external calibration projection and source pin")
    record_ids = {item.get("id") for item in control.get("records", [])}
    coverage_ids = {record_id for item in control.get("benchmark_coverage", []) for record_id in item.get("record_ids", [])}
    if len(record_ids) != 4 or record_ids != coverage_ids:
        errors.append("external calibration record closure")
    if sum(item.get("status") == "SUPPORTED_CONTROL" for item in control.get("benchmark_coverage", [])) != 3:
        errors.append("three-domain calibration coverage")
    if any(item.get("artifact", {}).get("status") == "CONTENT_PINNED" and not item.get("artifact", {}).get("sha256") for item in control.get("records", [])):
        errors.append("external calibration content pin")
    checks.append("external positive-control schema, records, and content pins")
    model_assembly = load(MODEL_ASSEMBLY)
    if result.get("model_scoped_assemblies") != [model_assembly] or result.get("model_scoped_sources") != [{
        "path": "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json",
        "sha256": hashlib.sha256(MODEL_ASSEMBLY.read_bytes()).hexdigest(),
    }]:
        errors.append("model-scoped assembly projection and source pin")
    if model_assembly.get("assembly_disposition") != {
        "status": "BOUNDED_PREDICTION_ASSEMBLY_COMPLETE",
        "complete_within_declared_scope": True,
        "empirically_supported_within_declared_scope": True,
        "complete_theory": False,
    }:
        errors.append("model-scoped bounded disposition")
    checks.append("model-scoped end-to-end assembly projection")
    if digest(result) != result.get("canonical_digest") or result.get("source_atlas_digest") != atlas.get("canonical_digest"):
        errors.append("content digest or source-atlas pin")
    checks.append("content-addressed assembly and source atlas")

    obligations = [item["id"] for axis in atlas["axes"] if axis["id"] == "REFINED_OBLIGATION" for item in axis["keys"]]
    cell_map = {(item["foundation"], item["carrier"], item["obligation"]): item for item in atlas["cells"]}
    assemblies = result.get("assemblies", [])
    certified_records = atlas.get("cross_cell_interfaces", [])
    if result.get("certified_interface_records") != certified_records or [item.get("id") for item in certified_records] != ["STATE_TO_PROBABILITY", "SELECTION_TO_DYNAMICS"]:
        errors.append("certified interface record projection")
    carrier_records = atlas.get("carrier_interfaces", [])
    if result.get("certified_carrier_interface_records") != carrier_records or [item.get("id") for item in carrier_records] != ["EUCLIDEAN_TO_KREIN_CARRIER"]:
        errors.append("certified carrier interface record projection")
    numerical_records = atlas.get("numerical_reproducibility_records", [])
    if result.get("numerical_reproducibility_ledger", {}).get("records") != numerical_records or len(numerical_records) != 1:
        errors.append("numerical reproduction record projection")
    expected_ids = {
        "STANDARD_MIXED_REFERENCE", "STANDARD_ALGEBRAIC_PROFILE",
        "FINITE_EXACT_PROGRAMME", "BT_EUCLIDEAN_LATTICE_PROGRAMME",
        "WEAK_BASE_FINITE_EXACT", "KREIN_ALGEBRAIC_PROGRAMME",
        "PURE_WEYL_BV_BFV_PROGRAMME", "CONSTRUCTIVE_PROGRAMME",
        "TOPOS_INTERNAL_PROGRAMME",
    }
    if len(assemblies) != 9 or {item.get("id") for item in assemblies} != expected_ids:
        errors.append("nine named research-camp prototype assemblies")
    for assembly in assemblies:
        for field in ("short_label", "camp_kind", "camp_summary", "central_question", "atlas_window", "scope_note"):
            if not assembly.get(field):
                errors.append("camp metadata " + assembly.get("id", "?") + "/" + field)
        if len(assembly.get("lineage", [])) != 3 or len(assembly.get("signature_ideas", [])) != 3:
            errors.append("camp lineage/signature closure " + assembly.get("id", "?"))
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
        gates = {item.get("id"): item.get("status") for item in assembly.get("maturity_rails", [])}
        certified_count = sum(item.get("certification_status") == "CERTIFIED" for item in assembly.get("interfaces", []))
        expected_gates = {
            "OBLIGATION_COVERAGE": "SATISFIED" if direct == 16 else "OPEN",
            "CROSS_CELL_COMPOSITION": "PARTIALLY_CERTIFIED" if certified_count else "NOT_ASSESSED",
            "PREDICTION_DERIVATION": "NOT_EVALUABLE",
            "OBSERVABLE_IDENTIFICATION": "NOT_REGISTERED",
            "NUMERICAL_REPRODUCIBILITY": "COARSE_REPRODUCTION_ONLY" if assembly["id"] == "BT_EUCLIDEAN_LATTICE_PROGRAMME" else "NO_RECORDS",
            "EMPIRICAL_COMPARISON": "NO_RECORDS",
            "ROBUSTNESS_OUT_OF_SAMPLE": "NO_RECORDS",
        }
        if gates != expected_gates or assembly.get("complete_theory") is not False or assembly.get("empirically_supported") is not False:
            errors.append("maturity-rail closure " + assembly["id"])
    certified_instances = sum(interface.get("certification_status") == "CERTIFIED" for assembly in assemblies for interface in assembly.get("interfaces", []))
    if certified_instances != 5:
        errors.append("five assembly projections of two certified relations")
    checks.append("independent cell selection, certified-interface projection, coverage, and maturity rails")

    ledger = result.get("empirical_ledger", {})
    if ledger.get("records") != [] or len(ledger.get("benchmarks", [])) != 6 or any(item.get("status") != "NOT_REGISTERED" for item in ledger.get("benchmarks", [])):
        errors.append("empty empirical ledger and benchmark closure")
    flags = result.get("claim_flags", {})
    for name in ("prototype_assemblies_generated", "research_camp_lenses_declared", "selected_cells_content_addressed", "interface_and_coverage_states_separated", "at_least_one_cross_cell_interface_certified", "scoped_carrier_interface_registered", "numerical_reproducibility_rail_declared", "empirical_record_schema_declared", "external_positive_control_registered", "missing_and_failed_states_separated", "model_scoped_prediction_assembly_registered", "bounded_prediction_chain_established", "bounded_empirical_agreement_assessed"):
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
        for token in ("Assemblies", "assembliesView", "Bounded assembly complete", "Field equations to Cassini", "Meet the research programmes", "Bateman–Turok", "Mannheim conformal gravity", "Pure-Weyl BV–BFV", "Seven independent maturity rails", "Numerical reproduction is not empirical validation", "Euclidean/Krein carrier boundary", "External positive control", "Typed interface ledger", "Empirical benchmark ledger", "NOT_ASSESSED"):
            if token not in combined + SITE_JS.read_text():
                errors.append("interface token " + token)
        for token in ("nine", "research-programme lenses", "Bateman–Turok", "Mannheim", "Pure-Weyl", "coverage envelope", "model-scoped", "Cassini", "COARSE_REPRODUCTION_ONLY", "Euclidean", "NOT_ASSESSED", "positive control", "does not establish"):
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
