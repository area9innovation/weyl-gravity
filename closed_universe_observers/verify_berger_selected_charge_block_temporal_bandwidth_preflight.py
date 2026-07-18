#!/usr/bin/env python3
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_selected_charge_block_temporal_bandwidth_preflight import (
    CERTIFICATE,
    SCHEMA,
    build,
)


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value == build()
    assert len(value["charge_audits"]) == 9
    assert len(value["actual_completed_input_order14_interval_audits"]) == 18
    assert all(Fraction(row["order14_exact_cosine_error_absolute_lower"]) > 0 for row in value["charge_audits"])
    assert all(row["width_below_one_tenth"] is False for row in value["actual_completed_input_order14_interval_audits"])
    assert value["coverage"]["maximum_required_geometric_order_for_1e_minus_17"] == 39
    assert value["coverage"]["maximum_required_even_clock_power"] == 78
    assert value["flags"]["TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("selected charge-block temporal bandwidth preflight verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
