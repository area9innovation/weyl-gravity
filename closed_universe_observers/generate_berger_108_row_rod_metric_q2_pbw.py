#!/usr/bin/env python3
"""Export the exact six-rod metric-interaction q2 PBW tensor."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
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
    scalar_scale,
    scale,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_local_rod_hessian_pbw_overlay import (
    ETA,
    METRIC_COMPONENTS,
    RODS,
    component_matrix,
    metric_hessian_uv_coefficient,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_ROD_METRIC_Q2_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_ROD_METRIC_Q2_PBW_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-rod-metric-q2-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-rod-metric-q2-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-rod-metric-q2-pbw.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "apparatus_action": P / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "local_rod_hessian": P / "certificates/BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY.json",
}
SOURCE_FILES = [Path(__file__), P / "verify_berger_108_row_rod_metric_q2_pbw.py", P / "tests/test_berger_108_row_rod_metric_q2_pbw.py", SCHEMA, PAYLOAD_SCHEMA, REPORT]

ScalarMatrix = tuple[tuple[Fraction, ...], ...]
Tensor = dict[tuple[int, int, tuple[int, ...], int, tuple[int, ...]], Polynomial]
ETA_MATRIX: ScalarMatrix = tuple(tuple(Fraction(ETA[i] if i == j else 0) for j in range(4)) for i in range(4))
METRIC_MATRICES: tuple[ScalarMatrix, ...] = tuple(
    tuple(tuple(Fraction(value) for value in row) for row in component_matrix(index))
    for index in range(10)
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def mat_add(*values: ScalarMatrix) -> ScalarMatrix:
    return tuple(tuple(sum(value[i][j] for value in values) for j in range(4)) for i in range(4))


def mat_scale(value: ScalarMatrix, factor: Fraction) -> ScalarMatrix:
    return tuple(tuple(factor * value[i][j] for j in range(4)) for i in range(4))


def mat_mul(left: ScalarMatrix, right: ScalarMatrix) -> ScalarMatrix:
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(4)) for j in range(4)) for i in range(4))


def trace(value: ScalarMatrix) -> Fraction:
    return sum(value[i][i] for i in range(4))


def x_matrix(value: ScalarMatrix) -> ScalarMatrix:
    return mat_mul(ETA_MATRIX, value)


def g1(value: ScalarMatrix) -> ScalarMatrix:
    return mat_scale(mat_mul(x_matrix(value), ETA_MATRIX), Fraction(-1))


def g2(left: ScalarMatrix, right: ScalarMatrix) -> ScalarMatrix:
    x, y = x_matrix(left), x_matrix(right)
    return mat_add(mat_mul(mat_mul(x, y), ETA_MATRIX), mat_mul(mat_mul(y, x), ETA_MATRIX))


def g3(first: ScalarMatrix, second: ScalarMatrix, third: ScalarMatrix) -> ScalarMatrix:
    matrices = tuple(map(x_matrix, (first, second, third)))
    return mat_scale(
        mat_add(*(mat_mul(mat_mul(mat_mul(matrices[i], matrices[j]), matrices[k]), ETA_MATRIX) for i, j, k in itertools.permutations(range(3)))),
        Fraction(-1),
    )


def s1(value: ScalarMatrix) -> Fraction:
    return trace(x_matrix(value)) / 2


def s2(left: ScalarMatrix, right: ScalarMatrix) -> Fraction:
    x, y = x_matrix(left), x_matrix(right)
    return trace(x) * trace(y) / 4 - trace(mat_mul(x, y)) / 2


def s3(first: ScalarMatrix, second: ScalarMatrix, third: ScalarMatrix) -> Fraction:
    x, y, z = tuple(map(x_matrix, (first, second, third)))
    traces = (trace(x), trace(y), trace(z))
    pair_sum = traces[0] * trace(mat_mul(y, z)) + traces[1] * trace(mat_mul(x, z)) + traces[2] * trace(mat_mul(x, y))
    cubic = sum(trace(mat_mul(mat_mul(matrices[i], matrices[j]), matrices[k])) for matrices in ((x, y, z),) for i, j, k in itertools.permutations(range(3)))
    return traces[0] * traces[1] * traces[2] / 8 - pair_sum / 4 + cubic / 6


@lru_cache(maxsize=None)
def density_derivative(components: tuple[int, ...]) -> ScalarMatrix:
    """D^n[-sqrt(-det g) g^{-1}/2] at the Minkowski frame metric."""
    values = tuple(METRIC_MATRICES[index] for index in components)
    if len(values) == 1:
        h, = values
        result = mat_add(mat_scale(ETA_MATRIX, s1(h)), g1(h))
    elif len(values) == 2:
        h, k = values
        result = mat_add(
            mat_scale(ETA_MATRIX, s2(h, k)),
            mat_scale(g1(k), s1(h)),
            mat_scale(g1(h), s1(k)),
            g2(h, k),
        )
    elif len(values) == 3:
        h, k, ell = values
        result = mat_add(
            mat_scale(ETA_MATRIX, s3(h, k, ell)),
            mat_scale(g1(ell), s2(h, k)),
            mat_scale(g1(k), s2(h, ell)),
            mat_scale(g1(h), s2(k, ell)),
            mat_scale(g2(k, ell), s1(h)),
            mat_scale(g2(h, ell), s1(k)),
            mat_scale(g2(h, k), s1(ell)),
            g3(h, k, ell),
        )
    else:
        raise ValueError("rod q2 needs density derivatives of orders one through three")
    return mat_scale(result, Fraction(-1, 2))


def rational(value: Fraction | int) -> tuple[Fraction, Fraction]:
    return Fraction(value), Fraction(0)


def constant(value: Fraction | int) -> Polynomial:
    return {(): rational(value)}


def parameter(name: str) -> Polynomial:
    return {(generator("parameter", name),): ONE_SCALAR}


def background(name: str, axis: int | None = None) -> Polynomial:
    value = {(generator("background", name),): ONE_SCALAR}
    return value if axis is None else derivative(value, axis)


def product(*values: Polynomial) -> Polynomial:
    result = constant(1)
    for value in values:
        result = multiply(result, value)
    return result


def add_term(tensor: Tensor, output: int, left: int, left_word: Iterable[int], right: int, right_word: Iterable[int], coefficient: Polynomial) -> None:
    for reduced_left, left_factor in _pbw_word(tuple(left_word)):
        for reduced_right, right_factor in _pbw_word(tuple(right_word)):
            value = scale(coefficient, scalar_mul(left_factor, right_factor))
            key = output, left, reduced_left, right, reduced_right
            tensor[key] = add(tensor.get(key, {}), value)
            if not tensor[key]:
                del tensor[key]


def add_symmetric_term(tensor: Tensor, output: int, left: int, left_word: Iterable[int], right: int, right_word: Iterable[int], coefficient: Polynomial) -> None:
    left_word, right_word = tuple(left_word), tuple(right_word)
    add_term(tensor, output, left, left_word, right, right_word, coefficient)
    if (left, left_word) != (right, right_word):
        add_term(tensor, output, right, right_word, left, left_word, coefficient)


def scaled_epsilon(value: Fraction) -> Polynomial:
    return scale(parameter("epsilon_R_squared"), rational(value))


@lru_cache(maxsize=1)
def action_blocks() -> dict[str, Tensor]:
    blocks: dict[str, Tensor] = {name: {} for name in ("hrr_metric_output", "hhr_metric_output", "hhh_metric_output", "hr_rod_output", "hh_rod_output")}
    for rod_index, name in enumerate(RODS):
        rod, rod_dual = 64 + rod_index, 74 + rod_index
        for output_component in range(10):
            metric_dual = 27 + output_component
            d1 = density_derivative((output_component,))
            for mu in range(4):
                for nu in range(4):
                    if d1[mu][nu]:
                        add_term(blocks["hrr_metric_output"], metric_dual, rod, (mu,), rod, (nu,), scaled_epsilon(2 * d1[mu][nu]))
                    for input_component in range(10):
                        metric = 5 + input_component
                        d2 = density_derivative((output_component, input_component))
                        if d2[mu][nu]:
                            coefficient = scale(product(parameter("epsilon_R_squared"), background(name, mu)), rational(2 * d2[mu][nu]))
                            add_symmetric_term(blocks["hhr_metric_output"], metric_dual, metric, (), rod, (nu,), coefficient)
                        for second_component in range(10):
                            d3 = density_derivative((output_component, input_component, second_component))
                            if d3[mu][nu]:
                                coefficient = scale(product(parameter("epsilon_R_squared"), background(name, mu), background(name, nu)), rational(d3[mu][nu]))
                                add_term(blocks["hhh_metric_output"], metric_dual, metric, (), 5 + second_component, (), coefficient)
        for input_component in range(10):
            metric = 5 + input_component
            d1_input = density_derivative((input_component,))
            for mu in range(4):
                for nu in range(4):
                    if d1_input[mu][nu]:
                        coefficient = scaled_epsilon(-2 * d1_input[mu][nu])
                        add_symmetric_term(blocks["hr_rod_output"], rod_dual, metric, (mu,), rod, (nu,), coefficient)
                        add_symmetric_term(blocks["hr_rod_output"], rod_dual, metric, (), rod, (mu, nu), coefficient)
                    for second_component in range(10):
                        d2 = density_derivative((input_component, second_component))
                        if not d2[mu][nu]:
                            continue
                        base = scale(product(parameter("epsilon_R_squared"), background(name, mu)), rational(-2 * d2[mu][nu]))
                        add_term(blocks["hh_rod_output"], rod_dual, metric, (nu,), 5 + second_component, (), base)
                        add_term(blocks["hh_rod_output"], rod_dual, metric, (), 5 + second_component, (nu,), base)
                        second = scale(product(parameter("epsilon_R_squared"), derivative(background(name, mu), nu)), rational(-2 * d2[mu][nu]))
                        add_term(blocks["hh_rod_output"], rod_dual, metric, (), 5 + second_component, (), second)
    return blocks


def merge_blocks(blocks: dict[str, Tensor], *, delete_last_term: bool = False) -> Tensor:
    result: Tensor = {}
    for block in blocks.values():
        for key, value in block.items():
            result[key] = add(result.get(key, {}), value)
    if delete_last_term:
        del result[sorted(result)[-1]]
    return result


def tensor_symmetry_defects(tensor: Tensor) -> int:
    return sum(value != tensor.get((output, right, right_word, left, left_word), {}) for (output, left, left_word, right, right_word), value in tensor.items())


def transpose_predictions(blocks: dict[str, Tensor]) -> tuple[Tensor, Tensor]:
    predicted_a: Tensor = {}
    for (output, left, left_word, right, right_word), coefficient in blocks["hrr_metric_output"].items():
        if len(left_word) != 1 or not 64 <= left <= 69 or left != right:
            raise AssertionError("hrr support changed")
        axis = left_word[0]
        metric = 5 + output - 27
        negative = scale(coefficient, rational(-1))
        add_symmetric_term(predicted_a, 74 + left - 64, metric, (axis,), right, right_word, negative)
        add_symmetric_term(predicted_a, 74 + left - 64, metric, (), right, (axis, *right_word), negative)

    predicted_b: Tensor = {}
    for (output, left, left_word, right, right_word), coefficient in blocks["hhr_metric_output"].items():
        if not (5 <= left <= 14 and 64 <= right <= 69 and not left_word and len(right_word) == 1):
            continue
        axis = right_word[0]
        metric_output = 5 + output - 27
        negative = scale(coefficient, rational(-1))
        rod_output = 74 + right - 64
        add_term(predicted_b, rod_output, metric_output, (axis,), left, (), negative)
        add_term(predicted_b, rod_output, metric_output, (), left, (axis,), negative)
        add_term(predicted_b, rod_output, metric_output, (), left, (), scale(derivative(coefficient, axis), rational(-1)))
    return predicted_a, predicted_b


def action_audit() -> dict[str, Any]:
    d2_defects = 0
    for left in range(10):
        for right in range(10):
            matrix = density_derivative((left, right))
            for mu in range(4):
                for nu in range(4):
                    d2_defects += matrix[mu][nu] != metric_hessian_uv_coefficient(component_matrix(left), component_matrix(right), mu, nu)

    a, b, c = sp.symbols("a b c")
    eta = sp.diag(-1, 1, 1, 1)
    d3_defects = 0
    fixtures = tuple((index % 10, (3 * index + index // 10) % 10, (7 * index + 2 * (index // 10) + 1) % 10) for index in range(40))
    for first, second, third in fixtures:
        g = eta + a * sp.Matrix(component_matrix(first)) + b * sp.Matrix(component_matrix(second)) + c * sp.Matrix(component_matrix(third))
        density = -sp.sqrt(-g.det()) * g.inv() / 2
        direct = density.diff(a, b, c).subs({a: 0, b: 0, c: 0})
        formula = density_derivative((first, second, third))
        d3_defects += sum(sp.Rational(formula[i][j].numerator, formula[i][j].denominator) != sp.simplify(direct[i, j]) for i in range(4) for j in range(4))
    d3_symmetry_defects = 0
    for components in itertools.product(range(10), repeat=3):
        reference = density_derivative(components)
        d3_symmetry_defects += sum(density_derivative(permutation) != reference for permutation in set(itertools.permutations(components)))
    if d2_defects or d3_defects or d3_symmetry_defects:
        raise AssertionError("densitized inverse-metric polarization failed")

    blocks = action_blocks()
    predicted_a, predicted_b = transpose_predictions(blocks)
    transpose_a = sum(value != predicted_a.get(key, {}) for key, value in blocks["hr_rod_output"].items()) + sum(value != blocks["hr_rod_output"].get(key, {}) for key, value in predicted_a.items())
    transpose_b = sum(value != predicted_b.get(key, {}) for key, value in blocks["hh_rod_output"].items()) + sum(value != blocks["hh_rod_output"].get(key, {}) for key, value in predicted_b.items())
    symmetry = sum(tensor_symmetry_defects(block) for block in blocks.values())
    if transpose_a or transpose_b or symmetry:
        raise AssertionError("rod q2 symmetry/cyclicity replay failed")
    return {
        "existing_metric_hessian_coefficient_comparisons": 100 * 16,
        "existing_metric_hessian_coefficient_defect_count": d2_defects,
        "direct_third_metric_variation_fixture_count": len(fixtures) * 16,
        "direct_third_metric_variation_defect_count": d3_defects,
        "third_frechet_permutation_defect_count": d3_symmetry_defects,
        "graded_symmetry_defect_count": symmetry,
        "hrr_to_hr_formal_transpose_defect_count": transpose_a,
        "hhr_to_hh_formal_transpose_defect_count": transpose_b,
        "cyclicity_scope": "complete six-rod cubic action tensor; metric permutations are exact Frechet symmetry and rod permutations are replayed by noncommuting PBW integration by parts",
    }


def serialize_tensor(tensor: Tensor) -> list[dict[str, Any]]:
    rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for (output, left, left_word, right, right_word), polynomial in sorted(tensor.items()):
        for term in serialize(polynomial):
            rows[output].append({
                "left_input_row": left,
                "left_pbw_multiindex": list(_multiindex_from_word(left_word)),
                "right_input_row": right,
                "right_pbw_multiindex": list(_multiindex_from_word(right_word)),
                "coefficient": term["coefficient"],
                "coefficient_factors": term["factors"],
            })
    return [{"output": output, "terms": terms} for output, terms in sorted(rows.items())]


@lru_cache(maxsize=1)
def payload_document() -> dict[str, Any]:
    blocks = action_blocks()
    tensor = merge_blocks(blocks)
    serialized = serialize_tensor(tensor)
    block_summary = {name: {"operator_key_count": len(block), "serialized_term_count": sum(len(serialize(value)) for value in block.values()), "canonical_sha256": canonical_sha256(serialize_tensor(block))} for name, block in blocks.items()}
    return {
        "schema": "closed-universe-berger-108-row-rod-metric-q2-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_ROD_METRIC_Q2_PBW_PAYLOAD",
        "shape": [108, 108, 108],
        "coefficient_field": "Q(sqrt(10))[epsilon_R_squared, finite Berger background rod jets]",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "source_action": "-epsilon_R_squared/2 sum_aI integral sqrt(-det gHat) gHat^{-1}(dR_aI,dR_aI)",
        "orbit_blocks": block_summary,
        "rows": serialized,
        "nonzero_output_rows": sorted({key[0] for key in tensor}),
        "operator_key_count": len(tensor),
        "serialized_term_count": sum(len(row["terms"]) for row in serialized),
        "canonical_sha256": canonical_sha256(serialized),
    }


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED",
        "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED",
        "apparatus_action": "APPARATUS_Q2_ACTION_JET_EXPORTED",
        "local_rod_hessian": "SCALAR_ROD_LOCAL_HESSIAN_PBW_OVERLAY_EXPORTED",
    }
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    audit = action_audit()
    payload = payload or payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_sha256 = payload_sha256 or hashlib.sha256(rendered_payload.encode()).hexdigest()
    mutated = serialize_tensor(merge_blocks(action_blocks(), delete_last_term=True))
    mutation_detected = canonical_sha256(mutated) != payload["canonical_sha256"]
    if not mutation_detected:
        raise AssertionError("rod q2 deletion mutation was not detected")
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate exports the complete six-rod metric-interaction contribution to q2 on the canonical 108-row Berger carrier. Starting from the invariant physical action -epsilon_R_squared/2 sum sqrt(-gHat) gHat^{-1}(dR,dR), it polarizes the densitized inverse metric through third Frechet order. The complete cubic action derivative splits into h-r-r, h-h-r and h-h-h orbits. Raising the first slot with the frozen signed pairing gives all ten metric-cotangent and all six rod-cotangent output rows, with every ordered Berger PBW input word and every finite background rod jet explicit. The second densitized-metric derivative agrees in all 1,600 components with the independently certified unary rod Hessian, while 640 direct SymPy third-variation components verify the new cubic coefficient. Graded symmetry is exact. Independent noncommuting integration-by-parts replays both rod-containing cyclic transposes with zero defect, including coefficient derivatives and Berger commutator terms, and deletion of one operator key is detected. This certifies the rod metric q2 block only. The universal scalar-BV block is separate; memory transport, normalized readout, emitter and their reciprocal q2 sectors, every q3 block, the complete q1q2 and q2q2+q1q3 identities, K_Berger equivariance, observer-morphism stability, detector response on Z2, nonlinear rank, physical Bridge 3, finite-parameter causal propagation and quantum claims remain unavailable. No compact-product mode is identified with a Berger row."
    )
    return {
        "schema": "closed-universe-berger-108-row-rod-metric-q2-pbw-v1",
        "result_id": "BERGER_108_ROW_ROD_METRIC_Q2_PBW",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_COMPLETE_SIX_ROD_METRIC_Q2_PBW_SUBBLOCK",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": payload_sha256, "operator_key_count": payload["operator_key_count"], "serialized_term_count": payload["serialized_term_count"], "nonzero_output_rows": payload["nonzero_output_rows"], "canonical_sha256": payload["canonical_sha256"]},
        "action_and_cyclicity_audit": audit,
        "mutation_results": [{"name": "delete_last_rod_q2_operator_key", "detected": mutation_detected}],
        "activation_disposition": {"rod_metric_q2_subblock_exported": True, "complete_apparatus_q2_exported": False, "complete_emitter_q2_exported": False, "scalar_q3_exported": False, "arity_replay_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"APPARATUS_ROD_METRIC_Q2_PBW_EXPORTED": True, "APPARATUS_ROD_METRIC_Q2_GRADED_SYMMETRIC": True, "APPARATUS_ROD_METRIC_Q2_CYCLIC": True, "COMPLETE_SCALAR_108_ROW_Q2_EXPORTED": False, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EXPORT_MEMORY_TRANSPORT_AND_NORMALIZED_READOUT_Q2_PBW_BLOCKS",
        "claim_boundary": boundary,
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
            raise SystemExit("stale rod metric q2 payload")
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise SystemExit("stale rod metric q2 certificate")
    print("BERGER_108_ROW_ROD_METRIC_Q2_PBW generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
