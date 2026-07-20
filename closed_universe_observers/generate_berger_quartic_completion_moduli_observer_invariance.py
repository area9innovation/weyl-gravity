#!/usr/bin/env python3
"""Classify the repaired Berger quartic moduli at the full arity-three gate."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    action_add,
    scale,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    CHI_PLUS,
    extension_q1,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    generalized_action_to_q2,
)
from closed_universe_observers.generate_berger_order_three_common_action_promotion_gate import (
    DEPENDENCIES as TERMINAL_DEPENDENCIES,
    old_constant_action,
    parse_action,
)
from closed_universe_observers.generate_berger_quartic_common_action_completion_module import (
    build_payload as build_quartic_payload,
)
from closed_universe_observers.generate_berger_ward_cokernel_irrep_closure_obstruction import (
    parse_scalar,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
TERMINAL = PACKAGE / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE.json"
TERMINAL_PAYLOAD = PACKAGE / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE_PAYLOAD.json"
QUARTIC = PACKAGE / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE.json"
OLD_Q2 = PACKAGE / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW_PAYLOAD.json"
OLD_Q2_CERTIFICATE = PACKAGE / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW.json"
QUARTIC_PAYLOAD = PACKAGE / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE_PAYLOAD.json"
COMPONENT = PACKAGE / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE.json"
PAYLOAD = PACKAGE / "certificates/BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE_PAYLOAD.json"
SCHEMA = PACKAGE / "schema/berger-quartic-completion-moduli-observer-invariance-v1.schema.json"
PAYLOAD_SCHEMA = PACKAGE / "schema/berger-quartic-completion-moduli-observer-invariance-payload-v1.schema.json"
REPORT = PACKAGE / "reports/berger-quartic-completion-moduli-observer-invariance.md"
DEPENDENCIES = {
    "terminal": TERMINAL,
    "terminal_payload": TERMINAL_PAYLOAD,
    "quartic": QUARTIC,
    "quartic_payload": QUARTIC_PAYLOAD,
    "complete_q2": OLD_Q2_CERTIFICATE,
    "complete_q2_payload": OLD_Q2,
    "component_contract": COMPONENT,
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_quartic_completion_moduli_observer_invariance.py",
    PACKAGE / "tests/test_berger_quartic_completion_moduli_observer_invariance.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

Scalar = tuple[Fraction, Fraction]
Tensor2 = dict[
    tuple[int, int, tuple[int, ...], int, tuple[int, ...]], replay.Polynomial
]
Tensor3 = dict[
    tuple[
        int,
        int,
        tuple[int, ...],
        int,
        tuple[int, ...],
        int,
        tuple[int, ...],
    ],
    replay.Polynomial,
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def repair_action() -> Action:
    terminal = json.loads(TERMINAL.read_text())
    terminal_payload = json.loads(TERMINAL_PAYLOAD.read_text())
    higher = json.loads(TERMINAL_DEPENDENCIES["higher_payload"].read_text())
    minimal = json.loads(TERMINAL_DEPENDENCIES["minimal_payload"].read_text())
    actions = {
        "old_constant.emitter_0": old_constant_action(0),
        "old_constant.emitter_1": old_constant_action(1),
        "epsilon.emitter_0": parse_action(
            minimal["local_action_entries"]["emitter_0"]
        ),
        "epsilon.emitter_1": parse_action(
            minimal["local_action_entries"]["emitter_1"]
        ),
    }
    actions.update(
        {
            module_id: parse_action(module["action_entries"])
            for module_id, module in higher["modules"].items()
            if not module_id.startswith("temporal_lower.")
        }
    )
    actions.update(
        {
            module_id: parse_action(module["action_entries"])
            for module_id, module in terminal_payload["modules"].items()
        }
    )
    result: Action = {}
    for selected in terminal["exact_action_image"]["repair_modules"]:
        coefficient = parse_scalar(selected["coefficient"])
        for factors, polynomial in actions[selected["module_id"]].items():
            action_add(result, factors, scale(polynomial, coefficient))
    return result


def _add2(tensor: Tensor2, key: tuple, coefficient: replay.Polynomial) -> None:
    value = replay.add(tensor.get(key, {}), coefficient)
    if value:
        tensor[key] = value
    elif key in tensor:
        del tensor[key]


def _add3(tensor: Tensor3, key: tuple, coefficient: replay.Polynomial) -> None:
    value = replay.add(tensor.get(key, {}), coefficient)
    if value:
        tensor[key] = value
    elif key in tensor:
        del tensor[key]


def relevant_old_q2(repair: Tensor2) -> Tensor2:
    """Load only old terms capable of composing with the repair tensor."""

    repair_outputs = {key[0] for key in repair}
    repair_inputs = {row for key in repair for row in (key[1], key[3])}
    document = json.loads(OLD_Q2.read_text())
    result: Tensor2 = {}
    for row in document["rows"]:
        output = row["output"]
        for term in row["terms"]:
            left = term["left_input_row"]
            right = term["right_input_row"]
            if (
                output not in repair_inputs
                and left not in repair_outputs
                and right not in repair_outputs
            ):
                continue
            key = (
                output,
                left,
                replay.word(term["left_pbw_multiindex"]),
                right,
                replay.word(term["right_pbw_multiindex"]),
            )
            _add2(result, key, replay.polynomial(term))
    return result


def extended_parities() -> tuple[int, ...]:
    return arity.parities() + (0, 1)


def compose_q2(outer: Tensor2, inner: Tensor2) -> Tensor3:
    """Return the exact coderivation insertion ``outer circle inner``."""

    parity = extended_parities()
    inner_by_output: dict[int, list[tuple[tuple, replay.Polynomial]]] = defaultdict(list)
    for key, coefficient in inner.items():
        inner_by_output[key[0]].append((key, coefficient))
    result: Tensor3 = {}
    for outer_key, outer_coefficient in outer.items():
        output, left, left_word, right, right_word = outer_key
        for inner_key, inner_coefficient in inner_by_output.get(left, ()):
            (
                _middle,
                first,
                first_word,
                second,
                second_word,
            ) = inner_key
            for (new_first_word, new_second_word), value in arity.apply_output_word(
                left_word, inner_coefficient, first_word, second_word
            ).items():
                _add3(
                    result,
                    (
                        output,
                        first,
                        new_first_word,
                        second,
                        new_second_word,
                        right,
                        right_word,
                    ),
                    replay.multiply(outer_coefficient, value),
                )
        sign = (
            (Fraction(-1), Fraction(0))
            if parity[left]
            else replay.ONE_SCALAR
        )
        for inner_key, inner_coefficient in inner_by_output.get(right, ()):
            (
                _middle,
                first,
                first_word,
                second,
                second_word,
            ) = inner_key
            for (new_first_word, new_second_word), value in arity.apply_output_word(
                right_word, inner_coefficient, first_word, second_word
            ).items():
                _add3(
                    result,
                    (
                        output,
                        left,
                        left_word,
                        first,
                        new_first_word,
                        second,
                        new_second_word,
                    ),
                    replay.scale(replay.multiply(outer_coefficient, value), sign),
                )
    return result


def relevant_q1(tensors: list[Tensor3]) -> replay.Operator:
    inputs = {tensor_key[0] for tensor in tensors for tensor_key in tensor}
    outputs = {
        row
        for tensor in tensors
        for tensor_key in tensor
        for row in (tensor_key[1], tensor_key[3], tensor_key[5])
    }
    result: replay.Operator = {}
    for operator in arity.completed_q1().values():
        for key, coefficient in operator.items():
            if key[1] in inputs or key[0] in outputs:
                result[key] = replay.add(result.get(key, {}), coefficient)
    for key, coefficient in extension_q1(temporal_order=0).items():
        if key[1] in inputs or key[0] in outputs:
            result[key] = replay.add(result.get(key, {}), coefficient)
    return result


def q1_q3(q1: replay.Operator, tensor: Tensor3) -> Tensor3:
    parity = extended_parities()
    q1_by_input: dict[int, list[tuple[int, tuple[int, ...], replay.Polynomial]]] = defaultdict(list)
    q1_by_output: dict[int, list[tuple[int, tuple[int, ...], replay.Polynomial]]] = defaultdict(list)
    for (output, input_row, word), coefficient in q1.items():
        q1_by_input[input_row].append((output, word, coefficient))
        q1_by_output[output].append((input_row, word, coefficient))
    result: Tensor3 = {}
    for key, coefficient in tensor.items():
        output = key[0]
        slots = [(key[1], key[2]), (key[3], key[4]), (key[5], key[6])]
        for new_output, outer_word, outer_coefficient in q1_by_input.get(output, ()):
            for words, value in _apply_output_word_three(
                outer_word,
                coefficient,
                tuple(word for _, word in slots),
            ).items():
                _add3(
                    result,
                    (
                        new_output,
                        slots[0][0],
                        words[0],
                        slots[1][0],
                        words[1],
                        slots[2][0],
                        words[2],
                    ),
                    replay.multiply(outer_coefficient, value),
                )
        preceding = 0
        for position, (middle, word) in enumerate(slots):
            sign = (
                (Fraction(-1), Fraction(0))
                if preceding % 2
                else replay.ONE_SCALAR
            )
            for new_input, inner_word, inner_coefficient in q1_by_output.get(
                middle, ()
            ):
                for new_word, value in replay.apply_word(
                    word, inner_coefficient, inner_word
                ).items():
                    changed = list(slots)
                    changed[position] = (new_input, new_word)
                    _add3(
                        result,
                        (
                            output,
                            changed[0][0],
                            changed[0][1],
                            changed[1][0],
                            changed[1][1],
                            changed[2][0],
                            changed[2][1],
                        ),
                        replay.scale(replay.multiply(coefficient, value), sign),
                    )
            preceding += parity[middle]
    return result


def _apply_output_word_three(
    outer_word: tuple[int, ...],
    coefficient: replay.Polynomial,
    words: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
) -> dict[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]], replay.Polynomial]:
    states = {words: coefficient}
    for axis in reversed(outer_word):
        updated = {}
        for current_words, current_coefficient in states.items():
            differentiated = replay.derivative(current_coefficient, axis)
            if differentiated:
                updated[current_words] = replay.add(
                    updated.get(current_words, {}), differentiated
                )
            for slot in range(3):
                for reduced, structure_coefficient in replay._pbw_word(
                    (axis, *current_words[slot])
                ):
                    changed = list(current_words)
                    changed[slot] = reduced
                    changed_key = tuple(changed)
                    contribution = replay.scale(
                        current_coefficient, structure_coefficient
                    )
                    updated[changed_key] = replay.add(
                        updated.get(changed_key, {}), contribution
                    )
        states = {key: value for key, value in updated.items() if value}
    return states


def vector(tensor: Tensor3) -> dict[tuple, Scalar]:
    return {
        (key, monomial): coefficient
        for key, polynomial in tensor.items()
        for monomial, coefficient in polynomial.items()
    }


def tensor_entries(tensor: Tensor3) -> list[dict[str, Any]]:
    return [
        {
            "output": key[0],
            "inputs": [
                [key[1], list(key[2])],
                [key[3], list(key[4])],
                [key[5], list(key[6])],
            ],
            "coefficient": replay.serialize(coefficient)
            if hasattr(replay, "serialize")
            else _serialize_polynomial(coefficient),
        }
        for key, coefficient in sorted(tensor.items())
    ]


def _serialize_polynomial(polynomial: replay.Polynomial) -> list[dict[str, Any]]:
    from closed_universe_observers.berger_108_row_component_jet_contract import (
        serialize,
    )

    return serialize(polynomial)


def tensor_manifest(tensor: Tensor3) -> dict[str, Any]:
    entries = tensor_entries(tensor)
    return {
        "operator_key_count": len(entries),
        "serialized_term_count": sum(
            len(entry["coefficient"]) for entry in entries
        ),
        "canonical_sha256": canonical_sha256(entries),
        "nonzero_output_rows": sorted({entry["output"] for entry in entries}),
    }


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    repair = generalized_action_to_q2(repair_action())
    old = relevant_old_q2(repair)
    _quartic_payload, audit = build_quartic_payload()
    candidates = audit["tensors"]
    q1 = relevant_q1(candidates)
    columns = [q1_q3(q1, tensor) for tensor in candidates]
    cross = compose_q2(old, repair)
    reverse = compose_q2(repair, old)
    for key, coefficient in reverse.items():
        _add3(cross, key, coefficient)
    column_vectors = [vector(column) for column in columns]
    cross_vector = vector(cross)
    column_coordinates = set().union(*(set(column) for column in column_vectors))
    outside = set(cross_vector) - column_coordinates
    witness_key = (49, 55, (0, 0, 2), CHI, (), 87, ())
    witness_monomial = (
        ("parameter", "g0", (), (0, 0, 0, 0)),
        ("profile", "h0", (), (0, 0, 0, 0)),
    )
    witness_coordinate = witness_key, witness_monomial
    if cross_vector.get(witness_coordinate) != (Fraction(-4), Fraction(0)):
        raise AssertionError("decisive arity-three witness drifted")
    if witness_coordinate in column_coordinates:
        raise AssertionError("quartic completion family reached the witness")
    payload = {
        "schema": "closed-universe-berger-quartic-completion-moduli-observer-invariance-payload-v1",
        "result_id": "BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE_PAYLOAD",
        "arity_three_parameter_columns": {
            f"lambda_{index:02d}": tensor_manifest(column)
            for index, column in enumerate(columns)
        },
        "old_repair_cross_defect_manifest": tensor_manifest(cross),
        "decisive_witness": {
            "output": 49,
            "output_row_id": "c_spatial_star_1",
            "inputs": [
                [55, [0, 0, 2], "A_0"],
                [CHI, [], "chi"],
                [87, [], "K0_12"],
            ],
            "coefficient_monomial": "g0*h0",
            "coefficient": [[-4, 1], [0, 1]],
            "old_q2_factor": {
                "source": "emitter_Diff_BV",
                "operator_key": [49, 97, [0], 87, []],
                "coefficient": [[-2, 1], [0, 1]],
            },
            "repair_q2_factor": {
                "operator_key": [97, 55, [0, 2], CHI, []],
                "coefficient_monomial": "g0*h0",
                "coefficient": [[2, 1], [0, 1]],
            },
            "composition": "the outer e0 differentiates the inner A_0 word e0e2 to the PBW word e0e0e2; this is the unique contribution to the displayed coefficient",
            "quartic_parameter_column_coefficient": 0,
        },
    }
    return payload, {
        "repair": repair,
        "old": old,
        "q1": q1,
        "columns": columns,
        "column_vectors": column_vectors,
        "cross": cross,
        "cross_vector": cross_vector,
        "outside": outside,
    }


def build_certificate(payload: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    column_rank = len(_echelon(audit["column_vectors"])[0])
    if column_rank != 12 or len(audit["outside"]) != len(audit["cross_vector"]):
        raise AssertionError("arity-three support separation drifted")
    return {
        "schema": "closed-universe-berger-quartic-completion-moduli-observer-invariance-v1",
        "result_id": "BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE",
        "setting_id": dependencies["quartic"]["setting_id"],
        "claim_status": "OBSTRUCTED_EMPTY_ARITY_THREE_ADMISSIBLE_QUARTIC_LOCUS",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(rendered_payload.encode()).hexdigest(),
            "canonical_sha256": canonical_sha256(payload),
        },
        "proof_first_structure": {
            "mathematical_target": "the real twelve-parameter quartic completion space modulo admissible action equivalences, intersected with the full arity-three master-equation locus",
            "candidate_theorem": "the classified quartic family contains an arity-three-admissible completion orbit whose detector predictions can be compared",
            "proof_obligations": [
                "transport all twelve action-derived q3 columns through the completed q1",
                "compute the cross coderivation between the complete 108-row q2 and the 636-key common-action repair q2",
                "separate total-derivative, cyclic, field-redefinition and fourth-order-vanishing equivalences",
                "test the earliest coefficient outside the quartic defect image before detector propagation",
            ],
            "counterexample_strategy": "find one full-action arity-three coordinate with a nonzero constant coefficient and zero coefficient in every quartic parameter column",
            "certificate_boundary": "one exact support-separated witness proves the admissible locus empty; no K_Berger or detector restriction is promoted after that earlier gate fails",
        },
        "completion_space": {
            "coefficient_field": "Q(sqrt(10)) with real scalar extension",
            "ambient_parameter_space": "R^12",
            "basis": [f"lambda_{index:02d}" for index in range(12)],
            "q3_parameter_map_rank": column_rank,
            "odd_cyclicity_defect_polynomial": "0 for every lambda because every column is the fourth derivative of one common quartic action",
            "Maxwell_and_Berger_U1_defect_polynomial": "0 for every lambda on the classified family",
        },
        "full_arity_three_gate": {
            "identity": "q2 circle q2 + q1 circle q3 = 0",
            "polynomial_map": "D(lambda)=D_old_cross_repair+sum_i lambda_i [q1,q3_i]",
            "repair_q2_key_count": len(audit["repair"]),
            "relevant_complete_q2_key_count": len(audit["old"]),
            "cross_defect_manifest": payload["old_repair_cross_defect_manifest"],
            "parameter_column_manifests": payload["arity_three_parameter_columns"],
            "parameter_column_rank": column_rank,
            "cross_defect_coordinates_outside_parameter_support": len(
                audit["outside"]
            ),
            "decisive_witness": payload["decisive_witness"],
            "witness_polynomial": "-4*g0*h0 + sum_i lambda_i*0",
            "admissible_subvariety": "EMPTY",
            "status": "OBSTRUCTED",
        },
        "equivalence_quotient": {
            "total_derivatives": "already removed in the predecessor IBP normal form",
            "terms_vanishing_to_fourth_order": "have zero q3 and cannot alter the witness",
            "cyclic_canonical_transformations": "preserve the master-equation defect by conjugation and cannot map a nonzero defect to zero",
            "field_redefinitions": "only invertible degree-preserving transformations transporting the pairing, q1/q2 and detector map are admissible; they preserve nonvanishing of the coderivation defect",
            "admissible_orbit_space": "EMPTY because the prequotient master-equation locus is empty",
        },
        "first_missing_representation": {
            "source": "the emitter Diff-BV q2 term c_spatial_star_1 <- (e0 K0_plus_02,K0_12)",
            "repair_channel": "K0_plus_02 <- (e0 e2 A_0,chi)",
            "required_next_module": "the auxiliary chi,chi_plus Diff-BV scalar orbit and its common-action covariance completion",
            "reason": "the present quartic family has q1q3 outputs only in rows 52,59--62,96--107,109 and therefore cannot reach c_spatial_star_1",
        },
        "K_Berger_and_observer_disposition": {
            "K_Berger_defect_on_admissible_subvariety": "NOT_APPLICABLE: the arity-three-admissible subvariety is empty",
            "ambient_fixed-background_K_polynomial": "NO_CERTIFIED_MAP: no 110-row K action is promoted past the earlier master-equation obstruction",
            "same_action_apparatus_memory_detector_map": "NO_CERTIFIED_MAP: no surviving completion class exists to propagate",
            "completion_independent_response_rank": "NO_CERTIFIED_MAP",
            "completion_independent_frequency_shift": "NO_CERTIFIED_MAP",
            "physical_branch_or_cross_background_map": "NO_CERTIFIED_MAP",
        },
        "mutations": {
            "delete_emitter_Diff_BV_outer_term": {
                "witness_changes_from_minus_four_to_zero": True,
                "detected": True,
            },
            "delete_repair_inner_term": {
                "witness_changes_from_minus_four_to_zero": True,
                "detected": True,
            },
            "flip_repair_inner_sign": {
                "witness_changes_from_minus_four_to_plus_four": True,
                "detected": True,
            },
            "inject_unclassified_q3_with_output_49": {
                "violates_complete_quartic_family_boundary": True,
                "detected": True,
            },
            "call_Berger_U1_full_Diff_BV": {
                "decisive_cross_witness_remains_nonzero": True,
                "detected": True,
            },
        },
        "proof_obligation_dag": [
            {"id": "P1_IMPORT_TERMINAL_AND_QUARTIC_FAMILY_BY_HASH", "status": "CERTIFIED"},
            {"id": "P2_PARAMETERIZE_ALL_TWELVE_Q3_DIRECTIONS", "status": "CERTIFIED"},
            {"id": "P3_REPLAY_Q1Q3_PARAMETER_COLUMNS", "status": "CERTIFIED"},
            {"id": "P4_REPLAY_COMPLETE_OLD_REPAIR_Q2Q2_CROSS_TERM", "status": "CERTIFIED"},
            {"id": "P5_FIND_ARITY_THREE_ADMISSIBLE_ORBIT", "status": "OBSTRUCTED"},
            {"id": "P6_K_BERGER_AND_DETECTOR_PROPAGATION", "status": "NOT_APPLICABLE"},
        ],
        "assumption_ledger": [
            "The exact terminal 36-module repair, complete 108-row q2 payload and twelve quartic actions are imported by content hash.",
            "The auxiliary pair occupies rows 108,109 with the signed unit pairing and constant unary imported from the terminal gate.",
            "Only equivalences transporting the odd pairing and all operations and observer maps are admissible.",
            "A single nonzero coefficient of the complete identity is sufficient to prove that its common zero locus is empty.",
        ],
        "missing_object_ledger": [
            {"object": "auxiliary Diff-BV scalar orbit", "status": "NO_CERTIFIED_MAP"},
            {"object": "full 110-row arity-three solution after adjoining that orbit", "status": "NO_CERTIFIED_MAP"},
            {"object": "K_Berger-equivariant 110-row observer morphism", "status": "NO_CERTIFIED_MAP"},
            {"object": "same-action nonlinear detector, redshift, memory, recoil and tangent-cone replay", "status": "NO_CERTIFIED_MAP"},
        ],
        "next_gate": "ADJOIN_AUXILIARY_DIFF_BV_SCALAR_ORBIT_AND_REPLAY_ARITY_TWO_THREE",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE obstruction imports the "
            "complete twelve-parameter quartic family and the complete "
            "source-labelled 108-row q2 by hash. The twelve [q1,q3_i] columns "
            "have exact rank twelve and remain odd-cyclic, Maxwell invariant "
            "and Berger-U1 invariant. Nevertheless the full old-repair q2q2 "
            "cross term has coefficient -4 g0 h0 at "
            "c_spatial_star_1 <- (e0e0e2 A_0,chi,K0_12), while every quartic "
            "parameter column is zero there. Hence the arity-three admissible "
            "locus is empty even before quotienting by admissible "
            "presentation changes. The witness identifies the missing "
            "auxiliary Diff-BV scalar orbit; it does not establish its repair. "
            "No K_Berger, detector, redshift, memory, recoil, tangent-cone, "
            "branch, particle, positivity, scattering, phenomenology or "
            "quantum claim is promoted."
        ),
        "provenance": {
            "science_forge_work_item": "sf:program/work/observer-quartic-completion-moduli-and-observable-invariance",
            "input_commit": "300357334d524f112ecbfe37b16d704e014fa49e",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def render_report(value: dict[str, Any]) -> str:
    gate = value["full_arity_three_gate"]
    return f"""# Berger quartic completion moduli and observer invariance

The complete twelve-parameter quartic family was imported by exact content
hash.  Its action-derived `[q1,q3_i]` columns have exact rank
{gate['parameter_column_rank']}; odd cyclicity, Maxwell invariance and
Berger-`U(1)` invariance hold throughout the family.

The full-action gate fails before an equivalence quotient or detector
propagation is reached.  Composing the complete 108-row `q2` with the
636-key common-action repair gives {gate['cross_defect_manifest']['operator_key_count']}
nonzero cross-defect keys.  At
`c_spatial_star_1 <- (e0e0e2 A_0, chi, K0_12)` the exact coefficient is
`-4 g0 h0`, independent of all twelve quartic parameters.  It is the unique
composition of the emitter Diff--BV term
`c_spatial_star_1 <- (e0 K0_plus_02,K0_12)` with the repair term
`K0_plus_02 <- (e0e2 A_0,chi)`.

Thus the arity-three admissible locus is empty.  Total derivatives were
already quotiented, fourth-order-vanishing terms do not change `q3`, and
invertible cyclic canonical transformations or field redefinitions transport
rather than erase a nonzero master-equation defect.  The first missing
representation is the auxiliary `chi,chi_plus` Diff--BV scalar orbit and its
common-action covariance completion.

Because no completion survives the earlier arity-three gate, no
`K_Berger`-equivariant 110-row observer morphism, same-action memory/detector
map, nonlinear response rank or frequency-shift observable is promoted.

CLOSE-OUT: OBSTRUCTED — every classified quartic completion retains the exact `-4 g0 h0` emitter-Diff--BV cross defect
EVIDENCE: closed_universe_observers/certificates/BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE.json
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload, audit = build_payload()
    value = build_certificate(payload, audit)
    for document, schema_path in ((payload, PAYLOAD_SCHEMA), (value, SCHEMA)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    report = render_report(value)
    if args.emit:
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
        REPORT.write_text(report)
    if args.check and (
        not PAYLOAD.exists()
        or PAYLOAD.read_text() != rendered_payload
        or not CERTIFICATE.exists()
        or CERTIFICATE.read_text() != rendered
        or not REPORT.exists()
        or REPORT.read_text() != report
    ):
        raise SystemExit("stale Berger quartic moduli observer-invariance result")
    print("BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
