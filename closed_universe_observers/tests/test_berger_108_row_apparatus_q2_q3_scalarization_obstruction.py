from fractions import Fraction

from closed_universe_observers.generate_berger_108_row_apparatus_q2_q3_scalarization_obstruction import (
    build,
    coordinate_jet_nonuniqueness,
)


def test_coordinate_jet_witness_separates_q2_and_q3_but_not_q1():
    witness = coordinate_jet_nonuniqueness()
    replay = witness["exact_replay"]
    assert replay["unary_difference_count"] == 0
    assert replay["q2_difference_nonzero"] is True
    assert replay["q3_difference_nonzero"] is True


def test_zero_coordinate_jets_remove_the_witnesses():
    assert coordinate_jet_nonuniqueness(f2=Fraction(0))["exact_replay"]["q2_difference_nonzero"] is False
    assert coordinate_jet_nonuniqueness(f3=Fraction(0))["exact_replay"]["q3_difference_nonzero"] is False


def test_scalarization_gate_fails_closed():
    value = build()
    assert value["atlas_status"] == "NO_CERTIFIED_MAP"
    assert value["flags"]["NONLINEAR_CLOCK_COORDINATE_JET_NONUNIQUENESS_CERTIFIED"] is True
    assert value["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED"] is False
    assert value["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False
    assert value["activation_disposition"]["physical_branch_bridge_activated"] is False
