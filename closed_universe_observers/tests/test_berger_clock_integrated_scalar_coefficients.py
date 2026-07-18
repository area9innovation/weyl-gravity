import json
from fractions import Fraction

from closed_universe_observers.generate_berger_clock_integrated_scalar_coefficients import (
    CLOCK_LAMBDA_SQUARED,
    MAX_MOMENT_K,
    PACKAGE,
    clock_secant_moments,
    integrated_coefficient_interval,
    mode_audit,
    monotonicity_audit,
    radial_moment_intervals,
)
from closed_universe_observers.generate_berger_local_su2_profile_coefficients import representation_matrix


def _radial() -> dict[int, tuple[Fraction, Fraction]]:
    value = json.loads((PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json").read_text())
    return radial_moment_intervals(value)


def test_clock_secant_moments_are_normalized_and_increasing() -> None:
    moments = clock_secant_moments(1024)
    assert moments[0] == (1, 1)
    assert all(moments[k][0] <= 1 <= moments[k][1] for k in range(1, MAX_MOMENT_K + 1))
    assert all(moments[k][1] <= moments[k + 1][1] for k in range(MAX_MOMENT_K))


def test_clock_darboux_enclosures_refine() -> None:
    coarse = clock_secant_moments(256)
    fine = clock_secant_moments(512)
    for k in range(MAX_MOMENT_K + 1):
        assert coarse[k][0] <= fine[k][0] <= fine[k][1] <= coarse[k][1]


def test_monotonicity_bound_is_exactly_strict() -> None:
    audit = monotonicity_audit()
    assert audit["all_decreasing"]
    assert all(Fraction(row["k_lambda_squared_over_cos_lower"]) < 1 for row in audit["rows"])


def test_clock_rate_conversion_is_not_clock_as_time() -> None:
    assert CLOCK_LAMBDA_SQUARED == Fraction(29, 41472)
    assert CLOCK_LAMBDA_SQUARED != Fraction(29, 73728)


def test_constant_spacetime_profile_mode_is_exact() -> None:
    clock = clock_secant_moments(1024)
    interval, remainder, _ = integrated_coefficient_interval(representation_matrix(0)[0, 0], _radial(), clock)
    assert interval == (1, 1)
    assert remainder == 0


def test_clock_integration_preserves_diagonality() -> None:
    clock = clock_secant_moments(1024)
    radial = _radial()
    assert all(mode_audit(two_j, radial, clock)["off_diagonal_nonzero_enclosure_count"] == 0 for two_j in range(5))
