#!/usr/bin/env python3
"""Independent fail-closed verifier for the exact global-map child cover."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


SCHEMA = "phase3-axial-global-map-cover-v1"
RECEIPT_SCHEMA = "phase3-axial-global-map-cover-receipt-v1"
CHILD_COUNT = 16
LOWER = Fraction(1, 2)
UPPER = Fraction(129, 256)
WIDTH = Fraction(1, 4096)
HEX = frozenset("0123456789abcdef")


class CoverError(ValueError):
    """The cover or one of its provenance links is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CoverError(message)


def _exact_keys(value: Any, expected: set[str], where: str) -> None:
    _require(isinstance(value, dict), f"{where}: expected object")
    got = set(value)
    _require(
        got == expected,
        f"{where}: keys differ: missing={expected-got}, extra={got-expected}",
    )


def _sha(value: Any, where: str) -> str:
    _require(
        isinstance(value, str)
        and len(value) == 64
        and all(char in HEX for char in value),
        f"{where}: invalid SHA-256",
    )
    return value


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _fraction(value: Any, where: str) -> Fraction:
    _require(isinstance(value, str) and "/" in value, f"{where}: bad rational")
    try:
        numerator, denominator = value.split("/", 1)
        result = Fraction(int(numerator), int(denominator))
    except (ValueError, ZeroDivisionError) as exc:
        raise CoverError(f"{where}: bad rational") from exc
    _require(
        numerator == str(result.numerator)
        and denominator == str(result.denominator),
        f"{where}: noncanonical rational",
    )
    return result


def _safe_path(root: Path, value: Any, where: str) -> Path:
    _require(isinstance(value, str) and value, f"{where}: empty path")
    relative = Path(value)
    _require(
        not relative.is_absolute() and ".." not in relative.parts,
        f"{where}: unsafe path",
    )
    root = root.resolve()
    result = (root / relative).resolve()
    _require(root in result.parents, f"{where}: path escapes repository")
    _require(result.is_file(), f"{where}: missing file")
    return result


def _load(path: Path, where: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise CoverError(f"{where}: unreadable JSON") from exc
    _require(isinstance(value, dict), f"{where}: expected object")
    return value


def _verify_ref(
    value: Any, root: Path, where: str, *, payload: dict[str, Any] | None = None
) -> Path:
    _exact_keys(value, {"path", "sha256", "payload_sha256"}, where)
    path = _safe_path(root, value["path"], f"{where}.path")
    _require(
        _file_sha256(path) == _sha(value["sha256"], f"{where}.sha256"),
        f"{where}: file hash mismatch",
    )
    loaded = payload if payload is not None else _load(path, where)
    _require(
        _canonical_sha256(loaded)
        == _sha(value["payload_sha256"], f"{where}.payload_sha256"),
        f"{where}: payload hash mismatch",
    )
    return path


def verify_manifest(data: Any, repo_root: Path) -> bool:
    _exact_keys(
        data,
        {
            "schema",
            "artifact_kind",
            "status",
            "dependency_tags",
            "cover",
            "shared_prefix",
            "entries",
            "integrity",
            "proof",
            "does_not_establish",
        },
        "manifest",
    )
    _require(data["schema"] == SCHEMA, "manifest: wrong schema")
    _require(data["status"] == "CERTIFIED", "manifest: not certified")
    _require(
        data["dependency_tags"] == ["LORENTZIAN-CAUSAL"],
        "manifest: dependency tag drift",
    )
    cover = data["cover"]
    _exact_keys(
        cover,
        {
            "parameter",
            "lower",
            "upper",
            "child_width",
            "child_count",
            "membership",
            "no_extras",
            "no_duplicates",
            "no_gaps_or_overlaps",
        },
        "cover",
    )
    expected_ids = [f"q{child:02d}" for child in range(CHILD_COUNT)]
    _require(cover["parameter"] == "Momega", "cover: wrong parameter")
    _require(_fraction(cover["lower"], "cover.lower") == LOWER, "cover: lower")
    _require(_fraction(cover["upper"], "cover.upper") == UPPER, "cover: upper")
    _require(
        _fraction(cover["child_width"], "cover.child_width") == WIDTH,
        "cover: width",
    )
    _require(cover["child_count"] == CHILD_COUNT, "cover: child count")
    _require(cover["membership"] == expected_ids, "cover: membership drift")
    _require(
        cover["no_extras"] is True
        and cover["no_duplicates"] is True
        and cover["no_gaps_or_overlaps"] is True,
        "cover: proof flags false",
    )

    prefix_path = _verify_ref(data["shared_prefix"], repo_root, "shared_prefix")
    prefix = _load(prefix_path, "shared_prefix")
    prefix_payload_sha = _canonical_sha256(prefix)
    prefix_file_sha = _file_sha256(prefix_path)
    artifact_dir = prefix_path.parent
    entries = data["entries"]
    _require(
        isinstance(entries, list) and len(entries) == CHILD_COUNT,
        "entries: expected exactly 16",
    )
    _require(
        _canonical_sha256(entries)
        == _sha(data["integrity"]["entry_set_sha256"], "integrity.entry_set"),
        "entries: aggregate hash mismatch",
    )

    global_paths: list[Path] = []
    tail_paths: list[Path] = []
    seen_ids: set[str] = set()
    cursor = LOWER
    for child, entry in enumerate(entries):
        where = f"entries[{child}]"
        _exact_keys(
            entry,
            {
                "child_id",
                "child_index",
                "lower",
                "upper",
                "global_map",
                "tail_join",
                "replay_link",
            },
            where,
        )
        child_id = f"q{child:02d}"
        _require(
            entry["child_id"] == child_id
            and entry["child_index"] == child
            and child_id not in seen_ids,
            f"{where}: duplicate or wrong child identity",
        )
        seen_ids.add(child_id)
        lo = _fraction(entry["lower"], f"{where}.lower")
        hi = _fraction(entry["upper"], f"{where}.upper")
        _require(
            lo == cursor and hi == lo + WIDTH,
            f"{where}: gap, overlap, or wrong width",
        )
        cursor = hi

        global_path = _verify_ref(
            entry["global_map"], repo_root, f"{where}.global_map"
        )
        tail_path = _verify_ref(
            entry["tail_join"], repo_root, f"{where}.tail_join"
        )
        _require(
            global_path
            == artifact_dir / "global_maps" / f"global_map_q{child:02d}.json"
            and tail_path
            == artifact_dir
            / "child_tail_joins"
            / f"child_tail_join_q{child:02d}.json",
            f"{where}: noncanonical source path",
        )
        global_paths.append(global_path)
        tail_paths.append(tail_path)
        global_map = _load(global_path, f"{where}.global_map")
        tail = _load(tail_path, f"{where}.tail_join")
        _require(
            global_map.get("artifact_kind")
            == "infinity-final-frequency-child-global-map"
            and global_map.get("status") == "CERTIFIED",
            f"{where}: global replay status drift",
        )
        _require(
            tail.get("artifact_kind")
            == "infinity-final-frequency-child-tail-join"
            and tail.get("status") == "CERTIFIED",
            f"{where}: tail replay status drift",
        )
        global_cell = global_map.get("cell")
        tail_cell = tail.get("cell")
        _require(
            isinstance(global_cell, dict)
            and global_cell == tail_cell
            and global_cell.get("parent_child_index") == child
            and global_cell.get("parent_child_count") == CHILD_COUNT
            and _fraction(global_cell.get("lower"), f"{where}.cell.lower") == lo
            and _fraction(global_cell.get("upper"), f"{where}.cell.upper") == hi
            and _fraction(
                global_cell.get("parent_lower"), f"{where}.cell.parent_lower"
            )
            == LOWER
            and _fraction(
                global_cell.get("parent_upper"), f"{where}.cell.parent_upper"
            )
            == UPPER,
            f"{where}: source child identity drift",
        )

        global_integrity = global_map.get("integrity")
        tail_integrity = tail.get("integrity")
        _require(
            isinstance(global_integrity, dict)
            and isinstance(tail_integrity, dict),
            f"{where}: missing source integrity",
        )
        _require(
            global_integrity.get("prefix")
            == {
                "path": data["shared_prefix"]["path"],
                "sha256": prefix_file_sha,
                "payload_sha256": prefix_payload_sha,
            },
            f"{where}: global-to-prefix linkage drift",
        )
        _require(
            global_integrity.get("tail")
            == {
                "path": entry["tail_join"]["path"],
                "sha256": entry["tail_join"]["sha256"],
                "payload_sha256": entry["tail_join"]["payload_sha256"],
            },
            f"{where}: global-to-tail linkage drift",
        )
        replay = entry["replay_link"]
        _exact_keys(
            replay,
            {
                "global_schema",
                "tail_schema",
                "prefix_payload_sha256",
                "tail_payload_sha256",
                "block_output_sha256",
                "standard_output_sha256",
                "tail_output_sha256",
            },
            f"{where}.replay_link",
        )
        _require(
            replay["global_schema"] == global_map.get("schema")
            and replay["tail_schema"] == tail.get("schema")
            and replay["prefix_payload_sha256"] == prefix_payload_sha
            and replay["tail_payload_sha256"] == _canonical_sha256(tail)
            and replay["block_output_sha256"]
            == _canonical_sha256(global_map.get("block_order_map"))
            == global_integrity.get("block_output_sha256")
            and replay["standard_output_sha256"]
            == _canonical_sha256(global_map.get("standard_realified_map"))
            == global_integrity.get("standard_output_sha256")
            and replay["tail_output_sha256"]
            == _canonical_sha256(tail.get("matrix"))
            == tail_integrity.get("output_sha256"),
            f"{where}: replay identity linkage drift",
        )
        global_proof = global_map.get("proof")
        tail_proof = tail.get("proof")
        _require(
            isinstance(global_proof, dict)
            and global_proof.get("ok") is True
            and global_proof.get("exact_state_permutation_verified") is True
            and isinstance(tail_proof, dict)
            and tail_proof.get("ok") is True
            and tail_proof.get("exact_cover_verified") is True
            and tail_proof.get("identity_transitions_verified") is True,
            f"{where}: replay proof flags incomplete",
        )
    _require(cursor == UPPER, "entries: exact upper endpoint not reached")
    _require(seen_ids == set(expected_ids), "entries: missing child")

    expected_global_names = {
        f"global_map_q{child:02d}.json" for child in range(CHILD_COUNT)
    }
    expected_tail_names = {
        f"child_tail_join_q{child:02d}.json" for child in range(CHILD_COUNT)
    }
    global_dir = global_paths[0].parent
    tail_dir = tail_paths[0].parent
    _require(
        {path.name for path in global_dir.glob("*.json")}
        == expected_global_names
        == {path.name for path in global_paths},
        "filesystem: global map extras, duplicates, or omissions",
    )
    _require(
        {path.name for path in tail_dir.glob("*.json")}
        == expected_tail_names
        == {path.name for path in tail_paths},
        "filesystem: tail join extras, duplicates, or omissions",
    )
    _require(
        data["proof"]
        == {
            "ok": True,
            "source_global_replay_verified": True,
            "matching_tail_and_prefix_identity_verified": True,
            "exact_rational_cover_verified": True,
            "filesystem_membership_verified": True,
        },
        "manifest: proof drift",
    )
    _require(
        isinstance(data["does_not_establish"], list)
        and "a physical outgoing trace map" in data["does_not_establish"],
        "manifest: missing claim boundary",
    )
    return True


def verify_receipt(
    receipt: Any, manifest_path: Path, repo_root: Path
) -> bool:
    _exact_keys(
        receipt,
        {
            "schema",
            "artifact_kind",
            "status",
            "dependency_tags",
            "artifacts",
            "commands",
            "higher_tiers_not_run",
            "does_not_establish",
        },
        "receipt",
    )
    _require(receipt["schema"] == RECEIPT_SCHEMA, "receipt: wrong schema")
    _require(receipt["status"] == "PASS", "receipt: not passing")
    _require(
        receipt["dependency_tags"] == ["LORENTZIAN-CAUSAL"],
        "receipt: dependency tag drift",
    )
    _exact_keys(
        receipt["artifacts"],
        {"manifest", "producer", "verifier", "mutation_tests"},
        "receipt.artifacts",
    )
    manifest_ref = receipt["artifacts"]["manifest"]
    _exact_keys(manifest_ref, {"path", "sha256"}, "receipt.manifest")
    _require(
        manifest_ref["path"]
        == manifest_path.resolve().relative_to(repo_root.resolve()).as_posix()
        and manifest_ref["sha256"] == _file_sha256(manifest_path),
        "receipt: manifest hash drift",
    )
    for name in ("producer", "verifier", "mutation_tests"):
        ref = receipt["artifacts"][name]
        _exact_keys(ref, {"path", "sha256"}, f"receipt.{name}")
        path = _safe_path(repo_root, ref["path"], f"receipt.{name}.path")
        _require(
            _file_sha256(path) == _sha(ref["sha256"], f"receipt.{name}.sha"),
            f"receipt: {name} hash drift",
        )
    commands = receipt["commands"]
    _require(
        isinstance(commands, list)
        and len(commands) == 4
        and all(
            isinstance(item, dict)
            and set(item)
            == {"tier", "command", "elapsed_seconds", "result"}
            and isinstance(item["command"], str)
            and item["command"]
            and isinstance(item["elapsed_seconds"], str)
            and item["elapsed_seconds"]
            and item["result"] == "PASS"
            for item in commands
        ),
        "receipt: command ledger incomplete",
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    try:
        manifest = _load(args.manifest, "manifest")
        verify_manifest(manifest, args.repo_root)
        if args.receipt is not None:
            verify_receipt(
                _load(args.receipt, "receipt"), args.manifest, args.repo_root
            )
    except CoverError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print("PASS: exact q00..q15 global-map cover and provenance linkage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
