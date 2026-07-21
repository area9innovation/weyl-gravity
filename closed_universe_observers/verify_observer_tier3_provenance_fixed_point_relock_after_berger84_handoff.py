#!/usr/bin/env python3
"""Independently verify the Observer Tier-3 relock shortfall manifest."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT
    / "closed_universe_observers/receipts/"
    "OBSERVER_TIER3_PROVENANCE_FIXED_POINT_RELOCK_AFTER_BERGER84_HANDOFF_V1_MANIFEST.json"
)
REPO_PREFIX = "physics/symplectic-reconstruction/"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def baseline_json(commit: str, path: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{REPO_PREFIX}{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return json.loads(proc.stdout)


def scrub_hash_provenance(value: Any) -> Any:
    if isinstance(value, list):
        return [scrub_hash_provenance(item) for item in value]
    if isinstance(value, dict):
        return {
            key: scrub_hash_provenance(item)
            for key, item in value.items()
            if key not in {"dependency_refs", "provenance"}
            and not key.lower().endswith("sha256")
        }
    return value


def iter_path_hash_refs(value: Any):
    if isinstance(value, list):
        for item in value:
            yield from iter_path_hash_refs(item)
    elif isinstance(value, dict):
        if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            yield value["path"], value["sha256"]
        for item in value.values():
            yield from iter_path_hash_refs(item)


def verify_manifest(manifest: dict[str, Any]) -> None:
    assert manifest["schema"] == "closed-universe-observer-tier3-provenance-fixed-point-manifest-v1"
    assert manifest["disposition"] == "SHORTFALL"
    assert manifest["relock_count"] == len(manifest["relocks"]) == 22
    assert len({entry["path"] for entry in manifest["relocks"]}) == 22
    assert len({entry["result_id"] for entry in manifest["relocks"]}) == 22

    baseline = manifest["baseline_commit"]
    for entry in manifest["relocks"]:
        current_path = ROOT / entry["path"]
        assert current_path.is_file(), entry["path"]
        assert sha256_path(current_path) == entry["new_sha256"], entry["result_id"]
        old = baseline_json(baseline, entry["path"])
        assert sha256_bytes(
            subprocess.run(
                ["git", "show", f"{baseline}:{REPO_PREFIX}{entry['path']}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
        ) == entry["old_sha256"], entry["result_id"]
        current = json.loads(current_path.read_text())
        assert current["result_id"] == entry["result_id"]
        assert entry["mutation_status"] == "PASS"
        for support in (
            entry["producer"],
            entry["independent_verifier"],
            entry["mutation_test"],
        ):
            assert (ROOT / support).is_file(), support

        old_projection = scrub_hash_provenance(old)
        current_projection = scrub_hash_provenance(current)
        if entry["scientific_comparison"] == "PIN_ONLY_IDENTICAL_AFTER_HASH_SCRUB":
            assert old_projection == current_projection, entry["result_id"]
        else:
            assert entry["scientific_comparison"] == "DETERMINISTIC_NORMALIZATION_PAYLOAD_UPDATE"
            assert entry["result_id"] == "BERGER_84_ROW_MIXED_R_KAPPA_UNARY_GATE"
            assert old_projection["q10_formal_green_correction"] == current_projection[
                "q10_formal_green_correction"
            ]
            field = "q10_memory_transport"
            assert field in old_projection and field in current_projection
            assert old_projection[field] != current_projection[field]
            del old_projection[field]
            del current_projection[field]
            assert old_projection == current_projection

        for ref_path, expected_sha in iter_path_hash_refs(current):
            resolved = ROOT / ref_path
            assert resolved.is_file(), f"missing referenced input {ref_path}"
            assert sha256_path(resolved) == expected_sha, f"stale referenced input {ref_path}"

    iterations = manifest["suite_iterations"]
    assert [row["iteration"] for row in iterations] == list(range(14))
    assert all(row["failed"] == 1 and row["elapsed_seconds"] > 0 for row in iterations)
    terminal = iterations[-1]
    assert terminal["passed_before_fail"] == 808
    assert terminal["failure_kind"] == "NON_PROVENANCE_SEMANTIC_CENSUS_FRONTIER"
    frontier = manifest["terminal_frontier"]
    assert frontier["expected_count"] == 5
    assert frontier["discovered_count"] == 7
    assert frontier["unclassified_ids"] == [
        "observer.berger.legacy_receiver_admissibility_replay",
        "observer.berger.legacy_receiver_operational_frequency_ratio_nonactivation",
    ]
    flags = manifest["flags"]
    assert flags["ZERO_STALE_PINS_IN_RELOCKED_SET"]
    assert not flags["ZERO_REMAINING_CORPUS_STALE_PINS_CERTIFIED"]
    assert not flags["OBSERVER_STREAM_TIER3_GREEN"]
    assert not flags["PAPER_9_FREEZE_GATE_ACTIVATED"]


def main() -> None:
    verify_manifest(json.loads(MANIFEST.read_text()))
    print("OBSERVER_TIER3_PROVENANCE_FIXED_POINT_RELOCK shortfall manifest verification: PASS")


if __name__ == "__main__":
    main()
