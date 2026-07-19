#!/usr/bin/env python3
"""Verify the partition-refined matched-feedback certificate."""

import json
from fractions import Fraction

from closed_universe_observers.generate_berger_recoil_partitioned_matched_feedback import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["flags"][
        "MATCHED_FEEDBACK_WIDTHS_STRICTLY_CONTRACT_2_TO_4_TO_8"
    ] is True
    assert value["flags"]["PARTITION8_WIDTHS_STRICTLY_BELOW_COARSE_HULLS"] is True
    assert value["flags"]["PARTITION8_MATCHED_FEEDBACK_INTERVALS_EXCLUDE_ZERO"] is False
    for detector, rows in value["partition_rails"].items():
        assert [row["partition_count"] for row in rows] == [2, 4, 8]
        for component in ("real", "imaginary"):
            widths = [
                Fraction(row["coefficient_block_interval"][component]["width"])
                for row in rows
            ]
            assert widths[0] > widths[1] > widths[2]
        assert all(row["coefficient_block_contains_zero"] for row in rows), detector
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger partitioned matched-feedback verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
