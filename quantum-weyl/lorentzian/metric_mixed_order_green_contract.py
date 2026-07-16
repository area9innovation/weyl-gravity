"""Fail-closed contract for the Berger mixed-order metric Green realization."""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
from typing import Any, Iterable


SCHEMA_ID = "quantum-weyl-berger-metric-mixed-order-green-export-v1"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"
REALIZATION_KINDS = {
    "FILTERED_MIXED_ORDER",
    "FIRST_ORDER_DIFFERENTIAL_ALGEBRAIC",
    "AUXILIARY_FIELD_REDUCTION",
}
OPERATOR_IDS = (
    "P_metric",
    "P_metric_antifield",
    "Lambda_metric_minus",
    "Lambda_metric_plus",
    "Lambda_metric_antifield_minus",
    "Lambda_metric_antifield_plus",
    "realization_backward",
    "realization_forward",
)
FACTOR_RECORD_IDS = (
    "Box_1_spatial_covector",
    "Box_1_spatial_covector_formal_adjoint",
    "F_spatial_K_spatial",
    "F_spatial_K_spatial_formal_adjoint",
)
PROOF_CHECKS = (
    "D_equivariance",
    "advanced_left_inverse",
    "advanced_right_inverse",
    "advanced_support",
    "characteristic_rank_stratification",
    "constraint_compatibility",
    "cyclic_advanced_retarded_adjointness",
    "generic_rank_and_kernel",
    "metric_antifield_formal_adjoint",
    "realization_equivalence",
    "retarded_left_inverse",
    "retarded_right_inverse",
    "retarded_support",
    "row_completeness",
    "zero_mode_policy_applied",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_fields(value: object, expected: Iterable[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{label} fields drifted")
    return value


def _artifact(value: object, *, repository_root: Path, label: str) -> dict[str, str]:
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


def _proof_ledger(value: object, *, repository_root: Path) -> None:
    ledger = _require_fields(value, PROOF_CHECKS, "proof checks")
    for check_id in PROOF_CHECKS:
        row = _require_fields(
            ledger[check_id], ("proof_artifact", "status"), f"proof checks.{check_id}"
        )
        if row["status"] != "VERIFIED":
            raise ValueError(f"proof checks.{check_id} is not verified")
        _artifact(
            row["proof_artifact"],
            repository_root=repository_root,
            label=f"proof checks.{check_id}.proof_artifact",
        )


def validate_metric_green_export(
    payload: object, *, repository_root: Path
) -> dict[str, Any]:
    """Validate a proposed physical mixed-order metric Green theorem."""

    record = _require_fields(
        payload,
        (
            "schema", "result_id", "result_state", "classical_commit",
            "dependency_tags", "setting_id", "row_layout", "principal_boundary",
            "realization", "support_category", "operators",
            "proof_checks", "claim_boundary",
        ),
        "metric Green export",
    )
    if (
        record["schema"] != SCHEMA_ID
        or record["result_id"] != "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION"
        or record["result_state"] != "METRIC_AND_ANTIFIELD_GREEN_CERTIFIED"
        or record["dependency_tags"] != ["LORENTZIAN-CAUSAL"]
        or record["setting_id"] != SETTING_ID
    ):
        raise ValueError("metric Green identity or lifecycle drifted")
    commit = record["classical_commit"]
    if not isinstance(commit, str) or len(commit) != 40 or any(
        char not in "0123456789abcdef" for char in commit
    ):
        raise ValueError("metric Green classical commit is invalid")

    layout = _require_fields(
        record["row_layout"],
        ("metric_antifield_row_ids", "metric_row_ids", "rows_per_degree"),
        "row layout",
    )
    for key in ("metric_row_ids", "metric_antifield_row_ids"):
        rows = layout[key]
        if (
            not isinstance(rows, list) or len(rows) != 10 or len(set(rows)) != 10
            or any(not isinstance(row, str) or not row for row in rows)
        ):
            raise ValueError("metric Green row layout drifted")
    if layout["rows_per_degree"] != 10:
        raise ValueError("metric Green row count drifted")

    principal = _require_fields(
        record["principal_boundary"],
        (
            "characteristic_rank_stratification", "generic_fourth_order_rank",
            "polynomial_kernel_dimension", "rank_proof",
        ),
        "principal boundary",
    )
    if (
        principal["generic_fourth_order_rank"] != 8
        or principal["polynomial_kernel_dimension"] != 2
        or principal["characteristic_rank_stratification"] != "CLASSIFIED"
    ):
        raise ValueError("principal rank boundary is incomplete")
    _artifact(
        principal["rank_proof"], repository_root=repository_root,
        label="principal boundary.rank_proof",
    )

    realization = _require_fields(
        record["realization"], ("auxiliary_rows", "kind", "support_local"), "realization"
    )
    if (
        realization["kind"] not in REALIZATION_KINDS
        or type(realization["auxiliary_rows"]) is not int
        or realization["auxiliary_rows"] < 0
        or realization["support_local"] is not True
    ):
        raise ValueError("mixed-order realization is inadmissible")

    support = _require_fields(
        record["support_category"],
        (
            "boundary_conditions", "globally_hyperbolic", "spacetime_dimension",
            "test_function_space", "zero_mode_policy",
        ),
        "support category",
    )
    if (
        support["globally_hyperbolic"] is not True
        or support["spacetime_dimension"] != 4
        or any(
            not isinstance(support[key], str) or not support[key]
            for key in ("boundary_conditions", "test_function_space", "zero_mode_policy")
        )
    ):
        raise ValueError("metric Green support category drifted")

    operators = _require_fields(record["operators"], OPERATOR_IDS, "operators")
    for operator_id in OPERATOR_IDS:
        _artifact(
            operators[operator_id], repository_root=repository_root,
            label=f"operators.{operator_id}",
        )
    _proof_ledger(record["proof_checks"], repository_root=repository_root)
    if not isinstance(record["claim_boundary"], str) or not record["claim_boundary"]:
        raise ValueError("metric Green claim boundary is missing")

    return {
        "classical_commit": commit,
        "generic_fourth_order_rank": 8,
        "polynomial_kernel_dimension": 2,
        "realization_kind": realization["kind"],
        "metric_green_status": "CERTIFIED",
        "metric_antifield_green_status": "CERTIFIED",
        "full_26_row_green_status": "ASSEMBLY_REQUIRED_NOT_IMPLICITLY_PROMOTED",
        "operator_hashes": {key: operators[key]["sha256"] for key in sorted(operators)},
    }


def build_contract_receipt() -> dict[str, Any]:
    return deepcopy(
        {
            "schema": "quantum-weyl-berger-metric-mixed-order-green-contract-v1",
            "result_id": "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION_CONTRACT",
            "result_state": "INTERFACE_READY_PHYSICAL_INPUT_BLOCKED",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "setting_id": SETTING_ID,
            "accepted_export_schema": SCHEMA_ID,
            "accepted_realization_kinds": sorted(REALIZATION_KINDS),
            "required_operator_ids": list(OPERATOR_IDS),
            "downstream_endpoint_factor_record_ids": list(FACTOR_RECORD_IDS),
            "required_proof_checks": list(PROOF_CHECKS),
            "current_principal_boundary": {
                "generic_fourth_order_rank": 8,
                "polynomial_kernel_dimension": 2,
                "characteristic_rank_stratification": "NOT_CLASSIFIED",
                "rank_drop_on_characteristic_covectors_excluded": False,
            },
            "physical_input_status": "NOT_RECEIVED",
            "metric_green_status": "NOT_CONSTRUCTED",
            "metric_antifield_green_status": "NOT_CONSTRUCTED",
            "full_26_row_green_status": "NOT_CONSTRUCTED",
            "quantum_execution_authorized": False,
            "next_gate": "IMPORT_CERTIFIED_BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION",
            "claim_boundary": (
                "Defines the exact portable acceptance boundary for the rank-eight-plus-two "
                "metric and metric-antifield Green problem. It constructs no physical "
                "Green operator, full 26-row homotopy, Hadamard state, causal product, "
                "QME restoration, or Lorentzian quantum theory."
            ),
        }
    )
