#!/usr/bin/env python3
"""Package the validated panelwise transport width shortfall."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "panel-run.json"
ECS = ROOT / "black_hole_programme/phase3/axial_qnm_ecs_inverse_tortoise_v1/certificate.json"
TANGENT = ROOT / "black_hole_programme/phase3/axial_qnm_ecs_tangent_initializer_v1/certificate.json"
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
ARTIFACTS = (
    "README.md", "report.md", "schema.json", "panel_preflight.py",
    "panel-run.json", "produce.py", "verify.py", "test_panel_preflight.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def produce() -> dict:
    run = json.loads(RUN.read_text())
    # The run stores outward-rounded lower bounds for every rectangular
    # component radius. Parse their decimal display only for the explicit
    # fail-closed threshold; the verifier reruns the acb calculation.
    all_wide = all(
        all(float(value.split()[0].strip("[]")) > 1 for value in row["component_radius_lower"])
        for row in run["rows"]
    )
    if not all_wide:
        raise RuntimeError("panel preflight no longer witnesses width loss")
    return {
        "schema": "phase3-axial-qnm-ecs-panel-transport-preflight-v1",
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "VALIDATED_ACB_PANEL_TAYLOR_WIDTH_SHORTFALL_NO_EVANS_BOUNDARY",
        "imports": {
            "ecs_base_initializer": {"path": str(ECS.relative_to(ROOT)), "sha256": sha256(ECS)},
            "ecs_tangent_initializer": {"path": str(TANGENT.relative_to(ROOT)), "sha256": sha256(TANGENT)},
            "panel_run": {"path": str(RUN.relative_to(ROOT)), "sha256": sha256(RUN)},
        },
        "method": {
            "frequency_panels": run["panel_count"],
            "taylor_order": run["taylor_order"],
            "radial_step": run["radial_step"],
            "arithmetic": run["arithmetic"],
            "cauchy_tail_per_step": True,
            "centered_after_each_step": True,
            "lohner_affine_reconditioning": False,
        },
        "result": {
            "all_panel_component_radii_exceed_one": True,
            "representative_first_panel_radius_lower": run["rows"][0]["component_radius_lower"],
            "conclusion": (
                "Even after 16 frequency panels, order-16 Taylor steps and "
                "per-step recentering, rectangular dependency wrapping grows "
                "to at least order 10^16 by r=4. The rail cannot enclose an "
                "Evans boundary. Affine Lohner/Taylor-model correlation or a "
                "Riccati/Grassmannian representation is required."
            ),
        },
        "claim_flags": {
            "panelwise_acb_transport_executed": True,
            "cauchy_step_tails_enclosed": True,
            "evans_usable_outgoing_column": False,
            "b_over_a_on_contour_constructed": False,
            "Evans_boundary_nonzero_certified": False,
            "QNM_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "does_not_establish": [
            "an Evans-usable outgoing column",
            "the factor-frame b/a boundary function",
            "Evans-boundary nonvanishing",
            "a QNM root count",
            "a QNM, Smith selection or EP2",
        ],
    }


def main() -> None:
    document = produce()
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-qnm-ecs-panel-transport-preflight-receipt-v1",
        "certificate": OUTPUT.name,
        "certificate_sha256": sha256(OUTPUT),
        "artifact_sha256": {name: sha256(HERE / name) for name in ARTIFACTS},
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_panel_transport_preflight_v1.panel_preflight",
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_panel_transport_preflight_v1.produce",
            "python3 -m black_hole_programme.phase3.axial_qnm_ecs_panel_transport_preflight_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase3.axial_qnm_ecs_panel_transport_preflight_v1.test_panel_preflight"
        ],
        "tier_2_not_run": "No shared operator changed; this is a reduced-mode numerical preflight.",
        "tier_3_not_run": "Not a freeze or theorem promotion."
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
