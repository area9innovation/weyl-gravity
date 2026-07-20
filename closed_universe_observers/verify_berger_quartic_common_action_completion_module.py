#!/usr/bin/env python3
"""Independently verify the minimal Berger quartic completion module."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import serialize
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    _dual_and_sign,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    _sympy_scalar,
    invariant_action_basis,
    local_action,
)
from closed_universe_observers.generate_berger_order_three_common_action_promotion_gate import (
    maxwell_gauge_variation,
)
from closed_universe_observers.generate_berger_quartic_common_action_completion_module import (
    CERTIFICATE,
    DEPENDENCIES,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
)
from closed_universe_observers.verify_berger_order_three_common_action_promotion_gate import (
    _action,
)


def _add(tensor, output, slots, coefficient):
    for order in itertools.permutations(range(3)):
        values = tuple(slots[index] for index in order)
        key = (
            output,
            values[0][0], values[0][1],
            values[1][0], values[1][1],
            values[2][0], values[2][1],
        )
        tensor[key] = replay.add(tensor.get(key, {}), coefficient)
        if not tensor[key]:
            del tensor[key]


def _apply(word, coefficient, words):
    states = {words: coefficient}
    for axis in reversed(word):
        updated = {}
        for current, current_coefficient in states.items():
            derivative = replay.derivative(current_coefficient, axis)
            if derivative:
                updated[current] = replay.add(updated.get(current, {}), derivative)
            for slot in range(3):
                for reduced, structure in replay._pbw_word((axis, *current[slot])):
                    changed = list(current)
                    changed[slot] = reduced
                    key = tuple(changed)
                    term = replay.scale(current_coefficient, structure)
                    updated[key] = replay.add(updated.get(key, {}), term)
        states = {key: value for key, value in updated.items() if value}
    return states


def _q3(action):
    output = {}
    for factors, coefficient in action.items():
        assert len(factors) == 4
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = _dual_and_sign(varied[0])
            if not varied[1]:
                _add(
                    output,
                    dual,
                    tuple(remaining),
                    replay.scale(coefficient, (Fraction(pairing_sign), Fraction(0))),
                )
                continue
            sign = pairing_sign * (-1) ** len(varied[1])
            for words, expanded in _apply(
                tuple(reversed(varied[1])),
                coefficient,
                tuple(word for _, word in remaining),
            ).items():
                slots = tuple(
                    (remaining[index][0], words[index]) for index in range(3)
                )
                _add(
                    output,
                    dual,
                    slots,
                    replay.scale(expanded, (Fraction(sign), Fraction(0))),
                )
    return output


def _entries(tensor):
    return [
        {
            "output": key[0],
            "inputs": [
                [key[1], list(key[2])],
                [key[3], list(key[4])],
                [key[5], list(key[6])],
            ],
            "coefficient": serialize(coefficient),
        }
        for key, coefficient in sorted(tensor.items())
    ]


def _digest(entries):
    return hashlib.sha256(
        json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _tensor_vector(tensor):
    return {
        (key, monomial): coefficient
        for key, polynomial in tensor.items()
        for monomial, coefficient in polynomial.items()
    }


def _maxwell_rank(emitter):
    invariant, _ = invariant_action_basis(emitter, 1)
    base = 84 + 6 * emitter
    k_has_two = {
        base: False,
        base + 1: True,
        base + 2: False,
        base + 3: True,
        base + 4: False,
        base + 5: True,
    }
    parities = []
    for _, terms in invariant:
        values = {
            (int(k_has_two[krow]) + int(arow == 57) + word.count(2)) % 2
            for krow, arow, word, _ in terms
        }
        assert len(values) == 1
        parities.append(values.pop())
    actions = [local_action(emitter, terms, profile_jet=0) for _, terms in invariant]
    vectors = [maxwell_gauge_variation(action) for action in actions]
    coordinates = sorted(set().union(*(set(vector) for vector in vectors)))
    matrix = sp.zeros(len(coordinates), len(vectors))
    index = {coordinate: row for row, coordinate in enumerate(coordinates)}
    for column, vector in enumerate(vectors):
        for coordinate, coefficient in vector.items():
            matrix[index[coordinate], column] = _sympy_scalar(coefficient)
    reflection = {"reflection_even": 0, "reflection_odd": 0}
    for vector in matrix.nullspace():
        values = {parities[index] for index, coefficient in enumerate(vector) if coefficient}
        assert len(values) == 1
        reflection["reflection_odd" if values.pop() else "reflection_even"] += 1
    return matrix.rank(), len(matrix.nullspace()), reflection


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for path, schema_path in ((CERTIFICATE, SCHEMA), (PAYLOAD, PAYLOAD_SCHEMA)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(json.loads(path.read_text()))
    assert hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == value["payload_ref"]["sha256"]
    for name, reference in value["dependency_refs"].items():
        path = ROOT / reference["path"]
        assert path == DEPENDENCIES[name]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]

    expected_reflection = {"reflection_even": 3, "reflection_odd": 3}
    assert _maxwell_rank(0) == (22, 6, expected_reflection)
    assert _maxwell_rank(1) == (22, 6, expected_reflection)
    tensors = []
    for module in payload["modules"].values():
        action = _action(module["action_entries"])
        assert all(
            sum(field == 108 and word == () for field, word in factors) == 2
            for factors in action
        )
        assert not maxwell_gauge_variation(action)
        tensor = _q3(action)
        entries = _entries(tensor)
        assert len(entries) == module["q3_manifest"]["key_count"]
        assert _digest(entries) == module["q3_manifest"]["canonical_sha256"]
        assert entries == module["q3_entries"]
        tensors.append(tensor)
    assert len(tensors) == 12
    assert len(_echelon([_tensor_vector(tensor) for tensor in tensors])[0]) == 12

    operation = value["action_derived_operations"]
    assert operation["q1_variation_at_zero_auxiliary_background"] == 0
    assert operation["q2_variation_at_zero_auxiliary_background"] == 0
    assert operation["q3_module_rank"] == 12
    obstruction = value["coefficient_selection_obstruction"]
    assert obstruction["dimension"] == 12
    assert obstruction["q1_q2_constraints_on_parameters"] == 0
    assert not obstruction["unique_q3_selected"]
    assert all(
        row["Maxwell_kernel_reflection_dimensions"] == expected_reflection
        for row in value["module_classification"]
    )
    assert len(value["assumption_ledger"]) == 4
    assert all(row["status"] == "NO_CERTIFIED_MAP" for row in value["missing_object_ledger"])
    assert not value["activation_disposition"]["full_arity_three_replay_authorized"]
    print("BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
