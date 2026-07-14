#!/usr/bin/env python3
"""Verify the Weyl--Cotton generalized block Green witness."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.weyl_cotton_block_green_witness import (
    WeylCottonBlockGreenWitness,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_block_green_witness.json"
)


def _must_fail(candidate: WeylCottonBlockGreenWitness, label: str) -> None:
    try:
        candidate.verify()
    except AssertionError:
        return
    raise AssertionError(f"negative guard did not fail: {label}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    witness = WeylCottonBlockGreenWitness.build()
    certificate = witness.certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))

    if args.guards:
        identities = certificate["exact_block_identities"]
        if not identities["P_equals_QW_plus_WQ"]:
            raise AssertionError("block witness identity regressed")
        if not identities["Q_P_equals_P_Q"]:
            raise AssertionError("chain commutation regressed")
        if not certificate["compatibility_complex"]["curved_unit_S3_correction_included"]:
            raise AssertionError("curved sourced correction was omitted")
        if not certificate["canonical_source_identification"][
            "K_and_R_coefficient_tables_equal"
        ]:
            raise AssertionError("K/R coefficient identification regressed")
        if not certificate["missing_for_complete_prolonged_BV_witness"]:
            raise AssertionError("full-BV boundary was hidden")
        for flag in (
            "prolonged_BV_operator_identity",
            "prolonged_green_witness",
            "curvature_causal_green_operators",
            "causal_green_homotopy",
        ):
            if certificate[flag]:
                raise AssertionError(f"kernel audit overpromoted {flag}")

        bad_expected = [row[:] for row in witness.expected_witness_operator]
        bad_expected[0][0] = bad_expected[0][0].scale(2)
        _must_fail(
            replace(witness, expected_witness_operator=bad_expected),
            "P=QW+WQ normalization",
        )
        _must_fail(
            replace(witness, source_table_sha256="0" * 64),
            "K/R coefficient mismatch",
        )
        print("WEYL-COTTON BLOCK GREEN WITNESS GUARDS: 11/11 PASS")

    print(
        "WEYL-COTTON BLOCK GREEN WITNESS: ANALYTIC KERNEL EXACT; "
        "COMPLETE PROLONGED BV INTEGRATION OPEN"
    )


if __name__ == "__main__":
    main()
