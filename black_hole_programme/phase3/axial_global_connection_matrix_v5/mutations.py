"""Negative mutations for the v5 terminal claim boundary."""
from __future__ import annotations

import copy
import json

from .produce import OUTPUT
from .verify import VerifyError, verify_data


def rejected(data: dict, text: str | None = None) -> bool:
    try:
        verify_data(data, text)
    except VerifyError:
        return True
    return False


def main() -> None:
    base = json.loads(OUTPUT.read_text())
    cases: list[tuple[dict, str | None]] = []

    m = copy.deepcopy(base)
    m["claim_flags"]["global_connection_certified"] = True
    cases.append((m, None))

    m = copy.deepcopy(base)
    m["affine_moving_frame_result"]["carrier_rank_certified"] = False
    cases.append((m, None))

    m = copy.deepcopy(base)
    m["structured_lower_lift_result"]["maximum_interval_width"] = 0.01
    cases.append((m, None))

    m = copy.deepcopy(base)
    m["missing_dependency"] = ""
    cases.append((m, None))

    m = copy.deepcopy(base)
    m["flattened_width_growth"][-1]["carrier_max_width"] = 0.1
    cases.append((m, None))

    m = copy.deepcopy(base)
    key = next(iter(m["imports"]))
    m["imports"][key]["sha256"] = "0" * 64
    cases.append((m, None))

    adapter = (OUTPUT.parent / "validated_global_connection.forge").read_text()
    cases.append((copy.deepcopy(base), adapter + "\nfn bad(){ let x=ivm_inverse(ivm_identity(2)); }\n"))

    if not all(rejected(data, text) for data, text in cases):
        raise SystemExit("mutation escaped")
    print(f"PASS {len(cases)} negative mutations rejected")


if __name__ == "__main__":
    main()
