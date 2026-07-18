#!/usr/bin/env python3
"""Verify the validated flat-bump moment enclosure certificate."""

import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_validated_flat_bump_moments import (
    CERTIFICATE,
    DEPENDENCIES,
    SCHEMA,
    _sha256,
    endpoint_only_peak_mutation,
    integral_enclosures,
    normalized_moments,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, path in DEPENDENCIES.items():
        assert value["dependency_refs"][name]["sha256"] == _sha256(path)
    integrals = integral_enclosures()
    expected_raw = [
        {"power": p, "integral": {"lower": str(lo), "upper": str(hi), "width": str(hi - lo)}}
        for p, (lo, hi) in sorted(integrals.items())
    ]
    assert value["raw_radial_integral_enclosures"] == expected_raw
    assert value["normalized_moments"]["clock_core_dimension_1"] == normalized_moments(integrals, 1)
    assert value["normalized_moments"]["radial_core_dimension_3"] == normalized_moments(integrals, 3)
    for family in value["normalized_moments"].values():
        assert all(Fraction(row["normalized_even_moment"]["width"]) < Fraction(1, 1000) for row in family)
    assert endpoint_only_peak_mutation()["detected"]
    print("BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
