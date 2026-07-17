#!/usr/bin/env python3
"""Verify claim typing, imports, lifecycle, and fail-closed comparison gates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "closed_universe_observers/ledgers/comparison_ledger.json"
SCHEMA = ROOT / "closed_universe_observers/schema/comparison-ledger-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ledger = json.loads(LEDGER.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(ledger)

    expected_sources = {"1908.10996v2", "2402.00098v3", "2403.13047v2", "2412.14014v3", "2501.02359v2"}
    if {item["arxiv_id"] for item in ledger["source_versions"]} != expected_sources:
        raise AssertionError("the five-source literature ledger is incomplete")
    if sum(step["interpretive_inference"] for source in ledger["source_versions"] for step in source["logical_chain"]) < 1:
        raise AssertionError("interpretive inferences are not marked")
    for imported in ledger["internal_imports"]:
        path = ROOT / imported["path"]
        if _sha256(path) != imported["sha256"]:
            raise AssertionError(f"import drift: {imported['path']}")
        data = json.loads(path.read_text())
        if data["result_id"] != imported["result_id"]:
            raise AssertionError(f"import result mismatch: {imported['path']}")

    dictionary_names = {row["object"] for row in ledger["object_dictionary"]}
    mandatory = {
        "Fundamental Hilbert space", "BRST/BV state cohomology", "One-particle complex",
        "Residual degree-four cohomology", "Covariant phase space", "Observable algebra",
        "Observer-effective Hilbert space",
    }
    if dictionary_names != mandatory:
        raise AssertionError("mandatory object dictionary drifted")
    claim_index = ledger["classical_observer_map"]["claim_index"]
    if set(claim_index) != {"theory", "background", "state_object", "quotient", "observer", "boundaries", "lifecycle"}:
        raise AssertionError("seven-field claim index is incomplete")
    component_status = {item["requirement"]: item["status"] for item in ledger["classical_observer_map"]["components"]}
    if component_status["two_distinguishable_clock_labelled_records"] != "OPEN":
        raise AssertionError("record gate was silently promoted")
    if ledger["classical_observer_map"]["map_certified"] is not False:
        raise AssertionError("partial observer map was promoted")
    matrix = {row["setting"]: row for row in ledger["comparison_matrix"]}
    if matrix["full quantum Berger theory"]["verdict"] != "QUANTUM_COMPARISON_NOT_YET_DEFINED":
        raise AssertionError("quantum comparison gate was promoted")
    status = ledger["common_fixture_status"]
    if status["common_category_found"] or status["classical_observer_map_passed"] or status["quantum_comparison_legal"]:
        raise AssertionError("common-fixture lifecycle is not fail closed")
    if ledger["current_lifecycle"] != "EXTERNAL_FIXTURE_REPRODUCED":
        raise AssertionError("lifecycle is inconsistent with the open classical map")
    print("CLOSED_UNIVERSE_OBSERVER_FIRST_COMPARISON ledger verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
