#!/usr/bin/env python3
"""Produce the stable-root panels 0--97 projective Evans aggregate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from .aggregate import (
    CHUNK_CERT,
    CHUNK_RUN,
    RUN,
    V9_CERT,
    V9_RUN,
    compute,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT, RECEIPT, REPORT = (
    HERE / "certificate.json",
    HERE / "receipt.json",
    HERE / "report.md",
)
ARTIFACTS = (
    "README.md", "__init__.py", "aggregate.py", "produce.py", "schema.json",
    "test_aggregate.py", "verify.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    started = time.monotonic()
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    imports = {
        "projective_rail_v9_certificate": V9_CERT,
        "projective_rail_v9_run": V9_RUN,
        "stable_root_chunk_certificate": CHUNK_CERT,
        "stable_root_chunk_run": CHUNK_RUN,
    }
    summary = run["summary"]
    obstruction = run["local_qnm_gate"]["first_obstruction"]
    certificate = {
        "schema": "phase3-axial-qnm-projective-evans-riccati-rail-v10",
        "status": run["status"],
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)), "sha256": sha(path)
            }
            for name, path in imports.items()
        },
        "run": {
            "path": str(RUN.relative_to(ROOT)), "sha256": sha(RUN)
        },
        "result": run,
        "claim_flags": {
            "panels_0_through_97_typed_two_sided_at_r32": (
                summary["contiguous_prefix"]
                and summary["two_sided_interface_gates_pass"]
            ),
            "panels_0_through_97_delta_nonzero": summary[
                "all_completed_deltas_exclude_zero"
            ],
            "panel_98_endpoint_export_certified": False,
            "stable_root_repair_applied_from_panel_77": True,
            "threshold_lowered": False,
            "full_contour_boundary_nonvanishing_certified": False,
            "interval_newton_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "does_not_establish": [
            "a certified common-affine mismatch exclusion for panel 98",
            "projective mismatch data for boundary panels 98--511",
            "boundary nonvanishing on the complete closed contour",
            "an interval-Newton or argument-principle QNM count",
            "a nonzero intrinsic QNM selector Delta_tau at a root",
            "a simple-root denominator Delta_omega on a root enclosure",
            "a Smith selector, defective QNM or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Projective Evans/Riccati rail v10\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The stable interval-root rail extends the contiguous typed "
        "two-sided prefix through panel 97 at `r=32`.  Every admitted Delta "
        "excludes zero.  The minimum lower bound is "
        f"`{summary['minimum_delta_modulus_lower']}` on panel "
        f"`{summary['minimum_delta_modulus_lower_panel']}`.  Ordered "
        f"transport stopped at panel `{obstruction['first_missing_panel']}` "
        f"with `{obstruction['code']}`.  No threshold was lowered and no "
        "Newton, QNM, Smith, or EP2 claim is made.\n"
    )
    commands = [
        ["python3", "-m", "py_compile", *[
            str((HERE / name).relative_to(ROOT))
            for name in ("aggregate.py", "produce.py", "verify.py")
        ]],
        ["python3", "-m", "jsonschema", "-i",
         str(CERT.relative_to(ROOT)), str((HERE / "schema.json").relative_to(ROOT))],
        ["python3", "-m", "unittest", "-v",
         "black_hole_programme.phase3."
         "axial_qnm_projective_evans_riccati_rail_v10.test_aggregate"],
        ["python3", "-m",
         "black_hole_programme.phase3."
         "axial_qnm_projective_evans_riccati_rail_v10.verify"],
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
            "phase3-axial-qnm-projective-evans-riccati-rail-receipt-v10"
        ),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "checks": checks,
        "input_sha256": {name: sha(path) for name, path in imports.items()},
        "output_sha256": {
            "certificate": sha(CERT), "run": sha(RUN), "report": sha(REPORT)
        },
        "artifact_sha256": {
            name: sha(HERE / name) for name in ARTIFACTS
        },
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": "scoped unit tests and independent aggregate verifier",
        "higher_tiers_not_run": (
            "Terminal boundary mismatch failure; no theorem lifecycle, "
            "freeze or release."
        ),
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
