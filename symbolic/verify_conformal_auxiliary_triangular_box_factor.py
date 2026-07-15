#!/usr/bin/env python3
"""Verify all four exact bare-Box triangular factor orientations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.auxiliary_triangular_box_factor import (
    AuxiliaryTriangularBoxFactor,
)


CERTIFICATE = (
    ROOT / "covariant_completion" / "certificates"
    / "curved_auxiliary_triangular_box_factor.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-general-factorization-no-go", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    forbidden = [
        name
        for name, enabled in (
            ("--claim-general-factorization-no-go", args.claim_general_factorization_no_go),
            ("--claim-green", args.claim_green),
            ("--promote-flag", args.promote_flag),
        )
        if enabled
    ]
    if forbidden:
        raise SystemExit(
            "REFUSED: scoped triangular solve cannot justify: " + ", ".join(forbidden)
        )

    certificate = AuxiliaryTriangularBoxFactor.build().certificate()
    if certificate["outcome"]["mixed_order_factorization_proved"]:
        raise AssertionError("triangular branch inferred a general factorization")
    if certificate["outcome"]["green_realization_proved"]:
        raise AssertionError("triangular branch inferred a Green theorem")
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    count = certificate["outcome"]["consistent_orientation_count"]
    print(
        "auxiliary triangular bare-Box factors: PASS "
        f"(four exact orientations; {count} consistent; no theorem promotion)"
    )


if __name__ == "__main__":
    main()
