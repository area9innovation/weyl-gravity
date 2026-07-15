"""Content-addressed registry for exact local operator backends.

Operator backends validate and manipulate local differential-operator
payloads without asserting that those payloads have been assembled into the
finite ``Fraction``-valued Cartan engine.  Keeping this registry separate from
the physical evaluator registry prevents an implicit reduced-mode
specialization of a support-local result.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Iterable


BackendValidator = Callable[[dict[str, Any]], Any]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class OperatorBackendDescriptor:
    backend_id: str
    expression_schema_version: str
    coefficient_domain: str
    supported_arities: tuple[int, ...]
    capabilities: tuple[str, ...]
    implementation_manifest: tuple[tuple[str, str], ...]
    assembly_mode: str
    nd2_physical_assembly_authorized: bool

    def __post_init__(self) -> None:
        if not self.backend_id or not self.expression_schema_version:
            raise ValueError("operator backend id and schema version are required")
        if not self.coefficient_domain:
            raise ValueError("operator backend coefficient domain is required")
        if (
            not self.supported_arities
            or self.supported_arities != tuple(sorted(set(self.supported_arities)))
            or any(arity < 1 for arity in self.supported_arities)
        ):
            raise ValueError("operator backend arities must be positive, sorted, and unique")
        if not self.capabilities or self.capabilities != tuple(sorted(set(self.capabilities))):
            raise ValueError("operator backend capabilities must be sorted and unique")
        if not self.implementation_manifest:
            raise ValueError("operator backend implementation manifest is required")
        paths = [path for path, _digest in self.implementation_manifest]
        if paths != sorted(paths) or len(paths) != len(set(paths)):
            raise ValueError("operator backend manifest must be sorted and unique")
        if any(
            not path
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            for path, digest in self.implementation_manifest
        ):
            raise ValueError("operator backend manifest contains an invalid entry")
        if self.assembly_mode not in {
            "OPERATOR_VALIDATION_ONLY",
            "FINITE_EXACT_CARTAN",
            "MODULE_VALUED_CARTAN",
        }:
            raise ValueError("operator backend assembly mode is invalid")
        if self.nd2_physical_assembly_authorized and self.assembly_mode == "OPERATOR_VALIDATION_ONLY":
            raise ValueError("validation-only backend cannot authorize ND2 assembly")

    @classmethod
    def from_paths(
        cls,
        *,
        backend_id: str,
        expression_schema_version: str,
        coefficient_domain: str,
        supported_arities: Iterable[int],
        capabilities: Iterable[str],
        repository_root: Path,
        implementation_paths: Iterable[Path],
        assembly_mode: str,
        nd2_physical_assembly_authorized: bool,
    ) -> "OperatorBackendDescriptor":
        root = repository_root.resolve()
        manifest = []
        for raw_path in implementation_paths:
            path = raw_path.resolve()
            try:
                relative = path.relative_to(root).as_posix()
            except ValueError as exc:
                raise ValueError("operator backend implementation lies outside repository") from exc
            if not path.is_file():
                raise ValueError(f"operator backend implementation is missing: {relative}")
            manifest.append((relative, _sha256(path)))
        return cls(
            backend_id=backend_id,
            expression_schema_version=expression_schema_version,
            coefficient_domain=coefficient_domain,
            supported_arities=tuple(sorted(set(supported_arities))),
            capabilities=tuple(sorted(set(capabilities))),
            implementation_manifest=tuple(sorted(manifest)),
            assembly_mode=assembly_mode,
            nd2_physical_assembly_authorized=nd2_physical_assembly_authorized,
        )

    @property
    def implementation_manifest_sha256(self) -> str:
        return _canonical_hash(dict(self.implementation_manifest))

    def verify_files(self, repository_root: Path) -> None:
        root = repository_root.resolve()
        for relative, expected in self.implementation_manifest:
            path = (root / relative).resolve()
            try:
                path.relative_to(root)
            except ValueError as exc:
                raise ValueError("operator backend manifest escapes repository") from exc
            if not path.is_file() or _sha256(path) != expected:
                raise ValueError(f"operator backend implementation hash mismatch: {relative}")

    def to_payload(self) -> dict[str, object]:
        return {
            "backend_id": self.backend_id,
            "expression_schema_version": self.expression_schema_version,
            "coefficient_domain": self.coefficient_domain,
            "supported_arities": list(self.supported_arities),
            "capabilities": list(self.capabilities),
            "implementation_manifest": dict(self.implementation_manifest),
            "implementation_manifest_sha256": self.implementation_manifest_sha256,
            "assembly_mode": self.assembly_mode,
            "nd2_physical_assembly_authorized": self.nd2_physical_assembly_authorized,
        }


@dataclass(frozen=True)
class _RegisteredBackend:
    descriptor: OperatorBackendDescriptor
    validate: BackendValidator


class OperatorBackendRegistry:
    def __init__(self, repository_root: Path) -> None:
        self.repository_root = repository_root.resolve()
        self._backends: dict[str, _RegisteredBackend] = {}

    def register(
        self,
        descriptor: OperatorBackendDescriptor,
        validate: BackendValidator,
    ) -> None:
        if descriptor.backend_id in self._backends:
            raise ValueError(f"duplicate operator backend: {descriptor.backend_id}")
        descriptor.verify_files(self.repository_root)
        self._backends[descriptor.backend_id] = _RegisteredBackend(descriptor, validate)

    def descriptor(self, backend_id: str) -> OperatorBackendDescriptor:
        try:
            registered = self._backends[backend_id]
        except KeyError as exc:
            raise ValueError(f"unregistered operator backend: {backend_id}") from exc
        registered.descriptor.verify_files(self.repository_root)
        return registered.descriptor

    def descriptors(self) -> tuple[OperatorBackendDescriptor, ...]:
        return tuple(self.descriptor(backend_id) for backend_id in sorted(self._backends))

    def validate(
        self,
        backend_id: str,
        expression_schema_version: str,
        payload: dict[str, Any],
        *,
        required_arity: int,
    ) -> Any:
        descriptor = self.descriptor(backend_id)
        if descriptor.expression_schema_version != expression_schema_version:
            raise ValueError(
                f"operator backend {backend_id} does not accept {expression_schema_version}"
            )
        if required_arity not in descriptor.supported_arities:
            raise ValueError(
                f"operator backend {backend_id} does not support arity {required_arity}"
            )
        return self._backends[backend_id].validate(payload)
