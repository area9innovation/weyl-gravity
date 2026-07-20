#!/usr/bin/env python3
"""Independent replay of the filtered second-jet curl mapping cone."""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import (
    _pbw_word,
)
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    action_add,
    constant,
    parameter,
    product,
    profile,
    rational,
    scale,
)
from closed_universe_observers.generate_berger_auxiliary_diff_bv_scalar_orbit_repair import (
    scalar_diff_q2,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    generalized_action_to_q2,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    _action_entries,
)
from closed_universe_observers.generate_berger_quartic_completion_moduli_observer_invariance import (
    repair_action,
)
from closed_universe_observers import (
    verify_berger_post_temporal_antifield_module_disposition as prior,
)
from closed_universe_observers import (
    verify_berger_temporal_maxwell_emitter_antifield_covariance_module as base,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = (
    P
    / "certificates/BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION.json"
)
PAYLOAD = (
    P
    / "certificates/BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION_PAYLOAD.json"
)
SCHEMA = (
    P
    / "schema/berger-temporal-maxwell-cotangent-mapping-cone-construction-v1.schema.json"
)
PAYLOAD_SCHEMA = (
    P
    / "schema/berger-temporal-maxwell-cotangent-mapping-cone-construction-payload-v1.schema.json"
)
ORDER_THREE = (
    P / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE_PAYLOAD.json"
)

ROOT10 = sp.sqrt(10)
B = (110, 111)
B_PLUS = (112, 113)
WORDS_TWO = tuple(combinations_with_replacement(range(4), 2))


def scalar(value):
    value = sp.expand(value)
    rational_part = value.coeff(ROOT10, 0)
    root_part = value.coeff(ROOT10, 1)
    assert sp.expand(
        value - rational_part - ROOT10 * root_part
    ) == 0
    return (
        Fraction(int(sp.numer(rational_part)), int(sp.denom(rational_part))),
        Fraction(int(sp.numer(root_part)), int(sp.denom(root_part))),
    )


def quadratic_action():
    action = {}
    for factors, coefficient in (
        (((110, ()), (55, (1,))), 1),
        (((110, ()), (56, (0,))), -1),
        (((111, ()), (55, (2,))), 1),
        (((111, ()), (57, (0,))), -1),
    ):
        action_add(action, factors, constant(coefficient))
    return action


def action_unary(action):
    operator = {}
    for factors, coefficient in action.items():
        for position, varied in enumerate(factors):
            remaining = factors[1 - position]
            if 55 <= varied[0] <= 58:
                output, pairing_sign = varied[0] + 4, -1
            else:
                assert varied[0] in B
                output, pairing_sign = varied[0] + 2, 1
            if not varied[1]:
                replay.add_operator_term(
                    operator,
                    (output, remaining[0], remaining[1]),
                    replay.scale(
                        coefficient,
                        (Fraction(pairing_sign), Fraction(0)),
                    ),
                )
            else:
                sign = pairing_sign * (-1) ** len(varied[1])
                for word, value in replay.apply_word(
                    tuple(reversed(varied[1])),
                    coefficient,
                    remaining[1],
                ).items():
                    replay.add_operator_term(
                        operator,
                        (output, remaining[0], word),
                        replay.scale(
                            value, (Fraction(sign), Fraction(0))
                        ),
                    )
    return operator


def row_action(row, emitter):
    if row == 112:
        return ((113, 1),)
    if row == 113:
        return ((112, -1),)
    base = 84 + 6 * emitter
    return {
        base: ((base + 1, 1),),
        base + 1: ((base, -1),),
        base + 2: (),
        base + 3: (),
        base + 4: ((base + 5, 1),),
        base + 5: ((base + 4, -1),),
    }[row]


def word_action(word):
    output = []
    for position, axis in enumerate(word):
        if axis not in (1, 2):
            continue
        target = 2 if axis == 1 else 1
        sign = 1 if axis == 1 else -1
        current = word[:position] + (target,) + word[position + 1 :]
        for reduced, coefficient in _pbw_word(current):
            output.append(
                (
                    reduced,
                    sign
                    * (
                        sp.Rational(
                            coefficient[0].numerator,
                            coefficient[0].denominator,
                        )
                        + ROOT10
                        * sp.Rational(
                            coefficient[1].numerator,
                            coefficient[1].denominator,
                        )
                    ),
                )
            )
    return output


def raw_basis(emitter):
    result = []
    for b_plus in B_PLUS:
        for k_row in range(84 + 6 * emitter, 90 + 6 * emitter):
            for axis in range(4):
                result.append((b_plus, k_row, (axis,), ()))
            for axis in range(4):
                result.append((b_plus, k_row, (), (axis,)))
            for word in WORDS_TWO:
                result.append((b_plus, k_row, word, ()))
            for tau_axis in range(4):
                for k_axis in range(4):
                    result.append(
                        (b_plus, k_row, (tau_axis,), (k_axis,))
                    )
            for word in WORDS_TWO:
                result.append((b_plus, k_row, (), word))
    assert len(result) == len(set(result)) == 528
    return result


def filtered_actions(emitter):
    raw = raw_basis(emitter)
    index = {monomial: position for position, monomial in enumerate(raw)}
    entries = {}

    def add(row, column, coefficient):
        entries[row, column] = (
            entries.get((row, column), sp.S.Zero) + coefficient
        )

    for column, (b_plus, k_row, tau_word, k_word) in enumerate(raw):
        for target, coefficient in row_action(b_plus, emitter):
            add(index[target, k_row, tau_word, k_word], column, coefficient)
        for target, coefficient in row_action(k_row, emitter):
            add(index[b_plus, target, tau_word, k_word], column, coefficient)
        for target, coefficient in word_action(tau_word):
            add(index[b_plus, k_row, target, k_word], column, coefficient)
        for target, coefficient in word_action(k_word):
            add(index[b_plus, k_row, tau_word, target], column, coefficient)
    matrix = sp.MutableSparseMatrix(528, 528, entries)
    kernel = matrix.nullspace()
    assert matrix.rank() == 404 and len(kernel) == 124

    actions = []
    for order, action in prior.invariant_actions(emitter):
        if order == 0:
            actions.append(("order_0_profile_jet", action))
    coefficient = product(
        parameter(f"g{emitter}"), profile(f"h{emitter}")
    )
    tier_counts = {
        "order_0_profile_jet": 4,
        "order_1": 0,
        "order_2_filtered": 0,
    }
    serialized_kernel = []
    for vector in kernel:
        action = {}
        has_order_two = False
        sparse_vector = []
        for position, (b_plus, k_row, tau_word, k_word) in enumerate(raw):
            if not vector[position]:
                continue
            has_order_two |= len(tau_word) + len(k_word) == 2
            value = scalar(vector[position])
            sparse_vector.append(
                [
                    position,
                    [
                        [value[0].numerator, value[0].denominator],
                        [value[1].numerator, value[1].denominator],
                    ],
                ]
            )
            action_add(
                action,
                ((b_plus, ()), (3, tau_word), (k_row, k_word)),
                scale(coefficient, value),
            )
        tier = "order_2_filtered" if has_order_two else "order_1"
        tier_counts[tier] += 1
        actions.append((tier, action))
        serialized_kernel.append(sparse_vector)
    assert tier_counts == {
        "order_0_profile_jet": 4,
        "order_1": 24,
        "order_2_filtered": 100,
    }
    return actions, matrix, serialized_kernel


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

    q1, indexed, _old_q00, extension = prior.mapping_cone_q1()
    assert action_unary(quadratic_action()) == extension
    assert not prior.cyclic_defect(q1[(0, 0)])

    base_q2 = arity.load_q2()
    prior.add_tensor(base_q2, generalized_action_to_q2(repair_action()))
    prior.add_tensor(base_q2, scalar_diff_q2())
    inherited = json.loads(ORDER_THREE.read_text())["modules"]
    normalized_sources = []

    for emitter in (0, 1):
        actions, matrix, serialized_kernel = filtered_actions(emitter)
        audit = payload["emitter_audits"][f"emitter_{emitter}"]
        assert matrix.rank() == audit["kernel_audit"]["generator_rank"]
        assert len(actions) == audit["second_jet_action_count"] == 128
        assert base.canonical_sha256(serialized_kernel) == audit[
            "kernel_audit"
        ]["kernel_canonical_sha256"]

        old_columns = []
        for record in inherited.values():
            if record["emitter"] != emitter:
                continue
            q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
            prior.add_tensor(
                q2,
                generalized_action_to_q2(
                    base.parse_action(record["action_entries"])
                ),
            )
            old_columns.append(prior.defect(q1, indexed, q2, emitter))
        for components in (range(3), range(3, 6)):
            q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
            prior.add_tensor(
                q2,
                generalized_action_to_q2(
                    base.profile_action(emitter, components)
                ),
            )
            old_columns.append(prior.defect(q1, indexed, q2, emitter))
        old_pivots, old_basis = _echelon(old_columns)
        source = prior.defect(q1, indexed, base_q2, emitter)
        source = base.reduce_vector(source, old_pivots, old_basis)
        assert len(old_pivots) == 934 and len(source) == 42

        antifield_columns = []
        for _name, _sector, _tier, action in base.module(emitter):
            current, _tensor = prior.column(q1, indexed, action, emitter)
            antifield_columns.append(
                base.reduce_vector(current, old_pivots, old_basis)
            )
        antifield_pivots, antifield_basis = _echelon(antifield_columns)
        source = base.reduce_vector(
            source, antifield_pivots, antifield_basis
        )
        assert len(antifield_pivots) == 1679

        columns = []
        records = []
        for index, (tier, action) in enumerate(actions):
            current, tensor = prior.column(q1, indexed, action, emitter)
            current = base.reduce_vector(current, old_pivots, old_basis)
            current = base.reduce_vector(
                current, antifield_pivots, antifield_basis
            )
            columns.append(current)
            entries = _action_entries(action)
            records.append(
                {
                    "id": (
                        f"emitter_{emitter}.order_0.invariant_{index}"
                        if tier == "order_0_profile_jet"
                        else (
                            f"emitter_{emitter}.filtered_second_jet_"
                            f"{index - 4}"
                        )
                    ),
                    "tier": tier,
                    "action_entry_count": len(entries),
                    "action_sha256": base.canonical_sha256(entries),
                    "q2_key_count": len(tensor),
                    "terminal_quotient_manifest": base.manifest(current),
                }
            )
        assert base.canonical_sha256(records) == audit[
            "second_jet_action_records_sha256"
        ]
        pivots, basis = _echelon(columns)
        final_source = base.reduce_vector(source, pivots, basis)
        assert len(pivots) == 28
        assert len(_echelon(columns + [source])[0]) == 29
        assert len(final_source) == 42
        assert base.manifest(final_source) == audit["final_source_manifest"]
        first = min(final_source.items())
        assert base.coordinate_json(*first) == audit[
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
        normalized_sources.append(prior.normalize_emitter(final_source, emitter))

    assert normalized_sources[0] == normalized_sources[1]
    assert certificate["filtered_second_jet_theorem"]["status"] == "OBSTRUCTED"
    assert certificate["downstream_disposition"]["K_Berger_covariance"] == (
        "NOT_EVALUATED_AFTER_ARITY_TWO_OBSTRUCTION"
    )
    print(
        "BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
