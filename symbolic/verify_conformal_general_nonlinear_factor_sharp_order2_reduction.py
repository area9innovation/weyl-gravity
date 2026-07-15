#!/usr/bin/env python3
"""Verify exact linear consequences of the sharp order-two constraints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.general_nonlinear_factor_sharp_order2_reduction import (
    GeneralNonlinearFactorSharpOrderTwoReduction,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_general_nonlinear_factor_sharp_order2_reduction.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-quadratic-ideal-solved", action="store_true")
    parser.add_argument("--claim-left-ideal-no-go", action="store_true")
    parser.add_argument("--claim-full-factorization", action="store_true")
    parser.add_argument("--claim-general-no-go", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    forbidden = [
        name
        for name, enabled in (
            ("--claim-quadratic-ideal-solved", args.claim_quadratic_ideal_solved),
            ("--claim-left-ideal-no-go", args.claim_left_ideal_no_go),
            ("--claim-full-factorization", args.claim_full_factorization),
            ("--claim-general-no-go", args.claim_general_no_go),
            ("--claim-green", args.claim_green),
            ("--promote-flag", args.promote_flag),
        )
        if enabled
    ]
    if forbidden:
        raise SystemExit(
            "REFUSED: affine-span reduction cannot justify: "
            + ", ".join(forbidden)
        )

    certificate = GeneralNonlinearFactorSharpOrderTwoReduction.build().certificate()
    outcome = certificate["outcome"]
    if outcome["full_quadratic_ideal_solved"]:
        raise AssertionError("affine reduction inferred a full ideal solve")
    if outcome["general_factorization_proved"]:
        raise AssertionError("affine reduction inferred a factorization")
    if outcome["general_factorization_disproved"]:
        raise AssertionError("affine reduction inferred a general no-go")
    if outcome["green_realization_proved"] or outcome["flag_promoted"]:
        raise AssertionError("affine reduction inferred a Green theorem")

    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    linear = certificate["all_affine_linear_consequences"]
    residual = certificate["residual_quadratic_system"]
    print(
        "sharp order-two polynomial reduction: PASS "
        f"({linear['eliminated_variables']} variables eliminated; "
        f"{residual['unique_constraint_count']} residual constraints; "
        "no uncontrolled inference)"
    )


if __name__ == "__main__":
    main()
