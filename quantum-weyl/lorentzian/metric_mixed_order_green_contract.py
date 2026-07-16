"""Fail-closed contract for the Berger mixed-order metric Green realization."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


SCHEMA_ID = "quantum-weyl-berger-metric-mixed-order-green-export-v1"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"
DIRECT_REALIZATION_KINDS = {
    "FILTERED_MIXED_ORDER",
    "FIRST_ORDER_DIFFERENTIAL_ALGEBRAIC",
    "AUXILIARY_FIELD_REDUCTION",
}
CLOCK_REALIZATION_KIND = "CLOCK_REATTACHED_SUPPORT_LOCAL_SDR"
REALIZATION_KINDS = DIRECT_REALIZATION_KINDS | {CLOCK_REALIZATION_KIND}
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
COMMON_PROOF_CHECKS = (
    "D_equivariance",
    "advanced_left_inverse",
    "advanced_right_inverse",
    "advanced_support",
    "constraint_compatibility",
    "cyclic_advanced_retarded_adjointness",
    "metric_antifield_formal_adjoint",
    "realization_equivalence",
    "retarded_left_inverse",
    "retarded_right_inverse",
    "retarded_support",
    "row_completeness",
    "zero_mode_policy_applied",
)
DIRECT_PROOF_CHECKS = (
    "characteristic_rank_stratification",
    "generic_rank_and_kernel",
)
CLOCK_PROOF_CHECKS = (
    "clock_reattached_principal_import",
    "clock_sdr_green_transport",
    "clock_sdr_support_local",
    "curved_clock_reattached_QW_plus_WQ",
    "scalar_biwave_characteristic_set",
)
ROOT = Path(__file__).resolve().parents[2]
CLOCK_PRINCIPAL_IMPORT = (
    ROOT / "quantum-weyl/lorentzian/certificates/BERGER_CLOCK_REATTACHED_PRINCIPAL_INPUT_IMPORT.json"
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


def _proof_ledger(
    value: object, *, expected: Iterable[str], repository_root: Path
) -> None:
    ledger = _require_fields(value, expected, "proof checks")
    for check_id in expected:
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

    realization = _require_fields(
        record["realization"],
        ("auxiliary_rows", "kind", "support_local", "working_degree_ranks"),
        "realization",
    )
    if (
        realization["kind"] not in REALIZATION_KINDS
        or type(realization["auxiliary_rows"]) is not int
        or realization["auxiliary_rows"] < 0
        or realization["support_local"] is not True
        or not isinstance(realization["working_degree_ranks"], list)
        or len(realization["working_degree_ranks"]) != 4
        or any(type(rank) is not int or rank < 0 for rank in realization["working_degree_ranks"])
    ):
        raise ValueError("mixed-order realization is inadmissible")

    principal = _require_fields(
        record["principal_boundary"],
        (
            "generic_fourth_order_rank", "polynomial_kernel_dimension",
            "principal_proof", "retained_characteristic_status",
            "scalar_characteristic_set",
        ),
        "principal boundary",
    )
    if (
        principal["generic_fourth_order_rank"] != 8
        or principal["polynomial_kernel_dimension"] != 2
        or not isinstance(principal["scalar_characteristic_set"], str)
        or not principal["scalar_characteristic_set"]
    ):
        raise ValueError("principal rank boundary is incomplete")
    principal_artifact = _artifact(
        principal["principal_proof"], repository_root=repository_root,
        label="principal boundary.principal_proof",
    )

    if realization["kind"] == CLOCK_REALIZATION_KIND:
        if (
            realization["auxiliary_rows"] != 8
            or realization["working_degree_ranks"] != [5, 12, 12, 5]
            or principal["retained_characteristic_status"]
            != "RESOLVED_BY_SUPPORT_LOCAL_CLOCK_REATTACHMENT"
            or principal["scalar_characteristic_set"] != "zeta^2=0"
        ):
            raise ValueError("clock-reattached principal route is incomplete")
        principal_path = (repository_root / principal_artifact["path"]).resolve()
        try:
            principal_payload = json.loads(principal_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("clock principal import is not portable JSON") from exc
        if (
            not isinstance(principal_payload, dict)
            or principal_payload.get("result_id")
            != "BERGER_CLOCK_REATTACHED_PRINCIPAL_INPUT_IMPORT"
            or principal_payload.get("result_state")
            != "PRINCIPAL_WITNESS_IMPORTED_CURVED_LOWER_ORDERS_OPEN"
            or principal_payload.get("preferred_realization", {}).get("kind")
            != CLOCK_REALIZATION_KIND
            or principal_payload.get("quantum_execution_authorized") is not False
        ):
            raise ValueError("clock principal import identity or boundary drifted")
        route_checks = CLOCK_PROOF_CHECKS
    else:
        if principal["retained_characteristic_status"] != "CLASSIFIED_DIRECTLY":
            raise ValueError("direct retained characteristic rank is not classified")
        route_checks = DIRECT_PROOF_CHECKS

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
    required_checks = COMMON_PROOF_CHECKS + route_checks
    _proof_ledger(
        record["proof_checks"], expected=required_checks, repository_root=repository_root
    )
    if not isinstance(record["claim_boundary"], str) or not record["claim_boundary"]:
        raise ValueError("metric Green claim boundary is missing")

    return {
        "classical_commit": commit,
        "generic_fourth_order_rank": 8,
        "polynomial_kernel_dimension": 2,
        "realization_kind": realization["kind"],
        "principal_resolution": principal["retained_characteristic_status"],
        "required_proof_checks": list(required_checks),
        "metric_green_status": "CERTIFIED",
        "metric_antifield_green_status": "CERTIFIED",
        "full_26_row_green_status": "ASSEMBLY_REQUIRED_NOT_IMPLICITLY_PROMOTED",
        "operator_hashes": {key: operators[key]["sha256"] for key in sorted(operators)},
    }


def build_contract_receipt() -> dict[str, Any]:
    principal_import = json.loads(CLOCK_PRINCIPAL_IMPORT.read_text(encoding="utf-8"))
    if (
        not isinstance(principal_import, dict)
        or principal_import.get("result_id")
        != "BERGER_CLOCK_REATTACHED_PRINCIPAL_INPUT_IMPORT"
        or principal_import.get("result_state")
        != "PRINCIPAL_WITNESS_IMPORTED_CURVED_LOWER_ORDERS_OPEN"
        or principal_import.get("preferred_realization", {}).get("kind")
        != CLOCK_REALIZATION_KIND
        or principal_import.get("next_gate") != "BERGER_CURVED_CLOCK_REATTACHED_WITNESS"
    ):
        raise ValueError("checked clock principal import identity or boundary drifted")
    return deepcopy(
        {
            "schema": "quantum-weyl-berger-metric-mixed-order-green-contract-v1",
            "result_id": "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION_CONTRACT",
            "result_state": "INTERFACE_READY_CLOCK_PRINCIPAL_IMPORTED_CURVED_OPEN",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "setting_id": SETTING_ID,
            "accepted_export_schema": SCHEMA_ID,
            "accepted_realization_kinds": sorted(REALIZATION_KINDS),
            "required_operator_ids": list(OPERATOR_IDS),
            "downstream_endpoint_factor_record_ids": list(FACTOR_RECORD_IDS),
            "common_proof_checks": list(COMMON_PROOF_CHECKS),
            "route_specific_proof_checks": {
                "DIRECT_RETAINED": list(DIRECT_PROOF_CHECKS),
                CLOCK_REALIZATION_KIND: list(CLOCK_PROOF_CHECKS),
            },
            "current_principal_boundary": {
                "generic_fourth_order_rank": 8,
                "polynomial_kernel_dimension": 2,
                "retained_characteristic_status": "PRESENTATION_EFFECT",
                "preferred_scalar_characteristic_set": "zeta^2=0",
                "preferred_principal_import": {
                    "path": "quantum-weyl/lorentzian/certificates/BERGER_CLOCK_REATTACHED_PRINCIPAL_INPUT_IMPORT.json",
                    "sha256": _sha256(CLOCK_PRINCIPAL_IMPORT),
                },
            },
            "physical_input_status": "CLOCK_REATTACHED_PRINCIPAL_IMPORTED_CURVED_OPEN",
            "metric_green_status": "NOT_CONSTRUCTED",
            "metric_antifield_green_status": "NOT_CONSTRUCTED",
            "full_26_row_green_status": "NOT_CONSTRUCTED",
            "quantum_execution_authorized": False,
            "next_gate": "BERGER_CURVED_CLOCK_REATTACHED_WITNESS",
            "claim_boundary": (
                "Imports the preferred clock-reattached scalar-biwave principal route and "
                "defines conditional acceptance for direct retained or support-local SDR "
                "realizations. It constructs no curved lower-order witness, physical Green "
                "operator, full 26-row homotopy, Hadamard state, QME restoration, or "
                "Lorentzian quantum theory."
            ),
        }
    )
