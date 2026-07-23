"""Negative mutations for recurrence/remainder and claim-boundary gates."""
from __future__ import annotations

import copy
import json

try:
    from .produce import CERTIFICATE
    from .verify import VerifyError, verify_data
except ImportError:  # deterministic direct-script command recorded in certificate
    from produce import CERTIFICATE
    from verify import VerifyError, verify_data


def rejected(data):
    try:
        verify_data(data)
    except VerifyError:
        return True
    return False


def main():
    original = json.loads(CERTIFICATE.read_text())
    tests = []

    recurrence = copy.deepcopy(original)
    recurrence["horizon"]["kappa"] = 3
    tests.append(rejected(recurrence))

    remainder = copy.deepcopy(original)
    remainder["horizon"]["S_B_tau"]["num"] += 1
    tests.append(rejected(remainder))

    gap = copy.deepcopy(original)
    gap["horizon"]["frequency_cells"][1][0]["num"] += 1
    tests.append(rejected(gap))

    false_promotion = copy.deepcopy(original)
    false_promotion["claim_flags"]["infinity_six_column_initializer_certified"] = True
    tests.append(rejected(false_promotion))

    nonintegrable = copy.deepcopy(original)
    nonintegrable["infinity"]["decay_p_ij"][0][0] = 1
    tests.append(rejected(nonintegrable))

    practical_fiction = copy.deepcopy(original)
    practical_fiction["infinity"]["practical_handoff_disposition"] = "READY"
    tests.append(rejected(practical_fiction))

    if tests == [True, True, True, True, True, True]:
        print("PASS six endpoint-enclosure mutations rejected")
        return
    raise SystemExit("mutation escaped verifier")


if __name__ == "__main__":
    main()
