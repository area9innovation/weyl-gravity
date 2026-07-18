#!/usr/bin/env python3
"""Verify finite nested Green time-convolution certificate."""

import json

from closed_universe_observers.generate_berger_recoil_finite_nested_time_convolution import CERTIFICATE, build


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["fixtures"]["remainder_upper"] == "61/200"
    assert value["flags"]["FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED"] is True
    assert value["flags"]["COMPLETE_PHYSICAL_NESTED_TIME_CONVOLUTION_BACKEND_EXPORTED"] is False
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger finite nested time-convolution verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
