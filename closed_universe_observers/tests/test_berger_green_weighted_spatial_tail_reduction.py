import copy
from fractions import Fraction
import json

import pytest
from jsonschema import ValidationError

from closed_universe_observers.generate_berger_green_weighted_spatial_tail_reduction import CERTIFICATE
from closed_universe_observers.verify_berger_green_weighted_spatial_tail_reduction import verify


def test_exact_charge_block_audit_has_no_defects() -> None:
    value = json.loads(CERTIFICATE.read_text())
    audit = value["spectral_lower_bound_theorem"]["exact_formula_audit"]
    assert audit["diagonal_shift_defect_count"] == 0
    assert audit["single_coupling_bound_defect_count"] == 0
    assert audit["maximum_row_degree_defect_count"] == 0
    assert audit["three_member_block_count"] > 0


def test_selected_cutoff_exports_four_exact_sobolev_factors() -> None:
    value = json.loads(CERTIFICATE.read_text())
    selected = next(row for row in value["cutoff_reductions"] if row["retained_max_two_j"] == 1024)
    assert selected["first_omitted_two_j"] == 1025
    assert Fraction(selected["delta1_spectral_lower_bound"]) > 262000
    assert [row["power"] for row in selected["sobolev_norm_reductions"]] == [1, 2, 3, 4]
    assert all(Fraction(row["factor"]) > 0 for row in selected["sobolev_norm_reductions"])


def test_exact_t_maxwell_tail_multipliers_are_contractive() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["maxwell_green_weighting"]["spatial_operator_norm_upper"] == "1"
    assert value["maxwell_green_weighting"]["temporal_operator_norm_upper"] == "1"
    assert value["flags"]["GREEN_WEIGHTED_MAXWELL_TAIL_CONVERSION_EXPORTED"] is True


def test_radical_and_row_degree_mutations_are_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert all(row["detected"] is True for row in value["mutation_results"])


def test_tail_and_response_remain_fail_closed() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert all(row["status"] == "OPEN" for row in value["unresolved_profile_ledger"])
    assert value["flags"]["EVALUATED_PROFILE_SOBOLEV_NORM_EXPORTED"] is False
    assert value["flags"]["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False


def test_false_numerical_tail_promotion_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["flags"]["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED"] = True
    with pytest.raises((AssertionError, ValidationError)):
        verify(value)
