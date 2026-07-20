#!/usr/bin/env python3
"""Independently verify the Berger quartic-moduli arity-three obstruction."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import serialize
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    action_add,
    scale,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    extension_q1,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
)
from closed_universe_observers.generate_berger_order_three_common_action_promotion_gate import (
    DEPENDENCIES as TERMINAL_DEPENDENCIES,
    old_constant_action,
)
from closed_universe_observers.generate_berger_quartic_completion_moduli_observer_invariance import (
    CERTIFICATE,
    DEPENDENCIES,
    OLD_Q2,
    PACKAGE,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
    TERMINAL,
    TERMINAL_PAYLOAD,
)
from closed_universe_observers.generate_berger_ward_cokernel_irrep_closure_obstruction import (
    parse_scalar,
)
from closed_universe_observers.verify_berger_order_three_common_action_promotion_gate import (
    _action,
    _q2,
)


def _canonical_sha256(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _repair_q2():
    terminal = json.loads(TERMINAL.read_text())
    terminal_payload = json.loads(TERMINAL_PAYLOAD.read_text())
    higher = json.loads(TERMINAL_DEPENDENCIES["higher_payload"].read_text())
    minimal = json.loads(TERMINAL_DEPENDENCIES["minimal_payload"].read_text())
    actions = {
        "old_constant.emitter_0": old_constant_action(0),
        "old_constant.emitter_1": old_constant_action(1),
        "epsilon.emitter_0": _action(
            minimal["local_action_entries"]["emitter_0"]
        ),
        "epsilon.emitter_1": _action(
            minimal["local_action_entries"]["emitter_1"]
        ),
    }
    actions.update(
        {
            module_id: _action(module["action_entries"])
            for module_id, module in higher["modules"].items()
            if not module_id.startswith("temporal_lower.")
        }
    )
    actions.update(
        {
            module_id: _action(module["action_entries"])
            for module_id, module in terminal_payload["modules"].items()
        }
    )
    result = {}
    for selected in terminal["exact_action_image"]["repair_modules"]:
        scalar = parse_scalar(selected["coefficient"])
        for factors, polynomial in actions[selected["module_id"]].items():
            action_add(result, factors, scale(polynomial, scalar))
    return _q2(result)


def _add2(tensor, key, coefficient):
    value = replay.add(tensor.get(key, {}), coefficient)
    if value:
        tensor[key] = value
    elif key in tensor:
        del tensor[key]


def _add3(tensor, key, coefficient):
    value = replay.add(tensor.get(key, {}), coefficient)
    if value:
        tensor[key] = value
    elif key in tensor:
        del tensor[key]


def _old_relevant(repair):
    outputs = {key[0] for key in repair}
    inputs = {row for key in repair for row in (key[1], key[3])}
    document = json.loads(OLD_Q2.read_text())
    result = {}
    for row in document["rows"]:
        for term in row["terms"]:
            left = term["left_input_row"]
            right = term["right_input_row"]
            if row["output"] not in inputs and left not in outputs and right not in outputs:
                continue
            key = (
                row["output"],
                left,
                replay.word(term["left_pbw_multiindex"]),
                right,
                replay.word(term["right_pbw_multiindex"]),
            )
            _add2(result, key, replay.polynomial(term))
    return result


def _compose(outer, inner):
    parity = arity.parities() + (0, 1)
    indexed = defaultdict(list)
    for key, coefficient in inner.items():
        indexed[key[0]].append((key, coefficient))
    result = {}
    for outer_key, outer_coefficient in outer.items():
        output, left, left_word, right, right_word = outer_key
        for inner_key, inner_coefficient in indexed.get(left, ()):
            _, first, first_word, second, second_word = inner_key
            for words, value in arity.apply_output_word(
                left_word, inner_coefficient, first_word, second_word
            ).items():
                _add3(
                    result,
                    (output, first, words[0], second, words[1], right, right_word),
                    replay.multiply(outer_coefficient, value),
                )
        sign = (Fraction(-1), Fraction(0)) if parity[left] else replay.ONE_SCALAR
        for inner_key, inner_coefficient in indexed.get(right, ()):
            _, first, first_word, second, second_word = inner_key
            for words, value in arity.apply_output_word(
                right_word, inner_coefficient, first_word, second_word
            ).items():
                _add3(
                    result,
                    (output, left, left_word, first, words[0], second, words[1]),
                    replay.scale(replay.multiply(outer_coefficient, value), sign),
                )
    return result


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


def _manifest(tensor):
    entries = _entries(tensor)
    return {
        "operator_key_count": len(entries),
        "serialized_term_count": sum(len(entry["coefficient"]) for entry in entries),
        "canonical_sha256": _canonical_sha256(entries),
        "nonzero_output_rows": sorted({entry["output"] for entry in entries}),
    }


def _q3_projection_rank():
    source = json.loads(
        (
            PACKAGE
            / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE_PAYLOAD.json"
        ).read_text()
    )
    columns = []
    outputs = set()
    for module in source["modules"].values():
        vector = {}
        for entry in module["q3_entries"]:
            outputs.add(entry["output"])
            if entry["output"] != 109:
                continue
            key = tuple(
                [entry["output"]]
                + [
                    item
                    for row, word in entry["inputs"]
                    for item in (row, tuple(word))
                ]
            )
            for polynomial_entry in entry["coefficient"]:
                factors = tuple(
                    (
                        factor["kind"],
                        factor["name"],
                        tuple(factor["vertical_multiindex"]),
                        tuple(factor["spacetime_multiindex"]),
                    )
                    for factor in polynomial_entry["factors"]
                )
                coefficient = parse_scalar(
                    [
                        [
                            polynomial_entry["coefficient"]["rational"]["numerator"],
                            polynomial_entry["coefficient"]["rational"]["denominator"],
                        ],
                        [
                            polynomial_entry["coefficient"]["sqrt10"]["numerator"],
                            polynomial_entry["coefficient"]["sqrt10"]["denominator"],
                        ],
                    ]
                )
                vector[(key, factors)] = coefficient
        columns.append(vector)
    return len(_echelon(columns)[0]), outputs


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

    repair = _repair_q2()
    assert len(repair) == 636
    old = _old_relevant(repair)
    assert len(old) == 1140
    cross = _compose(old, repair)
    reverse = _compose(repair, old)
    for key, coefficient in reverse.items():
        _add3(cross, key, coefficient)
    assert _manifest(cross) == payload["old_repair_cross_defect_manifest"]

    monomial = (
        ("parameter", "g0", (), (0, 0, 0, 0)),
        ("profile", "h0", (), (0, 0, 0, 0)),
    )
    witness = ((49, 55, (0, 0, 2), CHI, (), 87, ()), monomial)
    flattened = {
        (key, factor): coefficient
        for key, polynomial in cross.items()
        for factor, coefficient in polynomial.items()
    }
    assert flattened[witness] == (Fraction(-4), Fraction(0))
    assert repair[(97, 55, (0, 2), CHI, ())][monomial] == (
        Fraction(2),
        Fraction(0),
    )

    rank, q3_outputs = _q3_projection_rank()
    assert rank == 12
    q1 = {
        key
        for operator in arity.completed_q1().values()
        for key in operator
    } | set(extension_q1(temporal_order=0))
    assert 49 not in q3_outputs
    assert not any(output == 49 and input_row in q3_outputs for output, input_row, _ in q1)
    assert value["full_arity_three_gate"]["admissible_subvariety"] == "EMPTY"
    assert value["full_arity_three_gate"]["witness_polynomial"] == "-4*g0*h0 + sum_i lambda_i*0"
    assert value["K_Berger_and_observer_disposition"][
        "same_action_apparatus_memory_detector_map"
    ].startswith("NO_CERTIFIED_MAP")
    print("BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
