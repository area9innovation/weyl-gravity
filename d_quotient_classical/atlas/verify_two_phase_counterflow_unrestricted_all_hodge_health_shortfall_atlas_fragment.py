#!/usr/bin/env python3
"""Independent semantic check of the counterflow all-Hodge shortfall atlas row."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-unrestricted-all-hodge-health-shortfall-fragment-v1.json"


def main() -> None:
    value = json.loads(ATLAS.read_text())
    if hashlib.sha256((ROOT / value["generated_by"]).read_bytes()).hexdigest() != value["generated_by_sha256"]:
        raise AssertionError("atlas generator drift")
    row = value["entries"][0]
    if row["scope"]["background"] != "stationary biaxial Berger R x S3, a=1, c_squared=9/40":
        raise AssertionError("background scope drift")
    if row["descriptions"]["causal"] != "CERTIFIED":
        raise AssertionError("imported unary causal status lost")
    if row["descriptions"]["symplectic"] != "NO_CERTIFIED_MAP":
        raise AssertionError("physical pairing silently promoted")
    if row["mode_data"]["dispersion"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("missing harmonic restriction hidden")
    if row["scope"]["ell"] != "NO_CERTIFIED_MAP":
        raise AssertionError("unexported mode label invented")
    print("INDEPENDENT COUNTERFLOW ALL-HODGE SHORTFALL ATLAS VERIFIER: PASS")


if __name__ == "__main__":
    main()
