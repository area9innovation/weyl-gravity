#!/usr/bin/env python3
"""Verify the clock-integrated scalar coefficient certificate."""

import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_clock_integrated_scalar_coefficients import (
    CERTIFICATE,
    DEPENDENCIES,
    MAX_MOMENT_K,
    MAX_TWO_J,
    SCHEMA,
    _sha256,
    clock_secant_moments,
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
    clock = clock_secant_moments()
    expected_clock = [
        {"k": k, "expectation_secant_power_2k": {"lower": str(clock[k][0]), "upper": str(clock[k][1]), "width": str(clock[k][1] - clock[k][0])}}
        for k in range(MAX_MOMENT_K + 1)
    ]
    assert value["clock_secant_moment_enclosures"] == expected_clock
    radial = radial_moment_intervals(dependencies["moments"])
    expected_modes = [mode_audit(two_j, radial, clock) for two_j in range(MAX_TWO_J + 1)]
    assert value["audited_clock_integrated_coefficients"] == expected_modes
    assert all(mode["off_diagonal_nonzero_enclosure_count"] == 0 for mode in expected_modes)
    assert clock[0] == (1, 1)
    assert all(clock[k][0] > 1 for k in range(1, MAX_MOMENT_K + 1))
    for mode in expected_modes:
        for row in mode["diagonal"]:
            interval = row["clock_integrated_local_amplitude"]
            assert Fraction(interval["lower"]) <= Fraction(interval["upper"])
    print("BERGER_CLOCK_INTEGRATED_SCALAR_PROFILE_COEFFICIENTS verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
