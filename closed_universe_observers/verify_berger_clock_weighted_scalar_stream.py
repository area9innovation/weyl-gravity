#!/usr/bin/env python3
"""Verify one even-clock-weighted Berger scalar stream through two_j=139."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json

from closed_universe_observers.generate_berger_clock_weighted_scalar_stream import (
    CLOCK_POWERS,
    ROOT,
    build,
    certificate_path,
    result_id,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--power", type=int, choices=CLOCK_POWERS, required=True)
    args = parser.parse_args()
    value = json.loads(certificate_path(args.power).read_text())
    assert value == build(args.power)
    assert value["result_id"] == result_id(args.power)
    assert value["clock_weight"]["power"] == args.power
    assert value["coverage"] == {
        "mode_count": 140,
        "reconstructed_full_diagonal_count": 9870,
        "reflection": "basis_index r and n-r have equal local amplitudes",
        "serialized_unique_diagonal_count": 4970,
    }
    for n, mode in enumerate(value["modes"]):
        assert mode["two_j"] == n
        assert mode["dimension"] == n + 1
        assert len(mode["unique_diagonal"]) == n // 2 + 1
        for row in mode["unique_diagonal"]:
            interval = row["clock_weighted_local_amplitude"]
            assert Fraction(interval["lower"]) <= Fraction(interval["upper"])
    assert Fraction(value["truncation_remainder_audit"]["maximum_uniform_remainder_upper"]) < Fraction(1, 10**150)
    flags = value["flags"]
    assert flags["EXTERNAL_CLOCK_AND_EVEN_TIME_WEIGHTED_DIAGONAL_SCALAR_STREAM_TWO_J0_TO_139_EXPORTED"] is True
    assert flags["JOINT_CLOCK_MOMENT_DEPENDENCE_BOUNDED_WITHOUT_FACTORIZATION"] is True
    assert flags["POLARIZATION_RECURRENCE_AND_GREEN_CHARGE_BLOCKS_COMPOSED"] is False
    for evidence in value["dependency_refs"].values():
        path = ROOT / evidence["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
        assert json.loads(path.read_text())["result_id"] == evidence["result_id"]
    print(f"{result_id(args.power)} verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
