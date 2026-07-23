"""Validated affine-cell algebra for the Phase-3 channel handoff.

The global handoff represents every scalar as

    center + linear * e + remainder,       |e| <= 1,

with exact rational center/linear coefficients and binary64 interval
endpoints encoded by their bits.  This module independently checks the
nonlinear pullbacks and supplies a whole-cell inertia witness.  It never
promotes a sampled or midpoint-only classification.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import math
import struct
from typing import Iterable

import sympy as sp

from .classifier import rational_symmetric_inertia


# Forge's IvAffineMat uses a normalized generator e in [-1,1].  The physical
# frequency-cell radius is already absorbed into the serialized linear
# coefficient; applying it a second time would unsoundly shrink every bound.
PARAMETER_RADIUS = Fraction(1)


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def _float_fraction(bits: str) -> Fraction:
    value = struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]
    if not math.isfinite(value):
        raise ValueError("nonfinite interval endpoint")
    return Fraction.from_float(value)


@dataclass(frozen=True)
class Interval:
    lo: Fraction
    hi: Fraction

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError("reversed interval")

    @classmethod
    def point(cls, value: Fraction | int) -> "Interval":
        value = Fraction(value)
        return cls(value, value)

    def __add__(self, other: "Interval") -> "Interval":
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __neg__(self) -> "Interval":
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other: "Interval") -> "Interval":
        return self + (-other)

    def __mul__(self, other: "Interval") -> "Interval":
        products = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        return Interval(min(products), max(products))

    def scale(self, value: Fraction | int) -> "Interval":
        return self * Interval.point(Fraction(value))

    def contains(self, other: "Interval") -> bool:
        return self.lo <= other.lo and other.hi <= self.hi

    def contains_zero(self) -> bool:
        return self.lo <= 0 <= self.hi

    def abs_upper(self) -> Fraction:
        return max(abs(self.lo), abs(self.hi))


ZERO_INTERVAL = Interval.point(0)
PARAMETER_INTERVAL = Interval(-PARAMETER_RADIUS, PARAMETER_RADIUS)
PARAMETER_SQUARED_INTERVAL = Interval(0, PARAMETER_RADIUS**2)


@dataclass(frozen=True)
class AffineScalar:
    center: Fraction
    linear: Fraction
    remainder: Interval

    @classmethod
    def zero(cls) -> "AffineScalar":
        return cls(Fraction(), Fraction(), ZERO_INTERVAL)

    @classmethod
    def from_json(cls, value: dict) -> "AffineScalar":
        lo, hi = (_float_fraction(bits) for bits in value["remainder"])
        return cls(_fraction(value["center"]), _fraction(value["linear"]), Interval(lo, hi))

    def __add__(self, other: "AffineScalar") -> "AffineScalar":
        return AffineScalar(
            self.center + other.center,
            self.linear + other.linear,
            self.remainder + other.remainder,
        )

    def __neg__(self) -> "AffineScalar":
        return AffineScalar(-self.center, -self.linear, -self.remainder)

    def __sub__(self, other: "AffineScalar") -> "AffineScalar":
        return self + (-other)

    def __mul__(self, other: "AffineScalar") -> "AffineScalar":
        # The exact affine part is retained.  Every quadratic or
        # remainder-containing term is enclosed in the new remainder.
        remainder = (
            PARAMETER_SQUARED_INTERVAL.scale(self.linear * other.linear)
            + other.remainder.scale(self.center)
            + self.remainder.scale(other.center)
            + PARAMETER_INTERVAL.scale(self.linear) * other.remainder
            + PARAMETER_INTERVAL.scale(other.linear) * self.remainder
            + self.remainder * other.remainder
        )
        return AffineScalar(
            self.center * other.center,
            self.center * other.linear + self.linear * other.center,
            remainder,
        )

    def value_interval(self) -> Interval:
        return (
            Interval.point(self.center)
            + PARAMETER_INTERVAL.scale(self.linear)
            + self.remainder
        )

    def error_interval(self) -> Interval:
        return PARAMETER_INTERVAL.scale(self.linear) + self.remainder

    def contains_affine(self, other: "AffineScalar") -> bool:
        # Rebased producers may choose different dyadic center/linear
        # representatives.  Compare the represented functions, not their
        # serialization: the outer remainder must absorb that affine shift
        # for every value of the shared parameter.
        required_remainder = (
            other.remainder
            + Interval.point(other.center - self.center)
            + PARAMETER_INTERVAL.scale(other.linear - self.linear)
        )
        return self.remainder.contains(required_remainder)


@dataclass(frozen=True)
class ComplexAffine:
    re: AffineScalar
    im: AffineScalar

    @classmethod
    def zero(cls) -> "ComplexAffine":
        return cls(AffineScalar.zero(), AffineScalar.zero())

    @classmethod
    def from_json(cls, value: dict) -> "ComplexAffine":
        return cls(
            AffineScalar.from_json(value["re"]),
            AffineScalar.from_json(value["im"]),
        )

    def __add__(self, other: "ComplexAffine") -> "ComplexAffine":
        return ComplexAffine(self.re + other.re, self.im + other.im)

    def __neg__(self) -> "ComplexAffine":
        return ComplexAffine(-self.re, -self.im)

    def __sub__(self, other: "ComplexAffine") -> "ComplexAffine":
        return self + (-other)

    def __mul__(self, other: "ComplexAffine") -> "ComplexAffine":
        return ComplexAffine(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re,
        )

    def conjugate(self) -> "ComplexAffine":
        return ComplexAffine(self.re, -self.im)

    def contains_affine(self, other: "ComplexAffine") -> bool:
        return self.re.contains_affine(other.re) and self.im.contains_affine(other.im)


AffineMatrix = list[list[ComplexAffine]]


def matrix_from_json(matrix: list) -> AffineMatrix:
    if not matrix or not matrix[0]:
        raise ValueError("empty affine matrix")
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("ragged affine matrix")
    return [[ComplexAffine.from_json(value) for value in row] for row in matrix]


def matrix_shape(matrix: AffineMatrix) -> tuple[int, int]:
    return len(matrix), len(matrix[0])


def matrix_dagger(matrix: AffineMatrix) -> AffineMatrix:
    rows, cols = matrix_shape(matrix)
    return [[matrix[i][j].conjugate() for i in range(rows)] for j in range(cols)]


def matrix_multiply(left: AffineMatrix, right: AffineMatrix) -> AffineMatrix:
    lrows, inner = matrix_shape(left)
    rrows, rcols = matrix_shape(right)
    if inner != rrows:
        raise ValueError("affine matrix shape mismatch")
    answer: AffineMatrix = []
    for i in range(lrows):
        row = []
        for j in range(rcols):
            value = ComplexAffine.zero()
            for k in range(inner):
                value = value + left[i][k] * right[k][j]
            row.append(value)
        answer.append(row)
    return answer


def matrix_add(*matrices: AffineMatrix) -> AffineMatrix:
    if not matrices:
        raise ValueError("no affine matrices to add")
    shape = matrix_shape(matrices[0])
    if any(matrix_shape(matrix) != shape for matrix in matrices[1:]):
        raise ValueError("affine matrix addition shape mismatch")
    rows, cols = shape
    return [
        [
            sum(
                (matrix[i][j] for matrix in matrices),
                ComplexAffine.zero(),
            )
            for j in range(cols)
        ]
        for i in range(rows)
    ]


def matrix_negate(matrix: AffineMatrix) -> AffineMatrix:
    return [[-value for value in row] for row in matrix]


def matrix_contains(outer: AffineMatrix, inner: AffineMatrix) -> bool:
    if matrix_shape(outer) != matrix_shape(inner):
        return False
    rows, cols = matrix_shape(outer)
    return all(
        outer[i][j].contains_affine(inner[i][j])
        for i in range(rows)
        for j in range(cols)
    )


def pullback(connection: AffineMatrix, gram: AffineMatrix) -> AffineMatrix:
    return matrix_multiply(matrix_multiply(matrix_dagger(connection), gram), connection)


def require_hermitian_enclosure(matrix: AffineMatrix, name: str) -> None:
    """Require a conjugation-compatible enclosure of a Hermitian family.

    Interval boxes cannot themselves encode the dependency equating
    ``A[j,i]`` with ``conj(A[i,j])``.  This check therefore validates a
    symmetric enclosure; structural Hermiticity must still come from the
    action-current/pullback construction pinned by provenance.
    """
    rows, cols = matrix_shape(matrix)
    if rows != cols:
        raise ValueError(f"{name} is not square")
    for i in range(rows):
        for j in range(cols):
            value = matrix[i][j]
            transpose = matrix[j][i].conjugate()
            if value.re.center != transpose.re.center:
                raise ValueError(f"{name} real center is not Hermitian")
            if value.im.center != transpose.im.center:
                raise ValueError(f"{name} imaginary center is not Hermitian")
            if value.re.linear != transpose.re.linear:
                raise ValueError(f"{name} real linear coefficient is not Hermitian")
            if value.im.linear != transpose.im.linear:
                raise ValueError(f"{name} imaginary linear coefficient is not Hermitian")
            if (
                max(value.re.remainder.lo, transpose.re.remainder.lo)
                > min(value.re.remainder.hi, transpose.re.remainder.hi)
            ):
                raise ValueError(f"{name} real remainders have no Hermitian intersection")
            if (
                max(value.im.remainder.lo, transpose.im.remainder.lo)
                > min(value.im.remainder.hi, transpose.im.remainder.hi)
            ):
                raise ValueError(
                    f"{name} imaginary remainders have no Hermitian intersection"
                )


def determinant3(matrix: AffineMatrix) -> ComplexAffine:
    if matrix_shape(matrix) != (3, 3):
        raise ValueError("determinant witness requires 3x3 matrix")
    a = matrix
    return (
        a[0][0] * a[1][1] * a[2][2]
        + a[0][1] * a[1][2] * a[2][0]
        + a[0][2] * a[1][0] * a[2][1]
        - a[0][2] * a[1][1] * a[2][0]
        - a[0][1] * a[1][0] * a[2][2]
        - a[0][0] * a[1][2] * a[2][1]
    )


def determinant_excludes_zero(matrix: AffineMatrix) -> bool:
    determinant = determinant3(matrix)
    return not (
        determinant.re.value_interval().contains_zero()
        and determinant.im.value_interval().contains_zero()
    )


def _realification(matrix: AffineMatrix) -> list[list[AffineScalar]]:
    rows, cols = matrix_shape(matrix)
    if rows != cols:
        raise ValueError("realification requires a square matrix")
    return [
        [
            (
                matrix[i][j].re
                if i < rows and j < cols
                else -matrix[i][j - cols].im
                if i < rows
                else matrix[i - rows][j].im
                if j < cols
                else matrix[i - rows][j - cols].re
            )
            for j in range(2 * cols)
        ]
        for i in range(2 * rows)
    ]


def _sympy_rational(value: Fraction) -> sp.Rational:
    return sp.Rational(value.numerator, value.denominator)


def _fraction_from_sympy(value: sp.Expr) -> Fraction:
    value = sp.Rational(value)
    return Fraction(int(value.p), int(value.q))


@dataclass(frozen=True)
class WholeCellInertia:
    complex_inertia: tuple[int, int, int]
    inverse_perturbation_bound: Fraction


def certify_whole_cell_inertia(matrix: AffineMatrix) -> WholeCellInertia:
    """Certify constant inertia by a rigorous inverse-perturbation bound.

    Let ``A(t)=A0+E(t)`` be the realification.  If

        || |A0^-1| R ||_infinity < 1,

    where ``R`` bounds ``|E|`` entrywise, every matrix on the cell is
    nonsingular.  The real symmetric inertia is then constant by homotopy.
    """
    require_hermitian_enclosure(matrix, "whole-cell form")
    real = _realification(matrix)
    size = len(real)
    center = sp.Matrix(
        [[_sympy_rational(real[i][j].center) for j in range(size)] for i in range(size)]
    )
    linear = sp.Matrix(
        [[_sympy_rational(real[i][j].linear) for j in range(size)] for i in range(size)]
    )
    if center != center.T:
        raise ValueError("affine Hermitian center does not realify symmetrically")
    if linear != linear.T:
        raise ValueError("affine Hermitian linear coefficient is not symmetric")
    if center.det() == 0:
        raise ValueError("center form is singular; inverse perturbation witness unavailable")

    radii = [[Fraction() for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            radius = real[i][j].error_interval().abs_upper()
            transpose_radius = real[j][i].error_interval().abs_upper()
            radii[i][j] = max(radius, transpose_radius)

    inverse = center.inv()
    row_bounds = []
    for i in range(size):
        total = Fraction()
        for j in range(size):
            for k in range(size):
                total += abs(_fraction_from_sympy(inverse[i, k])) * radii[k][j]
        row_bounds.append(total)
    bound = max(row_bounds, default=Fraction())
    if bound >= 1:
        raise ValueError(f"whole-cell inertia unresolved: inverse bound {bound} >= 1")

    real_inertia = rational_symmetric_inertia(center)
    if any(value % 2 for value in real_inertia):
        raise AssertionError("realified Hermitian inertia is not doubled")
    return WholeCellInertia(
        tuple(value // 2 for value in real_inertia),
        bound,
    )


def select_rows(matrix: AffineMatrix, rows: Iterable[int]) -> AffineMatrix:
    return [matrix[i] for i in rows]


def select_principal(matrix: AffineMatrix, indices: Iterable[int]) -> AffineMatrix:
    indices = tuple(indices)
    rows, cols = matrix_shape(matrix)
    if rows != cols or any(index < 0 or index >= rows for index in indices):
        raise ValueError("invalid principal-submatrix selection")
    return [[matrix[i][j] for j in indices] for i in indices]


def _is_exact_zero(value: AffineScalar) -> bool:
    return (
        value.center == 0
        and value.linear == 0
        and value.remainder == ZERO_INTERVAL
    )


def _complex_excludes_zero(value: ComplexAffine) -> bool:
    return not (
        value.re.value_interval().contains_zero()
        and value.im.value_interval().contains_zero()
    )


def certify_origin_blocks(matrix: AffineMatrix) -> dict:
    """Classify Einstein/additional restrictions and their mixed block."""
    if matrix_shape(matrix) != (3, 3):
        raise ValueError("origin classification requires a 3x3 form")
    additional = select_principal(matrix, (0, 1))
    einstein = select_principal(matrix, (2,))
    mixed = [[matrix[0][2]], [matrix[1][2]]]
    if any(_complex_excludes_zero(row[0]) for row in mixed):
        mixed_status = "CERTIFIED_NONZERO"
        mixed_rank = 1
    elif all(
        _is_exact_zero(row[0].re) and _is_exact_zero(row[0].im)
        for row in mixed
    ):
        mixed_status = "EXACT_ZERO"
        mixed_rank = 0
    else:
        mixed_status = "UNRESOLVED"
        mixed_rank = None
    def restricted_witness(block: AffineMatrix) -> dict:
        try:
            witness = certify_whole_cell_inertia(block)
        except ValueError as exc:
            return {
                "status": "UNRESOLVED",
                "reason": str(exc),
            }
        return {
            "status": "CERTIFIED",
            "inertia": witness.complex_inertia,
            "inverse_perturbation_bound": witness.inverse_perturbation_bound,
        }

    return {
        "additional": restricted_witness(additional),
        "einstein": restricted_witness(einstein),
        "mixed_status": mixed_status,
        "mixed_rank": mixed_rank,
    }


def _validate_payload_algebra(payload: dict) -> dict:
    connection = matrix_from_json(payload["connection"]["complex_6_by_3"])
    cminus = matrix_from_json(payload["connection"]["Cminus_3_by_3"])
    cplus = matrix_from_json(payload["connection"]["Cplus_3_by_3"])
    if not matrix_contains(cminus, select_rows(connection, (0, 1, 4))):
        raise ValueError("Cminus does not contain the frozen connection projection")
    if not matrix_contains(cplus, select_rows(connection, (2, 3, 5))):
        raise ValueError("Cplus does not contain the frozen connection projection")
    if not determinant_excludes_zero(cminus):
        raise ValueError("Cminus rank three is not independently certified")
    if not determinant_excludes_zero(cplus):
        raise ValueError("Cplus rank three is not independently certified")

    forms = payload["endpoint_forms"]
    gminus = matrix_from_json(forms["Gminus"])
    gplus = matrix_from_json(forms["Gplus"])
    require_hermitian_enclosure(gminus, "Gminus")
    require_hermitian_enclosure(gplus, "Gplus")
    pulled_minus = matrix_from_json(forms["gminus_pullback"])
    pulled_plus = matrix_from_json(forms["gplus_pullback"])
    if not matrix_contains(pulled_minus, pullback(cminus, gminus)):
        raise ValueError("declared gminus does not enclose the independent pullback")
    if not matrix_contains(pulled_plus, pullback(cplus, gplus)):
        raise ValueError("declared gplus does not enclose the independent pullback")

    ghplus = matrix_from_json(forms["GHplus_outward"])
    computed_defect = matrix_add(
        ghplus,
        pulled_plus,
        matrix_negate(pulled_minus),
    )
    declared_defect = matrix_from_json(forms["conservation"]["defect"])
    if not matrix_contains(declared_defect, computed_defect):
        raise ValueError(
            "declared conservation defect does not enclose the independent sum"
        )
    for row in declared_defect:
        for value in row:
            if not value.re.value_interval().contains_zero():
                raise ValueError("conservation defect real part excludes zero")
            if not value.im.value_interval().contains_zero():
                raise ValueError("conservation defect imaginary part excludes zero")

    inertia = {
        "gminus": certify_whole_cell_inertia(pulled_minus),
        "gplus": certify_whole_cell_inertia(pulled_plus),
        "GHplus": certify_whole_cell_inertia(ghplus),
    }
    declared = payload["classification_witnesses"]["inertia"]
    for name, witness in inertia.items():
        expected = (
            declared[name]["positive"],
            declared[name]["negative"],
            declared[name]["zero"],
        )
        if witness.complex_inertia != expected:
            raise ValueError(
                f"{name} inertia mismatch: independent {witness.complex_inertia}, "
                f"declared {expected}"
            )
    return {
        "connection_rank": 3,
        "Cminus_rank": 3,
        "Cplus_rank": 3,
        "inertia": inertia,
        "origin_blocks": {
            "Iminus": certify_origin_blocks(pulled_minus),
            "Iplus": certify_origin_blocks(pulled_plus),
        },
        "pullbacks_independently_enclosed": True,
        "conservation_enclosure_independently_checked": True,
        "structural_hermiticity_required": True,
    }


def validate_channel_handoff_algebra(document: dict) -> dict:
    """Validate every certified cell in the subdivided channel handoff.

    The physical cell center/radius are checked as metadata.  Affine algebra
    always uses Forge's normalized generator ``e in [-1,1]``; the physical
    radius has already been absorbed into each serialized linear coefficient.
    """
    if document.get("schema") != "phase3-axial-global-channel-handoff-v1":
        raise ValueError("unexpected channel handoff schema")
    parent = document["parent_cell"]
    if parent != {
        "ell": 2,
        "mass_normalization": "M=1",
        "omega_parameter": "M*omega",
        "omega_interval": ["1/2", "129/256"],
        "center": "257/512",
        "radius": "1/512",
    }:
        raise ValueError("unexpected parent frequency cell")

    cursor = Fraction(parent["omega_interval"][0])
    upper = Fraction(parent["omega_interval"][1])
    results = {}
    unresolved = []
    for index, cell in enumerate(document["cells"]):
        if cell["cell_id"] != f"q{index}":
            raise ValueError("subcell ids are not ordered")
        lo, hi = map(Fraction, cell["omega_interval"])
        if lo != cursor or hi <= lo:
            raise ValueError("subcell cover has a gap, overlap, or reversal")
        if Fraction(cell["center"]) != (lo + hi) / 2:
            raise ValueError("subcell center is inconsistent")
        if Fraction(cell["radius"]) != (hi - lo) / 2:
            raise ValueError("subcell radius is inconsistent")
        if cell["affine_generator"] != 7315:
            raise ValueError("subcell affine generator changed")
        cursor = hi
        if cell["disposition"] != "CERTIFIED":
            unresolved.append(cell["cell_id"])
            continue
        payload = cell["validated_payload"]
        if payload is None or cell["shortfall"] is not None:
            raise ValueError("certified subcell has no clean payload")
        witness = payload["endpoint_forms"]["conservation"][
            "structural_identity_witness"
        ]
        expected_hash = hashlib.sha256(witness.encode("utf-8")).hexdigest()
        if (
            payload["endpoint_forms"]["conservation"]["witness_sha256"]
            != expected_hash
        ):
            raise ValueError("structural current witness hash mismatch")
        results[cell["cell_id"]] = _validate_payload_algebra(payload)
    if cursor != upper:
        raise ValueError("subcell cover does not reach the parent endpoint")

    state = document["parent_classification"]
    if state["exceptional_or_unresolved_cells"] != unresolved:
        raise ValueError("parent unresolved-cell ledger mismatch")
    all_resolved = not unresolved
    if state["all_cells_resolved"] != all_resolved:
        raise ValueError("parent resolved flag mismatch")
    if state["parent_rank_inertia_promoted"] != all_resolved:
        raise ValueError("parent classification promotion mismatch")
    expected_status = "CERTIFIED" if all_resolved else "SCOPED_SHORTFALL"
    if document["status"] != expected_status:
        raise ValueError("root handoff status mismatch")
    return {
        "parent_cell": parent,
        "normalized_affine_parameter": "e in [-1,1]",
        "certified_cells": results,
        "unresolved_cells": unresolved,
        "parent_promoted": all_resolved,
    }
