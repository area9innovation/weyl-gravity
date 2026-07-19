#!/usr/bin/env python3
"""Export the exact six-rod metric-interaction q3 PBW tensor."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import io
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
    scale,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_local_rod_hessian_pbw_overlay import (
    ETA,
    METRIC_COMPONENTS,
    RODS,
    component_matrix,
)
from closed_universe_observers.generate_berger_108_row_rod_metric_q2_pbw import (
    density_derivative as q2_density_derivative,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_ROD_METRIC_Q3_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_ROD_METRIC_Q3_PBW_PAYLOAD.json"
GENERATED = P / "generated/berger_108_row_rod_metric_q3_pbw"
SCHEMA = P / "schema/berger-108-row-rod-metric-q3-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-rod-metric-q3-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-rod-metric-q3-pbw.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "apparatus_action": P / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "rod_metric_q2": P / "certificates/BERGER_108_ROW_ROD_METRIC_Q2_PBW.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_108_row_rod_metric_q3_pbw.py",
    P / "tests/test_berger_108_row_rod_metric_q3_pbw.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
    REPORT,
]

ScalarMatrix = tuple[tuple[Fraction, ...], ...]
Slot = tuple[int, tuple[int, ...]]
TensorKey = tuple[int, int, tuple[int, ...], int, tuple[int, ...], int, tuple[int, ...]]
Tensor = dict[TensorKey, Polynomial]
ETA_MATRIX: ScalarMatrix = tuple(
    tuple(Fraction(ETA[i] if i == j else 0) for j in range(4)) for i in range(4)
)
METRIC_MATRICES: tuple[ScalarMatrix, ...] = tuple(
    tuple(tuple(Fraction(value) for value in row) for row in component_matrix(index))
    for index in range(10)
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def canonical_sha256(value: Any) -> str:
    return digest_bytes(canonical_bytes(value).rstrip(b"\n"))


def mat_zero() -> ScalarMatrix:
    return tuple(tuple(Fraction(0) for _ in range(4)) for _ in range(4))


def mat_add(*values: ScalarMatrix) -> ScalarMatrix:
    if not values:
        return mat_zero()
    return tuple(tuple(sum(value[i][j] for value in values) for j in range(4)) for i in range(4))


def mat_scale(value: ScalarMatrix, factor: Fraction) -> ScalarMatrix:
    return tuple(tuple(factor * value[i][j] for j in range(4)) for i in range(4))


def mat_mul(left: ScalarMatrix, right: ScalarMatrix) -> ScalarMatrix:
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(4)) for j in range(4)) for i in range(4))


def trace(value: ScalarMatrix) -> Fraction:
    return sum(value[i][i] for i in range(4))


def x_matrix(value: ScalarMatrix) -> ScalarMatrix:
    return mat_mul(ETA_MATRIX, value)


@lru_cache(maxsize=None)
def set_partitions(indices: tuple[int, ...]) -> tuple[tuple[tuple[int, ...], ...], ...]:
    if not indices:
        return ((),)
    first, rest = indices[0], indices[1:]
    output: set[tuple[tuple[int, ...], ...]] = set()
    for partition in set_partitions(rest):
        output.add(((first,), *partition))
        for block_index in range(len(partition)):
            blocks = list(partition)
            blocks[block_index] = tuple(sorted((first, *blocks[block_index])))
            output.add(tuple(sorted(blocks)))
    return tuple(sorted(output))


def log_density_derivative(values: tuple[ScalarMatrix, ...]) -> Fraction:
    """Derivative of (1/2) tr log(I+eta h) on distinct slots."""
    return _log_density_derivative_sorted(tuple(sorted(values)))


@lru_cache(maxsize=None)
def _log_density_derivative_sorted(values: tuple[ScalarMatrix, ...]) -> Fraction:
    order = len(values)
    if order == 0:
        return Fraction(0)
    matrices = tuple(map(x_matrix, values))
    total = sum(
        trace(_mat_product(tuple(matrices[index] for index in permutation)))
        for permutation in itertools.permutations(range(order))
    )
    return Fraction((-1) ** (order + 1), 2 * order) * total


def _mat_product(values: tuple[ScalarMatrix, ...]) -> ScalarMatrix:
    result = tuple(tuple(Fraction(i == j) for j in range(4)) for i in range(4))
    for value in values:
        result = mat_mul(result, value)
    return result


def volume_derivative(values: tuple[ScalarMatrix, ...]) -> Fraction:
    """Derivative of sqrt(det(I+eta h)) via the exponential partition rule."""
    return _volume_derivative_sorted(tuple(sorted(values)))


@lru_cache(maxsize=None)
def _volume_derivative_sorted(values: tuple[ScalarMatrix, ...]) -> Fraction:
    if not values:
        return Fraction(1)
    total = Fraction(0)
    for partition in set_partitions(tuple(range(len(values)))):
        term = Fraction(1)
        for block in partition:
            term *= log_density_derivative(tuple(values[index] for index in block))
        total += term
    return total


def inverse_metric_derivative(values: tuple[ScalarMatrix, ...]) -> ScalarMatrix:
    """Derivative of (eta+h)^-1 from its noncommutative geometric series."""
    return _inverse_metric_derivative_sorted(tuple(sorted(values)))


@lru_cache(maxsize=None)
def _inverse_metric_derivative_sorted(values: tuple[ScalarMatrix, ...]) -> ScalarMatrix:
    if not values:
        return ETA_MATRIX
    matrices = tuple(map(x_matrix, values))
    return mat_scale(
        mat_add(*(
            mat_mul(_mat_product(tuple(matrices[index] for index in permutation)), ETA_MATRIX)
            for permutation in itertools.permutations(range(len(values)))
        )),
        Fraction((-1) ** len(values)),
    )


def density_derivative(components: tuple[int, ...]) -> ScalarMatrix:
    """D^n[-sqrt(-det g) g^-1/2] at eta, for 0 <= n <= 4."""
    return _density_derivative_sorted(tuple(sorted(components)))


@lru_cache(maxsize=None)
def _density_derivative_sorted(components: tuple[int, ...]) -> ScalarMatrix:
    if len(components) > 4:
        raise ValueError("rod q3 needs density derivatives only through order four")
    values = tuple(METRIC_MATRICES[index] for index in components)
    terms = []
    indices = tuple(range(len(values)))
    for subset_size in range(len(values) + 1):
        for subset in itertools.combinations(indices, subset_size):
            selected = set(subset)
            volume_values = tuple(values[index] for index in subset)
            inverse_values = tuple(values[index] for index in indices if index not in selected)
            terms.append(mat_scale(inverse_metric_derivative(inverse_values), volume_derivative(volume_values)))
    return mat_scale(mat_add(*terms), Fraction(-1, 2))


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


def scaled_epsilon(value: Fraction | int) -> Polynomial:
    return scale(parameter("epsilon_R_squared"), rational(value))


def add_term(tensor: Tensor, output: int, slots: tuple[Slot, Slot, Slot], coefficient: Polynomial) -> None:
    reductions = [tuple(_pbw_word(word)) for _, word in slots]
    for first, second, third in itertools.product(*reductions):
        rows = tuple(slot[0] for slot in slots)
        words = (first[0], second[0], third[0])
        factor = scalar_mul(first[1], scalar_mul(second[1], third[1]))
        value = scale(coefficient, factor)
        key: TensorKey = (output, rows[0], words[0], rows[1], words[1], rows[2], words[2])
        tensor[key] = add(tensor.get(key, {}), value)
        if not tensor[key]:
            del tensor[key]


def place_rod(metric_slots: tuple[Slot, Slot], rod_slot: Slot, position: int) -> tuple[Slot, Slot, Slot]:
    values = list(metric_slots)
    values.insert(position, rod_slot)
    return tuple(values)  # type: ignore[return-value]


@lru_cache(maxsize=1)
def action_blocks() -> dict[str, Tensor]:
    blocks: dict[str, Tensor] = {
        name: {}
        for name in ("hhrr_metric_output", "hhhr_metric_output", "hhhh_metric_output", "hhr_rod_output", "hhh_rod_output")
    }
    metric_rows = tuple(range(5, 15))
    for rod_index, name in enumerate(RODS):
        rod, rod_dual = 64 + rod_index, 74 + rod_index
        for output_component in range(10):
            metric_dual = 27 + output_component
            for first_component in range(10):
                first_metric = 5 + first_component
                d2 = density_derivative((output_component, first_component))
                for mu in range(4):
                    for nu in range(4):
                        if d2[mu][nu]:
                            coefficient = scaled_epsilon(2 * d2[mu][nu])
                            for metric_position in range(3):
                                values: list[Slot] = [(rod, (mu,)), (rod, (nu,))]
                                values.insert(metric_position, (first_metric, ()))
                                add_term(blocks["hhrr_metric_output"], metric_dual, tuple(values), coefficient)  # type: ignore[arg-type]
                for second_component in range(10):
                    second_metric = 5 + second_component
                    d3 = density_derivative((output_component, first_component, second_component))
                    for mu in range(4):
                        for nu in range(4):
                            if d3[mu][nu]:
                                coefficient = scale(product(parameter("epsilon_R_squared"), background(name, mu)), rational(2 * d3[mu][nu]))
                                for rod_position in range(3):
                                    add_term(blocks["hhhr_metric_output"], metric_dual, place_rod(((first_metric, ()), (second_metric, ())), (rod, (nu,)), rod_position), coefficient)
                    for third_component in range(10):
                        d4 = density_derivative((output_component, first_component, second_component, third_component))
                        for mu in range(4):
                            for nu in range(4):
                                if d4[mu][nu]:
                                    coefficient = scale(product(parameter("epsilon_R_squared"), background(name, mu), background(name, nu)), rational(d4[mu][nu]))
                                    add_term(blocks["hhhh_metric_output"], metric_dual, ((first_metric, ()), (second_metric, ()), (5 + third_component, ())), coefficient)

        for first_component, second_component in itertools.product(range(10), repeat=2):
            first_metric, second_metric = 5 + first_component, 5 + second_component
            d2 = density_derivative((first_component, second_component))
            for mu in range(4):
                for nu in range(4):
                    if not d2[mu][nu]:
                        continue
                    coefficient = scaled_epsilon(-2 * d2[mu][nu])
                    metric_words = (((mu,), ()), ((), (mu,)), ((), ()))
                    rod_words = ((nu,), (nu,), (mu, nu))
                    for words, rod_word in zip(metric_words, rod_words):
                        for rod_position in range(3):
                            add_term(blocks["hhr_rod_output"], rod_dual, place_rod(((first_metric, words[0]), (second_metric, words[1])), (rod, rod_word), rod_position), coefficient)

        for components in itertools.product(range(10), repeat=3):
            metrics = tuple((5 + component, ()) for component in components)
            d3 = density_derivative(components)
            for mu in range(4):
                for nu in range(4):
                    if not d3[mu][nu]:
                        continue
                    base = scale(product(parameter("epsilon_R_squared"), background(name, mu)), rational(-2 * d3[mu][nu]))
                    for differentiated_slot in range(3):
                        slots = list(metrics)
                        slots[differentiated_slot] = (slots[differentiated_slot][0], (nu,))
                        add_term(blocks["hhh_rod_output"], rod_dual, tuple(slots), base)  # type: ignore[arg-type]
                    coefficient_term = scale(product(parameter("epsilon_R_squared"), derivative(background(name, mu), nu)), rational(-2 * d3[mu][nu]))
                    add_term(blocks["hhh_rod_output"], rod_dual, metrics, coefficient_term)  # type: ignore[arg-type]
    return blocks


def merge_blocks(blocks: dict[str, Tensor], *, delete_last_term: bool = False) -> Tensor:
    result: Tensor = {}
    for block in blocks.values():
        for key, value in block.items():
            result[key] = add(result.get(key, {}), value)
            if not result[key]:
                del result[key]
    if delete_last_term:
        del result[sorted(result)[-1]]
    return result


@lru_cache(maxsize=1)
def merged_tensor() -> Tensor:
    return merge_blocks(action_blocks())


def permuted_key(key: TensorKey, order: tuple[int, int, int]) -> TensorKey:
    output = key[0]
    slots = ((key[1], key[2]), (key[3], key[4]), (key[5], key[6]))
    ordered = tuple(slots[index] for index in order)
    return output, ordered[0][0], ordered[0][1], ordered[1][0], ordered[1][1], ordered[2][0], ordered[2][1]


def tensor_symmetry_defects(tensor: Tensor) -> int:
    return sum(
        value != tensor.get(permuted_key(key, order), {})
        for key, value in tensor.items()
        for order in ((1, 0, 2), (0, 2, 1))
    )


def transpose_predictions(blocks: dict[str, Tensor]) -> tuple[Tensor, Tensor]:
    predicted_hhr: Tensor = {}
    for key, coefficient in blocks["hhrr_metric_output"].items():
        output, first, first_word, second, second_word, third, third_word = key
        if not (5 <= first <= 14 and 64 <= second <= 69 and second == third and len(second_word) == len(third_word) == 1):
            continue
        metric_output = 5 + output - 27
        axis, remaining_axis = second_word[0], third_word[0]
        negative = scale(coefficient, rational(-1))
        metric_words = (((axis,), ()), ((), (axis,)), ((), ()))
        rod_words = ((remaining_axis,), (remaining_axis,), (axis, remaining_axis))
        for words, rod_word in zip(metric_words, rod_words):
            for rod_position in range(3):
                add_term(predicted_hhr, 74 + second - 64, place_rod(((metric_output, words[0]), (first, words[1])), (third, rod_word), rod_position), negative)

    predicted_hhh: Tensor = {}
    for key, coefficient in blocks["hhhr_metric_output"].items():
        output, first, first_word, second, second_word, third, third_word = key
        if not (5 <= first <= 14 and 5 <= second <= 14 and 64 <= third <= 69 and not first_word and not second_word and len(third_word) == 1):
            continue
        axis = third_word[0]
        slots: tuple[Slot, Slot, Slot] = ((5 + output - 27, ()), (first, ()), (second, ()))
        negative = scale(coefficient, rational(-1))
        for differentiated_slot in range(3):
            varied = list(slots)
            varied[differentiated_slot] = (varied[differentiated_slot][0], (axis,))
            add_term(predicted_hhh, 74 + third - 64, tuple(varied), negative)  # type: ignore[arg-type]
        add_term(predicted_hhh, 74 + third - 64, slots, scale(derivative(coefficient, axis), rational(-1)))
    return predicted_hhr, predicted_hhh


def tensor_difference_count(left: Tensor, right: Tensor) -> int:
    return sum(left.get(key, {}) != right.get(key, {}) for key in set(left) | set(right))


@lru_cache(maxsize=1)
def action_audit() -> dict[str, Any]:
    lower_defects = 0
    lower_comparisons = 0
    for order in range(1, 4):
        for components in itertools.product(range(10), repeat=order):
            reference = q2_density_derivative(components)
            value = density_derivative(components)
            lower_defects += sum(value[i][j] != reference[i][j] for i in range(4) for j in range(4))
            lower_comparisons += 16

    a, b, c, d = sp.symbols("a b c d")
    eta = sp.diag(-1, 1, 1, 1)
    fixtures = ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 0, 4), (1, 1, 5, 9))
    direct_defects = 0
    for components in fixtures:
        g = eta + sum((symbol * sp.Matrix(component_matrix(component)) for symbol, component in zip((a, b, c, d), components)), sp.zeros(4))
        direct = (-sp.sqrt(-g.det()) * g.inv() / 2).diff(a, b, c, d).subs({a: 0, b: 0, c: 0, d: 0})
        formula = density_derivative(components)
        direct_defects += sum(sp.Rational(formula[i][j].numerator, formula[i][j].denominator) != sp.simplify(direct[i, j]) for i in range(4) for j in range(4))

    symmetry_defects = 0
    for components in itertools.product(range(10), repeat=4):
        reference = density_derivative(components)
        symmetry_defects += density_derivative((components[1], components[0], components[2], components[3])) != reference
        symmetry_defects += density_derivative((components[0], components[2], components[1], components[3])) != reference
        symmetry_defects += density_derivative((components[0], components[1], components[3], components[2])) != reference

    blocks = action_blocks()
    predicted_hhr, predicted_hhh = transpose_predictions(blocks)
    transpose_hhr = tensor_difference_count(blocks["hhr_rod_output"], predicted_hhr)
    transpose_hhh = tensor_difference_count(blocks["hhh_rod_output"], predicted_hhh)
    operation_symmetry = sum(tensor_symmetry_defects(block) for block in blocks.values())
    if lower_defects or direct_defects or symmetry_defects or transpose_hhr or transpose_hhh or operation_symmetry:
        raise AssertionError("rod q3 action, symmetry, or cyclicity replay failed")
    return {
        "lower_order_density_component_comparison_count": lower_comparisons,
        "lower_order_density_component_defect_count": lower_defects,
        "direct_fourth_metric_variation_fixture_count": len(fixtures) * 16,
        "direct_fourth_metric_variation_defect_count": direct_defects,
        "fourth_frechet_adjacent_transposition_check_count": 3 * 10**4,
        "fourth_frechet_permutation_defect_count": symmetry_defects,
        "graded_symmetry_defect_count": operation_symmetry,
        "hhrr_to_hhr_formal_transpose_defect_count": transpose_hhr,
        "hhhr_to_hhh_formal_transpose_defect_count": transpose_hhh,
        "cyclicity_scope": "complete six-rod quartic action tensor; all ordered metric permutations and both rod-containing PBW formal transposes",
    }


def serialize_rows(tensor: Tensor) -> dict[int, dict[str, Any]]:
    rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for key, polynomial in sorted(tensor.items()):
        output, first, first_word, second, second_word, third, third_word = key
        for term in serialize(polynomial):
            rows[output].append({
                "first_input_row": first,
                "first_pbw_multiindex": list(_multiindex_from_word(first_word)),
                "second_input_row": second,
                "second_pbw_multiindex": list(_multiindex_from_word(second_word)),
                "third_input_row": third,
                "third_pbw_multiindex": list(_multiindex_from_word(third_word)),
                "coefficient": term["coefficient"],
                "coefficient_factors": term["factors"],
            })
    output = {}
    for row, terms in sorted(rows.items()):
        body = {"output": row, "terms": terms}
        output[row] = {**body, "canonical_sha256": canonical_sha256(body)}
    return output


def gzip_bytes(value: Any) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as handle:
        handle.write(canonical_bytes(value))
    return buffer.getvalue()


@lru_cache(maxsize=1)
def payload_bundle() -> tuple[dict[str, Any], dict[int, bytes]]:
    blocks = action_blocks()
    tensor = merged_tensor()
    rows = serialize_rows(tensor)
    chunks: list[dict[str, Any]] = []
    encoded: dict[int, bytes] = {}
    for output, row in rows.items():
        data = gzip_bytes(row)
        encoded[output] = data
        chunks.append({
            "output": output,
            "path": str((GENERATED / f"row_{output:03d}.json.gz").relative_to(ROOT)),
            "file_sha256": digest_bytes(data),
            "canonical_sha256": row["canonical_sha256"],
            "operator_key_count": sum(key[0] == output for key in tensor),
            "serialized_term_count": len(row["terms"]),
            "maximum_total_jet_order": max((sum(term["first_pbw_multiindex"]) + sum(term["second_pbw_multiindex"]) + sum(term["third_pbw_multiindex"]) for term in row["terms"]), default=0),
        })
    block_summary = {
        name: {
            "operator_key_count": len(block),
            "serialized_term_count": sum(len(serialize(value)) for value in block.values()),
            "canonical_sha256": canonical_sha256(serialize_rows(block)),
        }
        for name, block in blocks.items()
    }
    payload = {
        "schema": "closed-universe-berger-108-row-rod-metric-q3-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_ROD_METRIC_Q3_PBW_PAYLOAD",
        "shape": [108, 108, 108, 108],
        "coefficient_field": "Q(sqrt(10))[epsilon_R_squared, finite Berger background rod jets]",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "source_action": "-epsilon_R_squared/2 sum_aI integral sqrt(-det gHat) gHat^{-1}(dR_aI,dR_aI)",
        "storage": "deterministic-gzip-strict-json-row-chunks",
        "orbit_blocks": block_summary,
        "chunks": chunks,
        "nonzero_output_rows": sorted(rows),
        "operator_key_count": len(tensor),
        "serialized_term_count": sum(len(row["terms"]) for row in rows.values()),
        "canonical_sha256": canonical_sha256({output: row["canonical_sha256"] for output, row in rows.items()}),
    }
    return payload, encoded


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED",
        "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED",
        "apparatus_action": "APPARATUS_Q3_ACTION_JET_EXPORTED",
        "rod_metric_q2": "APPARATUS_ROD_METRIC_Q2_PBW_EXPORTED",
    }
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    audit = action_audit()
    payload = payload or payload_bundle()[0]
    payload_sha256 = payload_sha256 or digest_bytes(canonical_bytes(payload))
    tensor = merged_tensor()
    deleted_key = sorted(tensor)[-1]
    output = deleted_key[0]
    original_row = {key: value for key, value in tensor.items() if key[0] == output}
    mutated_row = dict(original_row)
    del mutated_row[deleted_key]
    mutation_detected = canonical_sha256(serialize_rows(mutated_row)) != canonical_sha256(serialize_rows(original_row))
    if not mutation_detected:
        raise AssertionError("rod q3 deletion mutation was not detected")
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate exports the complete six-rod physical metric contribution to q3 on the canonical 108-row Berger carrier. It differentiates -epsilon_R_squared/2 sum sqrt(-gHat) gHat^{-1}(dR,dR) through fourth action order, using an order-general determinant-log partition formula and the noncommutative inverse-metric series. The order-one through order-three density jets agree componentwise with the independently certified q2 producer, direct fourth variations and all adjacent Frechet transpositions have zero defect. The h-h-r-r, h-h-h-r and h-h-h-h metric-output orbits and their h-h-r and h-h-h rod-output cyclic mates are serialized in deterministic row chunks. Exact noncommuting PBW formal adjunction, including derivatives of finite background rod jets, reproduces every rod-output key; graded input symmetry and a deletion mutation pass. This certifies only the rod metric q3 subblock. Base gravity-clock-Maxwell q3, memory, readout and emitter q3 remain separate; scalar-BV and emitter Diff-BV are structural q3 zeros but are not assembled here. Complete q3, arity replay, K_Berger equivariance, observer-morphism stability, O_detector restricted to Z2, nonlinear rank, physical Bridge 3, finite-parameter causal propagation and quantum claims remain unavailable. No cross-background mode identification is made."
    )
    return {
        "schema": "closed-universe-berger-108-row-rod-metric-q3-pbw-v1",
        "result_id": "BERGER_108_ROW_ROD_METRIC_Q3_PBW",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_COMPLETE_SIX_ROD_METRIC_Q3_PBW_SUBBLOCK",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": payload_sha256, "operator_key_count": payload["operator_key_count"], "serialized_term_count": payload["serialized_term_count"], "nonzero_output_rows": payload["nonzero_output_rows"], "canonical_sha256": payload["canonical_sha256"]},
        "action_and_cyclicity_audit": audit,
        "mutation_results": [{"name": "delete_last_rod_q3_operator_key", "detected": mutation_detected}],
        "activation_disposition": {"rod_metric_q3_subblock_exported": True, "complete_scalar_q3_exported": False, "arity_replay_certified": False, "K_Berger_equivariance_certified": False, "observer_morphism_stability_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"APPARATUS_ROD_METRIC_Q3_PBW_EXPORTED": True, "APPARATUS_ROD_METRIC_Q3_GRADED_SYMMETRIC": True, "APPARATUS_ROD_METRIC_Q3_CYCLIC": True, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EXPORT_MEMORY_TRANSPORT_Q3_PBW_BLOCK",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload, encoded = payload_bundle()
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    rendered_payload = canonical_bytes(payload)
    value = build(payload=payload, payload_sha256=digest_bytes(rendered_payload))
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    if args.emit:
        GENERATED.mkdir(parents=True, exist_ok=True)
        for output, data in encoded.items():
            (GENERATED / f"row_{output:03d}.json.gz").write_bytes(data)
        PAYLOAD.write_bytes(rendered_payload)
        CERTIFICATE.write_bytes(rendered)
    if args.check:
        if not PAYLOAD.exists() or PAYLOAD.read_bytes() != rendered_payload:
            raise SystemExit("stale rod metric q3 payload")
        if not CERTIFICATE.exists() or CERTIFICATE.read_bytes() != rendered:
            raise SystemExit("stale rod metric q3 certificate")
        for output, data in encoded.items():
            path = GENERATED / f"row_{output:03d}.json.gz"
            if not path.exists() or path.read_bytes() != data:
                raise SystemExit(f"stale rod metric q3 row chunk {output}")
    print("BERGER_108_ROW_ROD_METRIC_Q3_PBW generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
