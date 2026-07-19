import json

from spectral.euclidean import (
    generic_background_physical_plus_ghost_n3_third_curvature_form_factors as producer,
)
from spectral.euclidean import (
    verify_generic_background_physical_plus_ghost_n3_third_curvature_form_factors as consumer,
)


def _certificate():
    value = json.loads(producer.OUTPUT.read_text())
    producer.validate(value)
    return value


def test_partial_bv_gate_is_fail_closed():
    value = _certificate()
    flags = value["claim_flags"]
    assert flags["PHYSICAL_PLUS_GHOST_N3_FIVE_CARRIER_FUNCTIONS_ASSEMBLED"]
    assert flags["PHYSICAL_PLUS_GHOST_N3_MELLIN_MS_REPRESENTATIVE_COMPUTED"]
    assert not flags["GHOST_N1_INSERTION_TRACE_COMPUTED"]
    assert not flags["GHOST_N2_INSERTION_TRACE_COMPUTED"]
    assert not flags["GENERIC_FINITE_SCHUR_ROWS_COMPUTED"]
    assert not flags["FULL_BV_FORM_FACTORS_COMPUTED"]


def test_channel_and_quotient_ledger():
    value = _certificate()
    assert len(value["channel_rows"]) == 11
    assert value["quotient_ledger"]["quotient_dimension"] == 10
    assert value["quotient_ledger"]["relation_status"] == "ZERO_COEFFICIENTWISE"
    assert all(
        status == "ZERO"
        for status in value["I28_relation"]["coordinate_status"].values()
    )


def test_exact_holdouts_are_present_for_every_channel():
    value = _certificate()
    assert all(
        [row["exact_holdouts"][0]["point"], row["exact_holdouts"][1]["point"]]
        == [[2, 3, 5], [3, 5, 7]]
        for row in value["channel_rows"]
    )


def test_independent_consumer():
    assert consumer.main() == 0
