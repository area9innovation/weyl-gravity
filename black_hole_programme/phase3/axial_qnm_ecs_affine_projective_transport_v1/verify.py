#!/usr/bin/env python3
"""Verify the affine projective transport certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
RUN = HERE / "affine-run.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    run = json.loads(RUN.read_text())
    assert certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "REDUCED-MODE"
    ]
    assert certificate["results"]["run_artifact"]["sha256"] == sha256(RUN)
    assert run["panel_count"] == 16
    assert all(row["match_radius_certified"] for row in run["rows"])
    assert all(row["match_snapshot"] is not None for row in run["rows"])
    assert all(
        row["first_terminal_obstruction"]["failure"]
        == "AFFINE_Q_REMAINDER_DISCRIMINANT"
        for row in run["rows"]
    )
    flags = certificate["claim_flags"]
    assert flags["affine_shared_omega_q_transport_to_r32_certified"]
    assert flags["affine_shared_omega_eta_transport_to_r32_certified"]
    assert flags["affine_shared_omega_xi_transport_to_r32_certified"]
    assert not flags["transport_to_r4_certified"]
    assert not flags["QNM_or_EP2_certified"]
    print("affine projective transport to r=32: PASS")


if __name__ == "__main__":
    main()
