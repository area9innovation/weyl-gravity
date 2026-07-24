#!/usr/bin/env python3
"""Produce the common-affine export shortfall certificate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from .audit import HORIZON, OUTGOING, RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    start = time.monotonic()
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    certificate = {
        "schema": "phase3-axial-qnm-common-affine-export-contract-v1",
        "status": "FAIL_CLOSED_COMMON_AFFINE_EXPORT_CONTRACT_MISSING",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "common_affine_endpoint_export_available": False,
            "boundary_nonvanishing_certified": False,
            "argument_principle_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "required_export_contract": run["required_common_export_contract"],
        "bounded_attempt": run["bounded_joint_rerun_attempt"],
        "gate_summary": run["gates"],
        "imports": {
            "outgoing_run": {
                "path": str(OUTGOING.relative_to(ROOT)),
                "sha256": sha(OUTGOING),
            },
            "horizon_run": {
                "path": str(HORIZON.relative_to(ROOT)),
                "sha256": sha(HORIZON),
            },
        },
        "run": {"path": str(RUN.relative_to(ROOT)), "sha256": sha(RUN)},
        "does_not_establish": [
            "a common centered-omega endpoint transport",
            "boundary nonvanishing or an argument-principle root count",
            "a K0, interval-Newton, QNM, defective Smith or EP2 gate",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Common affine endpoint export shortfall\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The serialized horizon and outgoing artifacts do not export a common "
        "omega-generator identity, centered omega-polynomial coefficients, or "
        "residual radii after subtracting those polynomials. Consequently the "
        "cross-endpoint cancellation required by "
        "`Delta=q_H-q_out+2*I*omega` cannot be reconstructed safely.\n\n"
        "A bounded singleton-centered horizon attempt passed its first Taylor "
        "reference step but failed the existing remainder self-map at the "
        "first seed step. No long rerun was started. Boundary nonvanishing and "
        "all downstream gates remain not run.\n"
    )
    commands = [
        ["python3", "-m", "py_compile",
         "black_hole_programme/phase3/axial_qnm_common_affine_export_contract_v1/audit.py",
         "black_hole_programme/phase3/axial_qnm_common_affine_export_contract_v1/produce.py",
         "black_hole_programme/phase3/axial_qnm_common_affine_export_contract_v1/verify.py"],
        ["python3", "-m", "jsonschema", "-i",
         "black_hole_programme/phase3/axial_qnm_common_affine_export_contract_v1/certificate.json",
         "black_hole_programme/phase3/axial_qnm_common_affine_export_contract_v1/schema.json"],
        ["python3", "-m", "unittest",
         "black_hole_programme.phase3.axial_qnm_common_affine_export_contract_v1.test_audit"],
        ["python3", "-m",
         "black_hole_programme.phase3.axial_qnm_common_affine_export_contract_v1.verify"],
    ]
    checks = []
    for command in commands:
        before = time.monotonic()
        result = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True, check=False
        )
        checks.append({
            "command": " ".join(command),
            "elapsed_seconds": round(time.monotonic() - before, 6),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        })
    RECEIPT.write_text(json.dumps({
        "schema": "phase3-axial-qnm-common-affine-export-contract-receipt-v1",
        "elapsed_seconds": round(time.monotonic() - start, 6),
        "checks": checks,
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": "scoped unit tests and verifier",
        "higher_tiers_not_run": "The prerequisite export contract is absent.",
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
