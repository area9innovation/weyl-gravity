"""Semantic receiver for a C2-visible repository full-BV coefficient match."""

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
from spectral.euclidean.multiplicity_export_receiver import (
    validate_repository_multiplicity_export,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCHEMA = HERE / "schema/repository-nonconformal-coefficient-match-input-v1.schema.json"
FROZEN_IMPORT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
RESULT_IDS = {
    "background": "REPOSITORY_C2_VISIBLE_BACKGROUND_ELIGIBILITY",
    "elliptic_complex": "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX",
    "multiplicity": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
    "measure": "REPOSITORY_LOCAL_BV_MEASURE_LEDGER",
    "regulator": "REPOSITORY_LOCAL_B4_REGULATOR",
    "zero_modes": "REPOSITORY_ZERO_MODE_LEDGER",
    "auxiliary_match": "REPOSITORY_AUXILIARY_FOURTH_ORDER_MATCH",
    "parity": "REPOSITORY_PARITY_WARD_IDENTITY",
    "round_S4": "REPOSITORY_ROUND_S4_EULER_COEFFICIENT",
    "snapshot_compatibility": "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _rational(value: object, label: str) -> Fraction:
    if (
        not isinstance(value, dict)
        or set(value) != {"numerator", "denominator"}
        or not isinstance(value["numerator"], int)
        or not isinstance(value["denominator"], int)
        or value["denominator"] <= 0
    ):
        raise ValueError(f"{label} is not an exact rational")
    return Fraction(value["numerator"], value["denominator"])


def _artifact(
    value: object, *, repository_root: Path, label: str
) -> tuple[dict[str, str], dict[str, Any]]:
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
    return value, payload


def _require_result_id(payload: dict[str, Any], expected: str, label: str) -> None:
    if payload.get("result_id") != expected:
        raise ValueError(
            f"{label} has result_id {payload.get('result_id')!r}, expected {expected!r}"
        )


def validate_nonconformal_coefficient_match(
    payload: object,
    *,
    repository_root: Path = ROOT,
    allow_synthetic_fixture: bool = False,
) -> dict[str, Any]:
    """Validate exact provenance, full-BV coverage, and coefficient arithmetic."""

    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if not isinstance(payload, dict):
        raise ValueError("nonconformal coefficient match is not an object")

    commit = payload["classical_commit"]
    background_artifact, background = _artifact(
        payload["background"]["eligibility_artifact"],
        repository_root=repository_root,
        label="background.eligibility",
    )
    operator = payload["operator_and_measure"]
    role_rows = {
        "elliptic_complex": operator["complete_elliptic_complex_artifact"],
        "multiplicity": operator["full_BV_multiplicity_artifact"],
        "measure": operator["local_measure_artifact"],
        "regulator": operator["local_b4_regulator_artifact"],
        "zero_modes": operator["zero_mode_ledger_artifact"],
        "parity": payload["consistency"]["parity_artifact"],
        "round_S4": payload["consistency"]["round_S4_cross_check_artifact"],
        "snapshot_compatibility": payload["classical_snapshot_compatibility_artifact"],
    }
    if operator["formulation"] == "SECOND_ORDER_AUXILIARY":
        role_rows["auxiliary_match"] = operator[
            "auxiliary_fourth_order_match_artifact"
        ]
    elif operator["auxiliary_fourth_order_match_artifact"] is not None:
        raise ValueError("fourth-order formulation supplied an auxiliary-only proof")

    loaded: dict[str, dict[str, Any]] = {}
    for role, artifact in role_rows.items():
        _, loaded[role] = _artifact(
            artifact, repository_root=repository_root, label=role
        )
    if not allow_synthetic_fixture:
        _require_result_id(background, RESULT_IDS["background"], "background")
        for role, value in loaded.items():
            _require_result_id(value, RESULT_IDS[role], role)
        validate_repository_multiplicity_export(
            loaded["multiplicity"],
            repository_root=repository_root,
            expected_classical_commit=commit,
            expected_analytic_route="EUCLIDEAN_ELLIPTIC",
        )
        eligibility = background.get("eligibility", {})
        invariants = background.get("exact_invariants", {})
        if (
            eligibility.get("dimension") != 4
            or eligibility.get("signature") != "EUCLIDEAN"
            or eligibility.get("Ricci_flat") is not True
            or eligibility.get("C2_nonzero") is not True
            or invariants.get("R") != {"numerator": 0, "denominator": 1}
            or invariants.get("Ricci_squared") != {"numerator": 0, "denominator": 1}
            or invariants.get("C2") == {"numerator": 0, "denominator": 1}
            or invariants.get("E4") != invariants.get("C2")
        ):
            raise ValueError("C2-visible Ricci-flat background eligibility drifted")
        measure = loaded["measure"]
        regulator = loaded["regulator"]
        zero_modes = loaded["zero_modes"]
        parity = loaded["parity"]
        target_ids = [row["target_factor_id"] for row in loaded["multiplicity"]["standard_factor_map"]]
        repository_ids = [row["repository_factor_ids"][0] for row in loaded["multiplicity"]["standard_factor_map"]]
        if (
            measure.get("factor_bundle_ranks") != [5, 1, 5, 3]
            or measure.get("York_Hodge_Delta0_cancellation") is not True
            or measure.get("nonminimal_quartet_superdeterminant") != "1"
            or regulator.get("factor_count") != 4
            or regulator.get("factor_ids") != target_ids
            or regulator.get("BoxR_scheme")
            != "set to zero by the declared local R2 counterterm convention"
            or zero_modes.get("policy") != "LOCAL_COMPACT_SUPPORT_NO_GLOBAL_KERNEL_SUBTRACTION"
            or zero_modes.get("local_b4_modified_by_finite_zero_modes") is not False
            or parity.get("ward_matrix") != [[2]]
            or parity.get("ward_rank") != 1
            or parity.get("CdualC_coefficient") != {"numerator": 0, "denominator": 1}
            or [row["factor_id"] for row in payload["coefficient_result"]["factor_contributions"]]
            != repository_ids
        ):
            raise ValueError("C2 coefficient carrier coverage or policy drifted")
        frozen = json.loads(FROZEN_IMPORT.read_text())
        validate_classical_snapshot_compatibility(
            loaded["snapshot_compatibility"],
            repository_root=repository_root,
            expected_local_commit=frozen["classical_commit"],
            expected_local_hashes=frozen["independent_replay"]["canonical_hashes"],
            expected_analytic_commit=commit,
        )

    basis = payload["coefficient_result"]["basis"]
    totals = {
        name: sum(
            (
                _rational(row["coordinates"][name], f"factor[{index}].{name}")
                for index, row in enumerate(
                    payload["coefficient_result"]["factor_contributions"]
                )
            ),
            Fraction(0),
        )
        for name in basis
    }
    declared = {
        name: _rational(
            payload["coefficient_result"]["coefficients"][name],
            f"coefficient.{name}",
        )
        for name in basis
    }
    if totals != declared:
        raise ValueError("nonconformal coefficient factor sum drifted")
    if payload["coefficient_result"]["factor_sum_verified"] is not True:
        raise ValueError("nonconformal coefficient sum is not certified")

    proof_payload = {
        key: payload[key]
        for key in (
            "classical_commit",
            "analytic_route",
            "background",
            "operator_and_measure",
            "coefficient_result",
            "consistency",
            "classical_snapshot_compatibility_artifact",
        )
    }
    if payload["proof_sha256"] != _canonical_hash(proof_payload):
        raise ValueError("nonconformal coefficient proof digest drifted")
    return {
        "result_id": payload["result_id"],
        "classical_commit": commit,
        "basis": basis,
        "coefficients": {
            name: {
                "numerator": declared[name].numerator,
                "denominator": declared[name].denominator,
            }
            for name in basis
        },
        "factor_count": len(payload["coefficient_result"]["factor_contributions"]),
        "status": "SEMANTIC_RECEIVER_ACCEPTED",
    }


def synthetic_payload(*, repository_root: Path = ROOT) -> dict[str, Any]:
    """Non-scientific exact fixture for receiver and mutation tests."""

    fixture_path = (
        repository_root
        / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_ROUND_S4_EULER_COEFFICIENT.json"
    )
    artifact = {
        "format": "JSON_PROOF",
        "path": str(fixture_path.relative_to(repository_root)),
        "sha256": _sha256(fixture_path),
    }
    result = {
        "schema": "quantum-weyl-repository-nonconformal-coefficient-match-input-v1",
        "result_id": RESULT_IDS["background"].replace(
            "C2_VISIBLE_BACKGROUND_ELIGIBILITY",
            "NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH",
        ),
        "result_state": "C2_VISIBLE_FULL_BV_LOCAL_COEFFICIENT_MATCHED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": "0" * 40,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "background": {
            "geometry": "synthetic C2-visible receiver fixture",
            "dimension": 4,
            "signature": "EUCLIDEAN",
            "C2_visibility": "NONZERO_LOCAL_DENSITY",
            "boundary_policy": "LOCAL_CLOSED_OR_COMPACT_SUPPORT",
            "eligibility_artifact": artifact,
        },
        "operator_and_measure": {
            "formulation": "FOURTH_ORDER_METRIC",
            "complete_elliptic_complex_artifact": artifact,
            "full_BV_multiplicity_artifact": artifact,
            "local_measure_artifact": artifact,
            "local_b4_regulator_artifact": artifact,
            "zero_mode_ledger_artifact": artifact,
            "auxiliary_fourth_order_match_artifact": None,
        },
        "coefficient_result": {
            "convention": "(4 pi)^(-2) [c C2-a E4+p CdualC+b BoxR]",
            "basis": ["C2", "E4", "CdualC", "BoxR"],
            "coefficients": {
                "C2": {"numerator": 3, "denominator": 2},
                "E4": {"numerator": -5, "denominator": 4},
                "CdualC": {"numerator": 0, "denominator": 1},
                "BoxR": {"numerator": 1, "denominator": 6},
            },
            "factor_contributions": [
                {
                    "factor_id": "fixture_factor_0",
                    "coordinates": {
                        "C2": {"numerator": 1, "denominator": 1},
                        "E4": {"numerator": -1, "denominator": 1},
                        "CdualC": {"numerator": 0, "denominator": 1},
                        "BoxR": {"numerator": 1, "denominator": 6},
                    },
                },
                {
                    "factor_id": "fixture_factor_1",
                    "coordinates": {
                        "C2": {"numerator": 1, "denominator": 2},
                        "E4": {"numerator": -1, "denominator": 4},
                        "CdualC": {"numerator": 0, "denominator": 1},
                        "BoxR": {"numerator": 0, "denominator": 1},
                    },
                },
            ],
            "factor_sum_verified": True,
        },
        "consistency": {
            "parity_status": "WARD_VERIFIED",
            "parity_artifact": artifact,
            "round_S4_Euler_cross_check": {"numerator": -87, "denominator": 20},
            "round_S4_cross_check_artifact": artifact,
        },
        "classical_snapshot_compatibility_artifact": artifact,
        "claim_flags": {
            "REPOSITORY_C2_COEFFICIENT_COMPUTED": True,
            "REPOSITORY_LOCAL_EFFECTIVE_ACTION_VECTOR_COMPUTED": True,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "claim_boundary": "Synthetic receiver fixture only; these arbitrary exact coefficients test arithmetic and role handling and are not physical evidence for Weyl gravity.",
    }
    result["proof_sha256"] = _canonical_hash(
        {
            key: result[key]
            for key in (
                "classical_commit",
                "analytic_route",
                "background",
                "operator_and_measure",
                "coefficient_result",
                "consistency",
                "classical_snapshot_compatibility_artifact",
            )
        }
    )
    return result
