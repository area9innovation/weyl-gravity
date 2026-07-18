#!/usr/bin/env python3
"""Independent consumer for clock-integrated detector form coefficients."""
import json
from fractions import Fraction
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "closed_universe_observers/certificates/BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS.json"
SCHEMA = ROOT / "closed_universe_observers/schema/berger-clock-integrated-form-profile-coefficients-v1.schema.json"

def main() -> int:
    value = json.loads(CERT.read_text()); Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    assert [row["detector_id"] for row in value["detectors"]] == ["D0", "D1"]
    assert [row["power"] for row in value["odd_secant_moment_enclosures"]] == [-1, 1, 3, 5, 7, 9, 11]
    for row in value["odd_secant_moment_enclosures"]:
        enclosure = row["enclosure"]; assert Fraction(enclosure["lower"]) <= Fraction(enclosure["upper"])
    for detector in value["detectors"]:
        assert [mode["two_j"] for mode in detector["modes"]] == list(range(5))
        assert detector["modes"][0]["spatial_codifferential_coefficients"] == []
        assert any(mode["spatial_codifferential_coefficients"] for mode in detector["modes"][1:])
        for mode in detector["modes"]:
            assert len(mode["polarization_one_form_components"]) == 3
    flags = value["flags"]
    assert flags["CLOCK_ZERO_MOMENT_FORM_COEFFICIENTS_TWO_J0_TO_4_EXPORTED"] is True
    assert flags["FULL_FOUR_DIMENSIONAL_TIME_KERNEL_WEIGHTED_SOURCE_COEFFICIENTS_EVALUATED"] is False
    assert flags["ADVANCED_GREEN_IMAGES_EVALUATED"] is False
    print("clock-integrated form profile independent verification: PASS"); return 0

if __name__ == "__main__": raise SystemExit(main())
