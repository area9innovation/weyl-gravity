#!/usr/bin/env python3
"""Fail-closed preflight for a portable classical antifield export."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REQUIRED_ROLES = {
    "metric_antifield": {"ghost_number": -1, "antifield_number": 1, "Grassmann_parity": 1},
    "diffeomorphism_ghost_antifield": {"ghost_number": -2, "antifield_number": 2, "Grassmann_parity": 0},
    "weyl_ghost_antifield": {"ghost_number": -2, "antifield_number": 2, "Grassmann_parity": 0},
}
REQUIRED_CHECKS = {
    "delta_squared_zero",
    "delta_gamma_anticommutator_zero",
    "Q_decomposition_sums_to_Q_image",
    "Q_squared_zero",
}
HASH_KEYS = {"generator_dictionary_hash", "q_image_hash", "filtration_hash"}
TOP_LEVEL_FIELDS = {
    "schema",
    "classical_commit",
    "dependency_tags",
    "expression_schema_version",
    "generators",
    "filtration_checks",
    "canonical_hashes",
}


class AntifieldExportError(RuntimeError):
    """Raised when a purported portable antifield export is incomplete."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AntifieldExportError(f"cannot load antifield export: {exc}") from exc
    if not isinstance(value, dict):
        raise AntifieldExportError("antifield export must be a JSON object")
    return value


def _exact_payload(value: object, path: str = "$") -> None:
    """Reject floating-point values recursively from certificate data."""

    if isinstance(value, float):
        raise AntifieldExportError(f"floating-point value forbidden at {path}")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise AntifieldExportError(f"non-string object key at {path}")
            _exact_payload(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _exact_payload(child, f"{path}[{index}]")


def _nonempty_object(record: dict[str, Any], field: str, symbol: str) -> None:
    value = record.get(field)
    if not isinstance(value, dict) or not value:
        raise AntifieldExportError(f"{symbol}: {field} must be a nonempty object")


def _is_exact_number(value: object) -> bool:
    if isinstance(value, int) and not isinstance(value, bool):
        return True
    return (
        isinstance(value, dict)
        and set(value) == {"numerator", "denominator"}
        and isinstance(value["numerator"], int)
        and not isinstance(value["numerator"], bool)
        and isinstance(value["denominator"], int)
        and not isinstance(value["denominator"], bool)
        and value["denominator"] != 0
    )


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _verify_pinned_artifact(
    repository_root: Path,
    classical_commit: str,
    relative: str,
    expected_sha256: str,
) -> None:
    root = repository_root.resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise AntifieldExportError(f"proof artifact escapes repository root: {relative}") from exc
    try:
        working_data = path.read_bytes()
    except OSError as exc:
        raise AntifieldExportError(f"cannot read proof artifact {relative}: {exc}") from exc
    if hashlib.sha256(working_data).hexdigest() != expected_sha256:
        raise AntifieldExportError(f"working-tree proof hash mismatch: {relative}")

    prefix = subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if prefix.returncode != 0:
        raise AntifieldExportError("repository_root is not inside a Git worktree")
    git_relative = prefix.stdout.strip() + relative
    committed = subprocess.run(
        ["git", "show", f"{classical_commit}:{git_relative}"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if committed.returncode != 0:
        raise AntifieldExportError(
            f"proof artifact is absent at classical_commit: {relative}"
        )
    if hashlib.sha256(committed.stdout).hexdigest() != expected_sha256:
        raise AntifieldExportError(f"classical-commit proof hash mismatch: {relative}")


def validate_export(
    payload: dict[str, Any],
    *,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    """Validate shape, exactness, minimal roles, filtration rows, and hashes."""

    _exact_payload(payload)
    if set(payload) != TOP_LEVEL_FIELDS:
        raise AntifieldExportError("antifield export has the wrong top-level field set")
    if payload.get("schema") != "quantum-weyl-antifield-export-v1":
        raise AntifieldExportError("unsupported antifield export schema")
    commit = payload.get("classical_commit")
    if not isinstance(commit, str) or len(commit) != 40 or any(
        character not in "0123456789abcdef" for character in commit
    ):
        raise AntifieldExportError("classical_commit must be a full lowercase Git id")
    if payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        raise AntifieldExportError("antifield export must be LOCAL-ALGEBRAIC only")
    if not isinstance(payload.get("expression_schema_version"), str) or not payload[
        "expression_schema_version"
    ]:
        raise AntifieldExportError("expression_schema_version is required")

    generators = payload.get("generators")
    if not isinstance(generators, list) or len(generators) < 3:
        raise AntifieldExportError("at least three antifield generators are required")
    symbols: set[str] = set()
    roles: dict[str, dict[str, Any]] = {}
    required_fields = {
        "symbol",
        "role",
        "sector",
        "tensor_type",
        "ghost_number",
        "antifield_number",
        "form_degree",
        "Grassmann_parity",
        "mass_dimension",
        "Weyl_weight",
        "Q_image",
        "Q_decomposition",
        "canonical_index_symmetry",
        "equation_or_identity_row",
    }
    for generator in generators:
        if not isinstance(generator, dict) or set(generator) != required_fields:
            raise AntifieldExportError("each generator must carry the exact required field set")
        symbol = generator["symbol"]
        if not isinstance(symbol, str) or not symbol or symbol in symbols:
            raise AntifieldExportError("generator symbols must be nonempty and unique")
        symbols.add(symbol)
        role = generator["role"]
        if role not in {*REQUIRED_ROLES, "other_antifield"}:
            raise AntifieldExportError(f"{symbol}: unknown antifield role")
        if role in REQUIRED_ROLES and role in roles:
            raise AntifieldExportError(f"duplicate antifield role: {role}")
        if role in REQUIRED_ROLES:
            roles[role] = generator
        if generator["sector"] not in {"minimal", "nonminimal", "auxiliary"}:
            raise AntifieldExportError(f"{symbol}: invalid sector")
        if not isinstance(generator["form_degree"], int) or not 0 <= generator[
            "form_degree"
        ] <= 4:
            raise AntifieldExportError(f"{symbol}: invalid form degree")
        if not isinstance(generator["ghost_number"], int) or isinstance(
            generator["ghost_number"], bool
        ):
            raise AntifieldExportError(f"{symbol}: invalid ghost number")
        if (
            not isinstance(generator["antifield_number"], int)
            or isinstance(generator["antifield_number"], bool)
            or generator["antifield_number"] < 1
        ):
            raise AntifieldExportError(f"{symbol}: invalid antifield number")
        if generator["Grassmann_parity"] not in {0, 1}:
            raise AntifieldExportError(f"{symbol}: invalid Grassmann parity")
        for field in ("mass_dimension", "Weyl_weight"):
            if not _is_exact_number(generator[field]):
                raise AntifieldExportError(f"{symbol}: {field} must be exact")
        for field in (
            "tensor_type",
            "Q_image",
            "canonical_index_symmetry",
            "equation_or_identity_row",
        ):
            _nonempty_object(generator, field, symbol)
        decomposition = generator["Q_decomposition"]
        if not isinstance(decomposition, dict) or set(decomposition) != {
            "delta",
            "gamma",
            "Q_gt0",
        }:
            raise AntifieldExportError(f"{symbol}: incomplete Q filtration")
        expected_shifts = {"delta": -1, "gamma": 0}
        for row_name, row in (
            ("delta", decomposition["delta"]),
            ("gamma", decomposition["gamma"]),
        ):
            if not isinstance(row, dict) or set(row) != {
                "antifield_number_shift",
                "image",
            }:
                raise AntifieldExportError(f"{symbol}: malformed {row_name} row")
            if not isinstance(row["image"], dict):
                raise AntifieldExportError(f"{symbol}: {row_name} image must be an object")
            if row_name in expected_shifts and row["antifield_number_shift"] != expected_shifts[row_name]:
                raise AntifieldExportError(f"{symbol}: wrong {row_name} antifield-number shift")
        higher_rows = decomposition["Q_gt0"]
        if not isinstance(higher_rows, list):
            raise AntifieldExportError(f"{symbol}: Q_gt0 must be a component list")
        higher_shifts: set[int] = set()
        for row in higher_rows:
            if not isinstance(row, dict) or set(row) != {
                "antifield_number_shift",
                "image",
            }:
                raise AntifieldExportError(f"{symbol}: malformed Q_gt0 component")
            shift = row["antifield_number_shift"]
            if not isinstance(shift, int) or isinstance(shift, bool) or shift < 1:
                raise AntifieldExportError(
                    f"{symbol}: Q_gt0 components must have positive filtration degree"
                )
            if shift in higher_shifts:
                raise AntifieldExportError(f"{symbol}: duplicate Q_gt0 filtration degree")
            higher_shifts.add(shift)
            if not isinstance(row["image"], dict):
                raise AntifieldExportError(f"{symbol}: Q_gt0 image must be an object")

    missing_roles = set(REQUIRED_ROLES) - set(roles)
    if missing_roles:
        raise AntifieldExportError(f"missing minimal antifield roles: {sorted(missing_roles)}")
    for role, expected in REQUIRED_ROLES.items():
        generator = roles[role]
        if generator["sector"] != "minimal":
            raise AntifieldExportError(f"{role} must be in the minimal sector")
        for field, value in expected.items():
            if generator[field] != value:
                raise AntifieldExportError(f"{role}: expected {field}={value}")

    checks = payload.get("filtration_checks")
    if not isinstance(checks, list):
        raise AntifieldExportError("filtration_checks must be a list")
    check_ids = [check.get("check_id") for check in checks if isinstance(check, dict)]
    if len(check_ids) != len(checks) or set(check_ids) != REQUIRED_CHECKS:
        raise AntifieldExportError("filtration check inventory is incomplete or duplicated")
    for check in checks:
        if set(check) != {"check_id", "status", "proof_artifact"}:
            raise AntifieldExportError(f"{check.get('check_id')}: malformed check row")
        if check.get("status") != "VERIFIED":
            raise AntifieldExportError(f"{check.get('check_id')}: must be VERIFIED")
        proof = check.get("proof_artifact")
        if not isinstance(proof, dict) or set(proof) != {"path", "sha256"}:
            raise AntifieldExportError(f"{check.get('check_id')}: malformed proof artifact")
        if not isinstance(proof["path"], str) or not proof["path"]:
            raise AntifieldExportError(f"{check.get('check_id')}: missing proof path")
        proof_path = Path(proof["path"])
        if proof_path.is_absolute() or ".." in proof_path.parts:
            raise AntifieldExportError(f"{check.get('check_id')}: unsafe proof path")
        digest = proof["sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise AntifieldExportError(f"{check.get('check_id')}: malformed proof digest")
        if repository_root is not None:
            _verify_pinned_artifact(repository_root, commit, proof["path"], digest)

    hashes = payload.get("canonical_hashes")
    if not isinstance(hashes, dict) or set(hashes) != HASH_KEYS:
        raise AntifieldExportError("canonical_hashes has the wrong key set")
    expected_hashes = {
        "generator_dictionary_hash": _digest(
            [
                {key: value for key, value in generator.items() if key not in {"Q_image", "Q_decomposition"}}
                for generator in generators
            ]
        ),
        "q_image_hash": _digest([generator["Q_image"] for generator in generators]),
        "filtration_hash": _digest(
            {
                "rows": [generator["Q_decomposition"] for generator in generators],
                "checks": checks,
            }
        ),
    }
    if hashes != expected_hashes:
        raise AntifieldExportError("canonical antifield export hashes do not reproduce")

    return {
        "status": "PREFLIGHT_VERIFIED",
        "classical_commit": commit,
        "generator_count": len(generators),
        "minimal_roles": sorted(REQUIRED_ROLES),
        "filtration_checks": sorted(REQUIRED_CHECKS),
        "proof_artifact_integrity_status": (
            "VERIFIED" if repository_root is not None else "NOT_CHECKED"
        ),
        "canonical_hashes": hashes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    parser.add_argument(
        "--repository-root",
        type=Path,
        help="also verify proof bytes in the working tree and at classical_commit",
    )
    args = parser.parse_args()
    try:
        result = validate_export(
            _load(args.export), repository_root=args.repository_root
        )
    except AntifieldExportError as exc:
        print(f"ANTIFIELD_EXPORT_FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
