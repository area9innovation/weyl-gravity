#!/usr/bin/env python3
"""Classify the minimal quartic completions of the repaired Berger action."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import serialize
from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import (
    Action,
    action_add,
    scale,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    _dual_and_sign,
)
from closed_universe_observers.generate_berger_common_action_obstruction_module import (
    _echelon,
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    _scalar,
    _sympy_scalar,
    invariant_action_basis,
    local_action,
)
from closed_universe_observers.generate_berger_minimal_invariant_scalar_hessian_channel_no_go import (
    _action_entries,
)
from closed_universe_observers.generate_berger_order_three_common_action_promotion_gate import (
    maxwell_gauge_variation,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE.json"
PAYLOAD = PACKAGE / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE_PAYLOAD.json"
SCHEMA = PACKAGE / "schema/berger-quartic-common-action-completion-module-v1.schema.json"
PAYLOAD_SCHEMA = PACKAGE / "schema/berger-quartic-common-action-completion-module-payload-v1.schema.json"
REPORT = PACKAGE / "reports/berger-quartic-common-action-completion-module.md"
DEPENDENCIES = {
    "terminal": PACKAGE / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE.json",
    "terminal_payload": PACKAGE / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE_PAYLOAD.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_quartic_common_action_completion_module.py",
    PACKAGE / "tests/test_berger_quartic_common_action_completion_module.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

Scalar = tuple[Fraction, Fraction]
Tensor3 = dict[tuple[int, int, tuple[int, ...], int, tuple[int, ...], int, tuple[int, ...]], replay.Polynomial]
ZERO: Scalar = (Fraction(0), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _add_three(
    tensor: Tensor3,
    output: int,
    slots: tuple[tuple[int, tuple[int, ...]], ...],
    coefficient: replay.Polynomial,
) -> None:
    for order in itertools.permutations(range(3)):
        permuted = tuple(slots[index] for index in order)
        key = (
            output,
            permuted[0][0],
            permuted[0][1],
            permuted[1][0],
            permuted[1][1],
            permuted[2][0],
            permuted[2][1],
        )
        tensor[key] = replay.add(tensor.get(key, {}), coefficient)
        if not tensor[key]:
            del tensor[key]


def apply_output_word_three(
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
                    key = tuple(changed)
                    contribution = replay.scale(
                        current_coefficient, structure_coefficient
                    )
                    updated[key] = replay.add(updated.get(key, {}), contribution)
        states = {key: value for key, value in updated.items() if value}
    return states


def action_to_q3(action: Action) -> Tensor3:
    tensor: Tensor3 = {}
    for factors, coefficient in action.items():
        if len(factors) != 4:
            raise AssertionError("quartic action arity drifted")
        for position, varied in enumerate(factors):
            remaining = list(factors)
            remaining.pop(position)
            dual, pairing_sign = _dual_and_sign(varied[0])
            if not varied[1]:
                _add_three(
                    tensor,
                    dual,
                    tuple(remaining),
                    replay.scale(coefficient, (Fraction(pairing_sign), Fraction(0))),
                )
                continue
            sign = pairing_sign * (-1) ** len(varied[1])
            expansion = apply_output_word_three(
                tuple(reversed(varied[1])),
                coefficient,
                tuple(word for _, word in remaining),
            )
            for words, expanded in expansion.items():
                slots = tuple(
                    (remaining[index][0], words[index]) for index in range(3)
                )
                _add_three(
                    tensor,
                    dual,
                    slots,
                    replay.scale(expanded, (Fraction(sign), Fraction(0))),
                )
    return tensor


def q3_entries(tensor: Tensor3) -> list[dict[str, Any]]:
    return [
        {
            "output": key[0],
            "inputs": [
                [key[1], list(key[2])],
                [key[3], list(key[4])],
                [key[5], list(key[6])],
            ],
            "coefficient": serialize(coefficient),
        }
        for key, coefficient in sorted(tensor.items())
    ]


def q3_manifest(tensor: Tensor3) -> dict[str, Any]:
    entries = q3_entries(tensor)
    return {
        "key_count": len(entries),
        "canonical_sha256": canonical_sha256(entries),
    }


def quartic_from_cubic(cubic: Action) -> Action:
    quartic: Action = {}
    for factors, coefficient in cubic.items():
        action_add(
            quartic,
            ((CHI, ()),) + factors,
            scale(coefficient, (Fraction(1, 2), Fraction(0))),
        )
    return quartic


def gauge_invariant_basis(emitter: int) -> tuple[list[Action], dict[str, Any]]:
    invariant, classification = invariant_action_basis(emitter, 1)
    base = 84 + 6 * emitter
    k_has_two = {
        base: False,
        base + 1: True,
        base + 2: False,
        base + 3: True,
        base + 4: False,
        base + 5: True,
    }
    invariant_parities = []
    for _, terms in invariant:
        parities = {
            (int(k_has_two[krow]) + int(arow == 57) + word.count(2)) % 2
            for krow, arow, word, _ in terms
        }
        if len(parities) != 1:
            raise AssertionError("U1 basis lost reflection homogeneity")
        invariant_parities.append(parities.pop())
    cubic_actions = [local_action(emitter, terms, profile_jet=0) for _, terms in invariant]
    variations = [maxwell_gauge_variation(action) for action in cubic_actions]
    coordinates = sorted(set().union(*(set(vector) for vector in variations)))
    index = {coordinate: position for position, coordinate in enumerate(coordinates)}
    matrix = sp.zeros(len(coordinates), len(variations))
    for column, vector in enumerate(variations):
        for coordinate, coefficient in vector.items():
            matrix[index[coordinate], column] = _sympy_scalar(coefficient)
    nullspace = matrix.nullspace()
    actions = []
    supports = []
    reflection_dimensions = {"reflection_even": 0, "reflection_odd": 0}
    for vector in nullspace:
        cubic: Action = {}
        support = []
        support_parities = set()
        for position, coefficient in enumerate(vector):
            if not coefficient:
                continue
            support_parities.add(invariant_parities[position])
            scalar = _scalar(coefficient)
            support.append(
                {
                    "invariant_basis_id": invariant[position][0],
                    "coefficient": [
                        [scalar[0].numerator, scalar[0].denominator],
                        [scalar[1].numerator, scalar[1].denominator],
                    ],
                }
            )
            for factors, polynomial in cubic_actions[position].items():
                action_add(cubic, factors, scale(polynomial, scalar))
        if maxwell_gauge_variation(cubic):
            raise AssertionError("Maxwell kernel basis drifted")
        if len(support_parities) != 1:
            raise AssertionError("Maxwell kernel basis mixes reflection parity")
        reflection_dimensions[
            "reflection_odd" if support_parities.pop() else "reflection_even"
        ] += 1
        actions.append(quartic_from_cubic(cubic))
        supports.append(support)
    if len(actions) != 6 or matrix.rank() != 22:
        raise AssertionError("minimal quartic Maxwell kernel drifted")
    return actions, {
        "emitter": emitter,
        "raw_K_DA_dimension": 96,
        "Berger_U1_invariant_dimension": classification["invariant_dimension"],
        "Maxwell_gauge_variation_rank": matrix.rank(),
        "Maxwell_and_U1_invariant_dimension": len(actions),
        "Maxwell_kernel_reflection_dimensions": reflection_dimensions,
        "kernel_supports": supports,
    }


def _tensor_vector(tensor: Tensor3) -> dict[tuple, Scalar]:
    return {
        (key, monomial): coefficient
        for key, polynomial in tensor.items()
        for monomial, coefficient in polynomial.items()
    }


def _rank(columns: list[dict]) -> int:
    return len(_echelon(columns)[0])


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    modules = {}
    classifications = []
    tensors = []
    for emitter in (0, 1):
        actions, classification = gauge_invariant_basis(emitter)
        classifications.append(classification)
        for position, action in enumerate(actions):
            module_id = f"quartic.emitter_{emitter}.basis_{position:02d}"
            tensor = action_to_q3(action)
            tensors.append(tensor)
            modules[module_id] = {
                "emitter": emitter,
                "action_entries": _action_entries(action),
                "q3_manifest": q3_manifest(tensor),
                "q3_entries": q3_entries(tensor),
            }
    if _rank([_tensor_vector(tensor) for tensor in tensors]) != 12:
        raise AssertionError("quartic q3 family lost independence")
    payload = {
        "schema": "closed-universe-berger-quartic-common-action-completion-module-payload-v1",
        "result_id": "BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE_PAYLOAD",
        "classifications": classifications,
        "modules": modules,
    }
    return payload, {"tensors": tensors}


def build_certificate(payload: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    terminal = values["terminal"]
    if sha256(DEPENDENCIES["terminal"]) != "a4dbe49924d494efcb866e8d2b98fc1dfd76ebad634bc87d94f895c389cf16f9":
        raise AssertionError("terminal certificate hash drifted")
    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    manifests = [module["q3_manifest"] for module in payload["modules"].values()]
    return {
        "schema": "closed-universe-berger-quartic-common-action-completion-module-v1",
        "result_id": "BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE",
        "setting_id": terminal["setting_id"],
        "claim_status": "OBSTRUCTED_TWELVE_PARAMETER_QUARTIC_Q3_COMPLETION_FAMILY",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
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
        "imported_terminal_disposition": {
            "typed_source_q1_q2_repaired": terminal["exact_action_image"]["typed_source_in_image"],
            "repair_module_count": terminal["exact_action_image"]["repair_module_count"],
            "repair_q2_manifest": terminal["exact_action_image"]["repair_q2_manifest"],
            "unique_q3": False,
            "terminal_next_gate": terminal["next_gate"],
        },
        "minimal_quartic_ansatz": {
            "action": "(1/2) chi^2 g_b h_b K_b,ab e_c A_d",
            "field_arity": 4,
            "total_differential_order": 1,
            "auxiliary_power": 2,
            "coefficient_grade": "undecorated g_b h_b",
            "both_emitters": True,
            "both_reflection_parities": True,
            "pairing": "same signed odd pairing as the terminal common-action repair",
            "background": "same pinned positive Berger clock",
        },
        "module_classification": payload["classifications"],
        "action_derived_operations": {
            "module_count": len(payload["modules"]),
            "q1_variation_at_zero_auxiliary_background": 0,
            "q2_variation_at_zero_auxiliary_background": 0,
            "q3_module_rank": _rank([_tensor_vector(tensor) for tensor in audit["tensors"]]),
            "q3_key_count_by_module": [manifest["key_count"] for manifest in manifests],
            "odd_cyclicity": "CERTIFIED_BY_COMMON_QUARTIC_ACTION",
            "Berger_U1_equivariance": "CERTIFIED_EXACT",
            "Maxwell_gauge_invariance": "CERTIFIED_EXACT",
        },
        "coefficient_selection_obstruction": {
            "completion_parameter_space": "Q(sqrt(10))^12",
            "dimension": 12,
            "q1_q2_constraints_on_parameters": 0,
            "cyclicity_constraints_on_parameters": 0,
            "Berger_U1_constraints_after_classification": 0,
            "Maxwell_constraints_after_classification": 0,
            "unique_q3_selected": False,
            "zero_and_each_basis_completion_share_terminal_q1_q2": True,
            "zero_and_each_basis_completion_have_distinct_q3": True,
            "theorem": (
                "The complete smallest quartic completion module consists of "
                "six independent Maxwell-gauge and Berger-invariant actions "
                "per emitter. All twelve leave the repaired q1/q2 unchanged "
                "at the zero auxiliary background and give independent cyclic "
                "q3 columns. Hence the terminal data select no unique q3."
            ),
        },
        "proof_obligation_dag": [
            {"id": "P1_IMPORT_TERMINAL_GATE_BY_HASH", "status": "CERTIFIED"},
            {"id": "P2_CLASSIFY_COMPLETE_MINIMAL_QUARTIC_U1_KERNEL", "status": "CERTIFIED"},
            {"id": "P3_INTERSECT_MAXWELL_GAUGE_KERNEL", "status": "CERTIFIED"},
            {"id": "P4_DERIVE_ALL_CYCLIC_Q3_COLUMNS", "status": "CERTIFIED"},
            {"id": "P5_SELECT_UNIQUE_SAME_ACTION_Q3", "status": "OBSTRUCTED"},
            {"id": "P6_FULL_ARITY_THREE_AND_OBSERVER_REPLAY", "status": "NO_CERTIFIED_MAP"},
        ],
        "assumption_ledger": [
            "The carrier is the same pinned positive Berger background and signed odd pairing imported from the terminal certificate.",
            "The auxiliary background is chi=0, so a quartic action with two undifferentiated chi factors has zero first and second variation there.",
            "Completeness is scoped to local chi^2 K-dA actions of field arity four, total differential order one and undecorated g_b h_b coefficient grade.",
            "All ranks and kernels are exact over Q(sqrt(10)); no floating-point evidence enters the claim.",
        ],
        "missing_object_ledger": [
            {"object": "full q2q2+q1q3 arity-three identity on the twelve-parameter family", "status": "NO_CERTIFIED_MAP"},
            {"object": "coefficient selection or quotient by cyclic canonical transformations and field redefinitions", "status": "NO_CERTIFIED_MAP"},
            {"object": "K_Berger-equivariant nonlinear observer morphism", "status": "NO_CERTIFIED_MAP"},
            {"object": "same-action detector, memory, redshift, recoil and tangent-cone replay", "status": "NO_CERTIFIED_MAP"},
        ],
        "mutations": {
            "drop_one_Maxwell_kernel_line": {"completeness_dimension_12_to_11": True, "detected": True},
            "flip_antisymmetric_DA_sign": {"Maxwell_gauge_defect_nonzero": True, "detected": True},
            "discard_reflection_odd_lines": {"declared_complete_family_fails": True, "detected": True},
            "set_one_lambda_zero_vs_one": {"same_q1_q2_different_q3": True, "detected": True},
            "import_external_q3": {"same_action_rule_fails": True, "detected": True},
        },
        "activation_disposition": {
            "complete_minimal_quartic_family_constructed": True,
            "unique_same_action_q3_selected": False,
            "full_arity_three_replay_authorized": False,
            "K_Berger_observer_morphism_authorized": False,
            "nonlinear_redshift_or_detector_rank_authorized": False,
            "particle_positivity_quantum_or_phenomenology_authorized": False,
        },
        "next_gate": "COMPUTE_FULL_ARITY_THREE_MASTER_EQUATION_ON_12_PARAMETER_QUARTIC_FAMILY",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result imports the "
            "terminal order-three common-action repair by exact hash and "
            "classifies the smallest same-carrier quartic completion family. "
            "The 96 raw chi^2 K eA monomials per emitter have a 28-dimensional "
            "Berger-U1 invariant subspace; exact Maxwell-gauge variation has "
            "rank 22, leaving six actions per emitter. All twelve serialized "
            "quartic actions use the same odd pairing, are cyclic and "
            "equivariant, leave q1/q2 unchanged at the zero auxiliary "
            "background, and generate twelve independent q3 columns. The "
            "terminal q1/q2 data, cyclicity, U1 and Maxwell invariance impose "
            "no remaining condition on their coefficients. Thus no unique "
            "same-action q3, full arity-three identity, K_Berger descent, "
            "detector/redshift/memory/recoil replay, tangent-cone, branch, "
            "particle, positivity, scattering, phenomenology or quantum "
            "claim is promoted."
        ),
        "provenance": {
            "science_forge_work_item": "sf:program/work/observer-post-common-action-frontier-input-pinned",
            "input_commit": "9fa301059b6b4ada217b455776580d3b5830344b",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def render_report(value: dict[str, Any]) -> str:
    operation = value["action_derived_operations"]
    return f"""# Berger quartic common-action completion module

The complete smallest quartic ansatz is
`(1/2) chi^2 g_b h_b K_b,ab e_c A_d`.  Per emitter its 96 raw monomials
contain 28 Berger-`U(1)` invariants.  Exact Maxwell-gauge variation has rank
22, leaving six invariant actions per emitter.

All twelve quartic actions are serialized and differentiated through the
same signed odd pairing.  They leave the repaired `q1` and `q2` unchanged at
the zero auxiliary background and generate
{operation['q3_module_rank']} independent cyclic `q3` columns.

The existing data do not select their coefficients: cyclicity, Berger
equivariance and Maxwell gauge invariance hold throughout the full
12-parameter family.  A complete `q2q2+q1q3` replay on that family is the
next gate.  Until it is run, no unique same-action `q3` or nonlinear observer
record exists.

CLOSE-OUT: OBSTRUCTED — the complete minimal quartic family gives twelve independent same-q1/q2 cyclic q3 completions, so the current action data do not select a unique nonlinear observer
EVIDENCE: closed_universe_observers/certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE.json
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
    rendered_report = render_report(value)
    if args.emit:
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
        REPORT.write_text(rendered_report)
    if args.check and (
        not PAYLOAD.exists()
        or PAYLOAD.read_text() != rendered_payload
        or not CERTIFICATE.exists()
        or CERTIFICATE.read_text() != rendered
        or not REPORT.exists()
        or REPORT.read_text() != rendered_report
    ):
        raise SystemExit("stale Berger quartic completion module")
    print("BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
