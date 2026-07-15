"""Fail-closed SHA-256 provenance helpers for certificate rails.

Two digest modes are intentionally distinct:

``RAW_FILE``
    Hash the exact bytes persisted on disk.  Use this when whitespace and
    serialization are part of the receipt.

``CANONICAL_JSON``
    Parse a JSON object and hash its compact, key-sorted serialization.  Use
    this when the certificate value, rather than its presentation, is the
    authoritative input.

Callers must select a mode explicitly.  Every filesystem access is confined
to an explicit trusted root after resolving symlinks, and digest ledgers are
accepted only with an exact declared key set.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
import hashlib
import json
from pathlib import Path
from typing import Mapping, TypeAlias


JsonObject: TypeAlias = Mapping[str, object]


@unique
class DigestMode(str, Enum):
    """The serialization contract covered by a provenance digest."""

    RAW_FILE = "raw-file-sha256"
    CANONICAL_JSON = "canonical-json-sha256"


@dataclass(frozen=True)
class ProvenanceInput:
    """One named input with an explicit path and digest contract."""

    path: Path
    mode: DigestMode

    def __post_init__(self) -> None:
        if not isinstance(self.path, Path):
            raise TypeError("provenance paths must be pathlib.Path values")
        if not isinstance(self.mode, DigestMode):
            raise TypeError("provenance digest mode must be a DigestMode")


def is_sha256(value: object) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _safe_file(path: Path, *, root: Path) -> Path:
    if not isinstance(path, Path) or not isinstance(root, Path):
        raise TypeError("path and root must be pathlib.Path values")
    trusted_root = root.resolve(strict=True)
    candidate = path.resolve(strict=True)
    try:
        candidate.relative_to(trusted_root)
    except ValueError as exc:
        raise ValueError(f"provenance path escapes trusted root: {path}") from exc
    if not candidate.is_file():
        raise ValueError(f"provenance input is not a regular file: {path}")
    return candidate


def load_json_object(path: Path, *, root: Path) -> dict[str, object]:
    safe_path = _safe_file(path, root=root)
    value = json.loads(safe_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON certificate is not an object: {path}")
    return value


def digest_json_object(value: JsonObject) -> str:
    if not isinstance(value, Mapping):
        raise TypeError("canonical certificate digest requires a JSON object")
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path, *, mode: DigestMode, root: Path) -> str:
    if not isinstance(mode, DigestMode):
        raise TypeError("digest mode must be selected explicitly with DigestMode")
    safe_path = _safe_file(path, root=root)
    if mode is DigestMode.RAW_FILE:
        payload = safe_path.read_bytes()
        return hashlib.sha256(payload).hexdigest()
    if mode is DigestMode.CANONICAL_JSON:
        return digest_json_object(load_json_object(safe_path, root=root))
    raise AssertionError(f"unhandled digest mode: {mode!r}")


def require_exact_keys(
    values: Mapping[str, object], expected_keys: tuple[str, ...]
) -> None:
    if not isinstance(values, Mapping):
        raise TypeError("digest ledger must be a mapping")
    if len(set(expected_keys)) != len(expected_keys):
        raise ValueError("expected digest keys contain duplicates")
    if any(not isinstance(key, str) or not key for key in expected_keys):
        raise ValueError("expected digest keys must be nonempty strings")
    actual = set(values)
    expected = set(expected_keys)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            f"digest ledger key mismatch; missing={missing}, extra={extra}"
        )


def digest_inputs(
    inputs: Mapping[str, ProvenanceInput],
    *,
    expected_keys: tuple[str, ...],
    root: Path,
) -> dict[str, str]:
    require_exact_keys(inputs, expected_keys)
    return {
        key: digest_file(inputs[key].path, mode=inputs[key].mode, root=root)
        for key in expected_keys
    }


def validate_digest_ledger(
    recorded: object,
    expected: Mapping[str, str],
    *,
    expected_keys: tuple[str, ...],
) -> bool:
    if not isinstance(recorded, Mapping):
        return False
    try:
        require_exact_keys(recorded, expected_keys)
        require_exact_keys(expected, expected_keys)
    except (TypeError, ValueError):
        return False
    return bool(
        all(is_sha256(recorded[key]) and is_sha256(expected[key]) for key in expected_keys)
        and all(recorded[key] == expected[key] for key in expected_keys)
    )
