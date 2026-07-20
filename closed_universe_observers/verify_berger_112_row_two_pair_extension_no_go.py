#!/usr/bin/env python3
"""Independently verify the complete 112-row scalar two-pair no-go."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers.berger_108_row_component_jet_contract import (
    _multiindex_from_word,
    serialize,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    PRIOR_WITNESS_KEY,
    SECOND_EMITTER_PRIOR_WITNESS_KEY,
    SECOND_WITNESS_KEY,
)
from closed_universe_observers.generate_berger_112_row_two_pair_extension_no_go import (
    CERTIFICATE,
    DEPENDENCIES,
    PAIR_ROWS,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
    q1_action_basis,
    q2_action_basis,
)


def _record(key, coefficient):
    left, left_word, right, right_word = key
    return {
        "left_input_row": left,
        "left_pbw_multiindex": list(_multiindex_from_word(left_word)),
        "right_input_row": right,
        "right_pbw_multiindex": list(_multiindex_from_word(right_word)),
        "coefficient": serialize(coefficient),
    }


def _independent_replay():
    q1 = {
        degree: dict(operator) for degree, operator in arity.completed_q1().items()
    }
    q2 = {
        degree: {target: dict(row) for target, row in rows.items()}
        for degree, rows in arity.load_q2().items()
    }
    # U=I: pair zero carries the constant unary, pair one the e0 unary.
    q1[(0, 0)].update(q1_action_basis(0, 0))
    q1[(0, 0)].update(q1_action_basis(1, 1))
    # B=[[0,0],[-1,-1]].
    for emitter in (0, 1):
        for (
            target,
            left,
            left_word,
            right,
            right_word,
        ), coefficient in q2_action_basis(1, emitter, -1).items():
            arity.add_bilinear_term(
                q2[(0, 0)].setdefault(target, {}),
                (left, left_word, right, right_word),
                coefficient,
            )
    row = arity.arity_two_row(
        52,
        (0, 0),
        q1,
        q2,
        arity.parities() + (0, 1, 0, 1),
    )
    specialized = arity.specialize_bilinear_rows({52: row})[52]
    old = {
        key: coefficient
        for key, coefficient in specialized.items()
        if key[0] < 108 and key[2] < 108
    }
    return specialized, old


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

    pairing = value["complete_enlarged_ansatz"]["pairing"]
    new_block = sp.Matrix(
        [
            [0, 1, 0, 0],
            [-1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, -1, 0],
        ]
    )
    assert new_block.rank() == pairing["new_block_rank"] == 4
    assert pairing["total_pairing_rank"] == 112
    assert PAIR_ROWS == ((108, 109), (110, 111))

    for pair in (0, 1):
        for order in (0, 1):
            assert len(q1_action_basis(pair, order)) == 2
        for emitter in (0, 1):
            assert len(q2_action_basis(pair, emitter)) == 138
    regenerated = value["complete_enlarged_ansatz"]["basis_regeneration"]
    assert regenerated["complete_unary_basis_key_count"] == 8
    assert regenerated["complete_binary_basis_key_count"] == 552

    specialized, old = _independent_replay()
    assert (len(specialized), sum(map(len, specialized.values()))) == (856, 880)
    assert (len(old), sum(map(len, old.values()))) == (824, 848)
    assert PRIOR_WITNESS_KEY not in old
    assert SECOND_EMITTER_PRIOR_WITNESS_KEY not in old
    assert SECOND_WITNESS_KEY in old
    entries = [_record(key, coefficient) for key, coefficient in sorted(old.items())]
    audit = payload["complete_original_tau_star_replay"]
    assert entries == audit["entries"]
    assert audit["first_scoped_obstruction"] == _record(
        SECOND_WITNESS_KEY, old[SECOND_WITNESS_KEY]
    )

    # Check the quotient invariant under a nontrivial exact GL2 mixing.
    U = sp.eye(2)
    B = sp.Matrix([[0, 0], [-1, -1]])
    R = sp.Matrix([[1, 1], [0, 1]])
    transformed_U = R * U
    transformed_B = R.inv().T * B
    assert transformed_U.T * transformed_B == U.T * B
    quotient = value["field_redefinition_quotient"]
    assert quotient["normalized_compatibility_point"] == [[0, 0], [-1, -1]]

    # The rank-two mutation is genuinely new at two pairs but remains in the
    # same four-column Ward image and cannot touch the decisive projection.
    rank_two = sp.eye(2)
    assert rank_two.det() == 1
    mutation = value["mutations"]["rank_two_Z"]
    assert mutation["excluded_by_one_pair"]
    assert mutation["admitted_by_two_pairs"]
    assert mutation["typed_maxwell_projection"] == "-2 g0 h0"
    module = json.loads(DEPENDENCIES["obstruction_module"].read_text())
    prior = module["complete_declared_source_pair_orbit"][
        "prior_projection_recovery"
    ]
    assert len(prior) == 2
    for projection in prior:
        source = projection["source_coefficient"][0]
        image = projection["image_coefficient"][0]
        assert source == [1, 1] and image == [1, 1]
        assert source[0] + projection["normalized_parameter"] * image[0] == 0
        assert source[0] + image[0] == 2
    typed = module["complete_declared_source_pair_orbit"][
        "typed_maxwell_projection_recovery"
    ]
    assert typed["all_action_columns_zero"]
    assert typed["source_coefficient"] == [[-2, 1], [0, 1]]
    theorem = value["action_to_ward_theorem"]
    assert theorem["two_pair_reachable_parameter_space_dimension"] == 4
    assert theorem["linear_image_rank"] == 4
    assert theorem["cokernel_dimension"] == 440
    assert value["next_minimal_enlargement"]["more_scalar_pairs"] == (
        "PROVED_INSUFFICIENT_FOR_ALL_N>=2"
    )
    assert not any(value["activation_disposition"].values())
    print("BERGER_112_ROW_TWO_PAIR_EXTENSION_NO_GO independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
