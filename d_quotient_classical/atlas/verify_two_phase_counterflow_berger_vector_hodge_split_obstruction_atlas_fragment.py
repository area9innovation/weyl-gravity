#!/usr/bin/env python3
"""Independent semantic verifier for the vector Hodge obstruction atlas row."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-berger-vector-hodge-split-obstruction-fragment-v1.json"


def main() -> None:
    value = json.loads(ATLAS.read_text())
    if value["status_vocabulary"] != ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]:
        raise AssertionError("atlas vocabulary drifted")
    entry = value["entries"][0]
    if entry["descriptions"]["causal"] != "OBSTRUCTED":
        raise AssertionError("nonclosed restriction was promoted")
    if any(entry["descriptions"][axis] != "NO_CERTIFIED_MAP" for axis in ("symplectic", "nonlinear", "observational", "quantum")):
        raise AssertionError("downstream atlas axis was promoted")
    if "full q70 parent" not in entry["claim_boundary"]:
        raise AssertionError("parent-preservation boundary missing")
    print("INDEPENDENT COUNTERFLOW BERGER VECTOR-HODGE OBSTRUCTION ATLAS: PASS")


if __name__ == "__main__":
    main()
