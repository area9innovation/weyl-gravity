#!/usr/bin/env python3
"""Verify the v4 bounded adaptive aggregate without rerunning transport."""
from __future__ import annotations

import json
from fractions import Fraction

from .runner import AGG, CERT, RAW, ROOT, sha


def main() -> None:
    cert = json.loads(CERT.read_text())
    raw = json.loads(RAW.read_text())
    aggregate = json.loads(AGG.read_text())
    assert cert["runs"]["raw"]["sha256"] == sha(RAW)
    assert cert["runs"]["aggregate"]["sha256"] == sha(AGG)
    for item in cert["imports"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert raw["elapsed_compute_seconds"] < 60
    assert not raw["threshold_lowered"]
    assert raw["horizon_remainder_root"] == cert["method"][
        "horizon_remainder_root"
    ]
    bounds = [
        (Fraction(x["start"]), Fraction(x["stop"]))
        for x in aggregate["segments"]
    ]
    assert bounds[0][0] == 0
    assert all(a[1] == b[0] for a, b in zip(bounds, bounds[1:]))
    assert bounds[-1][1] == Fraction(cert["result"]["coverage_stop"])
    assert aggregate["summary"]["all_materialized_deltas_exclude_zero"]
    for key in (
        "root_count_certified", "QNM_location_certified",
        "Smith_selector_certified", "defective_fibre_or_EP2_certified"
    ):
        assert not cert["claim_flags"][key]
    print(
        "adaptive dyadic v4 verifier: PASS "
        f"(coverage {cert['result']['coverage_stop']}; next "
        f"{cert['result']['next_honest_boundary_gap']['start']})"
    )


if __name__ == "__main__":
    main()
