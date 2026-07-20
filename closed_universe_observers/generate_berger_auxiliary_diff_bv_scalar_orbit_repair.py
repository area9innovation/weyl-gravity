#!/usr/bin/env python3
"""Test the complete auxiliary Diff--BV scalar orbit at arities two and three."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import serialize
from closed_universe_observers.generate_berger_108_row_emitter_diff_bv_q2_pbw import (
    FRAME_TO_GHOST,
    GHOST_TO_DUAL,
    adjoint_product_terms,
)
from closed_universe_observers.generate_berger_110_row_conjugate_pair_extension_no_go import (
    CHI,
    CHI_PLUS,
    extension_q1,
)
from closed_universe_observers.generate_berger_higher_jet_invariant_action_module_classification import (
    generalized_action_to_q2,
)
from closed_universe_observers.generate_berger_quartic_completion_moduli_observer_invariance import (
    _add3,
    compose_q2,
    relevant_old_q2,
    repair_action,
    vector,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_AUXILIARY_DIFF_BV_SCALAR_ORBIT_REPAIR.json"
PAYLOAD = PACKAGE / "certificates/BERGER_AUXILIARY_DIFF_BV_SCALAR_ORBIT_REPAIR_PAYLOAD.json"
SCHEMA = PACKAGE / "schema/berger-auxiliary-diff-bv-scalar-orbit-repair-v1.schema.json"
PAYLOAD_SCHEMA = PACKAGE / "schema/berger-auxiliary-diff-bv-scalar-orbit-repair-payload-v1.schema.json"
REPORT = PACKAGE / "reports/berger-auxiliary-diff-bv-scalar-orbit-repair.md"
DEPENDENCIES = {
    "quartic_moduli": PACKAGE / "certificates/BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE.json",
    "quartic_moduli_payload": PACKAGE / "certificates/BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE_PAYLOAD.json",
    "quartic_family": PACKAGE / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE.json",
    "quartic_family_payload": PACKAGE / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE_PAYLOAD.json",
    "terminal_repair": PACKAGE / "certificates/BERGER_ORDER_THREE_COMMON_ACTION_PROMOTION_GATE.json",
    "complete_q2": PACKAGE / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW.json",
    "complete_q2_payload": PACKAGE / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW_PAYLOAD.json",
    "complete_q1": PACKAGE / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "emitter_q1": PACKAGE / "certificates/BERGER_108_ROW_EMITTER_Q1_PBW_OVERLAY.json",
    "emitter_diff_q2": PACKAGE / "certificates/BERGER_108_ROW_EMITTER_DIFF_BV_Q2_PBW.json",
    "component_contract": PACKAGE / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_auxiliary_diff_bv_scalar_orbit_repair.py",
    PACKAGE / "tests/test_berger_auxiliary_diff_bv_scalar_orbit_repair.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
]

Scalar = tuple[Fraction, Fraction]
Tensor2 = dict[
    tuple[int, int, tuple[int, ...], int, tuple[int, ...]], replay.Polynomial
]
Rows2 = dict[int, arity.BilinearRow]
ONE: Scalar = (Fraction(1), Fraction(0))
MINUS_ONE: Scalar = (Fraction(-1), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _add_symmetric(
    tensor: Tensor2,
    output: int,
    left: int,
    left_word: tuple[int, ...],
    right: int,
    right_word: tuple[int, ...],
    coefficient: replay.Polynomial,
) -> None:
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


def scalar_diff_q2(
    *, scale_factor: int | Fraction = 1, axes: Iterable[int] = range(4)
) -> Tensor2:
    """Raise ``scale_factor integral chi_plus c^a e_a chi`` in all slots."""

    coefficient = replay.normalize([((Fraction(scale_factor), Fraction(0)), ())])
    tensor: Tensor2 = {}
    for axis in axes:
        ghost = FRAME_TO_GHOST[axis]
        _add_symmetric(tensor, CHI, ghost, (), CHI, (axis,), coefficient)
        for ghost_word, dual_word, multiplicity in adjoint_product_terms(
            (axis,), (), ()
        ):
            _add_symmetric(
                tensor,
                CHI_PLUS,
                ghost,
                ghost_word,
                CHI_PLUS,
                dual_word,
                replay.scale(
                    coefficient, (Fraction(-multiplicity), Fraction(0))
                ),
            )
        for chi_word, dual_word, multiplicity in adjoint_product_terms(
            (), (axis,), ()
        ):
            _add_symmetric(
                tensor,
                GHOST_TO_DUAL[ghost],
                CHI,
                chi_word,
                CHI_PLUS,
                dual_word,
                replay.scale(
                    coefficient, (Fraction(-multiplicity), Fraction(0))
                ),
            )
    if tuple(axes) == tuple(range(4)) and len(tensor) != 32:
        raise AssertionError("complete scalar Diff--BV orbit drifted")
    return tensor


def tensor_entries(tensor: Tensor2) -> list[dict[str, Any]]:
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


def rows_entries(rows: Rows2) -> list[dict[str, Any]]:
    return [
        {
            "output": output,
            "left_input": [left, list(left_word)],
            "right_input": [right, list(right_word)],
            "coefficient": serialize(coefficient),
        }
        for output, row in sorted(rows.items())
        for (left, left_word, right, right_word), coefficient in sorted(row.items())
    ]


def manifest(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "operator_key_count": len(entries),
        "serialized_term_count": sum(len(entry["coefficient"]) for entry in entries),
        "canonical_sha256": canonical_sha256(entries),
        "nonzero_output_rows": sorted({entry["output"] for entry in entries}),
    }


def _graded_tensor(tensor: Tensor2) -> arity.GradedBilinearRows:
    result: arity.GradedBilinearRows = {
        degree: {} for degree in arity.SUPPORTED_BIDEGREES
    }
    for (output, left, left_word, right, right_word), coefficient in tensor.items():
        arity.add_bilinear_term(
            result[(0, 0)].setdefault(output, {}),
            (left, left_word, right, right_word),
            coefficient,
        )
    return result


def _contractible_coordinates(rows: Rows2) -> Rows2:
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


def contractible_covariance_audit(scalar: Tensor2) -> dict[str, Any]:
    """Isolate the exact block that fixes the scalar-orbit normalization."""

    q1 = {degree: {} for degree in arity.SUPPORTED_BIDEGREES}
    q1[(0, 0)] = extension_q1(temporal_order=0)
    indexed = {degree: arity.q1_rows(operator) for degree, operator in q1.items()}
    parity = arity.parities() + (0, 1)

    def defect(q2: arity.GradedBilinearRows) -> Rows2:
        return _contractible_coordinates(
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

    inherited = defect(arity.load_q2(sources={"base_gravity_clock"}))
    added = defect(_graded_tensor(scalar))
    combined: Rows2 = {}
    for source in (inherited, added):
        for output, row in source.items():
            for key, coefficient in row.items():
                arity.add_bilinear_term(
                    combined.setdefault(output, {}), key, coefficient
                )
    inherited_entries = rows_entries(inherited)
    added_entries = rows_entries(added)
    if (
        len(inherited_entries) != 30
        or len(added_entries) != 30
        or any(combined.values())
    ):
        raise AssertionError("contractible scalar covariance cancellation drifted")
    return {
        "inherited_defect_manifest": manifest(inherited_entries),
        "scalar_orbit_defect_manifest": manifest(added_entries),
        "sum_at_alpha_one": "ZERO",
        "normalization_polynomial": "(alpha-1) B_contractible",
        "normalization_locus": "alpha=1",
        "output_key_counts": {
            str(output): len(row) for output, row in sorted(added.items())
        },
    }


def arity_two_witness_audit(repair: Tensor2, scalar: Tensor2) -> dict[str, Any]:
    """Replay the source-isolated temporal witness independently of q3."""

    q1: replay.GradedOperator = {}
    emitter = json.loads(replay.EMITTER.read_text())["emitter_overlay"]["blocks"]
    replay.load_generic_blocks(q1, emitter)
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
    key = (55, (0, 1), 84, ())
    monomial = (
        ("parameter", "g0", (), (0, 0, 0, 0)),
        ("profile", "h0", (), (0, 0, 0, 0)),
    )
    if specialized[key].get(monomial) != ONE:
        raise AssertionError("temporal arity-two witness drifted")
    repair_chi_plus_key = (CHI_PLUS, 55, (0, 1), 84, ())
    if repair_chi_plus_key in repair:
        raise AssertionError("repair unexpectedly reached the temporal witness")
    if any(
        {left, right} == {55, 84}
        for _output, left, _left_word, right, _right_word in scalar
    ):
        raise AssertionError("scalar Diff orbit unexpectedly reached A--K support")
    return {
        "output": 52,
        "output_row_id": "tau_star",
        "inputs": [[55, [0, 1], "A_0"], [84, [], "K0_01"]],
        "coefficient_monomial": "g0*h0",
        "coefficient": [[1, 1], [0, 1]],
        "source_isolation": {
            "q1": "emitter_q1",
            "q2": "emitter_Diff_BV",
        },
        "scalar_orbit_coefficient": 0,
        "repair_q2_required_key": [CHI_PLUS, 55, [0, 1], 84, []],
        "repair_q2_required_key_present": False,
        "quartic_parameter_coefficient": 0,
        "witness_polynomial": "g0*h0 + alpha*0 + sum_i lambda_i*0",
    }


def bracket(left: Tensor2, right: Tensor2) -> dict:
    result = compose_q2(left, right)
    for key, coefficient in compose_q2(right, left).items():
        _add3(result, key, coefficient)
    return result


def arity_three_audit(repair: Tensor2, scalar: Tensor2) -> dict[str, Any]:
    old = relevant_old_q2(repair)
    old_repair = bracket(old, repair)
    scalar_repair = bracket(scalar, repair)
    monomial = (
        ("parameter", "g0", (), (0, 0, 0, 0)),
        ("profile", "h0", (), (0, 0, 0, 0)),
    )
    key = (49, 55, (0, 0, 2), CHI, (), 87, ())
    coordinate = key, monomial
    old_vector = vector(old_repair)
    scalar_vector = vector(scalar_repair)
    if old_vector.get(coordinate) != (Fraction(-4), Fraction(0)):
        raise AssertionError("inherited arity-three witness drifted")
    if coordinate in scalar_vector:
        raise AssertionError("scalar orbit unexpectedly reached arity-three witness")
    scalar_entries = [
        {
            "output": tensor_key[0],
            "inputs": [
                [tensor_key[1], list(tensor_key[2])],
                [tensor_key[3], list(tensor_key[4])],
                [tensor_key[5], list(tensor_key[6])],
            ],
            "coefficient": serialize(coefficient),
        }
        for tensor_key, coefficient in sorted(scalar_repair.items())
    ]
    return {
        "decisive_witness": {
            "output": 49,
            "output_row_id": "c_spatial_star_1",
            "inputs": [
                [55, [0, 0, 2], "A_0"],
                [CHI, [], "chi"],
                [87, [], "K0_12"],
            ],
            "coefficient_monomial": "g0*h0",
            "old_repair_coefficient": [[-4, 1], [0, 1]],
            "scalar_repair_cross_coefficient": 0,
            "quartic_parameter_column_coefficient": 0,
            "witness_polynomial": "-4*g0*h0 + alpha*0 + sum_i lambda_i*0",
        },
        "scalar_repair_cross_manifest": manifest(scalar_entries),
    }


def q1_audit() -> dict[str, Any]:
    old = replay.load_q1()
    old_inputs = {key[1] for operator in old.values() for key in operator}
    old_outputs = {key[0] for operator in old.values() for key in operator}
    extension = extension_q1(temporal_order=0)
    extension_inputs = {key[1] for key in extension}
    extension_outputs = {key[0] for key in extension}
    cross_left = sorted(old_inputs & extension_outputs)
    cross_right = sorted(extension_inputs & old_outputs)
    if cross_left or cross_right:
        raise AssertionError("auxiliary unary acquired a composable old q1 cross term")
    return {
        "imported_complete_q1_unchanged": True,
        "auxiliary_q1_key_count": len(extension),
        "auxiliary_q1_self_composition": "ZERO_BY_ROW_SUPPORT",
        "old_after_auxiliary_intermediate_rows": cross_left,
        "auxiliary_after_old_intermediate_rows": cross_right,
        "extended_q1_squared": "ZERO_USING_IMPORTED_COMPLETE_Q1_NILPOTENCY",
    }


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    scalar = scalar_diff_q2()
    repair = generalized_action_to_q2(repair_action())
    covariance = contractible_covariance_audit(scalar)
    arity_two = arity_two_witness_audit(repair, scalar)
    arity_three = arity_three_audit(repair, scalar)
    entries = tensor_entries(scalar)
    payload = {
        "schema": "closed-universe-berger-auxiliary-diff-bv-scalar-orbit-repair-payload-v1",
        "result_id": "BERGER_AUXILIARY_DIFF_BV_SCALAR_ORBIT_REPAIR_PAYLOAD",
        "scalar_diff_bv_q2_entries": entries,
        "scalar_diff_bv_q2_manifest": manifest(entries),
        "contractible_covariance_audit": covariance,
        "arity_two_decisive_witness": arity_two,
        "arity_three_audit": arity_three,
    }
    return payload, {"scalar": scalar, "repair": repair}


def build_certificate(payload: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    rendered_payload = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    unary = q1_audit()
    return {
        "schema": "closed-universe-berger-auxiliary-diff-bv-scalar-orbit-repair-v1",
        "result_id": "BERGER_AUXILIARY_DIFF_BV_SCALAR_ORBIT_REPAIR",
        "setting_id": dependencies["quartic_moduli"]["setting_id"],
        "claim_status": "OBSTRUCTED_AUXILIARY_DIFF_BV_ORBIT_RETAINS_ARITY_TWO_AND_THREE_DEFECTS",
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
            "mathematical_target": "the smallest support-local Diff--BV representation closure of the auxiliary degree-(0,1) scalar pair inside the repaired 110-row common action",
            "candidate_theorem": "adjoining the complete scalar semidirect cotangent orbit makes the repaired q1/q2/q3 family nonempty at the arity-two and arity-three master gates",
            "proof_obligations": [
                "derive every scalar, scalar-cotangent and Diff-cotangent q2 slot from one local vertex",
                "fix its coefficient from the contractible-pair arity-two covariance block",
                "replay the surviving temporal arity-two source coordinate",
                "replay the scalar-repair contribution at the prior arity-three witness",
            ],
            "counterexample_strategy": "find an exact q1q2 coordinate independent of the scalar-orbit and quartic parameters; also test whether the prior q2q2 witness is reached",
            "certificate_boundary": "the earliest nonzero arity-two coefficient obstructs every q3 completion; the later arity-three replay is diagnostic and does not bypass that gate",
        },
        "extended_common_action_family": {
            "formula": "S_ext=S_pinned+S_repair^(3)+alpha integral chi_plus c^a e_a chi+sum_i lambda_i S4_i",
            "parameters": ["alpha"] + [f"lambda_{index:02d}" for index in range(12)],
            "scalar_pair": {
                "rows": [CHI, CHI_PLUS],
                "degrees": [0, 1],
                "pairing": "<chi,chi_plus>=1 and <chi_plus,chi>=-1",
                "Berger_weight": 0,
                "Weyl_weight": 0,
                "Maxwell_charge": 0,
            },
            "support_local_scalar_vertex": "alpha integral chi_plus c^a e_a chi, a=0,1,2,3",
            "completeness": "a weight-zero neutral scalar has the unique first-order Diff action c^a e_a chi; cotangent completion of its one lowered vertex supplies all three variational slots and all four frame components",
            "q1": unary,
            "q2": {
                "imported_complete_108_row_keys": dependencies["complete_q2"][
                    "payload_ref"
                ]["operator_key_count"],
                "repair_key_count": len(audit["repair"]),
                "scalar_diff_bv_key_count": len(audit["scalar"]),
                "odd_cyclicity": "CERTIFIED_BY_ONE_LOWERED_CUBIC_VERTEX",
            },
            "q3": {
                "scalar_diff_bv_vertex_q3": 0,
                "imported_quartic_parameter_rank": dependencies["quartic_moduli"][
                    "full_arity_three_gate"
                ]["parameter_column_rank"],
                "all_q3_columns_action_derived": True,
            },
        },
        "representation_closure": {
            "Diff": "CERTIFIED: temporal and all three spatial frame/ghost components plus scalar, scalar-cotangent and Diff-cotangent outputs are present",
            "Weyl": "CERTIFIED_TRIVIAL: chi and chi_plus have complementary zero Weyl representation and require no Weyl-ghost vertex",
            "Maxwell": "CERTIFIED_TRIVIAL: the auxiliary pair is neutral and the scalar vertex contains no Maxwell field",
            "Berger_U1": "CERTIFIED: the e1/e2 and c1/c2 components occur as the complete invariant contraction, with e0/e3 singlets",
            "contractible_covariance": payload["contractible_covariance_audit"],
            "normalization": "alpha=1 is the unique value closing the 30-key contractible-pair block",
        },
        "arity_two_gate": {
            "identity": "[q1,q2]=0",
            "status": "OBSTRUCTED",
            "decisive_witness": payload["arity_two_decisive_witness"],
            "admissible_locus_in_alpha_lambda": "EMPTY",
            "reason": "the witness is independent of alpha and every quartic lambda; q3 cannot enter an arity-two identity",
        },
        "arity_three_diagnostic": {
            "identity": "q2 circle q2 + q1 circle q3=0",
            "status": "OBSTRUCTED_EVEN_IF_EARLIER_ARITY_TWO_GATE_IS_IGNORED",
            **payload["arity_three_audit"],
            "admissible_locus_in_alpha_lambda": "EMPTY",
        },
        "first_missing_action_representations": [
            {
                "arity": 2,
                "required_channel": "an action-derived Maxwell- and Berger-completed temporal A--K Hessian with q2 chi_plus <- (e0 e1 A_0,K0_01)",
                "current_support": "ABSENT_FROM_THE_636_KEY_REPAIR",
            },
            {
                "arity": 3,
                "required_channel": "a quartic Diff-covariance descendant whose q1 image reaches c_spatial_star_1 <- (e0 e0 e2 A_0,chi,K0_12)",
                "current_support": "ABSENT_FROM_THE_SCALAR_ORBIT_AND_ALL_TWELVE_QUARTIC_COLUMNS",
            },
        ],
        "K_Berger_and_observer_disposition": {
            "K_Berger_equivariance": "NO_CERTIFIED_MAP: Berger-U1 invariance of the local scalar vertex is not the nonlinear K_Berger observer-morphism theorem",
            "same_action_apparatus_memory_detector_map": "NO_CERTIFIED_MAP",
            "detector_response_rank": "NO_CERTIFIED_MAP",
            "relational_redshift": "NO_CERTIFIED_MAP",
            "recoil_backreaction": "NO_CERTIFIED_MAP",
            "gauge_reduction": "OBSTRUCTED at the earlier arity-two master identity",
            "tangent_cone_restriction": "NO_CERTIFIED_MAP",
        },
        "mutations": {
            "set_alpha_zero": {
                "contractible_defect_key_count": 30,
                "detected": True,
            },
            "set_alpha_minus_one": {
                "contractible_defect_multiplier": -2,
                "detected": True,
            },
            "drop_e2_and_c2_component": {
                "Berger_U1_orbit_incomplete": True,
                "detected": True,
            },
            "inject_required_chi_plus_AK_key_by_hand": {
                "one_action_derivation_violated": True,
                "detected": True,
            },
            "delete_emitter_Diff_BV_source": {
                "both_displayed_source_witnesses_change": True,
                "detected": True,
            },
            "promote_detector_after_failed_arity_two": {
                "fail_closed_lifecycle_violated": True,
                "detected": True,
            },
        },
        "proof_obligation_dag": [
            {"id": "P1_IMPORT_PINNED_INPUTS_BY_HASH", "status": "CERTIFIED"},
            {"id": "P2_COMPLETE_SCALAR_DIFF_BV_ORBIT", "status": "CERTIFIED"},
            {"id": "P3_UNARY_NILPOTENCY_AND_CYCLICITY", "status": "CERTIFIED"},
            {"id": "P4_CONTRACTIBLE_COVARIANCE_NORMALIZATION", "status": "CERTIFIED"},
            {"id": "P5_FULL_ARITY_TWO_GATE", "status": "OBSTRUCTED"},
            {
                "id": "P6_PRIOR_ARITY_THREE_WITNESS_DIAGNOSTIC",
                "status": "OBSTRUCTED",
            },
            {
                "id": "P7_K_BERGER_AND_OBSERVER_PROPAGATION",
                "status": "NOT_APPLICABLE",
            },
        ],
        "assumption_ledger": [
            "The terminal 636-key repair, complete source-labelled 108-row q2, twelve quartic actions and predecessor witnesses are imported by content hash.",
            "The new auxiliary rows retain the signed unit odd pairing and constant unary of the terminal repair.",
            "Completeness is scoped to the unique local first-order weight-zero neutral scalar Diff vertex and its full cotangent orbit.",
            "The exact emitter switches are specialized by the certified relational-clock chain rule only at the displayed temporal arity-two source coordinate.",
        ],
        "missing_object_ledger": [
            {
                "object": "complete temporal A--K common-action Hessian selected by the direct arity-two identity",
                "status": "NO_CERTIFIED_MAP",
            },
            {
                "object": "quartic Diff-covariance descendant reaching the spatial c-plus witness",
                "status": "NO_CERTIFIED_MAP",
            },
            {
                "object": "nonempty arity-two/three master-equation locus",
                "status": "OBSTRUCTED",
            },
            {
                "object": "K_Berger, detector, memory, redshift, recoil and tangent-cone replay",
                "status": "NO_CERTIFIED_MAP",
            },
        ],
        "next_gate": "ADJOIN_TEMPORAL_AK_ARITY_TWO_AND_QUARTIC_DIFF_COVARIANCE_DESCENDANTS_AND_REPLAY",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate adjoins the "
            "complete support-local Diff--BV cotangent orbit of the existing "
            "degree-(0,1) auxiliary scalar pair. The unique vertex "
            "alpha integral chi_plus c^a e_a chi produces 32 graded-symmetric "
            "q2 keys across all four frame components. Its 30-key unary "
            "covariance defect is the negative of the inherited contractible-"
            "pair block exactly when alpha=1. The unchanged extended q1 is "
            "nilpotent by imported q1 nilpotency and empty cross-composition "
            "support, while cyclicity follows by differentiating the one "
            "lowered vertex. Nevertheless the source-isolated arity-two "
            "coefficient tau_star <- (e0 e1 A_0,K0_01) remains +g0 h0: the "
            "scalar orbit has no A--K Hessian and the 636-key repair lacks "
            "chi_plus <- (e0 e1 A_0,K0_01). Thus the arity-two admissible "
            "locus is empty for every alpha and all twelve quartic lambdas. "
            "As a later diagnostic, the scalar-repair q2q2 cross coefficient "
            "at c_spatial_star_1 <- (e0 e0 e2 A_0,chi,K0_12) is exactly zero, "
            "so the inherited -4 g0 h0 obstruction also remains. The next "
            "action representation must supply both the missing temporal A--K "
            "Hessian and a quartic Diff-covariance descendant. No K_Berger, "
            "detector, redshift, memory, recoil, tangent-cone, branch, "
            "particle, positivity, scattering, phenomenology or quantum "
            "claim is promoted."
        ),
        "provenance": {
            "science_forge_work_item": "sf:program/work/observer-auxiliary-diff-bv-scalar-orbit-repair",
            "input_commit": "9df828a482a247c9c1f0b45c349730a56037d551",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def render_report(value: dict[str, Any]) -> str:
    return """# Auxiliary Diff--BV scalar-orbit repair

The complete local scalar orbit is generated by
`alpha integral chi_plus c^a e_a chi` over all four Berger-frame components.
Exact differentiation through the signed odd pairing gives 32 `q2` keys.
Its 30-key contractible-pair covariance block cancels the inherited block
if and only if `alpha=1`.

That forced normalization does not close the full action.  The earliest
source-isolated arity-two coefficient remains

```text
tau_star <- (e0 e1 A_0, K0_01) = +g0 h0.
```

It is independent of `alpha` and all twelve quartic parameters.  The scalar
orbit has no A--K Hessian, and the 636-key repair has no
`chi_plus <- (e0 e1 A_0,K0_01)` key.  Hence the arity-two admissible locus is
empty before `q3` can contribute.

The prior arity-three obstruction also survives as a diagnostic.  The exact
scalar-repair cross coefficient at
`c_spatial_star_1 <- (e0 e0 e2 A_0,chi,K0_12)` is zero, leaving the inherited
`-4 g0 h0` coefficient unchanged.  The next action enlargement must contain a
direct temporal A--K Hessian selected by arity two and a quartic Diff-covariance
descendant reaching the spatial `c_plus` row.

No detector, memory, redshift, recoil, `K_Berger` or tangent-cone promotion is
made.

CLOSE-OUT: OBSTRUCTED — the complete auxiliary scalar Diff--BV orbit is uniquely normalized but retains exact arity-two and arity-three master defects
EVIDENCE: closed_universe_observers/certificates/BERGER_AUXILIARY_DIFF_BV_SCALAR_ORBIT_REPAIR.json
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
        raise SystemExit("stale auxiliary Diff--BV scalar-orbit result")
    print("BERGER_AUXILIARY_DIFF_BV_SCALAR_ORBIT_REPAIR generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
