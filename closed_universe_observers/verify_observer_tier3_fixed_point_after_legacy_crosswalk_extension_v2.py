#!/usr/bin/env python3
"""Independently verify the post-crosswalk Observer Tier-3 obstruction."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
MANIFEST = (
    ROOT
    / "closed_universe_observers/receipts/"
    "OBSERVER_TIER3_FIXED_POINT_AFTER_LEGACY_CROSSWALK_EXTENSION_V2_OBSTRUCTION.json"
)
REPO_PREFIX = "physics/symplectic-reconstruction/"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_assignment(path: Path, name: str) -> Any:
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"missing literal assignment {name}")


def verify_materialization(commit: str, expected_count: int) -> None:
    listing = subprocess.run(
        ["git", "ls-tree", "-r", "-z", commit, "--", REPO_PREFIX.rstrip("/")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    records = [record for record in listing.split(b"\0") if record]
    assert len(records) == expected_count
    object_ids = []
    for record in records:
        meta, encoded_path = record.split(b"\t", 1)
        mode, kind, expected_oid = meta.decode().split()
        assert kind == "blob"
        repo_path = encoded_path.decode()
        assert repo_path.startswith(REPO_PREFIX)
        assert mode in {"100644", "100755", "120000"}
        object_ids.append(expected_oid)
    proc = subprocess.run(
        ["git", "cat-file", "--batch-check=%(objectname) %(objecttype)"],
        cwd=REPO_ROOT,
        input=("\n".join(object_ids) + "\n").encode(),
        check=True,
        capture_output=True,
    )
    checked = proc.stdout.decode().splitlines()
    assert len(checked) == expected_count
    assert all(line.endswith(" blob") for line in checked)


def verify_manifest(manifest: dict[str, Any], *, check_materialization: bool = True) -> None:
    assert manifest["schema"] == (
        "closed-universe-observer-tier3-fixed-point-after-legacy-crosswalk-"
        "extension-v2-obstruction-v1"
    )
    assert manifest["disposition"] == "OBSTRUCTED"
    refs = manifest["input_refs"]
    for ref in refs.values():
        assert sha256_path(ROOT / ref["path"]) == ref["sha256"], ref["path"]

    prior = json.loads((ROOT / refs["prior_relock_manifest"]["path"]).read_text())
    assert prior["relock_count"] == refs["prior_relock_manifest"]["relock_count"] == 22
    iteration_13 = prior["suite_iterations"][13]
    assert iteration_13["passed_before_fail"] == 808
    assert iteration_13["failure_kind"] == "NON_PROVENANCE_SEMANTIC_CENSUS_FRONTIER"

    crosswalk_path = ROOT / refs["seven_row_crosswalk"]["path"]
    crosswalk = json.loads(crosswalk_path.read_text())
    completeness = crosswalk["census_completeness"]
    assert completeness["discovered_count"] == completeness["classified_count"] == 7
    assert completeness["complete"] and not completeness["unclassified_ids"]

    frontier = manifest["terminal_frontier"]
    producer_path = ROOT / refs["legacy_replay_producer"]["path"]
    producer_crosswalk = literal_assignment(producer_path, "CROSSWALK")
    assert producer_crosswalk["path"] == refs["seven_row_crosswalk"]["path"]
    assert producer_crosswalk["sha256"] == frontier["expected_historical_base_sha256"]
    legacy = json.loads((ROOT / refs["legacy_replay_certificate"]["path"]).read_text())
    assert (
        legacy["dependency_refs"]["receiver_contract"]["sha256"]
        == frontier["expected_historical_base_sha256"]
    )
    assert sha256_path(crosswalk_path) == frontier["actual_current_crosswalk_sha256"]
    assert frontier["expected_historical_base_sha256"] != frontier["actual_current_crosswalk_sha256"]
    assert frontier["classification"] == "HISTORICAL_BASE_CURRENT_PATH_BINDING_CONFLICT"
    assert "recursive content-address cycle" in frontier["cycle_boundary"]

    run = manifest["tier_3_run"]
    assert run["command"] == "PYTHONPATH=. pytest -q -x closed_universe_observers/tests"
    assert run["uninterrupted"] and run["fail_fast"]
    assert run["passed_before_fail"] == 398 and run["failed"] == 1 and run["skipped"] == 0
    assert run["pytest_elapsed_seconds"] > 0 and run["process_wall_seconds"] >= run["pytest_elapsed_seconds"]
    assert frontier["test"].endswith("::test_census_is_complete_and_fail_closed")

    materialization = manifest["committed_corpus_materialization"]
    assert materialization["expected_blob_count"] == materialization["materialized_blob_count"] == 11184
    assert materialization["hash_mismatch_count"] == 0
    if check_materialization:
        verify_materialization(manifest["input_commit"], materialization["expected_blob_count"])

    flags = manifest["flags"]
    assert flags["TWENTY_TWO_RELOCKS_IMPORTED"] and flags["SEVEN_ROW_CROSSWALK_IMPORTED"]
    assert flags["COMMITTED_CORPUS_COMPLETELY_MATERIALIZED"]
    assert not flags["ZERO_REMAINING_STALE_OR_UNCLASSIFIED_CONSUMERS"]
    assert not flags["OBSERVER_STREAM_TIER3_GREEN"]
    assert not flags["PAPER_9_FREEZE_GATE_ACTIVATED"]


def main() -> None:
    verify_manifest(json.loads(MANIFEST.read_text()))
    print("OBSERVER_TIER3_FIXED_POINT_AFTER_LEGACY_CROSSWALK_EXTENSION_V2 obstruction verification: PASS")


if __name__ == "__main__":
    main()
