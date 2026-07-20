import json

from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    CERTIFICATE,
    PAYLOAD,
)


def result():
    return json.loads(CERTIFICATE.read_text())


def payload():
    return json.loads(PAYLOAD.read_text())


def test_complete_bounded_invariant_dimensions():
    value = result()
    rows = value["invariant_module_classification"]
    assert [row["raw_dimension"] for row in rows] == [24, 96, 240]
    assert [row["invariant_dimension"] for row in rows] == [8, 28, 56]
    assert all(
        sum(row["reflection_dimensions"].values()) == row["invariant_dimension"]
        for row in rows
    )
    assert len(payload()["modules"]) == 224


def test_representation_carrier_is_closed_without_projection():
    carrier = result()["representation_closed_carrier"]
    assert carrier["old_closure_dimension"] == 900
    assert carrier["new_closure_dimension"] >= 900
    assert carrier["closure_check"] == "CERTIFIED_EXACT"


def test_order_two_family_remains_obstructed():
    value = result()
    image = value["exact_action_image"]
    assert image["complete_lower_family_rank"] == 118
    assert image["lower_family_plus_source_rank"] == 119
    assert image["order_two_enlarged_rank"] == 230
    assert image["order_two_enlarged_plus_source_rank"] == 231
    assert not image["typed_source_in_image"]
    decisive = value["decisive_quotient_projection"]
    assert decisive["source_support_coordinate_count"] == 64
    assert value["minimality"]["first_not_excluded_derivative_order"] == 3
    assert not any(value["activation_disposition"].values())
