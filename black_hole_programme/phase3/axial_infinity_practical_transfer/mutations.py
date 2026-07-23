"""Negative mutations for the F4, endpoint, phase, rank, and claim gates."""
from __future__ import annotations

import copy
import json

from .produce import OUTPUT
from .verify import VerifyError, verify_data


def rejected(data: dict) -> bool:
    try:
        verify_data(data)
    except VerifyError:
        return True
    return False


def main() -> None:
    original = json.loads(OUTPUT.read_text())
    trials = []

    f4 = copy.deepcopy(original)
    f4["structural_proof"]["XI2_XI3_derivative_consistency"] = "F4=0"
    trials.append(rejected(f4))

    zero_limit = copy.deepcopy(original)
    zero_limit["interval_cells"][0]["powers"][4][2] = 2
    trials.append(rejected(zero_limit))

    phase = copy.deepcopy(original)
    phase["interval_cells"][0]["cross_rate_minimum_p"] = 2
    phase["interval_cells"][0]["powers"][4][2] = 2
    trials.append(rejected(phase))

    rank = copy.deepcopy(original)
    rank["claim_flags"]["full_rank_R32_initializer_certified"] = False
    trials.append(rejected(rank))

    subdivision = copy.deepcopy(original)
    subdivision["interval_cells"].pop()
    trials.append(rejected(subdivision))

    promotion = copy.deepcopy(original)
    promotion["claim_flags"]["flux_certified"] = True
    trials.append(rejected(promotion))

    if trials == [True] * 6:
        print("PASS six practical-transfer mutations rejected")
        return
    raise SystemExit("mutation escaped practical-transfer verifier")


if __name__ == "__main__":
    main()
