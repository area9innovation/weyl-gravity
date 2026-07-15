"""Exact arity-two Cartan-defect and correction engine.

For a degree-one linear differential ``q1``, degree-one symmetric Taylor
coefficient ``q2``, degree-minus-one linear Cartan homotopy ``iota_D``, and
linear degree-zero action ``L_D``, the arity-two Cartan source is

    A_D^(2) = [q2, iota_D] - L_D^(2).

The correction equation is

    [q1, iota_D^(2)] = -A_D^(2).

This module constructs the exact rational complex of graded-symmetric
bilinear maps, checks the consistency source ``[L_D,q2]``, and either returns
an explicit correction or a normalized dual obstruction witness.  It is a
finite algebraic engine; fixtures are not a conformal-gravity coefficient
claim and do not replace the missing support-local classical export.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Sequence


Scalar = Fraction


def _fraction(value: int | Fraction) -> Fraction:
    if isinstance(value, bool):
        raise ValueError("boolean values are not exact scalar coefficients")
    return value if isinstance(value, Fraction) else Fraction(value)


def _zero_linear(dimension: int) -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]


def _zero_bilinear(dimension: int) -> list[list[list[Fraction]]]:
    return [
        [
            [Fraction(0) for _ in range(dimension)]
            for _ in range(dimension)
        ]
        for _ in range(dimension)
    ]


@dataclass(frozen=True)
class LinearOperator:
    """A homogeneous exact linear operator in output-input convention."""

    name: str
    degree: int
    entries: tuple[tuple[Scalar, ...], ...]

    def __post_init__(self) -> None:
        if not self.entries or not self.entries[0]:
            raise ValueError("a linear operator must be nonempty")
        width = len(self.entries[0])
        if len(self.entries) != width or any(len(row) != width for row in self.entries):
            raise ValueError("a linear operator must be square")
        object.__setattr__(
            self,
            "entries",
            tuple(tuple(_fraction(value) for value in row) for row in self.entries),
        )

    @classmethod
    def from_rows(
        cls,
        name: str,
        degree: int,
        rows: Sequence[Sequence[int | Fraction]],
    ) -> "LinearOperator":
        return cls(name, degree, tuple(tuple(_fraction(value) for value in row) for row in rows))

    @classmethod
    def zero(cls, name: str, degree: int, dimension: int) -> "LinearOperator":
        return cls.from_rows(name, degree, _zero_linear(dimension))

    @property
    def dimension(self) -> int:
        return len(self.entries)

    def is_zero(self) -> bool:
        return all(value == 0 for row in self.entries for value in row)

    def scaled(self, scalar: int | Fraction, *, name: str | None = None) -> "LinearOperator":
        coefficient = _fraction(scalar)
        return LinearOperator(
            name or self.name,
            self.degree,
            tuple(tuple(coefficient * value for value in row) for row in self.entries),
        )


@dataclass(frozen=True)
class BilinearOperator:
    """A homogeneous exact graded-symmetric bilinear operator."""

    name: str
    degree: int
    entries: tuple[tuple[tuple[Scalar, ...], ...], ...]

    def __post_init__(self) -> None:
        if not self.entries or not self.entries[0] or not self.entries[0][0]:
            raise ValueError("a bilinear operator must be nonempty")
        dimension = len(self.entries)
        if any(len(matrix) != dimension for matrix in self.entries) or any(
            len(row) != dimension for matrix in self.entries for row in matrix
        ):
            raise ValueError("a bilinear operator must have shape (n,n,n)")
        object.__setattr__(
            self,
            "entries",
            tuple(
                tuple(
                    tuple(_fraction(value) for value in row)
                    for row in matrix
                )
                for matrix in self.entries
            ),
        )

    @classmethod
    def from_entries(
        cls,
        name: str,
        degree: int,
        entries: Sequence[Sequence[Sequence[int | Fraction]]],
    ) -> "BilinearOperator":
        return cls(
            name,
            degree,
            tuple(
                tuple(tuple(_fraction(value) for value in row) for row in matrix)
                for matrix in entries
            ),
        )

    @classmethod
    def zero(cls, name: str, degree: int, dimension: int) -> "BilinearOperator":
        return cls.from_entries(name, degree, _zero_bilinear(dimension))

    @property
    def dimension(self) -> int:
        return len(self.entries)

    def is_zero(self) -> bool:
        return all(
            value == 0
            for matrix in self.entries
            for row in matrix
            for value in row
        )

    def scaled(
        self,
        scalar: int | Fraction,
        *,
        name: str | None = None,
    ) -> "BilinearOperator":
        coefficient = _fraction(scalar)
        return BilinearOperator(
            name or self.name,
            self.degree,
            tuple(
                tuple(
                    tuple(coefficient * value for value in row)
                    for row in matrix
                )
                for matrix in self.entries
            ),
        )

    def added(
        self,
        other: "BilinearOperator",
        *,
        name: str,
    ) -> "BilinearOperator":
        if self.degree != other.degree or self.dimension != other.dimension:
            raise ValueError("only equal-degree bilinear operators may be added")
        dimension = self.dimension
        return BilinearOperator.from_entries(
            name,
            self.degree,
            [
                [
                    [
                        self.entries[output][left][right]
                        + other.entries[output][left][right]
                        for right in range(dimension)
                    ]
                    for left in range(dimension)
                ]
                for output in range(dimension)
            ],
        )


def linear_commutator(
    left: LinearOperator,
    right: LinearOperator,
    *,
    name: str,
) -> LinearOperator:
    """Return the exact graded commutator of two linear operators."""

    if left.dimension != right.dimension:
        raise ValueError("linear operator dimensions differ")
    dimension = left.dimension
    sign = -1 if (left.degree * right.degree) % 2 else 1
    rows = _zero_linear(dimension)
    for output, source in product(range(dimension), repeat=2):
        rows[output][source] = sum(
            (
                left.entries[output][middle] * right.entries[middle][source]
                - sign
                * right.entries[output][middle]
                * left.entries[middle][source]
                for middle in range(dimension)
            ),
            Fraction(0),
        )
    return LinearOperator.from_rows(name, left.degree + right.degree, rows)


def linear_bilinear_commutator(
    linear: LinearOperator,
    bilinear: BilinearOperator,
    *,
    input_parities: Sequence[int],
    name: str,
) -> BilinearOperator:
    """Return ``[linear,bilinear]`` as a coderivation Taylor coefficient."""

    if linear.dimension != bilinear.dimension:
        raise ValueError("linear and bilinear dimensions differ")
    dimension = linear.dimension
    if len(input_parities) != dimension or any(parity not in (0, 1) for parity in input_parities):
        raise ValueError("input parity ledger is invalid")
    bracket_sign = -1 if (linear.degree * bilinear.degree) % 2 else 1
    entries = _zero_bilinear(dimension)
    for output, left_input, right_input in product(range(dimension), repeat=3):
        postcompose = sum(
            (
                linear.entries[output][middle]
                * bilinear.entries[middle][left_input][right_input]
                for middle in range(dimension)
            ),
            Fraction(0),
        )
        precompose_left = sum(
            (
                bilinear.entries[output][middle][right_input]
                * linear.entries[middle][left_input]
                for middle in range(dimension)
            ),
            Fraction(0),
        )
        second_sign = -1 if (linear.degree * input_parities[left_input]) % 2 else 1
        precompose_right = second_sign * sum(
            (
                bilinear.entries[output][left_input][middle]
                * linear.entries[middle][right_input]
                for middle in range(dimension)
            ),
            Fraction(0),
        )
        entries[output][left_input][right_input] = (
            postcompose - bracket_sign * (precompose_left + precompose_right)
        )
    return BilinearOperator.from_entries(
        name,
        linear.degree + bilinear.degree,
        entries,
    )


def _rref_solve(
    rows: Sequence[Sequence[Fraction]],
    rhs: Sequence[Fraction],
    variable_count: int,
) -> tuple[Fraction, ...] | None:
    """Solve an exact system, deterministically setting free variables to zero."""

    if len(rows) != len(rhs) or any(len(row) != variable_count for row in rows):
        raise ValueError("linear system has inconsistent dimensions")
    augmented = [list(row) + [value] for row, value in zip(rows, rhs)]
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
            if row == pivot_row or augmented[row][column] == 0:
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
    if any(
        all(value == 0 for value in row[:variable_count]) and row[-1] != 0
        for row in augmented
    ):
        return None
    solution = [Fraction(0) for _ in range(variable_count)]
    for row, column in enumerate(pivots):
        solution[column] = augmented[row][-1]
    return tuple(solution)


def _nullspace_basis(
    rows: Sequence[Sequence[Fraction]],
    variable_count: int,
) -> tuple[tuple[Fraction, ...], ...]:
    if any(len(row) != variable_count for row in rows):
        raise ValueError("constraint width differs from the ambient dimension")
    reduced = [list(row) for row in rows]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(variable_count):
        selected = next(
            (row for row in range(pivot_row, len(reduced)) if reduced[row][column]),
            None,
        )
        if selected is None:
            continue
        reduced[pivot_row], reduced[selected] = reduced[selected], reduced[pivot_row]
        pivot = reduced[pivot_row][column]
        reduced[pivot_row] = [value / pivot for value in reduced[pivot_row]]
        for row in range(len(reduced)):
            if row == pivot_row or reduced[row][column] == 0:
                continue
            factor = reduced[row][column]
            reduced[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(reduced[row], reduced[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(reduced):
            break
    free_columns = [column for column in range(variable_count) if column not in pivots]
    basis: list[tuple[Fraction, ...]] = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(variable_count)]
        vector[free] = Fraction(1)
        for row, pivot in reversed(list(enumerate(pivots))):
            vector[pivot] = -reduced[row][free]
        basis.append(tuple(vector))
    return tuple(basis)


@dataclass(frozen=True)
class ArityTwoComplex:
    """The exact complex of graded-symmetric bilinear maps under ``[q1,-]``."""

    basis_degrees: tuple[int, ...]
    basis_parities: tuple[int, ...]
    q1: LinearOperator

    def __post_init__(self) -> None:
        dimension = len(self.basis_degrees)
        if dimension == 0 or len(self.basis_parities) != dimension:
            raise ValueError("basis degree and parity ledgers must be nonempty and aligned")
        if any(parity not in (0, 1) for parity in self.basis_parities):
            raise ValueError("basis parities must be zero or one")
        if self.q1.degree != 1 or self.q1.dimension != dimension:
            raise ValueError("q1 must be a degree-one operator on the declared basis")
        self.validate_linear(self.q1)
        if not linear_commutator(self.q1, self.q1, name="[q1,q1]").is_zero():
            raise ValueError("q1 is not nilpotent")

    @property
    def dimension(self) -> int:
        return len(self.basis_degrees)

    def validate_linear(self, operator: LinearOperator) -> None:
        if operator.dimension != self.dimension:
            raise ValueError(f"{operator.name} has the wrong dimension")
        for output, input_ in product(range(self.dimension), repeat=2):
            if operator.entries[output][input_] == 0:
                continue
            if self.basis_degrees[output] - self.basis_degrees[input_] != operator.degree:
                raise ValueError(f"{operator.name} is nonhomogeneous at {(output, input_)}")
            if (self.basis_parities[output] - self.basis_parities[input_] - operator.degree) % 2:
                raise ValueError(f"{operator.name} violates parity at {(output, input_)}")

    def validate_bilinear(self, operator: BilinearOperator) -> None:
        if operator.dimension != self.dimension:
            raise ValueError(f"{operator.name} has the wrong dimension")
        for output, left, right in product(range(self.dimension), repeat=3):
            value = operator.entries[output][left][right]
            if value:
                degree = (
                    self.basis_degrees[output]
                    - self.basis_degrees[left]
                    - self.basis_degrees[right]
                )
                if degree != operator.degree:
                    raise ValueError(f"{operator.name} is nonhomogeneous at {(output, left, right)}")
                parity = (
                    self.basis_parities[output]
                    - self.basis_parities[left]
                    - self.basis_parities[right]
                    - operator.degree
                ) % 2
                if parity:
                    raise ValueError(f"{operator.name} violates parity at {(output, left, right)}")
            sign = -1 if self.basis_parities[left] * self.basis_parities[right] else 1
            if value != sign * operator.entries[output][right][left]:
                raise ValueError(f"{operator.name} is not graded symmetric")

    def linear_bracket(
        self,
        linear: LinearOperator,
        bilinear: BilinearOperator,
        *,
        name: str,
    ) -> BilinearOperator:
        self.validate_linear(linear)
        self.validate_bilinear(bilinear)
        result = linear_bilinear_commutator(
            linear,
            bilinear,
            input_parities=self.basis_parities,
            name=name,
        )
        self.validate_bilinear(result)
        return result

    def coordinate_slots(self, degree: int) -> tuple[tuple[int, int, int], ...]:
        slots = []
        for output in range(self.dimension):
            for left in range(self.dimension):
                for right in range(left, self.dimension):
                    if left == right and self.basis_parities[left] == 1:
                        continue
                    if (
                        self.basis_degrees[output]
                        - self.basis_degrees[left]
                        - self.basis_degrees[right]
                        == degree
                    ):
                        slots.append((output, left, right))
        return tuple(slots)

    def coordinates(self, operator: BilinearOperator) -> tuple[Fraction, ...]:
        self.validate_bilinear(operator)
        return tuple(
            operator.entries[output][left][right]
            for output, left, right in self.coordinate_slots(operator.degree)
        )

    def operator_from_coordinates(
        self,
        degree: int,
        coordinates: Sequence[int | Fraction],
        *,
        name: str,
    ) -> BilinearOperator:
        slots = self.coordinate_slots(degree)
        if len(coordinates) != len(slots):
            raise ValueError("coordinate count does not match the bilinear-map space")
        entries = _zero_bilinear(self.dimension)
        for (output, left, right), raw_value in zip(slots, coordinates):
            value = _fraction(raw_value)
            entries[output][left][right] = value
            if left != right:
                sign = -1 if self.basis_parities[left] * self.basis_parities[right] else 1
                entries[output][right][left] = sign * value
        result = BilinearOperator.from_entries(name, degree, entries)
        self.validate_bilinear(result)
        return result

    def differential(self, operator: BilinearOperator, *, name: str) -> BilinearOperator:
        return self.linear_bracket(self.q1, operator, name=name)

    def differential_columns(self, degree: int) -> tuple[tuple[Fraction, ...], ...]:
        slots = self.coordinate_slots(degree)
        columns = []
        for index in range(len(slots)):
            coordinates = [Fraction(0) for _ in slots]
            coordinates[index] = Fraction(1)
            basis = self.operator_from_coordinates(degree, coordinates, name=f"B_{degree}_{index}")
            columns.append(self.coordinates(self.differential(basis, name="delta_B")))
        return tuple(columns)

    def solve_boundary(self, target: BilinearOperator) -> BilinearOperator | None:
        self.validate_bilinear(target)
        columns = self.differential_columns(target.degree - 1)
        target_coordinates = self.coordinates(target)
        rows = tuple(
            tuple(column[row] for column in columns)
            for row in range(len(target_coordinates))
        )
        solution = _rref_solve(rows, target_coordinates, len(columns))
        if solution is None:
            return None
        primitive = self.operator_from_coordinates(
            target.degree - 1,
            solution,
            name=f"primitive_for_{target.name}",
        )
        if self.differential(primitive, name="delta_primitive").entries != target.entries:
            raise AssertionError("exact arity-two solver returned an invalid primitive")
        return primitive

    def dual_nontriviality_witness(self, cocycle: BilinearOperator) -> tuple[Fraction, ...]:
        self.validate_bilinear(cocycle)
        columns = self.differential_columns(cocycle.degree - 1)
        coordinates = self.coordinates(cocycle)
        equations = [tuple(column) for column in columns]
        equations.append(coordinates)
        rhs = [Fraction(0) for _ in columns] + [Fraction(1)]
        witness = _rref_solve(equations, rhs, len(coordinates))
        if witness is None:
            raise ValueError("no normalized dual obstruction witness exists")
        if any(
            sum((left * right for left, right in zip(witness, column)), Fraction(0))
            for column in columns
        ):
            raise AssertionError("dual witness does not annihilate the boundary image")
        if sum(
            (left * right for left, right in zip(witness, coordinates)),
            Fraction(0),
        ) != 1:
            raise AssertionError("dual obstruction witness is not normalized")
        return witness


@dataclass(frozen=True)
class BilinearConstraint:
    """A named exact linear constraint on bilinear-map coordinates."""

    name: str
    degree: int
    row: tuple[Fraction, ...]

    @classmethod
    def from_row(
        cls,
        name: str,
        degree: int,
        row: Sequence[int | Fraction],
    ) -> "BilinearConstraint":
        return cls(name, degree, tuple(_fraction(value) for value in row))


@dataclass(frozen=True)
class AdmissibleArityTwoComplex:
    """A differential-stable constrained subcomplex of bilinear maps."""

    ambient: ArityTwoComplex
    constraints: tuple[BilinearConstraint, ...]
    certified_source_degrees: tuple[int, ...]

    def __post_init__(self) -> None:
        seen: set[tuple[int, str]] = set()
        for constraint in self.constraints:
            key = (constraint.degree, constraint.name)
            if key in seen:
                raise ValueError(f"duplicate admissibility constraint {key}")
            seen.add(key)
            expected = len(self.ambient.coordinate_slots(constraint.degree))
            if len(constraint.row) != expected:
                raise ValueError(f"constraint {constraint.name} has the wrong width")
        for degree in self.certified_source_degrees:
            self.differential_columns(degree)

    @property
    def q1(self) -> LinearOperator:
        return self.ambient.q1

    def constraint_rows(self, degree: int) -> tuple[tuple[Fraction, ...], ...]:
        return tuple(
            constraint.row
            for constraint in self.constraints
            if constraint.degree == degree
        )

    def coordinate_basis(self, degree: int) -> tuple[tuple[Fraction, ...], ...]:
        dimension = len(self.ambient.coordinate_slots(degree))
        return _nullspace_basis(self.constraint_rows(degree), dimension)

    def coordinates(self, operator: BilinearOperator) -> tuple[Fraction, ...]:
        ambient_coordinates = self.ambient.coordinates(operator)
        basis = self.coordinate_basis(operator.degree)
        rows = tuple(
            tuple(vector[row] for vector in basis)
            for row in range(len(ambient_coordinates))
        )
        solution = _rref_solve(rows, ambient_coordinates, len(basis))
        if solution is None:
            raise ValueError(f"{operator.name} is not admissible")
        return solution

    def operator_from_coordinates(
        self,
        degree: int,
        coordinates: Sequence[int | Fraction],
        *,
        name: str,
    ) -> BilinearOperator:
        basis = self.coordinate_basis(degree)
        if len(coordinates) != len(basis):
            raise ValueError("coordinate count does not match the admissible space")
        ambient_dimension = len(self.ambient.coordinate_slots(degree))
        ambient_coordinates = tuple(
            sum(
                (
                    _fraction(coefficient) * vector[index]
                    for coefficient, vector in zip(coordinates, basis)
                ),
                Fraction(0),
            )
            for index in range(ambient_dimension)
        )
        return self.ambient.operator_from_coordinates(
            degree,
            ambient_coordinates,
            name=name,
        )

    def validate_bilinear(self, operator: BilinearOperator) -> None:
        self.coordinates(operator)

    def differential(self, operator: BilinearOperator, *, name: str) -> BilinearOperator:
        self.validate_bilinear(operator)
        result = self.ambient.differential(operator, name=name)
        self.validate_bilinear(result)
        return result

    def differential_columns(self, degree: int) -> tuple[tuple[Fraction, ...], ...]:
        basis = self.coordinate_basis(degree)
        columns = []
        for index in range(len(basis)):
            coordinates = [Fraction(0) for _ in basis]
            coordinates[index] = Fraction(1)
            source = self.operator_from_coordinates(
                degree,
                coordinates,
                name=f"A_{degree}_{index}",
            )
            try:
                columns.append(self.coordinates(self.ambient.differential(source, name="delta_A")))
            except ValueError as exc:
                raise ValueError(
                    f"admissibility constraints do not form a subcomplex at degree {degree}"
                ) from exc
        return tuple(columns)

    def solve_boundary(self, target: BilinearOperator) -> BilinearOperator | None:
        self.validate_bilinear(target)
        columns = self.differential_columns(target.degree - 1)
        target_coordinates = self.coordinates(target)
        rows = tuple(
            tuple(column[row] for column in columns)
            for row in range(len(target_coordinates))
        )
        solution = _rref_solve(rows, target_coordinates, len(columns))
        if solution is None:
            return None
        primitive = self.operator_from_coordinates(
            target.degree - 1,
            solution,
            name=f"admissible_primitive_for_{target.name}",
        )
        if self.ambient.differential(primitive, name="delta_primitive").entries != target.entries:
            raise AssertionError("admissible arity-two solver returned an invalid primitive")
        return primitive

    def dual_nontriviality_witness(self, cocycle: BilinearOperator) -> tuple[Fraction, ...]:
        self.validate_bilinear(cocycle)
        columns = self.differential_columns(cocycle.degree - 1)
        coordinates = self.coordinates(cocycle)
        equations = [tuple(column) for column in columns]
        equations.append(coordinates)
        rhs = [Fraction(0) for _ in columns] + [Fraction(1)]
        witness = _rref_solve(equations, rhs, len(coordinates))
        if witness is None:
            raise ValueError("no normalized admissible obstruction witness exists")
        if any(
            sum((left * right for left, right in zip(witness, column)), Fraction(0))
            for column in columns
        ):
            raise AssertionError("admissible dual witness does not annihilate boundaries")
        if sum(
            (left * right for left, right in zip(witness, coordinates)),
            Fraction(0),
        ) != 1:
            raise AssertionError("admissible dual obstruction witness is not normalized")
        return witness


@dataclass(frozen=True)
class ArityTwoCorrectionClassification:
    status: str
    source: BilinearOperator
    correction: BilinearOperator | None
    dual_witness: tuple[Fraction, ...] | None


def classify_cartan_source(
    complex_: ArityTwoComplex | AdmissibleArityTwoComplex,
    source: BilinearOperator,
) -> ArityTwoCorrectionClassification:
    """Solve ``[q1,iota_D^(2)]=-source`` or retain a dual witness."""

    complex_.validate_bilinear(source)
    if source.degree != 0:
        raise ValueError("the arity-two Cartan source must have degree zero")
    if not complex_.differential(source, name="delta_source").is_zero():
        raise ValueError("the arity-two Cartan source is not q1-closed")
    if source.is_zero():
        return ArityTwoCorrectionClassification("ZERO_SOURCE", source, None, None)
    target = source.scaled(-1, name="minus_cartan_source")
    correction = complex_.solve_boundary(target)
    if correction is not None:
        return ArityTwoCorrectionClassification(
            "EXACT_CORRECTION",
            source,
            correction,
            None,
        )
    witness = complex_.dual_nontriviality_witness(source)
    return ArityTwoCorrectionClassification(
        "NONTRIVIAL_OBSTRUCTION",
        source,
        None,
        witness,
    )


@dataclass(frozen=True)
class ArityTwoCartanData:
    """Complete finite data entering the classical arity-two Cartan equation."""

    complex: ArityTwoComplex
    q2: BilinearOperator
    iota_D: LinearOperator
    lie_D: LinearOperator
    lie_D2: BilinearOperator

    def __post_init__(self) -> None:
        self.complex.validate_bilinear(self.q2)
        self.complex.validate_linear(self.iota_D)
        self.complex.validate_linear(self.lie_D)
        self.complex.validate_bilinear(self.lie_D2)
        if self.q2.degree != 1:
            raise ValueError("q2 must have degree one")
        if self.iota_D.degree != -1:
            raise ValueError("iota_D must have degree minus one")
        if self.lie_D.degree != 0 or self.lie_D2.degree != 0:
            raise ValueError("the D action must have degree zero")

    def q2_nilpotency_source(self) -> BilinearOperator:
        return self.complex.linear_bracket(self.complex.q1, self.q2, name="[q1,q2]")

    def classical_cartan_defect(self) -> LinearOperator:
        return _subtract_linear(
            linear_commutator(self.complex.q1, self.iota_D, name="[q1,iota_D]"),
            self.lie_D,
            name="classical_cartan_defect",
        )

    def D_derivation_defect(self) -> BilinearOperator:
        return self.complex.linear_bracket(self.lie_D, self.q2, name="[L_D,q2]")

    def cartan_source(self) -> BilinearOperator:
        bracket = self.complex.linear_bracket(self.iota_D, self.q2, name="[iota_D,q2]")
        return bracket.added(self.lie_D2.scaled(-1), name="A_D_2")

    def source_consistency_defect(self) -> BilinearOperator:
        return self.complex.differential(self.cartan_source(), name="[q1,A_D_2]")

    def sourced_consistency_rhs(self) -> BilinearOperator:
        """Return ``[L_D,q2]-[q1,L_D^(2)]`` in the arity-two identity."""

        return _subtract_bilinear(
            self.D_derivation_defect(),
            self.complex.differential(self.lie_D2, name="[q1,L_D_2]"),
            name="D_q2_minus_delta_L_D_2",
        )

    def sourced_consistency_identity_defect(self) -> BilinearOperator:
        """Check the arity-two graded-Jacobi identity for the Cartan source."""

        return self.source_consistency_defect().added(
            self.sourced_consistency_rhs().scaled(-1),
            name="cartan_source_consistency_identity_defect",
        )

    def checks(self) -> dict[str, bool]:
        return {
            "q1_squared_zero": True,
            "q1_q2_arity_two_nilpotency": self.q2_nilpotency_source().is_zero(),
            "classical_Cartan_identity": self.classical_cartan_defect().is_zero(),
            "D_q2_derivation": self.D_derivation_defect().is_zero(),
            "sourced_consistency_identity": self.sourced_consistency_identity_defect().is_zero(),
            "cartan_source_q1_closed": self.source_consistency_defect().is_zero(),
        }

    def classify(
        self,
        complex_: ArityTwoComplex | AdmissibleArityTwoComplex | None = None,
    ) -> ArityTwoCorrectionClassification:
        failed = [name for name, passed in self.checks().items() if not passed]
        if failed:
            raise ValueError(f"arity-two Cartan consistency checks failed: {', '.join(failed)}")
        target_complex = complex_ or self.complex
        if isinstance(target_complex, AdmissibleArityTwoComplex) and target_complex.ambient != self.complex:
            raise ValueError("admissible arity-two complex has the wrong ambient complex")
        return classify_cartan_source(target_complex, self.cartan_source())


def _subtract_linear(
    left: LinearOperator,
    right: LinearOperator,
    *,
    name: str,
) -> LinearOperator:
    if left.degree != right.degree or left.dimension != right.dimension:
        raise ValueError("linear operators cannot be subtracted")
    return LinearOperator.from_rows(
        name,
        left.degree,
        [
            [
                left.entries[output][input_] - right.entries[output][input_]
                for input_ in range(left.dimension)
            ]
            for output in range(left.dimension)
        ],
    )


def _subtract_bilinear(
    left: BilinearOperator,
    right: BilinearOperator,
    *,
    name: str,
) -> BilinearOperator:
    if left.degree != right.degree or left.dimension != right.dimension:
        raise ValueError("bilinear operators cannot be subtracted")
    return left.added(right.scaled(-1), name=name)


def build_exact_correction_fixture() -> ArityTwoCartanData:
    """Return a nonzero equivariant contractible fixture with exact correction.

    Three two-term contractible pairs carry D weights one, one, and two.  The
    only q2 block maps the two weight-one lower generators to the weight-two
    upper generator.  This fixture exercises every identity without encoding
    any conformal-gravity coefficient.
    """

    degrees = (0, 1, 0, 1, 0, 1)
    parities = (0, 1, 0, 1, 0, 1)
    q1_rows = [[0 for _ in degrees] for _ in degrees]
    for lower, upper in ((0, 1), (2, 3), (4, 5)):
        q1_rows[upper][lower] = 1
    q1 = LinearOperator.from_rows("q1", 1, q1_rows)
    complex_ = ArityTwoComplex(degrees, parities, q1)

    iota_rows = [[0 for _ in degrees] for _ in degrees]
    iota_rows[0][1] = 1
    iota_rows[2][3] = 1
    iota_rows[4][5] = 2
    iota = LinearOperator.from_rows("iota_D", -1, iota_rows)
    lie_D = linear_commutator(q1, iota, name="L_D")

    q2_entries = [[[0 for _ in degrees] for _ in degrees] for _ in degrees]
    q2_entries[5][0][2] = 1
    q2_entries[5][2][0] = 1
    q2 = BilinearOperator.from_entries("q2", 1, q2_entries)
    lie_D2 = BilinearOperator.zero("L_D_2", 0, len(degrees))
    return ArityTwoCartanData(complex_, q2, iota, lie_D, lie_D2)
