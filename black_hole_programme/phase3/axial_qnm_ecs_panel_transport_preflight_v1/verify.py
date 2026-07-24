#!/usr/bin/env python3
"""Verifier that reruns the acb panel-width gate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .panel_preflight import compute

HERE = Path(__file__).resolve().parent


def verify(document: dict) -> list[str]:
    errors = []
    fresh = compute()
    for row in fresh["rows"]:
        for value in row["component_radius_lower"]:
            if float(value.split()[0].strip("[]")) <= 1:
                errors.append("a rerun panel component radius no longer exceeds one")
    flags = document["claim_flags"]
    if flags.get("panelwise_acb_transport_executed") is not True:
        errors.append("panel execution flag must be true")
    for key in (
        "evans_usable_outgoing_column", "b_over_a_on_contour_constructed",
        "Evans_boundary_nonzero_certified", "QNM_root_count_certified",
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
    print("PASS validated acb panel transport width shortfall")
    return 0


if __name__ == "__main__":
    sys.exit(main())
