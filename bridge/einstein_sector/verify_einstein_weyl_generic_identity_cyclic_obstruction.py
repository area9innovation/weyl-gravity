#!/usr/bin/env python3
"""Independent verifier for the fixed-identity generic cyclic obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_generic_identity_cyclic_obstruction.schema.json"


def main() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    for record in value["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise AssertionError(f"stale cyclic-obstruction input: {path}")
    eigenvalue = sp.symbols("lambda", positive=True)
    masters = {
        "axial": sp.Matrix([[eigenvalue, 2], [eigenvalue, eigenvalue]]),
        "polar": sp.Matrix([[eigenvalue, -2 * eigenvalue], [-1, eigenvalue]]),
    }
    for parity, master in masters.items():
        defect = sp.Rational(3, 2) * (master - eigenvalue * sp.eye(2))
        if defect.det() != -sp.Rational(9, 2) * eigenvalue:
            raise AssertionError(f"{parity} defect lost nondegeneracy")
        stored = value["cyclic_obstruction_theorem"]["parity_blocks"][parity]
        if stored["determinant_D"] != "-9*lambda/2" or stored["rank_for_physical_lambda"] != 2:
            raise AssertionError(f"{parity} stored defect changed")
    flags = value["classification"]
    if flags["fixed_identity_cyclic_pairing_compatibility"] != "OBSTRUCTED":
        raise AssertionError("cyclic obstruction was weakened")
    if flags["corrected_nonidentity_or_chain_homotopy_cyclic_morphism_classified"]:
        raise AssertionError("corrected cyclic problem was over-promoted")
    print("EINSTEIN_WEYL_GENERIC_IDENTITY_CYCLIC_OBSTRUCTION_V1 independent verification: PASS")


if __name__ == "__main__":
    main()
