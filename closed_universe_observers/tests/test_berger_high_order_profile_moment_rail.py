import json
from fractions import Fraction

from closed_universe_observers.generate_berger_high_order_profile_moment_rail import (
    CERTIFICATE,
    MAX_K,
    build,
    clock_secant_moments,
    monotonicity_audit,
    radial_moments,
)


def test_generated_certificate_is_current():
    assert json.loads(CERTIFICATE.read_text()) == build()


def test_high_order_rails_are_complete_and_probabilistic():
    radial = radial_moments()
    clock = clock_secant_moments()
    assert len(radial) == len(clock) == MAX_K + 1
    assert radial[0] == clock[0] == (Fraction(1), Fraction(1))
    assert all(0 <= lower <= upper <= 1 for lower, upper in radial)
    assert all(0 < clock[k][0] <= clock[k][1] and clock[k][1] > 1 for k in range(1, MAX_K + 1))


def test_clock_integrands_are_decreasing_through_k50():
    audit = monotonicity_audit()
    assert audit["all_decreasing"] is True
    assert audit["rows"][-1]["k"] == 50
    assert Fraction(audit["rows"][-1]["k_lambda_squared_over_cos_lower"]) < 1


def test_coarse_rail_contains_the_certified_low_order_values():
    compatibility = build()["low_order_compatibility_audit"]
    assert compatibility["audited_k"] == list(range(7))
    assert compatibility["radial_containment_defect_count"] == 0
    assert compatibility["clock_containment_defect_count"] == 0


def test_scalar_tail_and_branch_claims_remain_open():
    flags = build()["flags"]
    assert flags["VALIDATED_RADIAL_MOMENTS_K0_TO_50_EXPORTED"] is True
    assert flags["HIGH_MODE_SCALAR_COEFFICIENT_VALUES_EVALUATED"] is False
    assert flags["GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED"] is False
    assert flags["BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED"] is False
