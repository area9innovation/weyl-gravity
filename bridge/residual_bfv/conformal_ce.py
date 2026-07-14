"""Exact minimal residual conformal CE/BFV package.

The generator basis is

``D | R_01,...,R_23 | K+_0,...,K+_3 | K-_0,...,K-_3``.

It has compact grading ``0^7,+1^4,-1^4``.  Ghosts carry the opposite
grading.  The module implements the structure constants, exterior algebra,
Chevalley--Eilenberg differential, contraction with ``D``, compact Lie
derivative, complementary-degree top pairing, and the four-ghost polarized
vacuum.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import TypeAlias

import sympy as sp


Monomial: TypeAlias = tuple[int, ...]
ExteriorPolynomial: TypeAlias = dict[Monomial, sp.Expr]


def _rotation_name(first: int, second: int) -> tuple[str | None, int]:
    if first == second:
        return None, 0
    if first < second:
        return f"R{first}{second}", 1
    return f"R{second}{first}", -1


def _add(output: dict, key, value) -> None:
    value = sp.simplify(value)
    if value == 0 or key is None:
        return
    output[key] = sp.simplify(output.get(key, 0) + value)
    if output[key] == 0:
        del output[key]


def _basis_bracket(first: str, second: str) -> dict[str, sp.Expr]:
    if first == second:
        return {}
    if second == "D":
        return {name: -value for name, value in _basis_bracket("D", first).items()}
    if first == "D":
        if not second.startswith("K"):
            return {}
        sign = 1 if second.startswith("K+") else -1
        return {second: sp.Integer(sign)}
    if first.startswith("K") and second.startswith("R"):
        return {name: -value for name, value in _basis_bracket(second, first).items()}
    if first.startswith("R") and second.startswith("R"):
        a, b = int(first[1]), int(first[2])
        c, d = int(second[1]), int(second[2])
        output: dict[str, sp.Expr] = {}
        for coefficient, left, right in (
            (int(b == c), a, d),
            (-int(a == c), b, d),
            (-int(b == d), a, c),
            (int(a == d), b, c),
        ):
            name, orientation = _rotation_name(left, right)
            _add(output, name, coefficient * orientation)
        return output
    if first.startswith("R") and second.startswith("K"):
        a, b = int(first[1]), int(first[2])
        sign = "+" if second.startswith("K+") else "-"
        ambient = int(second[-1])
        output: dict[str, sp.Expr] = {}
        _add(output, f"K{sign}_{a}", int(b == ambient))
        _add(output, f"K{sign}_{b}", -int(a == ambient))
        return output
    if first.startswith("K") and second.startswith("K"):
        first_sign = 1 if first.startswith("K+") else -1
        second_sign = 1 if second.startswith("K+") else -1
        if first_sign == second_sign:
            return {}
        if first_sign == -1:
            return {
                name: -value for name, value in _basis_bracket(second, first).items()
            }
        first_ambient = int(first[-1])
        second_ambient = int(second[-1])
        output: dict[str, sp.Expr] = {}
        name, orientation = _rotation_name(first_ambient, second_ambient)
        _add(output, name, 2 * orientation)
        _add(output, "D", 2 * int(first_ambient == second_ambient))
        return output
    raise ValueError(f"unhandled bracket {first}, {second}")


def _wedge_monomials(first: Monomial, second: Monomial):
    if set(first).intersection(second):
        return None
    inversions = sum(left > right for left in first for right in second)
    return (-1 if inversions % 2 else 1), tuple(sorted(first + second))


@dataclass(frozen=True)
class ConformalCE:
    names: tuple[str, ...]
    structure_constants: tuple[tuple[tuple[sp.Expr, ...], ...], ...]
    generator_degrees: tuple[int, ...]
    ghost_degrees: tuple[int, ...]
    ghost_differentials: tuple[ExteriorPolynomial, ...]

    @classmethod
    def build(cls) -> "ConformalCE":
        names = (
            "D",
            *(f"R{first}{second}" for first, second in combinations(range(4), 2)),
            *(f"K+_{ambient}" for ambient in range(4)),
            *(f"K-_{ambient}" for ambient in range(4)),
        )
        index = {name: position for position, name in enumerate(names)}
        dimension = len(names)
        structure = [
            [[sp.Integer(0) for _ in range(dimension)] for _ in range(dimension)]
            for _ in range(dimension)
        ]
        for first, first_name in enumerate(names):
            for second, second_name in enumerate(names):
                for target_name, value in _basis_bracket(first_name, second_name).items():
                    structure[first][second][index[target_name]] = value
        structure_tuple = tuple(
            tuple(tuple(row) for row in matrix) for matrix in structure
        )
        generator_degrees = (0,) * 7 + (1,) * 4 + (-1,) * 4
        ghost_degrees = tuple(-degree for degree in generator_degrees)

        differentials: list[ExteriorPolynomial] = []
        for target in range(dimension):
            image: ExteriorPolynomial = {}
            for first in range(dimension):
                for second in range(dimension):
                    product = _wedge_monomials((first,), (second,))
                    if product is None:
                        continue
                    sign, monomial = product
                    _add(
                        image,
                        monomial,
                        -sp.Rational(1, 2)
                        * sign
                        * structure_tuple[first][second][target],
                    )
            differentials.append(image)
        result = cls(
            names,
            structure_tuple,
            generator_degrees,
            ghost_degrees,
            tuple(differentials),
        )
        result.verify_algebra()
        return result

    @property
    def dimension(self) -> int:
        return len(self.names)

    @property
    def index(self) -> dict[str, int]:
        return {name: position for position, name in enumerate(self.names)}

    @property
    def top(self) -> Monomial:
        return tuple(range(self.dimension))

    @property
    def lowering_ghosts(self) -> Monomial:
        """Ghosts dual to the four grade +1 generators."""

        return tuple(self.index[f"K+_{ambient}"] for ambient in range(4))

    @property
    def raising_ghosts(self) -> Monomial:
        return tuple(self.index[f"K-_{ambient}"] for ambient in range(4))

    @property
    def zero_ghosts(self) -> Monomial:
        return tuple(range(7))

    def wedge(self, first: ExteriorPolynomial, second: ExteriorPolynomial) -> ExteriorPolynomial:
        output: ExteriorPolynomial = {}
        for left, left_value in first.items():
            for right, right_value in second.items():
                product = _wedge_monomials(left, right)
                if product is None:
                    continue
                sign, monomial = product
                _add(output, monomial, sign * left_value * right_value)
        return output

    def differential(self, polynomial: ExteriorPolynomial) -> ExteriorPolynomial:
        output: ExteriorPolynomial = {}
        for monomial, value in polynomial.items():
            for position, ghost in enumerate(monomial):
                prefix = {monomial[:position]: sp.Integer(1)}
                suffix = {monomial[position + 1 :]: sp.Integer(1)}
                term = self.wedge(
                    self.wedge(prefix, self.ghost_differentials[ghost]), suffix
                )
                for result, coefficient in term.items():
                    _add(output, result, (-1) ** position * value * coefficient)
        return output

    def contract(self, generator: int, polynomial: ExteriorPolynomial) -> ExteriorPolynomial:
        output: ExteriorPolynomial = {}
        for monomial, value in polynomial.items():
            if generator not in monomial:
                continue
            position = monomial.index(generator)
            _add(
                output,
                monomial[:position] + monomial[position + 1 :],
                (-1) ** position * value,
            )
        return output

    def compact_degree(self, monomial: Monomial) -> int:
        return sum(self.ghost_degrees[index] for index in monomial)

    def lie_d(self, polynomial: ExteriorPolynomial) -> ExteriorPolynomial:
        return {
            monomial: sp.Integer(self.compact_degree(monomial)) * value
            for monomial, value in polynomial.items()
            if self.compact_degree(monomial) * value != 0
        }

    def top_coefficient(self, polynomial: ExteriorPolynomial) -> sp.Expr:
        return sp.simplify(polynomial.get(self.top, 0))

    def complementary_pair(self, first: Monomial, second: Monomial) -> sp.Expr:
        return self.top_coefficient(self.wedge({first: 1}, {second: 1}))

    def dagger_monomial(self, monomial: Monomial) -> tuple[sp.Expr, Monomial]:
        dagger_index = {
            **{self.index[f"K+_{a}"]: self.index[f"K-_{a}"] for a in range(4)},
            **{self.index[f"K-_{a}"]: self.index[f"K+_{a}"] for a in range(4)},
            **{index: index for index in range(7)},
        }
        output: ExteriorPolynomial = {(): sp.Integer(1)}
        for ghost in reversed(monomial):
            output = self.wedge(output, {(dagger_index[ghost],): sp.Integer(1)})
        if len(output) != 1:
            raise AssertionError("dagger monomial vanished")
        result, coefficient = next(iter(output.items()))
        return coefficient, result

    def polarized_pair(self, first: Monomial, second: Monomial) -> sp.Expr:
        coefficient, left = self.dagger_monomial(first)
        raw = self.top_coefficient(
            self.wedge(
                self.wedge({left: coefficient}, {self.zero_ghosts: 1}),
                {second: 1},
            )
        )
        vacuum_raw = self.top_coefficient(
            self.wedge(
                self.wedge(
                    {self.dagger_monomial(self.lowering_ghosts)[1]: self.dagger_monomial(self.lowering_ghosts)[0]},
                    {self.zero_ghosts: 1},
                ),
                {self.lowering_ghosts: 1},
            )
        )
        if vacuum_raw == 0:
            raise AssertionError("polarized vacuum does not saturate top form")
        return sp.simplify(raw / vacuum_raw)

    def verify_algebra(self) -> None:
        if self.dimension != 15:
            raise AssertionError("residual algebra is not fifteen dimensional")
        f = self.structure_constants
        for a in range(15):
            if sum(f[a][b][b] for b in range(15)) != 0:
                raise AssertionError("residual algebra is not unimodular")
            for b in range(15):
                for c in range(15):
                    if sp.simplify(f[a][b][c] + f[b][a][c]) != 0:
                        raise AssertionError("bracket is not antisymmetric")
        for a in range(15):
            for b in range(15):
                for c in range(15):
                    for target in range(15):
                        jacobi = sum(
                            f[b][c][middle] * f[a][middle][target]
                            + f[c][a][middle] * f[b][middle][target]
                            + f[a][b][middle] * f[c][middle][target]
                            for middle in range(15)
                        )
                        if sp.simplify(jacobi) != 0:
                            raise AssertionError("Jacobi identity failed")

    def verify_ce(self, maximum_degree: int = 5) -> None:
        for image in self.ghost_differentials:
            if self.differential(image):
                raise AssertionError("d^2 != 0 on a ghost generator")
        for degree in range(maximum_degree + 1):
            for monomial in combinations(range(15), degree):
                element = {monomial: sp.Integer(1)}
                image = self.differential(element)
                if self.differential(image):
                    raise AssertionError("d^2 != 0 on exterior basis")
                cartan = self.differential(self.contract(0, element))
                second = self.contract(0, image)
                for key, value in second.items():
                    _add(cartan, key, value)
                if cartan != self.lie_d(element):
                    raise AssertionError("Cartan identity failed")
        if self.polarized_pair(self.lowering_ghosts, self.lowering_ghosts) != 1:
            raise AssertionError("four-ghost vacuum norm is not one")
