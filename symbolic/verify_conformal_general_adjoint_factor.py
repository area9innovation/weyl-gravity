#!/usr/bin/env python3
"""Verify the pairing-aware sharp reduction of the general factor problem."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.general_adjoint_factor import (
    GeneralAdjointFactorReduction,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "general_adjoint_factor.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-factorization", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    parser.add_argument("--use-naive-word-adjoint", action="store_true")
    args = parser.parse_args()
    forbidden = [
        name
        for name, enabled in (
            ("--claim-factorization", args.claim_factorization),
            ("--claim-green", args.claim_green),
            ("--promote-flag", args.promote_flag),
            ("--use-naive-word-adjoint", args.use_naive_word_adjoint),
        )
        if enabled
    ]
    if forbidden:
        raise SystemExit(
            "REFUSED: the sharp-reduced cubic gate cannot justify: "
            + ", ".join(forbidden)
        )

    certificate = GeneralAdjointFactorReduction.build().certificate()
    outcome = certificate["outcome"]
    if outcome["general_factorization_proved"]:
        raise AssertionError("sharp cubic reduction inferred a factorization")
    if outcome["general_factorization_disproved"]:
        raise AssertionError("sharp cubic reduction inferred a general no-go")
    if outcome["mixed_order_green_realization"]:
        raise AssertionError("sharp cubic reduction inferred a Green theorem")
    if certificate["pairing_aware_adjoint"][
        "naive_ordered_word_box_square_defect"
    ] != 48:
        raise AssertionError("naive ordered-word mutation was not rejected")

    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        "general adjoint factor reduction: PASS "
        "(P,D self-adjoint; right factors induced; cubic family 21; "
        "214-parameter nonlinear lower solve remains open)"
    )


if __name__ == "__main__":
    main()
