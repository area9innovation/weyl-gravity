#!/usr/bin/env python3
"""Verify the exact finite Berger mode-kernel payload."""

import json

from closed_universe_observers.generate_berger_recoil_exact_mode_kernel_payload import CERTIFICATE, build


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert len(value["blocks"]) == 25
    massive_scalar_shells = {
        block["two_j"]
        for block in value["blocks"]
        if block["family"] == "massive_two_form" and block["form_degree"] == 0
    }
    assert massive_scalar_shells == set(range(5))
    assert all(block["recurrence_defect_count_through_order4"] == 0 for block in value["blocks"])
    assert value["flags"]["EXACT_SINE_KERNEL_SERIES_COEFFICIENTS_EXPORTED"] is True
    assert value["flags"]["MASSIVE_ONE_FORM_CORRECTION_BLOCKS_EXPORTED"] is True
    assert value["flags"]["INTERVAL_KERNEL_ENCLOSURES_EXPORTED"] is False
    assert value["mutation_results"][0]["detected"] is True
    print("Berger exact mode-kernel payload verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
