#!/usr/bin/env python3
"""Verify the finite detector coefficient provider certificate."""

import json
from closed_universe_observers.generate_berger_recoil_finite_detector_coefficient_provider import CERTIFICATE, build


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["flags"]["FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED"] is True
    assert value["flags"]["COMPLETE_DETECTOR_COEFFICIENT_PROVIDER_EXPORTED"] is False
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger finite detector coefficient provider verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
