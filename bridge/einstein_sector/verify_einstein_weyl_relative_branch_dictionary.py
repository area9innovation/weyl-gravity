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
    for identifier in ("ph.generic.axial.relative", "ph.generic.polar.relative"):
        if rows[identifier]["action_derived_pairing"].get("fixed_identity_cyclic_compatibility") != "OBSTRUCTED by a nonradical solution-pairing defect":
            raise AssertionError(f"fixed-identity cyclic obstruction was hidden: {identifier}")
    if rows["ph.exceptional.ell1.relative"]["projection_or_cofiber"]["status"] != "CERTIFIED":
        raise AssertionError("exceptional k0 solution cofiber was lost")
    if rows["ph.global.homogeneous.relative"]["projection_or_cofiber"]["status"] != "CERTIFIED":
        raise AssertionError("zero homogeneous solution cofiber was lost")
    if rows["ph.global.twist.relative"]["projection_or_cofiber"]["status"] != "CERTIFIED":
        raise AssertionError("zero twist solution cofiber was lost")
    if not value["classification"]["complete_homogeneous_twist_bounded_resonance_matrix_imported"]:
        raise AssertionError("complete homogeneous/twist resonance handoff was lost")
    if not value["classification"]["aligned_nonzero_stabilizer_resonance_common_zero_face_imported"]:
        raise AssertionError("aligned common-zero handoff was lost")
    if not value["classification"]["complete_declared_global_extra_common_zero_locus_imported"]:
        raise AssertionError("complete global--extra common-zero handoff was lost")
    if not value["classification"]["complete_global_extra_bounded_correction_obstruction_imported"]:
        raise AssertionError("global--extra bounded obstruction handoff was lost")
    if not value["classification"]["complete_global_extra_smooth_secular_extension_imported"]:
        raise AssertionError("global--extra smooth extension handoff was lost")
    if not value["classification"]["aligned_twist_extra_L1_L3_coefficient_correction_imported"]:
        raise AssertionError("aligned twist--extra coefficient correction handoff was lost")
    for identifier in ("ph.exceptional.ell1.nonzero_k.relative",):
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
