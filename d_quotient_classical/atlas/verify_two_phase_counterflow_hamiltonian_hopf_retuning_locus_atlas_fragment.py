#!/usr/bin/env python3
"""Independent atlas consumer for the counterflow retuning no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-hamiltonian-hopf-retuning-locus-fragment-v1.json"
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    atlas = json.loads(ATLAS.read_text())
    source = json.loads(SOURCE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    if atlas["status_vocabulary"] != ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]:
        raise AssertionError("atlas status vocabulary drifted")
    if len(atlas["entries"]) != 1:
        raise AssertionError("atlas entry count drifted")
    entry = atlas["entries"][0]
    if entry["descriptions"]["causal"] != "NO_CERTIFIED_MAP" or entry["descriptions"]["quantum"] != "NO_CERTIFIED_MAP":
        raise AssertionError("familywide causal/quantum status was overpromoted")
    if entry["mode_data"]["dispersion"]["status"] != "OBSTRUCTED" or entry["mode_data"]["lee_wald"]["status"] != "CERTIFIED":
        raise AssertionError("physical status drifted")
    if source["terminal_verdict"]["entire_component_Hamiltonian_Hopf"] is not True:
        raise AssertionError("source no-go drifted")
    if payload["charge_and_causal_gates"]["familywide_full_Green_homotopy"] != "NO_CERTIFIED_MAP":
        raise AssertionError("source causal boundary drifted")
    evidence = {record["result_id"]: record for record in entry["evidence"]}
    for path, value in ((SOURCE, source), (PAYLOAD, payload)):
        record = evidence[value["result_id"]]
        if record["sha256"] != _sha(path):
            raise AssertionError("atlas evidence digest drifted")
    print("TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_ATLAS_INDEPENDENT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
