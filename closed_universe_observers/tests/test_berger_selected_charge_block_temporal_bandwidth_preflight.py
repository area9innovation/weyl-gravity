import copy
from fractions import Fraction
import json

import pytest
from jsonschema import ValidationError

from closed_universe_observers.generate_berger_selected_charge_block_temporal_bandwidth_preflight import CERTIFICATE
from closed_universe_observers.verify_berger_selected_charge_block_temporal_bandwidth_preflight import verify


def test_all_selected_blocks_and_charges_are_audited() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert len(value["charge_audits"]) == 9
    assert len(value["actual_completed_input_order14_interval_audits"]) == 18


def test_order14_has_an_exact_error_witness_on_every_charge() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert all(Fraction(row["order14_exact_cosine_error_absolute_lower"]) > 0 for row in value["charge_audits"])


def test_current_independent_interval_outputs_are_all_too_wide() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert all(
        Fraction(row["maximum_order14_independent_interval_width"]) > Fraction(1, 10)
        for row in value["actual_completed_input_order14_interval_audits"]
    )


def test_current_geometric_proof_needs_p78() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["coverage"]["maximum_required_geometric_order_for_1e_minus_17"] == 39
    assert value["coverage"]["maximum_required_even_clock_power"] == 78


def test_false_temporal_promotion_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["flags"]["TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED"] = True
    with pytest.raises((AssertionError, ValidationError)):
        verify(value)


def test_response_tail_and_quantum_claims_remain_false() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["flags"]["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False
