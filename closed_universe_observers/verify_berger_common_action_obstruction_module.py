#!/usr/bin/env python3
"""Independently verify the Berger common-action obstruction module."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import (
    _q1_source_parts,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    SECOND_WITNESS_KEY,
    extension_q1,
    extension_q2,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    ACTION_COLUMN_ORDER,
    A_ROWS,
    CERTIFICATE,
    DEPENDENCIES,
    K_ROWS,
    PAYLOAD,
    PAYLOAD_SCHEMA,
    ROOT,
    SCHEMA,
    SOURCE_ORDER,
)


def _is_a_k(key):
    return (key[0] in A_ROWS and key[2] in K_ROWS) or (
        key[0] in K_ROWS and key[2] in A_ROWS
    )


def _flatten(row):
    return {
        (key, monomial): coefficient
        for key, polynomial in row.items()
        if _is_a_k(key)
        for monomial, coefficient in polynomial.items()
    }


def _raw_sources():
    q1 = _q1_source_parts()["emitter"]
    values = {}
    for source in SOURCE_ORDER:
        row = arity.arity_two_row(
            52,
            (0, 0),
            q1,
            arity.load_q2(sources={source}),
            arity.parities(),
        )
        values[source] = _flatten(
            arity.specialize_bilinear_rows({52: row})[52]
        )
    return values


def _raw_columns():
    values = {}
    for temporal_order in (0, 1):
        for emitter in (0, 1):
            q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
            for (
                target,
                left,
                left_word,
                right,
                right_word,
            ), coefficient in extension_q2(interaction_scale=1).items():
                if not any(
                    factor[0] == "parameter" and factor[1] == f"g{emitter}"
                    for monomial in coefficient
                    for factor in monomial
                ):
                    continue
                arity.add_bilinear_term(
                    q2[(0, 0)].setdefault(target, {}),
                    (left, left_word, right, right_word),
                    coefficient,
                )
            row = arity.arity_two_row(
                52,
                (0, 0),
                {(0, 0): extension_q1(temporal_order=temporal_order)},
                q2,
                arity.parities() + (0, 1),
            )
            values[f"z_{temporal_order}{emitter}"] = _flatten(
                arity.specialize_bilinear_rows({52: row})[52]
            )
    return values


def _parse_coordinate(value):
    left, left_word, right, right_word = value["ward_key"]
    monomial = tuple(
        replay.generator(kind, name, vertical, spacetime)
        for kind, name, vertical, spacetime in value["coefficient_monomial"]
    )
    return (left, tuple(left_word), right, tuple(right_word)), monomial


def _parse_scalar(value):
    return tuple(
        Fraction(numerator, denominator)
        for numerator, denominator in value
    )


def _parse_vector(entries, coordinates):
    return {
        coordinates[index]: _parse_scalar(coefficient)
        for index, coefficient in entries
    }


def _sympy_scalar(value):
    return sp.Rational(value[0].numerator, value[0].denominator) + sp.sqrt(
        10
    ) * sp.Rational(value[1].numerator, value[1].denominator)


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

    coordinates = [_parse_coordinate(item) for item in payload["coordinate_basis"]]
    assert coordinates == sorted(coordinates)
    assert len(coordinates) == len(set(coordinates)) == 444
    vectors = {
        name: _parse_vector(entries, coordinates)
        for name, entries in payload["vectors"].items()
    }
    raw_sources = _raw_sources()
    raw_columns = _raw_columns()
    assert {name: len(raw_sources[name]) for name in SOURCE_ORDER} == {
        "emitter_Diff_BV": 228,
        "base_maxwell_typed": 120,
    }
    assert {name: len(raw_columns[name]) for name in ACTION_COLUMN_ORDER} == {
        "z_00": 30,
        "z_01": 30,
        "z_10": 90,
        "z_11": 90,
    }
    for name in SOURCE_ORDER:
        assert vectors[name] == raw_sources[name]
    for name in ACTION_COLUMN_ORDER:
        assert vectors[name] == raw_columns[name]

    reduction = payload["canonical_linear_reduction"]
    pivots = reduction["pivot_coordinate_indices"]
    assert len(pivots) == 4
    pivot_minor = sp.Matrix(
        [
            [
                _sympy_scalar(vectors[column].get(coordinates[row], (0, 0)))
                for column in ACTION_COLUMN_ORDER
            ]
            for row in pivots
        ]
    )
    assert sp.simplify(pivot_minor.det()) != 0
    linear = value["action_to_ward_map"]["linear_envelope"]
    assert linear["image_rank"] == 4
    assert linear["cokernel_dimension"] == 440
    assert len(reduction["cokernel_representative_coordinate_indices"]) == 440
    zero_image = reduction[
        "coordinate_functionals_annihilating_the_entire_image"
    ]
    assert len(zero_image) == 204
    assert all(
        coordinates[index] not in vectors[column]
        for index in zero_image
        for column in ACTION_COLUMN_ORDER
    )

    g0_h0 = tuple(
        sorted(
            (
                replay.generator("parameter", "g0"),
                replay.generator("profile", "h0"),
            )
        )
    )
    decisive = (SECOND_WITNESS_KEY, g0_h0)
    decisive_index = coordinates.index(decisive)
    projection = value["complete_declared_source_pair_orbit"][
        "typed_maxwell_projection_recovery"
    ]
    assert projection["coordinate"] == decisive_index
    assert vectors["base_maxwell_typed"][decisive] == (Fraction(-2), Fraction(0))
    assert all(decisive not in vectors[column] for column in ACTION_COLUMN_ORDER)
    assert vectors["normalized_110_residual"][decisive] == (
        Fraction(-2),
        Fraction(0),
    )

    # Each source vector has a coordinate-functional witness outside the image.
    image_support = set().union(
        *(set(vectors[column]) for column in ACTION_COLUMN_ORDER)
    )
    assert set(vectors["emitter_Diff_BV"]) - image_support
    assert set(vectors["base_maxwell_typed"]) - image_support

    normalization = value["normalization_cokernel"]
    incidence = sp.Matrix(normalization["field_redefinition_incidence"])
    cycle = sp.Matrix([normalization["primitive_cycle_functional"]])
    valuation = sp.Matrix(normalization["frozen_v2_vector"])
    assert incidence.rank() == 2
    assert cycle * incidence == sp.zeros(1, 3)
    assert (cycle * valuation)[0] == 1
    assert normalization["recovered_holonomy"] == "H=2"

    locus = value["action_to_ward_map"]["nonlinear_action_locus"]
    z = locus["normalized_110_point"]
    assert z[0][0] * z[1][1] - z[0][1] * z[1][0] == 0
    assert value["minimal_lower_bound_theorem"]["outer_scalar_jet_order_alone"] == (
        "INSUFFICIENT_AT_EVERY_FINITE_ORDER"
    )
    assert value["mutations"]["break_rank_one_product_relation"][
        "rejected_by_nonlinear_action_locus"
    ]
    print("BERGER_COMMON_ACTION_OBSTRUCTION_MODULE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
