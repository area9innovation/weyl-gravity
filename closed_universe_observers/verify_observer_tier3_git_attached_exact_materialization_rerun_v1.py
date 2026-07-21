#!/usr/bin/env python3
"""Independent audit of the Git-attached Observer Tier-3 first frontier."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
RECEIPT = ROOT / "closed_universe_observers/receipts/OBSERVER_TIER3_GIT_ATTACHED_EXACT_MATERIALIZATION_RERUN_V1_OBSTRUCTION.json"
COMMIT = "d3b46e000875e06c97f4afd701c662e0ccb1bc1b"
PREFIX = "physics/symplectic-reconstruction/"
LEDGER = "closed_universe_observers/ledgers/comparison_ledger.json"
ARTIFACT = "closed_universe_observers/certificates/BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW.json"
TEST = "closed_universe_observers/tests/test_comparison_ledger.py"
LEDGER_VERIFIER = "closed_universe_observers/verify_comparison_ledger.py"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def committed_bytes(relative: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{COMMIT}:{PREFIX}{relative}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout


def committed_sha256(relative: str) -> str:
    return sha256_bytes(committed_bytes(relative))


def committed_tree_census() -> tuple[int, int, int]:
    output = subprocess.run(
        ["git", "ls-tree", "-r", "-z", "--full-tree", COMMIT, "--", PREFIX],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    regular = 0
    symlinks = 0
    for item in output.split(b"\0"):
        if not item:
            continue
        header, _path = item.split(b"\t", 1)
        mode, object_type, _oid = header.split()
        if object_type != b"blob":
            continue
        if mode == b"120000":
            symlinks += 1
        else:
            regular += 1
    return regular, symlinks, regular + symlinks


def verify_value(value: dict) -> dict:
    assert value["schema"] == "observer-tier3-git-attached-exact-materialization-rerun-obstruction-v1"
    assert value["result_id"] == "OBSERVER_TIER3_GIT_ATTACHED_EXACT_MATERIALIZATION_RERUN_V1_OBSTRUCTION"
    assert value["science_forge_work_item"].endswith("observer-tier3-git-attached-exact-materialization-rerun-v1")
    for ref in value["input_refs"].values():
        assert sha256(ROOT / ref["path"]) == ref["sha256"]

    manifest = json.loads(
        (ROOT / value["input_refs"]["materialization_manifest"]["path"]).read_text()
    )
    materialization = value["materialization"]
    assert manifest["selected_commit"] == materialization["selected_commit"] == COMMIT
    assert materialization["kind"] == "GIT_ATTACHED_DETACHED_WORKTREE"
    assert materialization["repo_prefix_from_scope"] == PREFIX
    assert materialization["repo_prefix_from_observer_package"] == PREFIX + "closed_universe_observers/"
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", f"{COMMIT}^{{commit}}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert resolved == COMMIT
    repo_tree = subprocess.run(
        ["git", "rev-parse", f"{COMMIT}^{{tree}}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    scope_tree = subprocess.run(
        ["git", "rev-parse", f"{COMMIT}:{PREFIX.rstrip('/')}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert materialization["repository_tree_oid"] == repo_tree
    assert materialization["scope_tree_oid"] == scope_tree
    regular, symlinks, total = committed_tree_census()
    assert (regular, symlinks, total) == (11189, 2, 11191)
    assert materialization["regular_file_count"] == regular
    assert materialization["symlink_count"] == symlinks
    assert materialization["total_blob_count"] == total
    assert materialization["missing_count"] == 0
    assert materialization["blob_hash_mismatch_count"] == 0
    assert materialization["mode_mismatch_count"] == 0
    assert materialization["status_porcelain_byte_count_before"] == 0
    assert materialization["status_porcelain_byte_count_after"] == 0
    assert materialization["status"] == "PASS_EXACT_GIT_ATTACHED_WORKTREE"
    assert value["resource_preflight"]["status"] == "PASS"

    run = value["authoritative_run"]
    assert run["command"] == "PYTHONPATH=. pytest -q -x closed_universe_observers/tests"
    assert run["run_count"] == 1 and run["retry_count"] == 0
    assert run["patches_inside_run"] == 0
    assert run["prior_partial_passes_credited"] is False
    assert run["passed_before_first_failure"] == 826
    assert run["failed"] == 1 and run["skipped_before_failure"] == 0
    assert run["pytest_elapsed_seconds"] == 1175.10
    assert run["wall_elapsed_seconds"] == 1183.15
    assert run["exit_code"] == 1 and run["fail_fast"] is True
    assert run["status"] == "STOPPED_AT_FIRST_FAILURE"
    assert run["stdout_log"] == {
        "retained_path": "/tmp/observer-tier3-git-attached-v1-pytest.log",
        "sha256": "decf8da65dfe054afd702614573fdc0d5c95ce461f7efc0e09823ea7ed64430c",
        "byte_count": 4382,
        "line_count": 69,
        "committed": False,
    }

    failure = value["first_failure"]
    assert failure["nodeid"] == f"{TEST}::test_comparison_ledger_is_fail_closed"
    assert failure["exception_location"] == f"{LEDGER_VERIFIER}:59"
    assert failure["classification"] == "STALE_COMPARISON_LEDGER_BRIDGE_ARTIFACT_PIN_WITH_CLAIM_BOUNDARY_DRIFT"
    assert committed_sha256(TEST) == failure["test_sha256_at_selected_commit"]
    assert committed_sha256(LEDGER_VERIFIER) == failure["verifier_sha256_at_selected_commit"]
    assert committed_sha256(LEDGER) == failure["ledger_sha256_at_selected_commit"]
    assert committed_sha256(ARTIFACT) == failure["actual_artifact_sha256_at_selected_commit"]

    ledger = json.loads(committed_bytes(LEDGER))
    artifact = json.loads(committed_bytes(ARTIFACT))
    row = next(
        row for row in ledger["bridge_artifacts"]
        if row["result_id"] == "BERGER_108_ROW_EMITTER_PHYSICAL_Q2_PBW"
    )
    assert ledger["provenance"]["internal_source_snapshot_commit"] == failure["ledger_internal_snapshot_commit"]
    assert row["path"] == failure["artifact_path"] == ARTIFACT
    assert row["result_id"] == failure["artifact_result_id"] == artifact["result_id"]
    assert row["sha256"] == failure["ledger_pinned_artifact_sha256"]
    assert sha256_bytes(row["claim_boundary"].encode()) == failure["ledger_pinned_claim_boundary_sha256"]
    assert len(row["claim_boundary"].encode()) == failure["ledger_pinned_claim_boundary_byte_count"]
    assert sha256_bytes(artifact["claim_boundary"].encode()) == failure["actual_claim_boundary_sha256_at_selected_commit"]
    assert len(artifact["claim_boundary"].encode()) == failure["actual_claim_boundary_byte_count"]
    assert row["sha256"] != committed_sha256(ARTIFACT)
    assert row["claim_boundary"] != artifact["claim_boundary"]
    assert failure["artifact_hash_drift"] is True
    assert failure["claim_boundary_drift"] is True
    assert failure["claim_boundary_change_is_material"] is True
    assert "separately certified" in artifact["claim_boundary"]
    assert "relational temporal emitter-Diff orbit" in artifact["claim_boundary"]
    assert "remains to be scalarized" in row["claim_boundary"]
    assert failure["scientific_contradiction"] is False
    assert failure["materialization_defect"] is False
    assert failure["test_harness_defect"] is False
    assert failure["prior_archive_git_defect_recurred"] is False

    disposition = value["disposition"]
    assert disposition["status"] == "OBSTRUCTED"
    assert disposition["paper09_freeze_decision"] == "DRAFT_ALLOWED"
    assert disposition["smallest_successor"] == "SEMANTIC_COMPARISON_LEDGER_BRIDGE_ARTIFACT_RELOCK_AND_FRESH_TIER3_RERUN"
    assert "blind hash-only repin is forbidden" in " ".join(disposition["successor_requirements"])
    flags = value["flags"]
    assert flags["GIT_ATTACHED"] and flags["EXACT_BLOBS"] and flags["CLEAN_WORKTREE"]
    assert flags["RESOURCE_PREFLIGHT_PASS"] and flags["AUTHORITATIVE_RUN_COUNT_EXACTLY_ONE"]
    assert flags["STALE_COMPARISON_LEDGER_PIN"] and flags["CLAIM_BOUNDARY_DRIFT"]
    assert not flags["AUTHORITATIVE_RUN_GREEN"]
    assert not flags["SCIENTIFIC_CONTRADICTION"]
    assert not flags["MATERIALIZATION_DEFECT"]
    assert not flags["PRIOR_ARCHIVE_GIT_DEFECT_RECURRED"]
    assert not flags["PAPER9_EVIDENCE_GATE_ACTIVATED"]
    assert not flags["PAPER9_THEOREM_FROZEN"]
    return value


def verify() -> dict:
    return verify_value(json.loads(RECEIPT.read_text()))


if __name__ == "__main__":
    verify()
    print("OBSERVER_TIER3_GIT_ATTACHED_EXACT_MATERIALIZATION_RERUN_V1 obstruction verification: PASS")
