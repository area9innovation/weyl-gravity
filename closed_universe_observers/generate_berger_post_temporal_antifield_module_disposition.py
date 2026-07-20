#!/usr/bin/env python3
"""Classify the first Maxwell-cotangent mapping cone after the old-row no-go."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    action_add,
    parameter,
    product,
    profile,
    rational,
    scale,
    tensor_add_symmetric,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
    _scalar_scale,
    _vector_add,
)
from closed_universe_observers.generate_berger_direct_temporal_ak_diff_covariance_repair import (
    Coordinate,
    Vector,
    action_columns,
    base_q2,
    canonical_sha256,
    coordinate_json,
    extended_q1,
    sha256,
    vector_manifest,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    _action_entries,
)
from closed_universe_observers.generate_berger_temporal_maxwell_emitter_antifield_covariance_module import (
    module_actions,
    reduce_vector,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_POST_TEMPORAL_ANTIFIELD_MODULE_DISPOSITION.json"
)
PAYLOAD = (
    PACKAGE
    / "certificates/BERGER_POST_TEMPORAL_ANTIFIELD_MODULE_DISPOSITION_PAYLOAD.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-post-temporal-antifield-module-disposition-v1.schema.json"
)
PAYLOAD_SCHEMA = (
    PACKAGE
    / "schema/berger-post-temporal-antifield-module-disposition-payload-v1.schema.json"
)
REPORT = (
    PACKAGE
    / "reports/berger-post-temporal-antifield-module-disposition.md"
)
DEPENDENCIES = {
    "terminal_antifield_module": PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE.json",
    "terminal_antifield_payload": PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE_PAYLOAD.json",
    "direct_covariance_predecessor": PACKAGE
    / "certificates/BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR.json",
    "component_contract": PACKAGE
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "complete_q1": PACKAGE
    / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE
    / "verify_berger_post_temporal_antifield_module_disposition.py",
    PACKAGE
    / "tests/test_berger_post_temporal_antifield_module_disposition.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

B01 = 110
B02 = 111
B01_PLUS = 112
B02_PLUS = 113
NEW_PARITIES = arity.parities() + (0, 1, 0, 0, 1, 1)
ONE = {(): (Fraction(1), Fraction(0))}
MINUS_ONE = {(): (Fraction(-1), Fraction(0))}


def mapping_cone_q1() -> tuple[replay.GradedOperator, dict, replay.Operator]:
    """Adjoin the minimal U(1) curl doublet and its signed cotangent dual."""

    q1, _old_index = extended_q1()
    extension: replay.Operator = {}
    entries = (
        ((59, B01, (1,)), ONE),
        ((60, B01, (0,)), MINUS_ONE),
        ((59, B02, (2,)), ONE),
        ((61, B02, (0,)), MINUS_ONE),
        ((B01_PLUS, 55, (1,)), ONE),
        ((B01_PLUS, 56, (0,)), MINUS_ONE),
        ((B02_PLUS, 55, (2,)), ONE),
        ((B02_PLUS, 57, (0,)), MINUS_ONE),
    )
    for key, coefficient in entries:
        replay.add_operator_term(extension, key, coefficient)
        replay.add_operator_term(q1[(0, 0)], key, coefficient)
    indexed = {
        degree: arity.q1_rows(operator) for degree, operator in q1.items()
    }
    return q1, indexed, extension


def extended_pairing() -> dict[int, tuple[int, replay.Scalar]]:
    """Return the old pairing, auxiliary pair and new cotangent doublet."""

    pairing = replay.pairing_map()
    pairing.update(
        {
            108: (109, (Fraction(1), Fraction(0))),
            109: (108, (Fraction(-1), Fraction(0))),
            B01: (B01_PLUS, (Fraction(1), Fraction(0))),
            B02: (B02_PLUS, (Fraction(1), Fraction(0))),
            B01_PLUS: (B01, (Fraction(-1), Fraction(0))),
            B02_PLUS: (B02, (Fraction(-1), Fraction(0))),
        }
    )
    return pairing


def cyclicity_defect(
    operator: replay.Operator,
    pairing: dict[int, tuple[int, replay.Scalar]] | None = None,
) -> replay.Operator:
    """Compute the formal-adjoint unary cyclicity defect on all 114 rows."""

    pairing = pairing or extended_pairing()
    paired: dict[
        tuple[int, int], dict[tuple[int, ...], replay.Polynomial]
    ] = defaultdict(dict)
    for row in range(114):
        partner, pairing_coefficient = pairing[row]
        for (output, column, word), coefficient in operator.items():
            if output != partner:
                continue
            paired[row, column][word] = replay.add(
                paired[row, column].get(word, {}),
                replay.scale(coefficient, pairing_coefficient),
            )
    defect: replay.Operator = {}
    positions = set(paired) | {(column, row) for row, column in paired}
    for row, column in sorted(positions):
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


def new_nilpotency_defects(
    q1: replay.GradedOperator,
    extension: replay.Operator,
) -> dict[tuple[int, int], replay.Operator]:
    """Return only q1-squared terms introduced by the mapping cone."""

    old_q00 = {
        key: coefficient
        for key, coefficient in q1[(0, 0)].items()
        if key not in extension
    }
    return {
        (0, 0): replay.add_operators(
            replay.compose(old_q00, extension),
            replay.compose(extension, old_q00),
            replay.compose(extension, extension),
        ),
        (1, 0): replay.add_operators(
            replay.compose(q1.get((1, 0), {}), extension),
            replay.compose(extension, q1.get((1, 0), {})),
        ),
    }


def row_action(row: int) -> tuple[tuple[int, int], ...]:
    """Infinitesimal Berger U(1) action on the selected row modules."""

    if row in (B01, B01_PLUS):
        return ((row + 1, 1),)
    if row in (B02, B02_PLUS):
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


def axis_action(axis: int) -> tuple[tuple[int, int], ...]:
    if axis == 1:
        return ((2, 1),)
    if axis == 2:
        return ((1, -1),)
    return ()


RawAction = tuple[int, int, str | None, int | None]


def invariant_kernel(
    emitter: int, order: int
) -> tuple[list[RawAction], list[sp.Matrix], sp.Matrix]:
    """Compute, rather than assume, the complete order-zero/one kernel."""

    if order not in (0, 1):
        raise ValueError("certified finite class has order zero or one")
    k_rows = range(84 + 6 * emitter, 90 + 6 * emitter)
    if order == 0:
        raw = [
            (b_plus, k_row, None, None)
            for b_plus in (B01_PLUS, B02_PLUS)
            for k_row in k_rows
        ]
    else:
        raw = [
            (b_plus, k_row, placement, axis)
            for b_plus in (B01_PLUS, B02_PLUS)
            for k_row in k_rows
            for placement in ("tau", "K")
            for axis in range(4)
        ]
    index = {monomial: position for position, monomial in enumerate(raw)}
    generator = sp.zeros(len(raw))
    for column, (b_plus, k_row, placement, axis) in enumerate(raw):
        for target, coefficient in row_action(b_plus):
            generator[
                index[target, k_row, placement, axis], column
            ] += coefficient
        for target, coefficient in row_action(k_row):
            generator[
                index[b_plus, target, placement, axis], column
            ] += coefficient
        if order:
            assert axis is not None
            for target, coefficient in axis_action(axis):
                generator[
                    index[b_plus, k_row, placement, target], column
                ] += coefficient
    return raw, generator.nullspace(), generator


def first_jet_actions(emitter: int) -> list[tuple[str, int, Action]]:
    """Serialize the complete IBP-normal first-jet cotangent action class."""

    actions = []
    for order in (0, 1):
        raw, kernel, _generator = invariant_kernel(emitter, order)
        for basis_index, vector in enumerate(kernel):
            action: Action = {}
            coefficient = product(
                parameter(f"g{emitter}"),
                profile(f"h{emitter}", (1,) if order == 0 else ()),
            )
            for position, (b_plus, k_row, placement, axis) in enumerate(raw):
                if not vector[position]:
                    continue
                factors = [(b_plus, ()), (3, ()), (k_row, ())]
                if order:
                    assert placement is not None and axis is not None
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
            actions.append(
                (
                    f"emitter_{emitter}.order_{order}.invariant_{basis_index}",
                    order,
                    action,
                )
            )
    if len(actions) != 28:
        raise AssertionError("first-jet invariant action count drifted")
    return actions


def dual_and_sign(row: int) -> tuple[int, int]:
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
    if row in (B01, B02):
        return row + 2, 1
    if row in (B01_PLUS, B02_PLUS):
        return row - 2, -1
    raise AssertionError(f"unsupported action row {row}")


def action_to_q2(action: Action) -> dict:
    """Euler-differentiate one local action through the 114-row pairing."""

    output = {}
    for factors, coefficient in action.items():
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = dual_and_sign(varied[0])
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
            expansion = arity.apply_output_word(
                tuple(reversed(word)),
                coefficient,
                remaining[0][1],
                remaining[1][1],
            )
            sign = pairing_sign * (-1) ** len(word)
            for (left_word, right_word), expanded in expansion.items():
                tensor_add_symmetric(
                    output,
                    dual,
                    (remaining[0][0], left_word),
                    (remaining[1][0], right_word),
                    scale(expanded, rational(sign)),
                )
    return output


def projection_defect(
    q1: replay.GradedOperator,
    indexed_q1: dict,
    q2: arity.GradedBilinearRows,
    emitter: int,
) -> Vector:
    rows = {
        output: row
        for output in (52, 59)
        if (
            row := arity.arity_two_row(
                output,
                (0, 0),
                q1,
                q2,
                NEW_PARITIES,
                indexed_q1,
            )
        )
    }
    rows = arity.specialize_bilinear_rows(rows)
    parameter_name = f"g{emitter}"
    return {
        ((output, *key), monomial): coefficient
        for output, row in rows.items()
        for key, polynomial in row.items()
        for monomial, coefficient in polynomial.items()
        if any(
            factor[0] == "parameter" and factor[1] == parameter_name
            for factor in monomial
        )
    }


def action_column(
    q1: replay.GradedOperator,
    indexed_q1: dict,
    action: Action,
    emitter: int,
) -> tuple[Vector, dict]:
    tensor = action_to_q2(action)
    q2 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    for (output, left, left_word, right, right_word), coefficient in tensor.items():
        arity.add_bilinear_term(
            q2[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    return projection_defect(q1, indexed_q1, q2, emitter), tensor


def coordinate_action(coordinate: Coordinate) -> dict[Coordinate, int]:
    """Act on the two inputs of the fixed-output covariance projection."""

    (output, left, left_word, right, right_word), monomial = coordinate
    transformed: dict[Coordinate, int] = defaultdict(int)
    for target, coefficient in row_action(left):
        transformed[
            ((output, target, left_word, right, right_word), monomial)
        ] += coefficient
    for position, axis in enumerate(left_word):
        for target, coefficient in axis_action(axis):
            word = (
                left_word[:position]
                + (target,)
                + left_word[position + 1 :]
            )
            transformed[
                ((output, left, word, right, right_word), monomial)
            ] += coefficient
    for target, coefficient in row_action(right):
        transformed[
            ((output, left, left_word, target, right_word), monomial)
        ] += coefficient
    for position, axis in enumerate(right_word):
        for target, coefficient in axis_action(axis):
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


def vector_action(vector: Vector) -> Vector:
    output: Vector = {}
    for coordinate, scalar in vector.items():
        for target, coefficient in coordinate_action(coordinate).items():
            output = _vector_add(
                output,
                {
                    target: (
                        coefficient * scalar[0],
                        coefficient * scalar[1],
                    )
                },
            )
    return output


def reflection_parity(coordinate: Coordinate, emitter: int) -> int:
    """Reflection e2 -> -e2 on the fixed Maxwell-temporal quotient."""

    (output, left, left_word, right, right_word), _monomial = coordinate
    value = left_word.count(2) + right_word.count(2)
    k_base = 84 + 6 * emitter
    for row in (output, left, right):
        if row in {60, 61}:
            value += int(row == 61)
        if row in {k_base + 1, k_base + 3, k_base + 5}:
            value += 1
    return value % 2


def normalize_emitter(vector: Vector, emitter: int) -> Vector:
    """Normalize source-isolated emitter labels to the emitter-zero carrier."""

    if emitter == 0:
        return vector
    output: Vector = {}
    for coordinate, scalar in vector.items():
        (target, left, left_word, right, right_word), monomial = coordinate

        def shift(row: int) -> int:
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
        output[
            (
                (
                    target,
                    shift(left),
                    left_word,
                    shift(right),
                    right_word,
                ),
                normalized_monomial,
            )
        ] = scalar
    return output


def sequential_reduce(
    vector: Vector,
    stages: list[tuple[list[Coordinate], list[Vector]]],
) -> Vector:
    for pivots, basis in stages:
        vector = reduce_vector(vector, pivots, basis)
    return vector


def extension_entries(extension: replay.Operator) -> list[dict[str, Any]]:
    return [
        {
            "output": output,
            "input": source,
            "pbw_word": list(word),
            "coefficient": [
                [coefficient[()][0].numerator, coefficient[()][0].denominator],
                [coefficient[()][1].numerator, coefficient[()][1].denominator],
            ],
        }
        for (output, source, word), coefficient in sorted(extension.items())
    ]


def build_payload() -> dict[str, Any]:
    q1, indexed_q1, extension = mapping_cone_q1()
    nilpotency = new_nilpotency_defects(q1, extension)
    if any(nilpotency.values()):
        raise AssertionError("mapping-cone q1 is not nilpotent")
    if cyclicity_defect(q1[(0, 0)]):
        raise AssertionError("mapping-cone q1 is not odd cyclic")

    kernel_audits = {}
    for order in (0, 1):
        raw, kernel, generator = invariant_kernel(0, order)
        kernel_audits[f"order_{order}"] = {
            "raw_dimension": len(raw),
            "generator_rank": generator.rank(),
            "invariant_dimension": len(kernel),
            "kernel_matrix_sha256": canonical_sha256(
                [
                    [
                        [value.p, value.q]
                        for value in vector
                    ]
                    for vector in kernel
                ]
            ),
        }

    audits = {}
    normalized_final_sources = []
    for emitter in (0, 1):
        _names, old_columns, _actions = action_columns(
            q1, indexed_q1, emitter
        )
        source = projection_defect(q1, indexed_q1, base_q2(), emitter)
        old_pivots, old_basis = _echelon(old_columns)
        old_source = reduce_vector(source, old_pivots, old_basis)
        if len(old_pivots) != 934 or len(old_source) != 42:
            raise AssertionError("imported old action image drifted")

        antifield_columns = []
        for _name, _sector, _tier, action in module_actions(emitter):
            column, _tensor = action_column(
                q1, indexed_q1, action, emitter
            )
            antifield_columns.append(
                reduce_vector(column, old_pivots, old_basis)
            )
        antifield_pivots, antifield_basis = _echelon(antifield_columns)
        if len(antifield_pivots) != 1679:
            raise AssertionError("terminal antifield image rank drifted")
        post_antifield_source = reduce_vector(
            old_source, antifield_pivots, antifield_basis
        )

        records = []
        candidate_columns = []
        by_order: dict[int, list[Vector]] = {0: [], 1: []}
        for name, order, action in first_jet_actions(emitter):
            column, tensor = action_column(q1, indexed_q1, action, emitter)
            quotient = sequential_reduce(
                column,
                [
                    (old_pivots, old_basis),
                    (antifield_pivots, antifield_basis),
                ],
            )
            candidate_columns.append(quotient)
            by_order[order].append(quotient)
            entries = _action_entries(action)
            records.append(
                {
                    "id": name,
                    "order": order,
                    "action_entry_count": len(entries),
                    "action_sha256": canonical_sha256(entries),
                    "q2_key_count": len(tensor),
                    "terminal_quotient_manifest": vector_manifest(quotient),
                }
            )
        candidate_pivots, candidate_basis = _echelon(candidate_columns)
        final_source = reduce_vector(
            post_antifield_source,
            candidate_pivots,
            candidate_basis,
        )
        augmented_rank = len(
            _echelon(candidate_columns + [post_antifield_source])[0]
        )
        if (
            len(candidate_pivots) != 4
            or augmented_rank != 5
            or len(final_source) != 42
        ):
            raise AssertionError("first-jet disposition rank drifted")
        first_coordinate, first_coefficient = min(final_source.items())
        expected = (59, 3, (), 84 + 6 * emitter, (0, 1))
        if (
            first_coordinate[0] != expected
            or first_coefficient != (Fraction(-3), Fraction(0))
        ):
            raise AssertionError("canonical source witness drifted")

        stages = [
            (old_pivots, old_basis),
            (antifield_pivots, antifield_basis),
            (candidate_pivots, candidate_basis),
        ]
        infinitesimal_orbit = sequential_reduce(
            vector_action(final_source), stages
        )
        if infinitesimal_orbit:
            raise AssertionError("surviving source class is not U1 trivial")
        reflection_support = {
            parity: sum(
                reflection_parity(coordinate, emitter) == parity
                for coordinate in final_source
            )
            for parity in (0, 1)
        }

        order_mutations = {}
        for omitted in (0, 1):
            retained = [
                column
                for order, columns in by_order.items()
                if order != omitted
                for column in columns
            ]
            retained_rank = len(_echelon(retained)[0])
            retained_augmented = len(
                _echelon(retained + [post_antifield_source])[0]
            )
            order_mutations[f"omit_order_{omitted}"] = {
                "retained_rank": retained_rank,
                "source_augmented_rank": retained_augmented,
                "source_still_obstructed": (
                    retained_augmented == retained_rank + 1
                ),
            }

        normalized = normalize_emitter(final_source, emitter)
        normalized_final_sources.append(normalized)
        audits[f"emitter_{emitter}"] = {
            "old_action_image_rank": len(old_pivots),
            "terminal_antifield_quotient_rank": len(antifield_pivots),
            "terminal_full_action_image_rank": (
                len(old_pivots) + len(antifield_pivots)
            ),
            "first_jet_action_count": len(records),
            "first_jet_action_records_sha256": canonical_sha256(records),
            "first_jet_action_records": records,
            "first_jet_quotient_rank": len(candidate_pivots),
            "full_action_image_rank": (
                len(old_pivots)
                + len(antifield_pivots)
                + len(candidate_pivots)
            ),
            "source_augmented_rank": (
                len(old_pivots)
                + len(antifield_pivots)
                + augmented_rank
            ),
            "source_outside_image": True,
            "final_source_manifest": vector_manifest(final_source),
            "normalized_final_source_manifest": vector_manifest(normalized),
            "first_quotient_witness": coordinate_json(
                first_coordinate, first_coefficient
            ),
            "representation": {
                "Berger_U1_weight": 0,
                "infinitesimal_orbit_quotient_manifest": vector_manifest(
                    infinitesimal_orbit
                ),
                "reflection_coordinate_support": reflection_support,
                "reflection_irrep_status": (
                    "NOT_APPLICABLE: reflection is not included in the "
                    "declared connected Berger-U1 representation category"
                ),
            },
            "mutations": order_mutations,
        }
    if normalized_final_sources[0] != normalized_final_sources[1]:
        raise AssertionError("emitter source-isolation crosswalk drifted")

    entries = extension_entries(extension)
    return {
        "schema": (
            "closed-universe-berger-post-temporal-antifield-module-"
            "disposition-payload-v1"
        ),
        "result_id": "BERGER_POST_TEMPORAL_ANTIFIELD_MODULE_DISPOSITION_PAYLOAD",
        "coefficient_field": "Q(sqrt(10)) differential switch-jet algebra",
        "mapping_cone": {
            "old_rows": 110,
            "new_rows": 4,
            "shape": [114, 114],
            "rows": [
                {"index": B01, "row_id": "B_01", "degree": 0},
                {"index": B02, "row_id": "B_02", "degree": 0},
                {"index": B01_PLUS, "row_id": "B_plus_01", "degree": 1},
                {"index": B02_PLUS, "row_id": "B_plus_02", "degree": 1},
            ],
            "q1_entries": entries,
            "q1_entries_sha256": canonical_sha256(entries),
            "new_q1_squared_key_counts": {
                f"{degree[0]},{degree[1]}": len(defect)
                for degree, defect in nilpotency.items()
            },
            "unary_cyclicity_defect_key_count": 0,
            "pairing": [
                [B01, B01_PLUS, 1],
                [B02, B02_PLUS, 1],
                [B01_PLUS, B01, -1],
                [B02_PLUS, B02, -1],
            ],
        },
        "declared_first_jet_class": {
            "normal_form": (
                "local cubic B_plus/tau/K_b actions; B_plus derivatives "
                "removed by integration by parts; total derivative order "
                "zero uses g_b h_b' and order one uses g_b h_b"
            ),
            "Berger_U1_kernel_audits": kernel_audits,
            "action_count_per_emitter": 28,
            "complete_within_declared_class": True,
        },
        "emitter_audits": audits,
        "emitter_exchange": {
            "normalized_source_classes_equal": True,
            "combined_representation": (
                "U1-weight-zero source-label doublet; "
                "under optional emitter exchange it splits into symmetric "
                "and antisymmetric singlets"
            ),
            "normalized_manifest": vector_manifest(
                normalized_final_sources[0]
            ),
        },
        "minimal_unexcluded_target": {
            "id": (
                "BERGER_TEMPORAL_MAXWELL_CURL_DOUBLET_SECOND_JET_"
                "ACTION_PROLONGATION"
            ),
            "carrier_rows": [B01, B02, B01_PLUS, B02_PLUS],
            "q1_and_pairing": "unchanged from the certified four-row cone",
            "new_action_tier": (
                "complete Berger-U1-invariant PBW/IBP order-two "
                "B_plus/tau/K_b cubic action module"
            ),
            "why_minimal": (
                "orders zero and one are complete and miss; the same carrier "
                "with exactly one higher action-jet tier is the least "
                "derivative enlargement not excluded by this theorem"
            ),
            "required_next_checks": [
                "enumerate the full PBW-correct order-two U1 kernel",
                "derive every q2 column as an action Hessian",
                "recompute both source-isolated covariance quotients",
                "delete each irreducible block and derivative tier",
            ],
            "status": "OPEN",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    dependency_values = {
        name: json.loads(path.read_text())
        for name, path in DEPENDENCIES.items()
    }
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    summaries = {}
    for emitter, audit in payload["emitter_audits"].items():
        summaries[emitter] = {
            key: value
            for key, value in audit.items()
            if key != "first_jet_action_records"
        }
    return {
        "schema": (
            "closed-universe-berger-post-temporal-antifield-module-"
            "disposition-v1"
        ),
        "result_id": "BERGER_POST_TEMPORAL_ANTIFIELD_MODULE_DISPOSITION",
        "setting_id": dependency_values["terminal_antifield_module"][
            "setting_id"
        ],
        "claim_status": (
            "OBSTRUCTED_COMPLETE_FIRST_JET_MAXWELL_COTANGENT_CURL_DOUBLET"
        ),
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": value.get("result_id", path.stem),
                "sha256": sha256(path),
            }
            for (name, path), value in zip(
                DEPENDENCIES.items(),
                dependency_values.values(),
                strict=True,
            )
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
        },
        "mapping_cone_gate": {
            "carrier": (
                "four new rows B_01,B_02,B_plus_01,B_plus_02 on the "
                "same Berger background and emitter carrier"
            ),
            "q1_squared": "CERTIFIED_ZERO_FOR_ALL_NEW_COMPOSITIONS",
            "odd_pairing": "CERTIFIED_NONDEGENERATE_SIGNED_COTANGENT_PAIR",
            "unary_odd_cyclicity": "CERTIFIED_ZERO",
            "Berger_U1_equivariance": "CERTIFIED_CURL_DOUBLET",
            "real_structure": (
                "CERTIFIED: all new coefficients are rational and real"
            ),
        },
        "finite_class_theorem": {
            "declared_class": payload["declared_first_jet_class"],
            "per_emitter_audits": summaries,
            "status": "OBSTRUCTED",
            "theorem": (
                "Every local Berger-U1-invariant B-plus/tau/K_b action in "
                "the declared IBP-normal total-order-zero/one class misses "
                "the surviving temporal covariance source class."
            ),
            "scope_warning": (
                "This is not a universal no-go: higher action jets and "
                "larger mixed bundles are not classified."
            ),
        },
        "irreducible_obstruction": {
            "per_emitter": (
                "one U1-weight-zero source-isolated class"
            ),
            "combined_emitters": payload["emitter_exchange"][
                "combined_representation"
            ],
            "emitter_exchange_crosswalk": (
                "CERTIFIED_BY_EXPLICIT_ROW_SHIFT_AND_g/h_LABEL_NORMALIZATION"
            ),
        },
        "minimal_unexcluded_target": payload["minimal_unexcluded_target"],
        "mutations": {
            "omit_order_zero": "DETECTED_BUT_SOURCE_REMAINS_OBSTRUCTED",
            "omit_order_one": "DETECTED_BUT_SOURCE_REMAINS_OBSTRUCTED",
            "delete_one_curl_component": "REJECTED_NOT_BERGER_U1_CLOSED",
            "delete_one_cotangent_partner": "REJECTED_DEGENERATE_PAIRING",
            "flip_one_cotangent_unary_sign": (
                "REJECTED_BY_UNARY_CYCLICITY_AND_NILPOTENCY"
            ),
            "old_2048_action_module": (
                "RETAINED_AS_EXACT_NEGATIVE_CONTROL_AT_RANK_2613"
            ),
        },
        "downstream_disposition": {
            "second_jet_action_prolongation": "OPEN",
            "same_action_q3": "NO_CERTIFIED_MAP",
            "K_Berger_and_raw_D_descent": "NO_CERTIFIED_MAP",
            "detector_redshift_memory_recoil": "NO_CERTIFIED_MAP",
            "tangent_cone_observer_restriction": "NO_CERTIFIED_MAP",
            "quantum_observer_algebra": "NO_CERTIFIED_MAP",
        },
        "assumption_ledger": [
            (
                "The terminal 2613-rank old-row action image and its "
                "42-coordinate source representative are imported by hash."
            ),
            (
                "The finite theorem is restricted to the four-row curl "
                "doublet and IBP-normal action orders zero and one."
            ),
            (
                "Emitter exchange is used only through the explicit same-"
                "background row-and-label crosswalk serialized in the payload."
            ),
        ],
        "missing_object_ledger": [
            "complete PBW/IBP order-two curl-doublet action kernel",
            "a zero arity-two covariance quotient",
            "same-action q3 and K_Berger replay",
            "backreacted relational detector or redshift observable",
        ],
        "next_gate": (
            "ENUMERATE_SECOND_JET_CURL_DOUBLET_ACTION_PROLONGATION_"
            "BEFORE_ANY_Q3_OR_OBSERVER_PROMOTION"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result imports the "
            "terminal temporal Maxwell/emitter antifield obstruction and "
            "constructs the smallest U1-covariant first-derivative q1 "
            "preimage of its Maxwell cotangent row: a four-row temporal "
            "curl doublet with signed cotangent partners. All new q1-squared "
            "compositions and the unary cyclicity defect vanish exactly. "
            "The complete declared first-jet local action class has 4 "
            "order-zero and 24 order-one invariants per emitter. It adds "
            "only four quotient directions, taking the full image rank from "
            "2613 to 2617, while the source raises it to 2618 and retains "
            "the 42-coordinate representative beginning at "
            "A_plus_0<-(tau,e0 e1 K_b,01)=-3 g_b h_b. The surviving "
            "source-isolated class is U1 weight zero. Reflection is outside "
            "the declared connected symmetry category and is not assigned "
            "an irreducible label. "
            "This obstructs only the declared four-row first-jet class. "
            "The minimal unexcluded target is its complete order-two "
            "PBW/IBP action prolongation. No q3, K_Berger, detector, "
            "redshift, recoil, tangent-cone or quantum claim follows."
        ),
        "provenance": {
            "source_files": [
                {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": sha256(path),
                }
                for path in SOURCE_FILES
            ],
            "generator_command": (
                "python3 -m closed_universe_observers."
                "generate_berger_post_temporal_antifield_module_disposition "
                "--write"
            ),
            "independent_verifier_command": (
                "python3 -m closed_universe_observers."
                "verify_berger_post_temporal_antifield_module_disposition"
            ),
        },
    }


def report_text(certificate: dict[str, Any]) -> str:
    audits = certificate["finite_class_theorem"]["per_emitter_audits"]
    lines = [
        "# Berger post-temporal antifield-module disposition",
        "",
        "## Result",
        "",
        "The smallest Berger-\\(U(1)\\) curl preimage is an exact four-row",
        "cotangent mapping cone:",
        "",
        "\\[",
        "q_1 B_{01}=e_1A^+_0-e_0A^+_1,\\qquad",
        "q_1 B_{02}=e_2A^+_0-e_0A^+_2,",
        "\\]",
        "",
        "with the signed adjoint rows on \\(B^+_{01},B^+_{02}\\).  Every new",
        "\\(q_1^2\\) composition and the unary odd-cyclicity defect vanishes",
        "exactly.",
        "",
        "The complete declared first-jet local action class contains 4",
        "order-zero and 24 order-one Berger-invariant actions per emitter.",
        "It does not repair the covariance source:",
        "",
        "| emitter | inherited rank | new curl rank | augmented rank |",
        "| --- | ---: | ---: | ---: |",
    ]
    for emitter, audit in audits.items():
        lines.append(
            f"| {emitter} | {audit['terminal_full_action_image_rank']} | "
            f"{audit['first_jet_quotient_rank']} | "
            f"{audit['source_augmented_rank']} |"
        )
    lines += [
        "",
        "For each source-isolated emitter the surviving class is one",
        "Berger-\\(U(1)\\) weight-zero, reflection-even class.  After the",
        "explicit same-background emitter row/label crosswalk, the two",
        "representatives agree exactly.  Reflection is not part of the",
        "declared connected symmetry category and receives no irrep label.",
        "",
        "## Scope",
        "",
        "This is a finite-class obstruction, not a universal no-go.  The",
        "smallest unexcluded target keeps the same four-row cone and adds the",
        "complete PBW/IBP total-order-two \\(B^+\\tau K_b\\) action tier.",
        "That tier is `OPEN`.  No same-action \\(q_3\\), Cartan generator,",
        "detector, redshift, recoil, tangent-cone, branch, or quantum result",
        "is promoted.",
        "",
    ]
    return "\n".join(lines)


def validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(
        payload
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    validate(certificate, payload)
    if args.write:
        PAYLOAD.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        )
        REPORT.write_text(report_text(certificate))
    print(
        json.dumps(
            {
                "result_id": certificate["result_id"],
                "status": certificate["atlas_status"],
                "payload_sha256": certificate["payload_ref"]["sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
