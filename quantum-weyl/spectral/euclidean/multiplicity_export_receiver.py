"""Semantic receiver for a repository full-BV determinant multiplicity export."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCHEMA = HERE / "schema/repository-full-bv-multiplicity-export-v1.schema.json"

TARGET_ROWS = (
    ("physical_depth_0", 5, 1),
    ("ghost_depth_0", 1, -1),
    ("physical_depth_1", 5, 1),
    ("ghost_depth_1", 3, -1),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_artifact(
    value: object, *, repository_root: Path, label: str
) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"format", "path", "sha256"}:
        raise ValueError(f"{label} artifact fields drifted")
    path = (repository_root / value["path"]).resolve()
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} artifact escapes repository") from exc
    if not path.is_file() or _sha256(path) != value["sha256"]:
        raise ValueError(f"{label} artifact hash mismatch")
    return value


def validate_repository_multiplicity_export(
    payload: object,
    *,
    repository_root: Path,
    expected_classical_commit: str,
    expected_analytic_route: str,
) -> dict[str, Any]:
    """Validate schema, provenance, and total row/factor coverage."""

    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if not isinstance(payload, dict):  # narrowed by the schema; keeps type checkers honest
        raise ValueError("multiplicity payload is not an object")
    if payload["classical_commit"] != expected_classical_commit:
        raise ValueError("multiplicity artifact classical commit drifted")
    if payload["analytic_route"] != expected_analytic_route:
        raise ValueError("multiplicity artifact analytic route drifted")
    expected_tag = (
        "EUCLIDEAN-SPECTRAL"
        if expected_analytic_route == "EUCLIDEAN_ELLIPTIC"
        else "LORENTZIAN-CAUSAL"
    )
    if expected_tag not in payload["dependency_tags"]:
        raise ValueError("multiplicity artifact dependency tag drifted")

    rows = payload["integration_slice"]["rows"]
    row_by_id = {row["generator_id"]: row for row in rows}
    if len(row_by_id) != len(rows):
        raise ValueError("multiplicity integration row IDs are not unique")
    factors = payload["repository_factors"]
    factor_by_id = {factor["factor_id"]: factor for factor in factors}
    if len(factor_by_id) != len(factors):
        raise ValueError("multiplicity factor IDs are not unique")

    used_rows: set[str] = set()
    for factor in factors:
        sources = set(factor["source_generator_ids"])
        if not sources.issubset(row_by_id):
            raise ValueError("multiplicity factor cites an unknown integration row")
        used_rows.update(sources)

    maps = payload["standard_factor_map"]
    observed_targets = tuple(
        (
            row["target_factor_id"],
            row["target_bundle_rank"],
            row["target_determinant_sign"],
        )
        for row in maps
    )
    if observed_targets != TARGET_ROWS:
        raise ValueError("standard target rank/sign ledger drifted")
    mapped_occurrences = [
        factor_id for row in maps for factor_id in row["repository_factor_ids"]
    ]
    if len(mapped_occurrences) != len(set(mapped_occurrences)):
        raise ValueError("repository factor is mapped to more than one standard factor")
    mapped_factors = set(mapped_occurrences)
    if not mapped_factors.issubset(factor_by_id):
        raise ValueError("standard factor map cites an unknown repository factor")
    for row in maps:
        expected_statistics = (
            "BOSONIC" if row["target_determinant_sign"] == 1 else "FERMIONIC"
        )
        for factor_id in row["repository_factor_ids"]:
            factor = factor_by_id[factor_id]
            if (
                factor["component_rank"] != row["target_bundle_rank"]
                or factor["statistics"] != expected_statistics
            ):
                raise ValueError("repository factor rank/statistics do not match target")

    cancellations = payload["cancellations"]
    cancelled_factors = set(cancellations["cancelled_repository_factor_ids"])
    if not cancelled_factors.issubset(factor_by_id):
        raise ValueError("cancellation cites an unknown repository factor")
    if mapped_factors & cancelled_factors:
        raise ValueError("repository factor is both mapped and cancelled")
    if mapped_factors | cancelled_factors != set(factor_by_id):
        raise ValueError("repository factor coverage is incomplete")

    cancelled_rows = set(cancellations["cancelled_integration_row_ids"])
    if not cancelled_rows.issubset(row_by_id):
        raise ValueError("cancellation cites an unknown integration row")
    if used_rows & cancelled_rows:
        raise ValueError("integration row is both used and cancelled")
    if used_rows | cancelled_rows != set(row_by_id):
        raise ValueError("integration row coverage is incomplete")

    scalar_inputs = cancellations["scalar_ghost_input_generator_ids"]
    scalar_rows = [row_by_id[row_id] for row_id in scalar_inputs]
    if any(
        row["role"] != "ghost"
        or row["statistics"] != "FERMIONIC"
        or row["component_rank"] != 1
        for row in scalar_rows
    ):
        raise ValueError("scalar ghost input rows are not two rank-one fermionic ghosts")
    scalar_output_id = cancellations["scalar_ghost_output_repository_factor_id"]
    if scalar_output_id not in factor_by_id:
        raise ValueError("scalar ghost output factor is unknown")
    scalar_output = factor_by_id[scalar_output_id]
    ghost_zero_map = next(row for row in maps if row["target_factor_id"] == "ghost_depth_0")
    if (
        scalar_output_id not in ghost_zero_map["repository_factor_ids"]
        or scalar_output["statistics"] != "FERMIONIC"
        or scalar_output["component_rank"] != 1
        or not set(scalar_inputs).issubset(scalar_output["source_generator_ids"])
    ):
        raise ValueError("scalar ghost output does not realize the rank-two to rank-one map")

    nested_artifacts = [
        payload["integration_slice"]["proof_artifact"],
        cancellations["proof_artifact"],
        *payload["proof_artifacts"],
        *(row["derivation_artifact"] for row in factors),
        *(row["proof_artifact"] for row in maps),
    ]
    for index, artifact in enumerate(nested_artifacts):
        _validate_artifact(
            artifact,
            repository_root=repository_root,
            label=f"multiplicity_nested_proof[{index}]",
        )

    return {
        "result_id": payload["result_id"],
        "integration_row_count": len(rows),
        "repository_factor_count": len(factors),
        "mapped_factor_count": len(mapped_factors),
        "cancelled_factor_count": len(cancelled_factors),
        "target_bundle_ranks": [row[1] for row in TARGET_ROWS],
        "target_signed_rank": sum(rank * sign for _, rank, sign in TARGET_ROWS),
        "scalar_ghost_input_rank": sum(row["component_rank"] for row in scalar_rows),
        "scalar_ghost_output_rank": scalar_output["component_rank"],
        "row_coverage_complete": True,
        "factor_coverage_complete": True,
        "nested_artifact_count": len(nested_artifacts),
        "status": "SEMANTIC_RECEIVER_ACCEPTED",
    }


def synthetic_multiplicity_payload(*, repository_root: Path = ROOT) -> dict[str, Any]:
    """Build a non-scientific exact fixture that exercises every receiver edge."""

    proof_path = "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
    artifact = {
        "format": "JSON_PROOF",
        "path": proof_path,
        "sha256": _sha256(repository_root / proof_path),
    }
    integration_rows = [
        ("h_TT", "field", "BOSONIC", 5, "A_2", -1, 2),
        ("f_TT", "auxiliary", "BOSONIC", 5, "I_f", -1, 2),
        ("xi_T", "ghost", "FERMIONIC", 3, "M_1", 1, 1),
        ("xi_L", "ghost", "FERMIONIC", 1, "M_L", 1, 1),
        ("omega", "ghost", "FERMIONIC", 1, "M_W", 1, 1),
    ]
    rows = [
        {
            "generator_id": generator_id,
            "role": role,
            "statistics": statistics,
            "component_rank": rank,
            "operator_id": operator,
            "determinant_exponent": {"numerator": numerator, "denominator": denominator},
            "zero_mode_policy_id": "synthetic_closed_fixture",
        }
        for generator_id, role, statistics, rank, operator, numerator, denominator in integration_rows
    ]
    factor_specs = (
        ("repo_physical_0", "TT2", "BOSONIC", 5, "A", ["h_TT"]),
        ("repo_ghost_0", "scalar", "FERMIONIC", 1, "M_0", ["xi_L", "omega"]),
        ("repo_physical_1", "TT2", "BOSONIC", 5, "A_plus_2", ["h_TT", "f_TT"]),
        ("repo_ghost_1", "T1", "FERMIONIC", 3, "M_1", ["xi_T"]),
    )
    factors = [
        {
            "factor_id": factor_id,
            "bundle": bundle,
            "statistics": statistics,
            "component_rank": rank,
            "operator": operator,
            "determinant_exponent": {"numerator": 1, "denominator": 1},
            "source_generator_ids": sources,
            "derivation_artifact": artifact,
        }
        for factor_id, bundle, statistics, rank, operator, sources in factor_specs
    ]
    maps = [
        {
            "target_factor_id": target,
            "target_bundle_rank": rank,
            "target_determinant_sign": sign,
            "repository_factor_ids": [factor["factor_id"]],
            "status": "VERIFIED",
            "proof_artifact": artifact,
        }
        for (target, rank, sign), factor in zip(TARGET_ROWS, factors)
    ]
    return {
        "schema": "quantum-weyl-repository-full-bv-multiplicity-export-v1",
        "result_id": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
        "result_state": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": "0" * 40,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "integration_slice": {
            "status": "VERIFIED",
            "gauge": "synthetic_receiver_fixture",
            "rows": rows,
            "antifields_integrated_independently": False,
            "all_rows_accounted": True,
            "proof_artifact": artifact,
        },
        "repository_factors": factors,
        "standard_factor_map": maps,
        "cancellations": {
            "contractible_pairs_status": "VERIFIED",
            "scalar_ghost_reduction_status": "VERIFIED",
            "scalar_ghost_input_rank": 2,
            "scalar_ghost_output_rank": 1,
            "scalar_ghost_input_generator_ids": ["xi_L", "omega"],
            "scalar_ghost_output_repository_factor_id": "repo_ghost_0",
            "nonminimal_Berezinian_status": "VERIFIED",
            "cancelled_repository_factor_ids": [],
            "cancelled_integration_row_ids": [],
            "factor_coverage_status": "VERIFIED",
            "integration_row_coverage_status": "VERIFIED",
            "determinant_exponent_balance_status": "VERIFIED",
            "proof_artifact": artifact,
        },
        "proof_artifacts": [artifact],
        "claim_boundary": (
            "Synthetic receiver mechanics fixture only. It does not supply a repository "
            "Hessian, gauge fixing, determinant, anomaly coefficient, or QME result."
        ),
    }


def synthetic_receiver_receipt(*, repository_root: Path = ROOT) -> dict[str, Any]:
    return validate_repository_multiplicity_export(
        synthetic_multiplicity_payload(repository_root=repository_root),
        repository_root=repository_root,
        expected_classical_commit="0" * 40,
        expected_analytic_route="EUCLIDEAN_ELLIPTIC",
    )
