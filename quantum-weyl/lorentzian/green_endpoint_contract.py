"""Contract for the retained Berger 26-row Green/Hadamard endpoint.

The classical 54-to-26 reduction is already certified.  This module defines
the exact portable payload required at the remaining analytic endpoint and
validates its content-addressed proof artifacts.  It does not construct a
Green operator or a Hadamard two-point function.
"""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
from pathlib import Path
from typing import Any, Iterable


SCHEMA_ID = "quantum-weyl-berger-26-row-green-endpoint-export-v1"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"
GREEN_CHECKS = (
    "D_equivariance",
    "advanced_chain_homotopy_identity",
    "advanced_support",
    "cyclic_advanced_retarded_adjointness",
    "retarded_chain_homotopy_identity",
    "retarded_support",
    "row_completeness",
    "zero_mode_policy_applied",
)
HADAMARD_CHECKS = (
    "BRST_compatibility",
    "CCR_antisymmetric_part",
    "Hadamard_wavefront_set",
    "bisolution_modulo_smooth",
    "positivity_or_Krein_policy",
)
OPERATOR_IDS = ("D26", "Lambda_minus", "Lambda_plus", "pairing26", "q26")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_fields(value: object, expected: Iterable[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{label} fields drifted")
    return value


def _artifact(
    value: object,
    *,
    repository_root: Path,
    label: str,
) -> dict[str, str]:
    record = _require_fields(value, ("format", "path", "sha256"), label)
    if record["format"] not in {
        "JSON_EXACT_SPARSE_OPERATOR",
        "JSON_PROOF_CERTIFICATE",
        "TEXT_PROOF_CERTIFICATE",
    }:
        raise ValueError(f"{label} has an unknown artifact format")
    path = (repository_root / record["path"]).resolve()
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} escapes the repository root") from exc
    if not path.is_file() or _sha256(path) != record["sha256"]:
        raise ValueError(f"{label} artifact hash mismatch")
    return record


def _proof_ledger(
    value: object,
    *,
    expected: Iterable[str],
    repository_root: Path,
    label: str,
) -> None:
    ledger = _require_fields(value, expected, label)
    for check_id in expected:
        row = _require_fields(
            ledger[check_id], ("proof_artifact", "status"), f"{label}.{check_id}"
        )
        if row["status"] != "VERIFIED":
            raise ValueError(f"{label}.{check_id} is not verified")
        _artifact(
            row["proof_artifact"],
            repository_root=repository_root,
            label=f"{label}.{check_id}.proof_artifact",
        )


def validate_green_endpoint_export(
    payload: object,
    *,
    repository_root: Path,
) -> dict[str, Any]:
    """Validate a physical retained-endpoint export and return a summary."""

    record = _require_fields(
        payload,
        (
            "schema",
            "result_id",
            "result_state",
            "classical_commit",
            "dependency_tags",
            "setting_id",
            "row_layout",
            "support_category",
            "operators",
            "green_proof_checks",
            "hadamard",
            "claim_boundary",
        ),
        "green endpoint export",
    )
    if (
        record["schema"] != SCHEMA_ID
        or record["result_id"] != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"
        or record["result_state"]
        not in {"GREEN_CERTIFIED_HADAMARD_OPEN", "GREEN_AND_HADAMARD_CERTIFIED"}
        or record["setting_id"] != SETTING_ID
        or record["dependency_tags"] != ["LORENTZIAN-CAUSAL"]
    ):
        raise ValueError("green endpoint identity or lifecycle drifted")
    commit = record["classical_commit"]
    if not isinstance(commit, str) or len(commit) != 40 or any(
        char not in "0123456789abcdef" for char in commit
    ):
        raise ValueError("green endpoint classical commit is invalid")

    layout = _require_fields(
        record["row_layout"], ("degree_ranks", "row_ids", "total_rows"), "row layout"
    )
    row_ids = layout["row_ids"]
    if (
        layout["total_rows"] != 26
        or layout["degree_ranks"] != [3, 10, 10, 3]
        or not isinstance(row_ids, list)
        or len(row_ids) != 26
        or len(set(row_ids)) != 26
        or any(not isinstance(row_id, str) or not row_id for row_id in row_ids)
    ):
        raise ValueError("green endpoint row layout drifted")

    support = _require_fields(
        record["support_category"],
        (
            "boundary_conditions",
            "globally_hyperbolic",
            "spacetime_dimension",
            "test_function_space",
            "zero_mode_policy",
        ),
        "support category",
    )
    if (
        support["spacetime_dimension"] != 4
        or support["globally_hyperbolic"] is not True
        or any(
            not isinstance(support[key], str) or not support[key]
            for key in ("boundary_conditions", "test_function_space", "zero_mode_policy")
        )
    ):
        raise ValueError("green endpoint support category drifted")

    operators = _require_fields(record["operators"], OPERATOR_IDS, "operators")
    for operator_id in OPERATOR_IDS:
        _artifact(
            operators[operator_id],
            repository_root=repository_root,
            label=f"operators.{operator_id}",
        )
    _proof_ledger(
        record["green_proof_checks"],
        expected=GREEN_CHECKS,
        repository_root=repository_root,
        label="green_proof_checks",
    )

    hadamard = _require_fields(record["hadamard"], ("proof_checks", "status"), "hadamard")
    if hadamard["status"] == "NOT_CONSTRUCTED":
        if hadamard["proof_checks"] != {} or record["result_state"] != "GREEN_CERTIFIED_HADAMARD_OPEN":
            raise ValueError("open Hadamard stage was over-promoted")
    elif hadamard["status"] == "CERTIFIED":
        if record["result_state"] != "GREEN_AND_HADAMARD_CERTIFIED":
            raise ValueError("certified Hadamard stage has the wrong lifecycle")
        _proof_ledger(
            hadamard["proof_checks"],
            expected=HADAMARD_CHECKS,
            repository_root=repository_root,
            label="hadamard.proof_checks",
        )
    else:
        raise ValueError("unknown Hadamard status")
    if not isinstance(record["claim_boundary"], str) or not record["claim_boundary"]:
        raise ValueError("green endpoint claim boundary is missing")
    return {
        "classical_commit": commit,
        "row_count": 26,
        "green_status": "CERTIFIED",
        "hadamard_status": hadamard["status"],
        "operator_hashes": {
            key: operators[key]["sha256"] for key in sorted(operators)
        },
        "zero_mode_policy": support["zero_mode_policy"],
    }


Matrix = tuple[tuple[Fraction, ...], ...]


def _matrix(rows: Iterable[Iterable[int]]) -> Matrix:
    return tuple(tuple(Fraction(value) for value in row) for row in rows)


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(
            sum(
                (left[row][middle] * right[middle][column] for middle in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def _add(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(a + b for a, b in zip(left_row, right_row))
        for left_row, right_row in zip(left, right)
    )


def _transpose(value: Matrix) -> Matrix:
    return tuple(tuple(value[row][column] for row in range(len(value))) for column in range(len(value[0])))


def green_mechanics_fixture() -> dict[str, Any]:
    """Return an exact finite fixture for the algebraic endpoint identities."""

    q = _matrix(((0, 0), (1, 0)))
    homotopy = _matrix(((0, 1), (0, 0)))
    identity = _matrix(((1, 0), (0, 1)))
    pairing = _matrix(((0, 1), (1, 0)))
    d_action = _matrix(((0, 0), (0, 0)))
    chain = _add(_multiply(q, homotopy), _multiply(homotopy, q))
    adjoint = _multiply(_multiply(pairing, _transpose(homotopy)), pairing)
    d_defect = _add(
        _multiply(d_action, homotopy),
        tuple(tuple(-value for value in row) for row in _multiply(homotopy, d_action)),
    )
    checks = {
        "advanced_chain_homotopy_identity": chain == identity,
        "retarded_chain_homotopy_identity": chain == identity,
        "cyclic_advanced_retarded_adjointness": adjoint == homotopy,
        "D_equivariance": all(value == 0 for row in d_defect for value in row),
    }
    if not all(checks.values()):
        raise AssertionError("finite Green mechanics fixture failed")
    return {
        "fixture_id": "acyclic_two_row_green_mechanics",
        "scope": "FINITE_EXACT_MECHANICS_FIXTURE_NO_CAUSAL_GEOMETRY",
        "checks": {key: "VERIFIED" for key in sorted(checks)},
        "support_checks": "NOT_APPLICABLE_TO_FINITE_FIXTURE",
        "hadamard_checks": "NOT_APPLICABLE_TO_FINITE_FIXTURE",
    }


def build_contract_receipt() -> dict[str, Any]:
    return deepcopy(
        {
            "schema": "quantum-weyl-berger-26-row-green-endpoint-contract-v1",
            "result_id": "BERGER_26_ROW_GREEN_HADAMARD_ENDPOINT_CONTRACT",
            "result_state": "INTERFACE_READY_PHYSICAL_INPUT_BLOCKED",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "setting_id": SETTING_ID,
            "accepted_export_schema": SCHEMA_ID,
            "required_green_checks": list(GREEN_CHECKS),
            "conditional_hadamard_checks": list(HADAMARD_CHECKS),
            "mechanics_fixture": green_mechanics_fixture(),
            "physical_input_status": "NOT_RECEIVED",
            "green_endpoint_status": "NOT_CONSTRUCTED",
            "hadamard_status": "NOT_CONSTRUCTED",
            "quantum_execution_authorized": False,
            "next_gate": "IMPORT_CERTIFIED_BERGER_26_ROW_GREEN_ENDPOINT",
            "claim_boundary": (
                "The portable endpoint schema, content-hash validator, conditional "
                "Hadamard gate, and finite exact chain-homotopy mechanics are ready. "
                "No physical retained Green operator, support theorem, Hadamard state, "
                "causal product, QME, or quantum Cartan verdict is constructed."
            ),
        }
    )
