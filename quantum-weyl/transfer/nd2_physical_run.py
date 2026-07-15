"""Stable physical-run contract for the ND2 arity-two Cartan calculation.

The permanent engine certificate is separate from a physical execution.  A
physical run pins the classical support-local export, contraction supplement,
admissibility policy, total-D disposition, evaluator, and assembly adapter.
Missing or mismatched objects stop before classification.  Only a certified
``D_GAUGE`` disposition reaches Cartan contraction.  Once assembled into exact
``ArityTwoCartanData``, this module returns either the retained correction or a
normalized obstruction witness.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any
from typing import Callable

try:
    from .arity_two_cartan import (
        AdmissibleArityTwoComplex,
        ArityTwoCartanData,
        BilinearOperator,
    )
    from .evaluator_registry import EvaluatorRegistry
except ImportError:
    from arity_two_cartan import AdmissibleArityTwoComplex, ArityTwoCartanData, BilinearOperator
    from evaluator_registry import EvaluatorRegistry


MANIFEST_SCHEMA = "quantum-weyl-nd2-physical-run-input-v1"
TERMINAL_STATES = ("EXACT_CORRECTION", "NONTRIVIAL_OBSTRUCTION", "ZERO_SOURCE")
D_DISPOSITIONS = (
    "OPEN",
    "D_GAUGE",
    "D_CHARGED_NO_QUOTIENT",
    "SECTOR_DEPENDENT",
    "NOT_HAMILTONIAN",
)
D_ROUTES = {
    "OPEN": "BLOCKED_PENDING_TOTAL_D_DISPOSITION",
    "D_GAUGE": "CARTAN_CONTRACTION_EXECUTED",
    "D_CHARGED_NO_QUOTIENT": "EQUIVARIANCE_ONLY_D_CHARGED_NO_QUOTIENT",
    "SECTOR_DEPENDENT": "SCOPED_DISPOSITION_REQUIRED",
    "NOT_HAMILTONIAN": "CARTAN_CONTRACTION_NOT_APPLICABLE",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _exact(value) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


@dataclass(frozen=True)
class PinnedArtifact:
    artifact_id: str
    path: str
    sha256: str

    @classmethod
    def from_payload(cls, payload: object) -> "PinnedArtifact":
        if not isinstance(payload, dict) or set(payload) != {"artifact_id", "path", "sha256"}:
            raise ValueError("physical-run artifact has the wrong field set")
        artifact = cls(payload["artifact_id"], payload["path"], payload["sha256"])
        if not artifact.artifact_id or not artifact.path:
            raise ValueError("physical-run artifact id and path are required")
        if len(artifact.sha256) != 64 or any(char not in "0123456789abcdef" for char in artifact.sha256):
            raise ValueError("physical-run artifact hash is invalid")
        return artifact

    def verify(self, repository_root: Path) -> None:
        root = repository_root.resolve()
        path = (root / self.path).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"physical-run artifact escapes repository: {self.artifact_id}") from exc
        if not path.is_file():
            raise ValueError(f"physical-run artifact is missing: {self.artifact_id}")
        if _sha256(path) != self.sha256:
            raise ValueError(f"physical-run artifact hash mismatch: {self.artifact_id}")

    def resolved_path(self, repository_root: Path) -> Path:
        root = repository_root.resolve()
        path = (root / self.path).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"physical-run artifact escapes repository: {self.artifact_id}") from exc
        return path


@dataclass(frozen=True)
class DDisposition:
    status: str
    setting_id: str
    generator_id: str

    @classmethod
    def from_payload(cls, payload: object) -> "DDisposition":
        if not isinstance(payload, dict) or set(payload) != {
            "status",
            "setting_id",
            "generator_id",
        }:
            raise ValueError("ND2 total-D disposition has the wrong field set")
        disposition = cls(payload["status"], payload["setting_id"], payload["generator_id"])
        if disposition.status not in D_DISPOSITIONS:
            raise ValueError("ND2 total-D disposition status is invalid")
        if not disposition.setting_id or disposition.generator_id != "D_compact":
            raise ValueError("ND2 total-D disposition scope is invalid")
        return disposition

    def verify_certificate(self, path: Path) -> None:
        try:
            certificate = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("total-D disposition certificate is not readable JSON") from exc
        if not isinstance(certificate, dict):
            raise ValueError("total-D disposition certificate is not a mapping")
        certified = certificate.get("D_disposition")
        if not isinstance(certified, dict) or certified.get("status") != self.status:
            raise ValueError("manifest total-D disposition disagrees with its certificate")
        if certificate.get("setting_id") != self.setting_id:
            raise ValueError("manifest total-D setting disagrees with its certificate")
        if certificate.get("generator_id") != self.generator_id:
            raise ValueError("manifest total-D generator disagrees with its certificate")
        if self.status != "OPEN" and certificate.get("claim_status") != "CERTIFIED":
            raise ValueError("terminal total-D disposition is not certified")


@dataclass(frozen=True)
class PhysicalRunManifest:
    run_id: str
    classical_commit: str
    artifacts: tuple[PinnedArtifact, ...]
    evaluator_id: str
    expression_schema_version: str
    evaluator_implementation_sha256: str
    assembly_adapter_id: str
    D_disposition: DDisposition

    @classmethod
    def from_payload(cls, payload: object) -> "PhysicalRunManifest":
        fields = {
            "schema",
            "run_id",
            "classical_commit",
            "dependency_tags",
            "artifacts",
            "evaluator",
            "assembly_adapter_id",
            "D_disposition",
        }
        if not isinstance(payload, dict) or set(payload) != fields:
            raise ValueError("ND2 physical-run manifest has the wrong field set")
        if payload["schema"] != MANIFEST_SCHEMA or payload["dependency_tags"] != ["LOCAL-ALGEBRAIC"]:
            raise ValueError("ND2 physical-run schema or dependency tag is invalid")
        commit = payload["classical_commit"]
        if not isinstance(commit, str) or len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
            raise ValueError("ND2 physical-run classical commit is invalid")
        raw_artifacts = payload["artifacts"]
        if not isinstance(raw_artifacts, list):
            raise ValueError("ND2 physical-run artifacts must be a list")
        artifacts = tuple(PinnedArtifact.from_payload(item) for item in raw_artifacts)
        ids = [artifact.artifact_id for artifact in artifacts]
        required_ids = [
            "D_disposition_certificate",
            "admissibility_policy",
            "classical_contraction",
            "support_local_q1_q2_D",
        ]
        if sorted(ids) != required_ids:
            raise ValueError("ND2 physical-run artifact inventory is incomplete or duplicated")
        evaluator = payload["evaluator"]
        if not isinstance(evaluator, dict) or set(evaluator) != {
            "evaluator_id",
            "expression_schema_version",
            "implementation_manifest_sha256",
        }:
            raise ValueError("ND2 physical-run evaluator descriptor is invalid")
        if not isinstance(payload["run_id"], str) or not payload["run_id"]:
            raise ValueError("ND2 physical-run id is required")
        if not isinstance(payload["assembly_adapter_id"], str) or not payload["assembly_adapter_id"]:
            raise ValueError("ND2 physical-run assembly adapter id is required")
        disposition = DDisposition.from_payload(payload["D_disposition"])
        return cls(
            payload["run_id"],
            commit,
            tuple(sorted(artifacts, key=lambda artifact: artifact.artifact_id)),
            evaluator["evaluator_id"],
            evaluator["expression_schema_version"],
            evaluator["implementation_manifest_sha256"],
            payload["assembly_adapter_id"],
            disposition,
        )

    def verify(self, repository_root: Path, registry: EvaluatorRegistry) -> None:
        for artifact in self.artifacts:
            artifact.verify(repository_root)
        disposition_artifact = next(
            artifact
            for artifact in self.artifacts
            if artifact.artifact_id == "D_disposition_certificate"
        )
        self.D_disposition.verify_certificate(disposition_artifact.resolved_path(repository_root))
        descriptor = registry.descriptor(self.evaluator_id)
        if descriptor.expression_schema_version != self.expression_schema_version:
            raise ValueError("physical-run evaluator schema mismatch")
        if descriptor.implementation_manifest_sha256 != self.evaluator_implementation_sha256:
            raise ValueError("physical-run evaluator implementation hash mismatch")


@dataclass(frozen=True)
class AssemblyAdapterDescriptor:
    """Content-addressed identity for a contraction/admissibility assembler."""

    adapter_id: str
    implementation_manifest: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.adapter_id:
            raise ValueError("assembly adapter id is required")
        paths = [path for path, _digest in self.implementation_manifest]
        if paths != sorted(paths) or len(paths) != len(set(paths)):
            raise ValueError("assembly adapter manifest must be sorted and unique")
        if any(
            not path
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
            for path, digest in self.implementation_manifest
        ):
            raise ValueError("assembly adapter manifest contains an invalid entry")

    @classmethod
    def from_paths(
        cls,
        *,
        adapter_id: str,
        repository_root: Path,
        implementation_paths: tuple[Path, ...],
    ) -> "AssemblyAdapterDescriptor":
        root = repository_root.resolve()
        manifest = []
        for raw_path in implementation_paths:
            path = raw_path.resolve()
            try:
                relative = path.relative_to(root).as_posix()
            except ValueError as exc:
                raise ValueError("assembly adapter implementation lies outside repository") from exc
            if not path.is_file():
                raise ValueError(f"assembly adapter implementation is missing: {relative}")
            manifest.append((relative, _sha256(path)))
        return cls(adapter_id, tuple(sorted(manifest)))

    @property
    def implementation_manifest_sha256(self) -> str:
        return hashlib.sha256(
            json.dumps(
                dict(self.implementation_manifest),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

    def verify_files(self, repository_root: Path) -> None:
        root = repository_root.resolve()
        for relative, expected in self.implementation_manifest:
            path = (root / relative).resolve()
            try:
                path.relative_to(root)
            except ValueError as exc:
                raise ValueError("assembly adapter manifest escapes repository") from exc
            if not path.is_file() or _sha256(path) != expected:
                raise ValueError(f"assembly adapter implementation hash mismatch: {relative}")

    def to_payload(self) -> dict[str, object]:
        return {
            "adapter_id": self.adapter_id,
            "implementation_manifest": dict(self.implementation_manifest),
            "implementation_manifest_sha256": self.implementation_manifest_sha256,
        }


AssemblyAdapter = Callable[
    [PhysicalRunManifest],
    tuple[ArityTwoCartanData, AdmissibleArityTwoComplex | None],
]


class AssemblyAdapterRegistry:
    """Fail-closed registry for exact contraction/admissibility assemblers."""

    def __init__(self, repository_root: Path) -> None:
        self.repository_root = repository_root.resolve()
        self._adapters: dict[str, tuple[AssemblyAdapterDescriptor, AssemblyAdapter]] = {}

    def register(self, descriptor: AssemblyAdapterDescriptor, adapter: AssemblyAdapter) -> None:
        if descriptor.adapter_id in self._adapters:
            raise ValueError(f"duplicate assembly adapter: {descriptor.adapter_id}")
        descriptor.verify_files(self.repository_root)
        self._adapters[descriptor.adapter_id] = (descriptor, adapter)

    def descriptors(self) -> tuple[AssemblyAdapterDescriptor, ...]:
        return tuple(self._adapters[key][0] for key in sorted(self._adapters))

    def assemble(
        self,
        manifest: PhysicalRunManifest,
    ) -> tuple[ArityTwoCartanData, AdmissibleArityTwoComplex | None]:
        try:
            descriptor, adapter = self._adapters[manifest.assembly_adapter_id]
        except KeyError as exc:
            raise ValueError(
                f"unregistered assembly adapter: {manifest.assembly_adapter_id}"
            ) from exc
        descriptor.verify_files(self.repository_root)
        data, admissible = adapter(manifest)
        if not isinstance(data, ArityTwoCartanData):
            raise ValueError("assembly adapter returned the wrong Cartan data type")
        if admissible is not None and not isinstance(admissible, AdmissibleArityTwoComplex):
            raise ValueError("assembly adapter returned the wrong admissibility type")
        return data, admissible


def load_manifest(
    path: Path,
    *,
    repository_root: Path,
    registry: EvaluatorRegistry,
) -> PhysicalRunManifest:
    manifest = PhysicalRunManifest.from_payload(json.loads(path.read_text(encoding="utf-8")))
    manifest.verify(repository_root, registry)
    return manifest


def _sparse(operator: BilinearOperator, data: ArityTwoCartanData) -> dict[str, object]:
    entries = []
    for output, left, right in data.complex.coordinate_slots(operator.degree):
        value = operator.entries[output][left][right]
        if value:
            entries.append([output, left, right, _exact(value)])
    return {"degree": operator.degree, "nonzero_entries": entries}


def execute_evaluated_cartan(
    data: ArityTwoCartanData,
    *,
    admissible_complex: AdmissibleArityTwoComplex | None = None,
) -> dict[str, Any]:
    """Execute a fully assembled exact physical input without claim promotion."""

    classification = data.classify(admissible_complex)
    payload: dict[str, Any] = {
        "checks": data.checks(),
        "classification": classification.status,
        "cartan_source": _sparse(classification.source, data),
        "correction": None,
        "dual_witness": None,
    }
    if classification.correction is not None:
        payload["correction"] = _sparse(classification.correction, data)
    if classification.dual_witness is not None:
        payload["dual_witness"] = [_exact(value) for value in classification.dual_witness]
    return payload


def execute_verified_manifest(
    manifest: PhysicalRunManifest,
    *,
    adapter_registry: AssemblyAdapterRegistry,
) -> dict[str, Any]:
    """Route on total-D status; only ``D_GAUGE`` executes Cartan contraction."""

    route = D_ROUTES[manifest.D_disposition.status]
    if manifest.D_disposition.status != "D_GAUGE":
        return {
            "D_disposition": manifest.D_disposition.status,
            "disposition_route": route,
            "cartan_execution": None,
        }

    data, admissible = adapter_registry.assemble(manifest)
    return {
        "D_disposition": manifest.D_disposition.status,
        "disposition_route": route,
        "cartan_execution": execute_evaluated_cartan(
            data,
            admissible_complex=admissible,
        ),
    }
