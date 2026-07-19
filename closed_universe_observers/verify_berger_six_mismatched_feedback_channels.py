#!/usr/bin/env python3
"""Verify the six mismatched Berger feedback-channel certificate."""

import json

from closed_universe_observers.generate_berger_six_mismatched_feedback_channels import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert {row["channel_id"] for row in value["causal_support_zero_channels"]} == {
        "I_001", "I_010", "I_011", "I_110"
    }
    assert set(value["causally_allowed_partition_rails"]) == {"I_100", "I_101"}
    assert all(
        row["coefficient_block_contains_zero"]
        for rows in value["causally_allowed_partition_rails"].values()
        for row in rows
    )
    assert value["flags"]["ALL_EIGHT_ABC_TWO_J0_K0_INTERVALS_EVALUATED"]
    assert not value["flags"]["ALL_EIGHT_ABC_ALL_SHELL_INTERVALS_EVALUATED"]
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger six mismatched feedback-channel verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
