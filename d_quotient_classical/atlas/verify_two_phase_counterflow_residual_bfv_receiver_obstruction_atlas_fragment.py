#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-residual-bfv-receiver-obstruction-fragment-v1.json"


def main():
    atlas = json.loads(ATLAS.read_text()); entry = atlas["entries"][0]
    if hashlib.sha256((ROOT / atlas["generated_by"]).read_bytes()).hexdigest() != atlas["generated_by_sha256"]: raise AssertionError("generator drift")
    evidence = entry["evidence"][0]
    if hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest() != evidence["sha256"]: raise AssertionError("source drift")
    if entry["descriptions"]["causal"] != "CERTIFIED" or entry["descriptions"]["symplectic"] != "NO_CERTIFIED_MAP": raise AssertionError("boundary promoted")
    if entry["mode_data"]["taub_maps"]["status"] != "NO_CERTIFIED_MAP": raise AssertionError("Taub map promoted")
    print("INDEPENDENT COUNTERFLOW RESIDUAL BFV ATLAS VERIFIER: PASS")


if __name__ == "__main__": main()
