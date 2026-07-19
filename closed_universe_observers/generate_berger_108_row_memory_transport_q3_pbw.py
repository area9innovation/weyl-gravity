#!/usr/bin/env python3
"""Export the exact two-channel memory-transport q3 PBW tensor."""

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
    Polynomial,
    _multiindex_from_word,
    _pbw_word,
    add,
    scalar_mul,
    scale,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_memory_transport_q2_pbw import (
    METRIC_COMPONENTS,
    velocity_first_jet,
)
from d_quotient_classical.backreacted_clock import berger_support_local_q2 as jet_engine


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_MEMORY_TRANSPORT_Q3_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_MEMORY_TRANSPORT_Q3_PBW_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-memory-transport-q3-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-memory-transport-q3-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-memory-transport-q3-pbw.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "apparatus_action": P / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "memory_q1": P / "certificates/BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY.json",
    "memory_q2": P / "certificates/BERGER_108_ROW_MEMORY_TRANSPORT_Q2_PBW.json",
}
SOURCE_FILES = [Path(__file__), P / "verify_berger_108_row_memory_transport_q3_pbw.py", P / "tests/test_berger_108_row_memory_transport_q3_pbw.py", SCHEMA, PAYLOAD_SCHEMA, REPORT]

Slot = tuple[int, tuple[int, ...]]
TensorKey = tuple[int, int, tuple[int, ...], int, tuple[int, ...], int, tuple[int, ...]]
Tensor = dict[TensorKey, Polynomial]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rational(value: Fraction | int) -> tuple[Fraction, Fraction]:
    return Fraction(value), Fraction(0)


def constant(value: Fraction | int) -> Polynomial:
    return {(): rational(value)}


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
    permutations = {
        tuple(slots[index] for index in order)
        for order in itertools.permutations(range(3))
    }
    for permuted in sorted(permutations):
        add_term(tensor, output, permuted, coefficient)  # type: ignore[arg-type]


def component_slot(component: int, word: tuple[int, ...]) -> Slot:
    if 0 <= component < 10:
        return 5 + component, word
    if 10 <= component < 14:
        return 16, (component - 10, *word)
    raise ValueError(f"unexpected clock-flow component {component}")


@lru_cache(maxsize=1)
def velocity_jets() -> tuple[jet_engine.Jet2, ...]:
    metric = jet_engine._metric()
    inverse = jet_engine._inverse_metric(metric)
    density = jet_engine._volume_density_ratio()
    clock = {
        axis: jet_engine.Jet2.field(10 + axis, sp.Rational(3, 4) if axis == 0 else sp.S.Zero)
        for axis in range(4)
    }
    denominator = jet_engine._sum_jets(
        inverse[(first, second)] * clock[first] * clock[second]
        for first, second in itertools.product(range(4), repeat=2)
    )
    return tuple(
        density
        * jet_engine._sum_jets(inverse[(output, axis)] * clock[axis] for axis in range(4))
        / denominator
        for output in range(4)
    )


@lru_cache(maxsize=1)
def velocity_second_jet() -> tuple[tuple[Slot, Slot, int, Fraction], ...]:
    """Canonical unordered geometry pairs in D2 V, with exact coefficients."""
    terms = []
    for velocity, value in enumerate(velocity_jets()):
        for first, first_word, second, second_word, coefficient in value.bilinear.terms:
            left, right = component_slot(first, first_word), component_slot(second, second_word)
            if left > right:
                continue
            coefficient = sp.Rational(coefficient)
            terms.append((left, right, velocity, Fraction(int(coefficient.p), int(coefficient.q))))
    return tuple(terms)


def direct_action_blocks() -> dict[str, Tensor]:
    blocks: dict[str, Tensor] = {}
    for channel in (0, 1):
        p, m = 72 + channel, 70 + channel
        p_output, m_output = 82 + channel, 80 + channel
        forward: Tensor = {}
        memory: Tensor = {}
        geometry: Tensor = {}
        for left, right, velocity, coefficient in velocity_second_jet():
            base = constant(coefficient)
            add_permutations(forward, p_output, (left, right, (m, (velocity,))), base)

            remaining = [(p, ()), left, right]
            for differentiated in range(3):
                slots = list(remaining)
                slots[differentiated] = (slots[differentiated][0], (velocity, *slots[differentiated][1]))
                add_permutations(memory, m_output, tuple(slots), constant(-coefficient))  # type: ignore[arg-type]

            varied_pairs = {(left, right), (right, left)}
            for varied, other in varied_pairs:
                if 5 <= varied[0] <= 14 and not varied[1]:
                    add_permutations(geometry, 27 + varied[0] - 5, ((p, ()), other, (m, (velocity,))), base)
                elif varied[0] == 16 and len(varied[1]) == 1:
                    axis = varied[1][0]
                    rest: tuple[Slot, Slot, Slot] = ((p, ()), other, (m, (velocity,)))
                    for differentiated in range(3):
                        slots = list(rest)
                        slots[differentiated] = (slots[differentiated][0], (axis, *slots[differentiated][1]))
                        add_permutations(geometry, 38, tuple(slots), constant(-coefficient))  # type: ignore[arg-type]
                else:
                    raise AssertionError("memory q3 geometry support changed")
        blocks[f"memory{channel}_p_euler"] = forward
        blocks[f"memory{channel}_m_euler"] = memory
        blocks[f"memory{channel}_geometry_euler"] = geometry
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


def permuted_key(key: TensorKey, order: tuple[int, int, int]) -> TensorKey:
    slots = ((key[1], key[2]), (key[3], key[4]), (key[5], key[6]))
    ordered = tuple(slots[index] for index in order)
    return key[0], ordered[0][0], ordered[0][1], ordered[1][0], ordered[1][1], ordered[2][0], ordered[2][1]


def symmetry_defects(tensor: Tensor) -> int:
    return sum(value != tensor.get(permuted_key(key, order), {}) for key, value in tensor.items() for order in ((1, 0, 2), (0, 2, 1)))


def transpose_predictions(blocks: dict[str, Tensor]) -> tuple[Tensor, Tensor]:
    predicted_memory: Tensor = {}
    predicted_geometry: Tensor = {}
    for channel in (0, 1):
        p, m = 72 + channel, 70 + channel
        p_output, m_output = 82 + channel, 80 + channel
        forward = blocks[f"memory{channel}_p_euler"]
        for key, coefficient in forward.items():
            output, first, first_word, second, second_word, third, third_word = key
            left, right = (first, first_word), (second, second_word)
            if output != p_output or third != m or len(third_word) != 1 or left > right:
                continue
            velocity = third_word[0]
            rest: tuple[Slot, Slot, Slot] = ((p, ()), left, right)
            for differentiated in range(3):
                slots = list(rest)
                slots[differentiated] = (slots[differentiated][0], (velocity, *slots[differentiated][1]))
                add_permutations(predicted_memory, m_output, tuple(slots), scale(coefficient, rational(-1)))  # type: ignore[arg-type]
            for varied, other in {(left, right), (right, left)}:
                remaining: tuple[Slot, Slot, Slot] = ((p, ()), other, (m, (velocity,)))
                if 5 <= varied[0] <= 14 and not varied[1]:
                    add_permutations(predicted_geometry, 27 + varied[0] - 5, remaining, coefficient)
                elif varied[0] == 16 and len(varied[1]) == 1:
                    axis = varied[1][0]
                    for differentiated in range(3):
                        slots = list(remaining)
                        slots[differentiated] = (slots[differentiated][0], (axis, *slots[differentiated][1]))
                        add_permutations(predicted_geometry, 38, tuple(slots), scale(coefficient, rational(-1)))  # type: ignore[arg-type]
    return predicted_memory, predicted_geometry


def difference_count(left: Tensor, right: Tensor) -> int:
    return sum(left.get(key, {}) != right.get(key, {}) for key in set(left) | set(right))


def velocity_audit() -> dict[str, Any]:
    first_terms = []
    for velocity, value in enumerate(velocity_jets()):
        for component, word, coefficient in value.linear.terms:
            row, mapped_word = component_slot(component, word)
            coefficient = sp.Rational(coefficient)
            first_terms.append((row, mapped_word, velocity, Fraction(int(coefficient.p), int(coefficient.q))))
    first_defects = set(first_terms) ^ set(velocity_first_jet())

    second = velocity_second_jet()
    symmetry = 0
    for left, right, velocity, coefficient in second:
        engine_terms = velocity_jets()[velocity].bilinear.terms
        candidates = []
        for first, first_word, second_component, second_word, value in engine_terms:
            if component_slot(first, first_word) == right and component_slot(second_component, second_word) == left:
                candidates.append(Fraction(int(sp.Rational(value).p), int(sp.Rational(value).q)))
        symmetry += candidates != [coefficient]

    fixtures = (
        ((0, 4, 10), (1, 7, 11)),
        ((2, 5, 12), (3, 9, 13)),
    )
    directional_defects = 0
    s, t = sp.symbols("s t")
    eta = sp.diag(-1, 1, 1, 1)
    for left_indices, right_indices in fixtures:
        left = [sp.S.Zero] * 14
        right = [sp.S.Zero] * 14
        for index, value in zip(left_indices, (1, -2, 3)):
            left[index] = sp.Rational(value)
        for index, value in zip(right_indices, (-1, 2, 1)):
            right[index] = sp.Rational(value)
        h_left, h_right = sp.zeros(4), sp.zeros(4)
        for index, (first, second_component) in enumerate(METRIC_COMPONENTS):
            h_left[first, second_component] = h_left[second_component, first] = left[index]
            h_right[first, second_component] = h_right[second_component, first] = right[index]
        q0 = sp.Matrix([sp.Rational(3, 4), 0, 0, 0])
        q_left, q_right = sp.Matrix(left[10:]), sp.Matrix(right[10:])
        metric = eta + s * h_left + t * h_right
        clock = q0 + s * q_left + t * q_right
        inverse = metric.inv()
        direct_vector = sp.sqrt(-metric.det()) * inverse * clock / (clock.T * inverse * clock)[0]
        for velocity in range(4):
            direct = sp.simplify(direct_vector[velocity].diff(s, t).subs({s: 0, t: 0}))
            predicted = sp.S.Zero
            for first, second_slot, component, coefficient in second:
                if component != velocity:
                    continue
                first_index = first[0] - 5 if 5 <= first[0] <= 14 else 10 + first[1][0]
                second_index = second_slot[0] - 5 if 5 <= second_slot[0] <= 14 else 10 + second_slot[1][0]
                coefficient_sp = sp.Rational(coefficient.numerator, coefficient.denominator)
                if first == second_slot:
                    predicted += coefficient_sp * left[first_index] * right[second_index]
                else:
                    predicted += coefficient_sp * (left[first_index] * right[second_index] + left[second_index] * right[first_index])
            directional_defects += sp.simplify(direct - predicted) != 0
    if first_defects or symmetry or directional_defects:
        raise AssertionError("memory clock-flow second jet audit failed")
    return {
        "first_jet_recovery_term_count": len(first_terms),
        "first_jet_recovery_defect_count": len(first_defects),
        "canonical_second_jet_term_count": len(second),
        "second_jet_ordered_term_count": sum(len(value.bilinear.terms) for value in velocity_jets()),
        "second_jet_permutation_defect_count": symmetry,
        "direct_directional_second_variation_component_count": len(fixtures) * 4,
        "direct_directional_second_variation_defect_count": directional_defects,
    }


def action_audit() -> dict[str, Any]:
    audit = velocity_audit()
    blocks = direct_action_blocks()
    memory = merge_blocks({name: block for name, block in blocks.items() if name.endswith("m_euler")})
    geometry = merge_blocks({name: block for name, block in blocks.items() if name.endswith("geometry_euler")})
    predicted_memory, predicted_geometry = transpose_predictions(blocks)
    audit.update({
        "graded_symmetry_defect_count": symmetry_defects(merge_blocks(blocks)),
        "p_to_m_formal_transpose_defect_count": difference_count(memory, predicted_memory),
        "p_to_geometry_formal_transpose_defect_count": difference_count(geometry, predicted_geometry),
        "cyclicity_scope": "complete two-channel quartic memory action tensor with p, m, metric and Theta Euler rows",
    })
    if any(audit[name] for name in ("graded_symmetry_defect_count", "p_to_m_formal_transpose_defect_count", "p_to_geometry_formal_transpose_defect_count")):
        raise AssertionError("memory q3 symmetry or cyclicity failed")
    return audit


def serialize_tensor(tensor: Tensor) -> list[dict[str, Any]]:
    rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for key, polynomial in sorted(tensor.items()):
        output, first, first_word, second, second_word, third, third_word = key
        for term in serialize(polynomial):
            rows[output].append({"first_input_row": first, "first_pbw_multiindex": list(_multiindex_from_word(first_word)), "second_input_row": second, "second_pbw_multiindex": list(_multiindex_from_word(second_word)), "third_input_row": third, "third_pbw_multiindex": list(_multiindex_from_word(third_word)), "coefficient": term["coefficient"], "coefficient_factors": term["factors"]})
    return [{"output": output, "terms": terms} for output, terms in sorted(rows.items())]


@lru_cache(maxsize=1)
def payload_document() -> dict[str, Any]:
    blocks = direct_action_blocks()
    tensor = merge_blocks(blocks)
    serialized = serialize_tensor(tensor)
    return {
        "schema": "closed-universe-berger-108-row-memory-transport-q3-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_MEMORY_TRANSPORT_Q3_PBW_PAYLOAD",
        "shape": [108, 108, 108, 108],
        "coefficient_field": "Q",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "source_action": "sum_a integral p_a V_gTheta^mu e_mu m_a",
        "block_hashes": {name: canonical_sha256(serialize_tensor(block)) for name, block in blocks.items()},
        "rows": serialized,
        "nonzero_output_rows": sorted({key[0] for key in tensor}),
        "operator_key_count": len(tensor),
        "serialized_term_count": sum(len(row["terms"]) for row in serialized),
        "canonical_sha256": canonical_sha256(serialized),
    }


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {"component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED", "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED", "apparatus_action": "APPARATUS_Q3_ACTION_JET_EXPORTED", "memory_q1": "SCALAR_MEMORY_Q1_PBW_OVERLAY_EXPORTED", "memory_q2": "APPARATUS_MEMORY_TRANSPORT_Q2_PBW_EXPORTED"}
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    audit = action_audit()
    payload = payload or payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_sha256 = payload_sha256 or hashlib.sha256(rendered_payload.encode()).hexdigest()
    mutation = canonical_sha256(serialize_tensor(merge_blocks(direct_action_blocks(), delete_last=True))) != payload["canonical_sha256"]
    if not mutation:
        raise AssertionError("memory q3 deletion mutation was not detected")
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate exports the complete profile-free two-channel memory-transport contribution to q3 on the canonical 108-row Berger carrier. The quartic vertex is the second geometry/clock variation of sum_a integral p_a V_gTheta^mu e_mu m_a. A sparse exact jet calculation gives the full Hessian of V over ten metric components and four clock-gradient components, recovers the certified eleven-term first jet exactly, has exact input permutation symmetry and agrees with independent two-parameter directional differentiations. Raising the common quartic action tensor supplies p-, m-, metric- and Theta-cotangent output rows. Every ordered input is PBW reduced; independent formal adjunction from the p Euler rows reproduces the m and geometry rows, including all derivatives distributed over three remaining inputs, and graded symmetry is exact. A deletion mutation changes the canonical payload hash. This certifies memory transport q3 only. The rod metric q3 block is separately certified; base gravity-clock-Maxwell, normalized readout and physical-emitter q3 remain to assemble, and scalar-BV/emitter-Diff-BV structural zeros remain to ledger. Complete q3, q1q2 and q2q2+q1q3 replay, K_Berger equivariance, observer-morphism stability, detector response on Z2, nonlinear rank, physical Bridge 3, finite-parameter causal propagation and quantum claims remain unavailable. No cross-background mode identification is made."
    )
    return {
        "schema": "closed-universe-berger-108-row-memory-transport-q3-pbw-v1", "result_id": "BERGER_108_ROW_MEMORY_TRANSPORT_Q3_PBW", "setting_id": values["component_contract"]["setting_id"], "claim_status": "CERTIFIED_COMPLETE_MEMORY_TRANSPORT_Q3_PBW_SUBBLOCK", "atlas_status": "CERTIFIED", "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": payload_sha256, "operator_key_count": payload["operator_key_count"], "serialized_term_count": payload["serialized_term_count"], "nonzero_output_rows": payload["nonzero_output_rows"], "canonical_sha256": payload["canonical_sha256"]},
        "velocity_and_cyclicity_audit": audit, "mutation_results": [{"name": "delete_last_memory_transport_q3_key", "detected": mutation}],
        "activation_disposition": {"memory_transport_q3_subblock_exported": True, "complete_scalar_q3_exported": False, "arity_replay_certified": False, "K_Berger_equivariance_certified": False, "observer_morphism_stability_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"APPARATUS_MEMORY_TRANSPORT_Q3_PBW_EXPORTED": True, "APPARATUS_MEMORY_TRANSPORT_Q3_GRADED_SYMMETRIC": True, "APPARATUS_MEMORY_TRANSPORT_Q3_CYCLIC": True, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EXPORT_NORMALIZED_READOUT_Q3_PBW_BLOCK", "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    payload = payload_document(); rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text()); Draft202012Validator.check_schema(payload_schema); Draft202012Validator(payload_schema).validate(payload)
    value = build(payload=payload, payload_sha256=hashlib.sha256(rendered_payload.encode()).hexdigest()); schema = json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit: PAYLOAD.write_text(rendered_payload); CERTIFICATE.write_text(rendered)
    if args.check and (not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload or not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered): raise SystemExit("stale memory transport q3 artifact")
    print("BERGER_108_ROW_MEMORY_TRANSPORT_Q3_PBW generation: PASS"); return 0


if __name__ == "__main__": raise SystemExit(main())
