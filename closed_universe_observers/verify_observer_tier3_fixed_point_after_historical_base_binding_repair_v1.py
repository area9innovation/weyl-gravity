#!/usr/bin/env python3
"""Independent audit of the post-repair Observer Tier-3 first frontier."""

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
OBSTRUCTION = ROOT / "closed_universe_observers/receipts/OBSERVER_TIER3_FIXED_POINT_AFTER_HISTORICAL_BASE_BINDING_REPAIR_V1_OBSTRUCTION.json"
COMMIT = "d3b46e000875e06c97f4afd701c662e0ccb1bc1b"
PREFIX = "physics/symplectic-reconstruction/"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def committed_sha256(relative: str) -> str:
    payload = subprocess.run(
        ["git", "show", f"{COMMIT}:{PREFIX}{relative}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    return hashlib.sha256(payload).hexdigest()


def committed_blob_count() -> int:
    output = subprocess.run(
        ["git", "ls-tree", "-r", "-z", COMMIT, PREFIX.rstrip("/")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    return sum(
        1
        for item in output.split(b"\0")
        if item and item.split(b"\t", 1)[0].split()[1] == b"blob"
    )


def verify_value(value: dict) -> dict:
    assert value["result_id"] == "OBSERVER_TIER3_FIXED_POINT_AFTER_HISTORICAL_BASE_BINDING_REPAIR_V1_OBSTRUCTION"
    for ref in value["input_refs"].values():
        assert sha256(ROOT / ref["path"]) == ref["sha256"]

    materialization = value["materialization"]
    assert materialization["repair_commit"] == COMMIT
    assert subprocess.run(
        ["git", "rev-parse", "--verify", f"{COMMIT}^{{commit}}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == COMMIT
    assert materialization["regular_file_and_symlink_blob_count"] == committed_blob_count() == 11191
    assert materialization["missing_count"] == materialization["hash_mismatch_count"] == 0
    assert materialization["status"] == "PASS_EXACT_GIT_BLOBS"

    failure = value["first_failure"]
    assert failure["classification"] == "TEST_HARNESS_MATERIALIZATION_INTERFACE_DEFECT"
    assert failure["test"].endswith("test_smeared_retarded_transfer_gate_remains_fail_closed")
    assert committed_sha256(failure["producer"]) == failure["producer_sha256"]
    assert committed_sha256(failure["test"].split("::", 1)[0]) == failure["test_sha256"]
    assert committed_sha256(failure["fixture"]) == failure["fixture_sha256"]
    assert failure["dependency_snapshot_commit"] == "fc7a680d32d23d516a1c29c54ae1e0734d532a75"
    assert not failure["scientific_contradiction"]
    assert not failure["historical_base_defect_recurred"]
    assert not failure["stale_pin_detected"]

    run = value["authoritative_run"]
    assert run["run_count"] == 1
    assert run["passed_before_first_failure"] == 300
    assert run["failed"] == 1 and run["skipped_before_failure"] == 0
    assert run["status"] == "STOPPED_AT_FIRST_FAILURE"
    assert all(mutation["detected"] for mutation in value["mutation_results"])
    assert not value["flags"]["AUTHORITATIVE_RUN_GREEN"]
    assert not value["flags"]["PAPER9_EVIDENCE_GATE_ACTIVATED"]
    assert not value["flags"]["PHYSICS_DISPOSITION_CHANGED"]
    return value


def verify() -> dict:
    return verify_value(json.loads(OBSTRUCTION.read_text()))


if __name__ == "__main__":
    verify()
    print("OBSERVER_TIER3_FIXED_POINT_AFTER_HISTORICAL_BASE_BINDING_REPAIR_V1 obstruction verification: PASS")
