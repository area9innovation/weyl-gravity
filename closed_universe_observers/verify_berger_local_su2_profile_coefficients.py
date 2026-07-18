#!/usr/bin/env python3
"""Verify the local SU(2) profile-coefficient enclosure certificate."""

import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_local_su2_profile_coefficients import (
    CERTIFICATE,
    DEPENDENCIES,
    MAX_TWO_J,
    SCHEMA,
    _sha256,
    generator_defect_count,
    mode_audit,
    radial_moment_intervals,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    for name, path in DEPENDENCIES.items():
        assert value["dependency_refs"][name]["sha256"] == _sha256(path)
    moments = radial_moment_intervals(dependencies["moments"])
    expected = [mode_audit(two_j, moments) for two_j in range(MAX_TWO_J + 1)]
    assert value["audited_mode_coefficients"] == expected
    assert all(mode["generator_convention_defect_count"] == 0 for mode in expected)
    assert all(mode["off_diagonal_nonzero_enclosure_count"] == 0 for mode in expected)
    assert generator_defect_count(1, flip_y1_sign=True) == value["mutation_results"][0]["generator_defect_count"] > 0
    for mode in expected:
        for row in mode["diagonal"]:
            interval = row["local_fourier_amplitude"]
            assert Fraction(interval["lower"]) <= Fraction(interval["upper"])
    print("BERGER_LOCAL_SU2_PROFILE_COEFFICIENT_ENCLOSURES verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
