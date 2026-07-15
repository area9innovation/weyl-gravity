"""Content-addressed registry for exact local-expression evaluators.

An evaluator is selected by both an identifier and an expression-schema
version.  Its complete implementation manifest is hashed at registration and
rechecked at dispatch.  This keeps the support-local consumer fail-closed while
allowing a future classical expression language to plug in without modifying
the consumer or the ND2 engine.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Iterable


Evaluator = Callable[[Any], Any]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class EvaluatorDescriptor:
    """Pinned identity and implementation provenance for one evaluator."""

    evaluator_id: str
    expression_schema_version: str
    implementation_manifest: tuple[tuple[str, str], ...]
    allowed_operator_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.evaluator_id or not self.expression_schema_version:
            raise ValueError("evaluator id and expression schema version are required")
        paths = [path for path, _digest in self.implementation_manifest]
        if paths != sorted(paths) or len(paths) != len(set(paths)):
            raise ValueError("evaluator implementation manifest must be sorted and unique")
        for path, digest in self.implementation_manifest:
            if not path or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                raise ValueError("evaluator implementation manifest contains an invalid hash")
        if not self.allowed_operator_ids or tuple(sorted(set(self.allowed_operator_ids))) != self.allowed_operator_ids:
            raise ValueError("allowed evaluator operator ids must be sorted and unique")

    @classmethod
    def from_paths(
        cls,
        *,
        evaluator_id: str,
        expression_schema_version: str,
        repository_root: Path,
        implementation_paths: Iterable[Path],
        allowed_operator_ids: Iterable[str],
    ) -> "EvaluatorDescriptor":
        root = repository_root.resolve()
        manifest = []
        for raw_path in implementation_paths:
            path = raw_path.resolve()
            try:
                relative = path.relative_to(root).as_posix()
            except ValueError as exc:
                raise ValueError("evaluator implementation lies outside repository root") from exc
            if not path.is_file():
                raise ValueError(f"evaluator implementation is missing: {relative}")
            manifest.append((relative, _sha256(path)))
        return cls(
            evaluator_id,
            expression_schema_version,
            tuple(sorted(manifest)),
            tuple(sorted(set(allowed_operator_ids))),
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
                raise ValueError("evaluator manifest escapes repository root") from exc
            if not path.is_file() or _sha256(path) != expected:
                raise ValueError(f"evaluator implementation hash mismatch: {relative}")

    def to_payload(self) -> dict[str, object]:
        return {
            "evaluator_id": self.evaluator_id,
            "expression_schema_version": self.expression_schema_version,
            "implementation_manifest": dict(self.implementation_manifest),
            "implementation_manifest_sha256": self.implementation_manifest_sha256,
            "allowed_operator_ids": list(self.allowed_operator_ids),
        }


@dataclass(frozen=True)
class _RegisteredEvaluator:
    descriptor: EvaluatorDescriptor
    evaluate: Evaluator


class EvaluatorRegistry:
    """Fail-closed evaluator dispatch keyed by id and expression schema."""

    def __init__(self, repository_root: Path) -> None:
        self.repository_root = repository_root.resolve()
        self._evaluators: dict[str, _RegisteredEvaluator] = {}

    def register(self, descriptor: EvaluatorDescriptor, evaluate: Evaluator) -> None:
        if descriptor.evaluator_id in self._evaluators:
            raise ValueError(f"duplicate evaluator id: {descriptor.evaluator_id}")
        descriptor.verify_files(self.repository_root)
        self._evaluators[descriptor.evaluator_id] = _RegisteredEvaluator(descriptor, evaluate)

    def descriptor(self, evaluator_id: str) -> EvaluatorDescriptor:
        try:
            registered = self._evaluators[evaluator_id]
        except KeyError as exc:
            raise ValueError(f"unregistered evaluator: {evaluator_id}") from exc
        registered.descriptor.verify_files(self.repository_root)
        return registered.descriptor

    def descriptors(self) -> tuple[EvaluatorDescriptor, ...]:
        return tuple(
            self.descriptor(evaluator_id)
            for evaluator_id in sorted(self._evaluators)
        )

    def dispatch(
        self,
        evaluator_id: str,
        expression_schema_version: str,
        parsed_export: Any,
    ) -> Any:
        descriptor = self.descriptor(evaluator_id)
        if descriptor.expression_schema_version != expression_schema_version:
            raise ValueError(
                f"evaluator {evaluator_id} does not accept {expression_schema_version}"
            )
        component_groups = []
        for attribute in ("q1_components", "q2_components", "D_components"):
            components = getattr(parsed_export, attribute, None)
            if components is None:
                raise ValueError("parsed export does not expose canonical operator components")
            component_groups.extend(components)
        used_operator_ids = {
            monomial.operator_id
            for component in component_groups
            for monomial, _coefficient in component.expression.terms
        }
        outside_inventory = sorted(used_operator_ids - set(descriptor.allowed_operator_ids))
        if outside_inventory:
            raise ValueError(
                f"evaluator {evaluator_id} received operators outside its declared inventory: "
                + ", ".join(outside_inventory)
            )
        return self._evaluators[evaluator_id].evaluate(parsed_export)
