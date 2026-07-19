#!/usr/bin/env python3
"""Independent verifier for the 108-row PBW input obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_108_ROW_PBW_INPUT_OBSTRUCTION.json"
SCHEMA = PACKAGE / "schema/berger-108-row-pbw-input-obstruction-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    for ref in value["dependency_refs"].values():
        path = ROOT / ref["path"]
        if _sha256(path) != ref["sha256"]:
            raise AssertionError(f"dependency hash drift: {ref['path']}")

    base_ref = value["dependency_refs"]["base_q2_payload"]
    base_payload = json.loads((ROOT / base_ref["path"]).read_text())
    if base_payload["shape"] != [64, 64, 64] or base_payload["coefficient_field"] != "Q(sqrt(10))":
        raise AssertionError("pinned base payload contract drifted")

    # Independent exact scaling derivation: a normalized d-dimensional bump
    # rescales at its centre as width^-d.  Detector dimension is three and
    # switch dimension is one.
    detector_ratio = (Fraction(1, 1) / Fraction(1, 2)) ** 3
    switch_ratio = Fraction(1, 1) / Fraction(1, 2)
    witnesses = value["nonuniqueness_witnesses"]
    if witnesses["detector_profile"]["normalized_centre_value_ratio_B_over_A"] != str(detector_ratio):
        raise AssertionError("detector-profile non-uniqueness ratio drifted")
    if witnesses["emitter_switch"]["unit_integral_centre_value_ratio_B_over_A"] != str(switch_ratio):
        raise AssertionError("emitter-switch non-uniqueness ratio drifted")

    apparatus = json.loads((ROOT / value["dependency_refs"]["apparatus_q2_q3"]["path"]).read_text())
    action_jets = apparatus["apparatus_action_jets"]
    if "rows" in action_jets or "terms" in action_jets:
        raise AssertionError("apparatus dependency unexpectedly gained a component payload")
    unary = json.loads((ROOT / value["dependency_refs"]["emitter_unary"]["path"]).read_text())
    blocks = unary["q1_new_blocks"]["new_nonzero_operator_blocks"]
    if len(blocks) != value["pinned_base_and_interface_audit"]["emitter_unary_extension"]["new_nonzero_block_count"]:
        raise AssertionError("emitter unary block count drifted")
    if any("terms" in block or "component_matrix" in block for block in blocks):
        raise AssertionError("emitter unary dependency unexpectedly gained scalar PBW matrices")

    flags = value["flags"]
    if flags["SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED"] is not False:
        raise AssertionError("PBW payload overclaimed")
    if flags["COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED"] is not False:
        raise AssertionError("component replay overclaimed")
    if value["atlas_status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("atlas disposition is not fail-closed")
    if not all(row["detected"] for row in value["mutation_results"]):
        raise AssertionError("mutation rail failed")
    print("BERGER_108_ROW_PBW_INPUT_OBSTRUCTION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
