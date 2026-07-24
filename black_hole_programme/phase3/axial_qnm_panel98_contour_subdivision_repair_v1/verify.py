#!/usr/bin/env python3
"""Independent hash-only verifier for the panel-98 repair."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from flint import arb

from ..axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row
from .repair import (
    AGGREGATE_RUN,
    CHILD_RUN,
    HERE,
    ROOT,
    STABLE_ROOT,
    canonical_sha,
    sha,
)

CERT = HERE / "certificate.json"


def main() -> None:
    certificate = json.loads(CERT.read_text())
    children = json.loads(CHILD_RUN.read_text())
    aggregate = json.loads(AGGREGATE_RUN.read_text())

    assert certificate["runs"]["children"]["sha256"] == sha(CHILD_RUN)
    assert certificate["runs"]["aggregate"]["sha256"] == sha(AGGREGATE_RUN)
    for imported in certificate["imports"].values():
        assert sha(ROOT / imported["path"]) == imported["sha256"]

    assert children["horizon_remainder_root"] == STABLE_ROOT
    assert not children["threshold_lowered"]
    assert children["all_children_nonzero"]
    assert [entry["panel"] for entry in children["children"]] == [196, 197]
    for entry in children["children"]:
        row = entry["row"]
        assert entry["panel_count"] == 1024
        assert entry["row_sha256"] == canonical_sha(row)
        assert row["boundary_nonvanishing"]["status"] == "PASS"
        assert arb(
            row["physical_mismatch"]["modulus_lower"]
        ).lower() > 0
        typed = typed_row(row)
        assert typed["delta"]["excludes_zero"]
        assert all(typed["interface_gates"].values())

    replacement = aggregate["replacement"]
    assert replacement["removed_parent"] == "98/512"
    assert replacement["inserted_children"] == ["196/1024", "197/1024"]
    assert replacement["same_geometric_interval"]
    segments = aggregate["segments"]
    bounds = [
        (Fraction(segment["start"]), Fraction(segment["stop"]))
        for segment in segments
    ]
    assert bounds[0][0] == 0
    assert all(
        left[1] == right[0] for left, right in zip(bounds, bounds[1:])
    )
    assert bounds[-1][1] == Fraction(99, 512)
    assert len(segments) == 100
    assert all(
        segment["typed_row"]["delta"]["excludes_zero"]
        for segment in segments
    )
    assert aggregate["next_honest_boundary_gap"]["start"] == "99/512"
    assert aggregate["next_honest_boundary_gap"][
        "first_unmaterialized_parent_panel"
    ] == 99
    assert not any(aggregate["closed_claim_gates"].values())

    flags = certificate["claim_flags"]
    assert flags["parent_98_subdivision_repaired"]
    assert flags["both_child_deltas_exclude_zero"]
    assert flags["stable_root_reused"]
    assert not flags["threshold_lowered"]
    assert flags["boundary_prefix_through_99_over_512_certified"]
    for name in (
        "full_contour_nonzero_certified",
        "argument_principle_certified",
        "root_count_certified",
        "QNM_location_certified",
        "Smith_selector_certified",
        "defective_fibre_or_EP2_certified",
    ):
        assert not flags[name]
    print(
        "panel-98 subdivision repair verifier: PASS "
        "(children 196/1024 and 197/1024 nonzero; "
        "next gap 99/512; root/Smith claims fail closed)"
    )


if __name__ == "__main__":
    main()
