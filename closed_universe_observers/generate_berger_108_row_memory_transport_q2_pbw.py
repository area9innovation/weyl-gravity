#!/usr/bin/env python3
"""Export the exact two-channel memory-transport q2 PBW tensor."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.berger_108_row_component_jet_contract import (
    ONE_SCALAR, Polynomial, _multiindex_from_word, _pbw_word, add, generator,
    scalar_mul, scale, serialize,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_MEMORY_TRANSPORT_Q2_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_MEMORY_TRANSPORT_Q2_PBW_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-memory-transport-q2-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-memory-transport-q2-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-memory-transport-q2-pbw.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "apparatus_action": P / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json",
    "memory_q1": P / "certificates/BERGER_108_ROW_MEMORY_Q1_PBW_OVERLAY.json",
}
SOURCE_FILES = [Path(__file__), P / "verify_berger_108_row_memory_transport_q2_pbw.py", P / "tests/test_berger_108_row_memory_transport_q2_pbw.py", SCHEMA, PAYLOAD_SCHEMA, REPORT]
Tensor = dict[tuple[int, int, tuple[int, ...], int, tuple[int, ...]], Polynomial]
METRIC_COMPONENTS = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rational(value: Fraction | int) -> tuple[Fraction, Fraction]:
    return Fraction(value), Fraction(0)


def constant(value: Fraction | int) -> Polynomial:
    return {(): rational(value)}


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


def velocity_first_jet() -> list[tuple[int, tuple[int, ...], int, Fraction]]:
    """Return (field row, field PBW word, velocity component, coefficient)."""
    terms = []
    for axis in range(4):
        component = METRIC_COMPONENTS.index((axis, axis))
        terms.append((5 + component, (), 0, Fraction(2 * (-1 if axis == 0 else 1), 3)))
    for spatial in range(1, 4):
        component = METRIC_COMPONENTS.index((0, spatial))
        terms.append((5 + component, (), spatial, Fraction(-4, 3)))
    for axis in range(4):
        terms.append((16, (axis,), axis, Fraction(-16, 9)))
    return terms


def symbolic_velocity_audit() -> dict[str, Any]:
    epsilon = sp.symbols("epsilon")
    omega = sp.Rational(3, 4)
    h_symbols = sp.symbols("h0:10")
    theta = sp.symbols("t0:4")
    h = sp.zeros(4)
    for symbol, (first, second) in zip(h_symbols, METRIC_COMPONENTS, strict=True):
        h[first, second] = symbol
        h[second, first] = symbol
    eta = sp.diag(-1, 1, 1, 1)
    g = eta + epsilon * h
    q = sp.Matrix([omega + epsilon * theta[0], *(epsilon * theta[index] for index in range(1, 4))])
    inverse = g.inv()
    vector = sp.sqrt(-g.det()) * inverse * q / ((q.T * inverse * q)[0])
    direct = [sp.expand(sp.diff(vector[index], epsilon).subs(epsilon, 0)) for index in range(4)]
    expected = [sp.S.Zero for _ in range(4)]
    for row, word, component, coefficient in velocity_first_jet():
        if row == 16:
            expected[component] += sp.Rational(coefficient.numerator, coefficient.denominator) * theta[word[0]]
        else:
            expected[component] += sp.Rational(coefficient.numerator, coefficient.denominator) * h_symbols[row - 5]
    defects = sum(sp.simplify(direct[index] - expected[index]) != 0 for index in range(4))
    if defects:
        raise AssertionError("memory velocity first jet failed")
    return {
        "background_velocity": ["4/3", "0", "0", "0"],
        "direct_symbolic_component_count": 4,
        "direct_symbolic_defect_count": defects,
        "first_jet_term_count": len(velocity_first_jet()),
        "formula": "delta V0=(2/3)tr_eta(h)-(16/9)e0(theta); delta Vi=-(4/3)h0i-(16/9)ei(theta)",
    }


def transpose_m_input(output_tensor: Tensor, channel: int) -> Tensor:
    result: Tensor = {}
    p_output, m, p = 82 + channel, 70 + channel, 72 + channel
    for (output, left, left_word, right, right_word), coefficient in output_tensor.items():
        if output != p_output or right != m or len(right_word) != 1:
            continue
        axis = right_word[0]
        negative = scale(coefficient, rational(-1))
        add_symmetric(result, 80 + channel, p, (axis,), left, left_word, negative)
        add_symmetric(result, 80 + channel, p, (), left, (axis, *left_word), negative)
    return result


def transpose_x_input(output_tensor: Tensor, channel: int) -> Tensor:
    result: Tensor = {}
    p_output, m, p = 82 + channel, 70 + channel, 72 + channel
    for (output, left, left_word, right, right_word), coefficient in output_tensor.items():
        if output != p_output or right != m:
            continue
        if 5 <= left <= 14 and not left_word:
            add_symmetric(result, 27 + left - 5, p, (), m, right_word, coefficient)
        elif left == 16 and len(left_word) == 1:
            axis = left_word[0]
            negative = scale(coefficient, rational(-1))
            add_symmetric(result, 38, p, (axis,), m, right_word, negative)
            add_symmetric(result, 38, p, (), m, (axis, *right_word), negative)
        else:
            raise AssertionError("memory velocity support changed")
    return result


def action_blocks() -> dict[str, Tensor]:
    blocks: dict[str, Tensor] = {}
    for channel in (0, 1):
        p_output, m = 82 + channel, 70 + channel
        forward: Tensor = {}
        for field, field_word, velocity, coefficient in velocity_first_jet():
            add_symmetric(forward, p_output, field, field_word, m, (velocity,), constant(coefficient))
        blocks[f"memory{channel}_p_euler"] = forward
        blocks[f"memory{channel}_m_euler"] = transpose_m_input(forward, channel)
        blocks[f"memory{channel}_geometry_euler"] = transpose_x_input(forward, channel)
    return blocks


def merge_blocks(blocks: dict[str, Tensor], *, delete_last: bool = False) -> Tensor:
    result: Tensor = {}
    for block in blocks.values():
        for key, value in block.items():
            result[key] = add(result.get(key, {}), value)
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


def payload_document() -> dict[str, Any]:
    blocks = action_blocks()
    tensor = merge_blocks(blocks)
    serialized = serialize_tensor(tensor)
    return {
        "schema": "closed-universe-berger-108-row-memory-transport-q2-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_MEMORY_TRANSPORT_Q2_PBW_PAYLOAD",
        "shape": [108, 108, 108],
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
    required = {"component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED", "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED", "apparatus_action": "APPARATUS_Q2_ACTION_JET_EXPORTED", "memory_q1": "SCALAR_MEMORY_Q1_PBW_OVERLAY_EXPORTED"}
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    audit = symbolic_velocity_audit()
    tensor = merge_blocks(action_blocks())
    audit["graded_symmetry_defect_count"] = symmetry_defects(tensor)
    audit["cyclicity_generation"] = "m, metric and Theta Euler rows are exact formal-adjoint cyclic mates of the p Euler row in the frozen signed pairing"
    if audit["graded_symmetry_defect_count"]:
        raise AssertionError("memory q2 symmetry failed")
    payload = payload or payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_sha256 = payload_sha256 or hashlib.sha256(rendered_payload.encode()).hexdigest()
    mutation = canonical_sha256(serialize_tensor(merge_blocks(action_blocks(), delete_last=True))) != payload["canonical_sha256"]
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate exports the complete profile-free two-channel memory-transport contribution to q2 on the canonical 108-row Berger carrier. The exact clock-flow vector density is V^mu=sqrt(-gHat) gHat^{mu nu}Theta_nu/gHat^{-1}(dTheta,dTheta). Direct symbolic differentiation at the positive-clock Berger background gives delta V0=(2/3)tr_eta(h)-(16/9)e0(theta) and delta Vi=-(4/3)h0i-(16/9)ei(theta), with zero defects in all four components. Inserting that eleven-term first jet into sum_a integral p_a V^mu e_mu m_a and raising the symmetric cubic action derivative supplies both channels' p-, m-, metric- and Theta-cotangent Euler rows. Every differentiated input is PBW-reduced in the noncommuting Berger frame; the m and geometry rows are generated by exact integration by parts from the same lowered vertex, and graded input symmetry is exact. A deletion mutation changes the canonical payload hash. This certifies memory transport q2 only. The normalized detector readout and emitter q2 sectors, every q3 block, the complete q1q2 and q2q2+q1q3 identities, K_Berger equivariance, observer-morphism stability, detector response on Z2, nonlinear rank, physical Bridge 3, finite-parameter causal propagation and quantum claims remain unavailable. No compact-product mode is identified with a Berger row."
    )
    return {
        "schema": "closed-universe-berger-108-row-memory-transport-q2-pbw-v1", "result_id": "BERGER_108_ROW_MEMORY_TRANSPORT_Q2_PBW", "setting_id": values["component_contract"]["setting_id"], "claim_status": "CERTIFIED_COMPLETE_MEMORY_TRANSPORT_Q2_PBW_SUBBLOCK", "atlas_status": "CERTIFIED", "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": payload_sha256, "operator_key_count": payload["operator_key_count"], "serialized_term_count": payload["serialized_term_count"], "nonzero_output_rows": payload["nonzero_output_rows"], "canonical_sha256": payload["canonical_sha256"]},
        "velocity_and_cyclicity_audit": audit, "mutation_results": [{"name": "delete_last_memory_transport_q2_key", "detected": mutation}],
        "activation_disposition": {"memory_transport_q2_subblock_exported": True, "complete_apparatus_q2_exported": False, "complete_emitter_q2_exported": False, "scalar_q3_exported": False, "arity_replay_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"APPARATUS_MEMORY_TRANSPORT_Q2_PBW_EXPORTED": True, "APPARATUS_MEMORY_TRANSPORT_Q2_GRADED_SYMMETRIC": True, "APPARATUS_MEMORY_TRANSPORT_Q2_CYCLIC": True, "COMPLETE_SCALAR_108_ROW_Q2_EXPORTED": False, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EXPORT_NORMALIZED_READOUT_Q2_PBW_BLOCK", "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    payload = payload_document(); rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text()); Draft202012Validator.check_schema(payload_schema); Draft202012Validator(payload_schema).validate(payload)
    value = build(payload=payload, payload_sha256=hashlib.sha256(rendered_payload.encode()).hexdigest()); schema = json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit: PAYLOAD.write_text(rendered_payload); CERTIFICATE.write_text(rendered)
    if args.check and (not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload or not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered): raise SystemExit("stale memory transport q2 artifact")
    print("BERGER_108_ROW_MEMORY_TRANSPORT_Q2_PBW generation: PASS"); return 0


if __name__ == "__main__": raise SystemExit(main())
