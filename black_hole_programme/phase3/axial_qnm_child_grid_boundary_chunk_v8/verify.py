#!/usr/bin/env python3
"""Verify v8 without rerunning its 32 transport panels."""
from __future__ import annotations

import json
from fractions import Fraction

from .runner import AGG, CERT, PANEL_COUNT, PRED_AGG, RAW, ROOT, START, sha


def main() -> None:
    cert = json.loads(CERT.read_text())
    raw = json.loads(RAW.read_text())
    aggregate = json.loads(AGG.read_text())
    predecessor = json.loads(PRED_AGG.read_text())
    assert cert["runs"]["raw"]["sha256"] == sha(RAW)
    assert cert["runs"]["aggregate"]["sha256"] == sha(AGG)
    for item in cert["imports"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert Fraction(predecessor["summary"]["coverage_stop"]) == Fraction(
        START, PANEL_COUNT
    )
    assert raw["requested_child_range"] == [214, 245]
    assert raw["child_panel_count"] == PANEL_COUNT
    assert 0 < raw["elapsed_compute_seconds"] < 120
    if raw["elapsed_compute_seconds"] >= 60:
        assert "Future transport chunks must be smaller" in cert["method"][
            "performance_disposition"
        ]
    assert not raw["threshold_lowered"]
    assert raw["horizon_remainder_root"] == cert["method"][
        "horizon_remainder_root"
    ]
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in aggregate["segments"]
    ]
    assert bounds[0][0] == 0
    assert all(a[1] == b[0] for a, b in zip(bounds, bounds[1:]))
    assert bounds[-1][1] == Fraction(cert["result"]["coverage_stop"])
    assert aggregate["summary"]["all_materialized_deltas_exclude_zero"]
    assert aggregate["summary"]["two_sided_interface_gates_pass"]
    assert cert["result"]["new_accepted_segment_count"] == len(
        raw["accepted_segments"]
    )
    for index, entry in enumerate(raw["accepted_segments"]):
        assert entry["panel"] == START + index
        assert entry["panel_count"] == PANEL_COUNT
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
        "child-grid v8 verifier: PASS "
        f"(coverage {cert['result']['coverage_stop']}; next "
        f"{cert['result']['next_honest_boundary_gap']['start']})"
    )


if __name__ == "__main__":
    main()
