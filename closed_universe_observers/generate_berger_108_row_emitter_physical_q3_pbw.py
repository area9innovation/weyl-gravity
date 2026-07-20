#!/usr/bin/env python3
"""Export the physical massive-emitter stress/switch q3 PBW subblock."""

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
    Polynomial,
    _multiindex_from_word,
    _pbw_word,
    add,
    derivative,
    multiply,
    scalar_mul,
    scale,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    Factor,
    METRIC_COMPONENTS,
    _component,
    action_add,
    constant,
    differential_slots,
    dual_and_pairing_sign,
    form_basis,
    physical_cubic_action,
    product,
    parameter,
    profile,
    rational,
)
from closed_universe_observers.generate_berger_108_row_rod_metric_q3_pbw import (
    METRIC_MATRICES,
    inverse_metric_derivative,
    volume_derivative,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q3_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q3_PBW_PAYLOAD.json"
GENERATED = P / "generated/berger_108_row_emitter_physical_q3_pbw"
SCHEMA = P / "schema/berger-108-row-emitter-physical-q3-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-emitter-physical-q3-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-emitter-physical-q3-pbw.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "emitter_physical_q2": P / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW.json",
    "emitter_master": P / "certificates/BERGER_108_ROW_EMITTER_Q1_Q2_MASTER_IDENTITY.json",
    "rod_metric_q3": P / "certificates/BERGER_108_ROW_ROD_METRIC_Q3_PBW.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "generate_berger_108_row_emitter_physical_q2_pbw.py",
    P / "generate_berger_108_row_rod_metric_q3_pbw.py",
    P / "verify_berger_108_row_emitter_physical_q3_pbw.py",
    P / "tests/test_berger_108_row_emitter_physical_q3_pbw.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
    REPORT,
]

Slot = tuple[int, tuple[int, ...]]
TensorKey = tuple[int, int, tuple[int, ...], int, tuple[int, ...], int, tuple[int, ...]]
Tensor = dict[TensorKey, Polynomial]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=None)
def form_bilinear_metric_derivative(
    degree: int,
    left: int,
    right: int,
    components: tuple[int, ...],
) -> Fraction:
    """Differentiate sqrt(-g)<e_I,e_J>_g in distinct metric slots."""
    basis = form_basis(degree)
    values = tuple(METRIC_MATRICES[index] for index in components)
    total = Fraction(0)
    for left_indices in itertools.permutations(basis[left]):
        left_component = _component(left_indices, basis)
        assert left_component is not None and left_component[0] == left
        for right_indices in itertools.permutations(basis[right]):
            right_component = _component(right_indices, basis)
            assert right_component is not None and right_component[0] == right
            orientation = left_component[1] * right_component[1]
            contribution = Fraction(0)
            for assignment in itertools.product(range(degree + 1), repeat=len(values)):
                volume_values = tuple(values[index] for index, target in enumerate(assignment) if target == 0)
                term = volume_derivative(volume_values)
                for slot, (first, second) in enumerate(zip(left_indices, right_indices, strict=True), start=1):
                    inverse_values = tuple(values[index] for index, target in enumerate(assignment) if target == slot)
                    term *= inverse_metric_derivative(inverse_values)[first][second]
                contribution += term
            total += orientation * contribution
    return total / Fraction(sp.factorial(degree))


def physical_cubic_action_regression() -> tuple[Action, dict[str, int]]:
    """Rebuild the certified q2 source action with the general metric jet."""
    action: Action = {}
    counts: dict[str, int] = defaultdict(int)
    d_k_template = differential_slots(2, 0)
    d_a = differential_slots(1, 55)
    for emitter, k_offset in ((0, 84), (1, 90)):
        d_k = [[((k_offset + row, word), coefficient) for (row, word), coefficient in terms] for terms in d_k_template]
        mass = parameter(f"m{emitter}_squared")
        switch = product(parameter(f"g{emitter}"), profile(f"h{emitter}"))
        switch_prime = product(parameter(f"g{emitter}"), profile(f"h{emitter}", (1,)))
        for component in range(10):
            metric = (5 + component, ())
            for first, second in itertools.product(range(4), repeat=2):
                jet = form_bilinear_metric_derivative(3, first, second, (component,))
                if jet:
                    for left_factor, left_coefficient in d_k[first]:
                        for right_factor, right_coefficient in d_k[second]:
                            coefficient = scalar_mul(left_coefficient, right_coefficient)
                            action_add(action, (metric, left_factor, right_factor), scale(constant(coefficient), rational(-jet / 2)))
                            counts["free_kinetic_metric"] += 1
            for first, second in itertools.product(range(6), repeat=2):
                jet = form_bilinear_metric_derivative(2, first, second, (component,))
                if not jet:
                    continue
                action_add(action, (metric, (k_offset + first, ()), (k_offset + second, ())), scale(mass, rational(-jet / 2)))
                counts["free_mass_metric"] += 1
                for a_factor, a_coefficient in d_a[second]:
                    action_add(action, (metric, (k_offset + first, ()), a_factor), scale(switch, scalar_mul(rational(jet), a_coefficient)))
                    counts["interaction_metric"] += 1
        for first, second in itertools.product(range(6), repeat=2):
            base = form_bilinear_metric_derivative(2, first, second, ())
            if not base:
                continue
            for a_factor, a_coefficient in d_a[second]:
                action_add(action, ((16, ()), (k_offset + first, ()), a_factor), scale(switch_prime, scalar_mul(rational(base), a_coefficient)))
                counts["interaction_clock_switch"] += 1
    return action, dict(sorted(counts.items()))


def quartic_action_blocks() -> dict[str, Action]:
    blocks: dict[str, Action] = {name: {} for name in (
        "free_kinetic_metric2",
        "free_mass_metric2",
        "interaction_metric2",
        "interaction_metric_clock",
        "interaction_clock2",
    )}
    d_k_template = differential_slots(2, 0)
    d_a = differential_slots(1, 55)
    for emitter, k_offset in ((0, 84), (1, 90)):
        d_k = [[((k_offset + row, word), coefficient) for (row, word), coefficient in terms] for terms in d_k_template]
        mass = parameter(f"m{emitter}_squared")
        switch = product(parameter(f"g{emitter}"), profile(f"h{emitter}"))
        switch_prime = product(parameter(f"g{emitter}"), profile(f"h{emitter}", (1,)))
        switch_second = product(parameter(f"g{emitter}"), profile(f"h{emitter}", (2,)))
        for first_component in range(10):
            first_metric = (5 + first_component, ())
            for second_component in range(first_component, 10):
                second_metric = (5 + second_component, ())
                taylor = Fraction(1, 2) if first_component == second_component else Fraction(1)
                for first, second in itertools.product(range(4), repeat=2):
                    jet = form_bilinear_metric_derivative(3, first, second, (first_component, second_component))
                    if jet:
                        for left_factor, left_coefficient in d_k[first]:
                            for right_factor, right_coefficient in d_k[second]:
                                coefficient = scalar_mul(left_coefficient, right_coefficient)
                                action_add(blocks["free_kinetic_metric2"], (first_metric, second_metric, left_factor, right_factor), scale(constant(coefficient), rational(-taylor * jet / 2)))
                for first, second in itertools.product(range(6), repeat=2):
                    jet = form_bilinear_metric_derivative(2, first, second, (first_component, second_component))
                    if not jet:
                        continue
                    action_add(blocks["free_mass_metric2"], (first_metric, second_metric, (k_offset + first, ()), (k_offset + second, ())), scale(mass, rational(-taylor * jet / 2)))
                    for a_factor, a_coefficient in d_a[second]:
                        action_add(blocks["interaction_metric2"], (first_metric, second_metric, (k_offset + first, ()), a_factor), scale(switch, scalar_mul(rational(taylor * jet), a_coefficient)))
            for first, second in itertools.product(range(6), repeat=2):
                jet = form_bilinear_metric_derivative(2, first, second, (first_component,))
                if not jet:
                    continue
                for a_factor, a_coefficient in d_a[second]:
                    action_add(blocks["interaction_metric_clock"], (first_metric, (16, ()), (k_offset + first, ()), a_factor), scale(switch_prime, scalar_mul(rational(jet), a_coefficient)))
        for first, second in itertools.product(range(6), repeat=2):
            base = form_bilinear_metric_derivative(2, first, second, ())
            if not base:
                continue
            for a_factor, a_coefficient in d_a[second]:
                action_add(blocks["interaction_clock2"], ((16, ()), (16, ()), (k_offset + first, ()), a_factor), scale(switch_second, scalar_mul(rational(base / 2), a_coefficient)))
    return blocks


def add_term(tensor: Tensor, output: int, slots: tuple[Slot, Slot, Slot], coefficient: Polynomial) -> None:
    reductions = [tuple(_pbw_word(word)) for _, word in slots]
    for first, second, third in itertools.product(*reductions):
        words = first[0], second[0], third[0]
        factor = scalar_mul(first[1], scalar_mul(second[1], third[1]))
        key: TensorKey = (output, slots[0][0], words[0], slots[1][0], words[1], slots[2][0], words[2])
        tensor[key] = add(tensor.get(key, {}), scale(coefficient, factor))
        if not tensor[key]:
            del tensor[key]


def add_permutations(tensor: Tensor, output: int, slots: tuple[Slot, Slot, Slot], coefficient: Polynomial) -> None:
    values = [tuple(slots[index] for index in order) for order in itertools.permutations(range(3))]
    for permuted in values:
        add_term(tensor, output, permuted, coefficient)  # type: ignore[arg-type]


def action_to_q3(action: Action) -> Tensor:
    tensor: Tensor = {}
    for factors, coefficient in action.items():
        assert len(factors) == 4
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = dual_and_pairing_sign(varied[0])
            slots = tuple(remaining)
            if not varied[1]:
                add_permutations(tensor, dual, slots, scale(coefficient, rational(pairing_sign)))  # type: ignore[arg-type]
                continue
            if len(varied[1]) != 1:
                raise AssertionError("physical emitter source word order changed")
            axis, = varied[1]
            factor = rational(-pairing_sign)
            add_permutations(tensor, dual, slots, scale(derivative(coefficient, axis), factor))  # type: ignore[arg-type]
            for differentiated in range(3):
                shifted = list(slots)
                shifted[differentiated] = (shifted[differentiated][0], (axis, *shifted[differentiated][1]))
                add_permutations(tensor, dual, tuple(shifted), scale(coefficient, factor))  # type: ignore[arg-type]
    return tensor


@lru_cache(maxsize=1)
def tensor_blocks() -> dict[str, Tensor]:
    return {name: action_to_q3(action) for name, action in quartic_action_blocks().items()}


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
    return merge_blocks(tensor_blocks())


def permuted_key(key: TensorKey, order: tuple[int, int, int]) -> TensorKey:
    slots = ((key[1], key[2]), (key[3], key[4]), (key[5], key[6]))
    ordered = tuple(slots[index] for index in order)
    return key[0], ordered[0][0], ordered[0][1], ordered[1][0], ordered[1][1], ordered[2][0], ordered[2][1]


def symmetry_defects(tensor: Tensor) -> int:
    return sum(value != tensor.get(permuted_key(key, order), {}) for key, value in tensor.items() for order in ((1, 0, 2), (0, 2, 1)))


def metric_jet_audit() -> dict[str, Any]:
    expected_action, _ = physical_cubic_action()
    rebuilt_action, _ = physical_cubic_action_regression()
    action_keys = set(expected_action) | set(rebuilt_action)
    first_defects = sum(expected_action.get(key, {}) != rebuilt_action.get(key, {}) for key in action_keys)
    first_component_defects = 0
    first_component_count = 0
    from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import form_bilinear_metric_jet
    for degree, size in ((2, 6), (3, 4)):
        for left, right, component in itertools.product(range(size), range(size), range(10)):
            first_component_count += 1
            first_component_defects += form_bilinear_metric_derivative(degree, left, right, (component,)) != form_bilinear_metric_jet(degree, left, right, component)
    symmetry_defects_count = 0
    for degree, size in ((2, 6), (3, 4)):
        for left, right, first, second in itertools.product(range(size), range(size), range(10), range(10)):
            value = form_bilinear_metric_derivative(degree, left, right, (first, second))
            symmetry_defects_count += value != form_bilinear_metric_derivative(degree, left, right, (second, first))
    epsilon, zeta = sp.symbols("epsilon zeta")
    fixtures = ((2, 0, 0, 0, 0), (2, 0, 3, 1, 8), (2, 2, 5, 4, 9), (3, 0, 0, 0, 4), (3, 0, 3, 1, 8), (3, 1, 2, 5, 9))
    direct_defects = 0
    eta = sp.diag(-1, 1, 1, 1)
    for degree, left, right, first, second in fixtures:
        metric = eta + epsilon * sp.Matrix(METRIC_MATRICES[first]) + zeta * sp.Matrix(METRIC_MATRICES[second])
        inverse = metric.inv()
        basis = form_basis(degree)
        direct = sp.S.Zero
        for left_indices in itertools.permutations(basis[left]):
            left_component = _component(left_indices, basis)
            for right_indices in itertools.permutations(basis[right]):
                right_component = _component(right_indices, basis)
                direct += left_component[1] * right_component[1] * sp.prod(inverse[a, b] for a, b in zip(left_indices, right_indices, strict=True))
        direct *= sp.sqrt(-metric.det()) / sp.factorial(degree)
        exact = sp.diff(direct, epsilon, zeta).subs({epsilon: 0, zeta: 0})
        direct_defects += sp.simplify(exact - form_bilinear_metric_derivative(degree, left, right, (first, second))) != 0
    return {
        "q2_cubic_action_regression_key_count": len(action_keys),
        "q2_cubic_action_regression_defect_count": first_defects,
        "first_metric_jet_component_comparison_count": first_component_count,
        "first_metric_jet_component_defect_count": first_component_defects,
        "second_metric_jet_permutation_defect_count": symmetry_defects_count,
        "direct_mixed_second_variation_fixture_count": len(fixtures),
        "direct_mixed_second_variation_defect_count": direct_defects,
        "clock_switch_second_derivative_families": ["h0_double_prime", "h1_double_prime"],
    }


@lru_cache(maxsize=1)
def action_audit() -> dict[str, Any]:
    audit = metric_jet_audit()
    tensor = merged_tensor()
    audit.update({
        "quartic_action_monomial_counts": {name: len(action) for name, action in quartic_action_blocks().items()},
        "graded_symmetry_defect_count": symmetry_defects(tensor),
        "cyclic_output_rows": sorted({key[0] for key in tensor}),
        "cyclicity_scope": "all Euler derivatives of the complete physical-emitter quartic metric/clock-switch action through the canonical signed odd pairing",
    })
    defect_fields = (
        "q2_cubic_action_regression_defect_count",
        "first_metric_jet_component_defect_count",
        "second_metric_jet_permutation_defect_count",
        "direct_mixed_second_variation_defect_count",
        "graded_symmetry_defect_count",
    )
    if any(audit[name] for name in defect_fields):
        raise AssertionError("physical emitter q3 audit failed")
    return audit


def serialize_tensor(tensor: Tensor) -> list[dict[str, Any]]:
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
    blocks = tensor_blocks()
    tensor = merged_tensor()
    outputs = sorted({key[0] for key in tensor})
    chunks = []
    encoded: dict[int, bytes] = {}
    row_hashes = {}
    serialized_total = 0
    for output in outputs:
        row_tensor = {key: value for key, value in tensor.items() if key[0] == output}
        row = serialize_tensor(row_tensor)[0]
        body_hash = canonical_sha256(row)
        document = {**row, "canonical_sha256": body_hash}
        data = gzip_bytes(document)
        encoded[output] = data
        row_hashes[output] = body_hash
        serialized_count = len(row["terms"])
        serialized_total += serialized_count
        chunks.append({
            "output": output,
            "path": str((GENERATED / f"row_{output:03d}.json.gz").relative_to(ROOT)),
            "file_sha256": hashlib.sha256(data).hexdigest(),
            "canonical_sha256": body_hash,
            "operator_key_count": len(row_tensor),
            "serialized_term_count": serialized_count,
            "maximum_total_jet_order": max((sum(term["first_pbw_multiindex"]) + sum(term["second_pbw_multiindex"]) + sum(term["third_pbw_multiindex"]) for term in row["terms"]), default=0),
        })
    payload = {
        "schema": "closed-universe-berger-108-row-emitter-physical-q3-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_EMITTER_PHYSICAL_Q3_PBW_PAYLOAD",
        "shape": [108, 108, 108, 108],
        "coefficient_field": "Q(sqrt(10)) differential switch-jet algebra",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "source_action": "sum_b[-1/2 sqrt(-g)<dK_b,dK_b>_g-m_b_squared/2 sqrt(-g)<K_b,K_b>_g+g_b h_b(Theta) sqrt(-g)<K_b,dA>_g] through quartic order",
        "storage": "deterministic-gzip-strict-json-row-chunks",
        "block_hashes": {name: tensor_digest(block) for name, block in blocks.items()},
        "chunks": chunks,
        "nonzero_output_rows": outputs,
        "operator_key_count": len(tensor),
        "serialized_term_count": serialized_total,
        "canonical_sha256": canonical_sha256(row_hashes),
    }
    return payload, encoded


def payload_document() -> dict[str, Any]:
    return payload_bundle()[0]


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED",
        "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED",
        "emitter_physical_q2": "EMITTER_PHYSICAL_Q2_PBW_EXPORTED",
        "emitter_master": "COVARIANT_108_ROW_Q1_Q2_MASTER_IDENTITY_CERTIFIED",
        "rod_metric_q3": "APPARATUS_ROD_METRIC_Q3_PBW_EXPORTED",
    }
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    audit = action_audit()
    payload = payload or payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_sha256 = payload_sha256 or hashlib.sha256(rendered_payload.encode()).hexdigest()
    tensor = merged_tensor()
    deleted_key = sorted(tensor)[-1]
    output = deleted_key[0]
    original = {key: value for key, value in tensor.items() if key[0] == output}
    mutated = dict(original)
    del mutated[deleted_key]
    mutation = canonical_sha256(serialize_tensor(mutated)) != canonical_sha256(serialize_tensor(original))
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate exports the complete physical-action contribution of both selected massive two-form emitters to q3 on the canonical 108-row Berger carrier. It takes the second metric and clock-switch jet of the same quadratic emitter action whose Hessian and cubic stress/switch jet were previously certified. The general densitized p-form pairing derivative distributes two independent metric variations across the volume density and every inverse-metric slot; all first derivatives regress the certified q2 cubic action exactly, the second jet is permutation symmetric, and direct symbolic mixed variations verify representative two- and three-form components. The quartic source retains the free kinetic and mass metric-square terms, switched Maxwell interaction metric-square and metric-clock terms, and both exact h_b'' clock-switch families. Euler differentiation of that one quartic action through the canonical signed odd pairing supplies every metric-, clock-, Maxwell- and twelve emitter-cotangent row, including noncommuting PBW integration by parts when dK or dA is varied. The resulting trilinear tensor is exactly graded symmetric and a deletion mutation is detected. This certifies physical-emitter q3 only. Rod, memory and normalized-readout q3 are separately certified; base gravity-clock-Maxwell q3 and the scalar-BV/emitter-Diff-BV structural-zero ledger remain to assemble. Complete q3, component arity replay, K_Berger equivariance, observer-morphism stability, detector response on Z2, nonlinear rank, physical Bridge 3, finite-parameter causal propagation and quantum claims remain unavailable. No cross-background mode identification is made."
    )
    return {
        "schema": "closed-universe-berger-108-row-emitter-physical-q3-pbw-v1",
        "result_id": "BERGER_108_ROW_EMITTER_PHYSICAL_Q3_PBW",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_COMPLETE_EMITTER_PHYSICAL_Q3_PBW_SUBBLOCK",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": payload_sha256, "operator_key_count": payload["operator_key_count"], "serialized_term_count": payload["serialized_term_count"], "nonzero_output_rows": payload["nonzero_output_rows"], "canonical_sha256": payload["canonical_sha256"]},
        "second_jet_and_cyclicity_audit": audit,
        "mutation_results": [{"name": "delete_last_emitter_physical_q3_key", "detected": mutation}],
        "activation_disposition": {"emitter_physical_q3_subblock_exported": True, "complete_scalar_q3_exported": False, "structural_q3_zero_ledger_complete": False, "arity_replay_certified": False, "K_Berger_equivariance_certified": False, "observer_morphism_stability_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"EMITTER_PHYSICAL_Q3_PBW_EXPORTED": True, "EMITTER_PHYSICAL_Q3_GRADED_SYMMETRIC": True, "EMITTER_PHYSICAL_Q3_CYCLIC": True, "EMITTER_PHYSICAL_Q3_Q2_REGRESSION_EXACT": True, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "STRUCTURAL_Q3_ZERO_LEDGER_COMPLETE": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "ASSEMBLE_BASE_Q3_AND_STRUCTURAL_ZERO_LEDGER",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload, encoded = payload_bundle()
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
        GENERATED.mkdir(parents=True, exist_ok=True)
        for output, data in encoded.items():
            (GENERATED / f"row_{output:03d}.json.gz").write_bytes(data)
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
    if args.check:
        if not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload or not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise SystemExit("stale emitter physical q3 artifact")
        for output, data in encoded.items():
            path = GENERATED / f"row_{output:03d}.json.gz"
            if not path.exists() or path.read_bytes() != data:
                raise SystemExit(f"stale emitter physical q3 row {output}")
    print("BERGER_108_ROW_EMITTER_PHYSICAL_Q3_PBW generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
