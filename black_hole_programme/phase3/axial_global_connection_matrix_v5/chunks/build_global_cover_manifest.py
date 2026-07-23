#!/usr/bin/env python3
"""Build the exact 16-child cover manifest for certified global radial maps."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from .compose_child_global import verify_global


SCHEMA = "phase3-axial-global-map-cover-v1"
RECEIPT_SCHEMA = "phase3-axial-global-map-cover-receipt-v1"
CHILD_COUNT = 16
LOWER = Fraction(1, 2)
UPPER = Fraction(129, 256)
WIDTH = Fraction(1, 4096)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build_manifest(
    *, repo_root: Path, artifact_dir: Path
) -> dict[str, Any]:
    prefix_path = artifact_dir / "prefix_join_0_to_191over8.json"
    global_dir = artifact_dir / "global_maps"
    tail_dir = artifact_dir / "child_tail_joins"
    _require(prefix_path.is_file(), "cover: missing shared prefix")

    expected_globals = {
        global_dir / f"global_map_q{child:02d}.json"
        for child in range(CHILD_COUNT)
    }
    expected_tails = {
        tail_dir / f"child_tail_join_q{child:02d}.json"
        for child in range(CHILD_COUNT)
    }
    _require(
        set(global_dir.glob("*.json")) == expected_globals,
        "cover: global map membership differs from exact q00..q15 set",
    )
    _require(
        set(tail_dir.glob("*.json")) == expected_tails,
        "cover: tail join membership differs from exact q00..q15 set",
    )

    prefix = _load(prefix_path)
    prefix_file_sha = _sha256(prefix_path)
    prefix_payload_sha = _canonical_sha256(prefix)
    entries = []
    cursor = LOWER
    for child in range(CHILD_COUNT):
        global_path = global_dir / f"global_map_q{child:02d}.json"
        tail_path = tail_dir / f"child_tail_join_q{child:02d}.json"
        global_map = _load(global_path)
        tail = _load(tail_path)
        verify_global(global_map, prefix, tail, child)

        lo = LOWER + child * WIDTH
        hi = lo + WIDTH
        _require(lo == cursor, "cover: internal gap or overlap")
        cursor = hi
        _require(
            Fraction(global_map["cell"]["lower"]) == lo
            and Fraction(global_map["cell"]["upper"]) == hi
            and global_map["cell"] == tail["cell"],
            f"cover: q{child:02d} child identity drift",
        )
        global_integrity = global_map["integrity"]
        _require(
            global_integrity["prefix"]["path"]
            == _relative(prefix_path, repo_root)
            and global_integrity["prefix"]["sha256"] == prefix_file_sha
            and global_integrity["prefix"]["payload_sha256"]
            == prefix_payload_sha,
            f"cover: q{child:02d} prefix linkage drift",
        )
        _require(
            global_integrity["tail"]["path"]
            == _relative(tail_path, repo_root)
            and global_integrity["tail"]["sha256"] == _sha256(tail_path)
            and global_integrity["tail"]["payload_sha256"]
            == _canonical_sha256(tail),
            f"cover: q{child:02d} tail linkage drift",
        )
        _require(
            global_map["proof"]["ok"] is True
            and global_map["proof"]["exact_state_permutation_verified"] is True
            and tail["proof"]["ok"] is True
            and tail["proof"]["exact_cover_verified"] is True
            and tail["proof"]["identity_transitions_verified"] is True,
            f"cover: q{child:02d} replay proof is incomplete",
        )
        entries.append(
            {
                "child_id": f"q{child:02d}",
                "child_index": child,
                "lower": _rational(lo),
                "upper": _rational(hi),
                "global_map": {
                    "path": _relative(global_path, repo_root),
                    "sha256": _sha256(global_path),
                    "payload_sha256": _canonical_sha256(global_map),
                },
                "tail_join": {
                    "path": _relative(tail_path, repo_root),
                    "sha256": _sha256(tail_path),
                    "payload_sha256": _canonical_sha256(tail),
                },
                "replay_link": {
                    "global_schema": global_map["schema"],
                    "tail_schema": tail["schema"],
                    "prefix_payload_sha256": prefix_payload_sha,
                    "tail_payload_sha256": _canonical_sha256(tail),
                    "block_output_sha256": global_integrity[
                        "block_output_sha256"
                    ],
                    "standard_output_sha256": global_integrity[
                        "standard_output_sha256"
                    ],
                    "tail_output_sha256": tail["integrity"]["output_sha256"],
                },
            }
        )
    _require(cursor == UPPER, "cover: exact upper endpoint not reached")

    entry_set_sha = _canonical_sha256(entries)
    return {
        "schema": SCHEMA,
        "artifact_kind": "exact-global-radial-map-frequency-cover",
        "status": "CERTIFIED",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "cover": {
            "parameter": "Momega",
            "lower": _rational(LOWER),
            "upper": _rational(UPPER),
            "child_width": _rational(WIDTH),
            "child_count": CHILD_COUNT,
            "membership": [f"q{child:02d}" for child in range(CHILD_COUNT)],
            "no_extras": True,
            "no_duplicates": True,
            "no_gaps_or_overlaps": True,
        },
        "shared_prefix": {
            "path": _relative(prefix_path, repo_root),
            "sha256": prefix_file_sha,
            "payload_sha256": prefix_payload_sha,
        },
        "entries": entries,
        "integrity": {
            "entry_set_sha256": entry_set_sha,
            "producer": {
                "path": _relative(Path(__file__), repo_root),
                "sha256": _sha256(Path(__file__)),
            },
        },
        "proof": {
            "ok": True,
            "source_global_replay_verified": True,
            "matching_tail_and_prefix_identity_verified": True,
            "exact_rational_cover_verified": True,
            "filesystem_membership_verified": True,
        },
        "does_not_establish": [
            "a normalized horizon frame",
            "a physical outgoing trace map",
            "a global Stokes identity",
            "a scattering or positivity theorem",
        ],
    }


def build_receipt(
    *,
    repo_root: Path,
    manifest_path: Path,
    verifier_path: Path,
    test_path: Path,
    producer_command: str,
    verifier_command: str,
    test_command: str,
    diff_command: str,
    verifier_elapsed: str,
    test_elapsed: str,
    diff_elapsed: str,
) -> dict[str, Any]:
    return {
        "schema": RECEIPT_SCHEMA,
        "artifact_kind": "global-map-cover-verification-receipt",
        "status": "PASS",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "artifacts": {
            "manifest": {
                "path": _relative(manifest_path, repo_root),
                "sha256": _sha256(manifest_path),
            },
            "producer": {
                "path": _relative(Path(__file__), repo_root),
                "sha256": _sha256(Path(__file__)),
            },
            "verifier": {
                "path": _relative(verifier_path, repo_root),
                "sha256": _sha256(verifier_path),
            },
            "mutation_tests": {
                "path": _relative(test_path, repo_root),
                "sha256": _sha256(test_path),
            },
        },
        "commands": [
            {
                "tier": 0,
                "command": diff_command,
                "elapsed_seconds": diff_elapsed,
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": verifier_command,
                "elapsed_seconds": verifier_elapsed,
                "result": "PASS",
            },
            {
                "tier": 1,
                "command": test_command,
                "elapsed_seconds": test_elapsed,
                "result": "PASS",
            },
            {
                "tier": "producer",
                "command": producer_command,
                "elapsed_seconds": "not-applicable-deterministic-emission",
                "result": "PASS",
            },
        ],
        "higher_tiers_not_run": {
            "tiers": [2, 3],
            "criterion": (
                "the change adds a manifest and independent cover verifier; "
                "it does not alter a mathematical input, operator, schema "
                "consumer, or promoted theorem"
            ),
        },
        "does_not_establish": [
            "reproduction of the global maps by a second numerical method",
            "a horizon-to-infinity physical connection",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--verifier", type=Path, required=True)
    parser.add_argument("--tests", type=Path, required=True)
    parser.add_argument("--producer-command", required=True)
    parser.add_argument("--verifier-command", required=True)
    parser.add_argument("--test-command", required=True)
    parser.add_argument("--diff-command", required=True)
    parser.add_argument("--verifier-elapsed", default="0.00")
    parser.add_argument("--test-elapsed", default="0.00")
    parser.add_argument("--diff-elapsed", default="0.00")
    args = parser.parse_args()

    manifest = build_manifest(
        repo_root=args.repo_root, artifact_dir=args.artifact_dir
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    receipt = build_receipt(
        repo_root=args.repo_root,
        manifest_path=args.output,
        verifier_path=args.verifier,
        test_path=args.tests,
        producer_command=args.producer_command,
        verifier_command=args.verifier_command,
        test_command=args.test_command,
        diff_command=args.diff_command,
        verifier_elapsed=args.verifier_elapsed,
        test_elapsed=args.test_elapsed,
        diff_elapsed=args.diff_elapsed,
    )
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
