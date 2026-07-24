#!/usr/bin/env python3
"""Produce the two-sided projective Evans/Riccati successor."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from .rail_v2 import COMMON_CERT, COMMON_RUN, RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
MOVING = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_horizon_moving_phase_v1/certificate.json"
)
HORIZON = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_horizon_projective_preflight_v1/certificate.json"
)
V1 = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_riccati_rail_v1/certificate.json"
)
ARTIFACTS = (
    "README.md",
    "__init__.py",
    "rail_v2.py",
    "produce.py",
    "schema.json",
    "test_rail_v2.py",
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
        "horizon_moving_phase": MOVING,
        "horizon_projective_preflight": HORIZON,
        "common_affine_certificate": COMMON_CERT,
        "common_affine_run": COMMON_RUN,
    }
    certificate = {
        "schema": "phase3-axial-qnm-projective-evans-riccati-rail-v2",
        "status": (
            "TYPED_TWO_SIDED_PANEL0_PROJECTIVE_MISMATCH_CERTIFIED"
            if run["passed"] else
            "FAIL_CLOSED_TWO_SIDED_PROJECTIVE_INTERFACE"
        ),
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
            "typed_horizon_projective_line_certified": run["horizon"][
                "passed"
            ],
            "horizon_fixed_chart_one_panel_transport_certified": run[
                "horizon"
            ]["passed"],
            "shared_omega_generator_certified": run["interface_gates"][
                "shared_omega_generator"
            ],
            "panel0_two_sided_projective_mismatch_certified": run[
                "common_match"
            ]["passed"],
            "panel0_mismatch_excludes_zero": run["common_match"][
                "mismatch"
            ]["excludes_zero"],
            "full_contour_boundary_nonvanishing_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "does_not_establish": [
            "projective mismatch nonvanishing on the other 511 panels",
            "boundary nonvanishing on a closed contour",
            "an interval-Newton or argument-principle QNM count",
            "a Smith selector, defective QNM or EP2",
            "a complete outgoing Bach frame or physical T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Projective Evans/Riccati rail v2\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The moving-phase horizon line is typed as "
        "`q_H=(partial_x P_H)/P_H` with "
        "`psi=exp(+I*omega*r_star)P_H`.  Its refined panel-0 pivot excludes "
        "zero, the post-normalization `(q_H,q_H_tau,q_H_omega)` state is "
        "finite, and one fixed-chart radial step is certified.\n\n"
        "At `r=32`, the horizon and outgoing exports share one omega "
        "generator.  The independently reassembled mismatch "
        "`Delta=q_H-q_out+2*I*omega` excludes zero on panel 0, with typed "
        "tau and omega sensitivity enclosures.\n\n"
        "This covers one of 512 panels.  It does not establish a closed "
        "contour count, QNM, Smith selector, EP2, or physical `T_plus`.\n"
    )
    commands = [
        [
            "python3", "-m", "py_compile",
            str((HERE / "rail_v2.py").relative_to(ROOT)),
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
            "axial_qnm_projective_evans_riccati_rail_v2.test_rail_v2",
        ],
        [
            "python3", "-m",
            "black_hole_programme.phase3."
            "axial_qnm_projective_evans_riccati_rail_v2.verify",
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
            "phase3-axial-qnm-projective-evans-riccati-rail-receipt-v2"
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
