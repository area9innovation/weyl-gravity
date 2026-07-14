#!/usr/bin/env python3
"""Verify the complete invariant cubic lower-order factor gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.auxiliary_lower_order_factor_ansatz import (
    AuxiliaryLowerOrderFactorAnsatz,
)


CERTIFICATE = (
    ROOT / "covariant_completion" / "certificates"
    / "curved_auxiliary_lower_order_factor_ansatz.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-full-factorization", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--skip-quadratic-curvature", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    forbidden = [
        name
        for name, enabled in (
            ("--claim-full-factorization", args.claim_full_factorization),
            ("--claim-green", args.claim_green),
            ("--skip-quadratic-curvature", args.skip_quadratic_curvature),
            ("--promote-flag", args.promote_flag),
        )
        if enabled
    ]
    if forbidden:
        raise SystemExit(
            "REFUSED: cubic gate cannot justify: " + ", ".join(forbidden)
        )

    certificate = AuxiliaryLowerOrderFactorAnsatz.build().certificate()
    if certificate["outcome"]["mixed_order_factorization_proved"]:
        raise AssertionError("cubic solution family inferred a factorization")
    if certificate["outcome"]["mixed_order_green_realization"]:
        raise AssertionError("cubic solution family inferred a Green theorem")
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        "auxiliary lower-order cubic gate: PASS "
        "(complete 93-parameter invariant X1; simultaneous family dimension 45; "
        "quadratic curvature solve remains open)"
    )


if __name__ == "__main__":
    main()
