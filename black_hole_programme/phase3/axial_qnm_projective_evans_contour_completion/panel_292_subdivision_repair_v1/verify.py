#!/usr/bin/env python3
"""Replayless verifier for the panel-292 dyadic repair."""
from __future__ import annotations

import json
from fractions import Fraction

from flint import arb

from ...axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row
from .produce import CERTIFICATE
from .repair import (
    AGGREGATE,
    CHILDREN,
    CHILD_COUNT,
    CHILD_RUN,
    PREDECESSOR_AGGREGATE,
    PREDECESSOR_CERTIFICATE,
    ROOT,
    STABLE_ROOT,
    canonical_sha,
    sha,
)


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    child_run = json.loads(CHILD_RUN.read_text())
    aggregate = json.loads(AGGREGATE.read_text())
    assert certificate["runs"]["children"]["sha256"] == sha(CHILD_RUN)
    assert certificate["runs"]["aggregate"]["sha256"] == sha(AGGREGATE)
    assert certificate["imports"]["predecessor_certificate"][
        "sha256"
    ] == sha(PREDECESSOR_CERTIFICATE)
    assert certificate["imports"]["predecessor_aggregate"][
        "sha256"
    ] == sha(PREDECESSOR_AGGREGATE)
    for imported in certificate["imports"].values():
        assert sha(ROOT / imported["path"]) == imported["sha256"]

    assert child_run["horizon_remainder_root"] == STABLE_ROOT
    assert not child_run["threshold_lowered"]
    assert child_run["all_children_nonzero"]
    assert [entry["panel"] for entry in child_run["children"]] == list(
        CHILDREN
    )
    for entry in child_run["children"]:
        row = entry["row"]
        assert row["panel_count"] == CHILD_COUNT
        assert entry["row_sha256"] == canonical_sha(row)
        assert row["boundary_nonvanishing"]["status"] == "PASS"
        assert arb(
            row["physical_mismatch"]["modulus_lower"]
        ).lower() > 0
        typed = typed_row(row)
        assert typed["delta"]["excludes_zero"]
        assert all(typed["interface_gates"].values())

    assert aggregate["replacement"]["removed_parent"] == "292/1024"
    assert aggregate["replacement"]["inserted_children"] == [
        "584/2048", "585/2048"
    ]
    assert aggregate["replacement"]["same_geometric_interval"]
    bounds = [
        (Fraction(segment["start"]), Fraction(segment["stop"]))
        for segment in aggregate["segments"]
    ]
    assert bounds[0][0] == 0
    assert all(
        left[1] == right[0] for left, right in zip(bounds, bounds[1:])
    )
    assert bounds[-1][1] == Fraction(293, 1024)
    assert aggregate["summary"]["contiguous_from_zero"]
    assert aggregate["summary"]["all_materialized_deltas_exclude_zero"]
    assert aggregate["summary"]["two_sided_interface_gates_pass"]
    assert aggregate["next_honest_boundary_gap"]["start"] == "293/1024"
    assert not any(aggregate["closed_claim_gates"].values())

    flags = certificate["claim_flags"]
    assert flags["parent_292_subdivision_repaired"]
    assert flags["both_child_deltas_exclude_zero"]
    assert flags["stable_root_reused"]
    assert not flags["threshold_lowered"]
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
        "Evans panel-292 dyadic repair verifier: PASS "
        "(children 584/2048 and 585/2048; next gap 293/1024)"
    )


if __name__ == "__main__":
    main()
