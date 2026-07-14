#!/usr/bin/env python3
"""Verify the all-level E/A/L spectrum of the Weyl--Cotton equations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.curvature_eal_spectrum import (
    AllLevelCurvatureEALSpectrum,
)


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATE_DIR / "curved_EAL_spectrum_all_level.json"
JET = CERTIFICATE_DIR / "curved_weyl_cotton_jet_comparison.json"
PREIMAGES = ROOT / "bridge" / "certificates" / "cylinder_metric_preimages.json"
BGG = ROOT / "bridge" / "certificates" / "cylinder_bgg_blocks.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    proof = AllLevelCurvatureEALSpectrum.build(
        jet_certificate=_load(JET),
        preimage_certificate=_load(PREIMAGES),
        bgg_certificate=_load(BGG),
    )
    certificate = proof.certificate()
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))
    if args.guards:
        checks = (
            certificate["all_level_not_finite_cutoff"],
            certificate["equation_bridge"]["exact_26_state_covariant_equivalence"],
            certificate["cotton_prolongation"]["cotton_unique_no_duplication"],
            certificate["global_exhaustion"]["global_BGG_exhaustion"],
            certificate["chirality"]["both_chiralities"],
            certificate["symbolic_character"]["identity_all_coefficients"],
            certificate["EAL_curvature_spectrum_match"],
            certificate["status_ledger_modified"] is False,
            certificate["low_level_regression"]["physical_dimensions"]
            == [10, 40, 82, 136, 202],
        )
        if not all(checks):
            raise AssertionError("all-level curvature E/A/L guard failed")
        if not certificate["fail_closed"]:
            raise AssertionError("all-level curvature spectrum is not fail closed")
        print("CURVED E/A/L ALL-LEVEL GUARDS: 10/10 PASS")
    print("CURVED E/A/L SPECTRUM: SYMBOLIC ALL-LEVEL ISOMORPHISM CERTIFIED")


if __name__ == "__main__":
    main()
