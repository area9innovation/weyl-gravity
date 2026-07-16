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
RAW_REALIZATION_KIND = "RAW_CLOCK_RANK_ONE_WAVE_EXTENSION"
REALIZATION_KINDS = DIRECT_REALIZATION_KINDS | {RAW_REALIZATION_KIND}
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
RAW_PROOF_CHECKS = (
    "raw_endpoint_input_import",
    "rank_one_wave_extension",
    "clock_sdr_green_transport",
    "clock_sdr_support_local",
    "raw_clock_reattached_QW_plus_WQ",
    "scalar_biwave_characteristic_set",
)
ROOT = Path(__file__).resolve().parents[2]
RAW_ROUTE_IMPORT = ROOT / "quantum-weyl/lorentzian/certificates/BERGER_RAW_ENDPOINT_INPUT_IMPORT.json"
RAW_EXTENSION_IMPORT = ROOT / "quantum-weyl/lorentzian/certificates/BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION_IMPORT.json"
CYCLIC_REALIZATION_IMPORT = ROOT / "quantum-weyl/lorentzian/certificates/BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION_IMPORT.json"
EQUAL_CONNECTION_SCREEN = ROOT / "quantum-weyl/lorentzian/certificates/BERGER_METRIC_EQUAL_CONNECTION_FACTOR_SCREEN.json"
RETAINED_COMPANION_PREFLIGHT = ROOT / "quantum-weyl/lorentzian/certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"


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
        not isinstance(principal["generic_fourth_order_rank"], int)
        or not isinstance(principal["polynomial_kernel_dimension"], int)
        or not isinstance(principal["scalar_characteristic_set"], str)
        or not principal["scalar_characteristic_set"]
    ):
        raise ValueError("principal rank boundary is incomplete")
    principal_artifact = _artifact(
        principal["principal_proof"], repository_root=repository_root,
        label="principal boundary.principal_proof",
    )

    if realization["kind"] == RAW_REALIZATION_KIND:
        if (
            realization["auxiliary_rows"] != 8
            or realization["working_degree_ranks"] != [5, 12, 12, 5]
            or principal["generic_fourth_order_rank"] != 10
            or principal["polynomial_kernel_dimension"] != 0
            or principal["retained_characteristic_status"]
            != "RESOLVED_IN_RAW_BV_COORDINATES_FILTERED_EXTENSION"
            or principal["scalar_characteristic_set"] != "zeta^2=0"
        ):
            raise ValueError("raw endpoint extension principal route is incomplete")
        principal_path = (repository_root / principal_artifact["path"]).resolve()
        try:
            principal_payload = json.loads(principal_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("raw endpoint import is not portable JSON") from exc
        if (
            not isinstance(principal_payload, dict)
            or principal_payload.get("result_id") != "BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION_IMPORT"
            or principal_payload.get("result_state")
            != "CYCLIC_36_ROW_ANALYTIC_REALIZATION_IMPORTED_GREEN_OPERATORS_OPEN"
            or principal_payload.get("claim_flags", {}).get("BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION") is not True
            or principal_payload.get("claim_flags", {}).get("BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS") is not False
            or principal_payload.get("claim_flags", {}).get("QUANTUM_CLAIM") is not False
        ):
            raise ValueError("raw endpoint import identity or boundary drifted")
        route_checks = RAW_PROOF_CHECKS
    else:
        if (
            principal["generic_fourth_order_rank"] != 8
            or principal["polynomial_kernel_dimension"] != 2
            or principal["retained_characteristic_status"] != "CLASSIFIED_DIRECTLY"
        ):
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
        "generic_fourth_order_rank": principal["generic_fourth_order_rank"],
        "polynomial_kernel_dimension": principal["polynomial_kernel_dimension"],
        "realization_kind": realization["kind"],
        "principal_resolution": principal["retained_characteristic_status"],
        "required_proof_checks": list(required_checks),
        "metric_green_status": "CERTIFIED",
        "metric_antifield_green_status": "CERTIFIED",
        "full_26_row_green_status": "ASSEMBLY_REQUIRED_NOT_IMPLICITLY_PROMOTED",
        "operator_hashes": {key: operators[key]["sha256"] for key in sorted(operators)},
    }


def build_contract_receipt() -> dict[str, Any]:
    raw_import = json.loads(RAW_ROUTE_IMPORT.read_text(encoding="utf-8"))
    extension_import = json.loads(RAW_EXTENSION_IMPORT.read_text(encoding="utf-8"))
    cyclic_import = json.loads(CYCLIC_REALIZATION_IMPORT.read_text(encoding="utf-8"))
    factor_screen = json.loads(EQUAL_CONNECTION_SCREEN.read_text(encoding="utf-8"))
    retained_companion = json.loads(
        RETAINED_COMPANION_PREFLIGHT.read_text(encoding="utf-8")
    )
    if (
        not isinstance(raw_import, dict)
        or raw_import.get("result_id") != "BERGER_RAW_ENDPOINT_INPUT_IMPORT"
        or raw_import.get("result_state")
        != "RAW_ENDPOINT_IMPORTED_EXACT_REPLAY_FILTERED_GREEN_EXTENSION_OPEN"
        or raw_import.get("principal_compatibility_certified") is not True
        or raw_import.get("filtered_extension_preflight_certified") is not True
        or raw_import.get("green_execution_authorized") is not False
        or raw_import.get("quantum_execution_authorized") is not False
        or raw_import.get("next_gate")
        != "CONSTRUCT_RANK_ONE_WAVE_FILTERED_GREEN_EXTENSION_FOR_RAW_ENDPOINT"
    ):
        raise ValueError("checked raw endpoint import identity or boundary drifted")
    if (
        not isinstance(extension_import, dict)
        or extension_import.get("result_id")
        != "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION_IMPORT"
        or extension_import.get("result_state")
        != "LOCAL_SCALAR_WAVE_PROLONGATION_IMPORTED_GREEN_OPERATORS_OPEN"
        or extension_import.get("claim_flags", {}).get(
            "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION"
        ) is not True
        or extension_import.get("claim_flags", {}).get(
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"
        ) is not False
        or extension_import.get("next_gate")
        != "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"
    ):
        raise ValueError("checked rank-one wave extension import identity or boundary drifted")
    if (
        not isinstance(cyclic_import, dict)
        or cyclic_import.get("result_id")
        != "BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION_IMPORT"
        or cyclic_import.get("result_state")
        != "CYCLIC_36_ROW_ANALYTIC_REALIZATION_IMPORTED_GREEN_OPERATORS_OPEN"
        or cyclic_import.get("claim_flags", {}).get(
            "BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION"
        ) is not True
        or cyclic_import.get("claim_flags", {}).get(
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"
        ) is not False
        or cyclic_import.get("next_gate")
        != "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"
    ):
        raise ValueError("checked cyclic analytic realization import identity or boundary drifted")
    if (
        not isinstance(factor_screen, dict)
        or factor_screen.get("result_id")
        != "BERGER_METRIC_EQUAL_CONNECTION_FACTOR_SCREEN"
        or factor_screen.get("result_state")
        != "LOWER_BY_TWO_AND_METRIC_CONE_NO_GO_IMPORTED_HYBRID_RETAINED_ROUTE_REQUIRED"
        or factor_screen.get("claim_flags", {}).get(
            "BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORTED"
        ) is not True
        or factor_screen.get("claim_flags", {}).get(
            "BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO_IMPORTED"
        ) is not True
        or factor_screen.get("claim_flags", {}).get(
            "EQUAL_CONNECTION_LAPLACE_FACTOR_ANSATZ"
        ) is not False
        or factor_screen.get("claim_flags", {}).get(
            "UNEQUAL_SUBPRINCIPAL_FACTOR_ANSATZ"
        ) != "OPEN"
        or factor_screen.get("claim_flags", {}).get(
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"
        ) is not False
        or factor_screen.get("screen", {}).get("normalized_dual_witness", {}).get("value")
        != "1"
    ):
        raise ValueError("equal-connection factor screen identity or boundary drifted")
    if (
        not isinstance(retained_companion, dict)
        or retained_companion.get("result_id")
        != "BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT"
        or retained_companion.get("result_state")
        != "RETAINED_METRIC_IDENTIFIED_COMPANION_EXACT_CAUSAL_RESOLVENT_OPEN"
        or retained_companion.get("retained_endpoint", {}).get("metric_identity")
        != "P26_metric=A10=Box_2^2+V_2"
        or retained_companion.get("companion_system", {}).get(
            "principal_determinant"
        )
        != "q^20"
        or retained_companion.get("companion_system", {}).get(
            "extra_characteristic_cone"
        )
        is not False
        or retained_companion.get("claim_flags", {}).get(
            "BERGER_RETAINED_BIWAVE_COMPANION_EXACT"
        )
        is not True
        or retained_companion.get("claim_flags", {}).get(
            "BERGER_RETAINED_BIWAVE_COMPANION_GRAPH_SDR"
        )
        is not True
        or retained_companion.get("claim_flags", {}).get(
            "BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION_IMPORTED"
        )
        is not True
        or retained_companion.get("claim_flags", {}).get(
            "BERGER_RAW_EXTRA_MODE_PURE_CLOCK"
        )
        is not False
        or retained_companion.get("claim_flags", {}).get(
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT"
        )
        is not False
        or retained_companion.get("claim_flags", {}).get("QUANTUM_CLAIM")
        is not False
        or retained_companion.get("next_gate")
        != "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT"
    ):
        raise ValueError("retained biwave companion identity or boundary drifted")
    return deepcopy(
        {
            "schema": "quantum-weyl-berger-metric-mixed-order-green-contract-v1",
            "result_id": "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION_CONTRACT",
            "result_state": "INTERFACE_READY_CYCLIC_ANALYTIC_REALIZATION_IMPORTED_GREEN_OPERATORS_OPEN",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            "setting_id": SETTING_ID,
            "accepted_export_schema": SCHEMA_ID,
            "accepted_realization_kinds": sorted(REALIZATION_KINDS),
            "required_operator_ids": list(OPERATOR_IDS),
            "downstream_endpoint_factor_record_ids": list(FACTOR_RECORD_IDS),
            "common_proof_checks": list(COMMON_PROOF_CHECKS),
            "route_specific_proof_checks": {
                "DIRECT_RETAINED": list(DIRECT_PROOF_CHECKS),
                RAW_REALIZATION_KIND: list(RAW_PROOF_CHECKS),
            },
            "current_principal_boundary": {
                "generic_fourth_order_rank": 10,
                "polynomial_kernel_dimension": 0,
                "retained_characteristic_status": "RESOLVED_IN_RAW_BV_COORDINATES_FILTERED_EXTENSION_OPEN",
                "preferred_scalar_characteristic_set": "zeta^2=0",
                "preferred_principal_import": {
                    "path": "quantum-weyl/lorentzian/certificates/BERGER_RAW_ENDPOINT_INPUT_IMPORT.json",
                    "sha256": _sha256(RAW_ROUTE_IMPORT),
                },
            },
            "current_curved_boundary": {
                "status": "DRESSED_REJECTED_FOR_GREEN_RAW_IMPORTED_AND_EXACTLY_REPLAYED",
                "path": "quantum-weyl/lorentzian/certificates/BERGER_RAW_ENDPOINT_INPUT_IMPORT.json",
                "sha256": _sha256(RAW_ROUTE_IMPORT),
                "certified_identities": [
                    "q34^2=0",
                    "pairing34_nondegenerate",
                    "q34_cyclic",
                    "q34_W34+W34_q34=P34",
                    "W34_cyclic",
                ],
            },
            "current_extension_boundary": {
                "status": "FULL_L13_METRIC_CONE_INVERSE_OBSTRUCTED_RETAINED_BIWAVE_COMPANION_EXACT_VOLTERRA_RESOLVENT_OPEN",
                "authoritative_BV_rows": 34,
                "analytic_rows": 36,
                "wave_extension_path": "quantum-weyl/lorentzian/certificates/BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION_IMPORT.json",
                "wave_extension_sha256": _sha256(RAW_EXTENSION_IMPORT),
                "cyclic_realization_path": "quantum-weyl/lorentzian/certificates/BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION_IMPORT.json",
                "cyclic_realization_sha256": _sha256(CYCLIC_REALIZATION_IMPORT),
                "factor_screen_path": "quantum-weyl/lorentzian/certificates/BERGER_METRIC_EQUAL_CONNECTION_FACTOR_SCREEN.json",
                "factor_screen_sha256": _sha256(EQUAL_CONNECTION_SCREEN),
                "factor_screen_verdict": "EQUAL_CONNECTION_LAPLACE_FACTOR_ANSATZ_OBSTRUCTED",
                "retained_companion_path": "quantum-weyl/lorentzian/certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json",
                "retained_companion_sha256": _sha256(RETAINED_COMPANION_PREFLIGHT),
                "retained_metric_identity": "P26_metric=A10=Box_2^2+V_2",
                "retained_companion_principal_determinant": "q^20",
                "lower_by_two_normal_form": "A10=Box_2^2+V_2",
                "lower_by_two_next_gate": "BERGER_LOWER_BY_TWO_CAUSAL_RESOLVENT",
                "full_L13_metric_cone_verdict": "EXACT_NO_GO_EXTRA_SPEED_SQRT2",
                "extra_characteristic": "p0^2=2|p_spatial|^2",
                "extra_characteristic_polarization": "MIXED_RETAINED_METRIC_AND_CLOCK",
                "raw_extra_mode_pure_clock": False,
                "selector_projection_kills_raw_polarization": False,
                "correct_homological_operation": "APPLY_BV_SDR_AND_CONSTRUCT_RETAINED_WITNESS_DO_NOT_PROJECT_L13_SOLUTIONS",
                "retained_companion_graph_sdr": True,
                "viable_next_architectures": [
                    "RETAINED_BIWAVE_VOLTERRA_RESOLVENT",
                    "WIDER_CHARACTERISTIC_CONE_GREEN_INVERSE_NONPHYSICAL_OPTION",
                ],
                "triangular_reduction": "E13 L13 U13^{-1}=L12 direct sum I1",
            },
            "physical_input_status": "FULL_L13_METRIC_CONE_NO_GO_IMPORTED_RETAINED_COMPANION_EXACT_VOLTERRA_OPEN",
            "metric_green_status": "NOT_CONSTRUCTED",
            "metric_antifield_green_status": "NOT_CONSTRUCTED",
            "full_26_row_green_status": "NOT_CONSTRUCTED",
            "quantum_execution_authorized": False,
            "next_gate": "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT",
            "claim_boundary": (
                "Rejects the dressed cyclic witness as a Green endpoint, imports the "
                "principal-compatible raw cyclic 34-row route, the rank-one scalar-wave "
                "prolongation, and its cyclic 36-row analytic realization. The normalized "
                "classical lower-by-two tensor-biwave normal form is independently replayed. "
                "The normalized quadratic-symbol witness rules out the shared-connection Laplace-type "
                "two-factor ansatz but leaves unequal subprincipal and auxiliary/first-order "
                "architectures open. The full 13-row endpoint additionally has a genuine "
                "sqrt(2) characteristic outside the metric cone, so a metric-causal inverse "
                "on arbitrary 13-row sources is ruled out and the hybrid retained chain route "
                "is required. Its polarization mixes retained metric and clock components; "
                "the BV SDR must construct a new retained witness rather than project L13 "
                "solutions. Exact projection identifies its metric block with A10, and the "
                "local 20-row companion has a two-sided graph SDR and principal determinant "
                "q^20 with no extra cone. "
                "The causal Volterra resolvent remains open. It "
                "constructs no advanced or retarded Green operator, causal support "
                "theorem, full 26-row homotopy, Hadamard state, QME restoration, or "
                "Lorentzian quantum theory."
            ),
        }
    )
