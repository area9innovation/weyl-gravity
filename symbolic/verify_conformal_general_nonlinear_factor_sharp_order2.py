#!/usr/bin/env python3
"""Verify the sharp-reduced 214-parameter order-two factor gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.general_nonlinear_factor_sharp_order2 import (
    GeneralNonlinearFactorSharpOrderTwo,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_general_nonlinear_factor_sharp_order2.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-full-factorization", action="store_true")
    parser.add_argument("--claim-general-no-go", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    forbidden = [
        name
        for name, enabled in (
            ("--claim-full-factorization", args.claim_full_factorization),
            ("--claim-general-no-go", args.claim_general_no_go),
            ("--claim-green", args.claim_green),
            ("--promote-flag", args.promote_flag),
        )
        if enabled
    ]
    if forbidden:
        raise SystemExit(
            "REFUSED: the sharp-reduced order-two gate cannot justify: "
            + ", ".join(forbidden)
        )

    certificate = GeneralNonlinearFactorSharpOrderTwo.build().certificate()
    outcome = certificate["outcome"]
    if outcome["orders_one_and_zero_solved"]:
        raise AssertionError("order-two gate inferred lower-order equations")
    if outcome["general_factorization_proved"]:
        raise AssertionError("order-two gate inferred a factorization")
    if outcome["general_factorization_disproved"]:
        raise AssertionError("order-two gate inferred a general no-go")
    if outcome["mixed_order_green_realization"] or outcome["flag_promoted"]:
        raise AssertionError("order-two gate inferred a Green theorem")

    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    gate = certificate["algebraic_schur_gate"]
    print(
        "sharp-reduced nonlinear factor order two: PASS "
        f"({certificate['sparse_order_two_system']['equation_rows']} rows; "
        f"rank {gate['rank']}/{gate['variable_count']}; "
        f"{gate['nonzero_projected_constraints']} projected constraints; "
        "no full-factorization promotion)"
    )


if __name__ == "__main__":
    main()
