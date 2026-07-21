#!/usr/bin/env python3
"""Independent fail-closed checks for the counterflow component atlas fragment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-background-component-round-fragment-v1.json"
ALLOWED = {"CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"}
SCOPE = {"theory", "background", "boundaries", "charge_sector", "carrier", "degree", "parity", "ell", "m", "k", "omega"}


def verify() -> None:
    atlas = json.loads(ATLAS.read_text())
    generator = ROOT / atlas["generated_by"]
    if hashlib.sha256(generator.read_bytes()).hexdigest() != atlas["generated_by_sha256"]:
        raise AssertionError("atlas generator hash mismatch")
    entries = {entry["id"]: entry for entry in atlas["entries"]}
    expected = {"classical.two_phase_counterflow_component.selected_berger", "classical.two_phase_counterflow_component.same_action_round"}
    if set(entries) != expected:
        raise AssertionError("atlas entry set drifted")
    for entry in entries.values():
        if set(entry["scope"]) != SCOPE:
            raise AssertionError("atlas mode scope is incomplete")
        if set(entry["descriptions"].values()) - ALLOWED:
            raise AssertionError("description is not fail-closed")
        for key in ("dispersion", "lee_wald", "taub_maps", "resonance"):
            if entry["mode_data"][key]["status"] not in ALLOWED:
                raise AssertionError("mode claim is not fail-closed")
        for evidence in entry["evidence"]:
            path = ROOT / evidence["path"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != evidence["sha256"]:
                raise AssertionError("evidence hash mismatch")
    selected = entries["classical.two_phase_counterflow_component.selected_berger"]
    round_entry = entries["classical.two_phase_counterflow_component.same_action_round"]
    if selected["descriptions"]["causal"] != "CERTIFIED" or selected["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("selected point boundary was lost")
    if round_entry["mode_data"]["dispersion"]["status"] != "OBSTRUCTED" or round_entry["descriptions"]["causal"] != "NO_CERTIFIED_MAP":
        raise AssertionError("round noninheritance was promoted")
    print("INDEPENDENT COUNTERFLOW COMPONENT ATLAS VERIFIER: PASS")


if __name__ == "__main__":
    verify()
