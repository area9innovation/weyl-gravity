#!/usr/bin/env python3
"""Independently replay the Berger order-three common-action gate."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers.berger_108_row_component_jet_contract import (
    _pbw_word,
    generator,
    normalize,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    action_add,
    rational,
    scale,
    tensor_add_symmetric,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    _dual_and_sign,
    extension_q1,
    interaction_action,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    ACTION_COLUMN_ORDER,
    _echelon,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    _load_old_vectors,
)
from closed_universe_observers.generate_berger_order_three_common_action_promotion_gate import (
    CERTIFICATE,
    DEPENDENCIES,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
)
from closed_universe_observers.generate_berger_ward_cokernel_irrep_closure_obstruction import (
    parse_coordinate,
    parse_scalar,
)


ZERO = (Fraction(0), Fraction(0))


def _fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def _polynomial(entries):
    terms = []
    for entry in entries:
        coefficient = entry["coefficient"]
        scalar = (
            _fraction(coefficient["rational"]),
            _fraction(coefficient["sqrt10"]),
        )
        factors = tuple(
            generator(
                factor["kind"],
                factor["name"],
                factor["vertical_multiindex"],
                factor["spacetime_multiindex"],
            )
            for factor in entry["factors"]
        )
        terms.append((scalar, factors))
    return normalize(terms)


def _action(entries):
    return {
        tuple((row, tuple(word)) for row, word in entry["factors"]):
        _polynomial(entry["coefficient"])
        for entry in entries
    }


def _scalar_mul(left, right):
    return (
        left[0] * right[0] + 10 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _q2(action):
    output = {}
    for factors, coefficient in action.items():
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = _dual_and_sign(varied[0])
            word = varied[1]
            if not word:
                tensor_add_symmetric(
                    output,
                    dual,
                    remaining[0],
                    remaining[1],
                    scale(coefficient, rational(pairing_sign)),
                )
                continue
            sign = pairing_sign * (-1) ** len(word)
            expansion = arity.apply_output_word(
                tuple(reversed(word)),
                coefficient,
                remaining[0][1],
                remaining[1][1],
            )
            for (left_word, right_word), expanded in expansion.items():
                tensor_add_symmetric(
                    output,
                    dual,
                    (remaining[0][0], left_word),
                    (remaining[1][0], right_word),
                    scale(expanded, rational(sign)),
                )
    return output


def _q2_manifest(tensor):
    entries = [
        {
            "output": output,
            "left": [left, list(left_word)],
            "right": [right, list(right_word)],
            "coefficient": serialize(coefficient),
        }
        for (output, left, left_word, right, right_word), coefficient in sorted(
            tensor.items()
        )
    ]
    digest = hashlib.sha256(
        json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {"key_count": len(entries), "canonical_sha256": digest}


def _ward(action):
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in _q2(action).items():
        arity.add_bilinear_term(
            q2[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    row = arity.arity_two_row(
        52,
        (0, 0),
        {(0, 0): extension_q1(temporal_order=0)},
        q2,
        arity.parities() + (0, 1),
    )
    specialized = arity.specialize_bilinear_rows({52: row})[52]
    return {
        (key, monomial): coefficient
        for key, polynomial in specialized.items()
        if (key[0] in range(55, 59) and key[2] in range(84, 96))
        or (key[2] in range(55, 59) and key[0] in range(84, 96))
        for monomial, coefficient in polynomial.items()
    }


def _word_variation(word):
    output = {}
    for position, axis in enumerate(word):
        replacements = ((2, 1),) if axis == 1 else ((1, -1),) if axis == 2 else ()
        for target, integer in replacements:
            changed = word[:position] + (target,) + word[position + 1 :]
            for reduced, coefficient in _pbw_word(changed):
                value = (integer * coefficient[0], integer * coefficient[1])
                old = output.get(reduced, ZERO)
                output[reduced] = (old[0] + value[0], old[1] + value[1])
    return {key: value for key, value in output.items() if value != ZERO}


def _action_vector(action):
    return {
        (factors, monomial): coefficient
        for factors, polynomial in action.items()
        for monomial, coefficient in polynomial.items()
    }


def _action_variation(action):
    rotations = {
        84: ((85, 1),), 85: ((84, -1),), 86: (), 87: (),
        88: ((89, 1),), 89: ((88, -1),),
        90: ((91, 1),), 91: ((90, -1),), 92: (), 93: (),
        94: ((95, 1),), 95: ((94, -1),),
        55: (), 56: ((57, 1),), 57: ((56, -1),), 58: (),
    }
    output = {}
    for factors, polynomial in action.items():
        for factor_position, (row, word) in enumerate(factors):
            for target, integer in rotations.get(row, ()):
                changed = list(factors)
                changed[factor_position] = (target, word)
                for monomial, coefficient in polynomial.items():
                    key = (tuple(changed), monomial)
                    value = (integer * coefficient[0], integer * coefficient[1])
                    old = output.get(key, ZERO)
                    output[key] = (old[0] + value[0], old[1] + value[1])
            for changed_word, word_coefficient in _word_variation(word).items():
                changed = list(factors)
                changed[factor_position] = (row, changed_word)
                for monomial, coefficient in polynomial.items():
                    key = (tuple(changed), monomial)
                    value = _scalar_mul(word_coefficient, coefficient)
                    old = output.get(key, ZERO)
                    output[key] = (old[0] + value[0], old[1] + value[1])
    return {key: value for key, value in output.items() if value != ZERO}


def _analytic_weight_zero_dimension():
    derivative_weights = (-1, 0, 0, 1)
    k_weights = (-1, -1, 0, 0, 1, 1)
    a_weights = (-1, 0, 0, 1)

    def symmetric_weights(order):
        result = Counter()
        for monomial in itertools.combinations_with_replacement(range(4), order):
            result[sum(derivative_weights[index] for index in monomial)] += 1
        return result

    by_order = []
    for total in range(4):
        count = 0
        for k_order in range(total + 1):
            for k_word_weight, k_count in symmetric_weights(k_order).items():
                for a_word_weight, a_count in symmetric_weights(total - k_order).items():
                    for k_weight in k_weights:
                        for a_weight in a_weights:
                            if k_weight + a_weight + k_word_weight + a_word_weight == 0:
                                count += k_count * a_count
        by_order.append(count)
    return by_order


def _old_action(emitter):
    output = {}
    name = f"g{emitter}"
    for factors, coefficient in interaction_action().items():
        names = {
            factor[1]
            for monomial in coefficient
            for factor in monomial
            if factor[0] == "parameter"
        }
        if name in names:
            action_add(output, ((CHI, ()),) + factors, coefficient)
    return output


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for path, schema_path in ((CERTIFICATE, SCHEMA), (PAYLOAD, PAYLOAD_SCHEMA)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(json.loads(path.read_text()))
    assert hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == value["payload_ref"]["sha256"]
    dependencies = {}
    for name, reference in value["dependency_refs"].items():
        path = ROOT / reference["path"]
        assert path == DEPENDENCIES[name]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]
        dependencies[name] = json.loads(path.read_text())

    assert _analytic_weight_zero_dimension() == [8, 56, 220, 648]
    classification = payload["classification"]
    assert classification["invariant_dimension_per_emitter"] == 932
    assert classification["reflection_dimensions_per_emitter"] == {
        "reflection_even": 466,
        "reflection_odd": 466,
    }
    modules = payload["modules"]
    assert len(modules) == 1864
    for emitter in (0, 1):
        actions = [
            _action(module["action_entries"])
            for module_id, module in modules.items()
            if module_id.startswith(f"order_three.emitter_{emitter}.")
        ]
        assert len(actions) == 932
        assert not any(_action_variation(action) for action in actions)
        assert len(_echelon([_action_vector(action) for action in actions])[0]) == 932
    for module in modules.values():
        action = _action(module["action_entries"])
        assert _q2_manifest(_q2(action)) == module["q2_manifest"]

    higher_modules = dependencies["higher_payload"]["modules"]
    minimal = dependencies["minimal_payload"]
    action_map = {
        "old_constant.emitter_0": _old_action(0),
        "old_constant.emitter_1": _old_action(1),
        "epsilon.emitter_0": _action(minimal["local_action_entries"]["emitter_0"]),
        "epsilon.emitter_1": _action(minimal["local_action_entries"]["emitter_1"]),
        **{
            module_id: _action(module["action_entries"])
            for module_id, module in higher_modules.items()
        },
        **{
            module_id: _action(module["action_entries"])
            for module_id, module in modules.items()
        },
    }
    repair = {}
    for entry in value["exact_action_image"]["repair_modules"]:
        coefficient = parse_scalar(entry["coefficient"])
        for factors, polynomial in action_map[entry["module_id"]].items():
            action_add(repair, factors, scale(polynomial, coefficient))
    assert len(value["exact_action_image"]["repair_modules"]) == 36
    assert _q2_manifest(_q2(repair)) == value["exact_action_image"]["repair_q2_manifest"]

    closure = [
        parse_coordinate(item)
        for item in dependencies["representation_payload"]["closure_coordinate_basis"]
    ]
    _, old_vectors = _load_old_vectors(dependencies["obstruction_payload"])
    minimal_vectors = {
        name: {closure[index]: parse_scalar(scalar) for index, scalar in entries}
        for name, entries in minimal["ward_vectors_on_900_coordinate_closure"].items()
    }
    assert _ward(repair) == minimal_vectors["typed_maxwell_source"]
    assert value["exact_action_image"]["typed_source_in_image"]
    assert value["decisive_quotient"]["complete_through_order_three_projected_rank"] == 592
    assert value["decisive_quotient"]["source_augmented_projected_rank"] == 592
    q3_gate = value["conditional_same_action_q3_gate"]
    assert q3_gate["repair_q2_self_composition"] == "ZERO_STRUCTURAL"
    assert q3_gate["selected_repair_maxwell_gauge_defect_count"] == 0
    ambiguity = q3_gate["quartic_completion_nonuniqueness"]
    assert ambiguity["same_certified_q1_q2"] and ambiguity["different_q3"]
    assert ambiguity["completion_lambda"]["q3_witness"]["coefficient"]
    assert not value["activation_disposition"]["same_action_q3_authorized"]
    print("BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
