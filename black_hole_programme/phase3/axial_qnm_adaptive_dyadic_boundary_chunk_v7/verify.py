#!/usr/bin/env python3
"""Verify v7 without rerunning the validated ODE transport."""
from __future__ import annotations

import json
from fractions import Fraction

from .runner import AGG, CERT, PRED_AGG, RAW, ROOT, sha


def main() -> None:
    cert = json.loads(CERT.read_text())
    raw = json.loads(RAW.read_text())
    aggregate = json.loads(AGG.read_text())
    predecessor = json.loads(PRED_AGG.read_text())

    assert cert["runs"]["raw"]["sha256"] == sha(RAW)
    assert cert["runs"]["aggregate"]["sha256"] == sha(AGG)
    for item in cert["imports"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert raw["elapsed_compute_seconds"] < 60
    assert raw["requested_parent_range"] == [105, 109]
    assert not raw["threshold_lowered"]
    assert raw["horizon_remainder_root"] == cert["method"][
        "horizon_remainder_root"
    ]
    assert Fraction(predecessor["summary"]["coverage_stop"]) == Fraction(
        105, 512
    )
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in aggregate["segments"]
    ]
    assert bounds[0][0] == 0
    assert all(a[1] == b[0] for a, b in zip(bounds, bounds[1:]))
    assert bounds[-1][1] == Fraction(cert["result"]["coverage_stop"])
    assert bounds[-1][1] >= Fraction(105, 512)
    assert aggregate["summary"]["all_materialized_deltas_exclude_zero"]
    assert aggregate["summary"]["two_sided_interface_gates_pass"]
    assert cert["result"]["new_accepted_segment_count"] == len(
        raw["accepted_segments"]
    )
    for key in (
        "full_contour_nonzero_certified",
        "argument_principle_certified",
        "root_count_certified",
        "QNM_location_certified",
        "Smith_selector_certified",
        "defective_fibre_or_EP2_certified",
    ):
        assert cert["claim_flags"][key] is False
    print(
        "adaptive dyadic v7 verifier: PASS "
        f"(coverage {cert['result']['coverage_stop']}; next "
        f"{cert['result']['next_honest_boundary_gap']['start']})"
    )


if __name__ == "__main__":
    main()
