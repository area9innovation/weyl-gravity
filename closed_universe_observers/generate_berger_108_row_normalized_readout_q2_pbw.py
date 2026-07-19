#!/usr/bin/env python3
"""Export the exact normalized two-detector readout q2 PBW tensor."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.berger_108_row_component_jet_contract import (
    ONE_SCALAR,
    Polynomial,
    _multiindex_from_word,
    _pbw_word,
    add,
    derivative,
    generator,
    multiply,
    scalar_mul,
    scale,
    serialize,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_NORMALIZED_READOUT_Q2_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_NORMALIZED_READOUT_Q2_PBW_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-normalized-readout-q2-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-normalized-readout-q2-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-normalized-readout-q2-pbw.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "apparatus_action": P / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "memory_q1": P / "certificates/BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY.json",
    "normalized_unary": P / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
}
SOURCE_FILES = [Path(__file__), P / "verify_berger_108_row_normalized_readout_q2_pbw.py", P / "tests/test_berger_108_row_normalized_readout_q2_pbw.py", SCHEMA, PAYLOAD_SCHEMA, REPORT]

Tensor = dict[tuple[int, int, tuple[int, ...], int, tuple[int, ...]], Polynomial]
Vertex = tuple[int, tuple[int, ...], int, tuple[int, ...], Polynomial]
METRIC_COMPONENTS = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))
RODS = (("R0_1", "R0_2", "R0_3"), ("R1_1", "R1_2", "R1_3"))
SELECTED_ROD = (0, 1)
ETA = (-1, 1, 1, 1)
OMEGA = Fraction(3, 4)
J_VERTICAL_ORDER = tuple(
    [f"g{a}{b}" for a, b in METRIC_COMPONENTS]
    + [f"q{a}" for a in range(4)]
    + [f"r{rod}_{axis}" for rod in range(3) for axis in range(4)]
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rational(value: Fraction | int) -> tuple[Fraction, Fraction]:
    return Fraction(value), Fraction(0)


def constant(value: Fraction | int) -> Polynomial:
    return {(): rational(value)} if value else {}


def parameter(name: str) -> Polynomial:
    return {(generator("parameter", name),): ONE_SCALAR}


def profile(name: str, vertical: Iterable[int] = ()) -> Polynomial:
    return {(generator("profile", name, vertical),): ONE_SCALAR}


def background(name: str, axis: int | None = None) -> Polynomial:
    value = {(generator("background", name),): ONE_SCALAR}
    return value if axis is None else derivative(value, axis)


def product(*values: Polynomial) -> Polynomial:
    result = constant(1)
    for value in values:
        result = multiply(result, value)
    return result


def one_hot(length: int, position: int) -> tuple[int, ...]:
    return tuple(int(index == position) for index in range(length))


def add_term(tensor: Tensor, output: int, left: int, left_word: Iterable[int], right: int, right_word: Iterable[int], coefficient: Polynomial) -> None:
    for reduced_left, left_factor in _pbw_word(tuple(left_word)):
        for reduced_right, right_factor in _pbw_word(tuple(right_word)):
            key = output, left, reduced_left, right, reduced_right
            value = scale(coefficient, scalar_mul(left_factor, right_factor))
            tensor[key] = add(tensor.get(key, {}), value)
            if not tensor[key]:
                del tensor[key]


def add_symmetric(tensor: Tensor, output: int, left: int, left_word: Iterable[int], right: int, right_word: Iterable[int], coefficient: Polynomial) -> None:
    left_word, right_word = tuple(left_word), tuple(right_word)
    add_term(tensor, output, left, left_word, right, right_word, coefficient)
    if (left, left_word) != (right, right_word):
        add_term(tensor, output, right, right_word, left, left_word, coefficient)


def p_form(channel: int, first: int, second: int) -> Polynomial:
    """Background component of dTheta wedge dR_selected."""
    rod = RODS[channel][SELECTED_ROD[channel]]
    result: Polynomial = {}
    if first == 0:
        result = add(result, scale(background(rod, second), rational(OMEGA)))
    if second == 0:
        result = add(result, scale(background(rod, first), rational(-OMEGA)))
    return result


def base_contraction(channel: int, pair: tuple[int, int]) -> Polynomial:
    first, second = pair
    return scale(p_form(channel, first, second), rational(ETA[first] * ETA[second]))


def metric_contraction_variation(channel: int, pair: tuple[int, int], component: int) -> Polynomial:
    """D C_g(F,P)[h_component], as the coefficient of F_pair."""
    first, second = pair
    a0, b0 = METRIC_COMPONENTS[component]

    def h_entry(left: int, right: int) -> int:
        return int((left, right) in ((a0, b0), (b0, a0)))

    result: Polynomial = {}
    for axis in range(4):
        delta_first_axis = -ETA[first] * ETA[axis] * h_entry(first, axis)
        if delta_first_axis:
            result = add(result, scale(p_form(channel, axis, second), rational(delta_first_axis * ETA[second])))
        delta_second_axis = -ETA[second] * ETA[axis] * h_entry(second, axis)
        if delta_second_axis:
            result = add(result, scale(p_form(channel, first, axis), rational(ETA[first] * delta_second_axis)))
    return result


def polarization_theta_variation(channel: int, pair: tuple[int, int], axis: int) -> Polynomial:
    first, second = pair
    rod = RODS[channel][SELECTED_ROD[channel]]
    value: Polynomial = {}
    if first == axis:
        value = add(value, background(rod, second))
    if second == axis:
        value = add(value, scale(background(rod, first), rational(-1)))
    return scale(value, rational(ETA[first] * ETA[second]))


def polarization_rod_variation(pair: tuple[int, int], axis: int) -> Polynomial:
    first, second = pair
    value = OMEGA * (int(first == 0 and second == axis) - int(second == 0 and first == axis))
    return constant(ETA[first] * ETA[second] * value)


def first_variation_terms(channel: int) -> tuple[dict[tuple[int, tuple[int, ...], tuple[int, int]], Polynomial], dict[str, int]]:
    """Return D W_a before the overall -kappa action coefficient."""
    f, rho, jacobian = profile(f"f{channel}"), profile(f"rho{channel}"), profile(f"J{channel}")
    base_profiles = product(f, rho, jacobian)
    result: dict[tuple[int, tuple[int, ...], tuple[int, int]], Polynomial] = {}
    source_counts: Counter[str] = Counter()

    def insert(source: str, row: int, word: tuple[int, ...], pair: tuple[int, int], coefficient: Polynomial) -> None:
        if not coefficient:
            return
        key = row, word, pair
        result[key] = add(result.get(key, {}), coefficient)
        source_counts[source] += 1

    for pair in ((a, b) for a in range(4) for b in range(a + 1, 4)):
        base = base_contraction(channel, pair)
        for component, (first, second) in enumerate(METRIC_COMPONENTS):
            volume = Fraction(ETA[first], 2) if first == second else Fraction(0)
            insert("volume", 5 + component, (), pair, scale(product(base_profiles, base), rational(volume)))
            insert("metric_contraction", 5 + component, (), pair, product(base_profiles, metric_contraction_variation(channel, pair, component)))
            j_vertical = profile(f"J{channel}", one_hot(len(J_VERTICAL_ORDER), component))
            insert("normalized_Jacobian_metric", 5 + component, (), pair, product(f, rho, j_vertical, base))

        insert("clock_bump", 16, (), pair, product(profile(f"f{channel}", (1,)), rho, jacobian, base))
        for local_rod in range(3):
            insert("rod_bump", 64 + 3 * channel + local_rod, (), pair, product(f, profile(f"rho{channel}", one_hot(3, local_rod)), jacobian, base))

        for axis in range(4):
            j_q = profile(f"J{channel}", one_hot(len(J_VERTICAL_ORDER), 10 + axis))
            insert("normalized_Jacobian_clock", 16, (axis,), pair, product(f, rho, j_q, base))
            insert("polarization_clock", 16, (axis,), pair, product(base_profiles, polarization_theta_variation(channel, pair, axis)))
            for local_rod in range(3):
                j_position = 14 + 4 * local_rod + axis
                j_r = profile(f"J{channel}", one_hot(len(J_VERTICAL_ORDER), j_position))
                rod_row = 64 + 3 * channel + local_rod
                insert("normalized_Jacobian_rod", rod_row, (axis,), pair, product(f, rho, j_r, base))
            selected_row = 64 + 3 * channel + SELECTED_ROD[channel]
            insert("polarization_rod", selected_row, (axis,), pair, product(base_profiles, polarization_rod_variation(pair, axis)))
    return result, dict(sorted(source_counts.items()))


def field_strength_slots(pair: tuple[int, int]) -> list[tuple[int, tuple[int, ...], Fraction]]:
    first, second = pair
    result = [(55 + second, (first,), Fraction(1)), (55 + first, (second,), Fraction(-1))]
    structure = {
        (1, 2): (3, Fraction(3, 20)),
        (2, 3): (1, Fraction(2, 3)),
        (1, 3): (2, Fraction(-2, 3)),
    }
    if pair in structure:
        target, coefficient = structure[pair]
        result.append((55 + target, (), -coefficient))
    return result


def action_vertices(channel: int) -> tuple[list[Vertex], dict[str, int]]:
    first_jet, source_counts = first_variation_terms(channel)
    vertices: list[Vertex] = []
    action_factor = scale(parameter("kappa"), rational(-1))
    for (x_row, x_word, pair), coefficient in sorted(first_jet.items()):
        for a_row, a_word, field_strength_coefficient in field_strength_slots(pair):
            vertices.append((x_row, x_word, a_row, a_word, scale(product(action_factor, coefficient), rational(field_strength_coefficient))))
    return vertices, source_counts


def cyclic_blocks(channel: int) -> dict[str, Tensor]:
    """Raise all three slots of the same cubic action vertex."""
    blocks: dict[str, Tensor] = {name: {} for name in ("p_euler", "A_euler", "geometry_euler")}
    p_row, p_dual = 72 + channel, 82 + channel
    for x_row, x_word, a_row, a_word, coefficient in action_vertices(channel)[0]:
        x_dual = (27 + x_row - 5) if 5 <= x_row <= 16 else (74 + x_row - 64)
        add_symmetric(blocks["p_euler"], p_dual, x_row, x_word, a_row, a_word, coefficient)

        a_dual = 59 + a_row - 55
        if not a_word:
            add_symmetric(blocks["A_euler"], a_dual, p_row, (), x_row, x_word, scale(coefficient, rational(-1)))
        else:
            axis, = a_word
            add_symmetric(blocks["A_euler"], a_dual, p_row, (), x_row, x_word, derivative(coefficient, axis))
            add_symmetric(blocks["A_euler"], a_dual, p_row, (axis,), x_row, x_word, coefficient)
            add_symmetric(blocks["A_euler"], a_dual, p_row, (), x_row, (axis, *x_word), coefficient)

        if not x_word:
            add_symmetric(blocks["geometry_euler"], x_dual, p_row, (), a_row, a_word, coefficient)
        else:
            axis, = x_word
            negative = scale(coefficient, rational(-1))
            add_symmetric(blocks["geometry_euler"], x_dual, p_row, (), a_row, a_word, derivative(negative, axis))
            add_symmetric(blocks["geometry_euler"], x_dual, p_row, (axis,), a_row, a_word, negative)
            add_symmetric(blocks["geometry_euler"], x_dual, p_row, (), a_row, (axis, *a_word), negative)
    return {f"readout{channel}_{name}": tensor for name, tensor in blocks.items()}


def action_blocks() -> dict[str, Tensor]:
    return {name: block for channel in (0, 1) for name, block in cyclic_blocks(channel).items()}


def merge_blocks(blocks: dict[str, Tensor], *, delete_last: bool = False) -> Tensor:
    result: Tensor = {}
    for block in blocks.values():
        for key, value in block.items():
            result[key] = add(result.get(key, {}), value)
            if not result[key]:
                del result[key]
    if delete_last:
        del result[sorted(result)[-1]]
    return result


def symmetry_defects(tensor: Tensor) -> int:
    return sum(value != tensor.get((output, right, right_word, left, left_word), {}) for (output, left, left_word, right, right_word), value in tensor.items())


def serialize_tensor(tensor: Tensor) -> list[dict[str, Any]]:
    rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for (output, left, left_word, right, right_word), polynomial in sorted(tensor.items()):
        for term in serialize(polynomial):
            rows[output].append({"left_input_row": left, "left_pbw_multiindex": list(_multiindex_from_word(left_word)), "right_input_row": right, "right_pbw_multiindex": list(_multiindex_from_word(right_word)), "coefficient": term["coefficient"], "coefficient_factors": term["factors"]})
    return [{"output": output, "terms": terms} for output, terms in sorted(rows.items())]


def symbolic_first_jet_audit(*, delete_jacobian_variation: bool = False) -> dict[str, Any]:
    """Compare the seven-term chain rule with direct symbolic differentiation."""
    epsilon = sp.symbols("epsilon")
    h_symbols = sp.symbols("h0:10")
    h = sp.zeros(4)
    for symbol, (first, second) in zip(h_symbols, METRIC_COMPONENTS, strict=True):
        h[first, second] = symbol
        h[second, first] = symbol
    eta = sp.diag(-1, 1, 1, 1)
    dq = sp.symbols("dq0:4")
    r = sp.symbols("r0:4")
    dr = sp.symbols("dr0:4")
    f0, df, rho0, drho, j0, dj = sp.symbols("f0 df rho0 drho j0 dj")
    q = sp.Matrix([sp.Rational(3, 4) + epsilon * dq[0], *(epsilon * dq[index] for index in range(1, 4))])
    rod = sp.Matrix([r[index] + epsilon * dr[index] for index in range(4)])
    metric = eta + epsilon * h
    inverse = metric.inv()
    polarization = q * rod.T - rod * q.T
    field_strength = sp.zeros(4)
    for first in range(4):
        for second in range(first + 1, 4):
            symbol = sp.Symbol(f"F{first}{second}")
            field_strength[first, second] = symbol
            field_strength[second, first] = -symbol
    contraction = sp.Rational(1, 2) * sum(field_strength[m, n] * polarization[a, b] * inverse[m, a] * inverse[n, b] for m in range(4) for n in range(4) for a in range(4) for b in range(4))
    direct = sp.diff(sp.sqrt(-metric.det()) * (f0 + epsilon * df) * (rho0 + epsilon * drho) * (j0 + epsilon * dj) * contraction, epsilon).subs(epsilon, 0)

    base_polarization = polarization.subs(epsilon, 0)
    base_contraction = contraction.subs(epsilon, 0)
    density_jet = sum(ETA[index] * h[index, index] for index in range(4)) / 2
    inverse_jet = -eta * h * eta
    metric_jet = sp.Rational(1, 2) * sum(field_strength[m, n] * base_polarization[a, b] * (inverse_jet[m, a] * eta[n, b] + eta[m, a] * inverse_jet[n, b]) for m in range(4) for n in range(4) for a in range(4) for b in range(4))
    polarization_jet = sp.diff(polarization, epsilon).subs(epsilon, 0)
    polarization_contraction_jet = sp.Rational(1, 2) * sum(field_strength[m, n] * polarization_jet[a, b] * eta[m, a] * eta[n, b] for m in range(4) for n in range(4) for a in range(4) for b in range(4))
    expected = f0 * rho0 * j0 * (density_jet * base_contraction + metric_jet + polarization_contraction_jet) + (df * rho0 * j0 + f0 * drho * j0 + (0 if delete_jacobian_variation else f0 * rho0 * dj)) * base_contraction
    defect = sp.expand(direct - expected)
    return {
        "direct_symbolic_defect_count": int(defect != 0),
        "jacobian_deletion_defect_count": int(delete_jacobian_variation and defect != 0),
        "factor_variations": ["volume", "clock_bump", "rod_bump", "normalized_Jacobian", "inverse_metric_contraction", "polarization"],
        "field_strength_component_count": 6,
        "J_vertical_coordinate_order": list(J_VERTICAL_ORDER),
    }


def component_first_jet_replay_audit(channel: int) -> dict[str, Any]:
    """Replay the serialized component families against the full derivative."""
    epsilon = sp.symbols("epsilon")
    h_symbols = sp.symbols(f"h{channel}_0:10")
    theta_value = sp.Symbol(f"theta{channel}")
    dq = sp.symbols(f"dq{channel}_0:4")
    rod_values = sp.symbols(f"u{channel}_0:3")
    rod_gradients = tuple(tuple(sp.symbols(f"du{channel}_{rod}_0:4")) for rod in range(3))
    background_rod = sp.symbols(f"r{channel}_0:4")
    field_strength_symbols = {(first, second): sp.Symbol(f"F{channel}_{first}{second}") for first in range(4) for second in range(first + 1, 4)}
    f0, fp, rho0, j0 = sp.symbols(f"f{channel} fp{channel} rho{channel} J{channel}")
    rho_derivatives = sp.symbols(f"rho{channel}_0:3")
    j_derivatives = sp.symbols(f"J{channel}_0:{len(J_VERTICAL_ORDER)}")

    profile_values: dict[tuple[str, tuple[int, ...]], sp.Expr] = {
        (f"f{channel}", ()): f0,
        (f"f{channel}", (1,)): fp,
        (f"rho{channel}", ()): rho0,
        (f"J{channel}", ()): j0,
    }
    for position in range(3):
        profile_values[(f"rho{channel}", one_hot(3, position))] = rho_derivatives[position]
    for position in range(len(J_VERTICAL_ORDER)):
        profile_values[(f"J{channel}", one_hot(len(J_VERTICAL_ORDER), position))] = j_derivatives[position]

    selected_name = RODS[channel][SELECTED_ROD[channel]]

    def evaluate_coefficient(value: Polynomial) -> sp.Expr:
        total = sp.S.Zero
        for monomial, coefficient in value.items():
            scalar = sp.Rational(coefficient[0].numerator, coefficient[0].denominator) + sp.sqrt(10) * sp.Rational(coefficient[1].numerator, coefficient[1].denominator)
            term = scalar
            for kind, name, vertical, spacetime in monomial:
                if kind == "profile":
                    term *= profile_values[name, vertical]
                elif kind == "background" and name == selected_name and sum(spacetime) == 1:
                    term *= background_rod[spacetime.index(1)]
                else:
                    raise AssertionError(f"unexpected first-jet coefficient generator {(kind, name, vertical, spacetime)}")
            total += term
        return sp.expand(total)

    def input_symbol(row: int, word: tuple[int, ...]) -> sp.Expr:
        if 5 <= row <= 14 and not word:
            return h_symbols[row - 5]
        if row == 16:
            return theta_value if not word else dq[word[0]]
        if 64 + 3 * channel <= row < 67 + 3 * channel:
            local_rod = row - 64 - 3 * channel
            return rod_values[local_rod] if not word else rod_gradients[local_rod][word[0]]
        raise AssertionError(f"unexpected first-jet input {(row, word)}")

    replay = sp.S.Zero
    first_jet, _ = first_variation_terms(channel)
    for (row, word, pair), coefficient in first_jet.items():
        replay += evaluate_coefficient(coefficient) * input_symbol(row, word) * field_strength_symbols[pair]

    h = sp.zeros(4)
    for symbol, (first, second) in zip(h_symbols, METRIC_COMPONENTS, strict=True):
        h[first, second] = symbol
        h[second, first] = symbol
    eta = sp.diag(-1, 1, 1, 1)
    metric = eta + epsilon * h
    q = sp.Matrix([sp.Rational(3, 4) + epsilon * dq[0], *(epsilon * dq[index] for index in range(1, 4))])
    selected = SELECTED_ROD[channel]
    rod = sp.Matrix([background_rod[index] + epsilon * rod_gradients[selected][index] for index in range(4)])
    polarization = q * rod.T - rod * q.T
    inverse = metric.inv()
    field_strength = sp.zeros(4)
    for (first, second), symbol in field_strength_symbols.items():
        field_strength[first, second] = symbol
        field_strength[second, first] = -symbol
    contraction = sp.Rational(1, 2) * sum(field_strength[m, n] * polarization[a, b] * inverse[m, a] * inverse[n, b] for m in range(4) for n in range(4) for a in range(4) for b in range(4))
    delta_f = fp * theta_value
    delta_rho = sum(rho_derivatives[index] * rod_values[index] for index in range(3))
    delta_j = sum(j_derivatives[index] * h_symbols[index] for index in range(10))
    delta_j += sum(j_derivatives[10 + axis] * dq[axis] for axis in range(4))
    delta_j += sum(j_derivatives[14 + 4 * local_rod + axis] * rod_gradients[local_rod][axis] for local_rod in range(3) for axis in range(4))
    direct = sp.diff(sp.sqrt(-metric.det()) * (f0 + epsilon * delta_f) * (rho0 + epsilon * delta_rho) * (j0 + epsilon * delta_j) * contraction, epsilon).subs(epsilon, 0)
    defect = sp.expand(direct - replay)
    return {
        "detector_id": f"D{channel}",
        "serialized_component_family_count": len(first_jet),
        "component_replay_defect_count": int(defect != 0),
    }


def payload_document() -> dict[str, Any]:
    blocks = action_blocks()
    tensor = merge_blocks(blocks)
    serialized = serialize_tensor(tensor)
    source_counts = {f"D{channel}": action_vertices(channel)[1] for channel in (0, 1)}
    return {
        "schema": "closed-universe-berger-108-row-normalized-readout-q2-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_NORMALIZED_READOUT_Q2_PBW_PAYLOAD",
        "shape": [108, 108, 108],
        "coefficient_field": "Q(sqrt(10)) differential profile-jet algebra",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "source_action": "-kappa sum_a integral p_a sqrt(-g) f_a(Theta) rho_a(R_a) J_a C_g(dA,dTheta wedge dR_aI(a))",
        "J_vertical_coordinate_order": list(J_VERTICAL_ORDER),
        "first_variation_source_counts": source_counts,
        "block_hashes": {name: canonical_sha256(serialize_tensor(block)) for name, block in blocks.items()},
        "rows": serialized,
        "nonzero_output_rows": sorted({key[0] for key in tensor}),
        "operator_key_count": len(tensor),
        "serialized_term_count": sum(len(row["terms"]) for row in serialized),
        "canonical_sha256": canonical_sha256(serialized),
    }


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "EXACT_DETECTOR_AND_SWITCH_SPECIALIZATIONS_BOUND",
        "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED",
        "apparatus_action": "APPARATUS_Q2_ACTION_JET_EXPORTED",
        "memory_q1": "SCALAR_MEMORY_Q1_PBW_OVERLAY_EXPORTED",
        "normalized_unary": "PROFILE_NORMALIZATION_EXACT",
    }
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    audit = symbolic_first_jet_audit()
    audit["component_replays"] = [component_first_jet_replay_audit(channel) for channel in (0, 1)]
    audit["component_replay_defect_count"] = sum(row["component_replay_defect_count"] for row in audit["component_replays"])
    mutation_audit = symbolic_first_jet_audit(delete_jacobian_variation=True)
    tensor = merge_blocks(action_blocks())
    audit["graded_symmetry_defect_count"] = symmetry_defects(tensor)
    audit["cyclicity_generation"] = "p, A, metric, clock and rod Euler rows are raised from one cubic action vertex using the canonical signed odd pairing and exact PBW integration by parts"
    if audit["direct_symbolic_defect_count"] or audit["component_replay_defect_count"] or audit["graded_symmetry_defect_count"] or mutation_audit["jacobian_deletion_defect_count"] != 1:
        raise AssertionError("normalized readout q2 audit failed")
    payload = payload or payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_sha256 = payload_sha256 or hashlib.sha256(rendered_payload.encode()).hexdigest()
    deletion_detected = canonical_sha256(serialize_tensor(merge_blocks(action_blocks(), delete_last=True))) != payload["canonical_sha256"]
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate exports the complete normalized two-detector readout contribution to q2 on the canonical 108-row Berger carrier. It differentiates the action density -kappa p_a sqrt(-g) f_a(Theta) rho_a(R_a) J_a C_g(dA,dTheta wedge dR_aI(a)) in all six first-jet channels: volume, clock bump, three-variable rod bump, normalized transverse Gram Jacobian, inverse-metric contraction and polarization. The exact radius-1/128 detector profiles are inherited through the component contract. The J_a vertical coordinates are explicitly ordered by ten metric components, four clock-gradient components and twelve detector-rod-gradient components, so every first variation and every Berger-frame derivative produced by formal adjunction has a canonical differential coefficient-jet normal form. Direct symbolic differentiation of the full five-factor density and form contraction has zero defect; deleting the J_a variation is detected. Raising the same cubic action vertex through the signed odd pairing supplies the p-, Maxwell-, metric-, clock- and rod-cotangent rows, including all coefficient derivatives from exact PBW integration by parts, with exact graded input symmetry. A payload-key deletion changes the canonical hash. This certifies normalized readout q2 only. Together with the already certified scalar-BV, six-rod metric and memory-transport subblocks it still does not complete scalar q2 because the dynamical-emitter q2 sector remains open. Every q3 block, complete q1q2 and q2q2+q1q3 replay, K_Berger equivariance, observer-morphism stability, restriction of detector response to Z2, nonlinear rank, physical Bridge 3, finite-parameter causal propagation and quantum claims remain unavailable. No compact-product mode is identified with a Berger row."
    )
    return {
        "schema": "closed-universe-berger-108-row-normalized-readout-q2-pbw-v1",
        "result_id": "BERGER_108_ROW_NORMALIZED_READOUT_Q2_PBW",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_COMPLETE_NORMALIZED_READOUT_Q2_PBW_SUBBLOCK",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": payload_sha256, "operator_key_count": payload["operator_key_count"], "serialized_term_count": payload["serialized_term_count"], "nonzero_output_rows": payload["nonzero_output_rows"], "canonical_sha256": payload["canonical_sha256"]},
        "first_jet_and_cyclicity_audit": audit,
        "mutation_results": [{"name": "delete_normalized_Jacobian_first_variation", "detected": mutation_audit["jacobian_deletion_defect_count"] == 1}, {"name": "delete_last_normalized_readout_q2_key", "detected": deletion_detected}],
        "activation_disposition": {"normalized_readout_q2_subblock_exported": True, "complete_apparatus_q2_exported": True, "complete_emitter_q2_exported": False, "complete_scalar_q2_exported": False, "scalar_q3_exported": False, "arity_replay_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"APPARATUS_NORMALIZED_READOUT_Q2_PBW_EXPORTED": True, "APPARATUS_NORMALIZED_READOUT_Q2_GRADED_SYMMETRIC": True, "APPARATUS_NORMALIZED_READOUT_Q2_CYCLIC": True, "COMPLETE_APPARATUS_Q2_SUBBLOCKS_EXPORTED": True, "COMPLETE_SCALAR_108_ROW_Q2_EXPORTED": False, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EXPORT_DYNAMICAL_EMITTER_Q2_PBW_BLOCK",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    value = build(payload=payload, payload_sha256=hashlib.sha256(rendered_payload.encode()).hexdigest())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
    if args.check and (not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload or not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale normalized readout q2 artifact")
    print("BERGER_108_ROW_NORMALIZED_READOUT_Q2_PBW generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
