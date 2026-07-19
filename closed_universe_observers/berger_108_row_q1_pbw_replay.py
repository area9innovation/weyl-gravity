"""Exact loader and composition engine for the scalar Berger 108-row q1."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path
from typing import Iterable

import sympy as sp

from closed_universe_observers import (
    generate_berger_108_row_background_specialization_differential_ideal as background_ideal,
)

from closed_universe_observers.berger_108_row_component_jet_contract import (
    ONE_SCALAR,
    Polynomial,
    Scalar,
    _pbw_word,
    add,
    derivative,
    generator,
    multiply,
    normalize,
    scalar_mul,
    scale,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
BASE = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
COMPONENT = P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json"
EMITTER = P / "certificates/BERGER_108_ROW_EMITTER_Q1_PBW_OVERLAY.json"
MEMORY = P / "certificates/BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY_PAYLOAD.json"
SHIFTED = P / "certificates/BERGER_108_ROW_SHIFTED_Q2_PHI2_PBW_OVERLAY_PAYLOAD.json"
LOCAL_ROD = P / "certificates/BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY_PAYLOAD.json"

Bidegree = tuple[int, int]
OperatorKey = tuple[int, int, tuple[int, ...]]
Operator = dict[OperatorKey, Polynomial]
GradedOperator = dict[Bidegree, Operator]
METRIC_COMPONENTS = ("00", "01", "02", "03", "11", "12", "13", "22", "23", "33")


def rational(value) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def scalar(value) -> Scalar:
    return rational(value["rational"]), rational(value["sqrt10"])


def parse_qsqrt10(text: str) -> Scalar:
    root = sp.sqrt(10)
    value = sp.expand(sp.sympify(text))
    rational_part = sp.expand(value).coeff(root, 0)
    root_part = sp.expand(value).coeff(root, 1)
    if sp.expand(value - rational_part - root * root_part) != 0:
        raise ValueError(f"coefficient is not in Q(sqrt(10)): {text}")
    return Fraction(int(sp.numer(rational_part)), int(sp.denom(rational_part))), Fraction(
        int(sp.numer(root_part)), int(sp.denom(root_part))
    )


def word(multiindex: Iterable[int]) -> tuple[int, ...]:
    return tuple(axis for axis, power in enumerate(multiindex) for _ in range(power))


def polynomial(term: dict) -> Polynomial:
    factors = tuple(
        generator(
            factor["kind"],
            factor["name"],
            factor["vertical_multiindex"],
            factor["spacetime_multiindex"],
        )
        for factor in term["coefficient_factors"]
    )
    return normalize([(scalar(term["coefficient"]), factors)])


def add_operator_term(operator: Operator, key: OperatorKey, coefficient: Polynomial) -> None:
    operator[key] = add(operator.get(key, {}), coefficient)
    if not operator[key]:
        del operator[key]


def split_bidegree(value: Polynomial) -> dict[Bidegree, Polynomial]:
    result: dict[Bidegree, list[tuple[Scalar, tuple]]] = defaultdict(list)
    for monomial, coefficient in value.items():
        reduced = []
        degree = [0, 0]
        for factor in monomial:
            kind, name, _vertical, _spacetime = factor
            if kind == "parameter" and name == "epsilon_R_squared":
                degree[0] += 1
            elif kind == "parameter" and name == "kappa":
                degree[1] += 1
            else:
                reduced.append(factor)
        if degree[0] <= 1 and degree[1] <= 1:
            result[tuple(degree)].append((coefficient, tuple(reduced)))
    return {degree: normalize(terms) for degree, terms in result.items()}


def add_graded_term(value: GradedOperator, key: OperatorKey, coefficient: Polynomial) -> None:
    for degree, part in split_bidegree(coefficient).items():
        add_operator_term(value.setdefault(degree, {}), key, part)


def load_base(value: GradedOperator) -> None:
    source = json.loads(BASE.read_text())["full_complex"]["classical_unary_q1"]
    if source["shape"] != [64, 64]:
        raise AssertionError("pinned base q1 shape changed")
    for row, column, terms in source["entries"]:
        for multiindex, coefficient in terms:
            add_operator_term(
                value.setdefault((0, 0), {}),
                (row, column, word(multiindex)),
                {(): parse_qsqrt10(coefficient)},
            )


def load_generic_blocks(value: GradedOperator, blocks: list[dict]) -> None:
    for block in blocks:
        for entry in block["entries"]:
            for term in entry["terms"]:
                add_graded_term(
                    value,
                    (entry["output_row"], entry["input_row"], word(term["input_pbw_multiindex"])),
                    polynomial(term),
                )


def load_shifted(value: GradedOperator) -> None:
    source = json.loads(SHIFTED.read_text())
    if source["active_base_shape"] != [64, 64]:
        raise AssertionError("shifted q2 base shape changed")
    operator = value.setdefault((1, 0), {})
    for row in source["rows"]:
        for input_row, input_word, component, background_word, coefficient in row["terms"]:
            factor = generator("background", f"Phi2_{METRIC_COMPONENTS[component]}", spacetime=background_word)
            add_operator_term(
                operator,
                (row["output"], input_row, word(input_word)),
                {(factor,): scalar(coefficient)},
            )


def load_q1() -> GradedOperator:
    result: GradedOperator = {}
    load_base(result)
    emitter = json.loads(EMITTER.read_text())["emitter_overlay"]["blocks"]
    memory = json.loads(MEMORY.read_text())["blocks"]
    local = json.loads(LOCAL_ROD.read_text())["blocks"]
    load_generic_blocks(result, emitter)
    load_generic_blocks(result, memory)
    load_generic_blocks(result, local)
    load_shifted(result)
    return {degree: operator for degree, operator in sorted(result.items()) if operator}


def apply_word(left_word: tuple[int, ...], coefficient: Polynomial, right_word: tuple[int, ...]) -> dict[tuple[int, ...], Polynomial]:
    """Expand D_left(coefficient D_right) in left-coefficient PBW form."""
    states: dict[tuple[int, ...], Polynomial] = {right_word: coefficient}
    for axis in reversed(left_word):
        updated: dict[tuple[int, ...], Polynomial] = {}
        for current_word, current_coefficient in states.items():
            differentiated = derivative(current_coefficient, axis)
            if differentiated:
                updated[current_word] = add(updated.get(current_word, {}), differentiated)
            for reduced_word, structure_coefficient in _pbw_word((axis, *current_word)):
                contribution = scale(current_coefficient, structure_coefficient)
                updated[reduced_word] = add(updated.get(reduced_word, {}), contribution)
        states = {key: item for key, item in updated.items() if item}
    return states


def compose(left: Operator, right: Operator) -> Operator:
    """Return left after right as an exact coefficient-jet PBW operator."""
    left_by_input: dict[int, list[tuple[int, tuple[int, ...], Polynomial]]] = defaultdict(list)
    right_by_output: dict[int, list[tuple[int, tuple[int, ...], Polynomial]]] = defaultdict(list)
    for (row, column, left_word), coefficient in left.items():
        left_by_input[column].append((row, left_word, coefficient))
    for (row, column, right_word), coefficient in right.items():
        right_by_output[row].append((column, right_word, coefficient))
    output: Operator = {}
    for middle in sorted(set(left_by_input) & set(right_by_output)):
        for row, left_word, left_coefficient in left_by_input[middle]:
            for column, right_word, right_coefficient in right_by_output[middle]:
                for result_word, inner_coefficient in apply_word(left_word, right_coefficient, right_word).items():
                    add_operator_term(output, (row, column, result_word), multiply(left_coefficient, inner_coefficient))
    return output


def add_operators(*operators: Operator) -> Operator:
    result: Operator = {}
    for operator in operators:
        for key, coefficient in operator.items():
            add_operator_term(result, key, coefficient)
    return result


def scale_operator(operator: Operator, coefficient: Scalar) -> Operator:
    return {key: scale(value, coefficient) for key, value in operator.items()}


def q1_squared_coefficients(q1: GradedOperator) -> GradedOperator:
    q00 = q1.get((0, 0), {})
    q10 = q1.get((1, 0), {})
    q01 = q1.get((0, 1), {})
    q11 = q1.get((1, 1), {})
    return {
        (0, 0): compose(q00, q00),
        (1, 0): add_operators(compose(q00, q10), compose(q10, q00)),
        (0, 1): add_operators(compose(q00, q01), compose(q01, q00)),
        (1, 1): add_operators(
            compose(q00, q11),
            compose(q11, q00),
            compose(q10, q01),
            compose(q01, q10),
        ),
    }


def formal_adjoint_entry(entry: dict[tuple[int, ...], Polynomial]) -> dict[tuple[int, ...], Polynomial]:
    result: dict[tuple[int, ...], Polynomial] = {}
    for current_word, coefficient in entry.items():
        sign = (Fraction(-1), Fraction(0)) if len(current_word) % 2 else ONE_SCALAR
        for result_word, result_coefficient in apply_word(tuple(reversed(current_word)), coefficient, ()).items():
            result[result_word] = add(result.get(result_word, {}), scale(result_coefficient, sign))
    return {key: value for key, value in result.items() if value}


def pairing_map() -> dict[int, tuple[int, Scalar]]:
    entries = json.loads(COMPONENT.read_text())["carrier_contract"]["pairing_entries"]
    result = {}
    for row, partner, terms in entries:
        if len(terms) != 1 or terms[0][0] != [0, 0, 0, 0]:
            raise AssertionError("108-row pairing ceased to be a signed permutation")
        result[row] = partner, parse_qsqrt10(terms[0][1])
    if set(result) != set(range(108)):
        raise AssertionError("108-row pairing is degenerate")
    return result


def cyclicity_defect(operator: Operator) -> Operator:
    pairing = pairing_map()
    paired: dict[tuple[int, int], dict[tuple[int, ...], Polynomial]] = defaultdict(dict)
    for row in range(108):
        partner, pairing_coefficient = pairing[row]
        for (output, column, current_word), coefficient in operator.items():
            if output == partner:
                key = row, column
                paired[key][current_word] = add(
                    paired[key].get(current_word, {}),
                    scale(coefficient, pairing_coefficient),
                )
    defect: Operator = {}
    positions = set(paired) | {(column, row) for row, column in paired}
    for row, column in sorted(positions):
        left = paired.get((row, column), {})
        right = formal_adjoint_entry(paired.get((column, row), {}))
        for current_word in set(left) | set(right):
            coefficient = add(
                left.get(current_word, {}),
                scale(right.get(current_word, {}), (Fraction(-1), Fraction(0))),
            )
            if coefficient:
                defect[row, column, current_word] = coefficient
    return defect


def term_count(operator: Operator) -> int:
    return sum(len(value) for value in operator.values())


def summary(operator: Operator) -> dict[str, object]:
    return {
        "operator_key_count": len(operator),
        "matrix_position_count": len({(row, column) for row, column, _word in operator}),
        "serialized_term_count": term_count(operator),
        "row_support": sorted({row for row, _column, _word in operator}),
        "column_support": sorted({column for _row, column, _word in operator}),
        "maximum_input_order": max((len(current_word) for _row, _column, current_word in operator), default=0),
    }


ModeValue = dict[int, sp.Expr]
TRIG_S = sp.Symbol("detector_phase_sine")
TRIG_C = sp.Symbol("detector_phase_cosine")
TIME_Z = sp.Symbol("detector_time_phase", nonzero=True)
TRIG_BASE = sp.sqrt(10) / 12
TIME_BASE = sp.I * sp.sqrt(58) / 24


def add_modes(*values: ModeValue) -> ModeValue:
    result: ModeValue = {}
    for value in values:
        for mode, coefficient in value.items():
            result[mode] = result.get(mode, sp.S.Zero) + coefficient
    return {mode: coefficient for mode, coefficient in result.items() if coefficient != 0}


def scale_modes(value: ModeValue, coefficient: sp.Expr) -> ModeValue:
    return {
        mode: coefficient * item
        for mode, item in value.items()
        if coefficient * item != 0
    }


def multiply_modes(left: ModeValue, right: ModeValue) -> ModeValue:
    result: ModeValue = {}
    for left_mode, left_coefficient in left.items():
        for right_mode, right_coefficient in right.items():
            mode = left_mode + right_mode
            result[mode] = result.get(mode, sp.S.Zero) + left_coefficient * right_coefficient
    return {mode: coefficient for mode, coefficient in result.items() if coefficient != 0}


class BackgroundEvaluator:
    """Evaluate coefficient jets in the certified finite Berger quotient."""

    def __init__(self) -> None:
        values = {
            name: json.loads(path.read_text())
            for name, path in background_ideal.DEPENDENCIES.items()
        }
        rods, _ = background_ideal._rod_specializations(values["global_rods"])
        phi2, _ = background_ideal._phi2_specializations(values["rod_gravity_unary"])
        self.values = {
            name: {
                mode: coefficient_normal_form(coefficient)
                for mode, coefficient in value.items()
            }
            for name, value in (rods | phi2).items()
        }

    @lru_cache(maxsize=None)
    def jet(self, name: str, spacetime: tuple[int, ...]) -> ModeValue:
        if not any(spacetime):
            return self.values[name]
        axis = next(index for index, count in enumerate(spacetime) if count)
        predecessor = list(spacetime)
        predecessor[axis] -= 1
        value = self.jet(name, tuple(predecessor))
        if axis == 0:
            return {
                mode: sp.I * background_ideal.OMEGA * mode * coefficient
                for mode, coefficient in value.items()
                if mode != 0 and coefficient != 0
            }
        return {
            mode: background_ideal.rods._frame_derivative(coefficient, axis - 1)
            for mode, coefficient in value.items()
            if coefficient != 0
        }

    def polynomial(self, value: Polynomial) -> ModeValue:
        result: ModeValue = {}
        root = sp.sqrt(10)
        for monomial, coefficient in value.items():
            current: ModeValue = {0: sp.Rational(coefficient[0].numerator, coefficient[0].denominator) + root * sp.Rational(coefficient[1].numerator, coefficient[1].denominator)}
            for kind, name, vertical, spacetime in monomial:
                if kind != "background" or vertical:
                    raise ValueError(
                        f"coefficient outside the certified background quotient: {(kind, name, vertical, spacetime)}"
                    )
                current = multiply_modes(current, self.jet(name, spacetime))
            result = add_modes(result, current)
        return result


def sphere_normal_form(expression: sp.Expr) -> sp.Expr:
    """Reduce a degree-at-most-two S3 polynomial and simplify its coefficients."""
    x0, x1, x2, x3 = background_ideal.X
    sphere_as_x3 = x3**2 + x0**2 + x1**2 + x2**2 - 1
    reduced = sp.expand(sp.rem(sp.Poly(sp.expand(expression), x3), sp.Poly(sphere_as_x3, x3)).as_expr())
    if reduced == 0:
        return sp.S.Zero
    polynomial = sp.Poly(reduced, x0, x1, x2, x3)
    rebuilt = sp.S.Zero
    for powers, coefficient in polynomial.terms():
        cleaned = coefficient_normal_form(coefficient)
        if cleaned != 0:
            rebuilt += cleaned * x0**powers[0] * x1**powers[1] * x2**powers[2] * x3**powers[3]
    return sp.expand(rebuilt)


def coefficient_normal_form(expression: sp.Expr) -> sp.Expr:
    """Canonicalize the exact detector phases without heuristic trig simplification."""
    sine, cosine = TRIG_S, TRIG_C
    sine2 = 2 * sine * cosine
    cosine2 = cosine**2 - sine**2
    replacements = {
        sp.sin(TRIG_BASE): sine,
        sp.cos(TRIG_BASE): cosine,
        sp.sin(2 * TRIG_BASE): sine2,
        sp.cos(2 * TRIG_BASE): cosine2,
        sp.sin(4 * TRIG_BASE): 2 * sine2 * cosine2,
        sp.cos(4 * TRIG_BASE): cosine2**2 - sine2**2,
    }
    for atom in expression.atoms(sp.exp):
        ratio = sp.simplify(atom.args[0] / TIME_BASE)
        if ratio.is_Integer:
            replacements[atom] = TIME_Z ** int(ratio)
    replaced = sp.together(expression.xreplace(replacements))
    numerator, denominator = replaced.as_numer_denom()
    numerator = sp.expand(numerator)
    reduced = sp.rem(
        sp.Poly(numerator, cosine),
        sp.Poly(cosine**2 + sine**2 - 1, cosine),
    ).as_expr()
    return sp.cancel(reduced / denominator)


def quotient_defect(operator: Operator) -> tuple[dict[tuple[int, int, tuple[int, ...], int], sp.Expr], dict[str, object]]:
    evaluator = BackgroundEvaluator()
    defects: dict[tuple[int, int, tuple[int, ...], int], sp.Expr] = {}
    evaluated_mode_count = 0
    for (row, column, current_word), coefficient in operator.items():
        for mode, expression in evaluator.polynomial(coefficient).items():
            evaluated_mode_count += 1
            normal = sphere_normal_form(expression)
            if normal != 0:
                defects[row, column, current_word, mode] = normal
    return defects, {
        "input_operator_key_count": len(operator),
        "evaluated_time_mode_count": evaluated_mode_count,
        "quotient_defect_count": len(defects),
        "quotient_defect_matrix_position_count": len(
            {(row, column) for row, column, _word, _mode in defects}
        ),
    }
