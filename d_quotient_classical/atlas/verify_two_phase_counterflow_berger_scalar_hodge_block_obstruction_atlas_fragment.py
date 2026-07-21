#!/usr/bin/env python3
"""Independent semantic audit of the scalar-Hodge obstruction atlas row."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-berger-scalar-hodge-block-obstruction-fragment-v1.json"


def main() -> None:
    value = json.loads(ATLAS.read_text())
    if hashlib.sha256((ROOT / value["generated_by"]).read_bytes()).hexdigest() != value["generated_by_sha256"]:
        raise AssertionError("atlas generator drifted")
    row = value["entries"][0]
    if row["scope"]["background"] != "stationary biaxial Berger R x S3, a=1, c_squared=9/40":
        raise AssertionError("same-background scope drifted")
    if row["descriptions"]["causal"] != "OBSTRUCTED":
        raise AssertionError("nonclosed scalar causal restriction hidden")
    if row["descriptions"]["symplectic"] != "NO_CERTIFIED_MAP":
        raise AssertionError("descended scalar pairing silently promoted")
    if row["mode_data"]["dispersion"]["status"] != "OBSTRUCTED":
        raise AssertionError("first closure obstruction lost")
    if "k=0 exceptional/open" not in row["scope"]["k"]:
        raise AssertionError("exceptional right-neutral modes silently decided")
    if "not a defect of q70" not in row["claim_boundary"]:
        raise AssertionError("scoped obstruction was promoted to a parent failure")
    print("INDEPENDENT COUNTERFLOW BERGER SCALAR-HODGE OBSTRUCTION ATLAS: PASS")


if __name__ == "__main__":
    main()
