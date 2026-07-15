"""Exact first-order Cartan-defect and endomorphism-cohomology engine.

The quantum Cartan defect has cohomological degree zero:

    A_D^(1) = [Q, iota_1] + [Q_1, iota_D] - L_D^(1).

When ``Q^2 = 0``, ``[Q,Q_1] = 0``, the classical Cartan identity holds, and
the first-order Ward compatibility condition holds, the graded Jacobi
identity gives ``[Q,A_D^(1)] = 0``.  The primary obstruction therefore lives
in degree-zero cohomology of the declared admissible operator complex.  This
module implements that finite exact calculation over the rationals.  It does
not choose the physical observable algebra or assert that a finite fixture is
the local pure-Weyl BV complex.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence


Scalar = Fraction


def _fraction(value: int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


@dataclass(frozen=True)
class ExactMatrix:
    """Small immutable rational matrix used by the certificate fixtures."""

    rows: tuple[tuple[Scalar, ...], ...]

    def __post_init__(self) -> None:
        if not self.rows:
            raise ValueError("an exact matrix must have at least one row")
        width = len(self.rows[0])
        if width == 0 or any(len(row) != width for row in self.rows):
            raise ValueError("an exact matrix must be nonempty and rectangular")
        object.__setattr__(
            self,
            "rows",
            tuple(tuple(_fraction(value) for value in row) for row in self.rows),
        )

    @classmethod
    def from_rows(
        cls, rows: Sequence[Sequence[int | Fraction]]
    ) -> "ExactMatrix":
        return cls(tuple(tuple(_fraction(value) for value in row) for row in rows))

    @classmethod
    def zero(cls, rows: int, columns: int) -> "ExactMatrix":
        if rows < 1 or columns < 1:
            raise ValueError("matrix dimensions must be positive")
        return cls(tuple(tuple(Fraction(0) for _ in range(columns)) for _ in range(rows)))

    @classmethod
    def identity(cls, dimension: int) -> "ExactMatrix":
        return cls(
            tuple(
                tuple(Fraction(int(row == column)) for column in range(dimension))
                for row in range(dimension)
            )
        )

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.rows), len(self.rows[0])

    def __getitem__(self, index: tuple[int, int]) -> Fraction:
        row, column = index
        return self.rows[row][column]

    def __add__(self, other: "ExactMatrix") -> "ExactMatrix":
        self._require_same_shape(other)
        return ExactMatrix(
            tuple(
                tuple(left + right for left, right in zip(left_row, right_row))
                for left_row, right_row in zip(self.rows, other.rows)
            )
        )

    def __sub__(self, other: "ExactMatrix") -> "ExactMatrix":
        self._require_same_shape(other)
        return ExactMatrix(
            tuple(
                tuple(left - right for left, right in zip(left_row, right_row))
                for left_row, right_row in zip(self.rows, other.rows)
            )
        )

    def __neg__(self) -> "ExactMatrix":
        return self.scale(-1)

    def scale(self, scalar: int | Fraction) -> "ExactMatrix":
        coefficient = _fraction(scalar)
        return ExactMatrix(
            tuple(tuple(coefficient * value for value in row) for row in self.rows)
        )

    def __matmul__(self, other: "ExactMatrix") -> "ExactMatrix":
        left_rows, left_columns = self.shape
        right_rows, right_columns = other.shape
        if left_columns != right_rows:
            raise ValueError("matrix dimensions do not compose")
        return ExactMatrix(
            tuple(
                tuple(
                    sum(
                        (self.rows[row][middle] * other.rows[middle][column]
                         for middle in range(left_columns)),
                        Fraction(0),
                    )
                    for column in range(right_columns)
                )
                for row in range(left_rows)
            )
        )

    def _require_same_shape(self, other: "ExactMatrix") -> None:
        if self.shape != other.shape:
            raise ValueError("matrix dimensions differ")

    def is_zero(self) -> bool:
        return all(value == 0 for row in self.rows for value in row)


@dataclass(frozen=True)
class HomogeneousOperator:
    """A homogeneous endomorphism with an explicit cohomological degree."""

    name: str
    degree: int
    matrix: ExactMatrix

    def scaled(self, scalar: int | Fraction, *, name: str | None = None) -> "HomogeneousOperator":
        return HomogeneousOperator(name or self.name, self.degree, self.matrix.scale(scalar))


def graded_commutator(
    left: HomogeneousOperator,
    right: HomogeneousOperator,
    *,
    name: str | None = None,
) -> HomogeneousOperator:
    """Return ``left right - (-1)^(|left||right|) right left`` exactly."""

    sign = -1 if (left.degree * right.degree) % 2 else 1
    matrix = (left.matrix @ right.matrix) - (right.matrix @ left.matrix).scale(sign)
    return HomogeneousOperator(
        name or f"[{left.name},{right.name}]",
        left.degree + right.degree,
        matrix,
    )


def add_operators(
    *operators: HomogeneousOperator,
    name: str,
) -> HomogeneousOperator:
    if not operators:
        raise ValueError("at least one operator is required")
    degree = operators[0].degree
    if any(operator.degree != degree for operator in operators):
        raise ValueError("only operators of equal degree may be added")
    matrix = operators[0].matrix
    for operator in operators[1:]:
        matrix = matrix + operator.matrix
    return HomogeneousOperator(name, degree, matrix)


def _rref_solve(
    rows: Sequence[Sequence[Fraction]],
    rhs: Sequence[Fraction],
    variable_count: int,
) -> tuple[Fraction, ...] | None:
    """Solve an exact linear system, choosing zero for every free variable."""

    if len(rows) != len(rhs):
        raise ValueError("row and right-hand-side counts differ")
    augmented = [list(row) + [value] for row, value in zip(rows, rhs)]
    if any(len(row) != variable_count + 1 for row in augmented):
        raise ValueError("linear-system width differs from variable count")
    pivot_row = 0
    pivots: list[int] = []
    for column in range(variable_count):
        selected = next(
            (row for row in range(pivot_row, len(augmented)) if augmented[row][column]),
            None,
        )
        if selected is None:
            continue
        augmented[pivot_row], augmented[selected] = augmented[selected], augmented[pivot_row]
        pivot = augmented[pivot_row][column]
        augmented[pivot_row] = [value / pivot for value in augmented[pivot_row]]
        for row in range(len(augmented)):
            if row == pivot_row or not augmented[row][column]:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(augmented):
            break
    for row in augmented:
        if all(value == 0 for value in row[:variable_count]) and row[-1] != 0:
            return None
    solution = [Fraction(0) for _ in range(variable_count)]
    for row, column in enumerate(pivots):
        solution[column] = augmented[row][-1]
    return tuple(solution)


def _matrix_rank(rows: Sequence[Sequence[Fraction]], variable_count: int) -> int:
    if not rows:
        return 0
    augmented = [list(row) for row in rows]
    rank = 0
    for column in range(variable_count):
        selected = next(
            (row for row in range(rank, len(augmented)) if augmented[row][column]),
            None,
        )
        if selected is None:
            continue
        augmented[rank], augmented[selected] = augmented[selected], augmented[rank]
        pivot = augmented[rank][column]
        augmented[rank] = [value / pivot for value in augmented[rank]]
        for row in range(len(augmented)):
            if row == rank or not augmented[row][column]:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[rank])
            ]
        rank += 1
        if rank == len(augmented):
            break
    return rank


@dataclass(frozen=True)
class FiniteGradedComplex:
    """A finite graded complex and its homogeneous endomorphism complex."""

    basis_degrees: tuple[int, ...]
    q: HomogeneousOperator

    def __post_init__(self) -> None:
        dimension = len(self.basis_degrees)
        if dimension == 0:
            raise ValueError("a graded complex needs at least one basis element")
        if self.q.degree != 1 or self.q.matrix.shape != (dimension, dimension):
            raise ValueError("Q must be a degree-one square operator")
        self.validate_operator(self.q)
        if not (self.q.matrix @ self.q.matrix).is_zero():
            raise ValueError("Q is not nilpotent")

    @property
    def dimension(self) -> int:
        return len(self.basis_degrees)

    def validate_operator(self, operator: HomogeneousOperator) -> None:
        if operator.matrix.shape != (self.dimension, self.dimension):
            raise ValueError(f"{operator.name} has the wrong matrix shape")
        for target in range(self.dimension):
            for source in range(self.dimension):
                if operator.matrix[target, source] == 0:
                    continue
                if self.basis_degrees[target] - self.basis_degrees[source] != operator.degree:
                    raise ValueError(
                        f"{operator.name} has a nonhomogeneous entry at {(target, source)}"
                    )

    def endomorphism_pairs(self, degree: int) -> tuple[tuple[int, int], ...]:
        return tuple(
            (target, source)
            for target in range(self.dimension)
            for source in range(self.dimension)
            if self.basis_degrees[target] - self.basis_degrees[source] == degree
        )

    def coordinates(self, operator: HomogeneousOperator) -> tuple[Fraction, ...]:
        self.validate_operator(operator)
        return tuple(operator.matrix[target, source] for target, source in self.endomorphism_pairs(operator.degree))

    def operator_from_coordinates(
        self,
        degree: int,
        coordinates: Sequence[Fraction],
        *,
        name: str,
    ) -> HomogeneousOperator:
        pairs = self.endomorphism_pairs(degree)
        if len(coordinates) != len(pairs):
            raise ValueError("coordinate count does not match the homogeneous operator space")
        rows = [[Fraction(0) for _ in range(self.dimension)] for _ in range(self.dimension)]
        for (target, source), value in zip(pairs, coordinates):
            rows[target][source] = value
        return HomogeneousOperator(name, degree, ExactMatrix.from_rows(rows))

    def endomorphism_differential_columns(
        self, degree: int
    ) -> tuple[tuple[Fraction, ...], ...]:
        columns = []
        source_pairs = self.endomorphism_pairs(degree)
        for index, _pair in enumerate(source_pairs):
            coordinates = [Fraction(0) for _ in source_pairs]
            coordinates[index] = Fraction(1)
            basis_operator = self.operator_from_coordinates(
                degree, coordinates, name=f"E_{degree}_{index}"
            )
            image = graded_commutator(self.q, basis_operator, name="delta_End")
            columns.append(self.coordinates(image))
        return tuple(columns)

    def differential_rank(self, degree: int) -> int:
        columns = self.endomorphism_differential_columns(degree)
        row_count = len(self.endomorphism_pairs(degree + 1))
        rows = tuple(
            tuple(column[row] for column in columns)
            for row in range(row_count)
        )
        return _matrix_rank(rows, len(columns))

    def cohomology_dimension(self, degree: int) -> int:
        space_dimension = len(self.endomorphism_pairs(degree))
        outgoing_rank = self.differential_rank(degree)
        incoming_rank = self.differential_rank(degree - 1)
        return space_dimension - outgoing_rank - incoming_rank

    def solve_boundary(
        self, cocycle: HomogeneousOperator
    ) -> HomogeneousOperator | None:
        self.validate_operator(cocycle)
        degree = cocycle.degree
        columns = self.endomorphism_differential_columns(degree - 1)
        target_coordinates = self.coordinates(cocycle)
        rows = tuple(
            tuple(column[row] for column in columns)
            for row in range(len(target_coordinates))
        )
        solution = _rref_solve(rows, target_coordinates, len(columns))
        if solution is None:
            return None
        primitive = self.operator_from_coordinates(
            degree - 1, solution, name=f"primitive_for_{cocycle.name}"
        )
        if graded_commutator(self.q, primitive).matrix != cocycle.matrix:
            raise AssertionError("the exact boundary solver returned an invalid primitive")
        return primitive

    def dual_nontriviality_witness(
        self, cocycle: HomogeneousOperator
    ) -> tuple[Fraction, ...]:
        """Return lambda with lambda(boundaries)=0 and lambda(cocycle)=1."""

        degree = cocycle.degree
        boundary_columns = self.endomorphism_differential_columns(degree - 1)
        cocycle_coordinates = self.coordinates(cocycle)
        equations = [tuple(column) for column in boundary_columns]
        equations.append(tuple(cocycle_coordinates))
        rhs = [Fraction(0) for _ in boundary_columns] + [Fraction(1)]
        witness = _rref_solve(equations, rhs, len(cocycle_coordinates))
        if witness is None:
            raise ValueError("no normalized dual nontriviality witness exists")
        if any(
            sum((left * right for left, right in zip(witness, column)), Fraction(0))
            for column in boundary_columns
        ):
            raise AssertionError("dual witness does not annihilate every boundary")
        normalization = sum(
            (left * right for left, right in zip(witness, cocycle_coordinates)),
            Fraction(0),
        )
        if normalization != 1:
            raise AssertionError("dual witness is not normalized")
        return witness


@dataclass(frozen=True)
class FirstOrderCartanData:
    """The complete first-order data entering the quantum Cartan defect."""

    complex: FiniteGradedComplex
    iota_0: HomogeneousOperator
    lie_0: HomogeneousOperator
    q_1: HomogeneousOperator
    iota_1: HomogeneousOperator
    lie_1: HomogeneousOperator

    def __post_init__(self) -> None:
        expected_degrees = {
            "iota_0": -1,
            "lie_0": 0,
            "q_1": 1,
            "iota_1": -1,
            "lie_1": 0,
        }
        for field, degree in expected_degrees.items():
            operator = getattr(self, field)
            if operator.degree != degree:
                raise ValueError(f"{field} must have degree {degree}")
            self.complex.validate_operator(operator)

    def defect(self) -> HomogeneousOperator:
        return add_operators(
            graded_commutator(self.complex.q, self.iota_1, name="[Q,iota_1]"),
            graded_commutator(self.q_1, self.iota_0, name="[Q_1,iota_D]"),
            self.lie_1.scaled(-1, name="-L_D_1"),
            name="A_D_1",
        )

    def checks(self) -> dict[str, bool]:
        q = self.complex.q
        q1_q = graded_commutator(q, self.q_1, name="[Q,Q_1]")
        classical_cartan = graded_commutator(q, self.iota_0, name="[Q,iota_D]")
        ward_first_order = add_operators(
            graded_commutator(q, self.lie_1, name="[Q,L_D_1]"),
            graded_commutator(self.q_1, self.lie_0, name="[Q_1,L_D]"),
            name="ward_first_order",
        )
        consistency = graded_commutator(q, self.defect(), name="[Q,A_D_1]")
        return {
            "Q_squared_zero": (q.matrix @ q.matrix).is_zero(),
            "classical_Cartan_identity": classical_cartan.matrix == self.lie_0.matrix,
            "first_order_QME_linearization": q1_q.matrix.is_zero(),
            "first_order_Ward_compatibility": ward_first_order.matrix.is_zero(),
            "defect_has_degree_zero": self.defect().degree == 0,
            "defect_consistency_Q_closed": consistency.matrix.is_zero(),
        }


@dataclass(frozen=True)
class DefectClassification:
    status: str
    defect: HomogeneousOperator
    primitive: HomogeneousOperator | None
    dual_witness: tuple[Fraction, ...] | None


def classify_closed_defect(
    complex_: FiniteGradedComplex,
    defect: HomogeneousOperator,
) -> DefectClassification:
    """Classify a closed defect in the declared finite operator complex."""

    complex_.validate_operator(defect)
    if defect.degree != 0:
        raise ValueError("a Cartan defect must have degree zero")
    if not graded_commutator(complex_.q, defect).matrix.is_zero():
        raise ValueError("the proposed defect is not Q-closed")
    if defect.matrix.is_zero():
        return DefectClassification("ZERO", defect, None, None)
    primitive = complex_.solve_boundary(defect)
    if primitive is not None:
        return DefectClassification("EXACT_REMOVABLE", defect, primitive, None)
    witness = complex_.dual_nontriviality_witness(defect)
    return DefectClassification("NONTRIVIAL_ANOMALY", defect, None, witness)


def exact_vector(values: Iterable[int | Fraction]) -> tuple[Fraction, ...]:
    """Public convenience constructor used by tests and fixtures."""

    return tuple(_fraction(value) for value in values)
