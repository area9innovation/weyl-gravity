#!/usr/bin/env python3
"""Independent verification of the scalar-q1 background-ideal obstruction."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERT = P / "certificates/BERGER_108_ROW_Q1_PBW_BACKGROUND_IDEAL_OBSTRUCTION.json"
SCHEMA = P / "schema/berger-108-row-q1-pbw-background-ideal-obstruction-v1.schema.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_term(coefficient, multiindex):
    return {
        "coefficient": {"rational": {"numerator": coefficient, "denominator": 1}, "sqrt10": {"numerator": 0, "denominator": 1}},
        "factors": [{"kind": "background", "name": "R0_1", "vertical_multiindex": [], "spacetime_multiindex": multiindex}],
    }


def main():
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in value["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    obstruction = value["background_ideal_obstruction"]
    expected = [
        expected_term(1, [0, 1, 0, 2]),
        expected_term(1, [0, 1, 2, 0]),
        expected_term(1, [0, 3, 0, 0]),
        expected_term(-1, [2, 1, 0, 0]),
    ]
    assert obstruction["free_jet_residual_normal_form"] == expected
    assert obstruction["separating_evaluation"]["value"] == "1"
    assert value["available_scalar_data"]["global_rod_wave_residuals"] == ["0"] * 6
    missing = value["missing_object_ledger"]
    assert set(missing["component_contract_background_specializations"]) == {"detector_profiles", "emitter_switches"}
    assert not missing["rod_background_specialization_exported"]
    assert not missing["background_equation_differential_ideal_exported"]
    assert all(row["detected"] for row in value["mutations"])
    assert not value["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
    print("BERGER_108_ROW_Q1_PBW_BACKGROUND_IDEAL_OBSTRUCTION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
