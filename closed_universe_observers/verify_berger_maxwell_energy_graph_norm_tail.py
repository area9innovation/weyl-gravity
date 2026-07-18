#!/usr/bin/env python3
"""Verify the generated Berger Maxwell energy-tail certificate."""

import json

from closed_universe_observers.generate_berger_maxwell_energy_graph_norm_tail import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    calculation = value["calculation"]
    assert calculation["first_sufficient_component_sum_graph_tail_retained_max_two_j"] == 68743
    assert all(
        float(row["component_sum_graph_tail_upper_after_two_j1024_decimal"]) > 300_000
        for row in calculation["polarization_bounds"]
    )
    assert value["route_disposition"]["dense_complete_projection_to_graph_subunit_cutoff"] == "NOT_SELECTED"
    assert value["flags"]["MASSIVE_FINITE_TIME_ENERGY_CONSTANT_EXPORTED"] is False
    print("Berger Maxwell energy graph-norm tail verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
