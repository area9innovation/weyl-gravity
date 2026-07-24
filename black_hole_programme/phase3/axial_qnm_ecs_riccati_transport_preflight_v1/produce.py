#!/usr/bin/env python3
"""Package the validated projective chart-enclosure obstruction."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "riccati-run.json"
ECS = ROOT / "black_hole_programme/phase3/axial_qnm_ecs_inverse_tortoise_v1/certificate.json"
TANGENT = ROOT / "black_hole_programme/phase3/axial_qnm_ecs_tangent_initializer_v1/certificate.json"
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md", "report.md", "schema.json", "riccati_preflight.py",
    "riccati-run.json", "produce.py", "verify.py",
    "test_riccati_preflight.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def produce() -> dict:
    run = json.loads(RUN.read_text())
    if not all(row["failure"] for row in run["rows"]):
        raise RuntimeError("a Riccati panel unexpectedly reached r=4")
    if not all(
        row["failure"]["projective_ball_contains_zero"]
        for row in run["rows"]
    ):
        raise RuntimeError("declared reciprocal-chart obstruction drift")
    last_radii = [row["last_certified_radius"] for row in run["rows"]]
    return {
        "schema": "phase3-axial-qnm-ecs-riccati-transport-preflight-v1",
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": (
            "VALIDATED_RICCATI_CHART_ENCLOSURE_OBSTRUCTION_FROM_COARSE_"
            "ECS_BASE_BALL_NO_PHYSICAL_POLE_INFERRED"
        ),
        "imports": {
            "ecs_base_initializer": {
                "path": str(ECS.relative_to(ROOT)), "sha256": sha256(ECS)
            },
            "ecs_tangent_initializer": {
                "path": str(TANGENT.relative_to(ROOT)),
                "sha256": sha256(TANGENT),
            },
            "riccati_run": {
                "path": str(RUN.relative_to(ROOT)), "sha256": sha256(RUN)
            },
        },
        "method": {
            "panel_count": run["panel_count"],
            "taylor_order": run["taylor_order"],
            "radial_step": run["radial_step"],
            "charts": ["q=v_x/v", "p=v/v_x"],
            "chart_switch_rule": (
                "switch only when the current acb enclosure excludes zero"
            ),
            "cauchy_tail_and_majorant_self_map": True,
        },
        "obstruction": {
            "all_panels_failed_before_r4": True,
            "last_certified_radii": last_radii,
            "failure_window": ["216/5", "867/20"],
            "all_failure_balls_contain_zero": True,
            "conclusion": (
                "The coarse norm-only ECS initializer loses projective "
                "separation after only 1.65--1.8 radial units. At failure "
                "the q enclosure contains zero, so p=1/q is not a certified "
                "chart, while the q-chart Cauchy majorant has no positive "
                "self-map discriminant. This is an enclosure obstruction, "
                "not evidence for a zero of the physical Jost solution."
            ),
        },
        "claim_flags": {
            "validated_projective_preflight_executed": True,
            "physical_projective_pole_established": False,
            "usable_r4_projective_enclosure": False,
            "tangent_sensitivity_transported_to_r4": False,
            "b_over_a_on_contour_constructed": False,
            "Evans_boundary_nonzero_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "next_gates": [
            (
                "replace the norm-only ECS base ball by a centered Picard/"
                "Neumann evaluation with a small residual correction"
            ),
            (
                "then rerun the q/p atlas and differentiate its Möbius "
                "updates using the certified intrinsic tangent initializer"
            ),
        ],
        "does_not_establish": [
            "a physical zero or pole of the scalar Jost line",
            "a usable projective enclosure at r=4",
            "transport of the tangent sensitivity to r=4",
            "b/a or Evans nonvanishing on the contour",
            "a QNM count, QNM, Smith selection or EP2",
        ],
    }


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-ecs-riccati-transport-preflight-receipt-v1",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "artifact_sha256": {name: sha256(HERE / name) for name in ARTIFACTS},
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_riccati_transport_preflight_v1.riccati_preflight",
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_riccati_transport_preflight_v1.produce",
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_riccati_transport_preflight_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase3.axial_qnm_ecs_riccati_transport_preflight_v1.test_riccati_preflight"
        ],
        "tier_2_not_run": "No shared operator changed; reduced-mode preflight only.",
        "tier_3_not_run": "Not a freeze or theorem promotion."
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
