#!/usr/bin/env python3
"""Produce the bounded multi-panel projective Evans certificate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from .rail_v3 import CHUNK_CERT, CHUNK_RUN, RUN, V1, V2, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
ARTIFACTS = (
    "README.md",
    "__init__.py",
    "rail_v3.py",
    "produce.py",
    "schema.json",
    "test_rail_v3.py",
    "verify.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    started = time.monotonic()
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    imports = {
        "outgoing_projective_rail_v1": V1,
        "two_sided_projective_rail_v2": V2,
        "common_affine_chunk_certificate": CHUNK_CERT,
        "common_affine_chunk_run": CHUNK_RUN,
    }
    certificate = {
        "schema": "phase3-axial-qnm-projective-evans-riccati-rail-v3",
        "status": run["status"],
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha(path),
            }
            for name, path in imports.items()
        },
        "run": {
            "path": str(RUN.relative_to(ROOT)),
            "sha256": sha(RUN),
        },
        "result": run,
        "claim_flags": {
            "panels_0_through_15_typed_two_sided_at_r32": run["summary"][
                "two_sided_co_location_passed"
            ],
            "panels_0_through_15_delta_nonzero": run["summary"][
                "all_completed_deltas_exclude_zero"
            ],
            "delta_tau_nonzero_certified": (
                run["summary"]["delta_tau_excludes_zero_panel_count"] > 0
            ),
            "delta_omega_nonzero_certified": (
                run["summary"]["delta_omega_excludes_zero_panel_count"] > 0
            ),
            "full_contour_boundary_nonvanishing_certified": False,
            "interval_newton_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "does_not_establish": [
            "projective mismatch data for boundary panels 16--511",
            "boundary nonvanishing on a closed contour",
            "an interval-Newton or argument-principle QNM count",
            "a nonzero intrinsic QNM selector Delta_tau at a root",
            "a simple-root denominator Delta_omega on a root enclosure",
            "a Smith selector, defective QNM or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    summary = run["summary"]
    obstruction = run["local_qnm_gate"]["first_obstruction"]
    REPORT.write_text(
        "# Projective Evans/Riccati rail v3\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        f"Panels 0--{summary['completed_panel_count'] - 1} carry typed, "
        "co-located horizon/outgoing projective data at `r=32`.  Every "
        "completed `Delta=q_H-q_out+2*I*omega` enclosure excludes zero; "
        f"the minimum lower bound is "
        f"`{summary['minimum_delta_modulus_lower']}`.\n\n"
        "The local-QNM gate stops fail-closed at "
        f"`{obstruction['code']}`: panel "
        f"`{obstruction['first_missing_panel']}` is the first missing "
        "shared-generator endpoint export.  In parallel, none of the "
        "completed `Delta_tau` or `Delta_omega` rectangular balls excludes "
        "zero.  No interval Newton, argument principle, QNM, Smith, or EP2 "
        "claim is made.\n"
    )
    commands = [
        [
            "python3", "-m", "py_compile",
            str((HERE / "rail_v3.py").relative_to(ROOT)),
            str((HERE / "produce.py").relative_to(ROOT)),
            str((HERE / "verify.py").relative_to(ROOT)),
        ],
        [
            "python3", "-m", "jsonschema", "-i",
            str(CERT.relative_to(ROOT)),
            str((HERE / "schema.json").relative_to(ROOT)),
        ],
        [
            "python3", "-m", "unittest", "-v",
            "black_hole_programme.phase3."
            "axial_qnm_projective_evans_riccati_rail_v3.test_rail_v3",
        ],
        [
            "python3", "-m",
            "black_hole_programme.phase3."
            "axial_qnm_projective_evans_riccati_rail_v3.verify",
        ],
    ]
    checks = []
    for command in commands:
        before = time.monotonic()
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
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
            "phase3-axial-qnm-projective-evans-riccati-rail-receipt-v3"
        ),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "checks": checks,
        "input_sha256": {name: sha(path) for name, path in imports.items()},
        "output_sha256": {
            "certificate": sha(CERT),
            "run": sha(RUN),
            "report": sha(REPORT),
        },
        "artifact_sha256": {
            name: sha(HERE / name) for name in ARTIFACTS
        },
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": "scoped unit tests and independent recomputation verifier",
        "higher_tiers_not_run": (
            "No shared operator, theorem lifecycle, freeze or release changed."
        ),
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
