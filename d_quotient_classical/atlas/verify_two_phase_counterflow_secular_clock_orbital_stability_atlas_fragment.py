#!/usr/bin/env python3
"""Independent semantic checks for the counterflow orbital-stability atlas rows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-secular-clock-orbital-stability-fragment-v1.json"


def main() -> None:
    value = json.loads(ATLAS.read_text())
    if hashlib.sha256((ROOT / value["generated_by"]).read_bytes()).hexdigest() != value["generated_by_sha256"]:
        raise AssertionError("atlas generator hash drifted")
    rows = {row["id"]: row for row in value["entries"]}
    reduced = rows["classical.counterflow.unrestricted_clock.action_angle_orbital_stability"]
    coupled = rows["classical.counterflow.coupled_berger.charge_family_separator"]
    if reduced["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED":
        raise AssertionError("absolute dephasing was hidden")
    if reduced["mode_data"]["second_order"]["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("integrable family tangent was lost")
    if coupled["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("isolated coupled background was promoted")
    if reduced["scope"]["carrier"] == coupled["scope"]["carrier"]:
        raise AssertionError("distinct carriers were silently identified")
    print("INDEPENDENT COUNTERFLOW ORBITAL-STABILITY ATLAS VERIFIER: PASS")


if __name__ == "__main__":
    main()
