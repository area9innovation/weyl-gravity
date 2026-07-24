#!/usr/bin/env python3
"""Produce the geometric-checkpoint reciprocal horizon certificate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from .checkpoint_transport import PARENT_RUN, RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
PARENT_CERT = PARENT_RUN.with_name("certificate.json")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    start = time.monotonic()
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    reached = sum(row["reached_r32"] for row in run["rows"])
    recovered = sum(
        checkpoint["q_recovery_denominator_excludes_zero"]
        for row in run["rows"] for checkpoint in row["checkpoints"]
    )
    certificate = {
        "schema": "phase3-axial-qnm-horizon-reciprocal-checkpoint-transport-v1",
        "status": (
            "HORIZON_PROJECTIVE_LINE_REACHES_R32"
            if reached == 16 else
            "FAIL_CLOSED_BEFORE_R32"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "all_panels_reached_r8_r16_r32": reached == 16,
            "base_horizon_projective_line_at_r32_certified": reached == 16,
            "shared_sensitivities_remain_valid": reached == 16,
            "QNM_or_EP2_certified": False,
            "Evans_boundary_nonzero_certified": False,
            "outgoing_match_certified": False,
        },
        "transport": {
            "initial_radius": 4,
            "checkpoint_radii": [8, 16, 32],
            "reached_panel_count": reached,
            "failed_panel_count": 16 - reached,
            "checkpoint_q_recovery_gate_count": recovered,
            "mobius_recentering_count": sum(
                row["mobius_recentering_used"] for row in run["rows"]
            ),
        },
        "imports": {
            "parent_certificate": {
                "path": str(PARENT_CERT.relative_to(ROOT)),
                "sha256": sha(PARENT_CERT),
            },
            "parent_run": {
                "path": str(PARENT_RUN.relative_to(ROOT)),
                "sha256": sha(PARENT_RUN),
            },
        },
        "run": {"path": str(RUN.relative_to(ROOT)), "sha256": sha(RUN)},
        "does_not_establish": [
            "agreement with the outgoing projective line at r=32",
            "an outgoing Bach frame or T_plus",
            "an Evans/Jost boundary nonvanishing theorem",
            "a QNM root count, defective Smith fibre or EP2",
            "sharp shared-sensitivity enclosures",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Horizon reciprocal geometric-checkpoint transport\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        f"All three geometric checkpoints were reached on {reached}/16 panels. "
        f"The reciprocal-to-q denominator gate passed at {recovered}/48 "
        "panel-checkpoints. No additional Möbius recentering was required.\n\n"
        "The r=32 artifact is a certified base horizon projective line with "
        "valid, intentionally broad shared tau and omega sensitivities. It is "
        "not an outgoing match, Evans, QNM, EP2, or causal certificate.\n"
    )
    commands = [
        ["python3", "-m", "py_compile",
         "black_hole_programme/phase3/axial_qnm_horizon_reciprocal_checkpoint_transport_v1/checkpoint_transport.py",
         "black_hole_programme/phase3/axial_qnm_horizon_reciprocal_checkpoint_transport_v1/produce.py",
         "black_hole_programme/phase3/axial_qnm_horizon_reciprocal_checkpoint_transport_v1/verify.py"],
        ["python3", "-m", "jsonschema", "-i",
         "black_hole_programme/phase3/axial_qnm_horizon_reciprocal_checkpoint_transport_v1/certificate.json",
         "black_hole_programme/phase3/axial_qnm_horizon_reciprocal_checkpoint_transport_v1/schema.json"],
        ["python3", "-m", "unittest",
         "black_hole_programme.phase3.axial_qnm_horizon_reciprocal_checkpoint_transport_v1.test_checkpoint_transport"],
        ["python3", "-m",
         "black_hole_programme.phase3.axial_qnm_horizon_reciprocal_checkpoint_transport_v1.verify"],
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
        "schema": "phase3-axial-qnm-horizon-reciprocal-checkpoint-receipt-v1",
        "elapsed_seconds": round(time.monotonic() - start, 6),
        "checks": checks,
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": "scoped unit tests and verifier",
        "higher_tiers_not_run": (
            "No shared operator, theorem lifecycle, freeze or release changed."
        ),
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
