import json
from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import (
    _clock_even_moments as low_mode_clock_even_moments,
    _joint_clock_moment as low_mode_joint_clock_moment,
)
from closed_universe_observers.generate_berger_clock_weighted_scalar_stream import (
    CLOCK_POWERS,
    DEPENDENCIES,
    build,
    certificate_path,
    joint_clock_moments,
)


def _load(power):
    return json.loads(certificate_path(power).read_text())


def test_all_five_weighted_stream_shards_have_complete_typed_coverage():
    for power in CLOCK_POWERS:
        value = _load(power)
        assert value["clock_weight"]["power"] == power
        assert value["coverage"]["mode_count"] == 140
        assert value["coverage"]["serialized_unique_diagonal_count"] == 4970
        assert value["coverage"]["reconstructed_full_diagonal_count"] == 9870
        assert "clock_weighted_local_amplitude" in value["modes"][139]["unique_diagonal"][0]
        assert "clock_integrated_local_amplitude" not in value["modes"][139]["unique_diagonal"][0]


def test_power_ten_generated_certificate_is_current():
    assert _load(10) == build(10)


def test_joint_bound_includes_the_external_detector_clock_factor():
    value = _load(10)
    rows = value["joint_clock_moment_enclosures"]
    k0 = rows[0]["interval"]
    k50 = rows[50]["interval"]
    assert Fraction(k0["lower"]) > 0
    assert Fraction(k0["lower"]) <= Fraction(k0["upper"])
    assert value["clock_weight"]["external_detector_factor"] == "a(t)=cos(lambda s)"
    assert Fraction(k50["lower"]) > Fraction(k0["lower"])
    assert Fraction(k50["upper"]) > Fraction(k0["upper"])


def test_joint_clock_convention_matches_the_existing_low_mode_green_chain():
    moments = json.loads(DEPENDENCIES["low_moments"].read_text())
    low_mode_even = low_mode_clock_even_moments(moments)
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    for power in CLOCK_POWERS:
        high_mode = joint_clock_moments(values, power)
        for k in range(7):
            assert high_mode[k] == low_mode_joint_clock_moment(k, power, low_mode_even)


def test_high_mode_intervals_are_nontrivial_and_narrow():
    for power in CLOCK_POWERS:
        row = _load(power)["modes"][139]["unique_diagonal"][69]
        interval = row["clock_weighted_local_amplitude"]
        lower, upper = Fraction(interval["lower"]), Fraction(interval["upper"])
        assert 0 < lower < upper < 1
        assert upper - lower < Fraction(1, 1000)


def test_invalid_clock_power_is_rejected():
    with pytest.raises(ValueError):
        joint_clock_moments({}, 3)
