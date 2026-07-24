#!/usr/bin/env python3
"""Produce the two-sided mismatch preflight certificate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from .mismatch_preflight import HORIZON, OUTGOING, RUN, compute

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
    passed = run["gates"]["boundary_nonvanishing"]["passed_panel_count"]
    certificate = {
        "schema": "phase3-axial-qnm-two-sided-projective-mismatch-preflight-v1",
        "status": (
            "BOUNDARY_NONVANISHING_CERTIFIED"
            if passed == 16 else
            "FAIL_CLOSED_AT_BOUNDARY_NONVANISHING"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "physical_projective_mismatch_assembled": True,
            "boundary_nonvanishing_certified": passed == 16,
            "argument_principle_root_count_certified": False,
            "K0_or_interval_newton_defect_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "gate_summary": run["gates"],
        "imports": {
            "outgoing_affine_run": {
                "path": str(OUTGOING.relative_to(ROOT)),
                "sha256": sha(OUTGOING),
            },
            "horizon_checkpoint_run": {
                "path": str(HORIZON.relative_to(ROOT)),
                "sha256": sha(HORIZON),
            },
        },
        "run": {"path": str(RUN.relative_to(ROOT)), "sha256": sha(RUN)},
        "does_not_establish": [
            "boundary nonvanishing of the physical projective mismatch",
            "an argument-principle QNM root count",
            "a K0, interval-Newton, defective Smith or EP2 gate",
            "a complete outgoing Bach frame or T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Two-sided physical projective mismatch preflight\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The horizon and outgoing reduced logarithmic derivatives use opposite "
        "phases. Their common physical mismatch is therefore "
        "`Delta=q_H-q_out+2*I*omega`; its tau and omega derivatives were "
        "assembled on all 16 panels.\n\n"
        f"Boundary nonvanishing passed on {passed}/16 panels. The serialized "
        "endpoint artifacts retain independent midpoint/radius remainders but "
        "not a common cross-endpoint affine omega generator. Summing those "
        "certified remainders makes every panel contain zero. The computation "
        "therefore stops at the first gate; argument-principle, K0 and "
        "interval-Newton gates were not run.\n"
    )
    commands = [
        ["python3", "-m", "py_compile",
         "black_hole_programme/phase3/axial_qnm_two_sided_projective_mismatch_preflight_v1/mismatch_preflight.py",
         "black_hole_programme/phase3/axial_qnm_two_sided_projective_mismatch_preflight_v1/produce.py",
         "black_hole_programme/phase3/axial_qnm_two_sided_projective_mismatch_preflight_v1/verify.py"],
        ["python3", "-m", "jsonschema", "-i",
         "black_hole_programme/phase3/axial_qnm_two_sided_projective_mismatch_preflight_v1/certificate.json",
         "black_hole_programme/phase3/axial_qnm_two_sided_projective_mismatch_preflight_v1/schema.json"],
        ["python3", "-m", "unittest",
         "black_hole_programme.phase3.axial_qnm_two_sided_projective_mismatch_preflight_v1.test_mismatch_preflight"],
        ["python3", "-m",
         "black_hole_programme.phase3.axial_qnm_two_sided_projective_mismatch_preflight_v1.verify"],
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
        "schema": "phase3-axial-qnm-two-sided-projective-mismatch-receipt-v1",
        "elapsed_seconds": round(time.monotonic() - start, 6),
        "checks": checks,
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": "scoped unit tests and verifier",
        "higher_tiers_not_run": (
            "The first boundary gate failed closed; no downstream claim changed."
        ),
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
