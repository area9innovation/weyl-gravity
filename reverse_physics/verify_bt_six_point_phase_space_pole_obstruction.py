#!/usr/bin/env python3
"""Independent checks for the BT six-point physical pole obstruction."""
import json
import os
import sys

import sympy as sp
from jsonschema import Draft202012Validator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from bt_six_point_phase_space_pole_obstruction import CERT, SCHEMA, exact_pole, sha256


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def verify(certificate):
    schema = load(os.path.join(ROOT, SCHEMA))
    pole = exact_pole()
    rows = pole["channel_values"]
    interpretation = certificate["interpretation"]
    checks = {
        "schema_validation": not list(Draft202012Validator(schema).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == sha256(row["path"]) for row in certificate["provenance"]["inputs"]),
        "exact_pole_payload_replays": pole == certificate["exact_transverse_physical_pole"],
        "one_and_only_one_channel_is_zero": [row["mask"] for row in rows if row["value"] == "0"] == [11],
        "remaining_nine_channels_are_nonzero": sum(row["value"] != "0" for row in rows) == 9,
        "transverse_derivative_is_nonzero": sp.Rational(pole["transverse_derivative"]) != 0,
        "rank_and_minor_make_the_point_physical_regular": pole["chart_rank"] == 5 and sp.Rational(pole["nonzero_minor_determinant"]) != 0,
        "positive_double_pole_coefficient": sp.Rational(pole["density_leading_coefficient_in_t_minus_3_over_5"]) > 0,
        "ordinary_integral_is_fail_closed": interpretation["ordinary_exclusive_tree_phase_space_integral"] == "DIVERGES_LOCALLY",
        "no_principal_value_promotion": interpretation["principal_value_of_positive_double_pole"] == "DOES_NOT_CURE_DIVERGENCE",
        "regulated_probability_remains_open": interpretation["regulated_or_inclusive_probability"] == "NOT_COMPUTED",
        "eq19_and_gravity_remain_open": interpretation["Eq19_all_orders"] == "NOT_PROVED" and interpretation["metric_BV_BRST_lift"] == "NOT_CONSTRUCTED",
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
