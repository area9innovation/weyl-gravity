#!/usr/bin/env python3
"""Verify the exhaustive curved Weyl/Cotton two-jet comparison."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.curvature_eb_jets import (
    CurvedWeylCottonJetComparison,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_jet_comparison.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    certificate = CurvedWeylCottonJetComparison.build().certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))
    if args.guards:
        if not certificate["coverage_complete"]:
            raise AssertionError("curved Weyl/Cotton jet coverage is incomplete")
        for defect in (
            "algebraic_weyl_defects",
            "cotton_coordinate_defects",
            "cotton_reconstruction_defects",
            "bach_coordinate_defects",
        ):
            if certificate[defect] != 0:
                raise AssertionError(f"curved jet defect did not vanish: {defect}")
        if not certificate["curved_EB_equations"]:
            raise AssertionError("exact curved E/B equations were not promoted")
        if not certificate["curved_EB_first_order_closure"]:
            raise AssertionError("exact rank-26 first-order closure was not promoted")
        for open_claim in (
            "symmetric_hyperbolicity_proved",
            "sourced_constraint_identity_proved",
            "EAL_curvature_spectrum_match",
        ):
            if certificate[open_claim]:
                raise AssertionError(f"curved jet comparison overclaimed {open_claim}")
        print("CURVED WEYL/COTTON JET GUARDS: 11/11 PASS")
    print("CURVED WEYL/COTTON JETS: EXACT TWO-JET COMPARISON CERTIFIED")


if __name__ == "__main__":
    main()
