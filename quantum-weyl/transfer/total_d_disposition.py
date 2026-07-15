"""Strict contract for a setting-scoped total-D presymplectic audit."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import PurePosixPath
from typing import Any


SCHEMA_ID = "pure-weyl-total-d-disposition-v1"
DEPENDENCY_TAG_ORDER = (
    "LOCAL-ALGEBRAIC",
    "EUCLIDEAN-SPECTRAL",
    "REDUCED-MODE",
    "LORENTZIAN-CAUSAL",
)
TERMINAL_DISPOSITIONS = (
    "D_GAUGE",
    "D_CHARGED",
    "SECTOR_DEPENDENT",
    "NOT_HAMILTONIAN",
)
DISPOSITIONS = ("OPEN",) + TERMINAL_DISPOSITIONS

_TERMINAL_AUDIT_SIGNATURES = {
    "D_GAUGE": ("INTEGRABLE", "D_IN_KERNEL", "ZERO"),
    "D_CHARGED": ("INTEGRABLE", "D_NOT_IN_KERNEL", "NONZERO"),
    "SECTOR_DEPENDENT": (
        "SECTOR_DEPENDENT",
        "SECTOR_DEPENDENT",
        "SECTOR_DEPENDENT",
    ),
    "NOT_HAMILTONIAN": ("NONINTEGRABLE", "NOT_DEFINED", "NOT_DEFINED"),
}
_EXACT_CHECKS = {
    "combined_presymplectic_contraction_derived",
    "charge_variation_identity_verified",
    "boundary_corner_terms_controlled",
    "fixed_coupling_tangent_space_classified",
    "exact_arithmetic",
}


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _require_fields(payload: object, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != fields:
        raise ValueError(f"{label} has the wrong field set")
    return payload


def _require_hash(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError(f"{label} hash is invalid")
    return value


def _require_commit(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 40
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError(f"{label} commit is invalid")
    return value


def _require_relative_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} path is required")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise ValueError(f"{label} path is noncanonical or escapes the repository")
    return value


@dataclass(frozen=True)
class TotalDDisposition:
    result_id: str
    claim_status: str
    assessment_status: str
    verdict: str | None
    setting_id: str
    phase_space_id: str
    generator_id: str
    boundary_conditions: str
    boundary_conditions_sha256: str
    classical_commit: str
    dependency_tags: tuple[str, ...]
    sector_ids: tuple[str, ...]
    D_quotient_authorized: bool
    source_artifacts: tuple[tuple[str, str, str], ...]
    source_manifest: tuple[tuple[str, str], ...]

    @property
    def status(self) -> str:
        return self.verdict if self.verdict is not None else "OPEN"

    @classmethod
    def from_payload(cls, value: object) -> "TotalDDisposition":
        payload = _require_fields(
            value,
            {
                "schema",
                "result_id",
                "lifecycle_layer",
                "claim_status",
                "assessment_status",
                "verdict",
                "setting_id",
                "phase_space_id",
                "generator_id",
                "boundary_conditions",
                "boundary_conditions_sha256",
                "classical_commit",
                "dependency_tags",
                "charge_audit",
                "sector_ledger",
                "exact_checks",
                "fail_closed",
                "verification_receipts",
                "provenance",
                "next_gate",
            },
            "total-D disposition certificate",
        )
        if payload["schema"] != SCHEMA_ID or payload["lifecycle_layer"] != "CLASSICAL_CHARGE":
            raise ValueError("total-D schema or lifecycle is invalid")
        for field in ("result_id", "setting_id", "phase_space_id", "boundary_conditions", "next_gate"):
            if not isinstance(payload[field], str) or not payload[field]:
                raise ValueError(f"total-D {field} is required")
        if payload["generator_id"] != "D_compact":
            raise ValueError("total-D generator is invalid")
        boundary_hash = _require_hash(
            payload["boundary_conditions_sha256"],
            "total-D boundary conditions",
        )
        if boundary_hash != _sha256_text(payload["boundary_conditions"]):
            raise ValueError("total-D boundary-condition hash mismatch")
        classical_commit = _require_commit(payload["classical_commit"], "total-D classical")

        raw_tags = payload["dependency_tags"]
        if not isinstance(raw_tags, list) or not raw_tags:
            raise ValueError("total-D dependency tags are required")
        tags = tuple(raw_tags)
        if (
            len(tags) != len(set(tags))
            or any(tag not in DEPENDENCY_TAG_ORDER for tag in tags)
            or tags != tuple(tag for tag in DEPENDENCY_TAG_ORDER if tag in tags)
            or "LOCAL-ALGEBRAIC" not in tags
        ):
            raise ValueError("total-D dependency tags are invalid or noncanonical")
        if (
            payload["phase_space_id"].startswith("positive_berger")
            and "REDUCED-MODE" not in tags
        ):
            raise ValueError("Berger total-D disposition lost REDUCED-MODE scope")

        claim_status = payload["claim_status"]
        assessment_status = payload["assessment_status"]
        verdict = payload["verdict"]
        if verdict is not None and verdict not in TERMINAL_DISPOSITIONS:
            raise ValueError("total-D verdict is invalid")
        if verdict is None:
            if claim_status != "OPEN" or assessment_status != "OPEN":
                raise ValueError("an open total-D audit cannot carry a certified claim")
        elif claim_status != "CERTIFIED" or assessment_status != "COMPUTED":
            raise ValueError("a terminal total-D verdict is not certified and computed")

        audit = _require_fields(
            payload["charge_audit"],
            {
                "combined_gravitational_matter_presymplectic_contraction",
                "normalization",
                "integrability",
                "allowed_fixed_coupling_delta_Q_tangent",
                "presymplectic_kernel",
                "total_D_charge_variation",
            },
            "total-D charge audit",
        )
        allowed_audit_values = {
            "combined_gravitational_matter_presymplectic_contraction": {
                "OPEN",
                "COMPUTED",
            },
            "normalization": {"OPEN", "FIXED"},
            "integrability": {"OPEN", "INTEGRABLE", "NONINTEGRABLE", "SECTOR_DEPENDENT"},
            "allowed_fixed_coupling_delta_Q_tangent": {
                "OPEN",
                "EXISTS",
                "ABSENT",
                "SECTOR_DEPENDENT",
            },
            "presymplectic_kernel": {
                "OPEN",
                "D_IN_KERNEL",
                "D_NOT_IN_KERNEL",
                "SECTOR_DEPENDENT",
                "NOT_DEFINED",
            },
            "total_D_charge_variation": {
                "OPEN",
                "ZERO",
                "NONZERO",
                "SECTOR_DEPENDENT",
                "NOT_DEFINED",
            },
        }
        if any(audit[key] not in allowed for key, allowed in allowed_audit_values.items()):
            raise ValueError("total-D charge audit contains an invalid state")

        checks = _require_fields(payload["exact_checks"], _EXACT_CHECKS, "total-D exact checks")
        if any(type(value) is not bool for value in checks.values()):
            raise ValueError("total-D exact checks must be Boolean")

        sectors = payload["sector_ledger"]
        if not isinstance(sectors, list):
            raise ValueError("total-D sector ledger must be a list")
        sector_ids: list[str] = []
        for item in sectors:
            sector = _require_fields(
                item,
                {
                    "sector_id",
                    "phase_space_id",
                    "verdict",
                    "total_D_charge_variation",
                    "presymplectic_kernel",
                },
                "total-D sector row",
            )
            if not isinstance(sector["sector_id"], str) or not sector["sector_id"]:
                raise ValueError("total-D sector id is required")
            if sector["phase_space_id"] != payload["phase_space_id"]:
                raise ValueError("total-D sector phase-space scope drifted")
            sector_signature = _TERMINAL_AUDIT_SIGNATURES.get(sector["verdict"])
            if sector_signature is None or sector["verdict"] == "SECTOR_DEPENDENT":
                raise ValueError("total-D sector verdict must be terminal and nonrecursive")
            if (
                sector["presymplectic_kernel"],
                sector["total_D_charge_variation"],
            ) != (
                sector_signature[1],
                sector_signature[2],
            ):
                raise ValueError("total-D sector verdict disagrees with its charge data")
            sector_ids.append(sector["sector_id"])
        if len(sector_ids) != len(set(sector_ids)):
            raise ValueError("total-D sector ids are duplicated")

        fail_closed = _require_fields(
            payload["fail_closed"],
            {"D_quotient_authorized", "unresolved_fields", "claim_boundary"},
            "total-D fail-closed ledger",
        )
        if type(fail_closed["D_quotient_authorized"]) is not bool:
            raise ValueError("total-D quotient authorization must be Boolean")
        if (
            not isinstance(fail_closed["unresolved_fields"], list)
            or any(not isinstance(item, str) or not item for item in fail_closed["unresolved_fields"])
            or not isinstance(fail_closed["claim_boundary"], str)
            or not fail_closed["claim_boundary"]
        ):
            raise ValueError("total-D fail-closed ledger is invalid")

        provenance = _require_fields(
            payload["provenance"],
            {"source_commit", "source_artifacts", "source_manifest", "source_manifest_sha256", "schema"},
            "total-D provenance",
        )
        if _require_commit(provenance["source_commit"], "total-D provenance") != classical_commit:
            raise ValueError("total-D provenance commit disagrees with classical commit")
        artifacts = provenance["source_artifacts"]
        if not isinstance(artifacts, list) or not artifacts:
            raise ValueError("total-D source artifacts are required")
        artifact_paths: list[str] = []
        for item in artifacts:
            artifact = _require_fields(
                item,
                {"path", "sha256", "git_commit"},
                "total-D source artifact",
            )
            _require_relative_path(artifact["path"], "total-D source artifact")
            _require_hash(artifact["sha256"], "total-D source artifact")
            _require_commit(artifact["git_commit"], "total-D source artifact")
            artifact_paths.append(artifact["path"])
        if len(artifact_paths) != len(set(artifact_paths)):
            raise ValueError("total-D source artifact paths are duplicated")
        source_manifest = provenance["source_manifest"]
        if not isinstance(source_manifest, dict) or not source_manifest:
            raise ValueError("total-D source manifest is required")
        for path, digest in source_manifest.items():
            _require_relative_path(path, "total-D source manifest")
            _require_hash(digest, "total-D source manifest")
        if _require_hash(
            provenance["source_manifest_sha256"],
            "total-D source manifest canonical",
        ) != _canonical_hash(source_manifest):
            raise ValueError("total-D source manifest canonical hash mismatch")
        if provenance["schema"] != "quantum-weyl/transfer/schema/total-d-disposition-v1.schema.json":
            raise ValueError("total-D schema provenance drifted")

        receipts = payload["verification_receipts"]
        if not isinstance(receipts, list) or not receipts:
            raise ValueError("total-D verification receipts are required")
        for item in receipts:
            receipt = _require_fields(
                item,
                {"command", "elapsed_seconds", "status", "test_tier"},
                "total-D verification receipt",
            )
            if (
                not isinstance(receipt["command"], str)
                or not receipt["command"]
                or not isinstance(receipt["elapsed_seconds"], (int, float))
                or isinstance(receipt["elapsed_seconds"], bool)
                or receipt["elapsed_seconds"] < 0
                or receipt["status"] != "PASS"
                or receipt["test_tier"] not in (0, 1, 2, 3)
            ):
                raise ValueError("total-D verification receipt is invalid")

        if verdict is None:
            if not fail_closed["unresolved_fields"] or fail_closed["D_quotient_authorized"]:
                raise ValueError("open total-D audit was not left fail-closed")
        else:
            if (
                audit["combined_gravitational_matter_presymplectic_contraction"]
                != "COMPUTED"
            ):
                raise ValueError(
                    "terminal total-D verdict lacks the combined presymplectic contraction"
                )
            if audit["normalization"] != "FIXED":
                raise ValueError("terminal total-D verdict lacks a fixed normalization")
            if audit["allowed_fixed_coupling_delta_Q_tangent"] == "OPEN":
                raise ValueError("terminal total-D verdict leaves the tangent audit open")
            if not all(checks.values()):
                raise ValueError("terminal total-D verdict has a failed exact check")
            if fail_closed["unresolved_fields"]:
                raise ValueError("terminal total-D verdict retains unresolved fields")
            expected = _TERMINAL_AUDIT_SIGNATURES[verdict]
            if (
                audit["integrability"],
                audit["presymplectic_kernel"],
                audit["total_D_charge_variation"],
            ) != expected:
                raise ValueError("terminal total-D verdict disagrees with the audit signature")
            if fail_closed["D_quotient_authorized"] is not (verdict == "D_GAUGE"):
                raise ValueError("total-D quotient authorization disagrees with the verdict")
            if verdict == "SECTOR_DEPENDENT" and not sector_ids:
                raise ValueError("sector-dependent total-D verdict lacks a sector ledger")
            if verdict != "SECTOR_DEPENDENT" and sector_ids:
                raise ValueError("non-sector total-D verdict carries an unexpected sector ledger")

        return cls(
            payload["result_id"],
            claim_status,
            assessment_status,
            verdict,
            payload["setting_id"],
            payload["phase_space_id"],
            payload["generator_id"],
            payload["boundary_conditions"],
            boundary_hash,
            classical_commit,
            tags,
            tuple(sector_ids),
            fail_closed["D_quotient_authorized"],
            tuple(
                (item["path"], item["sha256"], item["git_commit"])
                for item in artifacts
            ),
            tuple(sorted(source_manifest.items())),
        )


def validate_total_d_disposition(payload: object) -> TotalDDisposition:
    """Validate and normalize a total-D certificate without floating arithmetic."""

    return TotalDDisposition.from_payload(payload)
