from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "paper09_final_v2_verifier",
    ROOT / "closed_universe_observers/verify_paper09_final_freeze_after_historical_base_tier3_v2.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
DOC = json.loads((ROOT / "paper/09-relational-clocks-berger-d-cartan-claim-map.json").read_text())


def test_final_disposition_passes_fail_closed() -> None:
    receipt = MODULE.verify_final_disposition(copy.deepcopy(DOC), ROOT)
    assert receipt["decision"] == "DRAFT_ALLOWED"
    assert receipt["theorem_frozen"] is False
    assert receipt["flags"]["SOURCE_BINDING_FIXED_POINT"] is False
    assert receipt["flags"]["OBSERVER_TIER3_GREEN"] is False


def test_rejects_theorem_freeze_promotion() -> None:
    mutated = copy.deepcopy(DOC)
    mutated["freeze_decision"] = "THEOREM_FROZEN"
    mutated["final_disposition"]["status"] = "THEOREM_FROZEN"
    mutated["final_disposition"]["theorem_frozen"] = True
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_final_disposition(mutated, ROOT)


def test_rejects_tier3_green_promotion() -> None:
    mutated = copy.deepcopy(DOC)
    mutated["draft_allowed_gates"][1]["status"] = "GREEN"
    mutated["final_disposition"]["post_repair_observer_tier3"] = "GREEN"
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_final_disposition(mutated, ROOT)


def test_rejects_source_binding_fixed_point_promotion() -> None:
    mutated = copy.deepcopy(DOC)
    mutated["source_binding_fixed_point"]["cycle_present"] = False
    mutated["source_binding_fixed_point"]["classification"] = "PASS"
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_final_disposition(mutated, ROOT)


def test_rejects_missing_historical_base_import() -> None:
    mutated = copy.deepcopy(DOC)
    mutated["exact_hash_imports"] = [
        row for row in mutated["exact_hash_imports"]
        if row["path"] != "closed_universe_observers/receipts/OBSERVER_LEGACY_RECEIVER_HISTORICAL_BASE_BINDING_REPAIR_V1_MANIFEST.json"
    ]
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_final_disposition(mutated, ROOT)


def test_rejects_current_legacy_table_hash_drift() -> None:
    mutated = copy.deepcopy(DOC)
    row = next(
        row for row in mutated["exact_hash_imports"]
        if row["path"] == "d_quotient_classical/certificates/PAPER_09_BERGER_CLAIM_TABLE.json"
    )
    row["sha256"] = "0" * 64
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_final_disposition(mutated, ROOT)
