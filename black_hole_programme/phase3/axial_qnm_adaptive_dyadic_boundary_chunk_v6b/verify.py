#!/usr/bin/env python3
"""Independent structural verifier for the v6b child-only repair."""
from __future__ import annotations

import json
from fractions import Fraction

from flint import arb

from .runner import (
    AGG,
    CERT,
    CHILDREN,
    PREDECESSOR_AGG,
    PREDECESSOR_CERT,
    PREDECESSOR_RAW,
    RAW,
    core,
    sha,
)


def main() -> None:
    certificate = json.loads(CERT.read_text())
    raw = json.loads(RAW.read_text())
    aggregate = json.loads(AGG.read_text())
    predecessor_raw = json.loads(PREDECESSOR_RAW.read_text())
    predecessor_aggregate = json.loads(PREDECESSOR_AGG.read_text())

    assert certificate["runs"]["raw"]["sha256"] == sha(RAW)
    assert certificate["runs"]["aggregate"]["sha256"] == sha(AGG)
    for label, path in (
        ("predecessor_certificate", PREDECESSOR_CERT),
        ("predecessor_raw", PREDECESSOR_RAW),
        ("predecessor_aggregate", PREDECESSOR_AGG),
    ):
        assert certificate["imports"][label]["sha256"] == sha(path)
    assert Fraction(
        predecessor_aggregate["summary"]["coverage_stop"]
    ) == Fraction(104, 512)
    assert len(predecessor_raw["observations"]) == 1
    parent = predecessor_raw["observations"][0]
    assert parent["panel"] == 104
    assert parent["panel_count"] == 512
    assert parent["row_sha256"] == core.canonical_sha(parent["row"])
    assert (
        parent["row"]["boundary_nonvanishing"]["status"] == "FAIL_CLOSED"
    )
    assert certificate["parent_hash_linkage"]["source_raw_sha256"] == sha(
        PREDECESSOR_RAW
    )
    assert certificate["parent_hash_linkage"]["parent_row_sha256"] == parent[
        "row_sha256"
    ]
    assert (
        certificate["parent_hash_linkage"]["canonical_parent_row_sha256"]
        == parent["row_sha256"]
    )

    assert raw["threshold_lowered"] is False
    assert raw["requested_child_segments"] == ["208/1024", "209/1024"]
    assert len(raw["observations"]) == 3
    imported, *children = raw["observations"]
    assert imported["kind"] == "imported_parent_observation"
    assert imported["source_raw_sha256"] == sha(PREDECESSOR_RAW)
    assert tuple(entry["panel"] for entry in children) == CHILDREN
    assert all(entry["panel_count"] == 1024 for entry in children)
    assert all(entry["kind"] == "repair_child" for entry in children)
    assert all(
        entry["row_sha256"] == core.canonical_sha(entry["row"])
        for entry in children
    )
    passes = [
        entry["row"]["boundary_nonvanishing"]["status"] == "PASS"
        and arb(
            entry["row"]["physical_mismatch"]["modulus_lower"]
        ).lower() > 0
        for entry in children
    ]
    repaired = all(passes)
    assert len(raw["accepted_segments"]) == (2 if repaired else 0)
    expected_stop = Fraction(105, 512) if repaired else Fraction(104, 512)
    assert Fraction(aggregate["summary"]["coverage_stop"]) == expected_stop
    assert aggregate["summary"]["contiguous_from_zero"] is True
    assert aggregate["summary"]["all_materialized_deltas_exclude_zero"] is True
    assert certificate["claim_flags"][
        "children_208_209_nonzero_certified"
    ] is repaired
    assert certificate["claim_flags"]["threshold_lowered"] is False
    assert certificate["claim_flags"]["only_children_208_209_evaluated"] is True
    for flag in (
        "full_contour_nonzero_certified",
        "argument_principle_certified",
        "root_count_certified",
        "QNM_location_certified",
        "Smith_selector_certified",
        "defective_fibre_or_EP2_certified",
    ):
        assert certificate["claim_flags"][flag] is False
    assert not any(aggregate["closed_claim_gates"].values())
    print(
        "v6b verifier: PASS "
        f"(children 208/209 pass={passes}; "
        f"coverage={aggregate['summary']['coverage_stop']})"
    )


if __name__ == "__main__":
    main()
