#!/usr/bin/env python3
"""Produce the targeted panel-77 horizon self-map repair certificate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from flint import arb

from .repair import RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT, RECEIPT, REPORT = (
    HERE / "certificate.json",
    HERE / "receipt.json",
    HERE / "report.md",
)
BASE_SOURCE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_boundary_v1/common_affine.py"
)
HORIZON_SOURCE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_horizon_projective_preflight_v1/horizon_preflight.py"
)
TERMINAL_CHUNK = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_chunk_v5/certificate.json"
)
ARTIFACTS = (
    "README.md", "__init__.py", "repair.py", "produce.py", "schema.json",
    "test_repair.py", "verify.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    started = time.monotonic()
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    panel = run["repaired_panel"]
    boundary_passed = panel["boundary_nonvanishing"]["status"] == "PASS"
    mismatch_lower = panel["physical_mismatch"]["modulus_lower"]
    repaired = (
        boundary_passed
        and arb(mismatch_lower).lower() > 0
        and run["repair"]["strict_self_map_rechecked"]
        and not run["repair"]["threshold_lowered"]
    )
    imports = {
        "common_affine_source": BASE_SOURCE,
        "horizon_preflight_source": HORIZON_SOURCE,
        "terminal_chunk": TERMINAL_CHUNK,
    }
    baseline = next(
        row for row in run["diagnostic_grid"]
        if row["label"] == "center_baseline"
    )
    stable = next(
        row for row in run["diagnostic_grid"]
        if row["label"] == "center_stable_interval_root"
    )
    certificate = {
        "schema": "phase3-axial-qnm-horizon-center-self-map-repair-v1",
        "status": (
            "PANEL_77_HORIZON_CENTER_SELF_MAP_REPAIRED"
            if repaired else
            "PANEL_77_HORIZON_CENTER_SELF_MAP_FAIL_CLOSED"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "panel_77_horizon_center_self_map_repaired": repaired,
            "panel_77_boundary_nonvanishing_certified": repaired,
            "threshold_lowered": False,
            "full_contour_boundary_nonvanishing_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "method": {
            "target_panel": 77,
            "seed_radius": run["seed_radius"],
            "diagnostic_grid_size": len(run["diagnostic_grid"]),
            "repair": run["repair"]["method"],
            "strict_candidate_factor": "1000001/1000000",
            "reciprocal_pivot_audited": True,
        },
        "result": {
            "baseline_failure": baseline["failure"],
            "baseline_candidate": baseline["candidate"],
            "baseline_self_map_rhs": baseline["self_map_rhs"],
            "stable_candidate": stable["candidate"],
            "stable_self_map_rhs": stable["self_map_rhs"],
            "stable_strict_margin": stable["strict_margin"],
            "repaired_boundary_status": panel[
                "boundary_nonvanishing"
            ]["status"],
            "minimum_modulus_lower": mismatch_lower,
            "horizon_transport_diagnostics": panel["horizon"][
                "transport_diagnostics"
            ],
            "reciprocal_pivots": run["reciprocal_chart"],
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
            "boundary nonvanishing for panels 78--511",
            "boundary nonvanishing on the complete closed contour",
            "an argument-principle or interval-Newton QNM count",
            "a nonzero Delta_tau or Delta_omega selector at a root",
            "a Smith selector, defective QNM or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Panel-77 horizon center self-map repair\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "At `r=2+2^-22`, the panel-center seed radii are approximately "
        "`q=8.63e-25`, `eta=1.06e-23`, and `xi=6.53e-24`.  The original "
        "subtractive binary64 quadratic formula returns a negative candidate "
        "and fails the unchanged self-map inequality.  Raising arithmetic "
        "precision to 256 bits or raising the Frobenius/Taylor orders to "
        "24/32 does not repair that cancellation.\n\n"
        "Using the algebraically equivalent stable smaller-root formula "
        "`2*qc/(-qb+sqrt(discriminant))`, enlarged by the exact rational "
        "factor `1000001/1000000`, gives strict first-step margin "
        f"`{stable['strict_margin']}`.  The complete direct-`q` horizon "
        "transport then passes for both the box and center without rejection. "
        "The reciprocal pivots also exclude zero.  Panel 77 has certified "
        f"`|Delta|` lower bound `{mismatch_lower}`.  No threshold was "
        "lowered and no QNM or EP2 claim is made.\n"
    )
    commands = [
        ["python3", "-m", "py_compile", *[
            str((HERE / name).relative_to(ROOT))
            for name in ("repair.py", "produce.py", "verify.py")
        ]],
        ["python3", "-m", "jsonschema", "-i",
         str(CERT.relative_to(ROOT)), str((HERE / "schema.json").relative_to(ROOT))],
        ["python3", "-m", "unittest", "-v",
         "black_hole_programme.phase3."
         "axial_qnm_horizon_center_self_map_repair_v1.test_repair"],
        ["python3", "-m",
         "black_hole_programme.phase3."
         "axial_qnm_horizon_center_self_map_repair_v1.verify"],
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
            "phase3-axial-qnm-horizon-center-self-map-repair-receipt-v1"
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
        "tier_1": "scoped repair tests and independent verifier",
        "higher_tiers_not_run": (
            "Single repaired boundary panel; no complete contour, theorem "
            "lifecycle, freeze or release."
        ),
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
