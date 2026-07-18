#!/usr/bin/env python3
"""Independent fail-closed checks for the relative branch dictionary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_relative_branch_dictionary.schema.json"


def main() -> None:
    value = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    for name, record in value["provenance"]["inputs"].items():
        path = ROOT / record["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != record["sha256"]:
            raise AssertionError(f"stale branch input: {name}")
    rows = {row["id"]: row for row in value["branch_rows"]}
    if rows["ph.generic.axial.relative"]["map_lifecycle"] != "DERIVED_COFIBER_TRIANGLE":
        raise AssertionError("axial derived-cofiber lifecycle changed")
    if rows["ph.generic.polar.relative"]["map_lifecycle"] != "DERIVED_COFIBER_TRIANGLE":
        raise AssertionError("polar derived-cofiber lifecycle changed")
    if not any(
        "cyclic BV compatibility" in item
        for item in rows["ph.generic.polar.relative"]["missing"]
    ):
        raise AssertionError("polar cyclic boundary was hidden")
    if rows["ph.exceptional.ell1.relative"]["projection_or_cofiber"]["status"] != "CERTIFIED":
        raise AssertionError("exceptional k0 solution cofiber was lost")
    if rows["ph.global.homogeneous.relative"]["projection_or_cofiber"]["status"] != "CERTIFIED":
        raise AssertionError("zero homogeneous solution cofiber was lost")
    for identifier in ("ph.exceptional.ell1.nonzero_k.relative", "ph.global.twist.relative"):
        if rows[identifier]["projection_or_cofiber"]["status"] != "NO_CERTIFIED_MAP":
            raise AssertionError(f"missing cofiber was hidden: {identifier}")
    boundary = rows["ph.boundary.relative"]
    if boundary["map_lifecycle"] != "NO_CERTIFIED_MAP" or boundary["evidence"]:
        raise AssertionError("cross-background row acquired an implicit map")
    flags = value["classification"]
    if flags["full_offshell_all_sector_triangle_certified"] or flags["bridge_1_activation_gate_satisfied"]:
        raise AssertionError("bridge 1 was over-promoted")
    if flags["cross_background_mode_identification_made"]:
        raise AssertionError("a forbidden cross-background identification appeared")
    print("EINSTEIN_WEYL_RELATIVE_BRANCH_DICTIONARY_V1 independent verification: PASS")


if __name__ == "__main__":
    main()
