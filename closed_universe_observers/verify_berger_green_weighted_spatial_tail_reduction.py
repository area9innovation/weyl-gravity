#!/usr/bin/env python3
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_green_weighted_spatial_tail_reduction import CERTIFICATE, SCHEMA, build


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value == build()
    theorem = value["spectral_lower_bound_theorem"]
    assert theorem["exact_formula_audit"]["diagonal_shift_defect_count"] == 0
    assert theorem["exact_formula_audit"]["single_coupling_bound_defect_count"] == 0
    assert theorem["exact_formula_audit"]["maximum_row_degree_defect_count"] == 0
    selected = next(row for row in value["cutoff_reductions"] if row["retained_max_two_j"] == 1024)
    assert Fraction(selected["delta1_spectral_lower_bound"]) > 262000
    assert value["maxwell_green_weighting"]["additional_tail_amplification_factor"] == "1"
    assert value["flags"]["GREEN_WEIGHTED_MAXWELL_TAIL_CONVERSION_EXPORTED"] is True
    assert value["flags"]["EVALUATED_PROFILE_SOBOLEV_NORM_EXPORTED"] is False
    assert value["flags"]["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("Green-weighted spatial-tail reduction verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
