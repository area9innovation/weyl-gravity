import json
from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_clock_weighted_scalar_stream import (
    CLOCK_POWERS,
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


def test_joint_bound_uses_the_exact_unweighted_even_moment_at_k_zero():
    value = _load(10)
    rows = value["joint_clock_moment_enclosures"]
    k0 = rows[0]["interval"]
    k50 = rows[50]["interval"]
    assert Fraction(k0["lower"]) > 0
    assert Fraction(k0["lower"]) <= Fraction(k0["upper"])
    assert Fraction(k50["lower"]) == Fraction(k0["lower"])
    assert Fraction(k50["upper"]) > Fraction(k0["upper"])


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
