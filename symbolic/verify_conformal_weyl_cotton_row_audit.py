#!/usr/bin/env python3
"""Audit adjusted Weyl--Cotton rows against the exact covariant 34-row system."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.weyl_cotton_row_audit import (
    WeylCottonRowReductionAudit,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_weyl_cotton_row_audit.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    audit = WeylCottonRowReductionAudit.build()
    certificate = audit.certificate()
    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", CERTIFICATE.relative_to(ROOT))
    if args.guards:
        checks = {
            "first twenty exact": certificate[
                "first_twenty_adjusted_rows_are_exact_covariant_combinations"
            ],
            "exact lower terms": certificate["first_twenty_lower_order_covariant"],
            "vector rows distinct": not certificate[
                "adjusted_vector_rows_are_covariant_Bach_row_combinations"
            ],
            "six additional constraints": certificate["additional_constraint_rank"]
            == 6,
            "eight insufficient": not certificate[
                "row_equivalent_modulo_original_eight_constraints"
            ],
            "rank-six defect": certificate["exact_defect_rank"] == 6,
            "no status promotion": certificate["status_flags_promoted"] == [],
        }
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            raise AssertionError(f"Weyl--Cotton row-audit guards failed: {failed}")
        print(f"WEYL--COTTON ROW AUDIT GUARDS: {len(checks)}/{len(checks)} PASS")
    print(
        "WEYL--COTTON ROW AUDIT: FIRST 20 EXACT; VECTOR BACH REPLACEMENT "
        "HAS RANK-6 DEFECT MODULO THE ORIGINAL EIGHT CONSTRAINTS"
    )


if __name__ == "__main__":
    main()
