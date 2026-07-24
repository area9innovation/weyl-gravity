#!/usr/bin/env python3
"""Produce the bounded common-affine Evans boundary certificate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from .common_affine import RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
TOP_REPORT = ROOT / (
    "reports/phase3-axial-qnm-common-affine-evans-boundary-"
    "2026-07-24.md"
)
CONTRACT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_export_contract_v1/certificate.json"
)
OUTGOING = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_ecs_affine_projective_transport_v1/certificate.json"
)
HORIZON = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_horizon_reciprocal_checkpoint_transport_v1/certificate.json"
)
ARTIFACTS = (
    "README.md",
    "__init__.py",
    "common_affine.py",
    "produce.py",
    "schema.json",
    "test_common_affine.py",
    "verify.py"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _report(run: dict) -> str:
    gate = run["gates"]["boundary_nonvanishing"]
    row = run["rows"][0]
    return (
        "# Common-affine projective Evans boundary attempt\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The consumer now has an explicit shared panel-local generator and "
        "the typed opposite-phase rule\n"
        "`Delta=q_H-q_out+2*I*omega`.  Endpoint exports are required to "
        "subtract centered `q`, `q_tau`, and `q_omega` polynomials before "
        "adding independent residuals.\n\n"
        f"The bounded run stopped on panel `{row['panel']}` of "
        f"`{run['panel_count']}`.  The outgoing box transport passed, but "
        f"its singleton-center validation failed with "
        f"`{row['outgoing']['failure']}` at `r={row['outgoing']['radius']}`. "
        f"The horizon box validation failed with "
        f"`{row['horizon']['failure']}` at `r={row['horizon']['radius']}`. "
        "Accordingly no endpoint polynomial pair was emitted and the "
        f"boundary gate is `{gate['status']}`.\n\n"
        "This is a representation/majorant obstruction, not evidence for a "
        "zero of the physical mismatch.  No argument-principle count was "
        "run.\n"
    )


def main() -> None:
    start = time.monotonic()
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    gate = run["gates"]["boundary_nonvanishing"]
    first = gate["first_failure"]
    certificate = {
        "schema": "phase3-axial-qnm-common-affine-evans-boundary-v1",
        "status": (
            "COMMON_AFFINE_EVANS_BOUNDARY_NONVANISHING_CERTIFIED"
            if gate["status"] == "PASS" else
            "FAIL_CLOSED_AT_FIRST_COMMON_AFFINE_ENDPOINT_EXPORT"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "shared_panel_local_omega_generator_implemented": True,
            "opposite_endpoint_phase_convention_explicit": True,
            "both_endpoint_polynomial_exports_completed": (
                gate["status"] == "PASS"
            ),
            "Evans_boundary_nonzero_certified": gate["status"] == "PASS",
            "argument_principle_root_count_certified": False,
            "QNM_or_EP2_certified": False
        },
        "method": {
            "generator": "zeta=omega-omega_center",
            "generator_identity_shared_by": [
                "horizon endpoint",
                "outgoing endpoint",
                "physical mismatch"
            ],
            "endpoint_fields": [
                "q_polynomial_coefficients",
                "q_tau_polynomial_coefficients",
                "q_omega_polynomial_coefficients",
                "independent_residual_radius"
            ],
            "q_remainder": (
                "fundamental-theorem bound after subtracting "
                "q(omega_center)+q_omega(omega_center)*zeta"
            ),
            "physical_mismatch": "Delta=q_H-q_out+2*I*omega",
            "bounded_stop": "first failed endpoint export or boundary panel"
        },
        "result": {
            "requested_panel_count": run["panel_count"],
            "completed_panel_count": len(run["rows"]),
            "passed_boundary_panel_count": gate["passed_panel_count"],
            "first_failure": first,
            "horizon_failure": run["rows"][0]["horizon"],
            "outgoing_failure": run["rows"][0]["outgoing"],
            "argument_principle_status": (
                run["gates"]["argument_principle_root_count"]["status"]
            )
        },
        "imports": {
            "contract": {
                "path": str(CONTRACT.relative_to(ROOT)),
                "sha256": sha(CONTRACT)
            },
            "outgoing_transport": {
                "path": str(OUTGOING.relative_to(ROOT)),
                "sha256": sha(OUTGOING)
            },
            "horizon_transport": {
                "path": str(HORIZON.relative_to(ROOT)),
                "sha256": sha(HORIZON)
            }
        },
        "run": {
            "path": str(RUN.relative_to(ROOT)),
            "sha256": sha(RUN)
        },
        "does_not_establish": [
            "nonvanishing of the physical Evans mismatch on the contour",
            "an argument-principle QNM count",
            "a QNM location, Smith selector, defective fibre or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim"
        ]
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    text = _report(run)
    REPORT.write_text(text)
    TOP_REPORT.write_text(text)
    commands = [
        [
            "python3", "-m", "py_compile",
            "black_hole_programme/phase3/"
            "axial_qnm_common_affine_evans_boundary_v1/common_affine.py",
            "black_hole_programme/phase3/"
            "axial_qnm_common_affine_evans_boundary_v1/produce.py",
            "black_hole_programme/phase3/"
            "axial_qnm_common_affine_evans_boundary_v1/verify.py"
        ],
        [
            "python3", "-m", "jsonschema", "-i",
            "black_hole_programme/phase3/"
            "axial_qnm_common_affine_evans_boundary_v1/certificate.json",
            "black_hole_programme/phase3/"
            "axial_qnm_common_affine_evans_boundary_v1/schema.json"
        ],
        [
            "python3", "-m", "unittest",
            "black_hole_programme.phase3."
            "axial_qnm_common_affine_evans_boundary_v1.test_common_affine"
        ],
        [
            "python3", "-m",
            "black_hole_programme.phase3."
            "axial_qnm_common_affine_evans_boundary_v1.verify"
        ]
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
            "stderr": result.stderr
        })
    RECEIPT.write_text(json.dumps({
        "schema": "phase3-axial-qnm-common-affine-evans-boundary-receipt-v1",
        "elapsed_seconds": round(time.monotonic() - start, 6),
        "checks": checks,
        "input_sha256": {
            "contract": sha(CONTRACT),
            "outgoing_transport": sha(OUTGOING),
            "horizon_transport": sha(HORIZON)
        },
        "output_sha256": {
            "certificate": sha(CERT),
            "run": sha(RUN),
            "report": sha(REPORT),
            "top_report": sha(TOP_REPORT)
        },
        "artifact_sha256": {
            name: sha(HERE / name) for name in ARTIFACTS
        },
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": "scoped unit test and independent verifier",
        "higher_tiers_not_run": (
            "No shared operator, theorem lifecycle, freeze or release changed."
        )
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
