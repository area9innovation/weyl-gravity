"""Sparse first-jet PBW derivation of the relative Lee--Wald current.

Only the background and first field variation are required to form the
bilinear presymplectic current.  Keeping that truncation explicit avoids the
quadratic and cubic Taylor tensors used by the full action producers.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product

import sympy as sp

from bridge.einstein_sector.product_taylor_engine import (
    BASE_POINT,
    COORDINATES,
    PAIRS,
    PAIR_INDEX,
    BilinearOperator,
    LinearOperator,
)


@dataclass(frozen=True)
class FirstJet:
    background: sp.Expr = sp.S.Zero
    linear: LinearOperator = LinearOperator()

    @staticmethod
    def constant(value: sp.Expr) -> "FirstJet":
        return FirstJet(sp.sympify(value))

    @staticmethod
    def field(component: int, background: sp.Expr = sp.S.Zero) -> "FirstJet":
        return FirstJet(sp.sympify(background), LinearOperator.basis(component))

    def __add__(self, other: "FirstJet") -> "FirstJet":
        return FirstJet(self.background + other.background, self.linear + other.linear)

    def __neg__(self) -> "FirstJet":
        return self.scale(-1)

    def __sub__(self, other: "FirstJet") -> "FirstJet":
        return self + (-other)

    def scale(self, coefficient: sp.Expr) -> "FirstJet":
        return FirstJet(coefficient * self.background, self.linear.scale(coefficient))

    def __mul__(self, other: "FirstJet") -> "FirstJet":
        return FirstJet(
            self.background * other.background,
            self.linear.scale(other.background) + other.linear.scale(self.background),
        )

    def derivative(self, axis: int) -> "FirstJet":
        return FirstJet(
            sp.diff(self.background, COORDINATES[axis]),
            self.linear.derivative(axis),
        )


FZERO = FirstJet()


def _sum(values) -> FirstJet:
    values = tuple(values)
    if not values:
        return FZERO
    return FirstJet(
        sum((value.background for value in values), sp.S.Zero),
        LinearOperator.from_terms(term for value in values for term in value.linear.terms),
    )


@lru_cache(maxsize=1)
def first_geometry() -> dict[str, object]:
    theta = COORDINATES[2]
    background_metric = sp.diag(-1, 1, 1, sp.sin(theta) ** 2)
    background_inverse = sp.diag(-1, 1, 1, sp.sin(theta) ** -2)
    metric = {
        (a, b): FirstJet.field(PAIR_INDEX[tuple(sorted((a, b)))], background_metric[a, b])
        for a, b in product(range(4), repeat=2)
    }
    inverse = {}
    for a, b in product(range(4), repeat=2):
        inverse[(a, b)] = FirstJet(
            background_inverse[a, b],
            LinearOperator.from_terms(
                term
                for i, j in product(range(4), repeat=2)
                for term in metric[(i, j)].linear.scale(
                    -background_inverse[a, i] * background_inverse[j, b]
                ).terms
            ),
        )
    gamma = {
        (target, left, right): _sum(
            inverse[(target, index)]
            * (
                metric[(index, right)].derivative(left)
                + metric[(index, left)].derivative(right)
                - metric[(left, right)].derivative(index)
            ).scale(sp.Rational(1, 2))
            for index in range(4)
        )
        for target, left, right in product(range(4), repeat=3)
    }
    riemann = {
        (target, vector, first, second): gamma[(target, second, vector)].derivative(first)
        - gamma[(target, first, vector)].derivative(second)
        + _sum(
            gamma[(middle, second, vector)] * gamma[(target, first, middle)]
            - gamma[(middle, first, vector)] * gamma[(target, second, middle)]
            for middle in range(4)
        )
        for target, vector, first, second in product(range(4), repeat=4)
    }
    ricci = {
        (a, b): _sum(riemann[(index, a, index, b)] for index in range(4))
        for a, b in product(range(4), repeat=2)
    }
    scalar = _sum(
        inverse[(a, b)] * ricci[(a, b)] for a, b in product(range(4), repeat=2)
    )
    volume = FirstJet(
        sp.sin(theta),
        LinearOperator.from_terms(
            term
            for a, b in product(range(4), repeat=2)
            for term in metric[(a, b)].linear.scale(
                sp.sin(theta) * background_inverse[a, b] / 2
            ).terms
        ),
    )
    return {
        "metric": metric,
        "inverse": inverse,
        "connection": gamma,
        "riemann": riemann,
        "ricci": ricci,
        "scalar": scalar,
        "volume": volume,
    }


def _weyl_lower_and_up(
    geometry: dict[str, object],
) -> tuple[
    dict[tuple[int, int, int, int], FirstJet],
    dict[tuple[int, int, int, int], FirstJet],
]:
    metric = geometry["metric"]
    inverse = geometry["inverse"]
    riemann = geometry["riemann"]
    ricci = geometry["ricci"]
    scalar = geometry["scalar"]
    assert isinstance(metric, dict) and isinstance(inverse, dict)
    assert isinstance(riemann, dict) and isinstance(ricci, dict)
    assert isinstance(scalar, FirstJet)
    lower = {}
    for a, b, c, d in product(range(4), repeat=4):
        riemann_lower = _sum(metric[(a, target)] * riemann[(target, b, c, d)] for target in range(4))
        trace = (
            metric[(a, c)] * ricci[(b, d)]
            - metric[(a, d)] * ricci[(b, c)]
            - metric[(b, c)] * ricci[(a, d)]
            + metric[(b, d)] * ricci[(a, c)]
        ).scale(sp.Rational(1, 2))
        metric_pair = metric[(a, c)] * metric[(b, d)] - metric[(a, d)] * metric[(b, c)]
        lower[(a, b, c, d)] = riemann_lower - trace + scalar * metric_pair.scale(sp.Rational(1, 6))
    raised = {
        (a, b, c, d): _sum(
            inverse[(a, i)]
            * inverse[(b, j)]
            * inverse[(c, k)]
            * inverse[(d, l)]
            * lower[(i, j, k, l)]
            for i, j, k, l in product(range(4), repeat=4)
        )
        for a, b, c, d in product(range(4), repeat=4)
    }
    return lower, raised


def _covariant_divergence_up4(
    tensor: dict[tuple[int, int, int, int], FirstJet],
    gamma: dict[tuple[int, int, int], FirstJet],
) -> dict[tuple[int, int, int], FirstJet]:
    output = {}
    for a, b, c in product(range(4), repeat=3):
        output[(a, b, c)] = _sum(
            (
                tensor[(a, b, c, derivative)].derivative(derivative)
                + _sum(
                    gamma[(a, derivative, target)] * tensor[(target, b, c, derivative)]
                    + gamma[(b, derivative, target)] * tensor[(a, target, c, derivative)]
                    + gamma[(c, derivative, target)] * tensor[(a, b, target, derivative)]
                    + gamma[(derivative, derivative, target)] * tensor[(a, b, c, target)]
                    for target in range(4)
                )
            )
            for derivative in range(4)
        )
    return output


def _relative_momentum(geometry: dict[str, object]) -> dict[tuple[int, int, int, int], FirstJet]:
    inverse = geometry["inverse"]
    assert isinstance(inverse, dict)
    _, weyl = _weyl_lower_and_up(geometry)
    return {
        (a, b, c, d): weyl[(a, b, c, d)].scale(sp.Rational(3, 4))
        - (
            inverse[(a, c)] * inverse[(b, d)]
            - inverse[(a, d)] * inverse[(b, c)]
        ).scale(sp.Rational(1, 4))
        for a, b, c, d in product(range(4), repeat=4)
    }


def _bach_lower(
    geometry: dict[str, object],
    weyl_lower: dict[tuple[int, int, int, int], FirstJet],
) -> dict[tuple[int, int], FirstJet]:
    metric = geometry["metric"]
    inverse = geometry["inverse"]
    gamma = geometry["connection"]
    ricci = geometry["ricci"]
    scalar = geometry["scalar"]
    assert isinstance(metric, dict) and isinstance(inverse, dict)
    assert isinstance(gamma, dict) and isinstance(ricci, dict)
    assert isinstance(scalar, FirstJet)
    schouten = {
        (a, b): (
            ricci[(a, b)] - metric[(a, b)] * scalar.scale(sp.Rational(1, 6))
        ).scale(sp.Rational(1, 2))
        for a, b in product(range(4), repeat=2)
    }
    first_schouten = {}
    for axis, a, b in product(range(4), repeat=3):
        first_schouten[(axis, a, b)] = schouten[(a, b)].derivative(axis) - _sum(
            gamma[(target, axis, a)] * schouten[(target, b)]
            + gamma[(target, axis, b)] * schouten[(a, target)]
            for target in range(4)
        )
    cotton = {}
    for second in range(4):
        for inner in range(4):
            cotton[(inner, inner, second)] = FZERO
        for inner, first in combinations(range(4), 2):
            value = first_schouten[(inner, first, second)] - first_schouten[(first, second, inner)]
            cotton[(inner, first, second)] = value
            cotton[(first, inner, second)] = -value
    divergence = {}
    for first, second in PAIRS:
        contracted = []
        for outer, inner in product(range(4), repeat=2):
            derivative = cotton[(inner, first, second)].derivative(outer) - _sum(
                gamma[(target, outer, inner)] * cotton[(target, first, second)]
                + gamma[(target, outer, first)] * cotton[(inner, target, second)]
                + gamma[(target, outer, second)] * cotton[(inner, first, target)]
                for target in range(4)
            )
            contracted.append(inverse[(outer, inner)] * derivative)
        value = _sum(contracted)
        divergence[(first, second)] = value
        divergence[(second, first)] = value
    schouten_up = {
        (a, b): _sum(
            inverse[(a, left)] * inverse[(b, right)] * schouten[(left, right)]
            for left, right in product(range(4), repeat=2)
        )
        for a, b in product(range(4), repeat=2)
    }
    algebraic = {
        (a, b): _sum(
            schouten_up[(inner, outer)] * weyl_lower[(a, inner, b, outer)]
            for inner, outer in product(range(4), repeat=2)
        )
        for a, b in product(range(4), repeat=2)
    }
    return {
        (a, b): divergence[(a, b)] + algebraic[(a, b)]
        for a, b in product(range(4), repeat=2)
    }


@lru_cache(maxsize=1)
def relative_euler_rows_symbolic() -> tuple[LinearOperator, ...]:
    """Coordinate-density Hessian derived from the two metric actions."""

    geometry = first_geometry()
    metric = geometry["metric"]
    inverse = geometry["inverse"]
    ricci = geometry["ricci"]
    scalar = geometry["scalar"]
    volume = geometry["volume"]
    assert isinstance(metric, dict) and isinstance(inverse, dict)
    assert isinstance(ricci, dict) and isinstance(scalar, FirstJet)
    assert isinstance(volume, FirstJet)
    weyl_lower, _ = _weyl_lower_and_up(geometry)
    bach = _bach_lower(geometry, weyl_lower)
    einstein = {
        (a, b): ricci[(a, b)]
        - metric[(a, b)] * scalar.scale(sp.Rational(1, 2))
        + metric[(a, b)].scale(sp.Rational(1, 2))
        for a, b in product(range(4), repeat=2)
    }
    rows = []
    for a, b in PAIRS:
        multiplicity = 1 if a == b else 2
        raised = _sum(
            inverse[(a, left)]
            * inverse[(b, right)]
            * (einstein[(left, right)] - bach[(left, right)].scale(3))
            for left, right in product(range(4), repeat=2)
        )
        rows.append((volume * raised.scale(sp.Rational(multiplicity, 2))).linear)
    return tuple(rows)


def symbolic_green_current() -> tuple[BilinearOperator, ...]:
    """Ordered Green current of the symbolic coordinate-density Hessian."""

    raw = [[] for _ in range(4)]
    for output, row in enumerate(relative_euler_rows_symbolic()):
        for incoming, word, coefficient in row.terms:
            for position, axis in enumerate(word):
                prefix = word[:position]
                suffix = word[position + 1 :]
                for mask in range(1 << len(prefix)):
                    coefficient_word = tuple(
                        prefix[index]
                        for index in range(len(prefix))
                        if mask & (1 << index)
                    )
                    left_word = tuple(
                        prefix[index]
                        for index in range(len(prefix))
                        if not mask & (1 << index)
                    )
                    value = coefficient
                    for derivative in coefficient_word:
                        value = sp.diff(value, COORDINATES[derivative])
                    raw[axis].append(
                        (output, left_word, incoming, suffix, (-1) ** position * value)
                    )
    result = []
    for terms in raw:
        current = BilinearOperator.from_terms(terms)
        result.append((current - current.koszul_swapped((0,) * 10)).scale(sp.Rational(1, 2)))
    return tuple(result)


def _outer_coefficient_test(
    coefficient: FirstJet,
    test_component: int,
    test_word: tuple[int, ...],
) -> BilinearOperator:
    return BilinearOperator.from_terms(
        (field, word, test_component, test_word, value)
        for field, word, value in coefficient.linear.terms
    )


@lru_cache(maxsize=1)
def relative_lee_wald_current_symbolic() -> tuple[BilinearOperator, ...]:
    """Return the four symbolic coordinate-density current components."""

    geometry = first_geometry()
    gamma = geometry["connection"]
    volume = geometry["volume"]
    assert isinstance(gamma, dict) and isinstance(volume, FirstJet)
    momentum = _relative_momentum(geometry)
    divergence = _covariant_divergence_up4(momentum, gamma)
    components = []
    for mu in range(4):
        terms = []
        for a, b in product(range(4), repeat=2):
            test_component = PAIR_INDEX[tuple(sorted((a, b)))]
            for derivative in range(4):
                coefficient = (volume * momentum[(mu, a, b, derivative)]).scale(2)
                terms.extend(_outer_coefficient_test(coefficient, test_component, (derivative,)).terms)
                for target in range(4):
                    connection_first = (
                        volume
                        * momentum[(mu, a, b, derivative)]
                        * gamma[(target, derivative, a)]
                    ).scale(-2)
                    connection_second = (
                        volume
                        * momentum[(mu, a, b, derivative)]
                        * gamma[(target, derivative, b)]
                    ).scale(-2)
                    terms.extend(
                        _outer_coefficient_test(
                            connection_first,
                            PAIR_INDEX[tuple(sorted((target, b)))],
                            (),
                        ).terms
                    )
                    terms.extend(
                        _outer_coefficient_test(
                            connection_second,
                            PAIR_INDEX[tuple(sorted((a, target)))],
                            (),
                        ).terms
                    )
            algebraic = (volume * divergence[(mu, a, b)]).scale(-2)
            terms.extend(_outer_coefficient_test(algebraic, test_component, ()).terms)
        first_on_second = BilinearOperator.from_terms(terms)
        components.append(first_on_second - first_on_second.koszul_swapped((0,) * 10))
    return tuple(components)


def relative_lee_wald_current() -> tuple[BilinearOperator, ...]:
    """Return the exact equatorial coefficient table of the relative current."""

    return tuple(component.at_base_point() for component in relative_lee_wald_current_symbolic())


def lee_wald_divergence() -> BilinearOperator:
    return BilinearOperator.from_terms(
        term
        for axis, component in enumerate(relative_lee_wald_current_symbolic())
        for term in component.derivative(axis).at_base_point().terms
    )


def canonical_green_current() -> tuple[BilinearOperator, ...]:
    from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
        antisymmetric_green_current_profiles,
    )

    return tuple(
        BilinearOperator.from_terms(
            (left, left_word, right, right_word, profile.get((), 0))
            for (left, left_word, right, right_word), profile in component.items()
        )
        for component in antisymmetric_green_current_profiles()
    )


def canonical_green_divergence() -> BilinearOperator:
    from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
        antisymmetric_green_current_profiles,
        current_divergence,
    )

    rows = current_divergence(antisymmetric_green_current_profiles())
    return BilinearOperator.from_terms(
        (left, left_word, right, right_word, coefficient)
        for (left, left_word, right, right_word), coefficient in rows.items()
    )


def _theta_normal_form(value: sp.Expr) -> sp.Expr:
    return sp.trigsimp(sp.cancel(value))


def _normalized_bilinear(operator: BilinearOperator) -> BilinearOperator:
    return BilinearOperator.from_terms(
        (left, left_word, right, right_word, value)
        for left, left_word, right, right_word, coefficient in operator.terms
        if (value := _theta_normal_form(coefficient)) != 0
    )


def _superpotential_divergence(
    potential: dict[tuple[int, int], BilinearOperator],
) -> tuple[BilinearOperator, ...]:
    output = [BilinearOperator() for _ in range(4)]
    for (left, right), value in potential.items():
        output[left] = output[left] + value.derivative(right)
        output[right] = output[right] - value.derivative(left)
    return tuple(_normalized_bilinear(value) for value in output)


def _primitive_at_order(
    current: tuple[BilinearOperator, ...], order: int
) -> dict[tuple[int, int], BilinearOperator]:
    """Solve the constant-symbol horizontal equation at one jet order."""

    blocks: dict[tuple, dict[tuple, sp.Expr]] = defaultdict(dict)
    for component, operator in enumerate(current):
        for field_left, left_word, field_right, right_word, coefficient in operator.terms:
            if len(left_word) + len(right_word) != order:
                continue
            signature = (
                field_left,
                field_right,
                tuple(sorted((component, *left_word, *right_word))),
            )
            blocks[signature][(component, left_word, right_word)] = coefficient

    result: dict[tuple[int, int], list[tuple]] = defaultdict(list)
    for (field_left, field_right, _), target in blocks.items():
        candidates = set()
        for component, left_word, right_word in target:
            for slot, word in enumerate((left_word, right_word)):
                for position, axis in enumerate(word):
                    if axis == component:
                        continue
                    reduced = word[:position] + word[position + 1 :]
                    candidate_left = reduced if slot == 0 else left_word
                    candidate_right = right_word if slot == 0 else reduced
                    candidates.add(
                        (
                            min(component, axis),
                            max(component, axis),
                            candidate_left,
                            candidate_right,
                        )
                    )
        candidates = sorted(candidates)
        row_keys = set(target)
        for first, second, left_word, right_word in candidates:
            for component, axis in ((first, second), (second, first)):
                row_keys.add((component, tuple(sorted((*left_word, axis))), right_word))
                row_keys.add((component, left_word, tuple(sorted((*right_word, axis)))))
        rows = sorted(row_keys)
        row_index = {key: index for index, key in enumerate(rows)}
        matrix = sp.zeros(len(rows), len(candidates))
        source = sp.Matrix([target.get(key, sp.S.Zero) for key in rows])
        for column, (first, second, left_word, right_word) in enumerate(candidates):
            for component, axis, sign in ((first, second, 1), (second, first, -1)):
                matrix[row_index[(component, tuple(sorted((*left_word, axis))), right_word)], column] += sign
                matrix[row_index[(component, left_word, tuple(sorted((*right_word, axis))))], column] += sign
        solution_set = sp.linsolve((matrix, source))
        if solution_set == sp.EmptySet:
            raise AssertionError(
                f"horizontal symbol is not exact at order {order}: "
                f"fields {(field_left, field_right)}"
            )
        solution = next(iter(solution_set))
        free = set().union(*(value.free_symbols for value in solution))
        # The only legitimate free symbols are the parameters introduced by
        # linsolve.  Background theta dependence is already present in source.
        free -= {COORDINATES[2]}
        normalized = [
            _theta_normal_form(value.subs({symbol: 0 for symbol in free}))
            for value in solution
        ]
        if any(_theta_normal_form(value) != 0 for value in matrix * sp.Matrix(normalized) - source):
            raise AssertionError("normalized horizontal-symbol solution failed replay")
        for (first, second, left_word, right_word), coefficient in zip(candidates, normalized):
            if coefficient != 0:
                result[(first, second)].append(
                    (field_left, left_word, field_right, right_word, coefficient)
                )
    return {
        pair: BilinearOperator.from_terms(terms)
        for pair, terms in result.items()
    }


_FUNCTION_BASIS = (
    (0, -5),
    (0, -3),
    (0, -1),
    (0, 1),
    (1, -4),
    (1, -2),
    (1, 0),
)
_OUTPUT_FUNCTION_BASIS = (*_FUNCTION_BASIS, (1, -6))


def _basis_function(label: tuple[int, int]) -> sp.Expr:
    cosine_power, sine_power = label
    theta = COORDINATES[2]
    return sp.cos(theta) ** cosine_power * sp.sin(theta) ** sine_power


def _basis_derivative(label: tuple[int, int]) -> dict[tuple[int, int], sp.Rational]:
    cosine_power, sine_power = label
    if cosine_power == 0:
        return {(1, sine_power - 1): sp.Rational(sine_power)}
    return {
        (0, sine_power - 1): sp.Rational(sine_power),
        (0, sine_power + 1): sp.Rational(-(sine_power + 1)),
    }


def _basis_decomposition(value: sp.Expr) -> dict[tuple[int, int], sp.Rational]:
    theta = COORDINATES[2]
    sine, cosine = sp.symbols("sine cosine")
    expression = sp.together(
        sp.expand_trig(_theta_normal_form(value)).subs(
            {sp.sin(theta): sine, sp.cos(theta): cosine}
        )
    )
    numerator, denominator = sp.fraction(expression)
    relation = sp.Poly(cosine**2 + sine**2 - 1, cosine)
    numerator = sp.rem(sp.Poly(numerator, cosine), relation).as_expr()
    denominator = sp.rem(sp.Poly(denominator, cosine), relation).as_expr()
    expression = sp.expand(sp.cancel(numerator / denominator))
    if cosine in sp.fraction(expression)[1].free_symbols:
        raise ValueError(f"non-Laurent theta coefficient: {value}")
    output: dict[tuple[int, int], sp.Rational] = defaultdict(lambda: sp.S.Zero)
    for term in sp.Add.make_args(expression):
        powers = term.as_powers_dict()
        cosine_power = powers.get(cosine, 0)
        sine_power = powers.get(sine, 0)
        coefficient = sp.cancel(term / (cosine**cosine_power * sine**sine_power))
        if cosine_power not in (0, 1) or not coefficient.is_Rational:
            raise ValueError(f"coefficient left the declared Laurent basis: {value}")
        output[(int(cosine_power), int(sine_power))] += sp.Rational(coefficient)
    return {label: coefficient for label, coefficient in output.items() if coefficient}


@lru_cache(maxsize=1)
def horizontal_improvement() -> dict[tuple[int, int], BilinearOperator]:
    """Return ``U`` with ``omega_LW-omega_G=partial_nu U^{mu nu}``."""

    current = tuple(
        _normalized_bilinear(left - right)
        for left, right in zip(relative_lee_wald_current_symbolic(), symbolic_green_current())
    )
    targets: dict[tuple[int, int], dict[tuple, sp.Rational]] = defaultdict(
        lambda: defaultdict(lambda: sp.S.Zero)
    )
    candidates: dict[tuple[int, int], set[tuple]] = defaultdict(set)
    for component, operator in enumerate(current):
        for field_left, left_word, field_right, right_word, coefficient in operator.terms:
            field_pair = (field_left, field_right)
            for basis, value in _basis_decomposition(coefficient).items():
                if basis not in _FUNCTION_BASIS:
                    raise AssertionError(f"current coefficient basis drifted: {basis}")
                targets[field_pair][(component, left_word, right_word, basis)] += value
            for slot, word in enumerate((left_word, right_word)):
                for position, axis in enumerate(word):
                    if axis == component:
                        continue
                    reduced = word[:position] + word[position + 1 :]
                    candidates[field_pair].add(
                        (
                            min(component, axis),
                            max(component, axis),
                            reduced if slot == 0 else left_word,
                            right_word if slot == 0 else reduced,
                        )
                    )

    potential_terms: dict[tuple[int, int], list[tuple]] = defaultdict(list)
    for field_pair, field_candidates in sorted(candidates.items()):
        field_left, field_right = field_pair
        columns = [
            (*candidate, basis)
            for candidate in sorted(field_candidates)
            for basis in _FUNCTION_BASIS
        ]
        row_keys = set(targets[field_pair])
        contributions: list[dict[tuple, sp.Rational]] = []
        for first, second, left_word, right_word, basis in columns:
            column: dict[tuple, sp.Rational] = defaultdict(lambda: sp.S.Zero)
            for component, axis, sign in ((first, second, 1), (second, first, -1)):
                column[(component, tuple(sorted((*left_word, axis))), right_word, basis)] += sign
                column[(component, left_word, tuple(sorted((*right_word, axis))), basis)] += sign
                if axis == 2:
                    for derivative_basis, value in _basis_derivative(basis).items():
                        column[(component, left_word, right_word, derivative_basis)] += sign * value
            column = {key: value for key, value in column.items() if value}
            row_keys.update(column)
            contributions.append(column)
        rows = sorted(row_keys)
        row_index = {key: index for index, key in enumerate(rows)}
        matrix = sp.MutableSparseMatrix(len(rows), len(columns), {})
        for column_index, column in enumerate(contributions):
            for key, value in column.items():
                matrix[row_index[key], column_index] = value
        source = sp.Matrix([targets[field_pair].get(key, sp.S.Zero) for key in rows])
        solution_set = sp.linsolve((matrix, source))
        if solution_set == sp.EmptySet:
            raise AssertionError(f"no Laurent horizontal improvement for fields {field_pair}")
        solution = next(iter(solution_set))
        free = set().union(*(value.free_symbols for value in solution))
        solution = [sp.Rational(value.subs({symbol: 0 for symbol in free})) for value in solution]
        if matrix * sp.Matrix(solution) != source:
            raise AssertionError(f"Laurent horizontal improvement replay failed for {field_pair}")
        grouped: dict[tuple, sp.Expr] = defaultdict(lambda: sp.S.Zero)
        for (first, second, left_word, right_word, basis), value in zip(columns, solution):
            if value:
                grouped[(first, second, left_word, right_word)] += value * _basis_function(basis)
        for (first, second, left_word, right_word), coefficient in grouped.items():
            coefficient = _theta_normal_form(coefficient)
            if coefficient:
                potential_terms[(first, second)].append(
                    (field_left, left_word, field_right, right_word, coefficient)
                )

    potential = {
        pair: BilinearOperator.from_terms(terms)
        for pair, terms in potential_terms.items()
    }
    # The current is antisymmetric in field space, so average the primitive
    # with its antisymmetric field-slot part without changing its divergence.
    potential = {
        pair: _normalized_bilinear(
            (value - value.koszul_swapped((0,) * 10)).scale(sp.Rational(1, 2))
        )
        for pair, value in potential.items()
    }
    difference = _superpotential_divergence(potential)
    defect = tuple(
        _normalized_bilinear(value - reconstructed)
        for value, reconstructed in zip(current, difference)
    )
    if any(value.terms for value in defect):
        first = next(value.terms[0] for value in defect if value.terms)
        raise AssertionError(f"horizontal improvement left a residual term: {first}")
    return potential


def horizontal_improvement_defect() -> tuple[BilinearOperator, ...]:
    difference = tuple(
        _normalized_bilinear(left - right)
        for left, right in zip(relative_lee_wald_current_symbolic(), symbolic_green_current())
    )
    divergence = _superpotential_divergence(horizontal_improvement())
    return tuple(
        _normalized_bilinear(value - reconstructed)
        for value, reconstructed in zip(difference, divergence)
    )


def comparison_summary() -> dict[str, object]:
    lee_wald = relative_lee_wald_current()
    green = canonical_green_current()
    defects = tuple(left - right for left, right in zip(lee_wald, green))
    divergence_defect = lee_wald_divergence() - canonical_green_divergence()
    improvement = horizontal_improvement()
    improvement_defect = horizontal_improvement_defect()
    return {
        "lee_wald_component_term_counts": [len(value.terms) for value in lee_wald],
        "green_component_term_counts": [len(value.terms) for value in green],
        "difference_component_term_counts": [len(value.terms) for value in defects],
        "difference_zero": all(not value.terms for value in defects),
        "maximum_difference_order": max((value.maximum_total_order for value in defects), default=-1),
        "divergence_difference_term_count": len(divergence_defect.terms),
        "improvement_component_term_counts": {
            f"{left}{right}": len(improvement.get((left, right), BilinearOperator()).terms)
            for left in range(4)
            for right in range(left + 1, 4)
        },
        "improvement_defect_term_count": sum(len(value.terms) for value in improvement_defect),
    }


if __name__ == "__main__":
    print(comparison_summary())
