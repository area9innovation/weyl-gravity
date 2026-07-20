#!/usr/bin/env python3
"""Independently verify the minimal invariant scalar Hessian channel no-go."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers.berger_108_row_component_jet_contract import serialize
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    action_add,
    derivative,
    parameter,
    product,
    profile,
    rational,
    scale,
    tensor_add_symmetric,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    _dual_and_sign,
    extension_q1,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
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
    _rank,
    _scalar,
)


def _local_action(emitter, tensor="epsilon"):
    terms = {
        "epsilon": ((1, 2, 1), (2, 1, -1)),
        "delta": ((1, 1, 1), (2, 2, 1)),
        "symmetric_cross": ((1, 2, 1), (2, 1, 1)),
    }[tensor]
    coefficient = product(parameter(f"g{emitter}"), profile(f"h{emitter}"))
    result = {}
    for left_axis, right_axis, sign in terms:
        action_add(
            result,
            (
                (CHI, ()),
                (55, (left_axis,)),
                (87 + 6 * emitter, (right_axis,)),
            ),
            scale(coefficient, rational(sign)),
        )
    return result


def _q2(action):
    result = {}
    for factors, coefficient in action.items():
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = _dual_and_sign(varied[0])
            if not varied[1]:
                tensor_add_symmetric(
                    result,
                    dual,
                    remaining[0],
                    remaining[1],
                    scale(coefficient, rational(pairing_sign)),
                )
            else:
                axis, = varied[1]
                adjoint_sign = rational(-pairing_sign)
                tensor_add_symmetric(
                    result,
                    dual,
                    remaining[0],
                    remaining[1],
                    scale(derivative(coefficient, axis), adjoint_sign),
                )
                tensor_add_symmetric(
                    result,
                    dual,
                    (remaining[0][0], (axis, *remaining[0][1])),
                    remaining[1],
                    scale(coefficient, adjoint_sign),
                )
                tensor_add_symmetric(
                    result,
                    dual,
                    remaining[0],
                    (remaining[1][0], (axis, *remaining[1][1])),
                    scale(coefficient, adjoint_sign),
                )
    return result


def _ward(emitter, tensor="epsilon"):
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in _q2(
        _local_action(emitter, tensor)
    ).items():
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
        if (55 <= key[0] <= 58 and 84 <= key[2] <= 95)
        or (84 <= key[0] <= 95 and 55 <= key[2] <= 58)
        for monomial, coefficient in polynomial.items()
    }


def _action_entries(action):
    return [
        {
            "factors": [[row, list(word)] for row, word in factors],
            "coefficient": serialize(coefficient),
        }
        for factors, coefficient in sorted(action.items())
    ]


def _q2_entries(tensor):
    return [
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


def _vector_entries(vector, index):
    return [
        [
            index[coordinate],
            [
                [coefficient[0].numerator, coefficient[0].denominator],
                [coefficient[1].numerator, coefficient[1].denominator],
            ],
        ]
        for coordinate, coefficient in sorted(
            vector.items(), key=lambda item: index[item[0]]
        )
    ]


def _add(left, right, factor=Fraction(1)):
    result = dict(left)
    for coordinate, scalar in right.items():
        old = result.get(coordinate, ZERO)
        value = (old[0] + factor * scalar[0], old[1] + factor * scalar[1])
        if value == ZERO:
            result.pop(coordinate, None)
        else:
            result[coordinate] = value
    return result


def _J(vector):
    result = {}
    for coordinate, scalar in vector.items():
        for target, coefficient in coordinate_action(coordinate).items():
            result = _add(
                result,
                {target: (coefficient * scalar[0], coefficient * scalar[1])},
            )
    return result


def _profile_first_jet(coordinate):
    return any(
        factor[0] == "profile" and factor[2] == (1,)
        for factor in coordinate[1]
    )


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

    representation_payload = json.loads(
        DEPENDENCIES["representation_payload"].read_text()
    )
    closure = [
        _coordinate(item)
        for item in representation_payload["closure_coordinate_basis"]
    ]
    index = {coordinate: position for position, coordinate in enumerate(closure)}
    assert len(closure) == len(index) == 900
    old_payload = json.loads(DEPENDENCIES["obstruction_payload"].read_text())
    old_coordinates = [_coordinate(item) for item in old_payload["coordinate_basis"]]
    old_vectors = {
        name: {
            old_coordinates[position]: _scalar(scalar)
            for position, scalar in entries
        }
        for name, entries in old_payload["vectors"].items()
    }

    epsilon = []
    for emitter in (0, 1):
        action = _local_action(emitter)
        tensor = _q2(action)
        column = _ward(emitter)
        epsilon.append(column)
        assert len(action) == 2
        assert len(tensor) == 24
        assert len(column) == 4
        assert payload["local_action_entries"][f"emitter_{emitter}"] == (
            _action_entries(action)
        )
        assert payload["cyclic_q2_entries"][f"emitter_{emitter}"] == (
            _q2_entries(tensor)
        )
        assert payload["ward_vectors_on_900_coordinate_closure"][
            f"epsilon_{emitter}"
        ] == _vector_entries(column, index)
        assert not _J(column)

    rotation = sp.Matrix([[0, -1], [1, 0]])
    reflection = sp.diag(1, -1)
    basis = []
    odd_basis = []
    for raw in (
        sp.Matrix([[1, 0], [0, 0]]),
        sp.Matrix([[0, 1], [0, 0]]),
        sp.Matrix([[0, 0], [1, 0]]),
        sp.Matrix([[0, 0], [0, 1]]),
    ):
        basis.append(rotation.T * raw + raw * rotation)
        odd_basis.append(reflection.T * raw * reflection + raw)
    invariant_matrix = sp.Matrix.hstack(
        *(sp.Matrix(item).reshape(4, 1) for item in basis)
    )
    odd_matrix = sp.Matrix.vstack(
        invariant_matrix,
        sp.Matrix.hstack(*(sp.Matrix(item).reshape(4, 1) for item in odd_basis)),
    )
    assert 4 - invariant_matrix.rank() == 2
    assert 4 - odd_matrix.rank() == 1

    image = [
        old_vectors[name] for name in ("z_00", "z_01", "z_10", "z_11")
    ]
    typed = old_vectors["base_maxwell_typed"]
    assert _rank(image, closure) == 4
    assert _rank(image + epsilon, closure) == 6
    assert _rank(image + epsilon + [typed], closure) == 7
    residual = typed
    for column in epsilon:
        residual = _add(residual, column, Fraction(2))
    assert len(residual) == 112
    assert not _J(residual)
    assert _rank(image + epsilon + [residual], closure) == 7
    vectors = payload["ward_vectors_on_900_coordinate_closure"]
    assert vectors["typed_maxwell_source"] == _vector_entries(typed, index)
    assert vectors["normalized_residual"] == _vector_entries(residual, index)

    typed_first = {
        coordinate: scalar
        for coordinate, scalar in typed.items()
        if _profile_first_jet(coordinate)
    }
    image_first = [
        {
            coordinate: scalar
            for coordinate, scalar in vector.items()
            if _profile_first_jet(coordinate)
        }
        for vector in image + epsilon
    ]
    assert len(typed_first) == 24
    assert not any(image_first[-2:])
    assert not _J(typed_first)
    assert _rank(image_first, closure) == 2
    assert _rank(image_first + [typed_first], closure) == 3

    delta = [_ward(emitter, "delta") for emitter in (0, 1)]
    cross = [_ward(emitter, "symmetric_cross") for emitter in (0, 1)]
    assert all(not _J(vector) for vector in delta)
    assert all(_J(vector) for vector in cross)
    assert all(not (set(vector) & set(typed)) for vector in delta)
    assert value["image_in_representation_closure"][
        "enlarged_closed_cokernel_dimension"
    ] == 894
    assert value["next_invariant_obstruction"]["source_augmented_projected_rank"] == 3
    assert not any(value["activation_disposition"].values())
    print(
        "BERGER_MINIMAL_INVARIANT_SCALAR_HESSIAN_CHANNEL_NO_GO "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
