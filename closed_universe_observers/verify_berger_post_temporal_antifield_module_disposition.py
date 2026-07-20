#!/usr/bin/env python3
"""Independent replay of the first-jet Maxwell-cotangent disposition."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    action_add,
    parameter,
    product,
    profile,
    rational,
    scale,
    tensor_add_symmetric,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    extension_q1,
)
from closed_universe_observers.generate_berger_auxiliary_diff_bv_scalar_orbit_repair import (
    scalar_diff_q2,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
    _vector_add,
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    generalized_action_to_q2,
)
from closed_universe_observers.generate_berger_quartic_completion_moduli_observer_invariance import (
    repair_action,
)
from closed_universe_observers import (
    verify_berger_temporal_maxwell_emitter_antifield_covariance_module as prior,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = (
    P / "certificates/BERGER_POST_TEMPORAL_ANTIFIELD_MODULE_DISPOSITION.json"
)
PAYLOAD = (
    P
    / "certificates/BERGER_POST_TEMPORAL_ANTIFIELD_MODULE_DISPOSITION_PAYLOAD.json"
)
SCHEMA = (
    P
    / "schema/berger-post-temporal-antifield-module-disposition-v1.schema.json"
)
PAYLOAD_SCHEMA = (
    P
    / "schema/berger-post-temporal-antifield-module-disposition-payload-v1.schema.json"
)
ORDER_THREE = (
    P / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE_PAYLOAD.json"
)

B = (110, 111)
B_PLUS = (112, 113)
ONE = {(): (Fraction(1), Fraction(0))}
MINUS = {(): (Fraction(-1), Fraction(0))}
PARITY = arity.parities() + (0, 1, 0, 0, 1, 1)


def mapping_cone_q1():
    q1 = arity.completed_q1()
    q1[(0, 0)].update(extension_q1(temporal_order=0))
    old = dict(q1[(0, 0)])
    extension = {}
    for key, coefficient in (
        ((59, 110, (1,)), ONE),
        ((60, 110, (0,)), MINUS),
        ((59, 111, (2,)), ONE),
        ((61, 111, (0,)), MINUS),
        ((112, 55, (1,)), ONE),
        ((112, 56, (0,)), MINUS),
        ((113, 55, (2,)), ONE),
        ((113, 57, (0,)), MINUS),
    ):
        replay.add_operator_term(extension, key, coefficient)
        replay.add_operator_term(q1[(0, 0)], key, coefficient)
    indexed = {
        degree: arity.q1_rows(operator) for degree, operator in q1.items()
    }
    return q1, indexed, old, extension


def pairing():
    value = replay.pairing_map()
    value.update(
        {
            108: (109, (Fraction(1), Fraction(0))),
            109: (108, (Fraction(-1), Fraction(0))),
            110: (112, (Fraction(1), Fraction(0))),
            111: (113, (Fraction(1), Fraction(0))),
            112: (110, (Fraction(-1), Fraction(0))),
            113: (111, (Fraction(-1), Fraction(0))),
        }
    )
    return value


def cyclic_defect(operator):
    paired = defaultdict(dict)
    for row, (partner, pairing_coefficient) in pairing().items():
        for (output, column, word), coefficient in operator.items():
            if output == partner:
                paired[row, column][word] = replay.add(
                    paired[row, column].get(word, {}),
                    replay.scale(coefficient, pairing_coefficient),
                )
    defect = {}
    positions = set(paired) | {(column, row) for row, column in paired}
    for row, column in positions:
        left = paired.get((row, column), {})
        right = replay.formal_adjoint_entry(
            paired.get((column, row), {})
        )
        for word in set(left) | set(right):
            coefficient = replay.add(
                left.get(word, {}),
                replay.scale(
                    right.get(word, {}),
                    (Fraction(-1), Fraction(0)),
                ),
            )
            if coefficient:
                defect[row, column, word] = coefficient
    return defect


def row_generator(row):
    if row in (110, 112):
        return ((row + 1, 1),)
    if row in (111, 113):
        return ((row - 1, -1),)
    for base in (84, 90, 96, 102):
        if base <= row < base + 6:
            return {
                base: ((base + 1, 1),),
                base + 1: ((base, -1),),
                base + 2: (),
                base + 3: (),
                base + 4: ((base + 5, 1),),
                base + 5: ((base + 4, -1),),
            }[row]
    return ()


def axis_generator(axis):
    return ((2, 1),) if axis == 1 else (((1, -1),) if axis == 2 else ())


def invariant_actions(emitter):
    actions = []
    for order in (0, 1):
        k_rows = range(84 + 6 * emitter, 90 + 6 * emitter)
        if order == 0:
            raw = [
                (b_plus, k_row, None, None)
                for b_plus in B_PLUS
                for k_row in k_rows
            ]
        else:
            raw = [
                (b_plus, k_row, placement, axis)
                for b_plus in B_PLUS
                for k_row in k_rows
                for placement in ("tau", "K")
                for axis in range(4)
            ]
        index = {entry: position for position, entry in enumerate(raw)}
        matrix = sp.zeros(len(raw))
        for column, (b_plus, k_row, placement, axis) in enumerate(raw):
            for target, coefficient in row_generator(b_plus):
                matrix[index[target, k_row, placement, axis], column] += (
                    coefficient
                )
            for target, coefficient in row_generator(k_row):
                matrix[index[b_plus, target, placement, axis], column] += (
                    coefficient
                )
            if order:
                for target, coefficient in axis_generator(axis):
                    matrix[
                        index[b_plus, k_row, placement, target], column
                    ] += coefficient
        kernel = matrix.nullspace()
        assert (len(raw), matrix.rank(), len(kernel)) == {
            0: (12, 8, 4),
            1: (96, 72, 24),
        }[order]
        for vector in kernel:
            action = {}
            coefficient = product(
                parameter(f"g{emitter}"),
                profile(f"h{emitter}", (1,) if order == 0 else ()),
            )
            for position, (b_plus, k_row, placement, axis) in enumerate(raw):
                if not vector[position]:
                    continue
                factors = [(b_plus, ()), (3, ()), (k_row, ())]
                if order:
                    slot = 1 if placement == "tau" else 2
                    factors[slot] = (factors[slot][0], (axis,))
                action_add(
                    action,
                    factors,
                    scale(
                        coefficient,
                        rational(Fraction(vector[position])),
                    ),
                )
            actions.append((order, action))
    assert len(actions) == 28
    return actions


def dual(row):
    if row == 3:
        return 52, 1
    if row == 52:
        return 3, -1
    if 55 <= row <= 58:
        return row + 4, -1
    if 59 <= row <= 62:
        return row - 4, 1
    if 84 <= row <= 95:
        return row + 12, 1
    if 96 <= row <= 107:
        return row - 12, -1
    if row in B:
        return row + 2, 1
    if row in B_PLUS:
        return row - 2, -1
    raise AssertionError(row)


def hessian(action):
    tensor = {}
    for factors, coefficient in action.items():
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            output, pairing_sign = dual(varied[0])
            if not varied[1]:
                tensor_add_symmetric(
                    tensor,
                    output,
                    remaining[0],
                    remaining[1],
                    scale(coefficient, rational(pairing_sign)),
                )
                continue
            expansion = arity.apply_output_word(
                tuple(reversed(varied[1])),
                coefficient,
                remaining[0][1],
                remaining[1][1],
            )
            sign = pairing_sign * (-1) ** len(varied[1])
            for (left_word, right_word), value in expansion.items():
                tensor_add_symmetric(
                    tensor,
                    output,
                    (remaining[0][0], left_word),
                    (remaining[1][0], right_word),
                    scale(value, rational(sign)),
                )
    return tensor


def add_tensor(target, tensor):
    for (output, left, left_word, right, right_word), coefficient in tensor.items():
        arity.add_bilinear_term(
            target[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )


def defect(q1, indexed, q2, emitter):
    rows = {}
    for output in (52, 59):
        row = arity.arity_two_row(
            output, (0, 0), q1, q2, PARITY, indexed
        )
        if row:
            rows[output] = row
    rows = arity.specialize_bilinear_rows(rows)
    return {
        ((output, *key), monomial): coefficient
        for output, row in rows.items()
        for key, polynomial in row.items()
        for monomial, coefficient in polynomial.items()
        if any(
            factor[0] == "parameter" and factor[1] == f"g{emitter}"
            for factor in monomial
        )
    }


def column(q1, indexed, action, emitter):
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    tensor = hessian(action)
    add_tensor(q2, tensor)
    return defect(q1, indexed, q2, emitter), tensor


def coordinate_generator(coordinate):
    (output, left, left_word, right, right_word), monomial = coordinate
    transformed = defaultdict(int)
    for target, coefficient in row_generator(left):
        transformed[
            ((output, target, left_word, right, right_word), monomial)
        ] += coefficient
    for position, axis in enumerate(left_word):
        for target, coefficient in axis_generator(axis):
            word = (
                left_word[:position]
                + (target,)
                + left_word[position + 1 :]
            )
            transformed[
                ((output, left, word, right, right_word), monomial)
            ] += coefficient
    for target, coefficient in row_generator(right):
        transformed[
            ((output, left, left_word, target, right_word), monomial)
        ] += coefficient
    for position, axis in enumerate(right_word):
        for target, coefficient in axis_generator(axis):
            word = (
                right_word[:position]
                + (target,)
                + right_word[position + 1 :]
            )
            transformed[
                ((output, left, left_word, right, word), monomial)
            ] += coefficient
    return {
        key: coefficient
        for key, coefficient in transformed.items()
        if coefficient
    }


def vector_generator(vector):
    result = {}
    for coordinate, scalar in vector.items():
        for target, coefficient in coordinate_generator(coordinate).items():
            result = _vector_add(
                result,
                {
                    target: (
                        coefficient * scalar[0],
                        coefficient * scalar[1],
                    )
                },
            )
    return result


def normalize_emitter(vector, emitter):
    if emitter == 0:
        return vector
    result = {}
    for coordinate, scalar in vector.items():
        (output, left, left_word, right, right_word), monomial = coordinate

        def shift(row):
            return row - 6 if 90 <= row <= 107 else row

        normalized_monomial = tuple(
            (
                kind,
                {"g1": "g0", "h1": "h0"}.get(name, name),
                vertical,
                spacetime,
            )
            for kind, name, vertical, spacetime in monomial
        )
        result[
            (
                (
                    output,
                    shift(left),
                    left_word,
                    shift(right),
                    right_word,
                ),
                normalized_monomial,
            )
        ] = scalar
    return result


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for document, schema_path in (
        (certificate, SCHEMA),
        (payload, PAYLOAD_SCHEMA),
    ):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    assert hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == certificate[
        "payload_ref"
    ]["sha256"]
    for reference in certificate["dependency_refs"].values():
        path = ROOT / reference["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference[
            "sha256"
        ]

    q1, indexed, old_q00, extension = mapping_cone_q1()
    introduced00 = replay.add_operators(
        replay.compose(old_q00, extension),
        replay.compose(extension, old_q00),
        replay.compose(extension, extension),
    )
    introduced10 = replay.add_operators(
        replay.compose(q1.get((1, 0), {}), extension),
        replay.compose(extension, q1.get((1, 0), {})),
    )
    assert not introduced00 and not introduced10
    assert not cyclic_defect(q1[(0, 0)])

    base_q2 = arity.load_q2()
    add_tensor(base_q2, generalized_action_to_q2(repair_action()))
    add_tensor(base_q2, scalar_diff_q2())
    inherited = json.loads(ORDER_THREE.read_text())["modules"]

    normalized_sources = []
    for emitter in (0, 1):
        old_columns = []
        for record in inherited.values():
            if record["emitter"] != emitter:
                continue
            q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
            add_tensor(
                q2,
                generalized_action_to_q2(
                    prior.parse_action(record["action_entries"])
                ),
            )
            old_columns.append(defect(q1, indexed, q2, emitter))
        for components in (range(3), range(3, 6)):
            q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
            add_tensor(
                q2,
                generalized_action_to_q2(
                    prior.profile_action(emitter, components)
                ),
            )
            old_columns.append(defect(q1, indexed, q2, emitter))
        old_pivots, old_basis = _echelon(old_columns)
        source = defect(q1, indexed, base_q2, emitter)
        source = prior.reduce_vector(source, old_pivots, old_basis)
        assert len(old_pivots) == 934 and len(source) == 42

        antifield_columns = []
        for _name, _sector, _tier, action in prior.module(emitter):
            current, _tensor = column(q1, indexed, action, emitter)
            antifield_columns.append(
                prior.reduce_vector(current, old_pivots, old_basis)
            )
        antifield_pivots, antifield_basis = _echelon(antifield_columns)
        source = prior.reduce_vector(
            source, antifield_pivots, antifield_basis
        )
        assert len(antifield_pivots) == 1679

        candidate_columns = []
        for _order, action in invariant_actions(emitter):
            current, _tensor = column(q1, indexed, action, emitter)
            current = prior.reduce_vector(current, old_pivots, old_basis)
            current = prior.reduce_vector(
                current, antifield_pivots, antifield_basis
            )
            candidate_columns.append(current)
        candidate_pivots, candidate_basis = _echelon(candidate_columns)
        final_source = prior.reduce_vector(
            source, candidate_pivots, candidate_basis
        )
        augmented = len(_echelon(candidate_columns + [source])[0])
        assert len(candidate_pivots) == 4 and augmented == 5
        assert len(final_source) == 42

        audit = payload["emitter_audits"][f"emitter_{emitter}"]
        assert audit["full_action_image_rank"] == 2617
        assert audit["source_augmented_rank"] == 2618
        assert prior.manifest(final_source) == audit["final_source_manifest"]
        first = min(final_source.items())
        assert prior.coordinate_json(*first) == audit[
            "first_quotient_witness"
        ]
        assert first[0][0] == (
            59,
            3,
            (),
            84 + 6 * emitter,
            (0, 1),
        )
        assert first[1] == (Fraction(-3), Fraction(0))
        orbit = vector_generator(final_source)
        orbit = prior.reduce_vector(orbit, old_pivots, old_basis)
        orbit = prior.reduce_vector(
            orbit, antifield_pivots, antifield_basis
        )
        orbit = prior.reduce_vector(
            orbit, candidate_pivots, candidate_basis
        )
        assert not orbit
        assert prior.manifest(orbit) == audit["representation"][
            "infinitesimal_orbit_quotient_manifest"
        ]
        normalized_sources.append(normalize_emitter(final_source, emitter))

    assert normalized_sources[0] == normalized_sources[1]
    assert prior.manifest(normalized_sources[0]) == payload[
        "emitter_exchange"
    ]["normalized_manifest"]
    assert certificate["finite_class_theorem"]["status"] == "OBSTRUCTED"
    assert certificate["minimal_unexcluded_target"]["status"] == "OPEN"
    assert all(
        value == "NO_CERTIFIED_MAP"
        for key, value in certificate["downstream_disposition"].items()
        if key != "second_jet_action_prolongation"
    )
    print(
        "BERGER_POST_TEMPORAL_ANTIFIELD_MODULE_DISPOSITION "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
