#!/usr/bin/env python3
"""Fail-closed access to git-attached provenance after subtree extraction.

Historical certificates intentionally retain the commit ids and repository
paths from the pre-extraction monorepo.  This module translates those
references at lookup time through the content-derived standalone-history
crosswalk.  It never rewrites the historical record and never guesses.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


ROOT = Path(__file__).resolve().parent.parent
CROSSWALK = ROOT / "reports" / "standalone-history-crosswalk.json"
SCHEMA = "standalone-history-crosswalk-v1"
OLD_PREFIX = "physics/symplectic-reconstruction/"
HEX_COMMIT = re.compile(r"^[0-9a-f]{7,40}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ProvenanceResolutionError(AssertionError):
    """A historical reference cannot be resolved exactly in this repository."""


@dataclass(frozen=True)
class ResolvedRef:
    historical_commit: str
    historical_path: str
    commit: str
    path: str

    @property
    def translated(self) -> bool:
        return (
            self.historical_commit != self.commit
            or self.historical_path != self.path
        )

    @property
    def object_spec(self) -> str:
        return f"{self.commit}:{self.path}"


def _git(root: Path, args: list[str], *, input_bytes: bytes | None = None) -> bytes:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        input=input_bytes,
        capture_output=True,
    )
    if proc.returncode:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise ProvenanceResolutionError(
            f"git {' '.join(args)} failed"
            + (f": {detail}" if detail else "")
        )
    return proc.stdout


def _commit_exists(root: Path, commit: str) -> bool:
    proc = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=root,
        capture_output=True,
    )
    return proc.returncode == 0


def _validate_commit(commit: str) -> None:
    if not HEX_COMMIT.fullmatch(commit):
        raise ProvenanceResolutionError(
            f"historical commit must be a lowercase 7-to-40-hex id: {commit!r}"
        )


def normalize_repository_path(path: str) -> str:
    """Return the standalone path corresponding to a historical repo path."""
    if not isinstance(path, str) or not path:
        raise ProvenanceResolutionError("repository path must be a nonempty string")
    candidate = path[len(OLD_PREFIX):] if path.startswith(OLD_PREFIX) else path
    if not candidate:
        raise ProvenanceResolutionError(
            f"repository path resolves to the extracted repository root: {path!r}"
        )
    pure = PurePosixPath(candidate)
    if (
        pure.is_absolute()
        or "\\" in candidate
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        raise ProvenanceResolutionError(f"unsafe repository path: {path!r}")
    return pure.as_posix()


def _load_crosswalk(crosswalk_path: Path) -> dict:
    try:
        value = json.loads(crosswalk_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProvenanceResolutionError(
            f"cannot load standalone-history crosswalk {crosswalk_path}: {exc}"
        ) from exc
    if value.get("schema") != SCHEMA:
        raise ProvenanceResolutionError(
            f"unsupported standalone-history crosswalk schema: "
            f"{value.get('schema')!r}"
        )
    if value.get("unresolved_count") != 0 or value.get("unresolved"):
        raise ProvenanceResolutionError(
            "standalone-history crosswalk has unresolved in-repository pins"
        )
    if not isinstance(value.get("mapping"), dict):
        raise ProvenanceResolutionError("standalone-history mapping is missing")
    return value


def resolve_historical_commit(
    historical_commit: str,
    *,
    root: Path = ROOT,
    crosswalk_path: Path = CROSSWALK,
) -> str:
    """Resolve a historical commit id to its exact standalone image."""
    root = root.resolve()
    _validate_commit(historical_commit)
    if _commit_exists(root, historical_commit):
        return historical_commit

    crosswalk = _load_crosswalk(crosswalk_path)
    row = crosswalk["mapping"].get(historical_commit)
    if row is None:
        external = {
            item.get("old_commit"): item
            for item in crosswalk.get("external", [])
            if isinstance(item, dict)
        }
        if historical_commit in external:
            raise ProvenanceResolutionError(
                f"{historical_commit} belongs to an external repository: "
                f"{external[historical_commit].get('reason', 'unavailable')}"
            )
        raise ProvenanceResolutionError(
            f"no standalone-history mapping for {historical_commit}"
        )
    commit = row.get("new_commit", "")
    if not HEX40.fullmatch(commit):
        raise ProvenanceResolutionError(
            f"mapped standalone commit must be a full lowercase 40-hex id: "
            f"{commit!r}"
        )
    if not _commit_exists(root, commit):
        raise ProvenanceResolutionError(
            f"mapped standalone commit does not exist: {commit}"
        )
    return commit


def _resolve_blob_by_content(
    historical_commit: str,
    historical_path: str,
    expected_sha256: str,
    *,
    root: Path,
) -> tuple[ResolvedRef, bytes]:
    """Resolve a structurally unindexed pin by exact path/content history."""
    path = normalize_repository_path(historical_path)
    history = _git(
        root,
        ["log", "--format=%H", "--all", "--", path],
    ).decode("utf-8").splitlines()
    for commit in history:
        proc = subprocess.run(
            ["git", "show", f"{commit}:{path}"],
            cwd=root,
            capture_output=True,
        )
        if (
            proc.returncode == 0
            and hashlib.sha256(proc.stdout).hexdigest() == expected_sha256
        ):
            return (
                ResolvedRef(
                    historical_commit=historical_commit,
                    historical_path=historical_path,
                    commit=commit,
                    path=path,
                ),
                proc.stdout,
            )
    raise ProvenanceResolutionError(
        f"no standalone history blob matches {historical_commit}:"
        f"{historical_path} at sha256 {expected_sha256}"
    )


def resolve_attached_ref(
    historical_commit: str,
    historical_path: str,
    *,
    root: Path = ROOT,
    crosswalk_path: Path = CROSSWALK,
) -> ResolvedRef:
    """Resolve a historical commit/path pair without mutating its provenance."""
    root = root.resolve()
    _validate_commit(historical_commit)
    path = normalize_repository_path(historical_path)

    commit = resolve_historical_commit(
        historical_commit,
        root=root,
        crosswalk_path=crosswalk_path,
    )

    ref = ResolvedRef(
        historical_commit=historical_commit,
        historical_path=historical_path,
        commit=commit,
        path=path,
    )
    proc = subprocess.run(
        ["git", "cat-file", "-e", ref.object_spec],
        cwd=root,
        capture_output=True,
    )
    if proc.returncode:
        raise ProvenanceResolutionError(
            f"resolved git object does not exist: {ref.object_spec}"
        )
    return ref


def read_attached_blob(
    historical_commit: str,
    historical_path: str,
    expected_sha256: str,
    *,
    root: Path = ROOT,
    crosswalk_path: Path = CROSSWALK,
) -> tuple[ResolvedRef, bytes]:
    """Read and authenticate one pinned historical blob."""
    if not HEX64.fullmatch(expected_sha256):
        raise ProvenanceResolutionError(
            f"expected sha256 must be lowercase 64-hex: {expected_sha256!r}"
        )
    root = root.resolve()
    _validate_commit(historical_commit)
    try:
        ref = resolve_attached_ref(
            historical_commit,
            historical_path,
            root=root,
            crosswalk_path=crosswalk_path,
        )
    except ProvenanceResolutionError as exc:
        # A few records store one commit beside a collection of path/hash
        # entries, or use an abbreviated historical id.  The v1 crosswalk
        # collector cannot associate those shapes.  Exact content replay is
        # still deterministic and fail-closed, so use the same derivation
        # method here rather than guessing or editing the pin.
        if "no standalone-history mapping" not in str(exc):
            raise
        return _resolve_blob_by_content(
            historical_commit,
            historical_path,
            expected_sha256,
            root=root,
        )
    object_type = _git(root, ["cat-file", "-t", ref.object_spec])
    if object_type.strip() != b"blob":
        raise ProvenanceResolutionError(
            f"attached object is not a blob: {ref.object_spec}"
        )
    payload = _git(root, ["show", ref.object_spec])
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected_sha256:
        raise ProvenanceResolutionError(
            f"attached blob hash mismatch for {ref.object_spec}: "
            f"expected {expected_sha256}, got {actual}"
        )
    return ref, payload
