#!/usr/bin/env python3
"""Independently verify the closed-contour winding certificate."""
from __future__ import annotations

import json
from fractions import Fraction

from flint import arb, ctx

from .produce import (
    AGGREGATE,
    ANALYTIC,
    CERTIFICATE,
    ECS,
    FINAL_CERT,
    LEDGER,
    LEDGER_CERT,
    ROOT,
    sha,
)


def main() -> None:
    ctx.prec = 128
    certificate = json.loads(CERTIFICATE.read_text())
    ledger = json.loads(LEDGER.read_text())
    ledger_cert = json.loads(LEDGER_CERT.read_text())
    aggregate = json.loads(AGGREGATE.read_text())
    final_cert = json.loads(FINAL_CERT.read_text())
    analytic = json.loads(ANALYTIC.read_text())
    ecs = json.loads(ECS.read_text())

    for item in certificate["imports"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert ledger_cert["artifact"]["sha256"] == sha(LEDGER)
    assert Fraction(ledger["summary"]["coverage_start"]) == 0
    assert Fraction(ledger["summary"]["coverage_stop"]) == 1
    assert Fraction(aggregate["summary"]["coverage_stop"]) == 1
    assert Fraction(final_cert["result"]["coverage_stop"]) == 1
    assert ledger["summary"]["contiguous_from_zero"]
    assert aggregate["summary"]["all_materialized_deltas_exclude_zero"]
    assert aggregate["summary"]["two_sided_interface_gates_pass"]
    assert arb(
        ledger["summary"]["minimum_normalized_half_plane_margin"]["lower"]
    ).lower() > 0
    assert arb(
        ledger["summary"]["minimum_adjacent_sector_overlap"]["lower"]
    ).lower() > 0
    assert analytic["claim_flags"]["no_branch_points_axial_certified"]
    assert analytic["axial_analytic_continuation"]["mode_families"][
        "boundary_exponents_entire_in_omega"
    ]
    assert ecs["volterra"]["uniform_contraction_on_closed_disk"]
    assert "uniformly convergent Neumann series" in ecs["volterra"][
        "analytic_frequency_dependence"
    ]

    first = ledger["segments"][0]["argument_sector"]
    last = ledger["segments"][-1]["argument_sector"]
    first_lower = arb(first["unwrapped_lower"]).lower()
    first_upper = arb(first["unwrapped_upper"]).upper()
    last_lower = arb(last["unwrapped_lower"]).lower()
    last_upper = arb(last["unwrapped_upper"]).upper()
    winding = certificate["result"]["winding_number"]
    assert isinstance(winding, int)
    assert winding == (
        int(last["branch_shift"]) - int(first["branch_shift"])
    )
    shift = 2 * arb.pi() * winding
    overlap_lower = max(last_lower, first_lower + shift.lower())
    overlap_upper = min(last_upper, first_upper + shift.upper())
    overlap_width = overlap_upper - overlap_lower
    assert overlap_width.lower() > 0
    total_width = (
        first_upper - first_lower + last_upper - last_lower
    ).upper()
    assert total_width < (2 * arb.pi()).lower()
    assert arb(
        certificate["result"]["closing_sector_overlap"]["width_lower"]
    ).lower() > 0
    phase = ledger["summary"]["partial_argument_increment_enclosure"]
    assert arb(phase["lower"]).lower() <= shift.lower()
    assert arb(phase["upper"]).upper() >= shift.upper()
    assert certificate["domain"]["orientation"] == "counterclockwise"
    assert winding == 1
    assert certificate["result"][
        "argument_principle_root_count_with_multiplicity"
    ] == 1
    assert certificate["result"]["unique_simple_root"]
    for key in (
        "full_closed_contour_nonzero_certified",
        "closing_sector_compatibility_certified",
        "winding_number_certified",
        "argument_principle_root_count_certified",
        "unique_simple_spin_two_QNM_in_disk_certified",
    ):
        assert certificate["claim_flags"][key]
    for key in (
        "QNM_location_certified",
        "intrinsic_tangent_selector_certified",
        "Smith_selector_certified",
        "defective_fibre_or_EP2_certified",
        "Green_resolvent_double_pole_certified",
    ):
        assert not certificate["claim_flags"][key]
    print(
        "Axial projective Evans full-contour winding verifier: PASS "
        "(winding +1; exactly one simple spin-two QNM in disk)"
    )


if __name__ == "__main__":
    main()

