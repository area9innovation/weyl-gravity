#!/usr/bin/env python3
"""Export the physical massive-emitter stress/switch q2 PBW subblock."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.berger_108_row_component_jet_contract import (
    ONE_SCALAR, Polynomial, _multiindex_from_word, _pbw_word,
    _word_from_multiindex, add, derivative, generator, multiply, normalize,
    scalar_mul, scale, serialize,
)
from closed_universe_observers.generate_berger_108_row_emitter_q1_pbw_overlay import (
    _component, emitter_overlay, exterior_derivative, form_basis,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-emitter-physical-q2-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-emitter-physical-q2-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-emitter-physical-q2-pbw.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "emitter_q1": P / "certificates/BERGER_108_ROW_EMITTER_Q1_PBW_OVERLAY.json",
    "emitter_stress": P / "certificates/BERGER_EMITTER_STRESS_CLOCK_BACKREACTION_LEDGER.json",
    "emitter_master": P / "certificates/BERGER_108_ROW_EMITTER_Q1_Q2_MASTER_IDENTITY.json",
}
SOURCE_FILES = [Path(__file__), P / "verify_berger_108_row_emitter_physical_q2_pbw.py", P / "tests/test_berger_108_row_emitter_physical_q2_pbw.py", SCHEMA, PAYLOAD_SCHEMA, REPORT]

Scalar = tuple[Fraction, Fraction]
Factor = tuple[int, tuple[int, ...]]
Action = dict[tuple[Factor, ...], Polynomial]
Operator = dict[tuple[int, int, tuple[int, ...]], Polynomial]
Tensor = dict[tuple[int, int, tuple[int, ...], int, tuple[int, ...]], Polynomial]
ETA = (-1, 1, 1, 1)
METRIC_COMPONENTS = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))
FORM2 = form_basis(2)
FORM3 = form_basis(3)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rational(value: Fraction | int) -> Scalar:
    return Fraction(value), Fraction(0)


def constant(value: Scalar | Fraction | int) -> Polynomial:
    scalar = value if isinstance(value, tuple) else rational(value)
    return {(): scalar} if scalar != (0, 0) else {}


def parameter(name: str) -> Polynomial:
    return {(generator("parameter", name),): ONE_SCALAR}


def profile(name: str, vertical: Iterable[int] = ()) -> Polynomial:
    return {(generator("profile", name, vertical),): ONE_SCALAR}


def product(*values: Polynomial) -> Polynomial:
    result = constant(1)
    for value in values:
        result = multiply(result, value)
    return result


def action_add(action: Action, factors: Iterable[Factor], coefficient: Polynomial) -> None:
    key = tuple(sorted((row, tuple(word)) for row, word in factors))
    action[key] = add(action.get(key, {}), coefficient)
    if not action[key]:
        del action[key]


def inverse_jet(first: int, second: int, component: int) -> Fraction:
    left, right = METRIC_COMPONENTS[component]
    entry = int((first, second) in ((left, right), (right, left)))
    return Fraction(-ETA[first] * ETA[second] * entry)


def density_jet(component: int) -> Fraction:
    first, second = METRIC_COMPONENTS[component]
    return Fraction(ETA[first], 2) if first == second else Fraction(0)


@lru_cache(maxsize=None)
def form_bilinear_base(degree: int, left: int, right: int) -> Fraction:
    basis = form_basis(degree)
    if left != right:
        return Fraction(0)
    return Fraction(math.prod(ETA[axis] for axis in basis[left]))


@lru_cache(maxsize=None)
def form_bilinear_metric_jet(degree: int, left: int, right: int, component: int) -> Fraction:
    """D[sqrt(-g)<e_I,e_J>_g] at eta in the ordered form basis."""
    basis = form_basis(degree)
    total = Fraction(0)
    for left_indices in itertools.permutations(basis[left]):
        left_component = _component(left_indices, basis)
        assert left_component is not None and left_component[0] == left
        for right_indices in itertools.permutations(basis[right]):
            right_component = _component(right_indices, basis)
            assert right_component is not None and right_component[0] == right
            orientation = left_component[1] * right_component[1]
            base = Fraction(1)
            for a, b in zip(left_indices, right_indices, strict=True):
                base *= ETA[a] if a == b else 0
            contribution = density_jet(component) * base
            for slot in range(degree):
                term = inverse_jet(left_indices[slot], right_indices[slot], component)
                for other in range(degree):
                    if other != slot:
                        a, b = left_indices[other], right_indices[other]
                        term *= ETA[a] if a == b else 0
                contribution += term
            total += orientation * contribution
    return total / Fraction(sp.factorial(degree))


def differential_slots(degree: int, row_offset: int) -> list[list[tuple[Factor, Scalar]]]:
    matrix = exterior_derivative(degree)
    target = form_basis(degree + 1)
    slots: list[list[tuple[Factor, Scalar]]] = [[] for _ in target]
    for (output, source), terms in matrix.items():
        for term in terms:
            slots[output].append(((row_offset + source, term.word), term.coefficient))
    return slots


def physical_quadratic_action() -> Action:
    """The exact component action whose Hessian is the certified emitter q1."""
    action: Action = {}
    d_k = differential_slots(2, 0)
    d_a = differential_slots(1, 55)
    for emitter, k_offset in ((0, 84), (1, 90)):
        shifted_dk = [[((k_offset + row, word), coefficient) for (row, word), coefficient in terms] for terms in d_k]
        mass = parameter(f"m{emitter}_squared")
        coupling_switch = product(parameter(f"g{emitter}"), profile(f"h{emitter}"))
        for first in range(4):
            for second in range(4):
                base = form_bilinear_base(3, first, second)
                if base:
                    for left_factor, left_coefficient in shifted_dk[first]:
                        for right_factor, right_coefficient in shifted_dk[second]:
                            action_add(action, (left_factor, right_factor), scale(constant(scalar_mul(left_coefficient, right_coefficient)), rational(-base / 2)))
        for first in range(6):
            for second in range(6):
                base = form_bilinear_base(2, first, second)
                if base:
                    action_add(action, (((k_offset + first), ()), ((k_offset + second), ())), scale(mass, rational(-base / 2)))
                if base:
                    for a_factor, a_coefficient in d_a[second]:
                        action_add(action, (((k_offset + first), ()), a_factor), scale(coupling_switch, scalar_mul(rational(base), a_coefficient)))
    return action


def physical_cubic_action() -> tuple[Action, dict[str, int]]:
    action: Action = {}
    counts: dict[str, int] = defaultdict(int)
    d_k_template = differential_slots(2, 0)
    d_a = differential_slots(1, 55)
    for emitter, k_offset in ((0, 84), (1, 90)):
        d_k = [[((k_offset + row, word), coefficient) for (row, word), coefficient in terms] for terms in d_k_template]
        mass = parameter(f"m{emitter}_squared")
        coupling_switch = product(parameter(f"g{emitter}"), profile(f"h{emitter}"))
        coupling_switch_prime = product(parameter(f"g{emitter}"), profile(f"h{emitter}", (1,)))
        for metric_component in range(10):
            metric_factor = (5 + metric_component, ())
            for first in range(4):
                for second in range(4):
                    jet = form_bilinear_metric_jet(3, first, second, metric_component)
                    if jet:
                        for left_factor, left_coefficient in d_k[first]:
                            for right_factor, right_coefficient in d_k[second]:
                                action_add(action, (metric_factor, left_factor, right_factor), scale(constant(scalar_mul(left_coefficient, right_coefficient)), rational(-jet / 2)))
                                counts["free_kinetic_metric"] += 1
            for first in range(6):
                for second in range(6):
                    jet = form_bilinear_metric_jet(2, first, second, metric_component)
                    if not jet:
                        continue
                    action_add(action, (metric_factor, ((k_offset + first), ()), ((k_offset + second), ())), scale(mass, rational(-jet / 2)))
                    counts["free_mass_metric"] += 1
                    for a_factor, a_coefficient in d_a[second]:
                        action_add(action, (metric_factor, ((k_offset + first), ()), a_factor), scale(coupling_switch, scalar_mul(rational(jet), a_coefficient)))
                        counts["interaction_metric"] += 1
        theta_factor = (16, ())
        for first in range(6):
            for second in range(6):
                base = form_bilinear_base(2, first, second)
                if not base:
                    continue
                for a_factor, a_coefficient in d_a[second]:
                    action_add(action, (theta_factor, ((k_offset + first), ()), a_factor), scale(coupling_switch_prime, scalar_mul(rational(base), a_coefficient)))
                    counts["interaction_clock_switch"] += 1
    return action, dict(sorted(counts.items()))


def dual_and_pairing_sign(row: int) -> tuple[int, int]:
    if 5 <= row <= 16:
        return 27 + row - 5, 1
    if 55 <= row <= 58:
        return 59 + row - 55, -1
    if 84 <= row <= 95:
        return 96 + row - 84, 1
    raise AssertionError(f"unsupported physical emitter action row {row}")


def op_add(operator: Operator, output: int, input_row: int, word: Iterable[int], coefficient: Polynomial) -> None:
    for reduced, word_factor in _pbw_word(tuple(word)):
        key = output, input_row, reduced
        operator[key] = add(operator.get(key, {}), scale(coefficient, word_factor))
        if not operator[key]:
            del operator[key]


def tensor_add(tensor: Tensor, output: int, left: Factor, right: Factor, coefficient: Polynomial) -> None:
    left_row, left_word = left
    right_row, right_word = right
    for reduced_left, left_factor in _pbw_word(left_word):
        for reduced_right, right_factor in _pbw_word(right_word):
            key = output, left_row, reduced_left, right_row, reduced_right
            tensor[key] = add(tensor.get(key, {}), scale(coefficient, scalar_mul(left_factor, right_factor)))
            if not tensor[key]:
                del tensor[key]


def tensor_add_symmetric(tensor: Tensor, output: int, left: Factor, right: Factor, coefficient: Polynomial) -> None:
    # ``coefficient`` is the coefficient of the commutative cubic action
    # monomial.  When the two unvaried slots coincide, its second derivative
    # has multiplicity two.  Suppressing the repeated insertion here emitted
    # half of precisely those diagonal Hessian entries.
    tensor_add(tensor, output, left, right, coefficient)
    tensor_add(tensor, output, right, left, coefficient)


def action_to_unary(action: Action) -> Operator:
    output: Operator = {}
    for factors, coefficient in action.items():
        assert len(factors) == 2
        for position, varied in enumerate(factors):
            remaining = factors[1 - position]
            dual, pairing_sign = dual_and_pairing_sign(varied[0])
            if not varied[1]:
                op_add(output, dual, remaining[0], remaining[1], scale(coefficient, rational(pairing_sign)))
            else:
                axis, = varied[1]
                factor = rational(-pairing_sign)
                op_add(output, dual, remaining[0], remaining[1], scale(derivative(coefficient, axis), factor))
                op_add(output, dual, remaining[0], (axis, *remaining[1]), scale(coefficient, factor))
    return output


def action_to_q2(action: Action) -> Tensor:
    output: Tensor = {}
    for factors, coefficient in action.items():
        assert len(factors) == 3
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = dual_and_pairing_sign(varied[0])
            if not varied[1]:
                tensor_add_symmetric(output, dual, remaining[0], remaining[1], scale(coefficient, rational(pairing_sign)))
            else:
                axis, = varied[1]
                factor = rational(-pairing_sign)
                tensor_add_symmetric(output, dual, remaining[0], remaining[1], scale(derivative(coefficient, axis), factor))
                tensor_add_symmetric(output, dual, (remaining[0][0], (axis, *remaining[0][1])), remaining[1], scale(coefficient, factor))
                tensor_add_symmetric(output, dual, remaining[0], (remaining[1][0], (axis, *remaining[1][1])), scale(coefficient, factor))
    return output


def parse_q1_overlay() -> Operator:
    output: Operator = {}
    for block in emitter_overlay()["blocks"]:
        for entry in block["entries"]:
            for term in entry["terms"]:
                coefficient_json = term["coefficient"]
                scalar = (
                    Fraction(coefficient_json["rational"]["numerator"], coefficient_json["rational"]["denominator"]),
                    Fraction(coefficient_json["sqrt10"]["numerator"], coefficient_json["sqrt10"]["denominator"]),
                )
                factors = [generator(item["kind"], item["name"], item["vertical_multiindex"], item["spacetime_multiindex"]) for item in term["coefficient_factors"]]
                polynomial = normalize([(scalar, factors)])
                word = _word_from_multiindex(tuple(term["input_pbw_multiindex"]))
                op_add(output, entry["output_row"], entry["input_row"], word, polynomial)
    return output


def q1_hessian_recovery_audit() -> dict[str, Any]:
    rebuilt = action_to_unary(physical_quadratic_action())
    expected = parse_q1_overlay()
    keys = set(rebuilt) | set(expected)
    defects = sum(rebuilt.get(key, {}) != expected.get(key, {}) for key in keys)
    return {"rebuilt_operator_key_count": len(rebuilt), "certified_operator_key_count": len(expected), "q1_hessian_recovery_defect_count": defects}


def identical_slot_hessian_audit() -> dict[str, Any]:
    """Detect loss of the multiplicity-two derivative of h K^2."""

    action: Action = {}
    action_add(action, (((5), ()), ((84), ()), ((84), ())), constant(3))
    tensor = action_to_q2(action)
    key = 27, 84, (), 84, ()
    expected = constant(6)
    return {
        "fixture": "3 h_hat_00 K0_01 K0_01",
        "expected_metric_output_coefficient": serialize(expected),
        "actual_metric_output_coefficient": serialize(tensor.get(key, {})),
        "identical_slot_hessian_defect_count": int(tensor.get(key, {}) != expected),
    }


def metric_jet_audit() -> dict[str, Any]:
    epsilon = sp.symbols("epsilon")
    fixtures = [(2, 0, 0, 0), (2, 0, 3, 1), (3, 0, 0, 4), (3, 1, 2, 8)]
    defects = 0
    for degree, left, right, component in fixtures:
        h = sp.zeros(4)
        first, second = METRIC_COMPONENTS[component]
        h[first, second] = h[second, first] = 1
        metric = sp.diag(-1, 1, 1, 1) + epsilon * h
        inverse = metric.inv()
        basis = form_basis(degree)
        direct = sp.S.Zero
        for left_indices in itertools.permutations(basis[left]):
            left_component = _component(left_indices, basis)
            for right_indices in itertools.permutations(basis[right]):
                right_component = _component(right_indices, basis)
                direct += left_component[1] * right_component[1] * sp.prod(inverse[a, b] for a, b in zip(left_indices, right_indices, strict=True))
        direct = sp.sqrt(-metric.det()) * direct / sp.factorial(degree)
        exact = sp.diff(direct, epsilon).subs(epsilon, 0)
        formula = form_bilinear_metric_jet(degree, left, right, component)
        defects += int(sp.simplify(exact - formula) != 0)
    return {"fixture_count": len(fixtures), "metric_bilinear_first_jet_defect_count": defects}


def symmetry_defects(tensor: Tensor) -> int:
    return sum(value != tensor.get((output, right, right_word, left, left_word), {}) for (output, left, left_word, right, right_word), value in tensor.items())


def serialize_tensor(tensor: Tensor) -> list[dict[str, Any]]:
    rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for (output, left, left_word, right, right_word), polynomial in sorted(tensor.items()):
        for term in serialize(polynomial):
            rows[output].append({"left_input_row": left, "left_pbw_multiindex": list(_multiindex_from_word(left_word)), "right_input_row": right, "right_pbw_multiindex": list(_multiindex_from_word(right_word)), "coefficient": term["coefficient"], "coefficient_factors": term["factors"]})
    return [{"output": output, "terms": terms} for output, terms in sorted(rows.items())]


def payload_document() -> dict[str, Any]:
    action, source_counts = physical_cubic_action()
    tensor = action_to_q2(action)
    rows = serialize_tensor(tensor)
    return {
        "schema": "closed-universe-berger-108-row-emitter-physical-q2-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW_PAYLOAD",
        "shape": [108, 108, 108],
        "coefficient_field": "Q(sqrt(10)) differential switch-jet algebra",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "source_action": "sum_b[-1/2<dK_b,dK_b>-m_b_squared/2<K_b,K_b>+g_b h_b(Theta)<K_b,dA>]",
        "source_family_counts": source_counts,
        "action_monomial_count": len(action),
        "rows": rows,
        "nonzero_output_rows": sorted({key[0] for key in tensor}),
        "operator_key_count": len(tensor),
        "serialized_term_count": sum(len(row["terms"]) for row in rows),
        "canonical_sha256": canonical_sha256(rows),
    }


def build(*, payload: dict[str, Any] | None = None, payload_sha256: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {"component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED", "combined_clock_chart": "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED", "emitter_q1": "SCALAR_EMITTER_Q1_PBW_OVERLAY_EXPORTED", "emitter_stress": "EMITTER_STRESS_AND_CLOCK_SWITCH_Q2_BACKREACTION_INCLUDED", "emitter_master": "COVARIANT_108_ROW_Q1_Q2_MASTER_IDENTITY_CERTIFIED"}
    for name, flag in required.items():
        if values[name]["flags"][flag] is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    q1_audit = q1_hessian_recovery_audit()
    multiplicity_audit = identical_slot_hessian_audit()
    metric_audit = metric_jet_audit()
    tensor = action_to_q2(physical_cubic_action()[0])
    symmetry = symmetry_defects(tensor)
    if q1_audit["q1_hessian_recovery_defect_count"] or multiplicity_audit["identical_slot_hessian_defect_count"] or metric_audit["metric_bilinear_first_jet_defect_count"] or symmetry:
        raise AssertionError("emitter physical q2 audit failed")
    payload = payload or payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_sha256 = payload_sha256 or hashlib.sha256(rendered_payload.encode()).hexdigest()
    mutated = list(payload["rows"])
    mutated[-1] = {"output": mutated[-1]["output"], "terms": mutated[-1]["terms"][:-1]}
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate exports the complete physical-action contribution of both selected massive two-form emitters to q2 on the canonical 108-row Berger carrier. The component action is fixed by an exact Hessian recovery: its quadratic free and switched Maxwell--emitter terms reproduce every key of the previously certified scalar emitter q1 overlay with zero defect, including Lorentzian form weights and switch Leibniz jets. Exact first variation of the densitized two- and three-form pairings supplies the free kinetic and mass stress, the switched interaction stress, and the reciprocal clock-switch source. Raising every slot of the same cubic action through the signed odd pairing generates all metric-, clock-, Maxwell- and emitter-cotangent cyclic mates with noncommuting Berger-frame PBW integration by parts and exact graded input symmetry. The action Hessian now retains multiplicity two when the two remaining slots coincide; an independent 3 h_hat_00 K0_01^2 fixture detects the former half-weight diagonal emission. Independent symbolic fixtures verify the metric bilinear first jets, and deleting one payload term changes the canonical hash. This closes the physical emitter stress/switch q2 subblock only. The two-form Diff--BV q2 cotangent orbit remains to be scalarized before complete emitter or complete 108-row q2 can be claimed. Every q3 block, component q1q2 and q2q2+q1q3 replay, K_Berger equivariance, observer-morphism stability, detector response on Z2, nonlinear rank, physical Bridge 3, finite-parameter causal propagation and quantum claims remain unavailable. No compact-product mode is identified with a Berger row."
    )
    return {
        "schema": "closed-universe-berger-108-row-emitter-physical-q2-pbw-v1", "result_id": "BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW", "setting_id": values["component_contract"]["setting_id"], "claim_status": "CERTIFIED_COMPLETE_EMITTER_PHYSICAL_ACTION_Q2_PBW_SUBBLOCK", "atlas_status": "CERTIFIED", "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": payload_sha256, "operator_key_count": payload["operator_key_count"], "serialized_term_count": payload["serialized_term_count"], "nonzero_output_rows": payload["nonzero_output_rows"], "canonical_sha256": payload["canonical_sha256"]},
        "action_and_cyclicity_audit": {"q1_hessian_recovery": q1_audit, "identical_slot_hessian": multiplicity_audit, "metric_first_jet": metric_audit, "graded_symmetry_defect_count": symmetry, "cyclicity_generation": "all physical emitter q2 rows are Euler derivatives of one component action and are raised with the canonical signed odd pairing"},
        "mutation_results": [{"name": "delete_last_emitter_physical_q2_term", "detected": canonical_sha256(mutated) != payload["canonical_sha256"]}],
        "activation_disposition": {"emitter_physical_q2_subblock_exported": True, "emitter_diff_BV_q2_subblock_exported": False, "complete_emitter_q2_exported": False, "complete_scalar_q2_exported": False, "scalar_q3_exported": False, "arity_replay_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"EMITTER_PHYSICAL_Q2_PBW_EXPORTED": True, "EMITTER_PHYSICAL_Q2_GRADED_SYMMETRIC": True, "EMITTER_PHYSICAL_Q2_CYCLIC": True, "EMITTER_Q1_HESSIAN_RECOVERED_EXACTLY": True, "EMITTER_DIFF_BV_Q2_PBW_EXPORTED": False, "COMPLETE_EMITTER_Q2_PBW_EXPORTED": False, "COMPLETE_SCALAR_108_ROW_Q2_EXPORTED": False, "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "EXPORT_TWO_FORM_DIFF_BV_Q2_PBW_BLOCK", "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--emit", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    payload = payload_document(); rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text()); Draft202012Validator.check_schema(payload_schema); Draft202012Validator(payload_schema).validate(payload)
    value = build(payload=payload, payload_sha256=hashlib.sha256(rendered_payload.encode()).hexdigest()); schema = json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit: PAYLOAD.write_text(rendered_payload); CERTIFICATE.write_text(rendered)
    if args.check and (not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload or not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered): raise SystemExit("stale emitter physical q2 artifact")
    print("BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW generation: PASS"); return 0


if __name__ == "__main__": raise SystemExit(main())
