#!/usr/bin/env python3
"""Independent verifier for the projected 316-row q2 obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_BLOCK_DIAGONAL_Q2_OBSTRUCTION_V1.json"


def verify() -> dict[str, object]:
    value = json.loads(CERT.read_text())
    for artifact in value["dependencies"].values():
        path = ROOT / artifact["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise AssertionError(f"dependency hash drift: {path}")
    direct = json.loads((ROOT / value["dependencies"]["direct_f2_obstruction"]["path"]).read_text())
    witness = direct["taub_pairing"]["relative_half_delta2_pairing"]
    if witness != value["projection_argument"]["normalized_nonzero_witness"]:
        raise AssertionError("projected witness mismatch")
    if value["classification"]["complete_full_domain_q2_on_block_diagonal_316_exists"]:
        raise AssertionError("blocked q2 was promoted")
    for key in ("derived_taub_zero_homotopy_pullback_obstructed", "nonzero_typed_unary_cross_incidence_obstructed", "modified_endpoint_or_background_obstructed"):
        if value["classification"][key]:
            raise AssertionError(f"successor was over-obstructed: {key}")
    return {"status": "PASS", "witness": witness, "admissible_successors": len(value["admissible_successors"])}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
