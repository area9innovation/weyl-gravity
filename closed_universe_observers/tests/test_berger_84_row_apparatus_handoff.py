from __future__ import annotations

import json

from closed_universe_observers import generate_berger_84_row_apparatus_handoff as result
from closed_universe_observers import verify_berger_84_row_apparatus_handoff as verifier


def _data() -> dict:
    return json.loads(result.INPUT.read_text())


def test_authoritative_carrier_and_pairing_are_frozen() -> None:
    payload = result.build()
    assert payload["carrier"]["total_rows"] == 84
    assert payload["carrier"]["degree_ranks_minus1_0_1_2"] == [6, 36, 36, 6]
    assert [row["row_id"] for row in payload["carrier"]["component_rows"][64:74]] == result.NEW_FIELDS
    assert [row["row_id"] for row in payload["carrier"]["component_rows"][74:84]] == result.NEW_PLUS
    assert len(payload["carrier"]["new_pairing_entries"]) == 20


def test_memory_profile_and_source_categories_are_unambiguous() -> None:
    payload = result.build()
    assert payload["bulk_memory_contract"]["category"] == "BULK_CLOCK_TRANSPORTED_SCALARS"
    assert payload["bulk_memory_contract"]["worldline_or_defect_interpretation_excluded"] is True
    assert payload["profile_operator_contract"]["taylor_scope"] == "EXACT_TWO_JET_THROUGH_Q3_WITH_HIGHER_REMAINDER_OPEN"
    assert payload["source_boundary"]["role"] == "EXTERNAL_Q_CLOSED_CONSERVED_SOURCE"
    assert payload["source_boundary"]["emitter_recoil_included"] is False


def test_physical_phi2_is_synthesized_but_construction_remains_open() -> None:
    payload = result.build()
    assert payload["physical_backreaction_synthesis"]["actual_combined_source_primitive_certified"] is True
    assert payload["physical_backreaction_synthesis"]["zero_frequency_residual_nonzero_count"] == 0
    assert payload["physical_backreaction_synthesis"]["positive_frequency_residual_nonzero_count"] == 0
    assert payload["flags"]["84_ROW_Q1_CERTIFIED"] is False
    assert payload["flags"]["DEFORMED_RANK_TWO_RESPONSE_CERTIFIED"] is False


def test_every_declared_mutation_fails_its_gate() -> None:
    data = _data()
    for mutation in data["mutations"]:
        observed = result.evaluate(result._patched(data, mutation["patch"]))
        assert observed[mutation["expected_failed_requirement"]] is False


def test_persisted_certificate_and_independent_replay() -> None:
    assert json.loads(result.CERTIFICATE.read_text()) == result.build()
    assert verifier.main() == 0
