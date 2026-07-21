#!/usr/bin/env python3
"""Independent atlas boundary check for the fixed-charge obstruction."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-fixed-charge-reduced-health-fragment-v1.json"


def verify() -> None:
    atlas = json.loads(ATLAS.read_text())
    if hashlib.sha256((ROOT / atlas["generated_by"]).read_bytes()).hexdigest() != atlas["generated_by_sha256"]:
        raise AssertionError("generator drift")
    entry = atlas["entries"][0]
    evidence = entry["evidence"][0]
    if hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest() != evidence["sha256"]:
        raise AssertionError("evidence drift")
    if entry["descriptions"]["causal"] != "CERTIFIED" or entry["descriptions"]["symplectic"] != "OBSTRUCTED":
        raise AssertionError("parent/reduction distinction lost")
    if entry["mode_data"]["lee_wald"]["status"] != "OBSTRUCTED":
        raise AssertionError("clock quotient promoted")
    print("INDEPENDENT FIXED-CHARGE REDUCED-HEALTH ATLAS VERIFIER: PASS")


if __name__ == "__main__":
    verify()
