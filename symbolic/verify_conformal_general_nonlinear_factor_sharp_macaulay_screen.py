#!/usr/bin/env python3
"""Verify the exact structural degree-one Macaulay screen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.general_nonlinear_factor_sharp_macaulay_screen import (
    GeneralNonlinearFactorSharpMacaulayScreen,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_general_nonlinear_factor_sharp_macaulay_screen.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-constant-no-go", action="store_true")
    parser.add_argument("--claim-low-degree-elimination", action="store_true")
    parser.add_argument("--claim-full-factorization", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    forbidden = [
        name
        for name, enabled in (
            ("--claim-constant-no-go", args.claim_constant_no_go),
            ("--claim-low-degree-elimination", args.claim_low_degree_elimination),
            ("--claim-full-factorization", args.claim_full_factorization),
            ("--claim-green", args.claim_green),
            ("--promote-flag", args.promote_flag),
        )
        if enabled
    ]
    if forbidden:
        raise SystemExit(
            "REFUSED: structural/modular Macaulay screening cannot justify: "
            + ", ".join(forbidden)
        )

    certificate = GeneralNonlinearFactorSharpMacaulayScreen.build().certificate()
    outcome = certificate["outcome"]
    if outcome["constant_contradiction_decided"]:
        raise AssertionError("screening inferred a constant-ideal decision")
    if outcome["low_degree_ideal_dimensions_decided"]:
        raise AssertionError("screening inferred exact low-degree dimensions")
    if outcome["general_factorization_disproved"]:
        raise AssertionError("screening inferred a general no-go")
    if outcome["green_realization_proved"] or outcome["flag_promoted"]:
        raise AssertionError("screening inferred a Green theorem")

    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    matrix = certificate["exact_sparse_matrix"]
    bounds = certificate["degree_three_exact_bounds"]
    print(
        "sharp degree-one Macaulay screen: PASS "
        f"({matrix['total_rows']}x{certificate['input']['multiplier_columns']}; "
        f"degree-three rational rank in [{bounds['rational_rank_lower_bound']},"
        f"{bounds['rational_rank_upper_bound']}]; no ideal decision)"
    )


if __name__ == "__main__":
    main()
