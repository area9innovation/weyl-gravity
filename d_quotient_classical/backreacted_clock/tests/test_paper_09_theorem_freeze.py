from __future__ import annotations

import json

from d_quotient_classical.backreacted_clock import paper_09_theorem_freeze as freeze
from d_quotient_classical.backreacted_clock.verify_paper_09_theorem_freeze import main as independent_verify


def test_freeze_is_scoped_to_ten_gravity_clock_claims() -> None:
    payload = freeze.build()
    assert payload["paper_state"] == "THEOREM_FROZEN"
    assert payload["theorem_inventory"]["claim_count"] == 10
    assert payload["theorem_inventory"]["maxwell_main_theorem_included"] is False
    assert payload["theorem_inventory"]["observer_84_row_main_theorem_included"] is False


def test_authoritative_replay_and_pdfs_pass() -> None:
    payload = freeze.build()
    assert payload["verification"]["authoritative_freeze_rail"]["tests_passed"] == 47
    assert payload["verification"]["authoritative_freeze_rail"]["tests_failed"] == 0
    assert payload["verification"]["pdf_build"]["status"] == "PASS"


def test_broad_package_drift_is_disclosed_not_used() -> None:
    audit = freeze.build()["verification"]["broader_classical_package_audit"]
    assert audit["tests_passed"] == 170
    assert audit["tests_failed"] == 4
    assert audit["used_to_promote_theorem"] is False


def test_persisted_and_independent_replay() -> None:
    assert json.loads(freeze.OUTPUT.read_text()) == freeze.build()
    assert independent_verify() == 0
