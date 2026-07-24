#!/usr/bin/env python3
"""Produce the projective Evans/Riccati rail certificate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from .rail import RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
SENSITIVITY = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_sensitivity_v1/certificate.json"
)
CENTERED = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_ecs_centered_projective_initializer_v1/certificate.json"
)
COMMON = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_boundary_v1/certificate.json"
)
ARTIFACTS = (
    "README.md",
    "__init__.py",
    "rail.py",
    "produce.py",
    "schema.json",
    "test_rail.py",
    "verify.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    started = time.monotonic()
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    if not run["passed"]:
        status = "FAIL_CLOSED_PROJECTIVE_RICCATI_PREFLIGHT"
    else:
        status = "OUTGOING_PROJECTIVE_Q_QTAU_QOMEGA_ONE_PANEL_CERTIFIED"
    imports = {
        "exact_projective_sensitivity": SENSITIVITY,
        "centered_outgoing_initializer": CENTERED,
        "common_affine_phase_convention": COMMON,
    }
    certificate = {
        "schema": "phase3-axial-qnm-projective-evans-riccati-rail-v1",
        "status": status,
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
            "typed_projective_chart_certified": run["passed"],
            "outgoing_seed_pivot_excludes_zero": (
                run["passed"]
                and run["chart_gate"]["pivot_excludes_zero"]
            ),
            "joint_q_qtau_qomega_one_panel_transport_certified": run["passed"],
            "horizon_projective_line_certified_here": False,
            "two_sided_projective_mismatch_certified_here": False,
            "full_contour_boundary_nonvanishing_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "does_not_establish": [
            "a horizon projective endpoint line",
            "a two-sided projective Evans mismatch at a match point",
            "boundary nonvanishing on a closed contour",
            "an interval-Newton or argument-principle QNM count",
            "a Smith selector, defective QNM or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Projective Evans/Riccati rail v1\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The outgoing spin-two endpoint line is represented in the typed "
        "phase-factored chart `q=(partial_x P_out)/P_out`.  The reduced "
        "amplitude pivot excludes zero on refined spectral panel 0/512.  "
        "The correlated state `(q,q_tau,q_omega)` completes one validated "
        "radial Taylor/affine-remainder step from `r=45` to `r=899/20`.\n\n"
        "This is deliberately a one-endpoint, one-panel certificate.  No "
        "two-sided mismatch, closed-contour root count, QNM, Smith selector "
        "or EP2 is established.\n"
    )
    commands = [
        [
            "python3", "-m", "py_compile",
            str((HERE / "rail.py").relative_to(ROOT)),
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
            "axial_qnm_projective_evans_riccati_rail_v1.test_rail",
        ],
        [
            "python3", "-m",
            "black_hole_programme.phase3."
            "axial_qnm_projective_evans_riccati_rail_v1.verify",
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
            "phase3-axial-qnm-projective-evans-riccati-rail-receipt-v1"
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
