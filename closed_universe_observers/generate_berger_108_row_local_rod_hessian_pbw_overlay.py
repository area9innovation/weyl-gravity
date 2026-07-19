#!/usr/bin/env python3
"""Scalarize the six local Berger rod gauge, wave, and Hessian blocks."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.berger_108_row_component_jet_contract import (
    ONE_SCALAR,
    Polynomial,
    ZERO_SCALAR,
    U_BERGER,
    V_BERGER,
    add,
    derivative,
    generator,
    multiply,
    scalar_add,
    scalar_scale,
    scale,
    serialize,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-local-rod-hessian-pbw-overlay-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-local-rod-hessian-pbw-overlay-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-local-rod-hessian-pbw-overlay.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "background_quotient": P / "certificates/BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL.json",
    "rod_gravity_unary": P / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json",
    "shifted_q2_phi2": P / "certificates/BERGER_108_ROW_SHIFTED_Q2_PHI2_PBW_OVERLAY.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_108_row_local_rod_hessian_pbw_overlay.py",
    P / "tests/test_berger_108_row_local_rod_hessian_pbw_overlay.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
    REPORT,
]

Scalar = tuple[Fraction, Fraction]
Operator = dict[tuple[int, int, tuple[int, ...]], Polynomial]
ETA = (-1, 1, 1, 1)
METRIC_COMPONENTS = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))
RODS = ("R0_1", "R0_2", "R0_3", "R1_1", "R1_2", "R1_3")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rational(value: int | Fraction) -> Scalar:
    return Fraction(value), Fraction(0)


def background(name: str, spacetime=(0, 0, 0, 0)) -> Polynomial:
    return {(generator("background", name, spacetime=spacetime),): ONE_SCALAR}


def parameter(name: str) -> Polynomial:
    return {(generator("parameter", name),): ONE_SCALAR}


def product(*values: Polynomial) -> Polynomial:
    result: Polynomial = {(): ONE_SCALAR}
    for value in values:
        result = multiply(result, value)
    return result


def op_add(operator: Operator, row: int, column: int, word: tuple[int, ...], coefficient: Polynomial) -> None:
    key = row, column, word
    operator[key] = add(operator.get(key, {}), coefficient)
    if not operator[key]:
        del operator[key]


def op_scale(operator: Operator, coefficient: Polynomial) -> Operator:
    return {key: multiply(value, coefficient) for key, value in operator.items()}


def structure_constants() -> dict[tuple[int, int, int], Scalar]:
    result: dict[tuple[int, int, int], Scalar] = {}
    for first, second, target, value in ((1, 2, 3, U_BERGER), (2, 3, 1, V_BERGER), (3, 1, 2, V_BERGER)):
        result[first, second, target] = value
        result[second, first, target] = scalar_scale(value, -1)
    return result


def levi_civita() -> dict[tuple[int, int, int], Scalar]:
    """Return Gamma^target_first,second from the invariant-frame Koszul formula."""
    structure = structure_constants()
    result = {}
    for first in range(4):
        for second in range(4):
            for target in range(4):
                lowered = ZERO_SCALAR
                for value, sign in (
                    (structure.get((first, second, target), ZERO_SCALAR), ETA[target]),
                    (structure.get((second, target, first), ZERO_SCALAR), -ETA[first]),
                    (structure.get((target, first, second), ZERO_SCALAR), ETA[second]),
                ):
                    lowered = scalar_add(lowered, scalar_scale(value, sign))
                raised = (lowered[0] * ETA[target] / 2, lowered[1] * ETA[target] / 2)
                if raised != ZERO_SCALAR:
                    result[target, first, second] = raised
    return result


def connection_audit(connection: dict[tuple[int, int, int], Scalar]) -> dict[str, Any]:
    structure = structure_constants()
    torsion = metric = 0
    for a in range(4):
        for b in range(4):
            for c in range(4):
                lhs = scalar_add(connection.get((c, a, b), ZERO_SCALAR), scalar_scale(connection.get((c, b, a), ZERO_SCALAR), -1))
                torsion += lhs != structure.get((a, b, c), ZERO_SCALAR)
                lowered_ab_c = scalar_scale(connection.get((c, a, b), ZERO_SCALAR), ETA[c])
                lowered_ac_b = scalar_scale(connection.get((b, a, c), ZERO_SCALAR), ETA[b])
                metric += scalar_add(lowered_ab_c, lowered_ac_b) != ZERO_SCALAR
    wave_trace = []
    for target in range(4):
        value = ZERO_SCALAR
        for axis in range(4):
            value = scalar_add(value, scalar_scale(connection.get((target, axis, axis), ZERO_SCALAR), ETA[axis]))
        wave_trace.append(value)
    if torsion or metric or any(value != ZERO_SCALAR for value in wave_trace):
        raise AssertionError("Berger Levi-Civita audit failed")
    entries = [
        {"target": target, "first": first, "second": second, "coefficient": serialize({(): coefficient})[0]["coefficient"]}
        for (target, first, second), coefficient in sorted(connection.items())
    ]
    return {
        "entries": entries,
        "entry_count": len(entries),
        "entries_canonical_sha256": canonical_sha256(entries),
        "torsion_defect_count": torsion,
        "metric_compatibility_defect_count": metric,
        "contracted_scalar_wave_connection": [serialize({(): value})[0]["coefficient"] if value != ZERO_SCALAR else None for value in wave_trace],
        "contracted_scalar_wave_connection_defect_count": sum(value != ZERO_SCALAR for value in wave_trace),
    }


def symmetric_index(first: int, second: int) -> int:
    return METRIC_COMPONENTS.index(tuple(sorted((first, second))))


def covariant_second_rod(name: str, first: int, second: int, connection) -> Polynomial:
    value = derivative(derivative(background(name), second), first)
    for target in range(4):
        coefficient = connection.get((target, first, second), ZERO_SCALAR)
        if coefficient != ZERO_SCALAR:
            value = add(value, scale(derivative(background(name), target), scalar_scale(coefficient, -1)))
    return value


def gamma_blocks() -> tuple[Operator, Operator]:
    forward: Operator = {}
    sharp: Operator = {}
    for rod_index, name in enumerate(RODS):
        for spatial in range(1, 4):
            coefficient = derivative(background(name), spatial)
            op_add(forward, 64 + rod_index, spatial - 1, (), coefficient)
            op_add(sharp, 48 + spatial, 74 + rod_index, (), scale(coefficient, rational(-1)))
    return forward, sharp


def rod_wave_block() -> Operator:
    operator: Operator = {}
    factor = parameter("epsilon_R_squared")
    for rod_index in range(6):
        for axis in range(4):
            op_add(operator, 74 + rod_index, 64 + rod_index, (axis, axis), scale(factor, rational(ETA[axis])))
    return operator


def mixed_rod_metric_block(connection) -> Operator:
    operator: Operator = {}
    for rod_index, name in enumerate(RODS):
        rod_first = [derivative(background(name), axis) for axis in range(4)]
        rod_second = [[covariant_second_rod(name, first, second, connection) for second in range(4)] for first in range(4)]
        # -h^{mu nu} nabla_mu nabla_nu Rbar.
        for first in range(4):
            for second in range(4):
                component = symmetric_index(first, second)
                coefficient = scale(rod_second[first][second], rational(-ETA[first] * ETA[second]))
                op_add(operator, 74 + rod_index, 5 + component, (), coefficient)
        # -(nabla_mu h^{mu nu}) nabla_nu Rbar.
        for nu in range(4):
            for mu in range(4):
                component = symmetric_index(mu, nu)
                coefficient = scale(rod_first[nu], rational(-ETA[mu] * ETA[nu]))
                op_add(operator, 74 + rod_index, 5 + component, (mu,), coefficient)
            for mu in range(4):
                for rho in range(4):
                    gamma_trace = connection.get((mu, mu, rho), ZERO_SCALAR)
                    if gamma_trace != ZERO_SCALAR:
                        component = symmetric_index(rho, nu)
                        coefficient = scale(rod_first[nu], scalar_scale(gamma_trace, -ETA[rho] * ETA[nu]))
                        op_add(operator, 74 + rod_index, 5 + component, (), coefficient)
                    gamma = connection.get((nu, mu, rho), ZERO_SCALAR)
                    if gamma != ZERO_SCALAR:
                        component = symmetric_index(mu, rho)
                        coefficient = scale(rod_first[nu], scalar_scale(gamma, -ETA[mu] * ETA[rho]))
                        op_add(operator, 74 + rod_index, 5 + component, (), coefficient)
        # +(1/2) nabla^nu(tr h) nabla_nu Rbar.
        for nu in range(4):
            for diagonal in range(4):
                component = symmetric_index(diagonal, diagonal)
                coefficient = scale(rod_first[nu], rational(Fraction(ETA[nu] * ETA[diagonal], 2)))
                op_add(operator, 74 + rod_index, 5 + component, (nu,), coefficient)
    return op_scale(operator, parameter("epsilon_R_squared"))


def formal_transpose_mixed(operator: Operator) -> Operator:
    output: Operator = {}
    for (row, column, word), coefficient in operator.items():
        rod_index = row - 74
        component = column - 5
        if not word:
            op_add(output, 27 + component, 64 + rod_index, (), coefficient)
        elif len(word) == 1:
            axis = word[0]
            op_add(output, 27 + component, 64 + rod_index, (axis,), scale(coefficient, rational(-1)))
            op_add(output, 27 + component, 64 + rod_index, (), scale(derivative(coefficient, axis), rational(-1)))
        else:
            raise AssertionError("mixed rod Hessian exceeded first order")
    return output


def component_matrix(component: int) -> list[list[int]]:
    first, second = METRIC_COMPONENTS[component]
    value = [[0 for _ in range(4)] for _ in range(4)]
    value[first][second] = 1
    value[second][first] = 1
    return value


def metric_hessian_uv_coefficient(h, k, first: int, second: int) -> Fraction:
    tr_h = sum(ETA[a] * h[a][a] for a in range(4))
    tr_k = sum(ETA[a] * k[a][a] for a in range(4))
    tr_hk = sum(ETA[a] * ETA[b] * h[a][b] * k[a][b] for a in range(4) for b in range(4))
    value = Fraction(0)
    if first == second:
        value += (Fraction(1, 4) * tr_h * tr_k - Fraction(1, 2) * tr_hk) * ETA[first]
    value -= Fraction(1, 2) * tr_h * ETA[first] * ETA[second] * k[first][second]
    value -= Fraction(1, 2) * tr_k * ETA[first] * ETA[second] * h[first][second]
    mixed = sum(
        ETA[first] * ETA[second] * ETA[c] * (
            h[first][c] * k[c][second] + k[first][c] * h[c][second]
        )
        for c in range(4)
    )
    value += mixed
    return -value / 2


@lru_cache(maxsize=1)
def action_hessian_audit() -> dict[str, Any]:
    eta = sp.diag(-1, 1, 1, 1)
    vectors = (sp.Matrix([1, 2, 0, 1]), sp.Matrix([0, 1, 3, -1]))
    defects = 0
    symmetry = 0
    a, b = sp.symbols("a b")
    for vector in vectors:
        for left in range(10):
            h = sp.Matrix(component_matrix(left))
            for right in range(10):
                k = sp.Matrix(component_matrix(right))
                g = eta + a * h + b * k
                density = -sp.sqrt(-g.det()) * (vector.T * g.inv() * vector)[0] / 2
                direct = sp.diff(density, a, b).subs({a: 0, b: 0})
                formula = sum(
                    sp.Rational(metric_hessian_uv_coefficient(component_matrix(left), component_matrix(right), mu, nu).numerator,
                                metric_hessian_uv_coefficient(component_matrix(left), component_matrix(right), mu, nu).denominator)
                    * vector[mu] * vector[nu]
                    for mu in range(4) for nu in range(4)
                )
                defects += sp.simplify(direct - formula) != 0
                symmetry += metric_hessian_uv_coefficient(component_matrix(left), component_matrix(right), 0, 0) != metric_hessian_uv_coefficient(component_matrix(right), component_matrix(left), 0, 0)
    if defects or symmetry:
        raise AssertionError("local rod metric Hessian formula failed")
    return {"direct_second_variation_fixture_count": 200, "direct_second_variation_defect_count": defects, "metric_component_symmetry_defect_count": symmetry}


def scalar_sympy(value: Scalar) -> sp.Expr:
    return sp.Rational(value[0].numerator, value[0].denominator) + sp.sqrt(10) * sp.Rational(
        value[1].numerator, value[1].denominator
    )


def evaluate_fixture_polynomial(value: Polynomial, jets: dict[tuple[int, int, int, int], int]) -> sp.Expr:
    total = sp.S.Zero
    for monomial, coefficient in value.items():
        term = scalar_sympy(coefficient)
        for kind, name, _vertical, spacetime in monomial:
            if kind == "parameter":
                factor = 1
            else:
                if name != RODS[0]:
                    raise AssertionError("mixed-wave fixture unexpectedly crossed rod backgrounds")
                factor = jets[spacetime]
            term *= factor
        total += term
    return sp.expand(total)


def raw_second_fixture(
    first: int,
    second: int,
    first_jets: tuple[int, ...],
    pbw_jets: dict[tuple[int, int, int, int], int],
) -> sp.Expr:
    multiindex = tuple(int(axis == first) + int(axis == second) for axis in range(4))
    value = sp.Integer(pbw_jets[multiindex])
    if first > second:
        for target, coefficient in structure_constants().items():
            left, right, output = target
            if (left, right) == (first, second):
                value += scalar_sympy(coefficient) * first_jets[output]
    return sp.expand(value)


def direct_scalar_wave_metric_variation(
    component: int,
    component_value: int,
    component_derivatives: tuple[int, ...],
    first_jets: tuple[int, ...],
    pbw_jets: dict[tuple[int, int, int, int], int],
) -> sp.Expr:
    """Differentiate the general nonholonomic-frame scalar wave operator."""
    t = sp.symbols("t")
    eta = sp.diag(*ETA)
    basis = sp.Matrix(component_matrix(component))
    h = component_value * basis
    dh = [component_derivatives[axis] * basis for axis in range(4)]
    g = eta + t * h
    inverse = g.inv()
    structure = structure_constants()
    connection: dict[tuple[int, int, int], sp.Expr] = {}
    for first in range(4):
        for second in range(4):
            lowered = []
            for target in range(4):
                value = t * (dh[first][second, target] + dh[second][first, target] - dh[target][first, second])
                for output in range(4):
                    value -= g[first, output] * scalar_sympy(structure.get((second, target, output), ZERO_SCALAR))
                    value += g[second, output] * scalar_sympy(structure.get((target, first, output), ZERO_SCALAR))
                    value += g[target, output] * scalar_sympy(structure.get((first, second, output), ZERO_SCALAR))
                lowered.append(value / 2)
            for output in range(4):
                connection[output, first, second] = sum(inverse[output, target] * lowered[target] for target in range(4))
    box = sp.S.Zero
    for first in range(4):
        for second in range(4):
            covariant_second = raw_second_fixture(first, second, first_jets, pbw_jets)
            covariant_second -= sum(connection[target, first, second] * first_jets[target] for target in range(4))
            box += inverse[first, second] * covariant_second
    return sp.simplify(sp.diff(box, t).subs(t, 0))


@lru_cache(maxsize=1)
def mixed_wave_audit() -> dict[str, Any]:
    connection = levi_civita()
    operator = mixed_rod_metric_block(connection)
    first_jets = (2, -1, 3, 4)
    pbw_jets = {
        (2, 0, 0, 0): 5,
        (1, 1, 0, 0): -2,
        (1, 0, 1, 0): 7,
        (1, 0, 0, 1): 1,
        (0, 2, 0, 0): -4,
        (0, 1, 1, 0): 6,
        (0, 1, 0, 1): -3,
        (0, 0, 2, 0): 8,
        (0, 0, 1, 1): 2,
        (0, 0, 0, 2): -5,
    }
    jets = {(0, 0, 0, 0): 11}
    jets.update({tuple(int(axis == target) for axis in range(4)): first_jets[target] for target in range(4)})
    jets.update(pbw_jets)
    defects = 0
    for component in range(10):
        component_value = component + 2
        component_derivatives = tuple((component + 1) * (axis + 2) - 5 for axis in range(4))
        actual = sp.S.Zero
        for (row, column, word), coefficient in operator.items():
            if row != 74 or column != 5 + component:
                continue
            input_value = component_value if not word else component_derivatives[word[0]]
            actual += evaluate_fixture_polynomial(coefficient, jets) * input_value
        direct = direct_scalar_wave_metric_variation(
            component,
            component_value,
            component_derivatives,
            first_jets,
            pbw_jets,
        )
        defects += sp.simplify(actual - direct) != 0
    if defects:
        raise AssertionError("mixed scalar-wave metric variation failed")
    return {
        "direct_nonholonomic_metric_variation_fixture_count": 10,
        "direct_nonholonomic_metric_variation_defect_count": defects,
        "fixture_uses_nonzero_metric_first_jets": True,
        "fixture_uses_pbw_reduced_scalar_second_jets": True,
    }


def rod_metric_metric_block() -> Operator:
    operator: Operator = {}
    factor = parameter("epsilon_R_squared")
    matrices = [component_matrix(index) for index in range(10)]
    for output_component, k in enumerate(matrices):
        for input_component, h in enumerate(matrices):
            coefficient: Polynomial = {}
            for name in RODS:
                gradients = [derivative(background(name), axis) for axis in range(4)]
                for first in range(4):
                    for second in range(4):
                        number = metric_hessian_uv_coefficient(h, k, first, second)
                        if number:
                            coefficient = add(coefficient, scale(product(gradients[first], gradients[second]), rational(number)))
            if coefficient:
                op_add(operator, 27 + output_component, 5 + input_component, (), multiply(factor, coefficient))
    return operator


def serialize_operator(operator: Operator) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for (row, column, word), polynomial in sorted(operator.items()):
        for term in serialize(polynomial):
            grouped[row, column].append({
                "coefficient": term["coefficient"],
                "coefficient_factors": term["factors"],
                "input_pbw_multiindex": [word.count(axis) for axis in range(4)],
            })
    return [{"output_row": row, "input_row": column, "terms": terms} for (row, column), terms in sorted(grouped.items())]


@lru_cache(maxsize=1)
def payload_document() -> dict[str, Any]:
    connection = levi_civita()
    gamma, gamma_sharp = gamma_blocks()
    mixed = mixed_rod_metric_block(connection)
    blocks = [
        ("Gamma_R", gamma),
        ("Gamma_R_sharp", gamma_sharp),
        ("K_RR", rod_wave_block()),
        ("K_Rh", mixed),
        ("K_hR", formal_transpose_mixed(mixed)),
        ("Delta_K_hh_rod", rod_metric_metric_block()),
    ]
    serialized = [{"id": name, "entries": serialize_operator(operator)} for name, operator in blocks]
    positions = {(row, column) for _name, operator in blocks for row, column, _word in operator}
    terms = sum(len(serialize(polynomial)) for _name, operator in blocks for polynomial in operator.values())
    return {
        "schema": "closed-universe-berger-108-row-local-rod-hessian-pbw-overlay-payload-v1",
        "result_id": "BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY_PAYLOAD",
        "scalar_matrix_shape": [108, 108],
        "blocks": serialized,
        "block_count": len(blocks),
        "nonzero_matrix_position_count": len(positions),
        "serialized_term_count": terms,
        "row_support": sorted({row for _name, operator in blocks for row, _column, _word in operator}),
        "column_support": sorted({column for _name, operator in blocks for _row, column, _word in operator}),
        "blocks_canonical_sha256": canonical_sha256(serialized),
    }


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONCOMMUTING_BERGER_FRAME_PBW_CERTIFIED",
        "background_quotient": "SIX_ROD_BACKGROUND_SPECIALIZATION_EXPORTED",
        "rod_gravity_unary": "ROD_GRAVITY_ACTION_HESSIAN_EXPORTED",
        "shifted_q2_phi2": "SCALAR_SHIFTED_Q2_PHI2_PBW_OVERLAY_EXPORTED",
    }
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required dependency dropped: {name}.{flag}")
    connection = connection_audit(levi_civita())
    action_audit = action_hessian_audit()
    mixed_audit = mixed_wave_audit()
    payload = payload or payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_sha256 = payload_sha256 or hashlib.sha256(rendered_payload.encode()).hexdigest()
    summary = {key: payload[key] for key in ("block_count", "nonzero_matrix_position_count", "serialized_term_count", "row_support", "column_support", "blocks_canonical_sha256")}
    return {
        "schema": "closed-universe-berger-108-row-local-rod-hessian-pbw-overlay-v1",
        "result_id": "BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_SCALAR_LOCAL_ROD_GAUGE_WAVE_HESSIAN_OVERLAY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": value["result_id"], "sha256": sha256(path)} for (name, path), value in zip(DEPENDENCIES.items(), values.values())},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": payload_sha256, **summary},
        "connection_audit": connection,
        "action_hessian_audit": action_audit,
        "mixed_wave_audit": mixed_audit,
        "operator_contract": {
            "blocks": ["Gamma_R", "Gamma_R_sharp", "K_RR", "K_Rh", "K_hR", "Delta_K_hh_rod"],
            "rod_wave": "epsilon_R_squared(-e0^2+e1^2+e2^2+e3^2)",
            "mixed_formula": values["rod_gravity_unary"]["raw_covariant_rod_hessian"]["K_Rh"],
            "metric_metric_formula": values["rod_gravity_unary"]["raw_covariant_rod_hessian"]["Delta_K_hh_rod"],
            "frozen_pairing_adjoint": "K_hR is the explicit formal transpose of K_Rh; Gamma_R_sharp is the signed zero-order odd-pairing adjoint",
            "clock_dressing_order": "linearized first jet only",
            "missing_nonlinear_completion": "the second jet of the raw-to-dressed clock canonical transformation and its cotangent lift; equivalently the action-derived radial/temporal clock-source blocks required when sqrt(-gHat) gHat^{-1}(dR,dR) is expressed in the linearly dressed carrier",
        },
        "identity_disposition": {
            "connection_torsion_and_metric_compatibility": True,
            "local_odd_cyclicity_by_explicit_transpose_and_symmetric_hessian": True,
            "covariant_rod_noether_identity_imported": True,
            "complete_108_row_q1_nilpotency_replayed": False,
            "complete_108_row_q1_odd_cyclicity_replayed": False,
        },
        "flags": {
            "SCALAR_ROD_LOCAL_HESSIAN_PBW_OVERLAY_EXPORTED": True,
            "SCALAR_ROD_GRAVITY_Q1_PBW_OVERLAY_EXPORTED": True,
            "SCALAR_SHIFTED_Q2_PHI2_PBW_OVERLAY_IMPORTED": True,
            "SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED": False,
            "COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "COMPOSE_AND_REPLAY_COMPLETE_SCALAR_108_ROW_Q1",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate scalarizes the six linearly clock-dressed Berger rod gauge actions and their signed cotangent adjoints, the six epsilon_R_squared scalar wave blocks, the mixed rod--metric Hessian and its explicit frozen-pairing formal transpose, and the rod-induced metric--metric Hessian. The invariant-frame Levi-Civita coefficients are derived by the Koszul formula over Q(sqrt(10)) and independently audited for torsion, metric compatibility, and zero contracted scalar-wave connection. All ten metric-component columns of the mixed block are checked by directly varying the general nonholonomic-frame scalar wave operator with nonzero metric first jets and PBW-reduced scalar second jets; the metric Hessian is checked against two hundred direct exact second variations of the rod density. The phrase linearly clock-dressed is deliberate: the dependency closure supplies only the first jet of the raw-to-dressed clock canonical map. It does not supply the second jet or its cotangent lift, equivalently the radial and temporal clock-source completion generated when the invariant rod action is expressed in this linear carrier. Together with the separately certified shifted q2_64(Phi2,-) payload, this closes only the explicitly listed scalar overlay inputs. It does not certify their complete 108-row nilpotency, export the missing nonlinear clock completion, export scalar q2 on the full carrier, solve backreaction, restrict to the tangent cone, activate Bridge 3, prove finite-parameter causal propagation or make a quantum claim."
        ),
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = payload_document()
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    value = build(payload=payload, payload_sha256=hashlib.sha256(rendered_payload.encode()).hexdigest())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
    if args.check:
        if not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload:
            raise SystemExit("stale local rod Hessian payload")
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise SystemExit("stale local rod Hessian certificate")
    print("BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
