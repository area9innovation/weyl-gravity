import json
from fractions import Fraction

from closed_universe_observers.generate_berger_clock_integrated_scalar_stream import CERTIFICATE, build


def _interval(row):
    value = row["clock_integrated_local_amplitude"]
    return Fraction(value["lower"]), Fraction(value["upper"])


def test_generated_certificate_is_current():
    assert json.loads(CERTIFICATE.read_text()) == build()


def test_every_diagonal_is_reconstructed_by_reflection():
    value = build()
    assert value["coverage"]["serialized_unique_diagonal_count"] == 4970
    assert value["coverage"]["reconstructed_full_diagonal_count"] == 9870
    for mode in value["modes"]:
        n = mode["two_j"]
        assert [(row["basis_index"], row["reflected_basis_index"]) for row in mode["unique_diagonal"]] == [
            (row, n - row) for row in range(n // 2 + 1)
        ]


def test_specialized_stream_contains_the_old_low_modes():
    assert build()["low_mode_compatibility_audit"] == {
        "audited_two_j": [0, 1, 2, 3, 4],
        "overlap_defect_count": 0,
    }


def test_high_mode_intervals_are_nontrivial_and_narrow():
    modes = build()["modes"]
    for n, row in ((138, 69), (139, 0), (139, 69)):
        lower, upper = _interval(modes[n]["unique_diagonal"][row])
        assert 0 < lower < upper < 1
        assert upper - lower < Fraction(1, 1000)


def test_uniform_binomial_remainder_is_negligible_on_the_declared_rail():
    audit = build()["truncation_remainder_audit"]
    assert audit["maximum_mode_two_j"] == 139
    assert Fraction(audit["maximum_uniform_remainder_upper"]) < Fraction(1, 10**150)


def test_green_tail_recoil_and_branch_bridge_remain_open():
    flags = build()["flags"]
    assert flags["CLOCK_INTEGRATED_DIAGONAL_SCALAR_COEFFICIENTS_TWO_J0_TO_139_EXPORTED"] is True
    assert flags["POLARIZATION_RECURRENCE_CLOCK_GREEN_CHAIN_APPLIED"] is False
    assert flags["GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED"] is False
    assert flags["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
    assert flags["BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED"] is False
