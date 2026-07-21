"""Exact symbolic assembly engine for the positive-mixed replacement-112 q1."""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import sympy as sp

from closed_universe_observers import berger_108_row_q1_pbw_replay as old_replay
from closed_universe_observers import berger_108_row_nonlinear_clock_second_jet as second_jet
from closed_universe_observers.berger_108_row_component_jet_contract import _pbw_word
from closed_universe_observers import generate_berger_global_detector_rods as rods


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
OLD_COMPLETION = P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET_PAYLOAD.json"
PHI2 = P / "certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT_PAYLOAD.json"
INTERFACE = P / "certificates/BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE_PAYLOAD.json"
REPLACEMENT = P / "certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY_PAYLOAD.json"

Generator = tuple[str, str, tuple[int, ...], tuple[int, int, int, int]]
Monomial = tuple[Generator, ...]
Polynomial = dict[Monomial, sp.Expr]
Operator = dict[tuple[int, int, tuple[int, ...]], Polynomial]
GradedOperator = dict[tuple[int, int], Operator]

SA, CA, SU, CU = sp.symbols("sa ca su cu", nonzero=True, real=True)
R10, R58, J = sp.symbols("r10 r58 j")
SYMBOLS = {"sa": SA, "ca": CA, "su": SU, "cu": CU}
PHI2_VALUES = {
    "Phi2_00": sp.Rational(428, 567),
    "Phi2_11": -sp.Rational(29, 21),
    "Phi2_22": -sp.Rational(29, 21),
    "Phi2_33": -sp.Rational(6, 7),
}
RODS = ("R0_1", "R0_2", "R0_3", "R1_1", "R1_2", "R1_3", "R0_4", "R1_4")
OMEGA = sp.sqrt(58) / 6


def background_symbolize(value: sp.Expr) -> sp.Expr:
    return value.xreplace({sp.sqrt(10): R10, sp.sqrt(58): R58, sp.I: J})


def scalar(value: tuple[Any, Any]) -> sp.Expr:
    rational, root = value
    return sp.Rational(rational.numerator, rational.denominator) + sp.sqrt(10) * sp.Rational(root.numerator, root.denominator)


def serialized_scalar(value: dict[str, Any]) -> sp.Expr:
    q, r = value["rational"], value["sqrt10"]
    return sp.Rational(q["numerator"], q["denominator"]) + sp.sqrt(10) * sp.Rational(r["numerator"], r["denominator"])


@lru_cache(maxsize=1)
def unit_ideal() -> sp.GroebnerBasis:
    return sp.groebner([CA**2 + SA**2 - 1, CU**2 + SU**2 - 1], CA, CU, SA, SU, order="lex", extension=sp.sqrt(10))


@lru_cache(maxsize=None)
def reduce_expr(value: sp.Expr) -> sp.Expr:
    numerator, denominator = sp.cancel(value).as_numer_denom()
    ideal = unit_ideal()
    return sp.factor(ideal.reduce(sp.expand(numerator))[1] / ideal.reduce(sp.expand(denominator))[1])


def normalize(terms: list[tuple[sp.Expr, tuple[Generator, ...]]]) -> Polynomial:
    result: dict[Monomial, sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for coefficient, factors in terms:
        result[tuple(sorted(factors))] += coefficient
    return {monomial: sp.cancel(coefficient) for monomial, coefficient in sorted(result.items()) if coefficient != 0}


def add_poly(*values: Polynomial) -> Polynomial:
    return normalize([(coefficient, monomial) for value in values for monomial, coefficient in value.items()])


def scale_poly(value: Polynomial, coefficient: sp.Expr) -> Polynomial:
    return normalize([(coefficient * item, monomial) for monomial, item in value.items()])


def multiply_poly(left: Polynomial, right: Polynomial) -> Polynomial:
    return normalize([(a * b, left_monomial + right_monomial) for left_monomial, a in left.items() for right_monomial, b in right.items()])


def derivative(value: Polynomial, axis: int) -> Polynomial:
    terms: list[tuple[sp.Expr, tuple[Generator, ...]]] = []
    for monomial, coefficient in value.items():
        for position, factor in enumerate(monomial):
            kind, name, vertical, spacetime = factor
            if kind == "parameter":
                continue
            word = (axis,) + tuple(direction for direction, count in enumerate(spacetime) for _ in range(count))
            for reduced_word, pbw_coefficient in _pbw_word(word):
                factors = list(monomial)
                factors[position] = (kind, name, vertical, tuple(reduced_word.count(direction) for direction in range(4)))
                terms.append((coefficient * scalar(pbw_coefficient), tuple(factors)))
    return normalize(terms)


def add_term(operator: Operator, key: tuple[int, int, tuple[int, ...]], coefficient: Polynomial) -> None:
    operator[key] = add_poly(operator.get(key, {}), coefficient)
    if not operator[key]:
        del operator[key]


def add_operators(*operators: Operator) -> Operator:
    result: Operator = {}
    for operator in operators:
        for key, coefficient in operator.items():
            add_term(result, key, coefficient)
    return result


def apply_word(left_word: tuple[int, ...], coefficient: Polynomial, right_word: tuple[int, ...]) -> dict[tuple[int, ...], Polynomial]:
    states: dict[tuple[int, ...], Polynomial] = {right_word: coefficient}
    for axis in reversed(left_word):
        updated: dict[tuple[int, ...], Polynomial] = {}
        for current_word, current_coefficient in states.items():
            differentiated = derivative(current_coefficient, axis)
            if differentiated:
                updated[current_word] = add_poly(updated.get(current_word, {}), differentiated)
            for reduced_word, pbw_coefficient in _pbw_word((axis, *current_word)):
                contribution = scale_poly(current_coefficient, scalar(pbw_coefficient))
                updated[reduced_word] = add_poly(updated.get(reduced_word, {}), contribution)
        states = {key: value for key, value in updated.items() if value}
    return states


def compose(left: Operator, right: Operator) -> Operator:
    left_by_input: dict[int, list[tuple[int, tuple[int, ...], Polynomial]]] = defaultdict(list)
    right_by_output: dict[int, list[tuple[int, tuple[int, ...], Polynomial]]] = defaultdict(list)
    for (row, column, word), coefficient in left.items():
        left_by_input[column].append((row, word, coefficient))
    for (row, column, word), coefficient in right.items():
        right_by_output[row].append((column, word, coefficient))
    result: Operator = {}
    for middle in sorted(set(left_by_input) & set(right_by_output)):
        for row, left_word, left_coefficient in left_by_input[middle]:
            for column, right_word, right_coefficient in right_by_output[middle]:
                for word, differentiated in apply_word(left_word, right_coefficient, right_word).items():
                    add_term(result, (row, column, word), multiply_poly(left_coefficient, differentiated))
    return result


def _evaluate_phi2(value: Polynomial) -> Polynomial:
    terms = []
    for monomial, coefficient in value.items():
        remaining = []
        for factor in monomial:
            kind, name, _vertical, spacetime = factor
            if kind == "background" and name.startswith("Phi2_"):
                if any(spacetime) or name not in PHI2_VALUES:
                    coefficient = sp.S.Zero
                    break
                coefficient *= PHI2_VALUES[name]
            else:
                remaining.append(factor)
        if coefficient != 0:
            terms.append((coefficient, tuple(remaining)))
    return normalize(terms)


def _old_q1() -> GradedOperator:
    result: GradedOperator = {}
    for degree, operator in old_replay.load_q1().items():
        converted: Operator = {}
        for key, polynomial in operator.items():
            value = _evaluate_phi2({monomial: scalar(coefficient) for monomial, coefficient in polynomial.items()})
            if value:
                add_term(converted, key, value)
        result[degree] = converted
    return result


def _factor(record: dict[str, Any]) -> Generator:
    return (record["kind"], record["name"], tuple(record["vertical_multiindex"]), tuple(record["spacetime_multiindex"]))


def _word(multiindex: list[int]) -> tuple[int, ...]:
    return tuple(axis for axis, count in enumerate(multiindex) for _ in range(count))


def _split_term(coefficient: sp.Expr, factors: list[dict[str, Any]]) -> tuple[tuple[int, int], Polynomial]:
    degree = [0, 0]
    remaining = []
    for record in factors:
        if record["kind"] == "parameter" and record["name"] == "epsilon_R_squared":
            degree[0] += 1
        elif record["kind"] == "parameter" and record["name"] == "kappa":
            degree[1] += 1
        else:
            remaining.append(_factor(record))
    return tuple(degree), {tuple(sorted(remaining)): coefficient}


def _add_serialized_blocks(
    result: GradedOperator,
    blocks: list[dict[str, Any]],
    *,
    string_coefficients: bool,
    exclude_phi2: bool = False,
    forced_degree: tuple[int, int] | None = None,
) -> None:
    for block in blocks:
        for entry in block["entries"]:
            for term in entry["terms"]:
                has_phi2 = any(record["name"].startswith("Phi2_") for record in term["coefficient_factors"])
                if exclude_phi2 and has_phi2:
                    continue
                coefficient = sp.sympify(term["coefficient"], locals=SYMBOLS) if string_coefficients else serialized_scalar(term["coefficient"])
                degree, polynomial = _split_term(coefficient, term["coefficient_factors"])
                degree = forced_degree or degree
                add_term(result.setdefault(degree, {}), (entry["output_row"], entry["input_row"], _word(term["input_pbw_multiindex"])), polynomial)


def assemble() -> tuple[GradedOperator, dict[str, Any]]:
    old = _old_q1()
    old_summaries = {str(degree): summary(operator) for degree, operator in old.items()}
    result = {degree: add_operators(operator) for degree, operator in old.items()}
    old_completion = json.loads(OLD_COMPLETION.read_text())
    phi2 = json.loads(PHI2.read_text())
    interface = json.loads(INTERFACE.read_text())
    _add_serialized_blocks(result, old_completion["blocks"], string_coefficients=False, exclude_phi2=True, forced_degree=(1, 0))
    _add_serialized_blocks(result, phi2["evaluated_nonrod_D3S"]["blocks"], string_coefficients=True, forced_degree=(1, 0))
    for name in ("Gamma_R", "Gamma_R_sharp", "K_RR", "K_Rh", "K_hR", "Delta_K_hh_rod"):
        _add_serialized_blocks(result, [{"entries": interface["operator_blocks"][name]["net_replacement_delta"]["entries"]}], string_coefficients=True)
    result = {degree: operator for degree, operator in sorted(result.items()) if operator}
    audit = {
        "evaluated_old_q1_summaries": old_summaries,
        "assembled_summaries": {str(degree): summary(operator) for degree, operator in result.items()},
        "positive_phi2_evaluated_precompletion_term_count": sum(len(value) for value in old.get((1, 0), {}).values()),
        "unaffected_second_jet_term_count": phi2["evaluated_nonrod_D3S"]["unaffected_source_term_count"],
        "evaluated_second_jet_term_count": phi2["evaluated_nonrod_D3S"]["surviving_normalized_term_count"],
    }
    return result, audit


def pairing_map() -> dict[int, tuple[int, sp.Expr]]:
    payload = json.loads(REPLACEMENT.read_text())
    result = {}
    for entry in payload["carrier"]["pairing_entries"]:
        row, partner, value = entry
        text = value if isinstance(value, str) else value[0][1]
        result[row] = partner, sp.sympify(text)
    if set(result) != set(range(112)):
        raise AssertionError("replacement pairing is incomplete")
    return result


def formal_adjoint_entry(entry: dict[tuple[int, ...], Polynomial]) -> dict[tuple[int, ...], Polynomial]:
    result: dict[tuple[int, ...], Polynomial] = {}
    for word, coefficient in entry.items():
        sign = -1 if len(word) % 2 else 1
        for output_word, output_coefficient in apply_word(tuple(reversed(word)), coefficient, ()).items():
            result[output_word] = add_poly(result.get(output_word, {}), scale_poly(output_coefficient, sign))
    return result


def cyclicity_defect(operator: Operator) -> Operator:
    pairing = pairing_map()
    paired: dict[tuple[int, int], dict[tuple[int, ...], Polynomial]] = defaultdict(dict)
    for row in range(112):
        partner, pairing_coefficient = pairing[row]
        for (output, column, word), coefficient in operator.items():
            if output == partner:
                paired[row, column][word] = add_poly(paired[row, column].get(word, {}), scale_poly(coefficient, pairing_coefficient))
    defect: Operator = {}
    positions = set(paired) | {(column, row) for row, column in paired}
    for row, column in positions:
        right = formal_adjoint_entry(paired.get((column, row), {}))
        for word in set(paired.get((row, column), {})) | set(right):
            coefficient = add_poly(paired.get((row, column), {}).get(word, {}), scale_poly(right.get(word, {}), -1))
            reduced = {monomial: reduce_expr(value) for monomial, value in coefficient.items() if reduce_expr(value) != 0}
            if reduced:
                defect[row, column, word] = reduced
    return defect


def square(q1: GradedOperator) -> GradedOperator:
    q00, q10, q01, q11 = (q1.get(degree, {}) for degree in ((0, 0), (1, 0), (0, 1), (1, 1)))
    return {
        (0, 0): compose(q00, q00),
        (1, 0): add_operators(compose(q00, q10), compose(q10, q00)),
        (0, 1): add_operators(compose(q00, q01), compose(q01, q00)),
        (1, 1): add_operators(compose(q00, q11), compose(q11, q00), compose(q10, q01), compose(q01, q10)),
    }


def summary(operator: Operator) -> dict[str, Any]:
    return {
        "operator_key_count": len(operator),
        "matrix_position_count": len({(row, column) for row, column, _word in operator}),
        "serialized_term_count": sum(len(value) for value in operator.values()),
        "row_support": sorted({row for row, _column, _word in operator}),
        "column_support": sorted({column for _row, column, _word in operator}),
        "maximum_input_order": max((len(word) for _row, _column, word in operator), default=0),
    }


@lru_cache(maxsize=1)
def background_unit_ideal() -> sp.GroebnerBasis:
    return sp.groebner(
        [CA**2 + SA**2 - 1, CU**2 + SU**2 - 1, R10**2 - 10, R58**2 - 58, J**2 + 1],
        CA,
        CU,
        SA,
        SU,
        R10,
        R58,
        J,
        order="lex",
        domain=sp.QQ,
    )


@lru_cache(maxsize=None)
def background_reduce_expr(value: sp.Expr) -> sp.Expr:
    return background_reduce_terms((value,))


def background_reduce_terms(values: tuple[sp.Expr, ...] | list[sp.Expr]) -> sp.Expr:
    fractions = [sp.together(background_symbolize(value)).as_numer_denom() for value in values]
    denominators = tuple(dict.fromkeys(denominator for _numerator, denominator in fractions))
    common_denominator = sp.Mul(*denominators)
    numerator = sp.Add(
        *(
            term_numerator * sp.Mul(*(other for other in denominators if other != term_denominator))
            for term_numerator, term_denominator in fractions
        )
    )
    ideal = background_unit_ideal()
    reduced_numerator = ideal.reduce(sp.expand(numerator))[1]
    if reduced_numerator == 0:
        return sp.S.Zero
    return reduced_numerator / common_denominator


def add_modes(*values: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    result: dict[int, sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for value in values:
        for mode, coefficient in value.items():
            result[mode] += coefficient
    return {mode: coefficient for mode, coefficient in result.items() if coefficient != 0}


def multiply_modes(left: dict[int, sp.Expr], right: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    result: dict[int, sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for left_mode, left_coefficient in left.items():
        for right_mode, right_coefficient in right.items():
            result[left_mode + right_mode] += left_coefficient * right_coefficient
    return {mode: coefficient for mode, coefficient in result.items() if coefficient != 0}


@lru_cache(maxsize=None)
def sphere_power_remainder(power: int) -> tuple[tuple[tuple[int, int, int, int], sp.Expr], ...]:
    x0, x1, x2, x3 = rods.X
    replacement = (1 - x0**2 - x1**2 - x2**2) ** (power // 2) * x3 ** (power % 2)
    return tuple(sp.Poly(sp.expand(replacement), x0, x1, x2, x3).terms())


class PositiveBackgroundEvaluator:
    """Evaluate rod jets through R=B psi in the positive-mixed quotient."""

    def __init__(self, parameter_values: dict[sp.Symbol, sp.Expr] | None = None) -> None:
        self.parameter_values = parameter_values or {}
        payload = json.loads(REPLACEMENT.read_text())
        B = sp.Matrix(
            [
                [background_symbolize(sp.sympify(value, locals=SYMBOLS).subs(self.parameter_values)) for value in row]
                for row in payload["mixed_action"]["background_orbit_matrix_B"]
            ]
        )
        x = rods.X
        psi = [
            {-1: x[index] / 2, 1: x[index] / 2}
            for index in range(4)
        ] + [
            {-1: J * x[index] / 2, 1: -J * x[index] / 2}
            for index in range(4)
        ]
        self.values = {}
        for i, name in enumerate(RODS):
            value: dict[int, sp.Expr] = {}
            for j in range(8):
                value = add_modes(value, {mode: B[i, j] * coefficient for mode, coefficient in psi[j].items()})
            self.values[name] = value

    @lru_cache(maxsize=None)
    def jet(self, name: str, spacetime: tuple[int, ...]) -> dict[int, sp.Expr]:
        if not any(spacetime):
            return self.values[name]
        axis = next(index for index, count in enumerate(spacetime) if count)
        predecessor = list(spacetime)
        predecessor[axis] -= 1
        value = self.jet(name, tuple(predecessor))
        if axis == 0:
            return {mode: sp.expand(J * R58 * mode * coefficient / 6) for mode, coefficient in value.items() if mode != 0}
        return {
            mode: sp.expand(background_symbolize(rods._frame_derivative(coefficient, axis - 1)))
            for mode, coefficient in value.items()
        }

    @lru_cache(maxsize=None)
    def monomial(self, monomial: Monomial) -> dict[int, sp.Expr]:
        current = {0: sp.S.One}
        for kind, name, vertical, spacetime in monomial:
            if kind != "background" or vertical or name not in self.values:
                raise ValueError(f"coefficient outside positive background quotient: {(kind, name, vertical, spacetime)}")
            current = multiply_modes(current, self.jet(name, spacetime))
        return current

    @lru_cache(maxsize=None)
    def jet_spatial(self, name: str, spacetime: tuple[int, ...]) -> dict[int, tuple[tuple[tuple[int, int, int, int], sp.Expr], ...]]:
        x0, x1, x2, x3 = rods.X
        return {
            mode: tuple(sp.Poly(sp.expand(entry), x0, x1, x2, x3).terms())
            for mode, entry in self.jet(name, spacetime).items()
        }

    @lru_cache(maxsize=None)
    def spatial_remainder(self, monomial: Monomial) -> dict[int, tuple[tuple[tuple[int, int, int, int], sp.Expr], ...]]:
        states: dict[int, dict[tuple[int, int, int, int], sp.Expr]] = {0: {(0, 0, 0, 0): sp.S.One}}
        for kind, name, vertical, spacetime in monomial:
            if kind != "background" or vertical or name not in self.values:
                raise ValueError(f"coefficient outside positive background quotient: {(kind, name, vertical, spacetime)}")
            grouped: dict[int, dict[tuple[int, int, int, int], list[sp.Expr]]] = defaultdict(lambda: defaultdict(list))
            for left_mode, left_terms in states.items():
                for right_mode, right_terms in self.jet_spatial(name, spacetime).items():
                    for left_powers, left_coefficient in left_terms.items():
                        for right_powers, right_coefficient in right_terms:
                            powers = tuple(left_powers[index] + right_powers[index] for index in range(4))
                            grouped[left_mode + right_mode][powers].append(left_coefficient * right_coefficient)
            states = {
                mode: {powers: sp.expand(sp.Add(*coefficients)) for powers, coefficients in powers_to_terms.items()}
                for mode, powers_to_terms in grouped.items()
            }

        result = {}
        for mode, terms in states.items():
            grouped: dict[tuple[int, int, int, int], list[sp.Expr]] = defaultdict(list)
            for powers, coefficient in terms.items():
                for replacement_powers, replacement_coefficient in sphere_power_remainder(powers[3]):
                    output_powers = (
                        powers[0] + replacement_powers[0],
                        powers[1] + replacement_powers[1],
                        powers[2] + replacement_powers[2],
                        replacement_powers[3],
                    )
                    grouped[output_powers].append(coefficient * replacement_coefficient)
            result[mode] = tuple(
                (powers, sp.expand(sp.Add(*coefficients)))
                for powers, coefficients in sorted(grouped.items())
                if sp.expand(sp.Add(*coefficients)) != 0
            )
        return result

    @lru_cache(maxsize=None)
    def coefficient_value(self, coefficient: sp.Expr) -> sp.Expr:
        return sp.cancel(background_symbolize(coefficient.subs(self.parameter_values)))

    def polynomial(self, value: Polynomial) -> dict[int, sp.Expr]:
        grouped: dict[int, dict[tuple[int, int, int, int], list[sp.Expr]]] = defaultdict(lambda: defaultdict(list))
        for monomial, coefficient in value.items():
            coefficient = self.coefficient_value(coefficient)
            for mode, terms in self.spatial_remainder(monomial).items():
                for powers, entry in terms:
                    grouped[mode][powers].append(coefficient * entry)
        x0, x1, x2, x3 = rods.X
        result = {}
        for mode, powers_to_terms in grouped.items():
            expression = sp.S.Zero
            for powers, terms in powers_to_terms.items():
                if self.parameter_values:
                    cleaned = background_unit_ideal().reduce(sp.expand(sp.Add(*terms)))[1]
                else:
                    cleaned = background_reduce_terms(terms)
                if cleaned != 0:
                    expression += cleaned * x0**powers[0] * x1**powers[1] * x2**powers[2] * x3**powers[3]
            result[mode] = sp.expand(expression)
        return result

    def wave_defect_count(self) -> int:
        defects = 0
        for name in RODS:
            wave = {mode: -coefficient for mode, coefficient in self.jet(name, (2, 0, 0, 0)).items()}
            for axis in range(1, 4):
                multiindex = tuple(2 if direction == axis else 0 for direction in range(4))
                wave = add_modes(wave, self.jet(name, multiindex))
            defects += any(sphere_normal_form(value) != 0 for value in wave.values())
        return defects


@lru_cache(maxsize=None)
def sphere_normal_form(expression: sp.Expr) -> sp.Expr:
    x0, x1, x2, x3 = rods.X
    relation = x3**2 + x0**2 + x1**2 + x2**2 - 1
    expression = sp.cancel(expression)
    reduced = sp.expand(sp.rem(sp.Poly(sp.expand(expression), x3), sp.Poly(relation, x3)).as_expr())
    if reduced == 0:
        return sp.S.Zero
    polynomial = sp.Poly(reduced, x0, x1, x2, x3)
    result = sp.S.Zero
    for powers, coefficient in polynomial.terms():
        cleaned = background_reduce_expr(coefficient)
        if cleaned != 0:
            result += cleaned * x0**powers[0] * x1**powers[1] * x2**powers[2] * x3**powers[3]
    return sp.expand(result)


def background_quotient_defect(
    operator: Operator,
    parameter_values: dict[sp.Symbol, sp.Expr] | None = None,
) -> tuple[dict[tuple[int, int, tuple[int, ...], int], sp.Expr], dict[str, Any]]:
    evaluator = PositiveBackgroundEvaluator(parameter_values)
    defects = {}
    evaluated_modes = 0
    for (row, column, word), coefficient in operator.items():
        for mode, value in evaluator.polynomial(coefficient).items():
            evaluated_modes += 1
            if value != 0:
                defects[row, column, word, mode] = value
    return defects, {
        "input_operator_key_count": len(operator),
        "evaluated_time_mode_count": evaluated_modes,
        "quotient_defect_count": len(defects),
        "quotient_defect_matrix_position_count": len({(row, column) for row, column, _word, _mode in defects}),
        "rod_wave_defect_count": evaluator.wave_defect_count(),
    }
