#!/usr/bin/env python3
"""Independent structural verifier for the transverse formal Green variation."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-formal-metric-green-variation-v1.schema.json"


def main() -> None:
    payload = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    expected_defects = {
        "base_Q_squared",
        "linearized_Q_squared",
        "base_left_inverse",
        "base_right_inverse",
        "varied_left_inverse",
        "varied_right_inverse",
        "base_chain_commutation",
        "varied_chain_commutation",
        "base_homotopy",
        "varied_homotopy",
    }
    defects = payload["finite_fixture"]["identity_defects"]
    if set(defects) != expected_defects or any(defects.values()):
        raise AssertionError("finite differentiated algebra is incomplete or nonzero")
    if payload["tangent_family"]["first_integral_defect_through_epsilon2"] != 0:
        raise AssertionError("Einstein first-integral expansion failed")
    if payload["tangent_family"]["evolution_defect_through_epsilon2"] != 0:
        raise AssertionError("Einstein evolution expansion failed")
    if "-G0_+/- pdot G0_+/-" not in payload["formal_green_theorem"]["green_variation"]:
        raise AssertionError("Duhamel formula drifted")
    audit = payload["rank310_globalization_audit"]
    if audit["maximum_curvature_jet_order"] != 5:
        raise AssertionError("rank-310 jet scope drifted")
    if audit["global_smooth_coefficient_export_present"] is not False:
        raise AssertionError("global coefficient data were overclaimed")
    if payload["flags"]["TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION"] is not True:
        raise AssertionError("formal metric result was not promoted")
    for flag in (
        "TRANSVERSE_GLOBAL_RANK310_SDR_VARIATION",
        "TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION",
        "TRANSVERSE_CAUSAL_TRANSFER",
    ):
        if payload["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")
    print("NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1: independently verified")


if __name__ == "__main__":
    main()
