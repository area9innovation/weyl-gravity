#!/usr/bin/env python3
"""Independently verify the Berger profile-jet Hessian action repair."""

from __future__ import annotations

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
from closed_universe_observers.generate_berger_profile_jet_invariant_hessian_action_repair import (
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


def _basis(emitter):
    base = 84 + 6 * emitter
    output = []
    for family, row in (("K03", base + 2), ("K12", base + 3)):
        output += [
            (f"{family}_e0_A0", [(row, 55, 0, 1)]),
            (f"{family}_e0_A3", [(row, 58, 0, 1)]),
            (f"{family}_e3_A0", [(row, 55, 3, 1)]),
            (f"{family}_e3_A3", [(row, 58, 3, 1)]),
            (f"{family}_div_perp", [(row, 56, 1, 1), (row, 57, 2, 1)]),
            (f"{family}_curl_perp", [(row, 57, 1, 1), (row, 56, 2, -1)]),
        ]
    for family, rows in (("K0_perp", (base, base + 1)), ("K3_perp", (base + 4, base + 5))):
        r1, r2 = rows
        families = [
            ("e0_Aperp", [(r1, 56, 0, 1), (r2, 57, 0, 1)], [(r1, 57, 0, 1), (r2, 56, 0, -1)]),
            ("e3_Aperp", [(r1, 56, 3, 1), (r2, 57, 3, 1)], [(r1, 57, 3, 1), (r2, 56, 3, -1)]),
            ("eperp_A0", [(r1, 55, 1, 1), (r2, 55, 2, 1)], [(r1, 55, 2, 1), (r2, 55, 1, -1)]),
            ("eperp_A3", [(r1, 58, 1, 1), (r2, 58, 2, 1)], [(r1, 58, 2, 1), (r2, 58, 1, -1)]),
        ]
        for name, delta, epsilon in families:
            output.append((f"{family}_{name}_delta", delta))
            output.append((f"{family}_{name}_epsilon", epsilon))
    return output


def _raw_generator(emitter):
    base = 84 + 6 * emitter
    raw = [(k, a, d) for k in range(base, base + 6) for a in range(55, 59) for d in range(4)]
    index = {term: i for i, term in enumerate(raw)}
    k_action = {
        base: ((base + 1, 1),), base + 1: ((base, -1),),
        base + 2: (), base + 3: (),
        base + 4: ((base + 5, 1),), base + 5: ((base + 4, -1),),
    }
    a_action = {55: (), 56: ((57, 1),), 57: ((56, -1),), 58: ()}
    matrix = sp.zeros(96)
    for column, (krow, arow, axis) in enumerate(raw):
        for target, coefficient in k_action[krow]:
            matrix[index[(target, arow, axis)], column] += coefficient
        for target, coefficient in a_action[arow]:
            matrix[index[(krow, target, axis)], column] += coefficient
        if axis == 1:
            matrix[index[(krow, arow, 2)], column] += 1
        elif axis == 2:
            matrix[index[(krow, arow, 1)], column] -= 1
    return raw, matrix


def _local_action(emitter, terms):
    coefficient = product(parameter(f"g{emitter}"), profile(f"h{emitter}", (1,)))
    output = {}
    for krow, arow, axis, sign in terms:
        action_add(
            output,
            ((CHI, ()), (krow, ()), (arow, (axis,))),
            scale(coefficient, rational(sign)),
        )
    return output


def _q2(action):
    result = {}
    for factors, coefficient in action.items():
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = _dual_and_sign(varied[0])
            if not varied[1]:
                tensor_add_symmetric(
                    result, dual, remaining[0], remaining[1],
                    scale(coefficient, rational(pairing_sign)),
                )
            else:
                axis, = varied[1]
                adjoint = rational(-pairing_sign)
                tensor_add_symmetric(
                    result, dual, remaining[0], remaining[1],
                    scale(derivative(coefficient, axis), adjoint),
                )
                tensor_add_symmetric(
                    result, dual,
                    (remaining[0][0], (axis, *remaining[0][1])),
                    remaining[1], scale(coefficient, adjoint),
                )
                tensor_add_symmetric(
                    result, dual, remaining[0],
                    (remaining[1][0], (axis, *remaining[1][1])),
                    scale(coefficient, adjoint),
                )
    return result


def _ward(action):
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in _q2(action).items():
        arity.add_bilinear_term(
            q2[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    row = arity.arity_two_row(
        52, (0, 0), {(0, 0): extension_q1(temporal_order=0)}, q2,
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
        for (output, left, left_word, right, right_word), coefficient in sorted(tensor.items())
    ]


def _payload_vector(entries):
    return {
        _coordinate(entry["coordinate"]): _scalar(entry["coefficient"])
        for entry in entries
    }


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

    closure = [_coordinate(item) for item in dependencies["representation_payload"]["closure_coordinate_basis"]]
    closure_set = set(closure)
    vectors = {}
    preserving = []
    escaping = []
    for emitter in (0, 1):
        raw, generator = _raw_generator(emitter)
        basis = _basis(emitter)
        basis_matrix = sp.zeros(96, 28)
        raw_index = {term: i for i, term in enumerate(raw)}
        for column, (_, terms) in enumerate(basis):
            for krow, arow, axis, sign in terms:
                basis_matrix[raw_index[(krow, arow, axis)], column] += sign
        assert 96 - generator.rank() == 28
        assert generator * basis_matrix == sp.zeros(96, 28)
        assert basis_matrix.rank() == 28
        for name, terms in basis:
            module_id = f"emitter_{emitter}.{name}"
            row = payload["modules"][module_id]
            action = _local_action(emitter, terms)
            q2 = _q2(action)
            ward = _ward(action)
            assert row["action_entries"] == _action_entries(action)
            assert row["cyclic_q2_entries"] == _q2_entries(q2)
            assert _payload_vector(row["ward_vector"]) == ward
            defect = {}
            for coordinate, coefficient in ward.items():
                for target, integer in coordinate_action(coordinate).items():
                    defect = _add(defect, {target: coefficient}, Fraction(integer))
            assert not defect
            vectors[module_id] = ward
            (preserving if set(ward) <= closure_set else escaping).append(module_id)
    assert preserving == payload["closure_preserving_module_ids"]
    assert escaping == payload["closure_escaping_module_ids"]
    assert (len(preserving), len(escaping)) == (24, 32)

    old_payload = dependencies["obstruction_payload"]
    old_coordinates = [_coordinate(item) for item in old_payload["coordinate_basis"]]
    old = {
        name: {old_coordinates[index]: _scalar(scalar) for index, scalar in entries}
        for name, entries in old_payload["vectors"].items()
    }
    minimal = {
        name: {closure[index]: _scalar(scalar) for index, scalar in entries}
        for name, entries in dependencies["minimal_payload"][
            "ward_vectors_on_900_coordinate_closure"
        ].items()
    }
    base = [old[name] for name in ("z_00", "z_01", "z_10", "z_11")] + [
        minimal["epsilon_0"], minimal["epsilon_1"]
    ]
    image = base + [vectors[name] for name in preserving]
    source = minimal["typed_maxwell_source"]
    assert _rank(base, closure) == 6
    assert _rank(image, closure) == 30
    assert _rank(image + [source], closure) == 31

    repair = {}
    for emitter in (0, 1):
        for suffix, coefficient in (
            ("K0_perp_e0_Aperp_delta", Fraction(3, 2)),
            ("K0_perp_eperp_A0_delta", Fraction(-3, 2)),
            ("K03_e0_A3", Fraction(3, 2)),
            ("K03_e3_A0", Fraction(-3, 2)),
        ):
            repair = _add(repair, vectors[f"emitter_{emitter}.{suffix}"], coefficient)
    source_first = {
        coordinate: coefficient
        for coordinate, coefficient in source.items()
        if any(factor[0] == "profile" and factor[2] == (1,) for factor in coordinate[1])
    }
    assert repair == source_first
    residual = _add(_add(source, minimal["epsilon_0"], Fraction(2)), minimal["epsilon_1"], Fraction(2))
    residual = _add(residual, repair, Fraction(-1))
    assert len(residual) == 88
    assert not any(
        factor[0] == "profile" and factor[2] == (1,)
        for coordinate in residual
        for factor in coordinate[1]
    )
    assert not value["activation_disposition"]["complete_typed_maxwell_source_in_action_image"]
    assert not value["activation_disposition"]["detector_redshift_or_recoil_replay_authorized"]
    print("BERGER_PROFILE_JET_INVARIANT_HESSIAN_ACTION_REPAIR independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
