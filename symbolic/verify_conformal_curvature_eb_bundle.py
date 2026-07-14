#!/usr/bin/env python3
"""Verify the exact algebraic Weyl electric/magnetic bundle isomorphism."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator import WeylElectricMagneticBundle


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_curvature_eb_bundle.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    certificate = WeylElectricMagneticBundle.build().certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))
    if args.guards:
        required_true = (
            "reconstruction_and_extraction_are_inverse",
            "weyl_symmetries_verified",
            "algebraic_Bianchi_verified",
            "trace_free_verified",
        )
        for name in required_true:
            if not certificate[name]:
                raise AssertionError(f"electric/magnetic bundle guard failed: {name}")
        if certificate["hodge_action"] != "star(E,B)=(B,-E)":
            raise AssertionError("electric/magnetic Hodge sign drifted")
        if certificate["hodge_square"] != "-identity":
            raise AssertionError("Lorentzian Hodge square drifted")
        if certificate["field_equations_claimed"]:
            raise AssertionError("algebraic bundle map inferred field equations")
        if certificate["curved_EB_equations"]:
            raise AssertionError("algebraic bundle map promoted curved equations")
        print("CURVATURE E/B BUNDLE GUARDS: 8/8 PASS")
    print("CURVATURE E/B BUNDLE: EXACT ALGEBRAIC ISOMORPHISM CERTIFIED")


if __name__ == "__main__":
    main()
