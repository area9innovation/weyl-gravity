#!/usr/bin/env python3
"""Hash-only verifier for adaptive continuation v3."""
from __future__ import annotations

import json
from fractions import Fraction

from flint import arb

from .continuation import (
    AGGREGATE_RUN, HERE, RAW_RUN, ROOT, STABLE_ROOT, canonical_sha, sha,
)

CERT = HERE / "certificate.json"


def main() -> None:
    cert = json.loads(CERT.read_text())
    raw = json.loads(RAW_RUN.read_text())
    aggregate = json.loads(AGGREGATE_RUN.read_text())
    assert cert["runs"]["raw"]["sha256"] == sha(RAW_RUN)
    assert cert["runs"]["aggregate"]["sha256"] == sha(AGGREGATE_RUN)
    for imported in cert["imports"].values():
        assert sha(ROOT / imported["path"]) == imported["sha256"]
    assert raw["elapsed_compute_seconds"] < 60
    assert raw["horizon_remainder_root"] == STABLE_ROOT
    assert not raw["threshold_lowered"]
    imported = raw["observations"][0]
    assert imported["kind"] == "imported_parent_observation"
    assert imported["parent_panel"] == 101
    assert imported["row_sha256"] == canonical_sha(imported["row"])
    for entry in raw["accepted_segments"]:
        assert entry["row_sha256"] == canonical_sha(entry["row"])
        assert entry["row"]["boundary_nonvanishing"]["status"] == "PASS"
        assert arb(
            entry["row"]["physical_mismatch"]["modulus_lower"]
        ).lower() > 0
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in aggregate["segments"]
    ]
    assert all(
        left[1] == right[0] for left, right in zip(bounds, bounds[1:])
    )
    assert bounds[-1][1] == Fraction(
        aggregate["summary"]["coverage_stop"]
    )
    assert aggregate["summary"]["all_materialized_deltas_exclude_zero"]
    assert not any(aggregate["closed_claim_gates"].values())
    for name in (
        "root_count_certified", "QNM_location_certified",
        "Smith_selector_certified", "defective_fibre_or_EP2_certified",
    ):
        assert not cert["claim_flags"][name]
    print(
        "adaptive dyadic boundary v3 verifier: PASS "
        f"(coverage {aggregate['summary']['coverage_stop']}; "
        f"next {aggregate['next_honest_boundary_gap']['start']})"
    )


if __name__ == "__main__":
    main()
