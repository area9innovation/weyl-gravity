#!/usr/bin/env python3
"""Verify the Berger first-omitted-shell recoil provider certificate."""

import json

from closed_universe_observers.generate_berger_recoil_first_omitted_shell_provider import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    crosswalk = value["carrier_crosswalk"]
    assert crosswalk["detector_generator_source_hash_matches_import"]
    assert crosswalk["cross_window_generator_source_hash_matches_import"]
    assert crosswalk["kernel_generator_source_hash_matches_import"]
    assert (
        crosswalk["hashed_exact_T_two_j138_stream_identification_status"]
        == "NO_CERTIFIED_MAP"
    )
    assert value["detector_provider_extension"]["two_j"] == 5
    assert len(value["kernel_provider_extension"]["blocks"]) == 5
    assert all(row["detected"] for row in value["mutation_results"])
    assert not value["flags"]["TWO_J5_FEEDBACK_CHANNELS_EVALUATED"]
    assert not value["flags"]["COMPLETE_ALL_SHELL_PROVIDER_EXPORTED"]
    print("Berger recoil first-omitted-shell provider verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
