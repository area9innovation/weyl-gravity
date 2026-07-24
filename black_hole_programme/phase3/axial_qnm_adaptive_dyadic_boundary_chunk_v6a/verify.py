#!/usr/bin/env python3
"""Independent structural verifier for the bounded v6a observation."""
from __future__ import annotations

import json
from fractions import Fraction

from .runner import (
    AGG,
    CERT,
    PREDECESSOR_AGG,
    PREDECESSOR_CERT,
    RAW,
    sha,
)


def main() -> None:
    certificate = json.loads(CERT.read_text())
    raw = json.loads(RAW.read_text())
    aggregate = json.loads(AGG.read_text())
    predecessor = json.loads(PREDECESSOR_AGG.read_text())

    assert certificate["runs"]["raw"]["sha256"] == sha(RAW)
    assert certificate["runs"]["aggregate"]["sha256"] == sha(AGG)
    assert (
        certificate["imports"]["predecessor_certificate"]["sha256"]
        == sha(PREDECESSOR_CERT)
    )
    assert (
        certificate["imports"]["predecessor_aggregate"]["sha256"]
        == sha(PREDECESSOR_AGG)
    )
    assert Fraction(predecessor["summary"]["coverage_stop"]) == Fraction(
        104, 512
    )
    assert raw["requested_parent_range"] == [104, 104]
    assert raw["threshold_lowered"] is False
    assert len(raw["observations"]) == 1
    observation = raw["observations"][0]
    assert observation["kind"] == "parent_observation"
    assert observation["panel"] == 104
    assert observation["panel_count"] == 512
    assert not any(
        item["kind"] == "repair_child" for item in raw["observations"]
    )

    passed = (
        observation["row"]["boundary_nonvanishing"]["status"] == "PASS"
    )
    assert raw["accepted_segments"] == ([{
        **observation,
        "kind": "accepted_parent",
    }] if passed else [])
    expected_coverage = Fraction(105, 512) if passed else Fraction(104, 512)
    assert Fraction(aggregate["summary"]["coverage_stop"]) == expected_coverage
    disposition = certificate["result"]["coverage_disposition"]
    assert disposition["accepted_parent"] is passed
    assert disposition["children_launched"] is False
    assert Fraction(disposition["coverage_stop"]) == expected_coverage
    assert certificate["claim_flags"]["parent_104_nonzero_certified"] is passed
    assert certificate["claim_flags"]["children_launched"] is False
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
        "v6a verifier: PASS "
        f"(parent 104 status={disposition['parent_status']}; "
        f"coverage={disposition['coverage_stop']}; no children)"
    )


if __name__ == "__main__":
    main()
