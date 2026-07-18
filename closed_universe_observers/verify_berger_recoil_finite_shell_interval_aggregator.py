#!/usr/bin/env python3
"""Verify the exact Berger recoil finite-shell interval aggregator."""

import json

from closed_universe_observers.generate_berger_recoil_finite_shell_interval_aggregator import CERTIFICATE, build


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["exact_fixture"]["shell_interval"] == {"lower": "-16", "upper": "-72/5", "width": "8/5"}
    assert all(row["detected"] for row in value["mutation_results"])
    assert value["flags"]["CALLABLE_SHELL_INTERVAL_BACKEND_EXPORTED"] is True
    print("Berger recoil finite-shell interval aggregator verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
