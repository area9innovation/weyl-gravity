from fractions import Fraction

import pytest

from black_hole_programme.phase3.axial_structured_lower_transition_preflight.structured_reference import (
    StructureError,
    block_lower,
    exact_fixture,
    exact_nilpotent_exponential,
    matrix,
    structured_truncated_exponential,
    verify_exact_fixture,
)


def test_structured_recurrence_equals_exact_constant_block_exponential():
    assert verify_exact_fixture()


@pytest.mark.parametrize("mutation", ["omit_kernel_lower", "swap_order"])
def test_lower_recurrence_mutations_are_rejected(mutation):
    assert not verify_exact_fixture(mutation)


def test_exact_upper_right_block_is_zero():
    ac, g, ak, h = exact_fixture()
    out = structured_truncated_exponential(ac, g, ak, h, 4)
    assert all(out[i][j] == 0 for i in range(2) for j in range(2, 4))


def test_non_nilpotent_exact_fixture_is_refused():
    with pytest.raises(StructureError):
        exact_nilpotent_exponential(matrix(((1, 0), (0, 1))), Fraction(1))


def test_bad_block_shape_is_refused():
    with pytest.raises(StructureError):
        block_lower(matrix(((1, 0), (0, 1))), matrix(((1,),)), matrix(((1,),)))
