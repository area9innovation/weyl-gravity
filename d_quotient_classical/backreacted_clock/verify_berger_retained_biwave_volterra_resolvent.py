#!/usr/bin/env python3
"""Independent schema, hash, proof-artifact and receipt verifier for Volterra v2."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from jsonschema import Draft202012Validator

WORKTREE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKTREE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKTREE_ROOT))

from d_quotient_classical.backreacted_clock import berger_retained_biwave_volterra_resolvent as producer


ROOT = producer.ROOT
EXPECTED_ROLES = {
    "certificate", "schema", "producer", "verifier", "tests", "report",
    "analytic_proof:finite_slab_estimate", "analytic_proof:causal_support_passage",
    "analytic_proof:globalization_uniqueness", "analytic_proof:inverse_identities",
    "analytic_proof:adjoint_reversal",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise AssertionError(f"JSON root is not an object: {path}")
    return value


def verify_core() -> dict:
    certificate = _load(producer.CERTIFICATE_PATH)
    schema = _load(producer.SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    producer.verify(certificate)

    artifacts = certificate["analytic_proof_artifacts"]
    proof_payloads = {}
    for name, record in artifacts.items():
        path = ROOT / record["path"]
        if not path.is_file() or _sha256(path) != record["sha256"]:
            raise AssertionError(f"analytic proof hash mismatch: {name}")
        proof_payloads[name] = _load(path)
    finite = proof_payloads["finite_slab_estimate"]
    if (
        finite["derivative_mappings"][-2:] != [
            "K_sol,advanced/retarded=G0,advanced/retarded N:X_s(I)->X_s(I)",
            "K_src,advanced/retarded=N G0,advanced/retarded:Y_s(I)->Y_s(I)",
        ]
        or "X_s(I)->X_s(I)" not in finite["solution_series_bound"]
        or "Y_s(I)->Y_s(I)" not in finite["source_series_bound"]
    ):
        raise AssertionError("typed finite-slab estimate drifted")
    adjoint = proof_payloads["adjoint_reversal"]
    if (
        adjoint["typed_identity"] != "(G_A,advanced)^sharp=G_(A^sharp),retarded and (G_A,retarded)^sharp=G_(A^sharp),advanced"
        or adjoint["self_adjoint_simplification_used"] is not False
    ):
        raise AssertionError("typed adjoint proof drifted")

    manifest = _load(producer.MANIFEST_PATH)
    if manifest.get("target_result_id") != certificate["result_id"]:
        raise AssertionError("source manifest target drifted")
    records = manifest.get("files", [])
    if {record.get("role") for record in records} != EXPECTED_ROLES:
        raise AssertionError("source manifest role coverage drifted")
    for record in records:
        path = ROOT / record["path"]
        if not path.is_file() or _sha256(path) != record["sha256"]:
            raise AssertionError(f"source manifest hash mismatch: {record['role']}")
    if manifest.get("receipt_path") != str(producer.RECEIPT_PATH.relative_to(ROOT)):
        raise AssertionError("receipt path drifted")
    return {
        "certificate_sha256": _sha256(producer.CERTIFICATE_PATH),
        "schema_sha256": _sha256(producer.SCHEMA_PATH),
        "manifest_sha256": _sha256(producer.MANIFEST_PATH),
        "analytic_proof_hashes": {name: record["sha256"] for name, record in sorted(artifacts.items())},
    }


def _commands() -> list[list[str]]:
    return [
        ["python3", "-m", "d_quotient_classical.backreacted_clock.berger_retained_biwave_volterra_resolvent", "--check", "--guards"],
        ["python3", str(producer.VERIFIER_PATH.relative_to(ROOT)), "--verify-only"],
        ["python3", "-m", "unittest", "d_quotient_classical.backreacted_clock.tests.test_berger_retained_biwave_volterra_resolvent"],
    ]


def _run(command: list[str]) -> dict:
    started = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    elapsed = round(time.perf_counter() - started, 6)
    if result.returncode:
        raise AssertionError(
            f"verification command failed: {' '.join(command)}\n{result.stdout}\n{result.stderr}"
        )
    return {
        "command": " ".join(command),
        "elapsed_seconds": elapsed,
        "return_code": result.returncode,
        "status": "PASS",
    }


def write_receipt() -> dict:
    core = verify_core()
    command_results = [_run(command) for command in _commands()]
    receipt = {
        "schema": "pure-weyl-berger-volterra-verification-receipt-v1",
        "result_id": "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2_VERIFICATION_RECEIPT",
        "target_result_id": "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "covered_roles": sorted(EXPECTED_ROLES),
        "source_manifest": {
            "path": str(producer.MANIFEST_PATH.relative_to(ROOT)),
            "sha256": core["manifest_sha256"],
        },
        "certificate_sha256": core["certificate_sha256"],
        "schema_sha256": core["schema_sha256"],
        "analytic_proof_hashes": core["analytic_proof_hashes"],
        "commands": command_results,
        "overall_status": "PASS",
    }
    producer.RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def verify_receipt() -> dict:
    core = verify_core()
    receipt = _load(producer.RECEIPT_PATH)
    if (
        receipt.get("target_result_id") != "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2"
        or receipt.get("overall_status") != "PASS"
        or receipt.get("covered_roles") != sorted(EXPECTED_ROLES)
        or receipt.get("certificate_sha256") != core["certificate_sha256"]
        or receipt.get("schema_sha256") != core["schema_sha256"]
        or receipt.get("analytic_proof_hashes") != core["analytic_proof_hashes"]
        or receipt.get("source_manifest", {}).get("sha256") != core["manifest_sha256"]
    ):
        raise AssertionError("verification receipt content drifted")
    expected = [" ".join(command) for command in _commands()]
    rows = receipt.get("commands", [])
    if [row.get("command") for row in rows] != expected:
        raise AssertionError("verification receipt command coverage drifted")
    if any(
        row.get("status") != "PASS"
        or row.get("return_code") != 0
        or not isinstance(row.get("elapsed_seconds"), (int, float))
        or row["elapsed_seconds"] < 0
        for row in rows
    ):
        raise AssertionError("verification receipt timing/status drifted")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write_receipt:
        write_receipt()
    elif args.check:
        verify_receipt()
    else:
        verify_core()
    print("BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
