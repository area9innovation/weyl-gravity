#!/usr/bin/env python3
"""Independent hash-only verifier for the adaptive dyadic chunk."""
from __future__ import annotations

import json
from fractions import Fraction

from flint import arb

from ..axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row
from .adaptive import (
    AGGREGATE_RUN,
    HERE,
    RAW_RUN,
    ROOT,
    STABLE_ROOT,
    canonical_sha,
    sha,
)

CERT = HERE / "certificate.json"


def main() -> None:
    certificate = json.loads(CERT.read_text())
    raw = json.loads(RAW_RUN.read_text())
    aggregate = json.loads(AGGREGATE_RUN.read_text())
    assert certificate["runs"]["raw"]["sha256"] == sha(RAW_RUN)
    assert certificate["runs"]["aggregate"]["sha256"] == sha(AGGREGATE_RUN)
    for imported in certificate["imports"].values():
        assert sha(ROOT / imported["path"]) == imported["sha256"]
    assert raw["elapsed_compute_seconds"] < 60
    assert raw["horizon_remainder_root"] == STABLE_ROOT
    assert not raw["threshold_lowered"]
    for entry in raw["observations"]:
        assert entry["row_sha256"] == canonical_sha(entry["row"])
    for entry in raw["accepted_segments"]:
        assert entry["row"]["boundary_nonvanishing"]["status"] == "PASS"
        assert arb(
            entry["row"]["physical_mismatch"]["modulus_lower"]
        ).lower() > 0
        typed = typed_row(entry["row"])
        assert typed["delta"]["excludes_zero"]
        assert all(typed["interface_gates"].values())

    segments = aggregate["segments"]
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in segments
    ]
    assert bounds[0][0] == 0
    assert all(
        left[1] == right[0] for left, right in zip(bounds, bounds[1:])
    )
    assert bounds[-1][1] == Fraction(
        aggregate["summary"]["coverage_stop"]
    )
    assert aggregate["summary"]["all_materialized_deltas_exclude_zero"]
    assert aggregate["summary"]["two_sided_interface_gates_pass"]
    assert not any(aggregate["closed_claim_gates"].values())
    flags = certificate["claim_flags"]
    assert flags["adaptive_ordered_chunk_materialized"]
    assert flags["materialized_prefix_nonzero_certified"]
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
        "adaptive dyadic boundary verifier: PASS "
        f"(coverage {aggregate['summary']['coverage_stop']}; "
        f"terminal {raw['terminal']['code']}; root/Smith fail closed)"
    )


if __name__ == "__main__":
    main()
