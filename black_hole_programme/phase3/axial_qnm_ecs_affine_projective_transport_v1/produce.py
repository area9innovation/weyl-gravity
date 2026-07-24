#!/usr/bin/env python3
"""Produce the affine midpoint-recentered projective transport certificate."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from .affine_transport import ECS, RUN, TAIL, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INITIALIZER = (
    ROOT / "black_hole_programme/phase3/"
    "axial_qnm_ecs_centered_projective_initializer_v1/certificate.json"
)
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md", "report.md", "schema.json", "affine_transport.py",
    "produce.py", "verify.py", "test_affine_transport.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def produce() -> dict:
    run = compute()
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    rows = run["rows"]
    if not all(row["match_radius_certified"] for row in rows):
        raise RuntimeError("the common r=32 match radius was not certified")
    terminal_radii = [
        float(Fraction(row["first_terminal_obstruction"]["radius"]))
        for row in rows
    ]
    return {
        "schema": "phase3-axial-qnm-ecs-affine-projective-transport-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "AFFINE_MIDPOINT_RECENTERED_Q_ETA_XI_TRANSPORT_CERTIFIED_TO_"
            "R32_WITH_QUANTIFIED_INWARD_REMAINDER_BOTTLENECK"
        ),
        "imports": {
            "centered_initializer": {
                "path": str(INITIALIZER.relative_to(ROOT)),
                "sha256": sha256(INITIALIZER),
            },
            "ecs": {"path": str(ECS.relative_to(ROOT)), "sha256": sha256(ECS)},
            "tail": {"path": str(TAIL.relative_to(ROOT)), "sha256": sha256(TAIL)},
        },
        "method": {
            "reference": (
                "order-14 midpoint Taylor trajectory, recentered after each "
                "step of size 1/20"
            ),
            "shared_parameter_remainder": (
                "one omega-panel radius and simultaneous q, eta, xi radii"
            ),
            "key_reconditioning": (
                "the q remainder uses the backward scalar logarithmic norm "
                "Re[-c(2*i*omega-2*q)] rather than the absolute matrix norm"
            ),
            "validation": (
                "every proposed scalar majorant is accepted only after an "
                "arb self-map inequality passes"
            ),
        },
        "results": {
            "panel_count": len(rows),
            "common_match_radius": 32,
            "all_panels_reach_common_match_radius": True,
            "all_q_eta_xi_remainders_present_at_match": True,
            "continued_inward_after_match": True,
            "first_terminal_radius_range": [
                str(min(terminal_radii)), str(max(terminal_radii))
            ],
            "terminal_failure_kinds": sorted({
                row["first_terminal_obstruction"]["failure"] for row in rows
            }),
            "run_artifact": {
                "path": str(RUN.relative_to(ROOT)),
                "sha256": sha256(RUN),
            },
        },
        "claim_flags": {
            "affine_shared_omega_q_transport_to_r32_certified": True,
            "affine_shared_omega_eta_transport_to_r32_certified": True,
            "affine_shared_omega_xi_transport_to_r32_certified": True,
            "transport_to_r4_certified": False,
            "two_sided_Evans_boundary_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "shortfall": (
            "All panels reach r=32. Continued inward, the zero-centered q "
            "remainder grows until its Riccati self-map discriminant fails "
            "between the panel-dependent radii recorded in the run. The xi "
            "remainder is already broad at r=32 because the certified "
            "endpoint omega-sensitivity ball is broad; this is valid but not "
            "yet useful for a two-sided simple-root gate."
        ),
        "does_not_establish": [
            "transport to the intended near-horizon match point",
            "a horizon moving-phase endpoint line",
            "a nonzero two-sided Evans determinant on a contour",
            "an argument-principle root count",
            "a QNM, Smith selector or exceptional point",
        ],
    }


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-ecs-affine-projective-receipt-v1",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "input_sha256": {
            "centered_initializer": sha256(INITIALIZER),
            "ecs": sha256(ECS), "tail": sha256(TAIL),
        },
        "artifact_sha256": {
            name: sha256(HERE / name) for name in ARTIFACTS
        },
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_affine_projective_transport_v1.produce",
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_affine_projective_transport_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase3.axial_qnm_ecs_affine_projective_transport_v1.test_affine_transport",
            "python3 -m py_compile black_hole_programme/phase3/axial_qnm_ecs_affine_projective_transport_v1/*.py",
        ],
        "tier_2_not_run": (
            "No shared operator changed; this is a scoped validated transport "
            "successor over content-addressed endpoint inputs."
        ),
        "tier_3_not_run": "Not a freeze or theorem promotion.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
