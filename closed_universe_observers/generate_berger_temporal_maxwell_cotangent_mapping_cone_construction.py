#!/usr/bin/env python3
"""Construct and test the filtered second-jet Maxwell-cotangent mapping cone."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import (
    _pbw_word,
)
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    action_add,
    constant,
    parameter,
    product,
    profile,
    rational,
    scale,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
)
from closed_universe_observers.generate_berger_direct_temporal_ak_diff_covariance_repair import (
    action_columns,
    base_q2,
    canonical_sha256,
    coordinate_json,
    sha256,
    vector_manifest,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    _action_entries,
)
from closed_universe_observers.generate_berger_post_temporal_antifield_module_disposition import (
    B01,
    B02,
    B01_PLUS,
    B02_PLUS,
    action_column,
    cyclicity_defect,
    first_jet_actions,
    mapping_cone_q1,
    normalize_emitter,
    projection_defect,
)
from closed_universe_observers.generate_berger_temporal_maxwell_emitter_antifield_covariance_module import (
    module_actions,
    reduce_vector,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = (
    PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION.json"
)
PAYLOAD = (
    PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION_PAYLOAD.json"
)
SCHEMA = (
    PACKAGE
    / "schema/berger-temporal-maxwell-cotangent-mapping-cone-construction-v1.schema.json"
)
PAYLOAD_SCHEMA = (
    PACKAGE
    / "schema/berger-temporal-maxwell-cotangent-mapping-cone-construction-payload-v1.schema.json"
)
REPORT = (
    PACKAGE
    / "reports/berger-temporal-maxwell-cotangent-mapping-cone-construction.md"
)
DEPENDENCIES = {
    "disposition": PACKAGE
    / "certificates/BERGER_POST_TEMPORAL_ANTIFIELD_MODULE_DISPOSITION.json",
    "disposition_payload": PACKAGE
    / "certificates/BERGER_POST_TEMPORAL_ANTIFIELD_MODULE_DISPOSITION_PAYLOAD.json",
    "terminal_antifield_module": PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE.json",
    "terminal_antifield_payload": PACKAGE
    / "certificates/BERGER_TEMPORAL_MAXWELL_EMITTER_ANTIFIELD_COVARIANCE_MODULE_PAYLOAD.json",
    "component_contract": PACKAGE
    / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "complete_q1": PACKAGE
    / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE
    / "verify_berger_temporal_maxwell_cotangent_mapping_cone_construction.py",
    PACKAGE
    / "tests/test_berger_temporal_maxwell_cotangent_mapping_cone_construction.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

ROOT10 = sp.sqrt(10)
ORDER_TWO_WORDS = tuple(combinations_with_replacement(range(4), 2))


def qsqrt10(value: sp.Expr) -> tuple[Fraction, Fraction]:
    """Convert one exact SymPy element of Q(sqrt(10)) to the carrier scalar."""

    value = sp.expand(value)
    rational_part = value.coeff(ROOT10, 0)
    root_part = value.coeff(ROOT10, 1)
    if sp.expand(value - rational_part - ROOT10 * root_part) != 0:
        raise ValueError(f"coefficient is outside Q(sqrt(10)): {value}")
    return (
        Fraction(int(sp.numer(rational_part)), int(sp.denom(rational_part))),
        Fraction(int(sp.numer(root_part)), int(sp.denom(root_part))),
    )


def quadratic_mapping_cone_action() -> Action:
    """Return the single local quadratic action generating the eight q1 rows."""

    action: Action = {}
    for factors, coefficient in (
        (((B01, ()), (55, (1,))), 1),
        (((B01, ()), (56, (0,))), -1),
        (((B02, ()), (55, (2,))), 1),
        (((B02, ()), (57, (0,))), -1),
    ):
        action_add(action, factors, constant(coefficient))
    return action


def unary_dual(row: int) -> tuple[int, int]:
    if 55 <= row <= 58:
        return row + 4, -1
    if row in (B01, B02):
        return row + 2, 1
    raise AssertionError(f"unsupported quadratic action row {row}")


def quadratic_action_to_q1(action: Action) -> replay.Operator:
    """Euler-differentiate the quadratic action through the odd pairing."""

    output: replay.Operator = {}
    for factors, coefficient in action.items():
        if len(factors) != 2:
            raise AssertionError("quadratic q1 action ceased to be quadratic")
        for position, varied in enumerate(factors):
            remaining = factors[1 - position]
            output_row, pairing_sign = unary_dual(varied[0])
            if not varied[1]:
                replay.add_operator_term(
                    output,
                    (output_row, remaining[0], remaining[1]),
                    replay.scale(
                        coefficient,
                        (Fraction(pairing_sign), Fraction(0)),
                    ),
                )
                continue
            sign = pairing_sign * (-1) ** len(varied[1])
            for word, expanded in replay.apply_word(
                tuple(reversed(varied[1])),
                coefficient,
                remaining[1],
            ).items():
                replay.add_operator_term(
                    output,
                    (output_row, remaining[0], word),
                    replay.scale(
                        expanded, (Fraction(sign), Fraction(0))
                    ),
                )
    return output


def row_action(row: int, emitter: int) -> tuple[tuple[int, int], ...]:
    if row in (B01_PLUS,):
        return ((B02_PLUS, 1),)
    if row in (B02_PLUS,):
        return ((B01_PLUS, -1),)
    base = 84 + 6 * emitter
    return {
        base: ((base + 1, 1),),
        base + 1: ((base, -1),),
        base + 2: (),
        base + 3: (),
        base + 4: ((base + 5, 1),),
        base + 5: ((base + 4, -1),),
    }[row]


def word_action(word: tuple[int, ...]) -> list[tuple[tuple[int, ...], sp.Expr]]:
    """Apply J e1=e2, J e2=-e1 and reduce every term to Berger PBW form."""

    output = []
    for position, axis in enumerate(word):
        if axis not in (1, 2):
            continue
        target = 2 if axis == 1 else 1
        sign = 1 if axis == 1 else -1
        replaced = word[:position] + (target,) + word[position + 1 :]
        for reduced, (rational_part, root_part) in _pbw_word(replaced):
            coefficient = sign * (
                sp.Rational(
                    rational_part.numerator, rational_part.denominator
                )
                + ROOT10
                * sp.Rational(root_part.numerator, root_part.denominator)
            )
            output.append((reduced, coefficient))
    return output


RawMonomial = tuple[int, int, tuple[int, ...], tuple[int, ...]]


def filtered_raw_basis(emitter: int) -> list[RawMonomial]:
    """Return the IBP-normal order-one/two g_b h_b monomial basis."""

    output = []
    for b_plus in (B01_PLUS, B02_PLUS):
        for k_row in range(84 + 6 * emitter, 90 + 6 * emitter):
            for axis in range(4):
                output.append((b_plus, k_row, (axis,), ()))
            for axis in range(4):
                output.append((b_plus, k_row, (), (axis,)))
            for word in ORDER_TWO_WORDS:
                output.append((b_plus, k_row, word, ()))
            for tau_axis in range(4):
                for k_axis in range(4):
                    output.append(
                        (b_plus, k_row, (tau_axis,), (k_axis,))
                    )
            for word in ORDER_TWO_WORDS:
                output.append((b_plus, k_row, (), word))
    if len(output) != 528 or len(set(output)) != 528:
        raise AssertionError("filtered order-two raw basis drifted")
    return output


def filtered_generator(
    emitter: int,
) -> tuple[list[RawMonomial], sp.MutableSparseMatrix]:
    """Build the full PBW-filtered infinitesimal U1 generator."""

    raw = filtered_raw_basis(emitter)
    index = {monomial: position for position, monomial in enumerate(raw)}
    entries: dict[tuple[int, int], sp.Expr] = {}

    def add(row: int, column: int, coefficient: sp.Expr) -> None:
        entries[row, column] = (
            entries.get((row, column), sp.S.Zero) + coefficient
        )

    for column, (b_plus, k_row, tau_word, k_word) in enumerate(raw):
        for target, coefficient in row_action(b_plus, emitter):
            add(
                index[target, k_row, tau_word, k_word],
                column,
                coefficient,
            )
        for target, coefficient in row_action(k_row, emitter):
            add(
                index[b_plus, target, tau_word, k_word],
                column,
                coefficient,
            )
        for target, coefficient in word_action(tau_word):
            add(
                index[b_plus, k_row, target, k_word],
                column,
                coefficient,
            )
        for target, coefficient in word_action(k_word):
            add(
                index[b_plus, k_row, tau_word, target],
                column,
                coefficient,
            )
    return raw, sp.MutableSparseMatrix(len(raw), len(raw), entries)


def filtered_second_jet_actions(
    emitter: int,
) -> tuple[list[tuple[str, str, Action]], dict[str, Any]]:
    """Return four h' actions plus the complete filtered g h kernel."""

    actions = [
        (name, "order_0_profile_jet", action)
        for name, order, action in first_jet_actions(emitter)
        if order == 0
    ]
    raw, generator = filtered_generator(emitter)
    kernel = generator.nullspace()
    if generator.rank() != 404 or len(kernel) != 124:
        raise AssertionError("filtered second-jet U1 kernel drifted")
    coefficient = product(
        parameter(f"g{emitter}"), profile(f"h{emitter}")
    )
    tier_counts = {
        "order_0_profile_jet": len(actions),
        "order_1": 0,
        "order_2_filtered": 0,
    }
    mixed_lower_corrections = 0
    for basis_index, vector in enumerate(kernel):
        action: Action = {}
        has_order_two = False
        has_order_one = False
        for position, (b_plus, k_row, tau_word, k_word) in enumerate(raw):
            if not vector[position]:
                continue
            total_order = len(tau_word) + len(k_word)
            has_order_one |= total_order == 1
            has_order_two |= total_order == 2
            action_add(
                action,
                ((b_plus, ()), (3, tau_word), (k_row, k_word)),
                scale(coefficient, qsqrt10(vector[position])),
            )
        tier = "order_2_filtered" if has_order_two else "order_1"
        tier_counts[tier] += 1
        mixed_lower_corrections += int(has_order_two and has_order_one)
        actions.append(
            (
                f"emitter_{emitter}.filtered_second_jet_{basis_index}",
                tier,
                action,
            )
        )
    if tier_counts != {
        "order_0_profile_jet": 4,
        "order_1": 24,
        "order_2_filtered": 100,
    }:
        raise AssertionError("filtered action tier counts drifted")
    kernel_serialized = [
        [
            [
                position,
                [
                    [qsqrt10(value)[0].numerator, qsqrt10(value)[0].denominator],
                    [qsqrt10(value)[1].numerator, qsqrt10(value)[1].denominator],
                ],
            ]
            for position, value in enumerate(vector)
            if value
        ]
        for vector in kernel
    ]
    audit = {
        "raw_dimension": len(raw),
        "generator_rank": generator.rank(),
        "kernel_dimension": len(kernel),
        "generator_nnz": generator.nnz(),
        "tier_counts": tier_counts,
        "order_two_vectors_with_lower_order_PBW_corrections": (
            mixed_lower_corrections
        ),
        "kernel_canonical_sha256": canonical_sha256(kernel_serialized),
    }
    if len(actions) != 128:
        raise AssertionError("complete second-jet action count drifted")
    return actions, audit


def sequential_reduce(vector, stages):
    for pivots, basis in stages:
        vector = reduce_vector(vector, pivots, basis)
    return vector


def build_payload() -> dict[str, Any]:
    q1, indexed_q1, extension = mapping_cone_q1()
    quadratic_action = quadratic_mapping_cone_action()
    action_unary = quadratic_action_to_q1(quadratic_action)
    if action_unary != extension:
        raise AssertionError("quadratic action does not reproduce mapping-cone q1")
    if cyclicity_defect(q1[(0, 0)]):
        raise AssertionError("mapping-cone unary cyclicity drifted")

    audits = {}
    normalized_sources = []
    kernel_crosscheck = None
    for emitter in (0, 1):
        actions, kernel_audit = filtered_second_jet_actions(emitter)
        if kernel_crosscheck is None:
            kernel_crosscheck = {
                key: value
                for key, value in kernel_audit.items()
                if key != "kernel_canonical_sha256"
            }
        elif kernel_crosscheck != {
            key: value
            for key, value in kernel_audit.items()
            if key != "kernel_canonical_sha256"
        }:
            raise AssertionError("emitter filtered-kernel dimensions differ")

        _names, old_columns, _actions = action_columns(
            q1, indexed_q1, emitter
        )
        source = projection_defect(q1, indexed_q1, base_q2(), emitter)
        old_pivots, old_basis = _echelon(old_columns)
        source = reduce_vector(source, old_pivots, old_basis)
        if len(old_pivots) != 934 or len(source) != 42:
            raise AssertionError("old action image drifted")

        antifield_columns = []
        for _name, _sector, _tier, action in module_actions(emitter):
            column, _tensor = action_column(
                q1, indexed_q1, action, emitter
            )
            antifield_columns.append(
                reduce_vector(column, old_pivots, old_basis)
            )
        antifield_pivots, antifield_basis = _echelon(antifield_columns)
        source = reduce_vector(
            source, antifield_pivots, antifield_basis
        )
        if len(antifield_pivots) != 1679:
            raise AssertionError("terminal antifield rank drifted")

        columns = []
        by_tier: dict[str, list] = {
            "order_0_profile_jet": [],
            "order_1": [],
            "order_2_filtered": [],
        }
        records = []
        for name, tier, action in actions:
            column, tensor = action_column(
                q1, indexed_q1, action, emitter
            )
            quotient = sequential_reduce(
                column,
                [
                    (old_pivots, old_basis),
                    (antifield_pivots, antifield_basis),
                ],
            )
            columns.append(quotient)
            by_tier[tier].append(quotient)
            entries = _action_entries(action)
            records.append(
                {
                    "id": name,
                    "tier": tier,
                    "action_entry_count": len(entries),
                    "action_sha256": canonical_sha256(entries),
                    "q2_key_count": len(tensor),
                    "terminal_quotient_manifest": vector_manifest(quotient),
                }
            )
        pivots, basis = _echelon(columns)
        final_source = reduce_vector(source, pivots, basis)
        augmented_rank = len(_echelon(columns + [source])[0])
        if (
            len(pivots) != 28
            or augmented_rank != 29
            or len(final_source) != 42
        ):
            raise AssertionError("second-jet quotient disposition drifted")
        first_coordinate, first_coefficient = min(final_source.items())
        expected = (59, 3, (), 84 + 6 * emitter, (0, 1))
        if (
            first_coordinate[0] != expected
            or first_coefficient != (Fraction(-3), Fraction(0))
        ):
            raise AssertionError("second-jet canonical witness drifted")

        mutations = {}
        for omitted in by_tier:
            retained = [
                column
                for tier, tier_columns in by_tier.items()
                if tier != omitted
                for column in tier_columns
            ]
            retained_rank = len(_echelon(retained)[0])
            retained_augmented = len(_echelon(retained + [source])[0])
            mutations[f"omit_{omitted}"] = {
                "retained_action_count": len(retained),
                "retained_quotient_rank": retained_rank,
                "source_augmented_rank": retained_augmented,
                "source_still_obstructed": (
                    retained_augmented == retained_rank + 1
                ),
            }
        normalized = normalize_emitter(final_source, emitter)
        normalized_sources.append(normalized)
        audits[f"emitter_{emitter}"] = {
            "kernel_audit": kernel_audit,
            "old_action_image_rank": len(old_pivots),
            "terminal_antifield_quotient_rank": len(antifield_pivots),
            "terminal_full_action_image_rank": (
                len(old_pivots) + len(antifield_pivots)
            ),
            "second_jet_action_count": len(actions),
            "second_jet_action_records_sha256": canonical_sha256(records),
            "second_jet_action_records": records,
            "second_jet_quotient_rank": len(pivots),
            "full_action_image_rank": (
                len(old_pivots) + len(antifield_pivots) + len(pivots)
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
            "mutations": mutations,
        }
    if normalized_sources[0] != normalized_sources[1]:
        raise AssertionError("second-jet emitter crosswalk drifted")

    quadratic_entries = _action_entries(quadratic_action)
    return {
        "schema": (
            "closed-universe-berger-temporal-maxwell-cotangent-mapping-"
            "cone-construction-payload-v1"
        ),
        "result_id": (
            "BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_"
            "CONSTRUCTION_PAYLOAD"
        ),
        "coefficient_field": "Q(sqrt(10)) differential switch-jet algebra",
        "quadratic_mapping_cone_action": {
            "entries": quadratic_entries,
            "canonical_sha256": canonical_sha256(quadratic_entries),
            "derived_q1_key_count": len(action_unary),
            "derived_q1_equals_declared_extension": True,
        },
        "carrier_completion": {
            "shape": [114, 114],
            "new_rows": [
                "B_01",
                "B_02",
                "B_plus_01",
                "B_plus_02",
            ],
            "reducibility": (
                "NOT_APPLICABLE in the declared auxiliary curl cone: no "
                "independent gauge generator is assigned to B"
            ),
            "nonminimal_sector": (
                "NOT_APPLICABLE: the signed B/B_plus cotangent doublet is "
                "already the complete declared auxiliary carrier"
            ),
            "odd_pairing": "nondegenerate signed cotangent doublet",
            "real_structure": "all quadratic and cubic coefficients are real",
        },
        "filtered_second_jet_class": {
            "normal_form": (
                "B_plus derivatives removed by IBP; all order-one and "
                "order-two tau/K PBW placements with coefficient g_b h_b, "
                "plus the independent order-zero g_b h_b-prime kernel"
            ),
            "action_count_per_emitter": 128,
            "complete_within_declared_class": True,
        },
        "emitter_audits": audits,
        "emitter_exchange": {
            "normalized_source_classes_equal": True,
            "normalized_manifest": vector_manifest(normalized_sources[0]),
        },
        "negative_controls": {
            "old_2048_action_module": "rank 2613 < source-augmented rank 2614",
            "first_jet_mapping_cone": "rank 2617 < source-augmented rank 2618",
            "delete_curl_doublet": "returns the certified old-row obstruction",
            "delete_cotangent_doublet": "degenerates the odd pairing and removes every new cubic Hessian",
        },
        "next_unexcluded_target": {
            "id": (
                "BERGER_TEMPORAL_MAXWELL_CURL_DOUBLET_THIRD_JET_"
                "ACTION_PROLONGATION"
            ),
            "action_tier": (
                "complete filtered PBW/IBP total-order-three "
                "B_plus/tau/K_b module on the same four-row cone"
            ),
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
            if key != "second_jet_action_records"
        }
    return {
        "schema": (
            "closed-universe-berger-temporal-maxwell-cotangent-mapping-"
            "cone-construction-v1"
        ),
        "result_id": (
            "BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION"
        ),
        "setting_id": dependency_values["disposition"]["setting_id"],
        "claim_status": (
            "OBSTRUCTED_COMPLETE_FILTERED_SECOND_JET_CURL_MAPPING_CONE"
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
        "mapping_cone_action_gate": {
            "quadratic_action": "CERTIFIED",
            "all_eight_new_q1_rows_action_derived": "CERTIFIED",
            "q1_squared": "CERTIFIED_ZERO_BY_IMPORTED_DISPOSITION",
            "unary_odd_cyclicity": "CERTIFIED_ZERO",
            "odd_pairing": "CERTIFIED_NONDEGENERATE",
            "real_structure": "CERTIFIED",
            "reducibility_and_nonminimal_disposition": payload[
                "carrier_completion"
            ],
        },
        "filtered_second_jet_theorem": {
            "declared_class": payload["filtered_second_jet_class"],
            "per_emitter_audits": summaries,
            "status": "OBSTRUCTED",
            "theorem": (
                "Every action-derived q2 in the complete declared filtered "
                "second-jet curl-doublet class misses the temporal Maxwell/"
                "emitter covariance source."
            ),
            "scope_warning": (
                "This is not a universal no-go; the filtered third-jet "
                "module and larger mixed bundles remain unclassified."
            ),
        },
        "minimality": payload["negative_controls"],
        "next_unexcluded_target": payload["next_unexcluded_target"],
        "downstream_disposition": {
            "K_Berger_covariance": (
                "NOT_EVALUATED_AFTER_ARITY_TWO_OBSTRUCTION"
            ),
            "raw_D_descent": "NO_CERTIFIED_MAP",
            "same_action_q3": "NO_CERTIFIED_MAP",
            "detector_redshift_memory_recoil": "NO_CERTIFIED_MAP",
            "tangent_cone_observer_restriction": "NO_CERTIFIED_MAP",
            "branch_and_quantum": "NO_CERTIFIED_MAP",
        },
        "assumption_ledger": [
            (
                "The disposition theorem, terminal 2048-action module and "
                "their independent verifiers are imported by exact hashes."
            ),
            (
                "The finite completeness claim is restricted to the four-"
                "row curl cone and filtered total action order at most two."
            ),
            (
                "No gauge reducibility is assigned to the auxiliary B "
                "doublet; no omitted nonminimal sector is inferred."
            ),
        ],
        "missing_object_ledger": [
            "zero arity-two covariance quotient",
            "filtered third-jet curl-doublet action module",
            "K_Berger covariance on an arity-two-admissible mapping cone",
            "same-action q3 and relational observer replay",
        ],
        "next_gate": (
            "CLASSIFY_FILTERED_THIRD_JET_CURL_DOUBLET_BEFORE_K_BERGER_"
            "OR_OBSERVER_PROPAGATION"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE calculation imports "
            "the certified four-row Maxwell-cotangent curl cone and derives "
            "all eight new q1 rows from one serialized quadratic action. "
            "The complete filtered second-jet local class has 128 cubic "
            "actions per emitter: four independent g_b h_b-prime order-zero "
            "directions and a 124-dimensional PBW-correct kernel inside 528 "
            "raw g_b h_b order-one/two monomials. Every q2 column is an "
            "Euler Hessian. The module adds quotient rank 28 to the terminal "
            "rank 2613 image, but the source raises the full rank from 2641 "
            "to 2642 for both emitters and retains the same 42-coordinate "
            "representative beginning at -3 g_b h_b. This is the first "
            "exact obstruction, so K_Berger covariance and all q3, detector, "
            "redshift, recoil, tangent-cone, branch and quantum gates are "
            "not evaluated or promoted."
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
                "generate_berger_temporal_maxwell_cotangent_mapping_cone_"
                "construction --write"
            ),
            "independent_verifier_command": (
                "python3 -m closed_universe_observers."
                "verify_berger_temporal_maxwell_cotangent_mapping_cone_"
                "construction"
            ),
        },
    }


def report_text(certificate: dict[str, Any]) -> str:
    return """# Berger temporal Maxwell-cotangent mapping-cone construction

## Result

The four-row curl mapping cone is generated by one exact quadratic action
whose Euler Hessian reproduces all eight new unary rows.  Its signed
cotangent pairing, nilpotency, unary cyclicity and real structure are exact.

The complete declared second-jet class contains 128 local cubic actions per
emitter.  The PBW-filtered infinitesimal Berger-U(1) generator has rank 404
on 528 raw order-one/two monomials and hence a 124-dimensional kernel; four
independent order-zero profile-jet directions complete the class.  Every q2
column is the Euler Hessian of one serialized action.

The class is obstructed for both source-labelled emitters.  It contributes
quotient rank 28 over the terminal rank-2613 image.  The full action rank is
2641 and the source-augmented rank is 2642.  All 42 canonical source
coordinates survive, beginning at

\\[
A^+_0\\leftarrow(\\tau,e_0e_1K_{b,01})=-3g_bh_b.
\\]

This is a finite filtered-second-jet obstruction, not a universal no-go.  The
least unexcluded derivative enlargement is the complete filtered third-jet
module on the same cone.  Because arity two remains obstructed, K_Berger,
raw-D, q3 and every observer or quantum gate are not evaluated.
"""


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
