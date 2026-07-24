#!/usr/bin/env python3
"""Produce the panels 32--47 common-affine certificate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from flint import arb

from .chunk import CHECKPOINT, PANEL_START, PANEL_STOP, RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT, RECEIPT, REPORT = (
    HERE / "certificate.json",
    HERE / "receipt.json",
    HERE / "report.md",
)
PREDECESSOR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_chunk_v2/certificate.json"
)
BASE_SOURCE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_boundary_v1/common_affine.py"
)
ARTIFACTS = (
    "README.md", "__init__.py", "chunk.py", "produce.py", "schema.json",
    "test_chunk.py", "verify.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def minimum(run: dict) -> tuple[int | None, str | None]:
    passing = [
        row for row in run["rows"]
        if row["boundary_nonvanishing"]["status"] == "PASS"
    ]
    if not passing:
        return None, None
    row = min(
        passing,
        key=lambda item: arb(
            item["physical_mismatch"]["modulus_lower"]
        ).lower(),
    )
    return row["panel"], row["physical_mismatch"]["modulus_lower"]


def main() -> None:
    started = time.monotonic()
    run = compute(write_checkpoint=True)
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    panel, lower = minimum(run)
    complete = run["all_requested_panels_nonzero"]
    imports = {"predecessor_chunk": PREDECESSOR, "transport_source": BASE_SOURCE}
    certificate = {
        "schema": "phase3-axial-qnm-common-affine-evans-chunk-v3",
        "status": (
            "PANELS_32_THROUGH_47_BOUNDARY_NONVANISHING_CERTIFIED"
            if complete else "CHUNK_32_THROUGH_47_FAIL_CLOSED"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "requested_chunk_nonzero_certified": complete,
            "full_contour_nonzero_certified": False,
            "argument_principle_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "method": {
            "requested_panels": [PANEL_START, PANEL_STOP - 1],
            "worker_count": run["worker_count"],
            "batch_size": run["batch_size"],
            "checkpoint_after_each_batch": True,
            "ordered_stop_rule": run["stop_rule"],
            "shared_generator": (
                "one zeta=omega-omega_center generator per "
                "horizon/outgoing/mismatch triple"
            ),
            "endpoint_fields": ["q", "q_tau", "q_omega"],
        },
        "result": {
            "completed_panel_count": run["completed_panel_count"],
            "passed_panel_count": sum(
                row["boundary_nonvanishing"]["status"] == "PASS"
                for row in run["rows"]
            ),
            "terminal": run["terminal"],
            "minimum_modulus_lower_panel": panel,
            "minimum_modulus_lower": lower,
            "argument_principle_status": "NOT_RUN",
        },
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)), "sha256": sha(path)
            }
            for name, path in imports.items()
        },
        "run": {
            "path": str(RUN.relative_to(ROOT)), "sha256": sha(RUN)
        },
        "does_not_establish": [
            "boundary nonvanishing outside the materialized panels",
            "boundary nonvanishing on the complete closed contour",
            "an argument-principle QNM count",
            "a nonzero Delta_tau or Delta_omega selector",
            "a QNM location, Smith selector, defective fibre or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Common-affine projective Evans chunk v3\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        f"Requested panels 32--47; complete=`{complete}`, terminal="
        f"`{run['terminal']}`.  The smallest passing mismatch lower bound "
        f"is `{lower}` on panel `{panel}`.  No closed-contour or QNM claim "
        "is made.\n"
    )
    commands = [
        ["python3", "-m", "py_compile", *[
            str((HERE / name).relative_to(ROOT))
            for name in ("chunk.py", "produce.py", "verify.py")
        ]],
        ["python3", "-m", "jsonschema", "-i",
         str(CERT.relative_to(ROOT)), str((HERE / "schema.json").relative_to(ROOT))],
        ["python3", "-m", "unittest", "-v",
         "black_hole_programme.phase3."
         "axial_qnm_common_affine_evans_chunk_v3.test_chunk"],
        ["python3", "-m",
         "black_hole_programme.phase3."
         "axial_qnm_common_affine_evans_chunk_v3.verify"],
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
        "schema": (
            "phase3-axial-qnm-common-affine-evans-chunk-receipt-v3"
        ),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "checks": checks,
        "input_sha256": {name: sha(path) for name, path in imports.items()},
        "output_sha256": {
            "certificate": sha(CERT), "run": sha(RUN),
            "checkpoint": sha(CHECKPOINT), "report": sha(REPORT),
        },
        "artifact_sha256": {
            name: sha(HERE / name) for name in ARTIFACTS
        },
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": "materialized scoped tests and independent verifier",
        "higher_tiers_not_run": (
            "Bounded contour chunk; no theorem lifecycle, freeze or release."
        ),
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
