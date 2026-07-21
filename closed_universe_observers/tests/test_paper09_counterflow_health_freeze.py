from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "paper09_claim_verifier", ROOT / "paper/verify_09_relational_clocks_claim_map.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
DOC = json.loads((ROOT / "paper/09-relational-clocks-berger-d-cartan-claim-map.json").read_text())


def test_authoritative_map_passes() -> None:
    coverage = MODULE.verify_document(copy.deepcopy(DOC), ROOT)
    assert coverage["status"] == "NONVACUOUS_PASS"
    assert coverage["claims_total"] == 22
    assert DOC["final_disposition"]["status"] == "DRAFT_ALLOWED"
    assert DOC["final_disposition"]["theorem_frozen"] is False


def test_rejects_stale_healthy_carrier() -> None:
    mutated = copy.deepcopy(DOC)
    mutated["health_disposition"]["all_certified_physical_blocks"] = "HEALTHY"
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_document(mutated, ROOT)


def test_rejects_coordinate_ratio_as_redshift() -> None:
    mutated = copy.deepcopy(DOC)
    next(row for row in mutated["claims"] if row["claim_id"] == "P09-O5")["statement"] = "The coordinate ratio is an operational redshift."
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_document(mutated, ROOT)


def test_rejects_K_equals_D() -> None:
    mutated = copy.deepcopy(DOC)
    mutated["generator_semantics"]["K_equals_D"] = True
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_document(mutated, ROOT)


def test_rejects_tier3_obstruction_as_green() -> None:
    mutated = copy.deepcopy(DOC)
    mutated["draft_allowed_gates"][1]["status"] = "GREEN"
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_document(mutated, ROOT)


def test_rejects_source_binding_cycle_as_pass() -> None:
    mutated = copy.deepcopy(DOC)
    mutated["source_binding_fixed_point"]["cycle_present"] = False
    mutated["source_binding_fixed_point"]["legacy_table_imports_regenerated_publication_map"] = True
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_document(mutated, ROOT)


def test_rejects_draft_allowed_as_theorem_frozen() -> None:
    mutated = copy.deepcopy(DOC)
    mutated["freeze_decision"] = "THEOREM_FROZEN"
    mutated["final_disposition"]["theorem_frozen"] = True
    with pytest.raises(MODULE.VerificationError):
        MODULE.verify_document(mutated, ROOT)
