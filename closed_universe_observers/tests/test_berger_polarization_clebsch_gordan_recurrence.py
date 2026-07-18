import json

from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import (
    CERTIFICATE,
    axial_scalar_recurrence,
    build,
    product_identity_defects,
)


def test_generated_certificate_is_current():
    assert json.loads(CERTIFICATE.read_text()) == build()


def test_exact_product_identity_and_lower_channel_mutation():
    assert product_identity_defects() == 0
    assert product_identity_defects(2, drop_lower_channel=True) > 0


def test_exact_low_mode_sparsity_formulas():
    for two_j in range(8):
        dimension = two_j + 1
        recurrences = [
            axial_scalar_recurrence(two_j, row, column, coordinate)
            for coordinate in ("y0", "y1", "y2", "y3")
            for row in range(dimension)
            for column in range(dimension)
        ]
        supported = [terms for terms in recurrences if terms]
        assert len(supported) == 6 * dimension - 4
        assert sum(map(len, supported)) == 16 * dimension - 12
        assert max(map(len, supported)) <= 4


def test_capacity_rail_counts_are_exact_closed_form_sums():
    scale = build()["scale_audit_through_two_j138"]
    assert scale["coordinate_entry_count"] == 57824
    assert scale["scalar_recurrence_term_count"] == 154012
    assert scale["maximum_scalar_terms_per_coordinate_entry"] == 4


def test_clock_green_tail_and_branch_bridge_remain_open():
    flags = build()["flags"]
    assert flags["ALL_FINITE_TWO_J_POINTWISE_POLARIZATION_RECURRENCE_EXPORTED"] is True
    assert flags["CLOCK_AND_TEMPORAL_GREEN_INTEGRATION_COMPLETED"] is False
    assert flags["GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED"] is False
    assert flags["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
    assert flags["BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED"] is False
