import json
from fractions import Fraction

import sympy as sp

from closed_universe_observers.generate_berger_local_su2_profile_coefficients import (
    B2_INTERVAL,
    MAX_Y2,
    PACKAGE,
    Y0,
    Y1,
    Y2,
    Y3,
    coefficient_interval,
    generator_defect_count,
    mode_audit,
    radial_moment_intervals,
    representation_matrix,
)


def _moments() -> dict[int, tuple[Fraction, Fraction]]:
    value = json.loads((PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json").read_text())
    return radial_moment_intervals(value)


def test_representation_derivatives_match_berger_generators() -> None:
    assert all(generator_defect_count(two_j) == 0 for two_j in range(5))


def test_quaternion_sign_mutation_is_detected() -> None:
    assert generator_defect_count(1, flip_y1_sign=True) > 0


def test_axial_bump_fourier_matrices_are_diagonal() -> None:
    moments = _moments()
    assert all(mode_audit(two_j, moments)["off_diagonal_nonzero_enclosure_count"] == 0 for two_j in range(5))


def test_odd_y0_remainders_are_small_and_nonzero() -> None:
    moments = _moments()
    for two_j in (1, 3):
        audit = mode_audit(two_j, moments)
        assert all(0 < Fraction(row["y0_remainder_bound"]) < Fraction(1, 10**24) for row in audit["diagonal"])


def test_constant_mode_is_exactly_normalized() -> None:
    interval, remainder, _ = coefficient_interval(representation_matrix(0)[0, 0], _moments())
    assert interval == (Fraction(1), Fraction(1))
    assert remainder == 0


def test_chart_maximum_matches_anisotropic_scale() -> None:
    assert B2_INTERVAL[1] == MAX_Y2


def test_fundamental_matrix_is_su2_on_the_unit_sphere() -> None:
    matrix = representation_matrix(1)
    norm_relation = {Y0**2: 1 - Y1**2 - Y2**2 - Y3**2}
    product = sp.expand(matrix.conjugate().T * matrix)
    assert sp.simplify(product[0, 0].subs(norm_relation) - 1) == 0
    assert sp.simplify(product[0, 1]) == 0
