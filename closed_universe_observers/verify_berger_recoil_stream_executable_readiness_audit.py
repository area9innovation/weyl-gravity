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
    assert rows["detector_profile_coefficient_provider"] == "CERTIFIED"
    assert rows["finite_polynomial_nested_time_convolution"] == "CERTIFIED"
    assert rows["finite_partitioned_detector_matched_absolute_g3_feedback"] == "CERTIFIED"
    assert rows["finite_cross_window_detector_advanced_maxwell_remainder"] == "CERTIFIED"
    assert rows["finite_six_mismatched_absolute_g3_feedback_channels"] == "CERTIFIED"
    assert rows["finite_first_omitted_shell_direct_provider_two_j5"] == "CERTIFIED"
    assert rows["generic_direct_finite_shell_provider"] == "CERTIFIED"
    assert rows["complex_channel_to_real_shell_scalar_map"] == "CERTIFIED"
    assert rows["finite_two_j6_reality_folded_feedback_binding"] == "CERTIFIED"
    assert rows["nested_time_convolution_backend"] == "OBSTRUCTED"
    assert rows["shell_interval_evaluator"] == "CERTIFIED"
    assert rows["tail_aware_aggregate_stop_loop"] == "CERTIFIED"
    assert value["flags"]["FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED"] is True
    assert value["flags"]["FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED"] is True
    assert value["flags"]["FINITE_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK_EXPORTED"] is True
    assert value["flags"]["ALL_EIGHT_ABC_TWO_J0_K0_INTERVALS_EXPORTED"] is True
    assert value["flags"]["FINITE_FIRST_OMITTED_SHELL_DIRECT_PROVIDER_TWO_J5_EXPORTED"] is True
    assert value["flags"]["TWO_J5_FEEDBACK_CHANNELS_EVALUATED"] is True
    assert value["flags"]["ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED"] is True
    assert value["flags"]["GENERIC_DIRECT_FINITE_SHELL_PROVIDER_EXPORTED"] is True
    assert value["flags"]["TAIL_AWARE_AGGREGATE_STOP_LOOP_EXPORTED"] is True
    assert value["flags"]["COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED"] is True
    assert value["flags"]["TWO_J6_FEEDBACK_CHANNELS_EVALUATED"] is True
    assert value["flags"]["CALLABLE_SHELL_INTERVAL_BACKEND_EXPORTED"] is True
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger recoil executable-readiness audit verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
