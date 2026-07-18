"""Semantic receiver for cross-commit classical snapshot compatibility."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCHEMA = HERE / "schema/classical-snapshot-compatibility-input-v1.schema.json"
HASH_KEYS = (
    "generator_hash",
    "atom_hash",
    "differential_hash",
    "dependency_hash",
    "scope_hash",
)
REQUIRED_ROLES = [
    "minimal_generator_dictionary",
    "local_atom_dictionary",
    "classical_BV_differential",
    "action_and_identity_dependencies",
    "grading_and_locality_scope",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_artifact(
    value: object, *, repository_root: Path, label: str
) -> tuple[dict[str, str], dict[str, Any]]:
    if not isinstance(value, dict) or set(value) != {"format", "path", "sha256"}:
        raise ValueError(f"{label} artifact fields drifted")
    if value["format"] != "JSON_PROOF":
        raise ValueError(f"{label} must be a JSON_PROOF")
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


def validate_classical_snapshot_compatibility(
    payload: object,
    *,
    repository_root: Path,
    expected_local_commit: str,
    expected_local_hashes: dict[str, str],
    expected_analytic_commit: str,
    allow_synthetic_fixture: bool = False,
) -> dict[str, Any]:
    """Verify equality of the frozen local-BV content across two commits."""

    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if not isinstance(payload, dict):
        raise ValueError("snapshot compatibility payload is not an object")
    local = payload["local_BV_snapshot"]
    analytic = payload["analytic_operator_snapshot"]
    if local["classical_commit"] != expected_local_commit:
        raise ValueError("snapshot compatibility local commit drifted")
    if analytic["classical_commit"] != expected_analytic_commit:
        raise ValueError("snapshot compatibility analytic commit drifted")
    if local["classical_commit"] == analytic["classical_commit"]:
        raise ValueError("snapshot compatibility bridge requires distinct commits")
    if set(expected_local_hashes) != set(HASH_KEYS):
        raise ValueError("expected local canonical hash dictionary drifted")
    if local["canonical_hashes"] != expected_local_hashes:
        raise ValueError("snapshot compatibility local canonical hashes drifted")
    if analytic["canonical_hashes"] != expected_local_hashes:
        raise ValueError("snapshot compatibility analytic canonical hashes drifted")
    if payload["matched_roles"] != REQUIRED_ROLES:
        raise ValueError("snapshot compatibility role ledger drifted")

    artifacts = [
        _validate_artifact(
            value,
            repository_root=repository_root,
            label=f"snapshot_compatibility_proof[{index}]",
        )
        for index, value in enumerate(payload["proof_artifacts"])
    ]
    if not allow_synthetic_fixture:
        by_result_id = {value.get("result_id"): value for _, value in artifacts}
        local_proof = by_result_id.get("CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2")
        analytic_proof = by_result_id.get("CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2")
        if local_proof is None or analytic_proof is None:
            raise ValueError("snapshot compatibility proof roles are incomplete")
        if (
            local_proof.get("classical_commit") != expected_local_commit
            or local_proof.get("imported_export", {}).get("canonical_hashes")
            != expected_local_hashes
        ):
            raise ValueError("snapshot compatibility local proof content drifted")
        if (
            analytic_proof.get("classical_commit") != expected_analytic_commit
            or analytic_proof.get("canonical_hashes") != expected_local_hashes
        ):
            raise ValueError("snapshot compatibility analytic proof content drifted")
    return {
        "result_id": payload["result_id"],
        "local_BV_commit": local["classical_commit"],
        "analytic_operator_commit": analytic["classical_commit"],
        "matched_hash_count": len(HASH_KEYS),
        "matched_roles": payload["matched_roles"],
        "proof_artifact_count": len(artifacts),
        "status": "SEMANTIC_RECEIVER_ACCEPTED",
    }


def synthetic_payload(
    *,
    local_commit: str,
    analytic_commit: str,
    canonical_hashes: dict[str, str],
    repository_root: Path = ROOT,
) -> dict[str, Any]:
    """Non-scientific mechanics fixture with exact equal content hashes."""

    proof_paths = (
        "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json",
        "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json",
    )
    artifacts = [
        {
            "format": "JSON_PROOF",
            "path": path,
            "sha256": _sha256(repository_root / path),
        }
        for path in proof_paths
    ]
    return {
        "schema": "quantum-weyl-classical-snapshot-compatibility-input-v1",
        "result_id": "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY",
        "result_state": "LOCAL_BV_CONTENT_HASHES_EQUAL_ACROSS_DISTINCT_COMMITS",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "local_BV_snapshot": {
            "classical_commit": local_commit,
            "canonical_hashes": canonical_hashes,
        },
        "analytic_operator_snapshot": {
            "classical_commit": analytic_commit,
            "canonical_hashes": canonical_hashes,
        },
        "matched_roles": REQUIRED_ROLES,
        "compatibility": {
            "status": "CONTENT_HASH_COMPATIBLE",
            "all_declared_hashes_equal": True,
            "semantic_receiver_replayed": True,
        },
        "proof_artifacts": artifacts,
        "claim_boundary": (
            "Synthetic compatibility-receiver fixture only. Equal declared hashes "
            "exercise the exact acceptance path but do not certify the content of "
            "an absent analytic producer at the synthetic commit."
        ),
    }
