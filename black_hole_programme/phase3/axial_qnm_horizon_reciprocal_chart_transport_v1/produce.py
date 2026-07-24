#!/usr/bin/env python3
"""Produce the reciprocal-chart certificate and receipt."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from .reciprocal_transport import ECS, RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
PARENT = ROOT / "black_hole_programme/phase3/axial_qnm_horizon_projective_preflight_v1/certificate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    start = time.monotonic()
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    reached = sum(row["reached_r4"] for row in run["rows"])
    denominators = sum(
        row["switch"]["denominator_excludes_zero"] for row in run["rows"]
    )
    certificate = {
        "schema": "phase3-axial-qnm-horizon-reciprocal-chart-transport-v1",
        "status": (
            "RECIPROCAL_CHART_REACHES_R4"
            if reached == 16 else
            "FAIL_CLOSED_RECIPROCAL_CHART_PARTIAL"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "full_panel_reciprocal_denominator_certified": denominators == 16,
            "all_panels_reached_r4": reached == 16,
            "QNM_or_EP2_certified": False,
            "Evans_boundary_nonzero_certified": False,
        },
        "chart_switch": {
            "from": "q=P_x/P",
            "to": "p=1/q",
            "shared_derivative_rule": (
                "p_tau=-q_tau/q^2; p_omega=-q_omega/q^2"
            ),
            "certified_panel_count": denominators,
        },
        "transport": {
            "target_radius": 4,
            "reached_panel_count": reached,
            "failed_panel_count": 16 - reached,
        },
        "imports": {
            "predecessor": {"path": str(PARENT.relative_to(ROOT)), "sha256": sha(PARENT)},
            "ecs_disk": {"path": str(ECS.relative_to(ROOT)), "sha256": sha(ECS)},
        },
        "run": {"path": str(RUN.relative_to(ROOT)), "sha256": sha(RUN)},
        "does_not_establish": [
            "a horizon-to-infinity common checkpoint",
            "an outgoing Bach frame or T_plus",
            "an Evans/Jost boundary nonvanishing theorem",
            "a QNM root count, defective Smith fibre or EP2",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Horizon reciprocal-chart transport\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        f"The predecessor q-chart obstruction was tested on 16 panels. "
        f"The full-panel reciprocal denominator excludes zero on {denominators}/16 "
        f"panels, and the reciprocal rail reached the bounded common checkpoint "
        f"`r=4` on {reached}/16 panels.\n\n"
        "The chart change uses `p=1/q` with the shared derivative laws "
        "`p_tau=-q_tau/q^2` and `p_omega=-q_omega/q^2`. The artifact is "
        "fail-closed and makes no QNM, Evans, EP2, outgoing-frame, or causal claim.\n"
    )
    commands = [
        ["python3", "-m", "py_compile",
         "black_hole_programme/phase3/axial_qnm_horizon_reciprocal_chart_transport_v1/reciprocal_transport.py",
         "black_hole_programme/phase3/axial_qnm_horizon_reciprocal_chart_transport_v1/produce.py",
         "black_hole_programme/phase3/axial_qnm_horizon_reciprocal_chart_transport_v1/verify.py"],
        ["python3", "-m", "jsonschema",
         "-i", "black_hole_programme/phase3/axial_qnm_horizon_reciprocal_chart_transport_v1/certificate.json",
         "black_hole_programme/phase3/axial_qnm_horizon_reciprocal_chart_transport_v1/schema.json"],
        ["python3", "-m", "unittest",
         "black_hole_programme.phase3.axial_qnm_horizon_reciprocal_chart_transport_v1.test_reciprocal_transport"],
        ["python3", "-m",
         "black_hole_programme.phase3.axial_qnm_horizon_reciprocal_chart_transport_v1.verify"],
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
        "schema": "phase3-axial-qnm-horizon-reciprocal-chart-receipt-v1",
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
