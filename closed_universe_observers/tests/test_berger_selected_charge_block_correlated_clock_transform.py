import copy
from fractions import Fraction
import json

import pytest
from jsonschema import ValidationError

from closed_universe_observers.generate_berger_selected_charge_block_correlated_clock_transform import CERTIFICATE
from closed_universe_observers.verify_berger_selected_charge_block_correlated_clock_transform import verify


def test_all_exact_eigenvalue_transforms_are_exported() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert len(value["spectral_transform_audits"]) == 9
    assert value["coverage"]["exact_eigenvalue_transform_count"] == 27
    assert all(len(row["eigenmodes"]) == 3 for row in value["spectral_transform_audits"])


def test_all_selected_outputs_are_narrow() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert len(value["selected_block_outputs"]) == 18
    assert Fraction(value["coverage"]["maximum_selected_spatial_output_axis_width"]) < Fraction(1, 50)
    assert Fraction(value["coverage"]["maximum_selected_temporal_output_axis_width"]) < Fraction(6, 5)


def test_direct_transform_overlaps_the_lower_band() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["lower_band_overlap"]["zero_frequency_contained_in_p0_enclosure"] is True
    assert value["lower_band_overlap"]["two_j138_direct_transform_contained_in_order14_interval"] is True


def test_coarse_clock_quadrature_is_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["mutation_results"][0]["detected"] is True
    assert Fraction(value["mutation_results"][0]["mutated_maximum_transform_width"]) > Fraction(1, 50)


def test_false_tail_promotion_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["flags"]["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED"] = True
    with pytest.raises((AssertionError, ValidationError)):
        verify(value)


def test_response_and_quantum_claims_remain_false() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False
