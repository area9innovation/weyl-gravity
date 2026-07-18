#!/usr/bin/env python3
"""Verify the validated Berger scalar coefficient stream through two_j=139."""

import hashlib
import json
from fractions import Fraction

from closed_universe_observers.generate_berger_clock_integrated_scalar_stream import (
    CERTIFICATE,
    ROOT,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["coverage"] == {
        "mode_count": 140,
        "reconstructed_full_diagonal_count": 9870,
        "reflection": "basis_index r and n-r have equal local amplitudes",
        "serialized_unique_diagonal_count": 4970,
    }
    assert value["low_mode_compatibility_audit"]["overlap_defect_count"] == 0
    for n, mode in enumerate(value["modes"]):
        assert mode["two_j"] == n
        assert mode["dimension"] == n + 1
        assert len(mode["unique_diagonal"]) == mode["two_j"] // 2 + 1
        for row in mode["unique_diagonal"]:
            interval = row["clock_integrated_local_amplitude"]
            assert Fraction(interval["lower"]) <= Fraction(interval["upper"])
    assert Fraction(value["truncation_remainder_audit"]["maximum_uniform_remainder_upper"]) < Fraction(1, 10**150)
    assert value["flags"]["POLARIZATION_RECURRENCE_CLOCK_GREEN_CHAIN_APPLIED"] is False
    for evidence in value["dependency_refs"].values():
        path = ROOT / evidence["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
        assert json.loads(path.read_text())["result_id"] == evidence["result_id"]
    print("BERGER_CLOCK_INTEGRATED_SCALAR_STREAM_TWO_J139 verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
