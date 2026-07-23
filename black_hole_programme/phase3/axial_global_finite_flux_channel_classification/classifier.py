"""Exact downstream algebra for the axial global finite-flux classifier.

This module deliberately contains no radial solver.  It consumes a connection
matrix only after an upstream artifact has certified that matrix on its
declared frequency cell.  The exact routines are also used on small synthetic
fixtures so that rank, radical, inertia, origin, orientation, and one-sided
relation logic are tested before the global handoff exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import sympy as sp


RAW_HORIZON_ORDER = (
    "XH0a", "XH0b", "EH0", "XHplus", "EHout", "XHminus",
)
PUBLIC_HORIZON_ORDER = (
    "XH0a", "XH0b", "XHplus", "XHminus", "EH0", "EHout",
)
INFINITY_ORDER = ("XI0", "XI1", "XI2", "XI3", "EI0", "EI2")
RAW_FUTURE_REGULAR_SELECTOR = (0, 1, 2)
PUBLIC_FUTURE_REGULAR_SELECTOR = (0, 1, 4)
PUBLIC_TO_RAW = (0, 1, 3, 5, 2, 4)
RAW_TO_PUBLIC = (0, 1, 4, 2, 5, 3)
IMINUS_SELECTOR = (0, 1, 4)
IPLUS_SELECTOR = (2, 3, 5)
FUTURE_REGULAR_ORIGIN_ORDER = ("XH0a", "XH0b", "EH0")


def dagger(matrix: sp.Matrix) -> sp.Matrix:
    return matrix.conjugate().T.applyfunc(sp.simplify)


def selector(rows: Iterable[int], size: int = 6) -> sp.Matrix:
    rows = tuple(rows)
    answer = sp.zeros(len(rows), size)
    for i, row in enumerate(rows):
        answer[i, row] = 1
    return answer


def _is_zero(value: sp.Expr) -> bool:
    return sp.simplify(value) == 0


def require_hermitian(matrix: sp.Matrix, name: str) -> None:
    if matrix.rows != matrix.cols:
        raise ValueError(f"{name} is not square")
    if matrix.applyfunc(sp.simplify) != dagger(matrix):
        raise ValueError(f"{name} is not Hermitian")


def realify_hermitian(matrix: sp.Matrix) -> sp.Matrix:
    """Return the real symmetric form underlying a complex Hermitian form."""
    require_hermitian(matrix, "Hermitian form")
    real = matrix.applyfunc(lambda value: sp.simplify(sp.re(value)))
    imag = matrix.applyfunc(lambda value: sp.simplify(sp.im(value)))
    answer = sp.Matrix.vstack(
        sp.Matrix.hstack(real, -imag),
        sp.Matrix.hstack(imag, real),
    ).applyfunc(sp.simplify)
    if answer != answer.T:
        raise ValueError("realification is not symmetric")
    if any(value.free_symbols for value in answer):
        raise ValueError("exact inertia requires a constant exact matrix")
    return answer


def _permute(matrix: sp.Matrix, order: list[int]) -> sp.Matrix:
    return matrix.extract(order, order)


def rational_symmetric_inertia(matrix: sp.Matrix) -> tuple[int, int, int]:
    """Exact congruence inertia of a constant real symmetric matrix.

    A nonzero diagonal pivot contributes a one-dimensional sign and is
    removed by a Schur complement.  If every diagonal entry vanishes but an
    off-diagonal entry is nonzero, the corresponding 2x2 block has inertia
    (1,1) and is removed as a block.  This avoids sampled eigenvectors.
    """
    current = matrix.applyfunc(sp.simplify)
    if current != current.T:
        raise ValueError("inertia input is not symmetric")
    positive = negative = zero = 0
    while current.rows:
        n = current.rows
        diagonal = next(
            (i for i in range(n) if not _is_zero(current[i, i])),
            None,
        )
        if diagonal is not None:
            order = [diagonal] + [i for i in range(n) if i != diagonal]
            current = _permute(current, order)
            pivot = sp.simplify(current[0, 0])
            sign = sp.sign(pivot)
            if sign == 1:
                positive += 1
            elif sign == -1:
                negative += 1
            else:
                raise ValueError(f"undecidable exact pivot sign: {pivot}")
            if n == 1:
                current = sp.zeros(0)
            else:
                tail = current[1:, 1:]
                column = current[1:, 0]
                current = (tail - column * column.T / pivot).applyfunc(
                    sp.simplify
                )
            continue

        pair = None
        for i in range(n):
            for j in range(i + 1, n):
                if not _is_zero(current[i, j]):
                    pair = (i, j)
                    break
            if pair is not None:
                break
        if pair is None:
            zero += n
            break

        i, j = pair
        order = [i, j] + [k for k in range(n) if k not in (i, j)]
        current = _permute(current, order)
        block = current[:2, :2]
        if not (_is_zero(block[0, 0]) and _is_zero(block[1, 1])):
            raise AssertionError("two-dimensional pivot lost zero diagonal")
        positive += 1
        negative += 1
        if n == 2:
            current = sp.zeros(0)
        else:
            coupling = current[:2, 2:]
            tail = current[2:, 2:]
            current = (
                tail - coupling.T * block.inv() * coupling
            ).applyfunc(sp.simplify)
    return positive, negative, zero


def complex_hermitian_inertia(matrix: sp.Matrix) -> tuple[int, int, int]:
    real_inertia = rational_symmetric_inertia(realify_hermitian(matrix))
    if any(value % 2 for value in real_inertia):
        raise AssertionError("Hermitian realification did not have doubled inertia")
    return tuple(value // 2 for value in real_inertia)


def _column_space_matrix(matrix: sp.Matrix) -> sp.Matrix:
    columns = matrix.columnspace()
    return sp.Matrix.hstack(*columns) if columns else sp.zeros(matrix.rows, 0)


def _null_space_matrix(matrix: sp.Matrix) -> sp.Matrix:
    columns = matrix.nullspace()
    return sp.Matrix.hstack(*columns) if columns else sp.zeros(matrix.cols, 0)


def _joined_rank(*matrices: sp.Matrix) -> int:
    nonempty = [matrix for matrix in matrices if matrix.cols]
    if not nonempty:
        return 0
    return sp.Matrix.hstack(*nonempty).rank()


def _origin_embedding(columns: tuple[int, ...], size: int = 3) -> sp.Matrix:
    answer = sp.zeros(size, len(columns))
    for j, column in enumerate(columns):
        answer[column, j] = 1
    return answer


def classify_populated_form(
    trace_map: sp.Matrix,
    endpoint_gram: sp.Matrix,
) -> dict:
    """Classify the induced form on ``im(trace_map)``.

    The domain kernel is bookkeeping, not a physical radical.  If ``g`` is
    the pullback, then

        dim rad(im C) = nullity(g) - nullity(C),
        dim ((im C)/rad) = rank(g).
    """
    if trace_map.cols != 3:
        raise ValueError("future-regular domain must have three complex columns")
    require_hermitian(endpoint_gram, "endpoint Gram")
    if endpoint_gram.rows != trace_map.rows:
        raise ValueError("trace/Gram shape mismatch")
    pullback = (dagger(trace_map) * endpoint_gram * trace_map).applyfunc(
        sp.simplify
    )
    require_hermitian(pullback, "pullback Gram")
    image_rank = trace_map.rank()
    pullback_rank = pullback.rank()
    domain_kernel_dimension = trace_map.cols - image_rank
    pullback_nullity = trace_map.cols - pullback_rank
    radical_dimension = pullback_nullity - domain_kernel_dimension
    if radical_dimension < 0:
        raise AssertionError("trace kernel is not contained in pullback kernel")

    domain_radical = _null_space_matrix(pullback)
    image_radical = _column_space_matrix(trace_map * domain_radical)
    if image_radical.rank() != radical_dimension:
        raise AssertionError("image radical dimension mismatch")

    origins = {}
    for name, columns in {
        "additional": (0, 1),
        "einstein": (2,),
    }.items():
        embedded = _origin_embedding(columns)
        image = _column_space_matrix(trace_map * embedded)
        quotient_rank = _joined_rank(image_radical, image) - image_radical.rank()
        origins[name] = {
            "domain_dimension": len(columns),
            "populated_image_dimension": image.rank(),
            "physical_quotient_dimension": quotient_rank,
        }

    inertia = complex_hermitian_inertia(pullback)
    return {
        "trace_rank": image_rank,
        "trace_kernel_dimension": domain_kernel_dimension,
        "pullback_rank": pullback_rank,
        "pullback_nullity": pullback_nullity,
        "populated_radical_dimension": radical_dimension,
        "physical_quotient_dimension": pullback_rank,
        "pullback_gram": pullback,
        "realified_pullback_gram": realify_hermitian(pullback),
        "domain_inertia": inertia,
        "physical_inertia": (inertia[0], inertia[1], 0),
        "origins": origins,
    }


@dataclass(frozen=True)
class ExactCellClassification:
    connection: sp.Matrix
    imin_trace: sp.Matrix
    iplus_trace: sp.Matrix
    imin: dict
    iplus: dict
    joint_kernel_dimension: int
    joint_population_dimension: int
    conservation_certified: bool
    one_sided_relation: dict


def classify_exact_cell(
    connection: sp.Matrix,
    gram_minus: sp.Matrix,
    gram_plus: sp.Matrix,
    horizon_plus_gram: sp.Matrix | None = None,
) -> ExactCellClassification:
    """Classify a constant exact 6x3 connection fixture.

    This function is a correctness oracle for synthetic tests and any future
    exact-rational handoff.  A parameter interval must supply a separate
    validated enclosure proving that the same classification holds on the
    whole cell.
    """
    if connection.shape != (6, 3):
        raise ValueError("connection must be 6x3 in the frozen infinity order")
    cminus = selector(IMINUS_SELECTOR) * connection
    cplus = selector(IPLUS_SELECTOR) * connection
    minus = classify_populated_form(cminus, gram_minus)
    plus = classify_populated_form(cplus, gram_plus)
    stacked = sp.Matrix.vstack(cminus, cplus)
    joint_kernel_dimension = connection.cols - stacked.rank()

    gminus = minus["pullback_gram"]
    gplus = plus["pullback_gram"]
    conservation_certified = False
    one_sided: dict = {
        "constructed": False,
        "full_scattering_matrix": False,
        "reason": "horizon-plus Gram or invertible Iminus trace is absent",
    }
    if horizon_plus_gram is not None:
        require_hermitian(horizon_plus_gram, "future-horizon Gram")
        if horizon_plus_gram.shape != (3, 3):
            raise ValueError("future-horizon Gram must be 3x3")
        defect = (
            horizon_plus_gram + gplus - gminus
        ).applyfunc(sp.simplify)
        conservation_certified = defect == sp.zeros(3)
        if not conservation_certified:
            raise ValueError("orientation-correct current conservation failed")
        if cminus.det() != 0:
            inverse = cminus.inv()
            outgoing = sp.Matrix.vstack(inverse, cplus * inverse)
            jout = sp.diag(1, 1, 1, 1, 1, 1)
            jout[:3, :3] = horizon_plus_gram
            jout[3:, 3:] = gram_plus
            relation_defect = (
                dagger(outgoing) * jout * outgoing - gram_minus
            ).applyfunc(sp.simplify)
            if relation_defect != sp.zeros(3):
                raise AssertionError("one-sided relation is not J-isometric")
            one_sided = {
                "constructed": True,
                "full_scattering_matrix": False,
                "incoming_space": "Iminus",
                "outgoing_space": "Hplus direct_sum Iplus",
                "missing_boundary_block": "Hminus incoming data",
                "J_isometry_certified": True,
                "matrix": outgoing,
            }

    return ExactCellClassification(
        connection=connection,
        imin_trace=cminus,
        iplus_trace=cplus,
        imin=minus,
        iplus=plus,
        joint_kernel_dimension=joint_kernel_dimension,
        joint_population_dimension=stacked.rank(),
        conservation_certified=conservation_certified,
        one_sided_relation=one_sided,
    )

