#!/usr/bin/env python3
"""Verify that three observer dispositions survive the superseded input."""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RECEIPT = (
    ROOT
    / "closed_universe_observers/receipts/"
    "OBSERVER_SUPERSEDED_INPUT_REVALIDATION_2026_07_27_V1.json"
)

GENERATORS = {
    "POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1":
        "closed_universe_observers.generate_positive_berger_receiver_physical_descent_frequency_ratio_nonactivation",
    "PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1":
        "closed_universe_observers.generate_phase1_relational_observable_disposition_synthesis",
    "COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1":
        "closed_universe_observers.generate_counterflow_charged_time_physical_instantiation_after_repaired_q70_health_nonactivation",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scientific_projection(value: Any) -> Any:
    if isinstance(value, list):
        return [_scientific_projection(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _scientific_projection(item)
            for key, item in value.items()
            if key not in {"dependency_refs", "payload_ref", "provenance"}
            and not key.lower().endswith("sha256")
        }
    return value


def verify() -> dict:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["result_id"] == "OBSERVER_SUPERSEDED_INPUT_REVALIDATION_2026_07_27_V1"

    current = receipt["current_receiver_admissibility"]
    assert _sha256(ROOT / current["path"]) == current["sha256"]

    for row in receipt["historical_only_results"]:
        path = ROOT / row["path"]
        value = json.loads(path.read_text(encoding="utf-8"))
        assert value["result_id"] == row["result_id"]
        assert _sha256(path) == row["sha256"]
        assert row["disposition"] == "PRESERVED_HISTORICAL_BASE_REPLAY"

    for row in receipt["revalidated_results"]:
        path = ROOT / row["path"]
        old = json.loads(path.read_text(encoding="utf-8"))
        assert old["result_id"] == row["result_id"]
        assert _sha256(path) == row["sha256"]
        module = importlib.import_module(GENERATORS[row["result_id"]])
        rebuilt = module.build_certificate(module.build_payload())
        assert _scientific_projection(old) == _scientific_projection(rebuilt)
        assert row["current_input_rebuild"] == "SCIENTIFIC_PROJECTION_IDENTICAL"
        assert row["disposition"] == "RESULT_SURVIVES_CURRENT_INPUT_WITH_NEW_PROVENANCE"

    assert receipt["paper09_disposition"]["status"] == "DRAFT_ALLOWED"
    assert receipt["paper09_disposition"]["claim_map_current"] is False
    return receipt


if __name__ == "__main__":
    verify()
    print(
        "OBSERVER_SUPERSEDED_INPUT_REVALIDATION_2026_07_27_V1: PASS "
        "(3 results survive; 2 historical replays preserved)"
    )
