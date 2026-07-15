#!/usr/bin/env python3
"""Verify the exact sensitivity-first screen for pairs (1,7) and (2,7)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_incidence_screen import (  # noqa: E402
    ExpandedRelativeIncidenceScreen,
)


OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_incidence_screen.json"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-strong-hyperbolicity", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    args = parser.parse_args()
    if args.claim_strong_hyperbolicity or args.claim_green:
        raise SystemExit(
            "REFUSED: the nonzero R7sharp sensitivity keeps pairs (1,7) and "
            "(2,7) alive, but does not select coefficients, assemble a regular "
            "polynomial, prove semisimplicity, or construct Green operators"
        )

    screen = ExpandedRelativeIncidenceScreen.build()
    certificate = screen.certificate()
    sensitivity = certificate["intrinsic_Jordan_obstruction_sensitivity"]
    result = certificate["screening_result"]
    checks = {
        "minimal_incidence_list_complete": certificate[
            "complete_minimal_incidence_list"
        ]["complete"],
        "temporal_family_complete": certificate[
            "complete_first_order_R7sharp_family"
        ]["temporal_nullity"] == 36,
        "spatial_family_complete": certificate[
            "complete_first_order_R7sharp_family"
        ]["spatial_nullity"] == 86,
        "temporal_sensitivity_nonzero": sensitivity["temporal_rank"] == 8,
        "spatial_sensitivity_nonzero": sensitivity["spatial_rank"] == 8,
        "joint_sensitivity_nonzero": sensitivity["joint_rank"] == 16,
        "pair17_survives_screen": not result[
            "pair_1_plus_7_rejected_by_zero_sensitivity"
        ],
        "pair27_survives_screen": not result[
            "pair_2_plus_7_rejected_by_zero_sensitivity"
        ],
        "no_hyperbolicity_overclaim": (
            not certificate["strong_hyperbolicity_pair_1_plus_7"]
            and not certificate["strong_hyperbolicity_pair_2_plus_7"]
            and not certificate["prolonged_green_witness"]
            and not certificate["status_flags_promoted"]
        ),
        "fail_closed": certificate["fail_closed"],
    }

    if args.guards:
        mutated = sp.zeros(*screen.joint_sensitivity.shape)
        checks["mutated_sensitivity_rejected"] = (
            mutated != screen.joint_sensitivity
            and mutated.rank() != screen.joint_sensitivity.rank()
        )

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"alternative-incidence screen checks failed: {failed}")

    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print("=== Expanded relative alternative-incidence screen ===")
    for name, passed in checks.items():
        print(f"{name}: {passed}")
    print(f"certificate: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
