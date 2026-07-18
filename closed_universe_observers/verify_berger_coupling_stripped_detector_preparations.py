#!/usr/bin/env python3
"""Verify the coupling-stripped Berger detector preparations."""

import json

from closed_universe_observers.generate_berger_coupling_stripped_detector_preparations import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    factorization = value["factorization"]
    assert factorization["absolute_g3_channel_monomial"] == "g_b g_c^2"
    assert factorization["leading_determinant"] == "g_0 g_1 tilde_E_0 tilde_E_1"
    assert all(row["held_fixed_in_coupling_expansion"] for row in value["preparation_rows"])
    assert value["flags"]["HARMONIC_COEFFICIENTS_EVALUATED"] is False
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger coupling-stripped detector preparation verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
