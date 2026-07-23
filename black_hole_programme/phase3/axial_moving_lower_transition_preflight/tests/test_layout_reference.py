from black_hole_programme.phase3.axial_moving_lower_transition_preflight.layout_reference import (
    block_lower,
    contiguous_part,
    identity,
    matrix,
    moving_formula,
    mul,
    predecessor_interleaved_part,
    verify_layout_fixtures,
)


def test_layout_and_moving_formula_fixtures() -> None:
    assert verify_layout_fixtures()


def test_contiguous_extractor_round_trip() -> None:
    c = matrix(((2, 3), (5, 7)))
    d = matrix(((11, 13),))
    k = matrix(((17,),))
    a = block_lower(c, d, k)
    assert contiguous_part(a, 2, "carrier") == c
    assert contiguous_part(a, 2, "lower") == d
    assert contiguous_part(a, 2, "kernel") == k


def test_moving_identity_frames_return_original() -> None:
    u = block_lower(matrix(((2, 1), (0, 3))), matrix(((5, -2),)), matrix(((7,),)))
    eye = block_lower(identity(2), matrix(((0, 0),)), identity(1))
    assert moving_formula(u, eye, eye, 2) == u


def test_predecessor_interleaved_mutation_is_rejected() -> None:
    c = tuple(tuple(100 * i + j + 1 for j in range(8)) for i in range(8))
    d = tuple(tuple(1000 + 100 * i + j for j in range(8)) for i in range(4))
    k = tuple(tuple(2000 + 100 * i + j for j in range(4)) for i in range(4))
    a = block_lower(matrix(c), matrix(d), matrix(k))
    assert predecessor_interleaved_part(a, "carrier") != matrix(c)
    assert predecessor_interleaved_part(a, "lower") != matrix(d)
    assert predecessor_interleaved_part(a, "kernel") != matrix(k)


def test_formula_is_not_plain_unframed_product() -> None:
    u = block_lower(matrix(((2, 0), (1, 1))), matrix(((3, 2),)), matrix(((5,),)))
    b0 = block_lower(matrix(((1, 1), (0, 2))), matrix(((4, -1),)), matrix(((3,),)))
    b1 = block_lower(matrix(((2, 0), (1, 1))), matrix(((1, 5),)), matrix(((7,),)))
    assert moving_formula(u, b0, b1, 2) != mul(u, b0)
