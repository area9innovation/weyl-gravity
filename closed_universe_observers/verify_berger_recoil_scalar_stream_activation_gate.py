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
    assert rows["finite_detector_coefficient_provider_two_j0_to_4"] == "CERTIFIED"
    assert rows["finite_polynomial_nested_time_convolution"] == "CERTIFIED"
    assert rows["finite_partitioned_detector_matched_absolute_g3_feedback"] == "CERTIFIED"
    assert rows["finite_cross_window_detector_advanced_maxwell_remainder"] == "CERTIFIED"
    assert rows["finite_six_mismatched_absolute_g3_feedback_channels"] == "CERTIFIED"
    assert rows["finite_first_omitted_shell_direct_provider_two_j5"] == "CERTIFIED"
    assert rows["finite_two_j5_all_channel_column_feedback_binding"] == "CERTIFIED"
    assert rows["callable_shell_interval_backend"] == "CERTIFIED"
    assert rows["complete_detector_coefficient_provider"] == "CERTIFIED"
    assert rows["tail_aware_aggregate_stop_loop"] == "CERTIFIED"
    assert rows["generic_direct_finite_shell_provider"] == "CERTIFIED"
    assert rows["complex_channel_to_real_shell_scalar_map"] == "OBSTRUCTED"
    assert value["readiness"]["four_scalar_stream_active"] is False
    assert value["flags"]["FINITE_FIRST_OMITTED_SHELL_DIRECT_PROVIDER_TWO_J5_EXPORTED"] is True
    assert value["flags"]["TWO_J5_FEEDBACK_CHANNELS_EVALUATED"] is True
    assert value["flags"]["ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED"] is True
    assert value["flags"]["GENERIC_DIRECT_FINITE_SHELL_PROVIDER_EXPORTED"] is True
    assert value["flags"]["TAIL_AWARE_AGGREGATE_STOP_LOOP_EXPORTED"] is True
    assert all(row["detected"] for row in value["mutation_results"])
    assert value["atlas_status"] == "OBSTRUCTED"
    print("Berger recoil scalar stream activation-gate verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
