#!/usr/bin/env python3
"""Produce the bounded panels 0--15 Evans chunk certificate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from flint import arb

from .chunk import CHECKPOINT, RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
TOP_REPORT = ROOT / (
    "reports/phase3-axial-qnm-common-affine-evans-chunk-2026-07-24.md"
)
BASE_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_boundary_v1/certificate.json"
)
BASE_SOURCE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_boundary_v1/common_affine.py"
)
ARTIFACTS = (
    "README.md",
    "__init__.py",
    "chunk.py",
    "produce.py",
    "schema.json",
    "test_chunk.py",
    "verify.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _minimum(run: dict) -> tuple[int, str]:
    row = min(
        run["rows"],
        key=lambda item: arb(
            item["physical_mismatch"]["modulus_lower"]
        ).lower(),
    )
    return row["panel"], row["physical_mismatch"]["modulus_lower"]


def _report(run: dict) -> str:
    panel, lower = _minimum(run)
    return (
        "# Common-affine projective Evans contour chunk\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "A four-worker checkpointed rail certifies panels `0` through `15` "
        "of the 512-panel contour.  Every panel uses one generator shared "
        "by the horizon endpoint, outgoing endpoint, and the physical "
        "mismatch `Delta=q_H-q_out+2*I*omega`.\n\n"
        "All 16 requested panels emit both endpoint polynomials and have a "
        "strictly positive physical-mismatch modulus lower bound.  The "
        f"smallest bound is `{lower}` on panel `{panel}`.\n\n"
        "This is not a closed-contour certificate.  Panels 16 through 511 "
        "and the argument-principle count were not run, so no QNM count or "
        "EP2 claim follows.\n"
    )


def main() -> None:
    start = time.monotonic()
    run = compute(write_checkpoint=True)
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    panel, lower = _minimum(run)
    complete = run["all_requested_panels_nonzero"]
    certificate = {
        "schema": "phase3-axial-qnm-common-affine-evans-chunk-v1",
        "status": (
            "PANELS_0_THROUGH_15_BOUNDARY_NONVANISHING_CERTIFIED"
            if complete else "CHUNK_FAIL_CLOSED"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "panels_0_through_15_nonzero_certified": complete,
            "full_contour_nonzero_certified": False,
            "argument_principle_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "method": {
            "requested_panels": [0, 15],
            "full_contour_panel_count": run["full_contour_panel_count"],
            "worker_count": run["worker_count"],
            "batch_size": run["batch_size"],
            "checkpoint_after_each_batch": True,
            "ordered_stop_rule": run["stop_rule"],
            "shared_generator": (
                "one panel-local zeta=omega-omega_center generator per "
                "horizon/outgoing/mismatch triple"
            ),
            "physical_mismatch": "Delta=q_H-q_out+2*I*omega",
        },
        "result": {
            "completed_panel_count": run["completed_panel_count"],
            "terminal": run["terminal"],
            "minimum_modulus_lower_panel": panel,
            "minimum_modulus_lower": lower,
            "argument_principle_status": (
                run["argument_principle"]["status"]
            ),
        },
        "imports": {
            "panel0_certificate": {
                "path": str(BASE_CERT.relative_to(ROOT)),
                "sha256": sha(BASE_CERT),
            },
            "tightened_transport_source": {
                "path": str(BASE_SOURCE.relative_to(ROOT)),
                "sha256": sha(BASE_SOURCE),
            },
        },
        "run": {
            "path": str(RUN.relative_to(ROOT)),
            "sha256": sha(RUN),
        },
        "does_not_establish": [
            "boundary nonvanishing on panels 16 through 511",
            "boundary nonvanishing on the complete closed contour",
            "an argument-principle QNM count",
            "a QNM location, Smith selector, defective fibre or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    text = _report(run)
    REPORT.write_text(text)
    TOP_REPORT.write_text(text)
    commands = [
        [
            "python3", "-m", "py_compile",
            "black_hole_programme/phase3/"
            "axial_qnm_common_affine_evans_chunk_v1/chunk.py",
            "black_hole_programme/phase3/"
            "axial_qnm_common_affine_evans_chunk_v1/produce.py",
            "black_hole_programme/phase3/"
            "axial_qnm_common_affine_evans_chunk_v1/verify.py",
        ],
        [
            "python3", "-m", "jsonschema", "-i",
            "black_hole_programme/phase3/"
            "axial_qnm_common_affine_evans_chunk_v1/certificate.json",
            "black_hole_programme/phase3/"
            "axial_qnm_common_affine_evans_chunk_v1/schema.json",
        ],
        [
            "python3", "-m", "unittest",
            "black_hole_programme.phase3."
            "axial_qnm_common_affine_evans_chunk_v1.test_chunk",
        ],
        [
            "python3", "-m",
            "black_hole_programme.phase3."
            "axial_qnm_common_affine_evans_chunk_v1.verify",
        ],
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
        "schema": "phase3-axial-qnm-common-affine-evans-chunk-receipt-v1",
        "elapsed_seconds": round(time.monotonic() - start, 6),
        "checks": checks,
        "input_sha256": {
            "panel0_certificate": sha(BASE_CERT),
            "tightened_transport_source": sha(BASE_SOURCE),
        },
        "output_sha256": {
            "certificate": sha(CERT),
            "run": sha(RUN),
            "checkpoint": sha(CHECKPOINT),
            "report": sha(REPORT),
            "top_report": sha(TOP_REPORT),
        },
        "artifact_sha256": {
            name: sha(HERE / name) for name in ARTIFACTS
        },
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": "materialized scoped unit tests and independent verifier",
        "higher_tiers_not_run": (
            "The artifact covers a bounded contour chunk only and does not "
            "promote a theorem lifecycle, freeze or release."
        ),
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
