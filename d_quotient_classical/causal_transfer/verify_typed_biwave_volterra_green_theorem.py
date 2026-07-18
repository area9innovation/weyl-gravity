#!/usr/bin/env python3
"""Independent replay for the typed lower-order biwave Green theorem."""

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
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1.json"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/typed-biwave-volterra-green-theorem-v1.schema.json"
MANIFEST_PATH = ROOT / "d_quotient_classical/manifests/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1_SOURCE_MANIFEST.json"
RECEIPT_PATH = ROOT / "d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1_VERIFICATION_RECEIPT.json"

EXPECTED_ROLES = {
    "certificate",
    "schema",
    "producer",
    "verifier",
    "tests",
    "report",
    "analytic_proof:finite_slab_estimate",
    "analytic_proof:typed_inverse_identities",
    "analytic_proof:causal_globalization",
    "analytic_proof:adjoint_reversal",
}


def _load(path: Path) -> dict:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise AssertionError(f"JSON root is not an object: {path}")
    return payload


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _block(rows: list[list[sp.Matrix]]) -> sp.Matrix:
    return sp.BlockMatrix(rows).as_explicit()


def _replay_operator_algebra() -> dict[str, int]:
    """Use a fixture distinct from the producer's coefficients."""
    p1 = sp.Matrix([[1, 2], [1, 3]])
    p2 = sp.Matrix([[3, 1], [2, 1]])
    v = sp.Matrix([[2, -1], [1, 1]])
    eye = sp.eye(2)
    zero = sp.zeros(2)
    c0 = _block([[p1, zero], [v, p2]])
    n = _block([[zero, -eye], [zero, zero]])
    c = c0 + n
    g1 = p1.inv()
    g2 = p2.inv()
    g0 = _block([[g1, zero], [-g2 * v * g1, g2]])
    r_sol = (sp.eye(4) + g0 * n).inv()
    r_src = (sp.eye(4) + n * g0).inv()
    gc = r_sol * g0
    a = p2 * p1 + v
    p = sp.Matrix.hstack(eye, zero)
    i = sp.Matrix.vstack(zero, eye)
    ga = p * gc * i
    j = sp.Matrix.vstack(eye, p1)
    defects = {
        "C0G0": c0 * g0 - sp.eye(4),
        "G0C0": g0 * c0 - sp.eye(4),
        "push_through": gc - g0 * r_src,
        "CGC": c * gc - sp.eye(4),
        "GCC": gc * c - sp.eye(4),
        "graph": c * j - i * a,
        "AGA": a * ga - eye,
        "GAA": ga * a - eye,
    }
    nonzero = {
        name: matrix.tolist()
        for name, matrix in defects.items()
        if any(sp.simplify(entry) != 0 for entry in matrix)
    }
    if nonzero:
        raise AssertionError(f"independent operator replay failed: {nonzero}")
    if p1 * p2 == p2 * p1 or p1 * v == v * p1 or p2 * v == v * p2:
        raise AssertionError("independent fixture accidentally commutes")
    return {name: 0 for name in defects}


def verify_core() -> dict:
    certificate = _load(CERTIFICATE_PATH)
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)

    if certificate["dependency_tags"] != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        raise AssertionError("dependency tags drifted")
    if not all(certificate["exact_checks"].values()):
        raise AssertionError("certificate contains a failed exact check")
    if any(
        certificate["operator_hypotheses"][key]
        for key in ("commutativity_required", "stationarity_required", "self_adjointness_required")
    ):
        raise AssertionError("the abstract theorem acquired an unnecessary hypothesis")
    if certificate["typed_resolvents"]["solution"] == certificate["typed_resolvents"]["source"]:
        raise AssertionError("typed resolvents collapsed")
    if "A^sharp" not in certificate["theorem"]["adjoint_reversal"]:
        raise AssertionError("formal-adjoint target was lost")
    for flag in (
        "TRANSVERSE_BACH_FLAT_METRIC_SDR",
        "TRANSVERSE_BACH_FLAT_CAUSAL_TRANSFER",
        "HADAMARD_STATE",
        "NONLINEAR_STABILITY",
        "QUANTUM_THEORY",
    ):
        if certificate["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")

    proof_payloads = {}
    for name, record in certificate["analytic_proof_artifacts"].items():
        path = ROOT / record["path"]
        if not path.is_file() or _sha(path) != record["sha256"]:
            raise AssertionError(f"proof artifact hash mismatch: {name}")
        proof_payloads[name] = _load(path)
    finite = proof_payloads["finite_slab_estimate"]
    if (
        "n!" not in finite["solution_bound"]
        or "n!" not in finite["source_bound"]
        or "stationarity is not assumed" not in finite["hypotheses"][-1]
        or finite["mappings"]["K_sol"] == finite["mappings"]["K_src"]
    ):
        raise AssertionError("finite-slab proof lost its typed estimate")
    inverse = proof_payloads["typed_inverse_identities"]
    if (
        "X_s->X_s" not in inverse["solution_resolvent"]
        or "Y_s->Y_s" not in inverse["source_resolvent"]
        or len(inverse["companion_inverses"]) != 2
        or len(inverse["metric_inverses"]) != 2
    ):
        raise AssertionError("inverse proof is not two-sided and typed")
    adjoint = proof_payloads["adjoint_reversal"]
    if adjoint["self_adjointness_assumed"] is not False or "factor order reverses" not in adjoint["adjoint_operator"]:
        raise AssertionError("adjoint proof drifted")

    for record in certificate["consumers"].values():
        dependency = record["dependency"]
        path = ROOT / dependency["path"]
        payload = _load(path)
        if _sha(path) != dependency["sha256"] or payload["result_id"] != dependency["result_id"]:
            raise AssertionError("consumer dependency hash/result mismatch")

    manifest = _load(MANIFEST_PATH)
    if manifest["target_result_id"] != certificate["result_id"]:
        raise AssertionError("manifest target drifted")
    if {record["role"] for record in manifest["files"]} != EXPECTED_ROLES:
        raise AssertionError("manifest role coverage drifted")
    for record in manifest["files"]:
        path = ROOT / record["path"]
        if not path.is_file() or _sha(path) != record["sha256"]:
            raise AssertionError(f"manifest hash mismatch: {record['role']}")

    replay = _replay_operator_algebra()
    return {
        "certificate_sha256": _sha(CERTIFICATE_PATH),
        "schema_sha256": _sha(SCHEMA_PATH),
        "manifest_sha256": _sha(MANIFEST_PATH),
        "proof_hashes": {
            name: record["sha256"]
            for name, record in sorted(certificate["analytic_proof_artifacts"].items())
        },
        "independent_identity_defects": replay,
    }


def _commands() -> list[list[str]]:
    return [
        ["python3", "-m", "d_quotient_classical.causal_transfer.typed_biwave_volterra_green_theorem", "--check", "--guards"],
        ["python3", "d_quotient_classical/causal_transfer/verify_typed_biwave_volterra_green_theorem.py", "--verify-only"],
        ["python3", "-m", "unittest", "d_quotient_classical.causal_transfer.tests.test_typed_biwave_volterra_green_theorem"],
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
        "return_code": 0,
        "status": "PASS",
    }


def write_receipt() -> dict:
    core = verify_core()
    receipt = {
        "schema": "typed-biwave-volterra-green-theorem-verification-receipt-v1",
        "result_id": "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1_VERIFICATION_RECEIPT",
        "target_result_id": "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "covered_roles": sorted(EXPECTED_ROLES),
        "certificate_sha256": core["certificate_sha256"],
        "schema_sha256": core["schema_sha256"],
        "source_manifest": {
            "path": str(MANIFEST_PATH.relative_to(ROOT)),
            "sha256": core["manifest_sha256"],
        },
        "proof_hashes": core["proof_hashes"],
        "independent_identity_defects": core["independent_identity_defects"],
        "commands": [_run(command) for command in _commands()],
        "overall_status": "PASS",
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def verify_receipt() -> dict:
    core = verify_core()
    receipt = _load(RECEIPT_PATH)
    if (
        receipt["target_result_id"] != "TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1"
        or receipt["overall_status"] != "PASS"
        or receipt["covered_roles"] != sorted(EXPECTED_ROLES)
        or receipt["certificate_sha256"] != core["certificate_sha256"]
        or receipt["schema_sha256"] != core["schema_sha256"]
        or receipt["source_manifest"]["sha256"] != core["manifest_sha256"]
        or receipt["proof_hashes"] != core["proof_hashes"]
        or receipt["independent_identity_defects"] != core["independent_identity_defects"]
    ):
        raise AssertionError("verification receipt content drifted")
    expected = [" ".join(command) for command in _commands()]
    if [row["command"] for row in receipt["commands"]] != expected:
        raise AssertionError("verification command coverage drifted")
    if any(
        row["status"] != "PASS"
        or row["return_code"] != 0
        or not isinstance(row["elapsed_seconds"], (int, float))
        or row["elapsed_seconds"] < 0
        for row in receipt["commands"]
    ):
        raise AssertionError("receipt command status/timing drifted")
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
    print("TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
