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
    mismatch = row["physical_mismatch"]
    if gate["status"] == "PASS":
        disposition = (
            "The tightened physical mismatch is certified nonzero on panel "
            "0.  Its independent residual radius is "
            f"`{mismatch['independent_residual_radius']}`, and its modulus "
            f"lower bound is `{mismatch['modulus_lower']}`.  This is a "
            "panel-local boundary result only."
        )
    else:
        disposition = (
            "The independent post-polynomial residuals remain too wide for "
            "the physical mismatch: the residual radius is "
            f"`{mismatch['independent_residual_radius']}` and the modulus "
            f"lower bound is `{mismatch['modulus_lower']}`.  The panel-0 "
            "boundary gate therefore remains fail-closed."
        )
    return (
        "# Common-affine projective Evans panel-0 repair\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The consumer now has an explicit shared panel-local generator and "
        "the typed opposite-phase rule\n"
        "`Delta=q_H-q_out+2*I*omega`.  Endpoint exports are required to "
        "subtract centered `q`, `q_tau`, and `q_omega` polynomials before "
        "adding independent residuals.\n\n"
        "The bounded repair covers panel `0` only.  The earlier adaptive "
        "halving repairs are followed by order-26 direct-`q` transport with "
        "radial recentering at both endpoints.  Both endpoint box and "
        "singleton transports reach `r=32`, and both centered polynomial "
        "exports are emitted.\n\n"
        f"The mismatch polynomial coefficients are "
        f"`{mismatch['polynomial_coefficients']}`.  {disposition}\n\n"
        "The other 511 panels and the argument-principle count were not "
        "run; no QNM or EP2 claim follows from this single-panel gate.\n"
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
            "PANEL0_COMMON_AFFINE_EVANS_BOUNDARY_NONVANISHING_CERTIFIED"
            if gate["status"] == "PASS" else
            "PANEL0_ENDPOINT_EXPORTS_CERTIFIED_BOUNDARY_FAIL_CLOSED"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "shared_panel_local_omega_generator_implemented": True,
            "opposite_endpoint_phase_convention_explicit": True,
            "both_endpoint_polynomial_exports_completed": (
                run["rows"][0]["horizon"]["passed"]
                and run["rows"][0]["outgoing"]["passed"]
            ),
            "panel0_Evans_boundary_nonzero_certified": (
                gate["status"] == "PASS"
            ),
            "full_Evans_boundary_nonzero_certified": False,
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
            "outgoing_repair": (
                "adaptive radial halving; minimum attempted magnitude 1/320"
            ),
            "horizon_repair": (
                "order-26 direct-q transport with steps capped by (r-2)/16 "
                "near the regular singular point and adaptive halving"
            ),
            "tightened_gate": (
                "panel-0 physical mismatch after order-26 centered endpoint "
                "exports"
            ),
            "bounded_stop": "panel 0 only"
        },
        "result": {
            "requested_panel_count": run["panel_count"],
            "executed_panel_limit": run["panel_limit"],
            "completed_panel_count": len(run["rows"]),
            "passed_boundary_panel_count": gate["passed_panel_count"],
            "first_failure": first,
            "horizon_export": run["rows"][0]["horizon"],
            "outgoing_export": run["rows"][0]["outgoing"],
            "physical_mismatch": run["rows"][0]["physical_mismatch"],
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
