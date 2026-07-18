#!/usr/bin/env python3
"""Verify the Berger recoil-scalar stream activation gate."""

import json

from closed_universe_observers.generate_berger_recoil_scalar_stream_activation_gate import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    rows = {row["id"]: row["status"] for row in value["readiness"]["internal_rows"]}
    assert rows["response_specific_stopping_envelope"] == "CERTIFIED"
    assert rows["complete_harmonic_preparation_coefficients"] == "OPEN"
    assert rows["advanced_massive_preparation_image"] == "OPEN"
    assert value["readiness"]["four_scalar_stream_active"] is False
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger recoil scalar stream activation-gate verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
