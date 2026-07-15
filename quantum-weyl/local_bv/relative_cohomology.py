"""Exact sparse totalization and cohomology for finite local bicomplexes."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping, Sequence

from .algebra import canonical_sha256


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

    def _sparse_rref(self) -> tuple[list[dict[int, Fraction]], tuple[int, ...]]:
        """Return an exact sparse RREF without materializing zero entries."""

        rows = [{} for _ in range(self.row_count)]
        for (row, column), coefficient in self.entries.items():
            rows[row][column] = coefficient
        rows = [row for row in rows if row]
        pivot_row = 0
        pivots: list[int] = []
        for column in range(self.column_count):
            source = next(
                (
                    row_index
                    for row_index in range(pivot_row, len(rows))
                    if rows[row_index].get(column)
                ),
                None,
            )
            if source is None:
                continue
            rows[pivot_row], rows[source] = rows[source], rows[pivot_row]
            pivot = rows[pivot_row][column]
            rows[pivot_row] = {
                index: value / pivot
                for index, value in rows[pivot_row].items()
                if value
            }
            for row_index, row in enumerate(rows):
                if row_index == pivot_row or not row.get(column):
                    continue
                coefficient = row[column]
                reduced = dict(row)
                for index, pivot_value in rows[pivot_row].items():
                    value = reduced.get(index, Fraction()) - coefficient * pivot_value
                    if value:
                        reduced[index] = value
                    else:
                        reduced.pop(index, None)
                rows[row_index] = reduced
            pivots.append(column)
            pivot_row += 1
            if pivot_row == len(rows):
                break
        return rows[:pivot_row], tuple(pivots)

    def rank(self) -> int:
        return len(self._sparse_rref()[1])

    def nullspace(self) -> tuple[tuple[Fraction, ...], ...]:
        rref, pivots = self._sparse_rref()
        free_columns = tuple(
            column for column in range(self.column_count) if column not in pivots
        )
        basis: list[tuple[Fraction, ...]] = []
        for free in free_columns:
            vector = [Fraction() for _ in range(self.column_count)]
            vector[free] = Fraction(1)
            for row, pivot in zip(rref, pivots):
                vector[pivot] = -row.get(free, Fraction())
            basis.append(tuple(vector))
        return tuple(basis)

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


class _ExactRowSpace:
    """Incremental exact RREF used for deterministic independence tests."""

    def __init__(self, width: int) -> None:
        if width < 0:
            raise ValueError("row-space width must be nonnegative")
        self.width = width
        self.rows: dict[int, list[Fraction]] = {}

    @property
    def rank(self) -> int:
        return len(self.rows)

    def add(self, vector: Sequence[Fraction | int]) -> bool:
        if len(vector) != self.width:
            raise ValueError("row-space vector has the wrong dimension")
        row = list(map(Fraction, vector))
        for pivot in sorted(self.rows):
            coefficient = row[pivot]
            if coefficient:
                row = [
                    value - coefficient * pivot_value
                    for value, pivot_value in zip(row, self.rows[pivot])
                ]
        pivot = next((index for index, value in enumerate(row) if value), None)
        if pivot is None:
            return False
        coefficient = row[pivot]
        row = [value / coefficient for value in row]
        for existing_pivot, existing in list(self.rows.items()):
            coefficient = existing[pivot]
            if coefficient:
                self.rows[existing_pivot] = [
                    value - coefficient * pivot_value
                    for value, pivot_value in zip(existing, row)
                ]
        self.rows[pivot] = row
        return True


def _independent_extension(
    initial: Sequence[tuple[Fraction, ...]],
    candidates: Sequence[tuple[Fraction, ...]],
) -> tuple[tuple[Fraction, ...], ...]:
    vectors = [*initial, *candidates]
    if not vectors:
        return ()
    width = len(vectors[0])
    if any(len(vector) != width for vector in vectors):
        raise ValueError("independence candidates have inconsistent dimensions")
    row_space = _ExactRowSpace(width)
    for vector in initial:
        row_space.add(vector)
    additions: list[tuple[Fraction, ...]] = []
    for candidate in candidates:
        if row_space.add(candidate):
            additions.append(candidate)
    return tuple(additions)


def _pairing(
    left: Sequence[Fraction | int],
    right: Sequence[Fraction | int],
) -> Fraction:
    if len(left) != len(right):
        raise ValueError("pairing vectors have inconsistent dimensions")
    return sum(
        (Fraction(a) * Fraction(b) for a, b in zip(left, right)),
        Fraction(),
    )


def _dual_nontriviality_witness(
    boundaries: Sequence[tuple[Fraction, ...]],
    representative: tuple[Fraction, ...],
) -> tuple[Fraction, ...]:
    """Return ``lambda`` annihilating boundaries with ``lambda(rep)=1``.

    The witness lives in the algebraic dual of the ambient coordinate space.
    It is independently checkable without replaying quotient selection.
    """

    width = len(representative)
    if any(len(vector) != width for vector in boundaries):
        raise ValueError("boundary vectors have inconsistent dimensions")
    boundary_matrix = (
        SparseMatrix.from_dense(boundaries)
        if boundaries
        else SparseMatrix.zero(0, width)
    )
    for candidate in boundary_matrix.nullspace():
        value = _pairing(representative, candidate)
        if not value:
            continue
        witness = tuple(coefficient / value for coefficient in candidate)
        if boundary_matrix.apply(witness) != (Fraction(),) * len(boundaries):
            raise AssertionError("dual witness does not annihilate boundaries")
        if _pairing(representative, witness) != 1:
            raise AssertionError("dual witness normalization failed")
        return witness
    raise ValueError("representative lies in the supplied boundary space")


def _coordinates_payload(
    vectors: Sequence[Sequence[Fraction]],
) -> list[list[dict[str, int]]]:
    return [
        [
            {
                "numerator": value.numerator,
                "denominator": value.denominator,
            }
            for value in vector
        ]
        for vector in vectors
    ]


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

    def total_basis(
        self,
        total_degree: int,
        *,
        max_form_degree: int | None = None,
    ) -> tuple[tuple[Bidegree, int, str], ...]:
        if max_form_degree is not None and not 0 <= max_form_degree <= 4:
            raise ValueError("maximum form degree is outside 0,...,4")
        return tuple(
            (degree, index, label)
            for degree in sorted(
                (
                    item
                    for item in self.spaces
                    if item.total_degree == total_degree
                    and (
                        max_form_degree is None
                        or item.form_degree <= max_form_degree
                    )
                ),
                key=lambda item: (-item.form_degree, item.ghost_number),
            )
            for index, label in enumerate(self.spaces[degree])
        )

    def total_differential(
        self,
        total_degree: int,
        *,
        max_form_degree: int | None = None,
    ) -> SparseMatrix:
        source_basis = self.total_basis(
            total_degree, max_form_degree=max_form_degree
        )
        target_basis = self.total_basis(
            total_degree + 1, max_form_degree=max_form_degree
        )
        target_positions = {
            (degree, local_index): total_index
            for total_index, (degree, local_index, _) in enumerate(target_basis)
        }
        entries: dict[tuple[int, int], Fraction] = {}
        for source_index, (degree, local_column, _) in enumerate(source_basis):
            q_target = Bidegree(degree.ghost_number + 1, degree.form_degree)
            for (local_row, column), coefficient in self.q_map(degree).entries.items():
                if column == local_column:
                    target_key = (q_target, local_row)
                    if target_key not in target_positions:
                        continue
                    row = target_positions[target_key]
                    entries[(row, source_index)] = entries.get((row, source_index), Fraction()) + coefficient
            d_target = Bidegree(degree.ghost_number, degree.form_degree + 1)
            d_sign = -1 if degree.ghost_number % 2 else 1
            for (local_row, column), coefficient in self.d_map(degree).entries.items():
                if column == local_column:
                    target_key = (d_target, local_row)
                    if target_key not in target_positions:
                        continue
                    row = target_positions[target_key]
                    entries[(row, source_index)] = entries.get((row, source_index), Fraction()) + d_sign * coefficient
        return SparseMatrix(len(target_basis), len(source_basis), entries)

    def cohomology(
        self,
        total_degree: int,
        *,
        max_form_degree: int | None = None,
        basis_exhaustiveness_status: str = "TRUNCATED",
    ) -> dict[str, object]:
        if basis_exhaustiveness_status not in {"TRUNCATED", "EXHAUSTIVE"}:
            raise ValueError("unknown basis exhaustiveness status")
        self.verify_bicomplex()
        differential = self.total_differential(
            total_degree, max_form_degree=max_form_degree
        )
        previous = self.total_differential(
            total_degree - 1, max_form_degree=max_form_degree
        )
        next_differential = self.total_differential(
            total_degree + 1, max_form_degree=max_form_degree
        )
        if next_differential.compose(differential).entries:
            raise AssertionError("totalized differential is not nilpotent")
        cocycles = differential.nullspace()
        coboundaries = _independent_extension((), previous.columns())
        if any(differential.apply(vector) != (Fraction(),) * differential.row_count for vector in coboundaries):
            raise AssertionError("a total coboundary is not closed")
        representatives = _independent_extension(coboundaries, cocycles)
        quotient_dimension = len(representatives)
        dual_witnesses = tuple(
            _dual_nontriviality_witness(coboundaries, representative)
            for representative in representatives
        )
        basis_payload = [
            {
                "ghost_number": degree.ghost_number,
                "form_degree": degree.form_degree,
                "label": label,
            }
            for degree, _, label in self.total_basis(
                total_degree, max_form_degree=max_form_degree
            )
        ]
        representative_coordinates = _coordinates_payload(representatives)
        dual_witness_coordinates = _coordinates_payload(dual_witnesses)
        witness_type = (
            "COMPLETE_NONTRIVIALITY_WITNESS"
            if basis_exhaustiveness_status == "EXHAUSTIVE"
            else "TRUNCATED_NONMEMBERSHIP_WITNESS"
        )
        return {
            "total_degree": total_degree,
            "max_form_degree": max_form_degree,
            "ansatz_dimension": differential.column_count,
            "ansatz_basis_hash": canonical_sha256(basis_payload),
            "cocycle_matrix_rank": differential.rank(),
            "cocycle_dimension": len(cocycles),
            "coboundary_matrix_rank": len(coboundaries),
            "quotient_dimension": quotient_dimension,
            "representatives": representatives,
            "representative_coordinates": representative_coordinates,
            "basis_exhaustiveness_status": basis_exhaustiveness_status,
            "dual_witness_type": witness_type,
            "dual_nontriviality_witness_coordinates": dual_witness_coordinates,
            "dual_witness_pairings": [
                {
                    "numerator": _pairing(representative, witness).numerator,
                    "denominator": _pairing(representative, witness).denominator,
                }
                for representative, witness in zip(representatives, dual_witnesses)
            ],
            "proof_hash": canonical_sha256(
                {
                    "basis": basis_payload,
                    "differential": differential.canonical_payload(),
                    "previous": previous.canonical_payload(),
                    "representatives": representative_coordinates,
                    "dual_nontriviality_witnesses": dual_witness_coordinates,
                }
            ),
        }

    def relative_cohomology(
        self,
        ghost_number: int,
        form_degree: int,
        *,
        basis_exhaustiveness_status: str = "TRUNCATED",
    ) -> dict[str, object]:
        """Project complete total cocycles onto the requested top bidegree.

        The total complex is truncated to form degrees at most ``form_degree``.
        A relative class is the top component of a complete total cocycle,
        modulo top components of total coboundaries.  Total-cohomology classes
        with zero top component are counted separately and never promoted to
        ``H^{ghost_number,form_degree}(Q|d_h)``.
        """

        if basis_exhaustiveness_status not in {"TRUNCATED", "EXHAUSTIVE"}:
            raise ValueError("unknown basis exhaustiveness status")
        anchor = Bidegree(ghost_number, form_degree)
        if not 0 <= form_degree <= 4:
            raise ValueError("anchor form degree is outside 0,...,4")
        total_degree = anchor.total_degree
        total_basis = self.total_basis(
            total_degree, max_form_degree=form_degree
        )
        top_positions = tuple(
            index
            for index, (degree, _, _) in enumerate(total_basis)
            if degree == anchor
        )
        if len(top_positions) != self._dimension(anchor):
            raise AssertionError("anchored top basis does not match its space")

        differential = self.total_differential(
            total_degree, max_form_degree=form_degree
        )
        previous = self.total_differential(
            total_degree - 1, max_form_degree=form_degree
        )
        cocycle_lifts = differential.nullspace()
        coboundary_lifts = _independent_extension((), previous.columns())

        def top_component(
            vector: Sequence[Fraction | int],
        ) -> tuple[Fraction, ...]:
            return tuple(Fraction(vector[index]) for index in top_positions)

        top_cocycle_candidates = tuple(map(top_component, cocycle_lifts))
        top_cocycles = _independent_extension((), top_cocycle_candidates)
        top_coboundaries = _independent_extension(
            (), tuple(map(top_component, coboundary_lifts))
        )
        top_cocycle_space = _ExactRowSpace(self._dimension(anchor))
        for vector in top_cocycles:
            top_cocycle_space.add(vector)
        if any(top_cocycle_space.add(vector) for vector in top_coboundaries):
            raise AssertionError("a projected coboundary is not a projected cocycle")

        quotient_space = _ExactRowSpace(self._dimension(anchor))
        for vector in top_coboundaries:
            quotient_space.add(vector)
        relative_representatives: list[tuple[Fraction, ...]] = []
        descent_lifts: list[tuple[Fraction, ...]] = []
        for lift in cocycle_lifts:
            candidate = top_component(lift)
            if quotient_space.add(candidate):
                relative_representatives.append(candidate)
                descent_lifts.append(lift)

        dual_witnesses = tuple(
            _dual_nontriviality_witness(top_coboundaries, representative)
            for representative in relative_representatives
        )

        total = self.cohomology(
            total_degree,
            max_form_degree=form_degree,
            basis_exhaustiveness_status=basis_exhaustiveness_status,
        )
        quotient_dimension = len(relative_representatives)
        lower_only_dimension = total["quotient_dimension"] - quotient_dimension
        if lower_only_dimension < 0:
            raise AssertionError("anchored quotient exceeds total cohomology")

        top_basis_payload = [
            {
                "ghost_number": degree.ghost_number,
                "form_degree": degree.form_degree,
                "label": label,
            }
            for degree, _, label in total_basis
            if degree == anchor
        ]

        representative_payload = _coordinates_payload(relative_representatives)
        lift_payload = _coordinates_payload(descent_lifts)
        dual_witness_payload = _coordinates_payload(dual_witnesses)
        witness_type = (
            "COMPLETE_NONTRIVIALITY_WITNESS"
            if basis_exhaustiveness_status == "EXHAUSTIVE"
            else "TRUNCATED_NONMEMBERSHIP_WITNESS"
        )
        return {
            "ghost_number": ghost_number,
            "form_degree": form_degree,
            "total_degree": total_degree,
            "descent_completion_status": "COMPLETE_WITHIN_SUPPLIED_BICOMPLEX",
            "basis_exhaustiveness_status": basis_exhaustiveness_status,
            "top_ansatz_dimension": self._dimension(anchor),
            "top_ansatz_basis_hash": canonical_sha256(top_basis_payload),
            "complete_total_cocycle_dimension": len(cocycle_lifts),
            "projected_top_cocycle_dimension": len(top_cocycles),
            "projected_top_coboundary_rank": len(top_coboundaries),
            "quotient_dimension": quotient_dimension,
            "lower_only_total_class_dimension": lower_only_dimension,
            "representative_coordinates": representative_payload,
            "complete_descent_lift_coordinates": lift_payload,
            "closure_witnesses": [
                {
                    "total_basis_hash": total["ansatz_basis_hash"],
                    "complete_descent_lift_coordinates": lift,
                    "residual_status": "ZERO",
                }
                for lift in lift_payload
            ],
            "dual_witness_type": witness_type,
            "dual_nontriviality_witness_coordinates": dual_witness_payload,
            "dual_witness_pairings": [
                {
                    "numerator": _pairing(representative, witness).numerator,
                    "denominator": _pairing(representative, witness).denominator,
                }
                for representative, witness in zip(
                    relative_representatives, dual_witnesses
                )
            ],
            "proof_hash": canonical_sha256(
                {
                    "anchor": {
                        "ghost_number": ghost_number,
                        "form_degree": form_degree,
                    },
                    "basis_exhaustiveness_status": basis_exhaustiveness_status,
                    "top_basis": top_basis_payload,
                    "total_basis_hash": total["ansatz_basis_hash"],
                    "top_cocycles": _coordinates_payload(top_cocycles),
                    "top_coboundaries": _coordinates_payload(top_coboundaries),
                    "representatives": representative_payload,
                    "lifts": lift_payload,
                    "dual_nontriviality_witnesses": dual_witness_payload,
                }
            ),
        }


def certification_bicomplex() -> FiniteBicomplex:
    """Return a commuting square plus one isolated total-cohomology class."""

    spaces = {
        Bidegree(0, 0): ("x",),
        Bidegree(1, 0): ("Qx", "lower_only_class"),
        Bidegree(0, 1): ("dx", "c"),
        Bidegree(1, 1): ("Qdx",),
    }
    q_maps = {
        Bidegree(0, 0): SparseMatrix.from_dense(((1,), (0,))),
        Bidegree(0, 1): SparseMatrix.from_dense(((1, 0),)),
    }
    d_maps = {
        Bidegree(0, 0): SparseMatrix.from_dense(((1,), (0,))),
        Bidegree(1, 0): SparseMatrix.from_dense(((1, 0),)),
    }
    return FiniteBicomplex(spaces, q_maps, d_maps)
