"""Exact five-stabilizer precomposition of the relative Hessian current."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations_with_replacement

import sympy as sp

from bridge.einstein_sector.product_taylor_engine import BASE_POINT, COORDINATES, PAIRS
from d_quotient_classical.relative.einstein_weyl_relative_hessian_green_current_cone import (
    relative_operator_terms,
)


Profile = dict[tuple[int, ...], Fraction]
LinearTerm = tuple[int, int, tuple[int, ...], Profile]
CurrentKey = tuple[int, tuple[int, ...], int, tuple[int, ...]]


def _rational(value: sp.Expr) -> Fraction:
    reduced = sp.cancel(value.subs(BASE_POINT))
    if reduced == 0:
        return Fraction()
    if not reduced.is_Rational:
        raise ValueError(f"stabilizer coefficient is not rational at the base point: {reduced}")
    return Fraction(int(reduced.p), int(reduced.q))


def _words(maximum_order: int):
    yield ()
    for order in range(1, maximum_order + 1):
        yield from combinations_with_replacement(range(4), order)


@lru_cache(maxsize=None)
def coefficient_profile(expression: sp.Expr, maximum_order: int = 4) -> Profile:
    profile = {}
    for word in _words(maximum_order):
        value = expression
        for axis in word:
            value = sp.diff(value, COORDINATES[axis])
        rational = _rational(value)
        if rational:
            profile[word] = rational
    return profile


def stabilizer_vectors() -> dict[str, sp.Matrix]:
    _, _, theta, phi = COORDINATES
    return {
        "H": sp.Matrix([1, 0, 0, 0]),
        "P_x": sp.Matrix([0, 1, 0, 0]),
        "J_1": sp.Matrix([0, 0, 0, 1]),
        "J_2": sp.Matrix([0, 0, sp.cos(phi), -sp.cot(theta) * sp.sin(phi)]),
        "J_3": sp.Matrix([0, 0, sp.sin(phi), sp.cot(theta) * sp.cos(phi)]),
    }


def _merge_linear(raw: list[LinearTerm]) -> list[LinearTerm]:
    combined: dict[tuple, dict[tuple[int, ...], Fraction]] = defaultdict(lambda: defaultdict(Fraction))
    for output, incoming, word, profile in raw:
        for derivative, coefficient in profile.items():
            combined[(output, incoming, tuple(sorted(word)))][derivative] += coefficient
    result = []
    for (output, incoming, word), profile in sorted(combined.items()):
        cleaned = {derivative: coefficient for derivative, coefficient in profile.items() if coefficient}
        if cleaned:
            result.append((output, incoming, word, cleaned))
    return result


def stabilizer_action(generator: sp.Matrix) -> list[LinearTerm]:
    """Tensor Lie derivative plus the fixed-bundle Maxwell lift ``i_X da``."""

    raw: list[LinearTerm] = []
    pair_index = {pair: index for index, pair in enumerate(PAIRS)}
    for output, (mu, nu) in enumerate(PAIRS):
        for rho in range(4):
            raw.append((output, output, (rho,), coefficient_profile(generator[rho])))
            first_input = pair_index[tuple(sorted((rho, nu)))]
            second_input = pair_index[tuple(sorted((mu, rho)))]
            raw.append(
                (
                    output,
                    first_input,
                    (),
                    coefficient_profile(sp.diff(generator[rho], COORDINATES[mu])),
                )
            )
            raw.append(
                (
                    output,
                    second_input,
                    (),
                    coefficient_profile(sp.diff(generator[rho], COORDINATES[nu])),
                )
            )
    for mu in range(4):
        output = 10 + mu
        for rho in range(4):
            profile = coefficient_profile(generator[rho])
            raw.append((output, output, (rho,), profile))
            raw.append((output, 10 + rho, (mu,), {word: -value for word, value in profile.items()}))
    return _merge_linear(raw)


def _add(table: dict, key: tuple, value: Fraction) -> None:
    if value:
        table[key] += value


@lru_cache(maxsize=1)
def antisymmetric_green_current_profiles() -> list[dict[CurrentKey, Profile]]:
    """Return base values and first coefficient jets of the cyclic Green current."""

    raw = [defaultdict(lambda: defaultdict(Fraction)) for _ in range(4)]
    derivative_words = [(), (0,), (1,), (2,), (3,)]
    for output, incoming, word, profile in relative_operator_terms():
        for position, axis in enumerate(word):
            prefix = word[:position]
            suffix = word[position + 1 :]
            for mask in range(1 << len(prefix)):
                coefficient_word = tuple(sorted(prefix[index] for index in range(len(prefix)) if mask & (1 << index)))
                left_word = tuple(sorted(prefix[index] for index in range(len(prefix)) if not mask & (1 << index)))
                sign = Fraction((-1) ** position)
                key = (output, left_word, incoming, suffix)
                for derivative in derivative_words:
                    raw[axis][key][derivative] += sign * profile.get(tuple(sorted((*coefficient_word, *derivative))), 0)
    result = []
    for component in raw:
        antisymmetric = defaultdict(lambda: defaultdict(Fraction))
        for (left, left_word, right, right_word), profile in component.items():
            for derivative, coefficient in profile.items():
                antisymmetric[(left, left_word, right, right_word)][derivative] += coefficient / 2
                antisymmetric[(right, right_word, left, left_word)][derivative] -= coefficient / 2
        result.append(
            {
                key: {word: value for word, value in profile.items() if value}
                for key, profile in antisymmetric.items()
                if any(profile.values())
            }
        )
    return result


def _compose_second_slot(
    current: list[dict[CurrentKey, Profile]], action: list[LinearTerm]
) -> list[dict[CurrentKey, Profile]]:
    by_output: dict[int, list[LinearTerm]] = defaultdict(list)
    for term in action:
        by_output[term[0]].append(term)
    result = [defaultdict(lambda: defaultdict(Fraction)) for _ in range(4)]
    for component, rows in enumerate(current):
        for (left, left_word, action_output, differentiated_word), current_profile in rows.items():
            for _, incoming, action_word, action_profile in by_output[action_output]:
                for mask in range(1 << len(differentiated_word)):
                    coefficient_word = tuple(
                        sorted(
                            differentiated_word[index]
                            for index in range(len(differentiated_word))
                            if mask & (1 << index)
                        )
                    )
                    field_word = tuple(
                        sorted(
                            (*action_word,)
                            + tuple(
                                differentiated_word[index]
                                for index in range(len(differentiated_word))
                                if not mask & (1 << index)
                            )
                        )
                    )
                    key = (left, left_word, incoming, field_word)
                    base_current = current_profile.get((), 0)
                    base_action = action_profile.get(coefficient_word, 0)
                    result[component][key][()] += base_current * base_action
                    for axis in range(4):
                        result[component][key][(axis,)] += (
                            current_profile.get((axis,), 0) * base_action
                            + base_current
                            * action_profile.get(tuple(sorted((*coefficient_word, axis))), 0)
                        )
    return [
        {
            key: {word: value for word, value in profile.items() if value}
            for key, profile in component.items()
            if any(profile.values())
        }
        for component in result
    ]


def polarized_noether_current(action: list[LinearTerm]) -> list[dict[CurrentKey, Profile]]:
    composed = _compose_second_slot(antisymmetric_green_current_profiles(), action)
    result = []
    for component in composed:
        symmetric = defaultdict(lambda: defaultdict(Fraction))
        for (left, left_word, right, right_word), profile in component.items():
            for derivative, coefficient in profile.items():
                symmetric[(left, left_word, right, right_word)][derivative] += coefficient / 2
                symmetric[(right, right_word, left, left_word)][derivative] += coefficient / 2
        result.append(
            {
                key: {word: value for word, value in profile.items() if value}
                for key, profile in symmetric.items()
                if any(profile.values())
            }
        )
    return result


def current_divergence(current: list[dict[CurrentKey, Profile]]) -> dict[CurrentKey, Fraction]:
    output: dict[CurrentKey, Fraction] = defaultdict(Fraction)
    for axis, component in enumerate(current):
        for (left, left_word, right, right_word), profile in component.items():
            _add(output, (left, left_word, right, right_word), profile.get((axis,), 0))
            _add(output, (left, tuple(sorted((*left_word, axis))), right, right_word), profile.get((), 0))
            _add(output, (left, left_word, right, tuple(sorted((*right_word, axis)))), profile.get((), 0))
    return {key: value for key, value in output.items() if value}


def _compose_operator_action(terms: list[tuple], action: list[LinearTerm]) -> list[tuple]:
    by_output: dict[int, list[LinearTerm]] = defaultdict(list)
    for term in action:
        by_output[term[0]].append(term)
    output: dict[tuple, Fraction] = defaultdict(Fraction)
    for equation, action_output, word, profile in terms:
        base_operator = profile.get((), 0)
        for _, incoming, action_word, action_profile in by_output[action_output]:
            for mask in range(1 << len(word)):
                coefficient_word = tuple(sorted(word[index] for index in range(len(word)) if mask & (1 << index)))
                field_word = tuple(
                    sorted(
                        (*action_word,)
                        + tuple(word[index] for index in range(len(word)) if not mask & (1 << index))
                    )
                )
                _add(output, (equation, incoming, field_word), base_operator * action_profile.get(coefficient_word, 0))
    return [(*key, value) for key, value in sorted(output.items()) if value]


def polarized_euler_source(action: list[LinearTerm]) -> dict[CurrentKey, Fraction]:
    """Return the polarized source dictated by the variational identity."""

    terms = relative_operator_terms()
    composed = _compose_operator_action(terms, action)
    action_base = [(output, incoming, word, profile.get((), 0)) for output, incoming, word, profile in action if profile.get((), 0)]
    operator_base = [(output, incoming, word, profile.get((), 0)) for output, incoming, word, profile in terms if profile.get((), 0)]
    one_sided: dict[CurrentKey, Fraction] = defaultdict(Fraction)
    for equation, incoming, word, coefficient in composed:
        _add(one_sided, (equation, (), incoming, word), coefficient)
    actions_by_output: dict[int, list[tuple]] = defaultdict(list)
    for row in action_base:
        actions_by_output[row[0]].append(row)
    for equation, incoming, word, coefficient in operator_base:
        for _, action_input, action_word, action_coefficient in actions_by_output[equation]:
            _add(
                one_sided,
                (incoming, word, action_input, action_word),
                -coefficient * action_coefficient,
            )
    symmetric: dict[CurrentKey, Fraction] = defaultdict(Fraction)
    for (left, left_word, right, right_word), coefficient in one_sided.items():
        _add(symmetric, (left, left_word, right, right_word), coefficient / 2)
        _add(symmetric, (right, right_word, left, left_word), coefficient / 2)
    return {key: value for key, value in symmetric.items() if value}


def exact_data() -> dict[str, object]:
    metric = sp.diag(-1, 1, 1, sp.sin(COORDINATES[2]) ** 2)
    field = sp.zeros(4)
    field[2, 3] = sp.sin(COORDINATES[2])
    field[3, 2] = -field[2, 3]
    generators = stabilizer_vectors()
    records = {}
    for name, vector in generators.items():
        action = stabilizer_action(vector)
        current = polarized_noether_current(action)
        divergence = current_divergence(current)
        source = polarized_euler_source(action)
        defect = {key: divergence.get(key, 0) - source.get(key, 0) for key in set(divergence) | set(source)}
        defect = {key: value for key, value in defect.items() if value}
        records[name] = {
            "vector": [str(value) for value in vector],
            "action_term_count": len(action),
            "current_component_term_counts": [len(component) for component in current],
            "divergence_source_term_count": len(source),
            "divergence_defect_count": len(defect),
            "polarization_symmetric": all(
                profile == current[component].get((right, right_word, left, left_word))
                for component, rows in enumerate(current)
                for (left, left_word, right, right_word), profile in rows.items()
            ),
        }
        if defect:
            records[name]["first_defect"] = str(next(iter(defect.items())))
    # Direct geometric invariance checks prevent a mislabeled vector basis.
    for name, vector in generators.items():
        metric_lie = sp.Matrix(
            4,
            4,
            lambda mu, nu: sp.simplify(
                sum(vector[rho] * sp.diff(metric[mu, nu], COORDINATES[rho]) for rho in range(4))
                + sum(metric[rho, nu] * sp.diff(vector[rho], COORDINATES[mu]) for rho in range(4))
                + sum(metric[mu, rho] * sp.diff(vector[rho], COORDINATES[nu]) for rho in range(4))
            ),
        )
        if metric_lie != sp.zeros(4):
            raise AssertionError(f"{name} is not Killing")
        # The magnetic field is the sphere area form, so its ordinary tensor
        # Lie derivative must also vanish for every declared stabilizer.
        field_lie = sp.Matrix(
            4,
            4,
            lambda mu, nu: sp.simplify(
                sum(vector[rho] * sp.diff(field[mu, nu], COORDINATES[rho]) for rho in range(4))
                + sum(field[rho, nu] * sp.diff(vector[rho], COORDINATES[mu]) for rho in range(4))
                + sum(field[mu, rho] * sp.diff(vector[rho], COORDINATES[nu]) for rho in range(4))
            ),
        )
        if field_lie != sp.zeros(4):
            raise AssertionError(f"{name} does not preserve the magnetic background")
    return {"generator_basis": list(generators), "records": records}
