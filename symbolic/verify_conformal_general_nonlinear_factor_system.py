#!/usr/bin/env python3
"""Verify the complete sparse 421-variable mixed-order factor system."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.general_nonlinear_factor_system import (
    GeneralNonlinearFactorSystem,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_general_nonlinear_factor_system.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-factorization", action="store_true")
    parser.add_argument("--claim-obstruction", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()

    forbidden = [
        name
        for name, enabled in (
            ("--claim-factorization", args.claim_factorization),
            ("--claim-obstruction", args.claim_obstruction),
            ("--claim-green", args.claim_green),
            ("--promote-flag", args.promote_flag),
        )
        if enabled
    ]
    if forbidden:
        raise SystemExit(
            "REFUSED: exact system assembly and the first Schur rank cannot justify: "
            + ", ".join(forbidden)
        )

    certificate = GeneralNonlinearFactorSystem.build().certificate()
    outcome = certificate["outcome"]
    if outcome["exact_solution_found"] or outcome["exact_obstruction_found"]:
        raise AssertionError("assembly certificate crossed its theorem boundary")
    if outcome["mixed_order_factorization_proved"]:
        raise AssertionError("assembly inferred a factorization")
    if outcome["green_realization_proved"] or outcome["flag_promoted"]:
        raise AssertionError("assembly inferred a Green theorem")

    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    sparse = certificate["sparse_system"]
    schur = certificate["quadratic_order_schur_gate"]
    print(
        "general nonlinear mixed-order factor system: PASS "
        f"({sum(sparse['row_counts_by_derivative_order_0_to_4'])} rows; "
        f"rank {schur['rank']}/{schur['linear_variable_count']} at the "
        "order-two Schur gate; no theorem promotion)"
    )


if __name__ == "__main__":
    main()
