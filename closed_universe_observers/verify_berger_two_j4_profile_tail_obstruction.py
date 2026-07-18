#!/usr/bin/env python3
"""Verify the two_j<=4 detector-profile tail obstruction."""

import hashlib
import json
from fractions import Fraction

from closed_universe_observers.generate_berger_two_j4_profile_tail_obstruction import CERTIFICATE, ROOT, build


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    audit = value["tail_audit"]
    assert Fraction(audit["total_fourier_energy_lower"]) > 280_000_000
    assert Fraction(audit["retained_fourier_energy_upper"]) == 675
    assert Fraction(audit["omitted_energy_fraction_lower"]) > Fraction(99999, 100000)
    assert audit["uniform_small_tail_through_two_j4"] is False
    assert value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False
    for evidence in value["dependency_refs"].values():
        path = ROOT / evidence["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
        assert json.loads(path.read_text())["result_id"] == evidence["result_id"]
    print("BERGER_TWO_J4_PROFILE_TAIL_OBSTRUCTION verification: PASS")
    return 0


if __name__ == "__main__": raise SystemExit(main())
