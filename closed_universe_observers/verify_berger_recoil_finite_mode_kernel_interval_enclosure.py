#!/usr/bin/env python3
"""Verify the finite Berger mode-kernel interval enclosure certificate."""

import json

from closed_universe_observers.generate_berger_recoil_finite_mode_kernel_interval_enclosure import CERTIFICATE, build


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["flags"]["FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED"] is True
    assert value["flags"]["MASSIVE_ONE_FORM_CORRECTION_KERNEL_INTERVALS_EXPORTED"] is True
    assert value["flags"]["ACTUAL_SWITCH_PROFILE_AND_FORM_BINDING_EXPORTED"] is False
    assert value["fixtures"]["Maxwell_zero_mode_exact_tail"] == "0"
    assert value["fixtures"]["massive_two_j0_degree0_operator_norm_upper"] == "2"
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger finite mode-kernel interval enclosure verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
