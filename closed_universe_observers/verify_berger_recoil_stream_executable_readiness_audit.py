#!/usr/bin/env python3
"""Verify the fail-closed Berger recoil executable-readiness audit."""

import json

from closed_universe_observers.generate_berger_recoil_stream_executable_readiness_audit import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["readiness"]["symbolic_word_ready"] is True
    assert value["readiness"]["internal_executable_stream_ready"] is False
    assert value["readiness"]["external_specialization_deferred"] is True
    assert value["readiness"]["four_scalar_stream_active"] is False
    rows = {row["id"]: row["status"] for row in value["readiness"]["rows"]}
    assert rows["finite_detector_coefficient_provider_two_j0_to_4"] == "CERTIFIED"
    assert rows["detector_profile_coefficient_provider"] == "OBSTRUCTED"
    assert rows["finite_polynomial_nested_time_convolution"] == "CERTIFIED"
    assert rows["nested_time_convolution_backend"] == "OBSTRUCTED"
    assert rows["shell_interval_evaluator"] == "CERTIFIED"
    assert value["flags"]["FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED"] is True
    assert value["flags"]["FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED"] is True
    assert value["flags"]["CALLABLE_SHELL_INTERVAL_BACKEND_EXPORTED"] is True
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger recoil executable-readiness audit verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
