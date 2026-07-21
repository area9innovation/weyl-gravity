#!/usr/bin/env python3
"""Independent verifier for the counterflow residual-BFV obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_RESIDUAL_BFV_RECEIVER_OBSTRUCTION_PAYLOAD_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bracket(a: int, b: int) -> dict[int, int]:
    if a == b or a >= 3 or b >= 3:
        return {}
    # e0,e1,e2 with [e0,e1]=e2 cyclically.
    if (a, b) in ((0, 1), (1, 2), (2, 0)):
        return {3 - a - b: 1}
    return {3 - a - b: -1}


def main() -> None:
    cert, payload = json.loads(CERT.read_text()), json.loads(PAYLOAD.read_text())
    for row in cert["imports"].values():
        if sha(ROOT / row["path"]) != row["sha256"]:
            raise AssertionError("import hash drift")
    defects = 0
    for a in range(5):
        for b in range(5):
            for c in range(5):
                total: dict[int, int] = {}
                for x, yz in ((a, (b, c)), (b, (c, a)), (c, (a, b))):
                    for y, cy in bracket(*yz).items():
                        for z, cz in bracket(x, y).items():
                            total[z] = total.get(z, 0) + cy * cz
                defects += int(any(total.values()))
    if defects or cert["jacobi_defects"] != 0:
        raise AssertionError("independent Jacobi replay failed")
    cross = payload["old_round_crosswalk"]
    if len(cross["preserved_subalgebra"]) != 5 or len(cross["broken_generators"]) != 10:
        raise AssertionError("15-to-5 crosswalk count failed")
    if "not an ideal" not in cross["not_a_quotient_witness"]:
        raise AssertionError("non-quotient witness missing")
    missing = payload["missing_carrier"]
    if set(missing["spatial_generators"]) != {"L1", "L2", "L3", "R3"}:
        raise AssertionError("minimal missing carrier changed")
    if payload["receiver_status"]["full_BFV_nilpotency"] != "NOT_DEFINED_MISSING_MATTER_REPRESENTATION_AND_MOMENT_MAPS":
        raise AssertionError("BFV result promoted")
    if payload["charge_and_leaf"]["D_K_identification_before_reduction"]:
        raise AssertionError("raw D/K conflation")
    print("INDEPENDENT COUNTERFLOW RESIDUAL BFV OBSTRUCTION VERIFIER: PASS")


if __name__ == "__main__":
    main()
