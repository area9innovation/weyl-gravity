import copy
from fractions import Fraction
import json

import pytest
from jsonschema import ValidationError

from closed_universe_observers.generate_berger_haar_profile_normalization_repair import CERTIFICATE
from closed_universe_observers.verify_berger_haar_profile_normalization_repair import verify


def test_coordinate_and_gram_jacobians_are_distinguished() -> None:
    value = json.loads(CERTIFICATE.read_text())
    audit = value["jacobian_audit"]
    assert audit["coordinate_jacobian_dR_over_dy"] == "6*sqrt(10)*a**3/5"
    assert audit["normalized_gram_jacobian_J"] == "a**3*x0"
    assert audit["change_of_variables_identity"] == "J_a dSigma=d^3R"
    assert audit["clock_center_values"]["J"] == "1"


def test_corrected_two_j4_obstruction_survives() -> None:
    value = json.loads(CERTIFICATE.read_text())
    audit = value["corrected_tail_audit"]
    assert Fraction(audit["total_fourier_energy_lower"]) > 70_000_000
    assert audit["retained_fourier_energy_upper"] == "675"
    assert Fraction(audit["omitted_energy_fraction_lower"]) > Fraction(99999, 100000)


def test_capacity_label_is_corrected_without_demoting_working_rail() -> None:
    value = json.loads(CERTIFICATE.read_text())
    capacity = value["corrected_necessary_capacity"]
    assert capacity["certified_necessary_max_dimension"] == 98
    assert capacity["certified_necessary_two_j_max"] == 97
    assert capacity["published_working_rail_max_two_j"] == 138
    assert value["flags"]["HISTORICAL_TWO_J138_WORKING_RAIL_REMAINS_VALID"] is True
    assert value["flags"]["HISTORICAL_TWO_J138_NECESSITY_LABEL_SUPERSEDED"] is True


def test_legacy_numeric_claims_are_fail_closed() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert len(value["superseded_claims"]) == 2
    assert all(row["status"] == "NO_CERTIFIED_MAP" for row in value["superseded_claims"])
    assert all(row["detected"] is True for row in value["mutation_results"])


def test_false_tail_promotion_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] = True
    with pytest.raises((AssertionError, ValidationError)):
        verify(value)
