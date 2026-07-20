"""Audit restrictions of the Berger rank-40 Hermitian dilation.

The Hermitian form on the doubled companion is off diagonal.  Consequently,
each canonical 20-row summand is isotropic and its pullback annihilates the
scalar Pauli--Jordan form.  It therefore cannot realize the separately
certified retained metric causal Green structure by canonical restriction.
A nondegenerate raw-companion restriction must instead use a graph
u |-> (u, J u), with J intertwining C and C^dagger and with J+J^dagger
nondegenerate.  The retained six ghost/identity rows then still require
their graded covariance before the certified 26->54 lift can be applied.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DILATION = (
    HERE / "certificates/BERGER_CUTOFF_COMPANION_HERMITIAN_DILATION.json"
)
FULL_COVARIANCE = (
    HERE
    / "certificates/BERGER_FULL_DILATION_HADAMARD_KREIN_CCR_COVARIANCE.json"
)
GRADED = HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json"
CAUSAL = HERE / "certificates/BERGER_CAUSAL_CHAIN_V2_IMPORT.json"
LIFT = HERE / "certificates/BERGER_HADAMARD_LIFT_AND_ZERO_MODE_PREFLIGHT.json"

DEPENDENCIES = {
    "Hermitian_dilation": DILATION,
    "full_dilation_covariance": FULL_COVARIANCE,
    "graded_54_contract": GRADED,
    "retained_causal_chain": CAUSAL,
    "conditional_26_to_54_lift": LIFT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _matmul(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum(
                (left[row][inner] * right[inner][column]
                 for inner in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def _transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*matrix)]


def _rank(matrix: list[list[Fraction]]) -> int:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column]), None
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(rows):
            if row != rank and work[row][column]:
                factor = work[row][column]
                work[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(work[row], work[rank])
                ]
        rank += 1
    return rank


def canonical_summand_replay() -> dict[str, Any]:
    """Use a one-component block model to replay the exact pullbacks."""

    zero = Fraction(0)
    one = Fraction(1)
    H = [[zero, one], [one, zero]]
    i1 = [[one], [zero]]
    i2 = [[zero], [one]]
    # E_C and E_Cdagger are represented by independent nonzero placeholders
    # with coefficient one; only the block location matters here.
    E_dilated = [[one, zero], [zero, one]]
    causal_form = _matmul(H, E_dilated)

    def pullback(form: list[list[Fraction]], inclusion: list[list[Fraction]]):
        return _matmul(_matmul(_transpose(inclusion), form), inclusion)

    H1 = pullback(H, i1)
    H2 = pullback(H, i2)
    E1 = pullback(causal_form, i1)
    E2 = pullback(causal_form, i2)
    checks = {
        "first_canonical_summand_pairing_rank_zero": _rank(H1) == 0,
        "second_canonical_summand_pairing_rank_zero": _rank(H2) == 0,
        "first_canonical_summand_CCR_pullback_zero": _rank(E1) == 0,
        "second_canonical_summand_CCR_pullback_zero": _rank(E2) == 0,
        "full_dilation_pairing_nondegenerate": _rank(H) == 2,
        "full_dilation_causal_form_nondegenerate_in_block_model": (
            _rank(causal_form) == 2
        ),
    }
    return {
        "block_form": "H=[[0,I],[I,0]]",
        "dilated_Green_operator": "E_D=diag(E_C,E_Cdagger)",
        "scalar_causal_form": "H E_D=[[0,E_Cdagger],[E_C,0]]",
        "first_summand": {
            "inclusion": "i_1:u->(u,0)",
            "pulled_pairing": "i_1^dagger H i_1=0",
            "pulled_CCR_form": "i_1^dagger H E_D i_1=0",
            "pairing_rank_in_block_replay": _rank(H1),
        },
        "second_summand": {
            "inclusion": "i_2:u->(0,u)",
            "pulled_pairing": "i_2^dagger H i_2=0",
            "pulled_CCR_form": "i_2^dagger H E_D i_2=0",
            "pairing_rank_in_block_replay": _rank(H2),
        },
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def graph_restriction_contract(
    *,
    support_local_intertwiner_supplied: bool = False,
    intertwining_verified: bool = False,
    graph_pairing_nondegenerate: bool = False,
    covariance_pullback_verified: bool = False,
    ghost_covariance_supplied: bool = False,
) -> dict[str, Any]:
    graph_operator_invariant = (
        support_local_intertwiner_supplied and intertwining_verified
    )
    raw_metric_covariance = (
        graph_operator_invariant
        and graph_pairing_nondegenerate
        and covariance_pullback_verified
    )
    retained_26_covariance = raw_metric_covariance and ghost_covariance_supplied
    checks = {
        "support_local_regular_J": support_local_intertwiner_supplied,
        "operator_graph_invariance_Cdagger_J_equals_J_C": (
            intertwining_verified
        ),
        "pulled_graph_pairing_J_plus_Jdagger_nondegenerate": (
            graph_pairing_nondegenerate
        ),
        "pulled_covariance_has_exact_raw_CCR_and_Hadamard_WF": (
            covariance_pullback_verified
        ),
        "six_retained_ghost_identity_rows_have_graded_covariance": (
            ghost_covariance_supplied
        ),
    }
    return {
        "graph": "i_J:u->(u,J u)",
        "operator_invariance": "Cdagger J=J C",
        "pulled_pairing": "i_J^dagger H i_J=J+Jdagger",
        "required_properties": checks,
        "raw_metric_covariance_ready": raw_metric_covariance,
        "retained_26_covariance_ready": retained_26_covariance,
        "status": (
            "READY"
            if retained_26_covariance
            else "EXPLICIT_INTERTWINER_AND_GHOST_COVARIANCE_NOT_SUPPLIED"
        ),
    }


def _load() -> dict[str, dict[str, Any]]:
    return {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in DEPENDENCIES.items()
    }


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    values = _load()
    dilation = values["Hermitian_dilation"]
    full_covariance = values["full_dilation_covariance"]
    graded = values["graded_54_contract"]
    causal = values["retained_causal_chain"]
    lift = values["conditional_26_to_54_lift"]
    input_checks = {
        "off_diagonal_Hermitian_dilation_certified": dilation["claim_flags"][
            "BERGER_METRIC_COMPANION_RFHGHO_DILATION"
        ]
        is True,
        "full_dilation_Hadamard_Krein_covariance_certified": (
            full_covariance["claim_flags"][
                "BERGER_FULL_DILATION_HADAMARD_KREIN_COVARIANCE"
            ]
            is True
        ),
        "full_dilation_exact_CCR_certified": full_covariance["claim_flags"][
            "BERGER_FULL_DILATION_EXACT_CCR"
        ]
        is True,
        "graded_54_causal_pairing_certified": graded["claim_flags"][
            "BERGER_BRST_CAUSAL_PAIRING_DESCENT"
        ]
        is True,
        "retained_metric_causal_Green_operators_imported": causal[
            "claim_flags"
        ]["BERGER_RETAINED_METRIC_GREEN_OPERATORS_IMPORTED"]
        is True,
        "retained_causal_chain_matches_analytic_snapshot": causal[
            "provenance"
        ]["classical_commit"]
        == full_covariance["classical_commit"],
        "conditional_26_to_54_lift_certified": lift["claim_flags"][
            "BERGER_COVARIANCE_LIFT_26_TO_54"
        ]
        is True,
        "exact_retained_26_covariance_still_open": lift[
            "retained_26_construction_boundary"
        ]["exact_global_omega2_plus_26"]
        == "NOT_CONSTRUCTED",
        "analytic_inputs_share_classical_snapshot": len(
            {
                dilation["classical_commit"],
                full_covariance["classical_commit"],
                graded["classical_commit"],
            }
        )
        == 1,
        "conditional_lift_pins_exact_graded_contract": lift["dependency_refs"][
            "graded_state_space_contract"
        ]["sha256"]
        == _sha256(GRADED),
        "conditional_lift_setting_matches": lift["setting_id"]
        == full_covariance["setting_id"],
    }
    if not all(input_checks.values()):
        failed = [name for name, passed in input_checks.items() if not passed]
        raise ValueError(f"dilation restriction-audit input drift: {failed}")

    summands = canonical_summand_replay()
    open_graph = graph_restriction_contract()
    complete_fixture = graph_restriction_contract(
        support_local_intertwiner_supplied=True,
        intertwining_verified=True,
        graph_pairing_nondegenerate=True,
        covariance_pullback_verified=True,
        ghost_covariance_supplied=True,
    )
    if (
        not summands["all_pass"]
        or open_graph["retained_26_covariance_ready"]
        or not complete_fixture["retained_26_covariance_ready"]
    ):
        raise ValueError("dilation restriction audit replay failed")

    result = {
        "schema": "quantum-weyl-berger-dilation-retained26-restriction-audit-v1",
        "result_id": "BERGER_DILATION_TO_RETAINED26_RESTRICTION_AUDIT",
        "result_state": (
            "CANONICAL_SUMMAND_RESTRICTION_OBSTRUCTED_GRAPH_INTERTWINER_OR_"
            "DIRECT_RETAINED26_COVARIANCE_REQUIRED"
        ),
        "lifecycle_layer": "LORENTZIAN_GRADED_BV_COVARIANCE_BOUNDARY",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": full_covariance["classical_commit"],
        "setting_id": full_covariance["setting_id"],
        "dependency_refs": {
            name: _dependency(DEPENDENCIES[name], payload)
            for name, payload in values.items()
        },
        "exact_input_checks": input_checks,
        "canonical_summand_audit": summands,
        "graph_restriction_contract": open_graph,
        "complete_contract_fixture": complete_fixture,
        "retained_26_to_54_bridge": {
            "conditional_lift": "omega54=iota_cl omega26 pi_cl",
            "status": "CERTIFIED_CONDITIONAL_ON_EXACT_RETAINED26_COVARIANCE",
            "remaining_metric_rows": 20,
            "remaining_ghost_identity_rows": 6,
            "does_not_require_rebuilding_54_row_lift": True,
        },
        "admissible_next_routes": [
            {
                "route": "GRAPH_RESTRICTION",
                "required_input": (
                    "support-local regular J with Cdagger J=J C, "
                    "nondegenerate J+Jdagger, and verified covariance pullback"
                ),
                "status": "OPEN",
            },
            {
                "route": "DIRECT_RETAINED26_CONSTRUCTION",
                "required_input": (
                    "omega26 built from the certified BV pairing and causal "
                    "homotopy, including the six ghost/identity rows"
                ),
                "status": "OPEN",
            },
        ],
        "claim_flags": {
            "BERGER_CANONICAL_DILATION_SUMMAND_RESTRICTION_PRESERVES_CCR": False,
            "BERGER_DILATION_GRAPH_RESTRICTION_CONTRACT_READY": True,
            "BERGER_DILATION_GRAPH_INTERTWINER_SUPPLIED": False,
            "BERGER_RETAINED26_HADAMARD_KREIN_COVARIANCE": False,
            "BERGER_COVARIANCE_LIFT_26_TO_54": True,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": (
            "SUPPLY_SUPPORT_LOCAL_GRAPH_INTERTWINER_OR_CONSTRUCT_DIRECT_"
            "RETAINED26_GRADED_COVARIANCE_THEN_APPLY_CERTIFIED_26_TO_54_LIFT"
        ),
        "provenance": {
            "proof_type": (
                "EXACT_BLOCK_PULLBACK_AUDIT_AND_FAIL_CLOSED_CONSUMER_CONTRACT"
            )
        },
        "claim_boundary": (
            "The off-diagonal Hermitian form makes both canonical companion "
            "summands isotropic, so direct summand restriction cannot preserve "
            "or realize the separately certified retained metric causal Green "
            "and CCR structure: its pulled pairing and scalar causal form are "
            "identically zero. This rejects only that canonical restriction. "
            "It does not prove that no support-local graph intertwiner exists. "
            "No retained-26 or 54-row covariance, BRST Ward identity, positive "
            "state, physical positivity, renormalized Lorentzian product, "
            "Lorentzian QME or quantum theory is certified."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "BERGER_DILATION_TO_RETAINED26_RESTRICTION_AUDIT"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != (
            "SUPPLY_SUPPORT_LOCAL_GRAPH_INTERTWINER_OR_CONSTRUCT_DIRECT_"
            "RETAINED26_GRADED_COVARIANCE_THEN_APPLY_CERTIFIED_26_TO_54_LIFT"
        )
    ):
        raise ValueError("dilation restriction-audit identity drifted")
    if not all(result.get("exact_input_checks", {}).values()):
        raise ValueError("dilation restriction-audit inputs failed")
    if not result.get("canonical_summand_audit", {}).get("all_pass"):
        raise ValueError("canonical summand audit failed")
    flags = result.get("claim_flags", {})
    if (
        flags.get("BERGER_DILATION_GRAPH_RESTRICTION_CONTRACT_READY")
        is not True
        or flags.get("BERGER_COVARIANCE_LIFT_26_TO_54") is not True
    ):
        raise ValueError("restriction consumer contract under-promoted")
    for name in (
        "BERGER_CANONICAL_DILATION_SUMMAND_RESTRICTION_PRESERVES_CCR",
        "BERGER_DILATION_GRAPH_INTERTWINER_SUPPLIED",
        "BERGER_RETAINED26_HADAMARD_KREIN_COVARIANCE",
        "BERGER_54_ROW_BRST_HADAMARD",
        "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY",
        "BERGER_HADAMARD_DATA",
        "QUANTUM_CLAIM",
    ):
        if flags.get(name) is not False:
            raise ValueError("restriction or BV claim over-promoted")
