from fractions import Fraction

from closed_universe_observers.generate_berger_validated_flat_bump_moments import (
    endpoint_only_peak_mutation,
    integral_enclosures,
    normalized_moments,
    scaled_moments,
)


def test_darboux_enclosures_refine() -> None:
    coarse = integral_enclosures(256, 2)
    fine = integral_enclosures(512, 2)
    for power in fine:
        assert coarse[power][0] <= fine[power][0] <= fine[power][1] <= coarse[power][1]


def test_normalized_moments_are_probabilistic() -> None:
    integrals = integral_enclosures(1024, 2)
    for dimension in (1, 3):
        rows = normalized_moments(integrals, dimension, 2)
        assert rows[0]["normalized_even_moment"] == {"lower": "1", "upper": "1", "width": "0"}
        for row in rows:
            interval = row["normalized_even_moment"]
            assert 0 <= Fraction(interval["lower"]) <= Fraction(interval["upper"]) <= 2


def test_fixed_radius_scaling_is_exact() -> None:
    rows = normalized_moments(integral_enclosures(1024, 2), 3, 2)
    scaled = scaled_moments(rows, Fraction(1, 128))
    source = rows[1]["normalized_even_moment"]
    target = scaled[1]["scaled_even_moment"]
    assert Fraction(target["lower"]) <= Fraction(source["lower"]) / 128**2
    assert Fraction(target["upper"]) >= Fraction(source["upper"]) / 128**2


def test_endpoint_only_peak_mutation_is_detected() -> None:
    assert endpoint_only_peak_mutation()["detected"]
