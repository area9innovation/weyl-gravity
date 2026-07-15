"""Exact sparse totalization and cohomology for finite local bicomplexes."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping, Sequence

from .algebra import canonical_sha256
from .quotient import exact_nullspace, exact_rank


@dataclass(frozen=True, order=True)
class Bidegree:
    ghost_number: int
    form_degree: int

    @property
    def total_degree(self) -> int:
        return self.ghost_number + self.form_degree


@dataclass(frozen=True)
class SparseMatrix:
    """An exact row-by-column sparse matrix."""

    row_count: int
    column_count: int
    entries: Mapping[tuple[int, int], Fraction]

    def __post_init__(self) -> None:
        if self.row_count < 0 or self.column_count < 0:
            raise ValueError("matrix dimensions must be nonnegative")
        normalized: dict[tuple[int, int], Fraction] = {}
        for (row, column), value in self.entries.items():
            if not 0 <= row < self.row_count or not 0 <= column < self.column_count:
                raise ValueError("sparse matrix entry is outside its dimensions")
            coefficient = Fraction(value)
            if coefficient:
                normalized[(row, column)] = coefficient
        object.__setattr__(self, "entries", normalized)

    @classmethod
    def zero(cls, row_count: int, column_count: int) -> "SparseMatrix":
        return cls(row_count, column_count, {})

    @classmethod
    def from_dense(cls, rows: Sequence[Sequence[Fraction | int]]) -> "SparseMatrix":
        if not rows:
            raise ValueError("use SparseMatrix.zero when the row count is zero")
        width = len(rows[0])
        if any(len(row) != width for row in rows):
            raise ValueError("matrix is ragged")
        return cls(
            len(rows),
            width,
            {
                (row_index, column_index): Fraction(value)
                for row_index, row in enumerate(rows)
                for column_index, value in enumerate(row)
                if value
            },
        )

    def dense_rows(self) -> tuple[tuple[Fraction, ...], ...]:
        return tuple(
            tuple(
                self.entries.get((row, column), Fraction())
                for column in range(self.column_count)
            )
            for row in range(self.row_count)
        )

    def apply(self, vector: Sequence[Fraction | int]) -> tuple[Fraction, ...]:
        if len(vector) != self.column_count:
            raise ValueError("vector has the wrong source dimension")
        result = [Fraction() for _ in range(self.row_count)]
        for (row, column), coefficient in self.entries.items():
            result[row] += coefficient * Fraction(vector[column])
        return tuple(result)

    def compose(self, right: "SparseMatrix") -> "SparseMatrix":
        """Return ``self o right``."""

        if right.row_count != self.column_count:
            raise ValueError("matrix composition dimensions disagree")
        by_middle: dict[int, list[tuple[int, Fraction]]] = {}
        for (row, middle), coefficient in self.entries.items():
            by_middle.setdefault(middle, []).append((row, coefficient))
        result: dict[tuple[int, int], Fraction] = {}
        for (middle, column), right_coefficient in right.entries.items():
            for row, left_coefficient in by_middle.get(middle, ()):
                key = (row, column)
                result[key] = result.get(key, Fraction()) + left_coefficient * right_coefficient
        return SparseMatrix(self.row_count, right.column_count, result)

    def __add__(self, other: "SparseMatrix") -> "SparseMatrix":
        if (self.row_count, self.column_count) != (other.row_count, other.column_count):
            raise ValueError("matrix sum dimensions disagree")
        entries = dict(self.entries)
        for key, coefficient in other.entries.items():
            entries[key] = entries.get(key, Fraction()) + coefficient
        return SparseMatrix(self.row_count, self.column_count, entries)

    def scale(self, coefficient: Fraction | int) -> "SparseMatrix":
        return SparseMatrix(
            self.row_count,
            self.column_count,
            {key: Fraction(coefficient) * value for key, value in self.entries.items()},
        )

    def columns(self) -> tuple[tuple[Fraction, ...], ...]:
        return tuple(
            tuple(
                self.entries.get((row, column), Fraction())
                for row in range(self.row_count)
            )
            for column in range(self.column_count)
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "entries": [
                {
                    "row": row,
                    "column": column,
                    "coefficient": {
                        "numerator": coefficient.numerator,
                        "denominator": coefficient.denominator,
                    },
                }
                for (row, column), coefficient in sorted(self.entries.items())
            ],
        }


def _independent_extension(
    initial: Sequence[tuple[Fraction, ...]],
    candidates: Sequence[tuple[Fraction, ...]],
) -> tuple[tuple[Fraction, ...], ...]:
    selected = list(initial)
    rank = exact_rank(selected) if selected else 0
    additions: list[tuple[Fraction, ...]] = []
    for candidate in candidates:
        new_rank = exact_rank([*selected, candidate])
        if new_rank > rank:
            selected.append(candidate)
            additions.append(candidate)
            rank = new_rank
    return tuple(additions)


class FiniteBicomplex:
    """Finite exact bicomplex with coordinate ``Q d_h = d_h Q`` convention."""

    def __init__(
        self,
        spaces: Mapping[Bidegree, Sequence[str]],
        q_maps: Mapping[Bidegree, SparseMatrix],
        d_maps: Mapping[Bidegree, SparseMatrix],
    ) -> None:
        self.spaces = {
            degree: tuple(labels)
            for degree, labels in spaces.items()
            if labels
        }
        for degree, labels in self.spaces.items():
            if not 0 <= degree.form_degree <= 4:
                raise ValueError("form degree is outside 0,...,4")
            if len(labels) != len(set(labels)):
                raise ValueError(f"duplicate basis label in {degree}")
        self.q_maps = dict(q_maps)
        self.d_maps = dict(d_maps)
        self._validate_map_shapes()

    def _dimension(self, degree: Bidegree) -> int:
        return len(self.spaces.get(degree, ()))

    def _zero_map(self, source: Bidegree, target: Bidegree) -> SparseMatrix:
        return SparseMatrix.zero(self._dimension(target), self._dimension(source))

    def q_map(self, source: Bidegree) -> SparseMatrix:
        target = Bidegree(source.ghost_number + 1, source.form_degree)
        return self.q_maps.get(source, self._zero_map(source, target))

    def d_map(self, source: Bidegree) -> SparseMatrix:
        target = Bidegree(source.ghost_number, source.form_degree + 1)
        return self.d_maps.get(source, self._zero_map(source, target))

    def _validate_map_shapes(self) -> None:
        for source, matrix in self.q_maps.items():
            target = Bidegree(source.ghost_number + 1, source.form_degree)
            if (matrix.row_count, matrix.column_count) != (
                self._dimension(target),
                self._dimension(source),
            ):
                raise ValueError(f"Q map shape disagrees at {source}")
        for source, matrix in self.d_maps.items():
            target = Bidegree(source.ghost_number, source.form_degree + 1)
            if (matrix.row_count, matrix.column_count) != (
                self._dimension(target),
                self._dimension(source),
            ):
                raise ValueError(f"d_h map shape disagrees at {source}")

    def verify_bicomplex(self) -> dict[str, str]:
        for source in self.spaces:
            q_target = Bidegree(source.ghost_number + 1, source.form_degree)
            d_target = Bidegree(source.ghost_number, source.form_degree + 1)
            if self.q_map(q_target).compose(self.q_map(source)).entries:
                raise ValueError(f"Q^2 != 0 at {source}")
            if self.d_map(d_target).compose(self.d_map(source)).entries:
                raise ValueError(f"d_h^2 != 0 at {source}")
            q_then_d = self.d_map(q_target).compose(self.q_map(source))
            d_then_q = self.q_map(d_target).compose(self.d_map(source))
            if q_then_d.entries != d_then_q.entries:
                raise ValueError(f"coordinate Q and d_h do not commute at {source}")
        return {
            "Q_squared_zero": "VERIFIED",
            "d_h_squared_zero": "VERIFIED",
            "coordinate_Q_dh_commutator_zero": "VERIFIED",
            "totalized_differential_squared_zero": "VERIFIED",
        }

    def total_basis(self, total_degree: int) -> tuple[tuple[Bidegree, int, str], ...]:
        return tuple(
            (degree, index, label)
            for degree in sorted(
                (item for item in self.spaces if item.total_degree == total_degree),
                key=lambda item: (-item.form_degree, item.ghost_number),
            )
            for index, label in enumerate(self.spaces[degree])
        )

    def total_differential(self, total_degree: int) -> SparseMatrix:
        source_basis = self.total_basis(total_degree)
        target_basis = self.total_basis(total_degree + 1)
        target_positions = {
            (degree, local_index): total_index
            for total_index, (degree, local_index, _) in enumerate(target_basis)
        }
        entries: dict[tuple[int, int], Fraction] = {}
        for source_index, (degree, local_column, _) in enumerate(source_basis):
            q_target = Bidegree(degree.ghost_number + 1, degree.form_degree)
            for (local_row, column), coefficient in self.q_map(degree).entries.items():
                if column == local_column:
                    row = target_positions[(q_target, local_row)]
                    entries[(row, source_index)] = entries.get((row, source_index), Fraction()) + coefficient
            d_target = Bidegree(degree.ghost_number, degree.form_degree + 1)
            d_sign = -1 if degree.ghost_number % 2 else 1
            for (local_row, column), coefficient in self.d_map(degree).entries.items():
                if column == local_column:
                    row = target_positions[(d_target, local_row)]
                    entries[(row, source_index)] = entries.get((row, source_index), Fraction()) + d_sign * coefficient
        return SparseMatrix(len(target_basis), len(source_basis), entries)

    def cohomology(self, total_degree: int) -> dict[str, object]:
        self.verify_bicomplex()
        differential = self.total_differential(total_degree)
        previous = self.total_differential(total_degree - 1)
        next_differential = self.total_differential(total_degree + 1)
        if next_differential.compose(differential).entries:
            raise AssertionError("totalized differential is not nilpotent")
        cocycles = exact_nullspace(
            differential.dense_rows(),
            column_count=differential.column_count,
        )
        coboundaries = _independent_extension((), previous.columns())
        if any(differential.apply(vector) != (Fraction(),) * differential.row_count for vector in coboundaries):
            raise AssertionError("a total coboundary is not closed")
        representatives = _independent_extension(coboundaries, cocycles)
        quotient_dimension = len(representatives)
        basis_payload = [
            {
                "ghost_number": degree.ghost_number,
                "form_degree": degree.form_degree,
                "label": label,
            }
            for degree, _, label in self.total_basis(total_degree)
        ]
        representative_coordinates = [
            [
                {"numerator": value.numerator, "denominator": value.denominator}
                for value in representative
            ]
            for representative in representatives
        ]
        return {
            "total_degree": total_degree,
            "ansatz_dimension": differential.column_count,
            "ansatz_basis_hash": canonical_sha256(basis_payload),
            "cocycle_matrix_rank": exact_rank(differential.dense_rows()),
            "cocycle_dimension": len(cocycles),
            "coboundary_matrix_rank": len(coboundaries),
            "quotient_dimension": quotient_dimension,
            "representatives": representatives,
            "representative_coordinates": representative_coordinates,
            "proof_hash": canonical_sha256(
                {
                    "basis": basis_payload,
                    "differential": differential.canonical_payload(),
                    "previous": previous.canonical_payload(),
                    "representatives": representative_coordinates,
                }
            ),
        }


def certification_bicomplex() -> FiniteBicomplex:
    """Return a commuting square plus one isolated total-cohomology class."""

    spaces = {
        Bidegree(0, 0): ("x",),
        Bidegree(1, 0): ("Qx",),
        Bidegree(0, 1): ("dx", "c"),
        Bidegree(1, 1): ("Qdx",),
    }
    q_maps = {
        Bidegree(0, 0): SparseMatrix.from_dense(((1,),)),
        Bidegree(0, 1): SparseMatrix.from_dense(((1, 0),)),
    }
    d_maps = {
        Bidegree(0, 0): SparseMatrix.from_dense(((1,), (0,))),
        Bidegree(1, 0): SparseMatrix.from_dense(((1,),)),
    }
    return FiniteBicomplex(spaces, q_maps, d_maps)
