#!/usr/bin/env python3
"""Produce the QNM-band horizon projective preflight certificate."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from .horizon_preflight import ECS, INFINITY_RUN, MOVING, RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md", "report.md", "schema.json", "horizon_preflight.py",
    "produce.py", "verify.py", "test_horizon_preflight.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def produce() -> dict:
    moving = json.loads(MOVING.read_text())
    if moving["moving_phase"]["dot_lambda_H"] != "0":
        raise RuntimeError("imported horizon exponent moves under tau")
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    rows = run["rows"]
    if not all(row["coefficient_majorant_seed_gate"] for row in rows):
        raise RuntimeError("QNM-band Frobenius coefficient gate failed")
    radii = [float(Fraction(row["last_radius"])) for row in rows]
    failures = sorted({
        row["terminal"]["failure"] for row in rows if row["terminal"]
    })
    reached = [row["panel"] for row in rows if row["reached_r32"]]
    return {
        "schema": "phase3-axial-qnm-horizon-projective-preflight-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "QNM_BAND_MOVING_PHASE_HORIZON_GERM_CERTIFIED_BUT_AFFINE_"
            "PROJECTIVE_REFERENCE_MAJORANT_REFUSES_BEFORE_R32"
        ),
        "imports": {
            "moving_phase": {
                "path": str(MOVING.relative_to(ROOT)),
                "sha256": sha256(MOVING),
            },
            "ecs_disk": {
                "path": str(ECS.relative_to(ROOT)), "sha256": sha256(ECS),
            },
            "infinity_affine_run": {
                "path": str(INFINITY_RUN.relative_to(ROOT)),
                "sha256": sha256(INFINITY_RUN),
            },
        },
        "horizon_germ": {
            "phase": "psi=exp(I*omega*r_star)*P",
            "selected_exponent": "0",
            "dot_lambda_H": "0",
            "tau_log_required": False,
            "seed_radius": "rho=2^-22",
            "frobenius_order": 16,
            "coefficient_majorant": (
                "|base_n|,|tau_n|,|omega_n| <= 10^6*100^n"
            ),
            "majorant_induction": (
                "for n>=16 the base/tau recurrence multiplier is below 2 "
                "and the omega-differentiated multiplier is below 30; all "
                "coefficients through n=15 pass the stronger 100^n gate"
            ),
            "all_panel_seed_gates_pass": True,
        },
        "transport": {
            "variables": (
                "phase-reduced q=P_x/P, eta=d_tau q, xi=d_omega q"
            ),
            "transformation": (
                "with omega'=-omega, (q,-eta,-xi) uses the infinity "
                "reference Taylor equations"
            ),
            "geometric_step": "min((r-2)/16,1/20,32-r)",
            "panels_reaching_r32": reached,
            "all_panels_reach_r32": len(reached) == 16,
            "first_refusal_radius_range": [
                str(min(radii)), str(max(radii))
            ],
            "failure_kinds": failures,
            "run_artifact": {
                "path": str(RUN.relative_to(ROOT)), "sha256": sha256(RUN),
            },
        },
        "mismatch": {
            "assembled": False,
            "reason": (
                "no horizon panel reaches r=32 under the certified "
                "reference majorant, so Delta, Delta_tau and Delta_omega "
                "are intentionally not formed"
            ),
        },
        "claim_flags": {
            "qnm_band_horizon_moving_phase_seed_certified": True,
            "dot_lambda_H_exactly_zero": True,
            "horizon_projective_line_at_r32_certified": False,
            "projective_mismatch_at_r32_computed": False,
            "Evans_boundary_nonzero_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "shortfall": (
            "The selected moving-phase germ and its tau/omega jets are "
            "regular on every QNM panel. During outward transport, the "
            "absolute Cauchy majorant used for the singleton reference "
            "trajectory loses a positive Riccati discriminant while the "
            "affine remainder is still defined. The first refusal occurs "
            "at the exact radii in horizon-run.json. A phase-reduced "
            "reference logarithmic norm or direct Frobenius continuation "
            "must replace that absolute reference majorant."
        ),
        "does_not_establish": [
            "a horizon-selected line at r=32",
            "Delta, Delta_tau or Delta_omega",
            "a nonzero Evans boundary or argument-principle count",
            "a QNM, Smith selector or exceptional point",
        ],
    }


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-horizon-projective-preflight-receipt-v1",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "input_sha256": {
            "moving_phase": sha256(MOVING),
            "ecs_disk": sha256(ECS),
            "infinity_affine_run": sha256(INFINITY_RUN),
        },
        "artifact_sha256": {
            name: sha256(HERE / name) for name in ARTIFACTS
        },
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_qnm_horizon_projective_preflight_v1.produce",
            "python3 -m black_hole_programme.phase3.axial_qnm_horizon_projective_preflight_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase3.axial_qnm_horizon_projective_preflight_v1.test_horizon_preflight",
            "python3 -m py_compile black_hole_programme/phase3/axial_qnm_horizon_projective_preflight_v1/*.py",
        ],
        "tier_2_not_run": (
            "No shared operator changed; this is a fail-closed endpoint "
            "preflight over content-addressed moving-phase inputs."
        ),
        "tier_3_not_run": "Not a freeze or theorem promotion.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
