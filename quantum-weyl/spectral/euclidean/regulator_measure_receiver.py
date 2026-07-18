"""Semantic receiver for a repository regulator/zero-mode/measure ledger."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from classical_import.classical_snapshot_compatibility_receiver import (
    validate_classical_snapshot_compatibility,
)
from spectral.euclidean.elliptic_complex_receiver import (
    FROZEN_IMPORT,
    validate_euclidean_elliptic_complex,
)
from spectral.euclidean.multiplicity_export_receiver import (
    validate_repository_multiplicity_export,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCHEMA = HERE / "schema/repository-regulator-zero-mode-measure-input-v1.schema.json"
RESULT_IDS = {
    "elliptic_complex": "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX",
    "multiplicity": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
    "measure": "REPOSITORY_LOCAL_BV_MEASURE_LEDGER",
    "zero_modes": "REPOSITORY_ZERO_MODE_LEDGER",
    "regulator": "REPOSITORY_LOCAL_B4_REGULATOR",
    "contour_phase": "REPOSITORY_CONTOUR_AND_GLOBAL_PHASE_POLICY",
    "snapshot_compatibility": "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: object, label: str) -> Fraction:
    if (
        not isinstance(value, dict)
        or set(value) != {"numerator", "denominator"}
        or not isinstance(value["numerator"], int)
        or not isinstance(value["denominator"], int)
        or value["denominator"] <= 0
    ):
        raise ValueError(f"{label} is not an exact rational")
    return Fraction(value["numerator"], value["denominator"])


def _artifact(value: object, *, repository_root: Path, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"format", "path", "sha256"}:
        raise ValueError(f"{label} artifact fields drifted")
    path = (repository_root / value["path"]).resolve()
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} artifact escapes repository") from exc
    if not path.is_file() or _sha256(path) != value["sha256"]:
        raise ValueError(f"{label} artifact hash mismatch")
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"{label} artifact is not a JSON object")
    return payload


def validate_regulator_measure_ledger(
    payload: object,
    *,
    repository_root: Path = ROOT,
    allow_synthetic_fixture: bool = False,
) -> dict[str, Any]:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if not isinstance(payload, dict):
        raise ValueError("regulator/measure ledger is not an object")

    rows = payload["factor_ledger"]
    if len({row["factor_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate regulator/measure factor row")
    for row in rows:
        if row["primed"] != (row["zero_mode_dimension"] > 0):
            raise ValueError("factor priming does not match zero-mode dimension")
    weighted_rank = sum(
        (_q(row["Gamma_logdet_exponent"], row["factor_id"]) * row["bundle_rank"] for row in rows),
        Fraction(0),
    )
    declared_rank = _q(payload["aggregate_checks"]["weighted_logdet_rank"], "weighted_logdet_rank")
    zero_modes = sum(row["zero_mode_dimension"] for row in rows)
    if weighted_rank != declared_rank:
        raise ValueError("weighted determinant rank drifted")
    if zero_modes != payload["aggregate_checks"]["total_zero_mode_dimension"]:
        raise ValueError("zero-mode total drifted")

    artifacts = {
        role: _artifact(value, repository_root=repository_root, label=role)
        for role, value in payload["proof_artifacts"].items()
    }
    if not allow_synthetic_fixture:
        for role, expected in RESULT_IDS.items():
            if artifacts[role].get("result_id") != expected:
                raise ValueError(f"regulator/measure {role} proof role drifted")
        validate_euclidean_elliptic_complex(
            artifacts["elliptic_complex"], repository_root=repository_root
        )
        validate_repository_multiplicity_export(
            artifacts["multiplicity"],
            repository_root=repository_root,
            expected_classical_commit=payload["classical_commit"],
            expected_analytic_route=payload["analytic_route"],
        )
        frozen = json.loads(FROZEN_IMPORT.read_text())
        validate_classical_snapshot_compatibility(
            artifacts["snapshot_compatibility"],
            repository_root=repository_root,
            expected_local_commit=frozen["classical_commit"],
            expected_local_hashes=frozen["independent_replay"]["canonical_hashes"],
            expected_analytic_commit=payload["classical_commit"],
        )

    proof_payload = {
        key: payload[key]
        for key in (
            "classical_commit",
            "analytic_route",
            "background",
            "factor_ledger",
            "aggregate_checks",
            "measure_policy",
            "zero_mode_policy",
            "regulator_policy",
            "contour_and_phase_policy",
            "proof_artifacts",
        )
    }
    if payload["proof_sha256"] != _canonical_hash(proof_payload):
        raise ValueError("regulator/measure proof digest drifted")
    return {
        "result_id": payload["result_id"],
        "factor_count": len(rows),
        "weighted_logdet_rank": {
            "numerator": weighted_rank.numerator,
            "denominator": weighted_rank.denominator,
        },
        "zero_mode_dimension": zero_modes,
        "status": "SEMANTIC_RECEIVER_ACCEPTED",
    }


def synthetic_payload(*, repository_root: Path = ROOT) -> dict[str, Any]:
    fixture_path = repository_root / "quantum-weyl/spectral/euclidean/certificates/STANDARD_EUCLIDEAN_LOCAL_B4_INTEGRATION_SLICE.json"
    artifact = {
        "format": "JSON_PROOF",
        "path": str(fixture_path.relative_to(repository_root)),
        "sha256": _sha256(fixture_path),
    }
    value = {
        "schema": "quantum-weyl-repository-regulator-zero-mode-measure-input-v1",
        "result_id": "REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER",
        "result_state": "FULL_BV_REGULATOR_ZERO_MODE_MEASURE_LEDGER_COMPLETE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": "0" * 40,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "background": {"geometry": "synthetic compact Euclidean fixture", "dimension": 4, "boundary_policy": "CLOSED_NO_BOUNDARY"},
        "factor_ledger": [
            {"factor_id": "fixture_boson", "bundle_rank": 4, "Gamma_logdet_exponent": {"numerator": 1, "denominator": 2}, "zero_mode_dimension": 0, "primed": False},
            {"factor_id": "fixture_ghost", "bundle_rank": 2, "Gamma_logdet_exponent": {"numerator": -1, "denominator": 1}, "zero_mode_dimension": 3, "primed": True},
        ],
        "aggregate_checks": {"weighted_logdet_rank": {"numerator": 0, "denominator": 1}, "total_zero_mode_dimension": 3, "all_full_BV_rows_accounted": True},
        "measure_policy": {"common_nonzero_mode_domain": True, "all_jacobians_and_nonminimal_superdeterminants_included": True, "normalization_content_addressed": True},
        "zero_mode_policy": {"all_kernels_enumerated": True, "finite_symmetry_volume_policy": "DIVIDED_BY_DECLARED_NORMALIZED_VOLUME", "local_b4_effect": "FINITE_DIMENSIONAL_KERNELS_REMOVED_BEFORE_LOCAL_HEAT_TRACE"},
        "regulator_policy": {"regularization": "COVARIANT_HEAT_KERNEL", "local_covariance": True, "factorwise_scale_and_sign_conventions_fixed": True, "parity_disposition_certified": True},
        "contour_and_phase_policy": {"all_indefinite_directions_covered": True, "global_phase_status": "FIXED", "local_logarithmic_effect_separated": True},
        "proof_artifacts": {role: artifact for role in RESULT_IDS},
        "claim_flags": {"REPOSITORY_REGULATOR_ZERO_MODE_MEASURE_LEDGER_CERTIFIED": True, "REGULATED_SLAVNOV_BREAKING_COMPUTED": False, "QME_DISPOSITION": False, "LORENTZIAN_CERTIFIED": False},
        "claim_boundary": "Synthetic receiver fixture only. It exercises exact determinant-rank arithmetic, zero-mode priming, measure, regulator, contour and content-addressed proof-role mechanics; it does not certify the Weyl-gravity functional measure or master equation.",
    }
    value["proof_sha256"] = _canonical_hash({key: value[key] for key in ("classical_commit", "analytic_route", "background", "factor_ledger", "aggregate_checks", "measure_policy", "zero_mode_policy", "regulator_policy", "contour_and_phase_policy", "proof_artifacts")})
    return value
