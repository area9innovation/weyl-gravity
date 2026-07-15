#!/usr/bin/env python3
"""Verify the exact repair of the common bare-Box quadratic channel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.quadratic_obstruction_channel import (
    QuadraticObstructionChannel,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "quadratic_obstruction_channel.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-full-quadratic-solve", action="store_true")
    parser.add_argument("--claim-factorization", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    forbidden = [
        name
        for name, enabled in (
            ("--claim-full-quadratic-solve", args.claim_full_quadratic_solve),
            ("--claim-factorization", args.claim_factorization),
            ("--claim-green", args.claim_green),
            ("--promote-flag", args.promote_flag),
        )
        if enabled
    ]
    if forbidden:
        raise SystemExit(
            "REFUSED: one repaired quadratic orbit cannot justify: "
            + ", ".join(forbidden)
        )

    certificate = QuadraticObstructionChannel.build().certificate()
    outcome = certificate["outcome"]
    if outcome["full_quadratic_system_solved"]:
        raise AssertionError("scoped channel inferred a full quadratic solve")
    if outcome["mixed_order_factorization_proved"]:
        raise AssertionError("scoped channel inferred a factorization")
    if outcome["green_realization_proved"] or outcome["flag_promoted"]:
        raise AssertionError("scoped channel inferred a theorem promotion")
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        "quadratic obstruction channel: PASS "
        "(-8 attained on the complete invariant family; SO(3) orbit repaired; "
        "no factorization promotion)"
    )


if __name__ == "__main__":
    main()
