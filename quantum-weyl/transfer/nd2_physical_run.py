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
    from .total_d_disposition import (
        DEPENDENCY_TAG_ORDER,
        DISPOSITIONS,
        TotalDDisposition,
        validate_total_d_disposition,
    )
except ImportError:
    from arity_two_cartan import AdmissibleArityTwoComplex, ArityTwoCartanData, BilinearOperator
    from evaluator_registry import EvaluatorRegistry
    from total_d_disposition import (
        DEPENDENCY_TAG_ORDER,
        DISPOSITIONS,
        TotalDDisposition,
        validate_total_d_disposition,
    )


MANIFEST_SCHEMA = "quantum-weyl-nd2-physical-run-input-v1"
TERMINAL_STATES = ("EXACT_CORRECTION", "NONTRIVIAL_OBSTRUCTION", "ZERO_SOURCE")
D_ROUTES = {
    "OPEN": "BLOCKED_PENDING_TOTAL_D_DISPOSITION",
    "D_GAUGE": "CARTAN_CONTRACTION_EXECUTED",
    "D_CHARGED": "EQUIVARIANCE_ONLY_D_CHARGED_NO_QUOTIENT",
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
    dependency_tags: tuple[str, ...]

    @classmethod
    def from_payload(cls, payload: object) -> "PinnedArtifact":
        if not isinstance(payload, dict) or set(payload) != {
            "artifact_id",
            "path",
            "sha256",
            "dependency_tags",
        }:
            raise ValueError("physical-run artifact has the wrong field set")
        raw_tags = payload["dependency_tags"]
        if not isinstance(raw_tags, list):
            raise ValueError("physical-run artifact dependency tags must be a list")
        tags = tuple(raw_tags)
        if (
            not tags
            or len(tags) != len(set(tags))
            or any(tag not in DEPENDENCY_TAG_ORDER for tag in tags)
            or tags != tuple(tag for tag in DEPENDENCY_TAG_ORDER if tag in tags)
        ):
            raise ValueError("physical-run artifact dependency tags are invalid")
        artifact = cls(
            payload["artifact_id"],
            payload["path"],
            payload["sha256"],
            tags,
        )
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
    phase_space_id: str
    generator_id: str
    boundary_conditions_sha256: str

    @classmethod
    def from_payload(cls, payload: object) -> "DDisposition":
        if not isinstance(payload, dict) or set(payload) != {
            "status",
            "setting_id",
            "phase_space_id",
            "generator_id",
            "boundary_conditions_sha256",
        }:
            raise ValueError("ND2 total-D disposition has the wrong field set")
        disposition = cls(
            payload["status"],
            payload["setting_id"],
            payload["phase_space_id"],
            payload["generator_id"],
            payload["boundary_conditions_sha256"],
        )
        if disposition.status not in DISPOSITIONS:
            raise ValueError("ND2 total-D disposition status is invalid")
        if (
            not disposition.setting_id
            or not disposition.phase_space_id
            or disposition.generator_id != "D_compact"
        ):
            raise ValueError("ND2 total-D disposition scope is invalid")
        if (
            len(disposition.boundary_conditions_sha256) != 64
            or any(
                char not in "0123456789abcdef"
                for char in disposition.boundary_conditions_sha256
            )
        ):
            raise ValueError("ND2 total-D boundary-condition hash is invalid")
        return disposition


@dataclass(frozen=True)
class PhysicalRunManifest:
    run_id: str
    classical_commit: str
    dependency_tags: tuple[str, ...]
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
        if payload["schema"] != MANIFEST_SCHEMA:
            raise ValueError("ND2 physical-run schema is invalid")
        raw_tags = payload["dependency_tags"]
        if not isinstance(raw_tags, list):
            raise ValueError("ND2 physical-run dependency tags must be a list")
        dependency_tags = tuple(raw_tags)
        if (
            not dependency_tags
            or len(dependency_tags) != len(set(dependency_tags))
            or any(tag not in DEPENDENCY_TAG_ORDER for tag in dependency_tags)
            or dependency_tags
            != tuple(tag for tag in DEPENDENCY_TAG_ORDER if tag in dependency_tags)
            or "LOCAL-ALGEBRAIC" not in dependency_tags
        ):
            raise ValueError("ND2 physical-run dependency tags are invalid or noncanonical")
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
        artifact_dependency_union = tuple(
            tag
            for tag in DEPENDENCY_TAG_ORDER
            if any(tag in artifact.dependency_tags for artifact in artifacts)
        )
        if dependency_tags != artifact_dependency_union:
            raise ValueError(
                "ND2 physical-run dependency tags do not equal the artifact union"
            )
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
            run_id=payload["run_id"],
            classical_commit=commit,
            dependency_tags=dependency_tags,
            artifacts=tuple(sorted(artifacts, key=lambda artifact: artifact.artifact_id)),
            evaluator_id=evaluator["evaluator_id"],
            expression_schema_version=evaluator["expression_schema_version"],
            evaluator_implementation_sha256=evaluator["implementation_manifest_sha256"],
            assembly_adapter_id=payload["assembly_adapter_id"],
            D_disposition=disposition,
        )

    def verify(
        self,
        repository_root: Path,
        registry: EvaluatorRegistry,
    ) -> "VerifiedPhysicalRun":
        for artifact in self.artifacts:
            artifact.verify(repository_root)
        disposition_artifact = next(
            artifact
            for artifact in self.artifacts
            if artifact.artifact_id == "D_disposition_certificate"
        )
        try:
            disposition_payload = json.loads(
                disposition_artifact.resolved_path(repository_root).read_text(
                    encoding="utf-8"
                )
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("total-D disposition certificate is not readable JSON") from exc
        disposition = validate_total_d_disposition(disposition_payload)
        binding = self.D_disposition
        if disposition.status != binding.status:
            raise ValueError("manifest total-D disposition disagrees with its certificate")
        if disposition.setting_id != binding.setting_id:
            raise ValueError("manifest total-D setting disagrees with its certificate")
        if disposition.phase_space_id != binding.phase_space_id:
            raise ValueError("manifest total-D phase space disagrees with its certificate")
        if disposition.generator_id != binding.generator_id:
            raise ValueError("manifest total-D generator disagrees with its certificate")
        if disposition.boundary_conditions_sha256 != binding.boundary_conditions_sha256:
            raise ValueError("manifest total-D boundary conditions disagree with its certificate")
        if disposition.classical_commit != self.classical_commit:
            raise ValueError("manifest classical commit disagrees with total-D provenance")
        if disposition.dependency_tags != disposition_artifact.dependency_tags:
            raise ValueError(
                "disposition artifact dependency scope disagrees with total-D provenance"
            )
        self._verify_disposition_sources(repository_root, disposition)
        descriptor = registry.descriptor(self.evaluator_id)
        if descriptor.expression_schema_version != self.expression_schema_version:
            raise ValueError("physical-run evaluator schema mismatch")
        if descriptor.implementation_manifest_sha256 != self.evaluator_implementation_sha256:
            raise ValueError("physical-run evaluator implementation hash mismatch")
        return VerifiedPhysicalRun._create(self, disposition)

    @staticmethod
    def _verify_disposition_sources(
        repository_root: Path,
        disposition: TotalDDisposition,
    ) -> None:
        root = repository_root.resolve()
        for relative, expected in disposition.source_artifacts + disposition.source_manifest:
            path = (root / relative).resolve()
            try:
                path.relative_to(root)
            except ValueError as exc:
                raise ValueError("total-D provenance path escapes repository") from exc
            if not path.is_file() or _sha256(path) != expected:
                raise ValueError(f"total-D provenance hash mismatch: {relative}")


_VERIFIED_PHYSICAL_RUN_TOKEN = object()


@dataclass(frozen=True, init=False)
class VerifiedPhysicalRun:
    """Opaque result of verifying every physical-run artifact and scope."""

    manifest: PhysicalRunManifest
    total_D_disposition: TotalDDisposition
    _token: object

    def __init__(self, *_args, **_kwargs) -> None:
        raise TypeError("VerifiedPhysicalRun objects are created only by manifest verification")

    @classmethod
    def _create(
        cls,
        manifest: PhysicalRunManifest,
        disposition: TotalDDisposition,
    ) -> "VerifiedPhysicalRun":
        value = object.__new__(cls)
        object.__setattr__(value, "manifest", manifest)
        object.__setattr__(value, "total_D_disposition", disposition)
        object.__setattr__(value, "_token", _VERIFIED_PHYSICAL_RUN_TOKEN)
        return value

    def assert_verified(self) -> None:
        if self._token is not _VERIFIED_PHYSICAL_RUN_TOKEN:
            raise ValueError("physical-run verification token is invalid")


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
) -> VerifiedPhysicalRun:
    manifest = PhysicalRunManifest.from_payload(json.loads(path.read_text(encoding="utf-8")))
    return manifest.verify(repository_root, registry)


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
    verified_run: VerifiedPhysicalRun,
    *,
    adapter_registry: AssemblyAdapterRegistry,
) -> dict[str, Any]:
    """Route on total-D status; only ``D_GAUGE`` executes Cartan contraction."""

    if not isinstance(verified_run, VerifiedPhysicalRun):
        raise TypeError("execute_verified_manifest requires a VerifiedPhysicalRun")
    verified_run.assert_verified()
    manifest = verified_run.manifest
    disposition = verified_run.total_D_disposition
    route = D_ROUTES[disposition.status]
    if disposition.status != "D_GAUGE":
        return {
            "D_disposition": disposition.status,
            "disposition_route": route,
            "cartan_execution": None,
        }
    if not disposition.D_quotient_authorized:
        raise ValueError("D_GAUGE certificate did not authorize the quotient")

    data, admissible = adapter_registry.assemble(manifest)
    return {
        "D_disposition": disposition.status,
        "disposition_route": route,
        "cartan_execution": execute_evaluated_cartan(
            data,
            admissible_complex=admissible,
        ),
    }
