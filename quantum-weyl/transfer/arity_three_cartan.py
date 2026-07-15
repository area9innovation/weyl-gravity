"""Exact arity-three Cartan recurrence and obstruction engine.

With the suspended graded-symmetric factorial convention, the arity-three
Cartan source is

    A_D^(3) = [q3,iota_D] + [q2,iota_D^(2)] - L_D^(3),

and the next correction obeys

    [q1,iota_D^(3)] = -A_D^(3).

This module checks the arity-three ``Q^2=0`` and D-equivariance identities,
constructs the complete exact complex of graded-symmetric ternary maps, and
retains either a rational primitive or a normalized dual obstruction witness.
Fixtures exercise mechanics only and contain no conformal-gravity coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations, product
from typing import Sequence

try:
    from .arity_two_cartan import (
        ArityTwoComplex,
        BilinearOperator,
        LinearOperator,
        _rref_solve,
        linear_commutator,
    )
except ImportError:
    from arity_two_cartan import (
        ArityTwoComplex,
        BilinearOperator,
        LinearOperator,
        _rref_solve,
        linear_commutator,
    )


def _fraction(value: int | Fraction) -> Fraction:
    if isinstance(value, bool):
        raise ValueError("ternary coefficients must be exact")
    return value if isinstance(value, Fraction) else Fraction(value)


def _zero_ternary(dimension: int) -> list[list[list[list[Fraction]]]]:
    return [
        [
            [
                [Fraction(0) for _ in range(dimension)]
                for _ in range(dimension)
            ]
            for _ in range(dimension)
        ]
        for _ in range(dimension)
    ]


@dataclass(frozen=True)
class TernaryOperator:
    name: str
    degree: int
    entries: tuple[tuple[tuple[tuple[Fraction, ...], ...], ...], ...]

    def __post_init__(self) -> None:
        if not self.entries:
            raise ValueError("a ternary operator must be nonempty")
        dimension = len(self.entries)
        if any(len(cube) != dimension for cube in self.entries) or any(
            len(matrix) != dimension for cube in self.entries for matrix in cube
        ) or any(
            len(row) != dimension
            for cube in self.entries
            for matrix in cube
            for row in matrix
        ):
            raise ValueError("a ternary operator must have shape (n,n,n,n)")
        object.__setattr__(
            self,
            "entries",
            tuple(
                tuple(
                    tuple(
                        tuple(_fraction(value) for value in row)
                        for row in matrix
                    )
                    for matrix in cube
                )
                for cube in self.entries
            ),
        )

    @classmethod
    def from_entries(cls, name: str, degree: int, entries) -> "TernaryOperator":
        return cls(name, degree, tuple(tuple(tuple(tuple(row) for row in matrix) for matrix in cube) for cube in entries))

    @classmethod
    def zero(cls, name: str, degree: int, dimension: int) -> "TernaryOperator":
        return cls.from_entries(name, degree, _zero_ternary(dimension))

    @property
    def dimension(self) -> int:
        return len(self.entries)

    def is_zero(self) -> bool:
        return all(
            value == 0
            for cube in self.entries
            for matrix in cube
            for row in matrix
            for value in row
        )

    def scaled(self, scalar: int | Fraction, *, name: str | None = None) -> "TernaryOperator":
        coefficient = _fraction(scalar)
        return TernaryOperator.from_entries(
            name or self.name,
            self.degree,
            [
                [
                    [
                        [coefficient * value for value in row]
                        for row in matrix
                    ]
                    for matrix in cube
                ]
                for cube in self.entries
            ],
        )

    def added(self, other: "TernaryOperator", *, name: str) -> "TernaryOperator":
        if self.degree != other.degree or self.dimension != other.dimension:
            raise ValueError("ternary operators cannot be added")
        dimension = self.dimension
        return TernaryOperator.from_entries(
            name,
            self.degree,
            [
                [
                    [
                        [
                            self.entries[output][first][second][third]
                            + other.entries[output][first][second][third]
                            for third in range(dimension)
                        ]
                        for second in range(dimension)
                    ]
                    for first in range(dimension)
                ]
                for output in range(dimension)
            ],
        )


def _permutation_sign(inputs: tuple[int, int, int], order: tuple[int, int, int], parities: Sequence[int]) -> int:
    exponent = 0
    for left in range(3):
        for right in range(left + 1, 3):
            if order[left] > order[right]:
                exponent += parities[inputs[order[left]]] * parities[inputs[order[right]]]
    return -1 if exponent % 2 else 1


def linear_ternary_commutator(
    linear: LinearOperator,
    ternary: TernaryOperator,
    *,
    input_parities: Sequence[int],
    name: str,
) -> TernaryOperator:
    if linear.dimension != ternary.dimension:
        raise ValueError("linear and ternary dimensions differ")
    dimension = linear.dimension
    bracket_sign = -1 if (linear.degree * ternary.degree) % 2 else 1
    entries = _zero_ternary(dimension)
    for output, first, second, third in product(range(dimension), repeat=4):
        inputs = (first, second, third)
        postcompose = sum(
            (
                linear.entries[output][middle]
                * ternary.entries[middle][first][second][third]
                for middle in range(dimension)
            ),
            Fraction(0),
        )
        precompose = Fraction(0)
        for position in range(3):
            sign = -1 if (
                linear.degree * sum(input_parities[inputs[index]] for index in range(position))
            ) % 2 else 1
            for middle in range(dimension):
                replaced = list(inputs)
                replaced[position] = middle
                precompose += (
                    sign
                    * ternary.entries[output][replaced[0]][replaced[1]][replaced[2]]
                    * linear.entries[middle][inputs[position]]
                )
        entries[output][first][second][third] = postcompose - bracket_sign * precompose
    return TernaryOperator.from_entries(name, linear.degree + ternary.degree, entries)


def _bilinear_composition(
    outer: BilinearOperator,
    inner: BilinearOperator,
    *,
    input_parities: Sequence[int],
    name: str,
) -> TernaryOperator:
    if outer.dimension != inner.dimension:
        raise ValueError("bilinear operator dimensions differ")
    dimension = outer.dimension
    entries = _zero_ternary(dimension)
    unshuffles = (((0, 1), 2), ((0, 2), 1), ((1, 2), 0))
    for output, first, second, third in product(range(dimension), repeat=4):
        inputs = (first, second, third)
        total = Fraction(0)
        for pair, remainder in unshuffles:
            order = (pair[0], pair[1], remainder)
            sign = _permutation_sign(inputs, order, input_parities)
            for middle in range(dimension):
                total += (
                    sign
                    * outer.entries[output][middle][inputs[remainder]]
                    * inner.entries[middle][inputs[pair[0]]][inputs[pair[1]]]
                )
        entries[output][first][second][third] = total
    return TernaryOperator.from_entries(name, outer.degree + inner.degree, entries)


def bilinear_bilinear_commutator(
    left: BilinearOperator,
    right: BilinearOperator,
    *,
    input_parities: Sequence[int],
    name: str,
) -> TernaryOperator:
    left_right = _bilinear_composition(
        left,
        right,
        input_parities=input_parities,
        name="left_after_right",
    )
    right_left = _bilinear_composition(
        right,
        left,
        input_parities=input_parities,
        name="right_after_left",
    )
    sign = -1 if (left.degree * right.degree) % 2 else 1
    return left_right.added(right_left.scaled(-sign), name=name)


@dataclass(frozen=True)
class ArityThreeComplex:
    basis_degrees: tuple[int, ...]
    basis_parities: tuple[int, ...]
    q1: LinearOperator

    def __post_init__(self) -> None:
        self.bilinear_complex.validate_linear(self.q1)

    @property
    def bilinear_complex(self) -> ArityTwoComplex:
        return ArityTwoComplex(self.basis_degrees, self.basis_parities, self.q1)

    @property
    def dimension(self) -> int:
        return len(self.basis_degrees)

    def validate_linear(self, operator: LinearOperator) -> None:
        self.bilinear_complex.validate_linear(operator)

    def validate_bilinear(self, operator: BilinearOperator) -> None:
        self.bilinear_complex.validate_bilinear(operator)

    def validate_ternary(self, operator: TernaryOperator) -> None:
        if operator.dimension != self.dimension:
            raise ValueError(f"{operator.name} has the wrong dimension")
        for output, first, second, third in product(range(self.dimension), repeat=4):
            inputs = (first, second, third)
            value = operator.entries[output][first][second][third]
            if value:
                degree = self.basis_degrees[output] - sum(self.basis_degrees[index] for index in inputs)
                if degree != operator.degree:
                    raise ValueError(f"{operator.name} is nonhomogeneous at {(output,) + inputs}")
                parity = (
                    self.basis_parities[output]
                    - sum(self.basis_parities[index] for index in inputs)
                    - operator.degree
                ) % 2
                if parity:
                    raise ValueError(f"{operator.name} violates parity at {(output,) + inputs}")
            for position in (0, 1):
                swapped = list(inputs)
                swapped[position], swapped[position + 1] = swapped[position + 1], swapped[position]
                sign = -1 if (
                    self.basis_parities[inputs[position]]
                    * self.basis_parities[inputs[position + 1]]
                ) else 1
                if value != sign * operator.entries[output][swapped[0]][swapped[1]][swapped[2]]:
                    raise ValueError(f"{operator.name} is not graded symmetric")

    def coordinate_slots(self, degree: int) -> tuple[tuple[int, int, int, int], ...]:
        slots = []
        for output in range(self.dimension):
            for first in range(self.dimension):
                for second in range(first, self.dimension):
                    for third in range(second, self.dimension):
                        inputs = (first, second, third)
                        if any(
                            inputs.count(index) > 1 and self.basis_parities[index] == 1
                            for index in set(inputs)
                        ):
                            continue
                        if self.basis_degrees[output] - sum(self.basis_degrees[index] for index in inputs) == degree:
                            slots.append((output, first, second, third))
        return tuple(slots)

    def coordinates(self, operator: TernaryOperator) -> tuple[Fraction, ...]:
        self.validate_ternary(operator)
        return tuple(operator.entries[slot[0]][slot[1]][slot[2]][slot[3]] for slot in self.coordinate_slots(operator.degree))

    def operator_from_coordinates(
        self,
        degree: int,
        coordinates: Sequence[int | Fraction],
        *,
        name: str,
    ) -> TernaryOperator:
        slots = self.coordinate_slots(degree)
        if len(coordinates) != len(slots):
            raise ValueError("coordinate count does not match the ternary-map space")
        entries = _zero_ternary(self.dimension)
        for (output, first, second, third), raw_value in zip(slots, coordinates):
            value = _fraction(raw_value)
            inputs = (first, second, third)
            for order in set(permutations((0, 1, 2))):
                permuted = (inputs[order[0]], inputs[order[1]], inputs[order[2]])
                entries[output][permuted[0]][permuted[1]][permuted[2]] = (
                    _permutation_sign(inputs, order, self.basis_parities) * value
                )
        result = TernaryOperator.from_entries(name, degree, entries)
        self.validate_ternary(result)
        return result

    def linear_bracket(self, linear: LinearOperator, ternary: TernaryOperator, *, name: str) -> TernaryOperator:
        self.validate_linear(linear)
        self.validate_ternary(ternary)
        result = linear_ternary_commutator(
            linear,
            ternary,
            input_parities=self.basis_parities,
            name=name,
        )
        self.validate_ternary(result)
        return result

    def bilinear_bracket(self, left: BilinearOperator, right: BilinearOperator, *, name: str) -> TernaryOperator:
        self.validate_bilinear(left)
        self.validate_bilinear(right)
        result = bilinear_bilinear_commutator(
            left,
            right,
            input_parities=self.basis_parities,
            name=name,
        )
        self.validate_ternary(result)
        return result

    def differential(self, operator: TernaryOperator, *, name: str) -> TernaryOperator:
        return self.linear_bracket(self.q1, operator, name=name)

    def differential_columns(self, degree: int) -> tuple[tuple[Fraction, ...], ...]:
        slots = self.coordinate_slots(degree)
        columns = []
        for index in range(len(slots)):
            coordinates = [Fraction(0) for _ in slots]
            coordinates[index] = Fraction(1)
            basis = self.operator_from_coordinates(degree, coordinates, name=f"T_{degree}_{index}")
            columns.append(self.coordinates(self.differential(basis, name="delta_T")))
        return tuple(columns)

    def solve_boundary(self, target: TernaryOperator) -> TernaryOperator | None:
        self.validate_ternary(target)
        columns = self.differential_columns(target.degree - 1)
        target_coordinates = self.coordinates(target)
        rows = tuple(tuple(column[row] for column in columns) for row in range(len(target_coordinates)))
        solution = _rref_solve(rows, target_coordinates, len(columns))
        if solution is None:
            return None
        primitive = self.operator_from_coordinates(target.degree - 1, solution, name=f"primitive_for_{target.name}")
        if self.differential(primitive, name="delta_primitive").entries != target.entries:
            raise AssertionError("arity-three solver returned an invalid primitive")
        return primitive

    def dual_nontriviality_witness(self, cocycle: TernaryOperator) -> tuple[Fraction, ...]:
        self.validate_ternary(cocycle)
        columns = self.differential_columns(cocycle.degree - 1)
        coordinates = self.coordinates(cocycle)
        equations = [tuple(column) for column in columns] + [coordinates]
        rhs = [Fraction(0) for _ in columns] + [Fraction(1)]
        witness = _rref_solve(equations, rhs, len(coordinates))
        if witness is None:
            raise ValueError("no normalized arity-three obstruction witness exists")
        if any(
            sum((left * right for left, right in zip(witness, column)), Fraction(0))
            for column in columns
        ):
            raise AssertionError("arity-three dual witness does not annihilate boundaries")
        if sum(
            (left * right for left, right in zip(witness, coordinates)),
            Fraction(0),
        ) != 1:
            raise AssertionError("arity-three dual obstruction witness is not normalized")
        return witness


@dataclass(frozen=True)
class ArityThreeClassification:
    status: str
    source: TernaryOperator
    correction: TernaryOperator | None
    dual_witness: tuple[Fraction, ...] | None


def classify_arity_three_source(complex_: ArityThreeComplex, source: TernaryOperator) -> ArityThreeClassification:
    complex_.validate_ternary(source)
    if source.degree != 0:
        raise ValueError("the arity-three Cartan source must have degree zero")
    if not complex_.differential(source, name="delta_source").is_zero():
        raise ValueError("the arity-three Cartan source is not q1-closed")
    if source.is_zero():
        return ArityThreeClassification("ZERO_SOURCE", source, None, None)
    correction = complex_.solve_boundary(source.scaled(-1, name="minus_source"))
    if correction is not None:
        return ArityThreeClassification("EXACT_CORRECTION", source, correction, None)
    return ArityThreeClassification(
        "NONTRIVIAL_OBSTRUCTION",
        source,
        None,
        complex_.dual_nontriviality_witness(source),
    )


@dataclass(frozen=True)
class ArityThreeCartanData:
    complex: ArityThreeComplex
    q2: BilinearOperator
    q3: TernaryOperator
    iota_D: LinearOperator
    iota_D2: BilinearOperator
    lie_D: LinearOperator
    lie_D2: BilinearOperator
    lie_D3: TernaryOperator

    def __post_init__(self) -> None:
        self.complex.validate_bilinear(self.q2)
        self.complex.validate_ternary(self.q3)
        self.complex.validate_linear(self.iota_D)
        self.complex.validate_bilinear(self.iota_D2)
        self.complex.validate_linear(self.lie_D)
        self.complex.validate_bilinear(self.lie_D2)
        self.complex.validate_ternary(self.lie_D3)
        if (self.q2.degree, self.q3.degree, self.iota_D.degree, self.iota_D2.degree) != (1, 1, -1, -1):
            raise ValueError("q and iota Taylor degrees are invalid")
        if (self.lie_D.degree, self.lie_D2.degree, self.lie_D3.degree) != (0, 0, 0):
            raise ValueError("D-action Taylor degrees are invalid")

    def q_arity_two_defect(self) -> BilinearOperator:
        return self.complex.bilinear_complex.linear_bracket(self.complex.q1, self.q2, name="[q1,q2]")

    def q_arity_three_defect(self) -> TernaryOperator:
        return self.complex.differential(self.q3, name="[q1,q3]").added(
            self.complex.bilinear_bracket(self.q2, self.q2, name="[q2,q2]").scaled(Fraction(1, 2)),
            name="Q_squared_arity_three",
        )

    def linear_cartan_defect(self) -> LinearOperator:
        bracket = linear_commutator(self.complex.q1, self.iota_D, name="[q1,iota_D]")
        return LinearOperator.from_rows(
            "linear_cartan_defect",
            0,
            [
                [bracket.entries[output][input_] - self.lie_D.entries[output][input_] for input_ in range(self.complex.dimension)]
                for output in range(self.complex.dimension)
            ],
        )

    def arity_two_cartan_defect(self) -> BilinearOperator:
        delta_iota2 = self.complex.bilinear_complex.linear_bracket(
            self.complex.q1,
            self.iota_D2,
            name="[q1,iota_D2]",
        )
        lower = self.complex.bilinear_complex.linear_bracket(
            self.iota_D,
            self.q2,
            name="[iota_D,q2]",
        )
        return delta_iota2.added(lower, name="arity_two_cartan_lhs").added(
            self.lie_D2.scaled(-1),
            name="arity_two_cartan_defect",
        )

    def D_arity_two_defect(self) -> BilinearOperator:
        return self.complex.bilinear_complex.linear_bracket(
            self.lie_D,
            self.q2,
            name="[L_D,q2]",
        ).added(
            self.complex.bilinear_complex.linear_bracket(
                self.complex.q1,
                self.lie_D2,
                name="[q1,L_D2]",
            ).scaled(-1),
            name="D_arity_two_defect",
        )

    def D_arity_three_defect(self) -> TernaryOperator:
        return self.complex.linear_bracket(self.lie_D, self.q3, name="[L_D,q3]").added(
            self.complex.bilinear_bracket(self.lie_D2, self.q2, name="[L_D2,q2]"),
            name="D_arity_three_partial",
        ).added(
            self.complex.differential(self.lie_D3, name="[q1,L_D3]").scaled(-1),
            name="D_arity_three_defect",
        )

    def cartan_source(self) -> TernaryOperator:
        direct = self.complex.linear_bracket(self.iota_D, self.q3, name="[iota_D,q3]")
        exchange = self.complex.bilinear_bracket(self.q2, self.iota_D2, name="[q2,iota_D2]")
        return direct.added(exchange, name="A_D3_without_L3").added(
            self.lie_D3.scaled(-1),
            name="A_D3",
        )

    def checks(self) -> dict[str, bool]:
        return {
            "q1_squared_zero": True,
            "Q_squared_arity_two": self.q_arity_two_defect().is_zero(),
            "Q_squared_arity_three": self.q_arity_three_defect().is_zero(),
            "Cartan_identity_arity_one": self.linear_cartan_defect().is_zero(),
            "Cartan_identity_arity_two": self.arity_two_cartan_defect().is_zero(),
            "D_equivariance_arity_two": self.D_arity_two_defect().is_zero(),
            "D_equivariance_arity_three": self.D_arity_three_defect().is_zero(),
            "cartan_source_q1_closed": self.complex.differential(self.cartan_source(), name="delta_A_D3").is_zero(),
        }

    def classify(self) -> ArityThreeClassification:
        failed = [name for name, passed in self.checks().items() if not passed]
        if failed:
            raise ValueError(f"arity-three Cartan consistency checks failed: {', '.join(failed)}")
        return classify_arity_three_source(self.complex, self.cartan_source())


def build_direct_q3_correction_fixture() -> ArityThreeCartanData:
    """Nonzero direct-q3 fixture with an exact arity-three correction."""

    degrees = (0, 1, 0, 1)
    parities = degrees
    q1_rows = [[0 for _ in degrees] for _ in degrees]
    for lower, upper in ((0, 1), (2, 3)):
        q1_rows[upper][lower] = 1
    q1 = LinearOperator.from_rows("q1", 1, q1_rows)
    complex_ = ArityThreeComplex(degrees, parities, q1)

    iota_rows = [[0 for _ in degrees] for _ in degrees]
    for lower, upper, weight in ((0, 1, 1), (2, 3, 3)):
        iota_rows[lower][upper] = weight
    iota = LinearOperator.from_rows("iota_D", -1, iota_rows)
    lie_D = linear_commutator(q1, iota, name="L_D")

    q3_entries = _zero_ternary(len(degrees))
    q3_entries[3][0][0][0] = Fraction(1)
    q3 = TernaryOperator.from_entries("q3", 1, q3_entries)
    q2 = BilinearOperator.zero("q2", 1, len(degrees))
    iota2 = BilinearOperator.zero("iota_D2", -1, len(degrees))
    lie_D2 = BilinearOperator.zero("L_D2", 0, len(degrees))
    lie_D3 = TernaryOperator.zero("L_D3", 0, len(degrees))
    return ArityThreeCartanData(complex_, q2, q3, iota, iota2, lie_D, lie_D2, lie_D3)


def build_exchange_bracket_fixture() -> tuple[
    ArityThreeComplex,
    BilinearOperator,
    BilinearOperator,
    TernaryOperator,
]:
    """Return a minimal homogeneous fixture with nonzero ``[q2,iota_D2]``."""

    degrees = (-1, 0, 1)
    parities = (1, 0, 1)
    q1 = LinearOperator.zero("q1", 1, 3)
    complex_ = ArityThreeComplex(degrees, parities, q1)
    q2_entries = [[[0 for _ in degrees] for _ in degrees] for _ in degrees]
    q2_entries[2][1][1] = 1
    q2_entries[1][0][1] = 1
    q2_entries[1][1][0] = 1
    q2 = BilinearOperator.from_entries("q2", 1, q2_entries)
    iota2_entries = [[[0 for _ in degrees] for _ in degrees] for _ in degrees]
    iota2_entries[0][1][1] = 1
    iota2 = BilinearOperator.from_entries("iota_D2", -1, iota2_entries)
    exchange = complex_.bilinear_bracket(q2, iota2, name="[q2,iota_D2]")
    return complex_, q2, iota2, exchange
