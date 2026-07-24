#!/usr/bin/env python3
"""Independently verify the lifted-phase prefix ledger."""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from black_hole_programme.phase3.axial_qnm_projective_evans_contour_completion.phase_ledger_v1.produce import (
        AGGREGATE,
        CERTIFICATE,
        CURRENT_CERT,
        LEDGER,
        ROOT,
        TYPED_SOURCE,
        directions,
        sha,
    )
    from black_hole_programme.phase3.axial_qnm_horizon_reciprocal_checkpoint_transport_v1.checkpoint_transport import (
        parse_acb,
    )
else:
    from .produce import (
        AGGREGATE,
        CERTIFICATE,
        CURRENT_CERT,
        LEDGER,
        ROOT,
        TYPED_SOURCE,
        directions,
        sha,
    )
    from ...axial_qnm_horizon_reciprocal_checkpoint_transport_v1.checkpoint_transport import (
        parse_acb,
    )


def main() -> None:
    ctx.prec = 128
    certificate = json.loads(CERTIFICATE.read_text())
    ledger = json.loads(LEDGER.read_text())
    aggregate = json.loads(AGGREGATE.read_text())
    assert certificate["artifact"]["sha256"] == sha(LEDGER)
    assert certificate["imports"]["certificate"]["sha256"] == sha(
        CURRENT_CERT
    )
    assert certificate["imports"]["aggregate"]["sha256"] == sha(AGGREGATE)
    assert certificate["imports"]["typed_row_implementation"][
        "sha256"
    ] == sha(TYPED_SOURCE)
    assert len(ledger["segments"]) == len(aggregate["segments"]) == 172
    assert ledger["summary"]["coverage_stop"] == "135/512"
    assert ledger["summary"]["contiguous_from_zero"]
    assert arb(
        ledger["summary"]["minimum_normalized_half_plane_margin"]["lower"]
    ).lower() > 0
    assert arb(
        ledger["summary"]["maximum_argument_sector_width"]["upper"]
    ).upper() < arb.pi().lower()
    assert arb(
        ledger["summary"]["minimum_adjacent_sector_overlap"]["lower"]
    ).lower() > 0
    previous = None
    for source, record in zip(aggregate["segments"], ledger["segments"]):
        assert record["source_row_sha256"] == source.get(
            "source_row_sha256"
        )
        assert Fraction(record["start"]) == Fraction(
            source["typed_row"]["panel"],
            source["typed_row"]["panel_count"],
        )
        assert Fraction(record["stop"]) > Fraction(record["start"])
        center = parse_acb(record["delta_center"])
        radius = arb(record["reconstructed_radius_upper"])
        index = record["separator"]["direction_index"]
        real, imag = directions()[index]
        assert [real, imag] == record["separator"]["integer_vector"]
        norm_upper = arb(real * real + imag * imag).sqrt().upper()
        margin = (
            real * center.real + imag * center.imag
        ).lower() - norm_upper * radius
        assert margin.lower() > 0
        assert arb(record["separator"]["half_plane_margin_lower"]).lower() > 0
        sector = record["argument_sector"]
        lower = arb(sector["unwrapped_lower"])
        upper = arb(sector["unwrapped_upper"])
        assert upper.lower() > lower.upper()
        assert upper - lower < arb.pi()
        if previous is not None:
            overlap_lower = max(previous[0].lower(), lower.lower())
            overlap_upper = min(previous[1].upper(), upper.upper())
            assert overlap_upper > overlap_lower
            overlap = record["previous_sector_overlap"]
            assert overlap is not None and overlap["certified_nonempty"]
        previous = (lower, upper)
    for key in (
        "full_closed_contour_certified",
        "winding_number_certified",
        "argument_principle_root_count_certified",
        "QNM_or_EP2_certified",
    ):
        assert not ledger["claim_flags"][key]
        assert not certificate["claim_flags"][key]
    print(
        "Evans lifted-phase ledger verifier: PASS "
        "(172 segments; coverage 135/512; contour remains open)"
    )


if __name__ == "__main__":
    main()
