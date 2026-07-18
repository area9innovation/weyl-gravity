#!/usr/bin/env python3
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_selected_charge_block_correlated_clock_transform import CERTIFICATE, SCHEMA, build


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value == build()
    assert len(value["spectral_transform_audits"]) == 9
    assert len(value["selected_block_outputs"]) == 18
    assert value["coverage"]["exact_eigenvalue_transform_count"] == 27
    assert Fraction(value["coverage"]["maximum_clock_transform_width"]) < Fraction(1, 250)
    assert Fraction(value["coverage"]["maximum_selected_spatial_output_axis_width"]) < Fraction(1, 50)
    assert Fraction(value["coverage"]["maximum_selected_temporal_output_axis_width"]) < Fraction(6, 5)
    assert value["lower_band_overlap"]["two_j138_direct_transform_contained_in_order14_interval"] is True
    assert value["flags"]["TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED"] is True
    assert value["flags"]["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("selected charge-block correlated clock transform verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
