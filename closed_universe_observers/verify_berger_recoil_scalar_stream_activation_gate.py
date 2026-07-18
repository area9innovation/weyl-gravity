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
    assert rows["complete_symbolic_harmonic_preparation_functional"] == "CERTIFIED"
    assert rows["advanced_massive_preparation_operator_word"] == "CERTIFIED"
    assert rows["complete_modewise_recoil_scalar_integrand"] == "CERTIFIED"
    assert value["readiness"]["symbolic_modewise_word_ready"] is True
    assert value["readiness"]["internal_modewise_stream_ready"] is False
    assert rows["callable_shell_interval_backend"] == "OBSTRUCTED"
    assert value["readiness"]["four_scalar_stream_active"] is False
    assert all(row["detected"] for row in value["mutation_results"])
    assert value["atlas_status"] == "OBSTRUCTED"
    print("Berger recoil scalar stream activation-gate verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
