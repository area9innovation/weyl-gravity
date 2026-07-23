"""Sound adapter from shared degree-two transport data to affine handoffs.

The validated radial transports retain

    A(e) = A0 + A1 e + A2 e^2 + R(e),   |e| <= 1.

The existing channel-classification schema deliberately accepts only an
affine shared-parameter model.  This module performs the one admissible
loss of information at that boundary: ``A2 e^2`` is absorbed into an
outward interval remainder.  It never drops the quadratic coefficient or
pretends that ``e^2`` is an independent signed generator.

The transport solve is realified.  ``realified_to_complex_affine`` recovers
the complex matrix using the convention

    [[Re C, -Im C],
     [Im C,  Re C]].

If the independently enclosed duplicate blocks are not byte-identical, the
returned complex entry is an outer affine hull of both representations.
"""

from __future__ import annotations

from fractions import Fraction
import math
import struct
from typing import Iterable


def _fraction(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def _float_from_bits(bits: str) -> float:
    value = struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]
    if not math.isfinite(value):
        raise ValueError("nonfinite interval endpoint")
    return value


def _bits(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("nonfinite interval endpoint")
    return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def _outward_float(value: Fraction, *, lower: bool) -> float:
    """Return a finite binary64 endpoint on the requested side of ``value``."""

    candidate = float(value)
    if not math.isfinite(candidate):
        raise ValueError("rational endpoint overflows binary64")
    represented = Fraction.from_float(candidate)
    if lower:
        while represented > value:
            candidate = math.nextafter(candidate, -math.inf)
            represented = Fraction.from_float(candidate)
    else:
        while represented < value:
            candidate = math.nextafter(candidate, math.inf)
            represented = Fraction.from_float(candidate)
    return candidate


def _rational_string(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _interval_from_bits(pair: list[str]) -> tuple[Fraction, Fraction]:
    if len(pair) != 2:
        raise ValueError("interval must have two endpoints")
    lo = Fraction.from_float(_float_from_bits(pair[0]))
    hi = Fraction.from_float(_float_from_bits(pair[1]))
    if lo > hi:
        raise ValueError("reversed interval")
    return lo, hi


def _interval_bits(lo: Fraction, hi: Fraction) -> list[str]:
    if lo > hi:
        raise ValueError("reversed interval")
    return [
        _bits(_outward_float(lo, lower=True)),
        _bits(_outward_float(hi, lower=False)),
    ]


def flatten_taylor_scalar(
    c0: str | int | Fraction,
    c1: str | int | Fraction,
    c2: str | int | Fraction,
    remainder_bits: list[str],
) -> dict:
    """Enclose a scalar Taylor2 model by a shared affine model.

    Since ``e^2`` ranges over ``[0,1]``, a positive quadratic coefficient
    contributes ``[0,c2]`` and a negative one contributes ``[c2,0]``.
    The original outward interval is combined in exact rational arithmetic
    before new outward binary64 endpoints are chosen.
    """

    a0, a1, a2 = map(_fraction, (c0, c1, c2))
    lo, hi = _interval_from_bits(remainder_bits)
    qlo, qhi = min(Fraction(), a2), max(Fraction(), a2)
    return {
        "center": _rational_string(a0),
        "linear": _rational_string(a1),
        "remainder": _interval_bits(lo + qlo, hi + qhi),
    }


def flatten_taylor_matrix(
    document: dict, *, expected_generator: int = 7315
) -> list[list[dict]]:
    """Validate and flatten one serialized ``ivtaylor-degree2-v1`` matrix."""

    if document.get("schema") != "ivtaylor-degree2-v1":
        raise ValueError("wrong Taylor serialization schema")
    if document.get("degree") != 2 or document.get("refusal_code") != 0:
        raise ValueError("Taylor input is not an accepted degree-two model")
    if document.get("generator") != expected_generator:
        raise ValueError("Taylor input uses the wrong shared generator")
    rows, cols = document.get("rows"), document.get("cols")
    if not isinstance(rows, int) or not isinstance(cols, int):
        raise ValueError("Taylor shape is not integral")
    if rows <= 0 or cols <= 0:
        raise ValueError("Taylor matrix is empty")
    coefficients = document.get("coefficients")
    remainder = document.get("remainder_bits")
    if not isinstance(coefficients, list) or len(coefficients) != 3:
        raise ValueError("Taylor input needs exactly three coefficient matrices")

    def require_shape(matrix: list, name: str) -> None:
        if len(matrix) != rows or any(len(row) != cols for row in matrix):
            raise ValueError(f"{name} shape mismatch")

    for index, matrix in enumerate(coefficients):
        require_shape(matrix, f"coefficient {index}")
    require_shape(remainder, "remainder")
    return [
        [
            flatten_taylor_scalar(
                coefficients[0][i][j],
                coefficients[1][i][j],
                coefficients[2][i][j],
                remainder[i][j],
            )
            for j in range(cols)
        ]
        for i in range(rows)
    ]


def _negate_affine(value: dict) -> dict:
    lo, hi = _interval_from_bits(value["remainder"])
    return {
        "center": _rational_string(-_fraction(value["center"])),
        "linear": _rational_string(-_fraction(value["linear"])),
        "remainder": _interval_bits(-hi, -lo),
    }


def _affine_hull(values: Iterable[dict]) -> dict:
    """Outer-hull affine models while retaining one shared generator.

    The first center and linear coefficient are used as the canonical
    representative.  Differences in another representative are absorbed as
    ``delta_center + delta_linear*e`` over ``|e|<=1``.
    """

    values = list(values)
    if not values:
        raise ValueError("cannot hull an empty affine family")
    center = _fraction(values[0]["center"])
    linear = _fraction(values[0]["linear"])
    required: list[tuple[Fraction, Fraction]] = []
    for value in values:
        lo, hi = _interval_from_bits(value["remainder"])
        delta_center = _fraction(value["center"]) - center
        delta_linear = _fraction(value["linear"]) - linear
        spread = abs(delta_linear)
        required.append(
            (lo + delta_center - spread, hi + delta_center + spread)
        )
    return {
        "center": _rational_string(center),
        "linear": _rational_string(linear),
        "remainder": _interval_bits(
            min(lo for lo, _ in required),
            max(hi for _, hi in required),
        ),
    }


def realified_to_complex_affine(matrix: list[list[dict]]) -> list[list[dict]]:
    """Recover a complex affine matrix from a sound realified enclosure."""

    if not matrix or not matrix[0]:
        raise ValueError("empty realified matrix")
    row_count, col_count = len(matrix), len(matrix[0])
    if any(len(row) != col_count for row in matrix):
        raise ValueError("ragged realified matrix")
    if row_count % 2 or col_count % 2:
        raise ValueError("realified dimensions must both be even")
    rows, cols = row_count // 2, col_count // 2
    result: list[list[dict]] = []
    for i in range(rows):
        row = []
        for j in range(cols):
            real = _affine_hull((matrix[i][j], matrix[i + rows][j + cols]))
            imaginary = _affine_hull(
                (matrix[i + rows][j], _negate_affine(matrix[i][j + cols]))
            )
            row.append({"re": real, "im": imaginary})
        result.append(row)
    return result


def complex_to_realified_affine(matrix: list[list[dict]]) -> list[list[dict]]:
    """Serialize a complex affine matrix in the frozen handoff convention."""

    if not matrix or not matrix[0]:
        raise ValueError("empty complex matrix")
    rows, cols = len(matrix), len(matrix[0])
    if any(len(row) != cols for row in matrix):
        raise ValueError("ragged complex matrix")
    return [
        [
            (
                matrix[i][j]["re"]
                if i < rows and j < cols
                else _negate_affine(matrix[i][j - cols]["im"])
                if i < rows
                else matrix[i - rows][j]["im"]
                if j < cols
                else matrix[i - rows][j - cols]["re"]
            )
            for j in range(2 * cols)
        ]
        for i in range(2 * rows)
    ]
