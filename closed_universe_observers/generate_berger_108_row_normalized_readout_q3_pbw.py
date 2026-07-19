#!/usr/bin/env python3
"""Export the exact normalized two-detector readout q3 PBW tensor."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
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
    ONE_SCALAR, Polynomial, _multiindex_from_word, _pbw_word, add,
    derivative, generator, multiply, scalar_mul, scale, serialize,
)
from closed_universe_observers.generate_berger_108_row_normalized_readout_q2_pbw import (
    J_VERTICAL_ORDER, METRIC_COMPONENTS, OMEGA, RODS, SELECTED_ROD,
    field_strength_slots, first_variation_terms,
)
from d_quotient_classical.backreacted_clock import berger_support_local_q2 as jet_engine


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_NORMALIZED_READOUT_Q3_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_NORMALIZED_READOUT_Q3_PBW_PAYLOAD.json"
GENERATED = P / "generated/berger_108_row_normalized_readout_q3_pbw"
SCHEMA = P / "schema/berger-108-row-normalized-readout-q3-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-normalized-readout-q3-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-normalized-readout-q3-pbw.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "apparatus_action": P / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "normalized_unary": P / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
    "normalized_readout_q2": P / "certificates/BERGER_108_ROW_NORMALIZED_READOUT_Q2_PBW.json",
}
SOURCE_FILES = [Path(__file__), P / "verify_berger_108_row_normalized_readout_q3_pbw.py", P / "tests/test_berger_108_row_normalized_readout_q3_pbw.py", SCHEMA, PAYLOAD_SCHEMA, REPORT]

Slot = tuple[int, tuple[int, ...]]
TensorKey = tuple[int, int, tuple[int, ...], int, tuple[int, ...], int, tuple[int, ...]]
Tensor = dict[TensorKey, Polynomial]
ROD_SYMBOLS = sp.symbols("rod_background_0:4")


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


def background(name: str, axis: int) -> Polynomial:
    return derivative({(generator("background", name),): ONE_SCALAR}, axis)


def product(*values: Polynomial) -> Polynomial:
    result = constant(1)
    for value in values:
        result = multiply(result, value)
    return result


def one_hot(length: int, *positions: int) -> tuple[int, ...]:
    counts = [0] * length
    for position in positions:
        counts[position] += 1
    return tuple(counts)


def add_term(tensor: Tensor, output: int, slots: tuple[Slot, Slot, Slot], coefficient: Polynomial) -> None:
    reductions = [tuple(_pbw_word(word)) for _, word in slots]
    for first, second, third in itertools.product(*reductions):
        words = (first[0], second[0], third[0])
        factor = scalar_mul(first[1], scalar_mul(second[1], third[1]))
        key: TensorKey = (output, slots[0][0], words[0], slots[1][0], words[1], slots[2][0], words[2])
        tensor[key] = add(tensor.get(key, {}), scale(coefficient, factor))
        if not tensor[key]:
            del tensor[key]


def add_permutations(tensor: Tensor, output: int, slots: tuple[Slot, Slot, Slot], coefficient: Polynomial) -> None:
    values = {tuple(slots[index] for index in order) for order in itertools.permutations(range(3))}
    for permuted in sorted(values):
        add_term(tensor, output, permuted, coefficient)  # type: ignore[arg-type]


@dataclass
class PJet2:
    background: Polynomial
    linear: dict[Slot, Polynomial]
    bilinear: dict[tuple[Slot, Slot], Polynomial]


def polynomial_sum(*values: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for value in values:
        result = add(result, value)
    return result


def multiply_jets(left: PJet2, right: PJet2) -> PJet2:
    linear: dict[Slot, Polynomial] = {}
    for slot in set(left.linear) | set(right.linear):
        value = polynomial_sum(
            multiply(left.linear.get(slot, {}), right.background),
            multiply(left.background, right.linear.get(slot, {})),
        )
        if value:
            linear[slot] = value
    bilinear: dict[tuple[Slot, Slot], Polynomial] = {}
    slots = set(left.linear) | set(right.linear)
    pairs = set(left.bilinear) | set(right.bilinear) | set(itertools.product(slots, repeat=2))
    for first, second in pairs:
        value = polynomial_sum(
            multiply(left.bilinear.get((first, second), {}), right.background),
            multiply(left.background, right.bilinear.get((first, second), {})),
            multiply(left.linear.get(first, {}), right.linear.get(second, {})),
            multiply(right.linear.get(first, {}), left.linear.get(second, {})),
        )
        if value:
            bilinear[first, second] = value
    return PJet2(multiply(left.background, right.background), linear, bilinear)


def multiply_all_jets(*values: PJet2) -> PJet2:
    result = PJet2(constant(1), {}, {})
    for value in values:
        result = multiply_jets(result, value)
    return result


def sympy_polynomial(value: sp.Expr, rod_name: str) -> Polynomial:
    result: Polynomial = {}
    polynomial = sp.Poly(sp.expand(value), *ROD_SYMBOLS)
    for exponents, coefficient in polynomial.terms():
        coefficient = sp.Rational(coefficient)
        term = constant(Fraction(int(coefficient.p), int(coefficient.q)))
        for axis, exponent in enumerate(exponents):
            for _ in range(exponent):
                term = multiply(term, background(rod_name, axis))
        result = add(result, term)
    return result


def component_slot(component: int, selected_row: int) -> Slot:
    if 0 <= component < 10:
        return 5 + component, ()
    if 10 <= component < 14:
        return 16, (component - 10,)
    if 14 <= component < 18:
        return selected_row, (component - 14,)
    raise ValueError(component)


@lru_cache(maxsize=None)
def contraction_jet(channel: int, pair: tuple[int, int]) -> PJet2:
    metric = jet_engine._metric()
    inverse = jet_engine._inverse_metric(metric)
    density = jet_engine._volume_density_ratio()
    clock = {axis: jet_engine.Jet2.field(10 + axis, sp.Rational(3, 4) if axis == 0 else sp.S.Zero) for axis in range(4)}
    rod = {axis: jet_engine.Jet2.field(14 + axis, ROD_SYMBOLS[axis]) for axis in range(4)}
    polarization = {(first, second): clock[first] * rod[second] - rod[first] * clock[second] for first, second in itertools.product(range(4), repeat=2)}
    first, second = pair
    value = density * jet_engine._sum_jets(
        inverse[(first, left)] * inverse[(second, right)] * polarization[(left, right)]
        for left, right in itertools.product(range(4), repeat=2)
    )
    selected_row = 64 + 3 * channel + SELECTED_ROD[channel]
    linear: dict[Slot, Polynomial] = {}
    for component, word, coefficient in value.linear.terms:
        slot = component_slot(component, selected_row)
        linear[slot] = add(linear.get(slot, {}), sympy_polynomial(coefficient, RODS[channel][SELECTED_ROD[channel]]))
    bilinear: dict[tuple[Slot, Slot], Polynomial] = {}
    for first_component, first_word, second_component, second_word, coefficient in value.bilinear.terms:
        slots = component_slot(first_component, selected_row), component_slot(second_component, selected_row)
        bilinear[slots] = add(bilinear.get(slots, {}), sympy_polynomial(coefficient, RODS[channel][SELECTED_ROD[channel]]))
    return PJet2(sympy_polynomial(value.background, RODS[channel][SELECTED_ROD[channel]]), linear, bilinear)


def f_jet(channel: int) -> PJet2:
    slot = (16, ())
    return PJet2(profile(f"f{channel}"), {slot: profile(f"f{channel}", (1,))}, {(slot, slot): profile(f"f{channel}", (2,))})


def rho_jet(channel: int) -> PJet2:
    slots = tuple((64 + 3 * channel + local, ()) for local in range(3))
    return PJet2(
        profile(f"rho{channel}"),
        {slot: profile(f"rho{channel}", one_hot(3, index)) for index, slot in enumerate(slots)},
        {(left, right): profile(f"rho{channel}", one_hot(3, first, second)) for first, left in enumerate(slots) for second, right in enumerate(slots)},
    )


def jacobian_slots(channel: int) -> tuple[Slot, ...]:
    return tuple(
        [(5 + component, ()) for component in range(10)]
        + [(16, (axis,)) for axis in range(4)]
        + [(64 + 3 * channel + rod, (axis,)) for rod in range(3) for axis in range(4)]
    )


def jacobian_jet(channel: int) -> PJet2:
    slots = jacobian_slots(channel)
    return PJet2(
        profile(f"J{channel}"),
        {slot: profile(f"J{channel}", one_hot(len(slots), index)) for index, slot in enumerate(slots)},
        {(left, right): profile(f"J{channel}", one_hot(len(slots), first, second)) for first, left in enumerate(slots) for second, right in enumerate(slots)},
    )


@lru_cache(maxsize=None)
def readout_jet(channel: int, pair: tuple[int, int]) -> PJet2:
    return multiply_all_jets(f_jet(channel), rho_jet(channel), jacobian_jet(channel), contraction_jet(channel, pair))


def x_dual(row: int) -> int:
    if 5 <= row <= 16:
        return 27 + row - 5
    if 64 <= row <= 69:
        return 74 + row - 64
    raise ValueError(row)


@lru_cache(maxsize=1)
def direct_action_blocks() -> dict[str, Tensor]:
    blocks: dict[str, Tensor] = {}
    for channel in (0, 1):
        p, p_dual = 72 + channel, 82 + channel
        forward: Tensor = {}
        maxwell: Tensor = {}
        geometry: Tensor = {}
        for pair in ((a, b) for a in range(4) for b in range(a + 1, 4)):
            jet = readout_jet(channel, pair)
            for left, right in sorted(jet.bilinear):
                if left > right:
                    continue
                base_coefficient = multiply(scale(parameter("kappa"), rational(-1)), jet.bilinear[left, right])
                for a_row, a_word, field_coefficient in field_strength_slots(pair):
                    coefficient = scale(base_coefficient, rational(field_coefficient))
                    add_permutations(forward, p_dual, (left, right, (a_row, a_word)), coefficient)
                    a_dual = 59 + a_row - 55
                    if not a_word:
                        add_permutations(maxwell, a_dual, ((p, ()), left, right), scale(coefficient, rational(-1)))
                    else:
                        axis, = a_word
                        rest: tuple[Slot, Slot, Slot] = ((p, ()), left, right)
                        add_permutations(maxwell, a_dual, rest, derivative(coefficient, axis))
                        for differentiated in range(3):
                            slots = list(rest)
                            slots[differentiated] = (slots[differentiated][0], (axis, *slots[differentiated][1]))
                            add_permutations(maxwell, a_dual, tuple(slots), coefficient)  # type: ignore[arg-type]
                    for varied, other in {(left, right), (right, left)}:
                        rest = ((p, ()), other, (a_row, a_word))
                        if not varied[1]:
                            add_permutations(geometry, x_dual(varied[0]), rest, coefficient)
                        elif len(varied[1]) == 1:
                            axis = varied[1][0]
                            negative = scale(coefficient, rational(-1))
                            add_permutations(geometry, x_dual(varied[0]), rest, derivative(negative, axis))
                            for differentiated in range(3):
                                slots = list(rest)
                                slots[differentiated] = (slots[differentiated][0], (axis, *slots[differentiated][1]))
                                add_permutations(geometry, x_dual(varied[0]), tuple(slots), negative)  # type: ignore[arg-type]
                        else:
                            raise AssertionError("readout q3 geometry word order changed")
        blocks[f"readout{channel}_p_euler"] = forward
        blocks[f"readout{channel}_A_euler"] = maxwell
        blocks[f"readout{channel}_geometry_euler"] = geometry
    return blocks


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


@lru_cache(maxsize=1)
def merged_tensor() -> Tensor:
    return merge_blocks(direct_action_blocks())


def permuted_key(key: TensorKey, order: tuple[int, int, int]) -> TensorKey:
    slots = ((key[1], key[2]), (key[3], key[4]), (key[5], key[6]))
    ordered = tuple(slots[index] for index in order)
    return key[0], ordered[0][0], ordered[0][1], ordered[1][0], ordered[1][1], ordered[2][0], ordered[2][1]


def symmetry_defects(tensor: Tensor) -> int:
    return sum(value != tensor.get(permuted_key(key, order), {}) for key, value in tensor.items() for order in ((1, 0, 2), (0, 2, 1)))


def difference_count(left: Tensor, right: Tensor) -> int:
    return sum(left.get(key, {}) != right.get(key, {}) for key in set(left) | set(right))


def transpose_predictions(blocks: dict[str, Tensor]) -> tuple[Tensor, Tensor]:
    predicted_maxwell: Tensor = {}
    predicted_geometry: Tensor = {}
    for channel in (0, 1):
        p, p_dual = 72 + channel, 82 + channel
        for key, coefficient in blocks[f"readout{channel}_p_euler"].items():
            output, first, first_word, second, second_word, third, third_word = key
            left, right, a_slot = (first, first_word), (second, second_word), (third, third_word)
            if output != p_dual or not (55 <= third <= 58) or left > right:
                continue
            a_dual = 59 + third - 55
            if not third_word:
                add_permutations(predicted_maxwell, a_dual, ((p, ()), left, right), scale(coefficient, rational(-1)))
            else:
                axis, = third_word
                rest: tuple[Slot, Slot, Slot] = ((p, ()), left, right)
                add_permutations(predicted_maxwell, a_dual, rest, derivative(coefficient, axis))
                for differentiated in range(3):
                    slots = list(rest)
                    slots[differentiated] = (slots[differentiated][0], (axis, *slots[differentiated][1]))
                    add_permutations(predicted_maxwell, a_dual, tuple(slots), coefficient)  # type: ignore[arg-type]
            for varied, other in {(left, right), (right, left)}:
                rest = ((p, ()), other, a_slot)
                if not varied[1]:
                    add_permutations(predicted_geometry, x_dual(varied[0]), rest, coefficient)
                else:
                    axis, = varied[1]
                    negative = scale(coefficient, rational(-1))
                    add_permutations(predicted_geometry, x_dual(varied[0]), rest, derivative(negative, axis))
                    for differentiated in range(3):
                        slots = list(rest)
                        slots[differentiated] = (slots[differentiated][0], (axis, *slots[differentiated][1]))
                        add_permutations(predicted_geometry, x_dual(varied[0]), tuple(slots), negative)  # type: ignore[arg-type]
    return predicted_maxwell, predicted_geometry


def jet_audit() -> dict[str, Any]:
    first_defects = 0
    second_symmetry = 0
    first_count = 0
    second_count = 0
    second_profile_orders: set[tuple[str, int]] = set()
    for channel in (0, 1):
        for pair in ((a, b) for a in range(4) for b in range(a + 1, 4)):
            jet = readout_jet(channel, pair)
            expected, _ = first_variation_terms(channel)
            expected_pair = {(row, word): coefficient for (row, word, source_pair), coefficient in expected.items() if source_pair == pair}
            first_defects += difference_polynomial_maps(jet.linear, expected_pair)
            first_count += len(jet.linear)
            for (left, right), coefficient in jet.bilinear.items():
                second_count += 1
                second_symmetry += coefficient != jet.bilinear.get((right, left), {})
                for monomial in coefficient:
                    for kind, name, vertical, _spacetime in monomial:
                        if kind == "profile" and sum(vertical) == 2:
                            second_profile_orders.add((name, len(vertical)))
    required_profiles = {(f"f{channel}", 1) for channel in (0, 1)} | {(f"rho{channel}", 3) for channel in (0, 1)} | {(f"J{channel}", 26) for channel in (0, 1)}
    missing_profiles = sorted(required_profiles - second_profile_orders)
    if first_defects or second_symmetry or missing_profiles:
        raise AssertionError("normalized readout second jet audit failed")
    return {"first_jet_regression_term_count": first_count, "first_jet_regression_defect_count": first_defects, "ordered_second_jet_term_count": second_count, "second_jet_permutation_defect_count": second_symmetry, "certified_second_profile_derivative_families": sorted([list(value) for value in second_profile_orders]), "missing_second_profile_derivative_family_count": len(missing_profiles)}


def difference_polynomial_maps(left: dict, right: dict) -> int:
    return sum(left.get(key, {}) != right.get(key, {}) for key in set(left) | set(right))


@lru_cache(maxsize=1)
def action_audit() -> dict[str, Any]:
    audit = jet_audit()
    blocks = direct_action_blocks()
    maxwell = merge_blocks({name: block for name, block in blocks.items() if name.endswith("A_euler")})
    geometry = merge_blocks({name: block for name, block in blocks.items() if name.endswith("geometry_euler")})
    predicted_maxwell, predicted_geometry = transpose_predictions(blocks)
    audit.update({"graded_symmetry_defect_count": symmetry_defects(merged_tensor()), "p_to_Maxwell_formal_transpose_defect_count": difference_count(maxwell, predicted_maxwell), "p_to_geometry_formal_transpose_defect_count": difference_count(geometry, predicted_geometry), "cyclicity_scope": "complete two-detector quartic normalized readout action tensor"})
    if any(audit[name] for name in ("graded_symmetry_defect_count", "p_to_Maxwell_formal_transpose_defect_count", "p_to_geometry_formal_transpose_defect_count")):
        raise AssertionError("normalized readout q3 symmetry or cyclicity failed")
    return audit


def serialize_tensor(tensor: Tensor) -> list[dict[str, Any]]:
    rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for key, polynomial in sorted(tensor.items()):
        output, first, first_word, second, second_word, third, third_word = key
        for term in serialize(polynomial):
            rows[output].append({"first_input_row": first, "first_pbw_multiindex": list(_multiindex_from_word(first_word)), "second_input_row": second, "second_pbw_multiindex": list(_multiindex_from_word(second_word)), "third_input_row": third, "third_pbw_multiindex": list(_multiindex_from_word(third_word)), "coefficient": term["coefficient"], "coefficient_factors": term["factors"]})
    return [{"output": output, "terms": terms} for output, terms in sorted(rows.items())]


def tensor_digest(tensor: Tensor) -> str:
    digest = hashlib.sha256()
    for key, polynomial in sorted(tensor.items()):
        digest.update(json.dumps([key[0], key[1], list(_multiindex_from_word(key[2])), key[3], list(_multiindex_from_word(key[4])), key[5], list(_multiindex_from_word(key[6])), serialize(polynomial)], sort_keys=True, separators=(",", ":")).encode())
    return digest.hexdigest()


def gzip_bytes(value: Any) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as handle:
        handle.write((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode())
    return buffer.getvalue()


@lru_cache(maxsize=1)
def payload_bundle() -> tuple[dict[str, Any], dict[int, bytes]]:
    blocks = direct_action_blocks(); tensor = merged_tensor()
    outputs = sorted({key[0] for key in tensor})
    chunks = []
    encoded = {}
    row_hashes = {}
    serialized_total = 0
    for output in outputs:
        row_tensor = {key: value for key, value in tensor.items() if key[0] == output}
        row = serialize_tensor(row_tensor)[0]
        body_hash = canonical_sha256(row)
        row_document = {**row, "canonical_sha256": body_hash}
        data = gzip_bytes(row_document)
        encoded[output] = data
        row_hashes[output] = body_hash
        serialized_count = len(row["terms"])
        serialized_total += serialized_count
        chunks.append({"output": output, "path": str((GENERATED / f"row_{output:03d}.json.gz").relative_to(ROOT)), "file_sha256": hashlib.sha256(data).hexdigest(), "canonical_sha256": body_hash, "operator_key_count": len(row_tensor), "serialized_term_count": serialized_count, "maximum_total_jet_order": max((sum(term["first_pbw_multiindex"]) + sum(term["second_pbw_multiindex"]) + sum(term["third_pbw_multiindex"]) for term in row["terms"]), default=0)})
    payload = {"schema": "closed-universe-berger-108-row-normalized-readout-q3-pbw-payload-v1", "result_id": "BERGER_108_ROW_NORMALIZED_READOUT_Q3_PBW_PAYLOAD", "shape": [108, 108, 108, 108], "coefficient_field": "Q(sqrt(10)) differential profile-jet algebra", "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3", "factorial_convention": "suspended-graded-symmetric-factorial-v1", "source_action": "-kappa sum_a integral p_a sqrt(-g) f_a(Theta) rho_a(R_a) J_a C_g(dA,dTheta wedge dR_aI(a))", "J_vertical_coordinate_order": list(J_VERTICAL_ORDER), "storage": "deterministic-gzip-strict-json-row-chunks", "block_hashes": {name: tensor_digest(block) for name, block in blocks.items()}, "chunks": chunks, "nonzero_output_rows": outputs, "operator_key_count": len(tensor), "serialized_term_count": serialized_total, "canonical_sha256": canonical_sha256(row_hashes)}
    return payload, encoded


def payload_document() -> dict[str, Any]:
    return payload_bundle()[0]


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {"component_contract": "EXACT_DETECTOR_AND_SWITCH_SPECIALIZATIONS_BOUND", "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED", "apparatus_action": "APPARATUS_Q3_ACTION_JET_EXPORTED", "normalized_unary": "PROFILE_NORMALIZATION_EXACT", "normalized_readout_q2": "APPARATUS_NORMALIZED_READOUT_Q2_PBW_EXPORTED"}
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True: raise AssertionError(f"required gate dropped: {name}.{flag}")
    audit = action_audit(); payload = payload or payload_document(); rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"; payload_sha256 = payload_sha256 or hashlib.sha256(rendered_payload.encode()).hexdigest()
    tensor = merged_tensor(); deleted_key = sorted(tensor)[-1]; output = deleted_key[0]; original_row = {key: value for key, value in tensor.items() if key[0] == output}; mutated_row = dict(original_row); del mutated_row[deleted_key]
    mutation = canonical_sha256(serialize_tensor(mutated_row)) != canonical_sha256(serialize_tensor(original_row))
    boundary = "This exact LOCAL-ALGEBRAIC certificate exports the complete normalized two-detector readout contribution to q3 on the canonical 108-row Berger carrier. A declared second-order jet algebra differentiates the full product sqrt(-g) f_a(Theta) rho_a(R_a) J_a C_g(dA,dTheta wedge dR_selected) over the detector clock, three rod values, ten metric components, four clock gradients and twelve local rod gradients. It retains exact f'', rho_IJ and all 26-by-26 normalized-Jacobian vertical Hessian generators, every cross-factor term, the second inverse-metric/volume variation and the bilinear polarization channel. Its first derivative recovers the certified q2 first-variation tensor exactly and its second derivative is permutation symmetric. Raising the common quartic action supplies p-, Maxwell-, metric-, clock- and rod-cotangent outputs; independent PBW formal adjunction from the p rows reproduces every Maxwell and geometry row, including coefficient derivatives and derivatives distributed over three inputs. Graded symmetry and a deletion mutation pass. This certifies normalized readout q3 only. Rod and memory q3 are separately certified; base gravity-clock-Maxwell and physical-emitter q3 remain to assemble, and scalar-BV/emitter-Diff-BV structural zeros remain to ledger. Complete q3, arity replay, K_Berger equivariance, observer-morphism stability, detector response on Z2, nonlinear rank, physical Bridge 3, finite-parameter causal propagation and quantum claims remain unavailable. No cross-background mode identification is made."
    return {"schema": "closed-universe-berger-108-row-normalized-readout-q3-pbw-v1", "result_id": "BERGER_108_ROW_NORMALIZED_READOUT_Q3_PBW", "setting_id": values["component_contract"]["setting_id"], "claim_status": "CERTIFIED_COMPLETE_NORMALIZED_READOUT_Q3_PBW_SUBBLOCK", "atlas_status": "CERTIFIED", "dependency_tags": ["LOCAL-ALGEBRAIC"], "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()}, "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": payload_sha256, "operator_key_count": payload["operator_key_count"], "serialized_term_count": payload["serialized_term_count"], "nonzero_output_rows": payload["nonzero_output_rows"], "canonical_sha256": payload["canonical_sha256"]}, "second_jet_and_cyclicity_audit": audit, "mutation_results": [{"name": "delete_last_normalized_readout_q3_key", "detected": mutation}], "activation_disposition": {"normalized_readout_q3_subblock_exported": True, "complete_scalar_q3_exported": False, "arity_replay_certified": False, "K_Berger_equivariance_certified": False, "observer_morphism_stability_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False}, "flags": {"APPARATUS_NORMALIZED_READOUT_Q3_PBW_EXPORTED": True, "APPARATUS_NORMALIZED_READOUT_Q3_GRADED_SYMMETRIC": True, "APPARATUS_NORMALIZED_READOUT_Q3_CYCLIC": True, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False}, "next_gate": "EXPORT_PHYSICAL_EMITTER_Q3_PBW_BLOCK", "claim_boundary": boundary, "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args(); payload, encoded = payload_bundle(); rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"; payload_schema = json.loads(PAYLOAD_SCHEMA.read_text()); Draft202012Validator.check_schema(payload_schema); Draft202012Validator(payload_schema).validate(payload); value = build(payload=payload, payload_sha256=hashlib.sha256(rendered_payload.encode()).hexdigest()); schema = json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered = json.dumps(value, indent=2, sort_keys=True) + "\n";
    if args.emit:
        GENERATED.mkdir(parents=True, exist_ok=True)
        for output, data in encoded.items(): (GENERATED / f"row_{output:03d}.json.gz").write_bytes(data)
        PAYLOAD.write_text(rendered_payload); CERTIFICATE.write_text(rendered)
    if args.check:
        if not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload or not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered: raise SystemExit("stale normalized readout q3 artifact")
        for output, data in encoded.items():
            path = GENERATED / f"row_{output:03d}.json.gz"
            if not path.exists() or path.read_bytes() != data: raise SystemExit(f"stale normalized readout q3 row {output}")
    print("BERGER_108_ROW_NORMALIZED_READOUT_Q3_PBW generation: PASS"); return 0


if __name__ == "__main__": raise SystemExit(main())
