#!/usr/bin/env python3
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_haar_profile_normalization_repair import CERTIFICATE, SCHEMA, build


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value == build()
    assert value["jacobian_audit"]["normalized_gram_jacobian_J"] == "a**3*x0"
    assert value["jacobian_audit"]["clock_center_values"]["J"] == "1"
    audit = value["corrected_tail_audit"]
    assert Fraction(audit["total_fourier_energy_lower"]) > 70_000_000
    assert Fraction(audit["omitted_energy_fraction_lower"]) > Fraction(99999, 100000)
    assert value["corrected_necessary_capacity"]["certified_necessary_two_j_max"] == 97
    assert value["flags"]["HISTORICAL_TWO_J138_WORKING_RAIL_REMAINS_VALID"] is True
    assert value["flags"]["HISTORICAL_TWO_J138_NECESSITY_LABEL_SUPERSEDED"] is True
    assert value["flags"]["STREAMED_COEFFICIENT_VALUES_CHANGED"] is False
    assert value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("Berger Haar profile-normalization repair verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
