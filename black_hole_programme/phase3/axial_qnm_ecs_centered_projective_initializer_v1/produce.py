#!/usr/bin/env python3
"""Produce the centered phase-factored projective initializer certificate."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from .centered_initializer import ECS, RUN, TAIL, TANGENT, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md", "report.md", "schema.json", "centered_initializer.py",
    "produce.py", "verify.py", "test_centered_initializer.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def produce() -> dict:
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    rows = run["rows"]
    if not all(row["base"]["value_ball_excludes_zero"] for row in rows):
        raise RuntimeError("a reduced outgoing value ball contains zero")
    if not all(
        row["first_projective_segment"]["certified"] for row in rows
    ):
        raise RuntimeError("the first projective segment is not certified")
    last_radii = [
        float(Fraction(
            row["q_only_continuation_preflight"]["last_certified_radius"]
        ))
        for row in rows
    ]
    return {
        "schema": "phase3-axial-qnm-ecs-centered-projective-initializer-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "PHASE_FACTORED_FINITE_ASYMPTOTIC_CENTER_WITH_RESIDUAL_ONLY_"
            "VOLTERRA_BALL_FOR_Q_ETA_XI_AND_FIRST_PROJECTIVE_SEGMENT"
        ),
        "imports": {
            "ecs": {"path": str(ECS.relative_to(ROOT)), "sha256": sha256(ECS)},
            "tail": {"path": str(TAIL.relative_to(ROOT)), "sha256": sha256(TAIL)},
            "tangent": {
                "path": str(TANGENT.relative_to(ROOT)),
                "sha256": sha256(TANGENT),
            },
        },
        "method": {
            "phase": "y=exp(-I*omega*r_star)*v",
            "expanded_object": (
                "the reduced amplitude v, never the omega-dependent phase"
            ),
            "finite_center": "order-16 z=1/r asymptotic recurrence",
            "remainder": (
                "the exact finite-center differential residual is inserted "
                "as an inhomogeneity into the already certified ECS "
                "Volterra contraction; only the correction is balled"
            ),
            "sensitivities": (
                "tau and omega coefficient recurrences share the same base "
                "acb panel and are converted together to q, eta=d_tau q "
                "and xi=d_omega q"
            ),
        },
        "panel_results": {
            "panel_count": len(rows),
            "all_reduced_value_balls_exclude_zero": True,
            "all_q_eta_xi_initializers_constructed": True,
            "all_first_q_segments_certified": True,
            "first_segment": "r=45 to r=899/20",
            "q_only_continuation_last_radius_range": [
                str(min(last_radii)), str(max(last_radii))
            ],
            "q_only_terminal_statuses": sorted({
                row["q_only_continuation_preflight"]["terminal_status"]
                for row in rows
            }),
            "run_artifact": {
                "path": str(RUN.relative_to(ROOT)),
                "sha256": sha256(RUN),
            },
        },
        "claim_flags": {
            "phase_factored_centered_base_initializer_certified": True,
            "centered_tau_projective_initializer_certified": True,
            "centered_omega_projective_initializer_certified": True,
            "first_inward_projective_segment_certified": True,
            "full_inward_projective_transport_certified": False,
            "horizon_moving_phase_jet_certified": False,
            "Evans_boundary_nonzero_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "shortfall": (
            "The centered q rail removes the immediate r approximately 43.2 "
            "failure of the coarse initializer and reaches r between about "
            "39.55 and 40.2, depending on panel. Rectangular Taylor/Cauchy "
            "wrapping then makes the scalar Riccati majorant discriminant "
            "nonpositive. A QR/Lohner or recentered multi-chart rail is "
            "still required for full contour transport."
        ),
        "does_not_establish": [
            "a horizon moving-phase Frobenius jet or dot(lambda_H)",
            "transport of q, eta and xi to the matching radius",
            "a two-sided Evans boundary enclosure",
            "an argument-principle QNM count",
            "a QNM, Smith selector or exceptional point",
        ],
    }


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-ecs-centered-projective-receipt-v1",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "input_sha256": {
            "ecs": sha256(ECS), "tail": sha256(TAIL),
            "tangent": sha256(TANGENT),
        },
        "artifact_sha256": {
            name: sha256(HERE / name) for name in ARTIFACTS
        },
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_centered_projective_initializer_v1.produce",
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_centered_projective_initializer_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase3.axial_qnm_ecs_centered_projective_initializer_v1.test_centered_initializer",
            "python3 -m py_compile black_hole_programme/phase3/axial_qnm_ecs_centered_projective_initializer_v1/*.py",
        ],
        "tier_2_not_run": (
            "No shared operator changed; this successor recomputes one "
            "content-addressed endpoint rail and its first transport segment."
        ),
        "tier_3_not_run": "Not a freeze or theorem promotion.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
