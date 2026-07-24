#!/usr/bin/env python3
"""Verify the centered phase-factored projective initializer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .centered_initializer import ECS, RUN, TAIL, TANGENT

HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    run = json.loads(RUN.read_text())
    assert certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "REDUCED-MODE"
    ]
    assert certificate["imports"]["ecs"]["sha256"] == sha256(ECS)
    assert certificate["imports"]["tail"]["sha256"] == sha256(TAIL)
    assert certificate["imports"]["tangent"]["sha256"] == sha256(TANGENT)
    assert certificate["panel_results"]["run_artifact"]["sha256"] == sha256(RUN)
    assert run["panel_count"] == 16
    assert all(
        row["base"]["value_ball_excludes_zero"] for row in run["rows"]
    )
    assert all(
        row["first_projective_segment"]["certified"]
        for row in run["rows"]
    )
    flags = certificate["claim_flags"]
    assert flags["phase_factored_centered_base_initializer_certified"]
    assert flags["centered_tau_projective_initializer_certified"]
    assert flags["centered_omega_projective_initializer_certified"]
    assert flags["first_inward_projective_segment_certified"]
    assert not flags["full_inward_projective_transport_certified"]
    assert not flags["QNM_or_EP2_certified"]
    print("centered phase-factored projective initializer: PASS")


if __name__ == "__main__":
    main()
