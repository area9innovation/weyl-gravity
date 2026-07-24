#!/usr/bin/env python3
"""Verifier rerunning the projective preflight."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .riccati_preflight import compute

HERE = Path(__file__).resolve().parent


def verify(document: dict) -> list[str]:
    errors = []
    run = compute()
    for row in run["rows"]:
        if not row["failure"]:
            errors.append("a panel unexpectedly reached r=4")
        elif not row["failure"]["projective_ball_contains_zero"]:
            errors.append("failure ball unexpectedly admits reciprocal chart")
    flags = document["claim_flags"]
    if flags.get("validated_projective_preflight_executed") is not True:
        errors.append("preflight flag must be true")
    for key in (
        "physical_projective_pole_established",
        "usable_r4_projective_enclosure",
        "tangent_sensitivity_transported_to_r4",
        "b_over_a_on_contour_constructed",
        "Evans_boundary_nonzero_certified",
        "QNM_root_count_certified",
        "QNM_or_EP2_certified",
    ):
        if flags.get(key) is not False:
            errors.append(f"{key} must remain false")
    return errors


def main() -> int:
    errors = verify(json.loads((HERE / "certificate.json").read_text()))
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("PASS validated Riccati chart-enclosure obstruction")
    return 0


if __name__ == "__main__":
    sys.exit(main())
