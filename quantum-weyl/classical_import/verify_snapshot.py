#!/usr/bin/env python3
"""Verify a classical-import snapshot without importing classical code.

This verifier intentionally checks only portable snapshot integrity and a few
small semantic guardrails.  It does not rerun or trust the classical team's
proof scripts, and it refuses Gate A until complete exported maps are present.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SNAPSHOT = Path(__file__).parent / "snapshots" / "bootstrap-v1.json"
DEFAULT_CERTIFICATE = (
    Path(__file__).parent / "certificates" / "CLASSICAL_IMPORT_CERTIFICATE.json"
)

ALLOWED_DEPENDENCY_TAGS = {
    "LOCAL-ALGEBRAIC",
    "EUCLIDEAN-SPECTRAL",
    "REDUCED-MODE",
    "LORENTZIAN-CAUSAL",
}
REQUIRED_EXPORT_IDS = {
    "field_ghost_antifield_dictionary",
    "field_gradings",
    "local_classical_bv_differential_q0",
    "gauge_fixed_nonminimal_contractions",
    "trace_sector_contraction",
    "conformal_killing_zero_modes_15",
    "residual_representation_matrices",
    "so42_structure_constants",
    "classical_inclusion_iota_cl",
    "classical_projection_pi_cl",
    "classical_homotopy_s_cl",
    "cyclic_pairing",
    "taub_moment_map_normalization",
    "bfv_suspension_convention",
    "positive_frequency_state_ledger",
    "normalized_weyl_square_representatives",
    "centered_cohomology_bases_h3_h4_h5",
    "residual_differential_q_res_0",
}
REQUIRED_FREEZE_CHECKS = {
    "q0_squared_zero",
    "pi_cl_iota_cl_identity",
    "classical_contraction_identity",
    "q0_iota_intertwining",
    "pi_q0_intertwining",
    "cyclic_compatibility",
}
REQUIRED_HASH_KEYS = {
    "field_dictionary_hash",
    "differential_hash",
    "zero_mode_basis_hash",
    "pairing_hash",
    "representative_hash",
}


class SnapshotError(RuntimeError):
    """Raised when the import manifest fails closed."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"cannot load JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SnapshotError(f"expected JSON object in {path}")
    return value


def _safe_repo_path(relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise SnapshotError(f"artifact path escapes repository: {relative}")
    resolved = (REPO_ROOT / rel).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise SnapshotError(f"artifact path escapes repository: {relative}") from exc
    return resolved


def _git_blob(commit: str, relative: str) -> bytes:
    prefix_proc = subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if prefix_proc.returncode != 0:
        raise SnapshotError("cannot determine the workspace prefix inside the Git repository")
    git_relative = prefix_proc.stdout.strip() + relative
    proc = subprocess.run(
        ["git", "show", f"{commit}:{git_relative}"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    )
    if proc.returncode != 0:
        message = proc.stderr.decode("utf-8", errors="replace").strip()
        raise SnapshotError(
            f"artifact is unavailable at classical commit {commit}: {relative}: {message}"
        )
    return proc.stdout


def _validate_shape(snapshot: dict[str, Any]) -> None:
    if snapshot.get("schema") != "quantum-weyl-classical-import-v1":
        raise SnapshotError("unsupported snapshot schema")

    commit = snapshot.get("classical_commit")
    if not isinstance(commit, str) or len(commit) != 40 or any(
        char not in "0123456789abcdef" for char in commit
    ):
        raise SnapshotError("classical_commit must be a full lowercase Git object id")

    tags = snapshot.get("dependency_tags")
    if not isinstance(tags, list) or not tags or len(tags) != len(set(tags)):
        raise SnapshotError("dependency_tags must be a nonempty unique list")
    if not set(tags) <= ALLOWED_DEPENDENCY_TAGS:
        raise SnapshotError("snapshot contains an unknown dependency tag")
    if tags != ["LOCAL-ALGEBRAIC"]:
        raise SnapshotError("classical import bootstrap must be LOCAL-ALGEBRAIC only")

    hashes = snapshot.get("required_hashes")
    if not isinstance(hashes, dict) or set(hashes) != REQUIRED_HASH_KEYS:
        raise SnapshotError("required_hashes has the wrong key set")

    exports = snapshot.get("required_exports")
    if not isinstance(exports, list):
        raise SnapshotError("required_exports must be a list")
    export_ids = [record.get("export_id") for record in exports if isinstance(record, dict)]
    if len(export_ids) != len(exports) or len(export_ids) != len(set(export_ids)):
        raise SnapshotError("required export ids must be present and unique")
    if set(export_ids) != REQUIRED_EXPORT_IDS:
        missing = sorted(REQUIRED_EXPORT_IDS - set(export_ids))
        extra = sorted(set(export_ids) - REQUIRED_EXPORT_IDS)
        raise SnapshotError(f"wrong required export inventory; missing={missing}, extra={extra}")

    for record in exports:
        status = record.get("status")
        artifacts = record.get("artifacts")
        if status not in {"AVAILABLE", "INCOMPLETE", "NOT_AVAILABLE"}:
            raise SnapshotError(f"bad export status for {record.get('export_id')}")
        if not isinstance(artifacts, list):
            raise SnapshotError(f"artifacts must be a list for {record.get('export_id')}")
        if status == "AVAILABLE" and not artifacts:
            raise SnapshotError(f"AVAILABLE export has no artifact: {record.get('export_id')}")
        if status == "NOT_AVAILABLE" and artifacts:
            raise SnapshotError(
                f"NOT_AVAILABLE export cannot silently carry artifacts: {record.get('export_id')}"
            )
        if not isinstance(record.get("reason"), str) or not record["reason"]:
            raise SnapshotError(f"missing export reason for {record.get('export_id')}")

    checks = snapshot.get("freeze_checks")
    if not isinstance(checks, list):
        raise SnapshotError("freeze_checks must be a list")
    check_ids = [record.get("check_id") for record in checks if isinstance(record, dict)]
    if len(check_ids) != len(checks) or len(check_ids) != len(set(check_ids)):
        raise SnapshotError("freeze check ids must be present and unique")
    if set(check_ids) != REQUIRED_FREEZE_CHECKS:
        raise SnapshotError("freeze check inventory is incomplete")
    for record in checks:
        if record.get("status") not in {
            "VERIFIED",
            "BLOCKED_MISSING_EXPORT",
            "FAILED",
        }:
            raise SnapshotError(f"bad freeze check status for {record.get('check_id')}")


def _verify_artifacts(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    verified: dict[str, dict[str, Any]] = {}
    commit = snapshot["classical_commit"]
    for export in snapshot["required_exports"]:
        for artifact in export["artifacts"]:
            relative = artifact.get("path")
            expected = artifact.get("sha256")
            if not isinstance(relative, str) or not isinstance(expected, str):
                raise SnapshotError(f"malformed artifact in {export['export_id']}")
            if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
                raise SnapshotError(f"invalid artifact digest for {relative}")

            if relative in verified:
                if verified[relative]["sha256"] != expected:
                    raise SnapshotError(f"conflicting hashes for repeated artifact {relative}")
                continue

            path = _safe_repo_path(relative)
            try:
                working_data = path.read_bytes()
            except OSError as exc:
                raise SnapshotError(f"cannot read artifact {relative}: {exc}") from exc
            working_hash = _sha256(working_data)
            if working_hash != expected:
                raise SnapshotError(
                    f"working-tree hash mismatch for {relative}: {working_hash} != {expected}"
                )

            commit_hash = _sha256(_git_blob(commit, relative))
            if commit_hash != expected:
                raise SnapshotError(
                    f"classical-commit hash mismatch for {relative}: {commit_hash} != {expected}"
                )
            verified[relative] = {
                "sha256": expected,
                "working_tree_matches": True,
                "classical_commit_matches": True,
            }
    return verified


def _semantic_evidence_checks() -> list[dict[str, Any]]:
    zero_modes = _load_json(
        REPO_ROOT
        / "field_bv_identification/gauge_fixed_equivalence/certificates/zero_mode_preservation.json"
    )
    residual = _load_json(REPO_ROOT / "bridge/certificates/residual_bfv.json")
    completed_h4 = _load_json(
        REPO_ROOT / "analytic_completion/certificates/completed_H4.json"
    )
    metric = _load_json(REPO_ROOT / "bridge/certificates/metric_to_residual.json")

    checks = [
        {
            "check_id": "zero_mode_ledger_has_15_unique_labels",
            "passed": zero_modes.get("zero_mode_dimension") == 15
            and len(zero_modes.get("labels", [])) == 15
            and len(set(zero_modes.get("labels", []))) == 15,
        },
        {
            "check_id": "residual_bfv_has_15_unique_generators",
            "passed": residual.get("dimension") == 15
            and len(residual.get("basis", [])) == 15
            and len(set(residual.get("basis", []))) == 15,
        },
        {
            "check_id": "completed_centered_h4_names_and_gram",
            "passed": completed_h4.get("centered", {}).get("classes")
            == ["W_+^2", "W_-^2"]
            and completed_h4.get("centered", {}).get("normalized_gram")
            == [[1, 0], [0, 1]],
        },
        {
            "check_id": "metric_residual_h4_dimension_and_gram",
            "passed": metric.get("two_particle", {}).get("h4") == 2
            and metric.get("two_particle", {}).get("normalized_gram")
            == [[1, 0], [0, 1]],
        },
    ]
    failed = [check["check_id"] for check in checks if not check["passed"]]
    if failed:
        raise SnapshotError(f"semantic evidence checks failed: {failed}")
    return checks


def build_certificate(snapshot_path: Path = DEFAULT_SNAPSHOT) -> dict[str, Any]:
    snapshot_path = snapshot_path.resolve()
    snapshot = _load_json(snapshot_path)
    _validate_shape(snapshot)
    artifacts = _verify_artifacts(snapshot)
    semantic_inputs = {
        "field_bv_identification/gauge_fixed_equivalence/certificates/zero_mode_preservation.json",
        "bridge/certificates/residual_bfv.json",
        "analytic_completion/certificates/completed_H4.json",
        "bridge/certificates/metric_to_residual.json",
    }
    unpinned_semantic_inputs = sorted(semantic_inputs - set(artifacts))
    if unpinned_semantic_inputs:
        raise SnapshotError(
            f"semantic evidence inputs are not pinned by the snapshot: {unpinned_semantic_inputs}"
        )
    evidence_checks = _semantic_evidence_checks()

    incomplete = sorted(
        record["export_id"]
        for record in snapshot["required_exports"]
        if record["status"] != "AVAILABLE"
    )
    blocked_checks = sorted(
        record["check_id"]
        for record in snapshot["freeze_checks"]
        if record["status"] != "VERIFIED"
    )
    null_hashes = sorted(
        key for key, value in snapshot["required_hashes"].items() if value is None
    )
    gate_a_accepted = not incomplete and not blocked_checks and not null_hashes
    expected_gate_status = "VERIFIED" if gate_a_accepted else "FAIL_CLOSED"
    if snapshot.get("gate_a_status") != expected_gate_status:
        raise SnapshotError(
            "declared gate_a_status disagrees with exports, hashes, and independent checks"
        )

    relative_snapshot = snapshot_path.relative_to(REPO_ROOT).as_posix()
    return {
        "result_id": "CLASSICAL_IMPORT_CERTIFICATE",
        "schema": "quantum-weyl-classical-import-certificate-v1",
        "classical_commit": snapshot["classical_commit"],
        "classical_schema_version": snapshot["classical_schema_version"],
        "dependency_tags": snapshot["dependency_tags"],
        "claim_state": snapshot["claim_state"],
        "snapshot": relative_snapshot,
        "snapshot_sha256": _sha256(snapshot_path.read_bytes()),
        "artifact_integrity_status": "VERIFIED",
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "evidence_integrity_checks": evidence_checks,
        "required_hashes": snapshot["required_hashes"],
        "missing_or_incomplete_exports": incomplete,
        "blocked_or_failed_freeze_checks": blocked_checks,
        "gate_a_status": expected_gate_status,
        "publishable_quantum_results_allowed": gate_a_accepted,
        "notes": (
            "Artifact integrity is verified at the pinned classical commit and in the "
            "working tree. Gate A remains fail-closed because this is not an independent "
            "verification of the missing complete classical exports."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare generated output with the checked-in certificate",
    )
    parser.add_argument(
        "--certificate", type=Path, default=DEFAULT_CERTIFICATE
    )
    args = parser.parse_args(argv)

    try:
        rendered = _canonical_json(build_certificate(args.snapshot))
        if args.check:
            try:
                checked_in = args.certificate.read_text(encoding="utf-8")
            except OSError as exc:
                raise SnapshotError(f"cannot read checked-in certificate: {exc}") from exc
            if checked_in != rendered:
                raise SnapshotError("checked-in classical import certificate is stale")
        else:
            sys.stdout.write(rendered)
    except SnapshotError as exc:
        print(f"CLASSICAL_IMPORT_FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
