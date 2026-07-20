#!/usr/bin/env python3
"""Independently verify the bounded higher-jet invariant action family."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers.berger_108_row_component_jet_contract import (
    _pbw_word,
    generator,
    normalize,
    serialize,
)
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    rational,
    scale,
    tensor_add_symmetric,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    _dual_and_sign,
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    CERTIFICATE,
    DEPENDENCIES,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
)
from closed_universe_observers.verify_berger_ward_cokernel_irrep_closure_obstruction import (
    ZERO,
    _action as coordinate_action,
    _coordinate,
    _decomposition,
    _rank,
    _scalar,
)


ROOT10 = sp.sqrt(10)


def _sympy_scalar(value):
    return (
        sp.Rational(value[0].numerator, value[0].denominator)
        + ROOT10 * sp.Rational(value[1].numerator, value[1].denominator)
    )


def _kernel_data(emitter, order):
    base = 84 + 6 * emitter
    words = lambda degree: list(itertools.combinations_with_replacement(range(4), degree))
    domain = [
        (k, a, word)
        for k in range(base, base + 6)
        for a in range(55, 59)
        for word in words(order)
    ]
    ambient = [
        (k, a, word)
        for k in range(base, base + 6)
        for a in range(55, 59)
        for degree in range(order + 1)
        for word in words(degree)
    ]
    index = {term: position for position, term in enumerate(ambient)}
    k_action = {
        base: ((base + 1, 1),), base + 1: ((base, -1),),
        base + 2: (), base + 3: (),
        base + 4: ((base + 5, 1),), base + 5: ((base + 4, -1),),
    }
    a_action = {55: (), 56: ((57, 1),), 57: ((56, -1),), 58: ()}
    matrix = sp.zeros(len(ambient), len(domain))
    for column, (krow, arow, word) in enumerate(domain):
        for target, coefficient in k_action[krow]:
            matrix[index[(target, arow, word)], column] += coefficient
        for target, coefficient in a_action[arow]:
            matrix[index[(krow, target, word)], column] += coefficient
        for position, axis in enumerate(word):
            replacements = ((2, 1),) if axis == 1 else ((1, -1),) if axis == 2 else ()
            for target, integer in replacements:
                changed = word[:position] + (target,) + word[position + 1 :]
                for reduced, coefficient in _pbw_word(changed):
                    matrix[index[(krow, arow, reduced)], column] += (
                        integer * _sympy_scalar(coefficient)
                    )
    nullspace = matrix.nullspace()
    return len(domain), len(ambient), matrix.rank(), len(nullspace)


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
                    output, dual, remaining[0], remaining[1],
                    scale(coefficient, rational(pairing_sign)),
                )
                continue
            sign = pairing_sign * (-1) ** len(word)
            expansion = arity.apply_output_word(
                tuple(reversed(word)), coefficient,
                remaining[0][1], remaining[1][1],
            )
            for (left_word, right_word), expanded in expansion.items():
                tensor_add_symmetric(
                    output, dual,
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
        for (output, left, left_word, right, right_word), coefficient in sorted(tensor.items())
    ]
    digest = hashlib.sha256(
        json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {"key_count": len(entries), "canonical_sha256": digest}


def _vector(entries):
    return {
        _coordinate(entry["coordinate"]): _scalar(entry["coefficient"])
        for entry in entries
    }


def _add(left, right, factor=Fraction(1)):
    output = dict(left)
    for coordinate, scalar in right.items():
        old = output.get(coordinate, ZERO)
        value = (old[0] + factor * scalar[0], old[1] + factor * scalar[1])
        if value == ZERO:
            output.pop(coordinate, None)
        else:
            output[coordinate] = value
    return output


def _closure(seed):
    result = set(seed)
    frontier = list(seed)
    while frontier:
        coordinate = frontier.pop()
        for target in coordinate_action(coordinate):
            if target not in result:
                result.add(target)
                frontier.append(target)
    return result


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

    classifications = payload["invariant_classification_by_derivative_order"]
    for order, expected in enumerate(classifications):
        raw, ambient, rank, nullity = _kernel_data(0, order)
        assert (raw, ambient, rank, nullity) == (
            expected["raw_dimension"],
            expected["ambient_closure_dimension"],
            expected["generator_rank"],
            expected["invariant_dimension"],
        )

    vectors = []
    for module in payload["modules"].values():
        action = _action(module["action_entries"])
        assert _q2_manifest(_q2(action)) == module["q2_manifest"]
        vector = _vector(module["ward_vector"])
        defect = {}
        for coordinate, coefficient in vector.items():
            for target, integer in coordinate_action(coordinate).items():
                defect = _add(defect, {target: coefficient}, Fraction(integer))
        assert not defect
        vectors.append(vector)

    old_closure = [
        _coordinate(item)
        for item in dependencies["representation_payload"]["closure_coordinate_basis"]
    ]
    closed = _closure(set(old_closure).union(*(set(vector) for vector in vectors)))
    carrier = value["representation_closed_carrier"]
    assert len(closed) == carrier["new_closure_dimension"]
    assert _decomposition(sorted(closed)) == {
        int(weight): dimension
        for weight, dimension in carrier["isotypic_dimensions"].items()
    }

    old_payload = dependencies["obstruction_payload"]
    old_coordinates = [_coordinate(item) for item in old_payload["coordinate_basis"]]
    old = {
        name: {old_coordinates[index]: _scalar(scalar) for index, scalar in entries}
        for name, entries in old_payload["vectors"].items()
    }
    minimal = {
        name: {old_closure[index]: _scalar(scalar) for index, scalar in entries}
        for name, entries in dependencies["minimal_payload"][
            "ward_vectors_on_900_coordinate_closure"
        ].items()
    }
    base = [old[name] for name in ("z_00", "z_01", "z_10", "z_11")] + [
        minimal["epsilon_0"], minimal["epsilon_1"]
    ]
    profile = []
    temporal = []
    order_two = []
    for module_id, module in payload["modules"].items():
        vector = _vector(module["ward_vector"])
        if module_id.startswith("profile_first."):
            profile.append(vector)
        elif module_id.startswith("temporal_lower."):
            temporal.append(vector)
        else:
            order_two.append(vector)
    source = minimal["typed_maxwell_source"]
    lower = base + profile + temporal
    enlarged = lower + order_two
    coordinates = sorted(closed)
    assert _rank(lower, coordinates) == 118
    assert _rank(lower + [source], coordinates) == 119
    assert _rank(enlarged, coordinates) == 230
    assert _rank(enlarged + [source], coordinates) == 231
    assert not any(value["activation_disposition"].values())
    print("BERGER_HIGHER_JET_INVARIANT_ACTION_MODULE_CLASSIFICATION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
