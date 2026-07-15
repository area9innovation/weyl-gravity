#!/usr/bin/env python3
"""Verify the complete order-two gate for the fixed minimal split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.quadratic_obstruction_channel_fixed_branch import (
    QuadraticObstructionChannelFixedBranch,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "quadratic_obstruction_channel_fixed_branch.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-general-factorization-no-go", action="store_true")
    parser.add_argument("--claim-factorization", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    forbidden = [
        name
        for name, enabled in (
            (
                "--claim-general-factorization-no-go",
                args.claim_general_factorization_no_go,
            ),
            ("--claim-factorization", args.claim_factorization),
            ("--claim-green", args.claim_green),
            ("--promote-flag", args.promote_flag),
        )
        if enabled
    ]
    if forbidden:
        raise SystemExit(
            "REFUSED: one fixed split cannot justify: " + ", ".join(forbidden)
        )

    certificate = QuadraticObstructionChannelFixedBranch.build().certificate()
    outcome = certificate["outcome"]
    if outcome["general_two_nontrivial_factor_branch_decided"]:
        raise AssertionError("fixed split inferred a general no-go")
    if outcome["mixed_order_factorization_proved"]:
        raise AssertionError("inconsistent split inferred a factorization")
    if outcome["green_realization_proved"] or outcome["flag_promoted"]:
        raise AssertionError("inconsistent split inferred a theorem promotion")
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        "quadratic obstruction fixed branch: PASS "
        "(order-two rank 100/101; exact one-row no-go; scope fixed)"
    )


if __name__ == "__main__":
    main()
