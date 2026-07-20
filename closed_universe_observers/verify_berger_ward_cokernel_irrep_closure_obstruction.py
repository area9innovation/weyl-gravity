#!/usr/bin/env python3
"""Independently verify the Berger Ward-cokernel closure obstruction."""

from __future__ import annotations

from collections import defaultdict, deque
from fractions import Fraction
import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_ward_cokernel_irrep_closure_obstruction import (
    CERTIFICATE,
    DEPENDENCIES,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
)


ZERO = (Fraction(0), Fraction(0))


def _coordinate(value):
    left, left_word, right, right_word = value["ward_key"]
    monomial = tuple(
        (kind, name, tuple(vertical), tuple(spacetime))
        for kind, name, vertical, spacetime in value["coefficient_monomial"]
    )
    return (left, tuple(left_word), right, tuple(right_word)), monomial


def _component_action(row):
    if row in (55, 58, 86, 87, 92, 93):
        return ()
    pairs = {
        56: (57, 1),
        57: (56, -1),
        84: (85, 1),
        85: (84, -1),
        88: (89, 1),
        89: (88, -1),
        90: (91, 1),
        91: (90, -1),
        94: (95, 1),
        95: (94, -1),
    }
    return (pairs[row],)


def _word_terms(word):
    for position, axis in enumerate(word):
        if axis == 1:
            yield word[:position] + (2,) + word[position + 1 :], 1
        elif axis == 2:
            yield word[:position] + (1,) + word[position + 1 :], -1


def _action(coordinate):
    (left, left_word, right, right_word), monomial = coordinate
    result = defaultdict(int)
    for target, coefficient in _component_action(left):
        result[((target, left_word, right, right_word), monomial)] += coefficient
    for word, coefficient in _word_terms(left_word):
        result[((left, word, right, right_word), monomial)] += coefficient
    for target, coefficient in _component_action(right):
        result[((left, left_word, target, right_word), monomial)] += coefficient
    for word, coefficient in _word_terms(right_word):
        result[((left, left_word, right, word), monomial)] += coefficient
    return {target: coefficient for target, coefficient in result.items() if coefficient}


def _closure(seed):
    result = set(seed)
    queue = deque(seed)
    while queue:
        coordinate = queue.popleft()
        for target in _action(coordinate):
            if target not in result:
                result.add(target)
                queue.append(target)
    return result


def _blocks(coordinates):
    universe = set(coordinates)
    adjacency = {coordinate: set() for coordinate in coordinates}
    for coordinate in coordinates:
        for target in _action(coordinate):
            assert target in universe
            adjacency[coordinate].add(target)
            adjacency[target].add(coordinate)
    unseen = set(coordinates)
    result = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        block = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for target in adjacency[current]:
                if target in unseen:
                    unseen.remove(target)
                    block.add(target)
                    queue.append(target)
        result.append(sorted(block))
    return result


def _matrix(block):
    index = {coordinate: row for row, coordinate in enumerate(block)}
    matrix = sp.zeros(len(block))
    for column, coordinate in enumerate(block):
        for target, coefficient in _action(coordinate).items():
            matrix[index[target], column] += coefficient
    return matrix


def _decomposition(coordinates):
    dimensions = defaultdict(int)
    for block in _blocks(coordinates):
        matrix = _matrix(block)
        identity = sp.eye(len(block))
        annihilator = matrix * (matrix * matrix + 4 * identity) * (
            matrix * matrix + 16 * identity
        )
        assert annihilator == sp.zeros(len(block))
        dimensions[0] += len(block) - matrix.rank()
        for weight in range(1, 9):
            nullity = len(block) - (
                matrix * matrix + weight * weight * identity
            ).rank()
            if nullity:
                dimensions[weight] += nullity
    assert sum(dimensions.values()) == len(coordinates)
    return dict(sorted(dimensions.items()))


def _scalar(value):
    return tuple(Fraction(numerator, denominator) for numerator, denominator in value)


def _add(left, right, factor=Fraction(1)):
    result = dict(left)
    for coordinate, scalar in right.items():
        old = result.get(coordinate, ZERO)
        value = (
            old[0] + factor * scalar[0],
            old[1] + factor * scalar[1],
        )
        if value == ZERO:
            result.pop(coordinate, None)
        else:
            result[coordinate] = value
    return result


def _vector_action(vector):
    result = {}
    for coordinate, scalar in vector.items():
        for target, coefficient in _action(coordinate).items():
            result = _add(
                result,
                {target: (coefficient * scalar[0], coefficient * scalar[1])},
            )
    return result


def _rank(vectors, coordinates):
    support = sorted(set().union(*(set(vector) for vector in vectors)))
    matrix = sp.Matrix(
        [
            [
                sp.Rational(vector.get(coordinate, ZERO)[0].numerator,
                            vector.get(coordinate, ZERO)[0].denominator)
                + sp.sqrt(10)
                * sp.Rational(vector.get(coordinate, ZERO)[1].numerator,
                              vector.get(coordinate, ZERO)[1].denominator)
                for vector in vectors
            ]
            for coordinate in support
        ]
    )
    assert set(support) <= set(coordinates)
    return matrix.rank()


def _orbit(vector):
    result = []
    current = vector
    for _ in range(5):
        result.append(current)
        current = _vector_action(current)
    return result


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    schema = json.loads(SCHEMA.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(schema).validate(value)
    Draft202012Validator(payload_schema).validate(payload)

    for name, reference in value["dependency_refs"].items():
        path = ROOT / reference["path"]
        assert path == DEPENDENCIES[name]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]
    payload_ref = value["payload_ref"]
    assert ROOT / payload_ref["path"] == PAYLOAD
    assert hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == payload_ref["sha256"]

    old_payload = json.loads(DEPENDENCIES["obstruction_payload"].read_text())
    old_coordinates = [_coordinate(item) for item in old_payload["coordinate_basis"]]
    seed = set(old_coordinates)
    assert len(old_coordinates) == len(seed) == 444
    escaping = [coordinate for coordinate in seed if set(_action(coordinate)) - seed]
    outside = set().union(
        *(set(_action(coordinate)) - seed for coordinate in seed)
    )
    incidences = sum(
        sum(target not in seed for target in _action(coordinate))
        for coordinate in seed
    )
    assert (len(escaping), len(outside), incidences) == (392, 424, 848)
    gate = value["original_444_space_gate"]
    assert not gate["invariant_under_J_Berger_U1"]
    assert not gate["induced_action_on_440_cokernel_exists"]

    closure = sorted(_closure(seed))
    serialized_closure = [_coordinate(item) for item in payload["closure_coordinate_basis"]]
    assert serialized_closure == closure
    assert len(closure) == 900
    index = {coordinate: position for position, coordinate in enumerate(closure)}
    assert payload["original_coordinate_indices_in_closure"] == [
        index[coordinate] for coordinate in old_coordinates
    ]
    sparse_columns = [
        [
            column,
            [[index[target], coefficient] for target, coefficient in sorted(
                _action(coordinate).items(), key=lambda item: index[item[0]]
            )],
        ]
        for column, coordinate in enumerate(closure)
        if _action(coordinate)
    ]
    assert payload["sparse_generator_columns"] == sparse_columns

    decomposition = _decomposition(closure)
    assert decomposition == {0: 460, 2: 424, 4: 16}
    closed = value["minimal_representation_closure"]
    assert closed["isotypic_dimensions"] == {"0": 460, "2": 424, "4": 16}
    assert closed["irreducible_copy_counts"] == {
        "weight_0_real_lines": 460,
        "weight_2_real_planes": 212,
        "weight_4_real_planes": 8,
    }
    for emitter in ("g0", "g1"):
        sector = [
            coordinate
            for coordinate in closure
            if any(
                factor[0] == "parameter" and factor[1] == emitter
                for factor in coordinate[1]
            )
        ]
        assert len(sector) == 450
        assert _decomposition(sector) == {0: 230, 2: 212, 4: 8}

    vectors = {
        name: {
            old_coordinates[position]: _scalar(scalar)
            for position, scalar in entries
        }
        for name, entries in old_payload["vectors"].items()
    }
    image = [vectors[name] for name in ("z_00", "z_01", "z_10", "z_11")]
    assert _rank(image, closure) == 4
    assert all(not _vector_action(vector) for vector in image)
    quotient = value["action_image_and_closed_cokernel"]
    assert quotient["minimal_closed_cokernel_dimension"] == 896
    assert quotient["minimal_closed_cokernel_isotypic_dimensions"] == {
        "0": 456,
        "2": 424,
        "4": 16,
    }

    for name, expected in {
        "emitter_Diff_BV": (3, {"0": 1, "2": 2}),
        "base_maxwell_typed": (1, {"0": 1}),
        "source_total": (3, {"0": 1, "2": 2}),
    }.items():
        orbit = _orbit(vectors[name])
        dimension = _rank(orbit, closure)
        augmented = _rank(image + orbit, closure) - 4
        assert (dimension, augmented) == (expected[0], expected[0])
        certified = value["source_pair_orbit_types"][name]
        assert certified["isotypic_dimensions"] == expected[1]
        assert certified["dimension_mod_action_image"] == expected[0]
    assert not _vector_action(vectors["base_maxwell_typed"])

    module = json.loads(DEPENDENCIES["obstruction_module"].read_text())
    decisive_index = module["complete_declared_source_pair_orbit"][
        "typed_maxwell_projection_recovery"
    ]["coordinate"]
    decisive = old_coordinates[decisive_index]
    display = {decisive: (Fraction(1), Fraction(0))}
    second = _vector_action(_vector_action(display))
    weight_zero = _add(display, second, Fraction(1, 4))
    weight_two = _add(display, weight_zero, Fraction(-1))
    assert _rank(_orbit(display), closure) == 3
    assert not _vector_action(weight_zero)
    assert _vector_action(_vector_action(weight_two)) == {
        coordinate: (-4 * scalar[0], -4 * scalar[1])
        for coordinate, scalar in weight_two.items()
    }
    assert weight_zero[decisive][0] == weight_two[decisive][0] == Fraction(1, 2)
    assert _rank(image + _orbit(display), closure) - 4 == 3

    witness = value["witness_location"]
    assert witness["normalization_H_equals_2"]["Berger_type"] == (
        "weight_0 trivial line"
    )
    assert witness["typed_Maxwell_source_class"]["dimension_mod_action_image"] == 1
    theorem = value["representation_content_theorem"]
    assert theorem["minimal_new_isotypic_content"] == (
        "one additional weight-0 real line"
    )
    assert theorem["pure_weight_2_or_weight_4_channel"] == "INSUFFICIENT"
    assert theorem["action_level_sufficiency"].startswith("NO_CERTIFIED_MAP")
    assert not any(value["activation_disposition"].values())
    print(
        "BERGER_WARD_COKERNEL_IRREP_CLOSURE_OBSTRUCTION "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
