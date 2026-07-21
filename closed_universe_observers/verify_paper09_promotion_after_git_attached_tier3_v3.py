#!/usr/bin/env python3
"""Verify the fail-closed Paper 9 v3 no-promotion disposition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "closed_universe_observers/receipts/PAPER09_PROMOTION_AFTER_GIT_ATTACHED_TIER3_V3_NO_PROMOTION.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_ref(value: dict, name: str) -> dict:
    ref = value["input_refs"][name]
    path = ROOT / ref["path"]
    assert digest(path) == ref["sha256"]
    return json.loads(path.read_text())


def verify_value(value: dict) -> dict:
    assert value["schema"] == "paper09-promotion-after-git-attached-tier3-v3-no-promotion-v1"
    assert value["result_id"] == "PAPER09_PROMOTION_AFTER_GIT_ATTACHED_TIER3_V3_NO_PROMOTION"
    assert value["science_forge_work_item"].endswith("observer-paper09-promotion-after-git-attached-tier3-v3")
    for path, expected in value["preserved_publication_artifacts"].items():
        assert digest(ROOT / path) == expected

    prior = load_ref(value, "paper09_v2_disposition")
    prior_tier = load_ref(value, "paper09_v2_tier_receipt")
    manifest = load_ref(value, "git_attached_tier3_manifest")
    tier3 = load_ref(value, "git_attached_tier3_obstruction")
    tier3_tier = load_ref(value, "git_attached_tier3_tier_receipt")
    legacy = load_ref(value, "legacy_receiver_census")
    ratio = load_ref(value, "legacy_frequency_ratio_nonactivation")
    health = load_ref(value, "repaired_q70_health_nonactivation")

    assert prior["decision"] == prior_tier["decision"] == "DRAFT_ALLOWED"
    assert prior["theorem_frozen"] is False
    assert prior["flags"]["OBSERVER_TIER3_GREEN"] is False
    assert prior["historical_base"]["dispositions_unchanged"] is True
    assert manifest["flags"]["GIT_ATTACHED"] is True
    assert manifest["flags"]["EXACT_BLOBS"] is True
    assert tier3_tier["decision"] == "OBSTRUCTED"
    assert tier3["authoritative_run"]["run_count"] == 1
    assert tier3["authoritative_run"]["passed_before_first_failure"] == 826
    assert tier3["authoritative_run"]["status"] == "STOPPED_AT_FIRST_FAILURE"
    assert tier3["first_failure"]["classification"] == "STALE_COMPARISON_LEDGER_BRIDGE_ARTIFACT_PIN_WITH_CLAIM_BOUNDARY_DRIFT"
    assert tier3["flags"]["AUTHORITATIVE_RUN_GREEN"] is False
    assert tier3["flags"]["SCIENTIFIC_CONTRADICTION"] is False

    census = legacy["census_completeness"]
    assert census == {
        "classified_count": 7,
        "complete": True,
        "discovered_count": 7,
        "expected_count": 7,
        "unclassified_result_ids": [],
    }
    assert all(row["admissibility_status"] == "NO_CERTIFIED_MAP" for row in legacy["legacy_receiver_census"])
    assert ratio["flags"]["OPERATIONAL_FREQUENCY_RATIO_DEFINED"] is False
    assert ratio["flags"]["COORDINATE_RATIO_PROMOTED_AS_REDSHIFT"] is False
    assert health["claim_status"] == "NOT_ACTIVATED_NO_COMMON_HEALTHY_PHYSICAL_CLOCK_RECEIVER_CARRIER"
    assert health["atlas_status"] == "NO_CERTIFIED_MAP"
    assert health["frequency_ratio_result"]["value"] == "UNDEFINED"
    assert health["frequency_ratio_result"]["redshift"] == "NO_CERTIFIED_MAP"
    assert health["thirteen_field_interface"]["physical_receiver_quotient"]["status"] == "NO_CERTIFIED_MAP"
    assert "all physically unstable" in health["thirteen_field_interface"]["physical_receiver_quotient"]["reason"]

    gate = value["promotion_gate"]
    assert gate["gate"] == "OBSERVER_STREAM_TIER3_GREEN"
    assert gate["required"] is True and gate["certified"] is False
    assert gate["git_attached_materialization"] == "PASS"
    assert gate["authoritative_run_count"] == 1
    assert gate["passed_before_first_failure"] == 826
    assert gate["first_failure"] == tier3["first_failure"]["classification"]
    assert "obsolete hash" in gate["remaining_evidence_boundary"]
    assert "obsolete claim boundary" in gate["remaining_evidence_boundary"]
    assert gate["decision"] == "NO_PROMOTION"

    preserved = value["preserved_scientific_disposition"]
    assert preserved["claim_count"] == 22
    assert preserved["paper09_status"] == "DRAFT_ALLOWED"
    assert preserved["theorem_frozen"] is False
    assert preserved["seven_row_receiver_census_complete"] is True
    assert preserved["seven_row_receiver_census_count"] == 7
    assert preserved["both_legacy_rows_no_certified_map"] is True
    assert preserved["operational_frequency_ratio_defined"] is False
    assert preserved["coordinate_ratio_promoted_as_redshift"] is False
    assert preserved["repaired_q70_physical_blocks"] == "ALL_CERTIFIED_BLOCKS_UNSTABLE"
    assert preserved["higher_repaired_q70_isotypes"] == "NO_CERTIFIED_MAP"
    assert preserved["common_healthy_physical_clock_receiver_carrier"] == "NO_CERTIFIED_MAP"
    assert preserved["observer_science_reopened"] is False

    flags = value["flags"]
    assert flags == {
        "OBSERVER_STREAM_TIER3_GREEN": False,
        "PAPER_MAP_REGENERATED": False,
        "PAPER_PDFS_REBUILT": False,
        "PAPER09_PROMOTED": False,
        "PAPER09_THEOREM_FROZEN": False,
        "SCIENTIFIC_CLAIMS_CHANGED": False,
        "OPERATIONAL_OBSERVABLE_PROMOTED": False,
        "COORDINATE_RATIO_PROMOTED_AS_REDSHIFT": False,
    }
    assert value["next_typed_gate"] == "SEMANTIC_COMPARISON_LEDGER_BRIDGE_ARTIFACT_RELOCK_AND_FRESH_TIER3_RERUN"
    return value


def verify() -> dict:
    return verify_value(json.loads(RECEIPT.read_text()))


if __name__ == "__main__":
    verify()
    print("PAPER09_PROMOTION_AFTER_GIT_ATTACHED_TIER3_V3_NO_PROMOTION verification: PASS")
