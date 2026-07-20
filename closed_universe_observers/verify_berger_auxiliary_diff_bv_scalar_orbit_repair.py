#!/usr/bin/env python3
"""Independently verify the auxiliary Diff--BV scalar-orbit obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import serialize
from closed_universe_observers.generate_berger_108_row_emitter_diff_bv_q2_pbw import (
    FRAME_TO_GHOST,
    GHOST_TO_DUAL,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    CHI_PLUS,
    extension_q1,
)
from closed_universe_observers.generate_berger_auxiliary_diff_bv_scalar_orbit_repair import (
    CERTIFICATE,
    DEPENDENCIES,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
)
from closed_universe_observers.verify_berger_quartic_completion_moduli_observer_invariance import (
    _add3,
    _compose,
    _old_relevant,
    _repair_q2,
)


ONE = (Fraction(1), Fraction(0))
MINUS_ONE = (Fraction(-1), Fraction(0))


def canonical_sha256(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def add_symmetric(tensor, output, left, left_word, right, right_word, coefficient):
    parity = arity.parities() + (0, 1)
    for key, value in (
        ((output, left, left_word, right, right_word), coefficient),
        (
            (output, right, right_word, left, left_word),
            replay.scale(
                coefficient,
                MINUS_ONE if parity[left] * parity[right] else ONE,
            ),
        ),
    ):
        combined = replay.add(tensor.get(key, {}), value)
        if combined:
            tensor[key] = combined
        else:
            tensor.pop(key, None)


def independently_rebuild_scalar_q2():
    """Differentiate chi_plus c^a e_a chi without the producer helper."""

    tensor = {}
    coefficient = replay.normalize([(ONE, ())])
    for axis in range(4):
        ghost = FRAME_TO_GHOST[axis]
        add_symmetric(tensor, CHI, ghost, (), CHI, (axis,), coefficient)
        # Formal adjunction of e_a from the varied chi slot gives the scalar
        # density-cotangent action on both c and chi_plus.
        add_symmetric(
            tensor, CHI_PLUS, ghost, (axis,), CHI_PLUS, (), coefficient
        )
        add_symmetric(
            tensor, CHI_PLUS, ghost, (), CHI_PLUS, (axis,), coefficient
        )
        # Variation of the undifferentiated ghost gives the Diff moment map.
        add_symmetric(
            tensor,
            GHOST_TO_DUAL[ghost],
            CHI,
            (axis,),
            CHI_PLUS,
            (),
            replay.scale(coefficient, MINUS_ONE),
        )
    return tensor


def tensor_entries(tensor):
    return [
        {
            "output": output,
            "left_input": [left, list(left_word)],
            "right_input": [right, list(right_word)],
            "coefficient": serialize(coefficient),
        }
        for (
            output,
            left,
            left_word,
            right,
            right_word,
        ), coefficient in sorted(tensor.items())
    ]


def graded(tensor):
    result = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in tensor.items():
        arity.add_bilinear_term(
            result[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    return result


def contractible(rows):
    return {
        output: selected
        for output, row in rows.items()
        if (
            selected := {
                key: coefficient
                for key, coefficient in row.items()
                if output >= 108 or key[0] >= 108 or key[2] >= 108
            }
        )
    }


def contractible_defect(q2):
    q1 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    q1[(0, 0)] = extension_q1(temporal_order=0)
    indexed = {degree: arity.q1_rows(operator) for degree, operator in q1.items()}
    parity = arity.parities() + (0, 1)
    return contractible(
        {
            output: row
            for output in (49, 50, 51, 52, CHI)
            if (
                row := arity.arity_two_row(
                    output, (0, 0), q1, q2, parity, indexed
                )
            )
        }
    )


def add_rows(left, right):
    result = {}
    for source in (left, right):
        for output, row in source.items():
            for key, coefficient in row.items():
                arity.add_bilinear_term(
                    result.setdefault(output, {}), key, coefficient
                )
    return result


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    for path, schema_path in ((CERTIFICATE, SCHEMA), (PAYLOAD, PAYLOAD_SCHEMA)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(json.loads(path.read_text()))
    assert hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == value["payload_ref"][
        "sha256"
    ]
    for name, reference in value["dependency_refs"].items():
        path = ROOT / reference["path"]
        assert path == DEPENDENCIES[name]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]

    scalar = independently_rebuild_scalar_q2()
    entries = tensor_entries(scalar)
    assert len(scalar) == 32
    assert entries == payload["scalar_diff_bv_q2_entries"]
    assert canonical_sha256(entries) == payload["scalar_diff_bv_q2_manifest"][
        "canonical_sha256"
    ]

    inherited = contractible_defect(
        arity.load_q2(sources={"base_gravity_clock"})
    )
    added = contractible_defect(graded(scalar))
    assert sum(len(row) for row in inherited.values()) == 30
    assert sum(len(row) for row in added.values()) == 30
    assert not any(add_rows(inherited, added).values())

    # Rebuild the surviving temporal coordinate from only the two certified
    # sources named in the claim.
    q1 = {}
    replay.load_generic_blocks(
        q1, json.loads(replay.EMITTER.read_text())["emitter_overlay"]["blocks"]
    )
    q2 = arity.load_q2(sources={"emitter_Diff_BV"})
    indexed = {degree: arity.q1_rows(operator) for degree, operator in q1.items()}
    row = arity.arity_two_row(
        52,
        (0, 0),
        q1,
        q2,
        arity.parities() + (0, 1),
        indexed,
    )
    specialized = arity.specialize_bilinear_rows({52: row})[52]
    monomial = (
        ("parameter", "g0", (), (0, 0, 0, 0)),
        ("profile", "h0", (), (0, 0, 0, 0)),
    )
    assert specialized[(55, (0, 1), 84, ())][monomial] == ONE

    repair = _repair_q2()
    assert (CHI_PLUS, 55, (0, 1), 84, ()) not in repair
    assert not any(
        {left, right} == {55, 84}
        for _output, left, _left_word, right, _right_word in scalar
    )

    old = _old_relevant(repair)
    old_repair = _compose(old, repair)
    for key, coefficient in _compose(repair, old).items():
        _add3(old_repair, key, coefficient)
    scalar_repair = _compose(scalar, repair)
    for key, coefficient in _compose(repair, scalar).items():
        _add3(scalar_repair, key, coefficient)
    witness_key = (49, 55, (0, 0, 2), CHI, (), 87, ())
    old_vector = {
        (key, factors): coefficient
        for key, polynomial in old_repair.items()
        for factors, coefficient in polynomial.items()
    }
    scalar_vector = {
        (key, factors): coefficient
        for key, polynomial in scalar_repair.items()
        for factors, coefficient in polynomial.items()
    }
    coordinate = witness_key, monomial
    assert old_vector[coordinate] == (Fraction(-4), Fraction(0))
    assert coordinate not in scalar_vector

    assert value["arity_two_gate"]["admissible_locus_in_alpha_lambda"] == "EMPTY"
    assert value["arity_three_diagnostic"]["decisive_witness"][
        "scalar_repair_cross_coefficient"
    ] == 0
    assert value["K_Berger_and_observer_disposition"][
        "same_action_apparatus_memory_detector_map"
    ] == "NO_CERTIFIED_MAP"
    print(
        "BERGER_AUXILIARY_DIFF_BV_SCALAR_ORBIT_REPAIR independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
