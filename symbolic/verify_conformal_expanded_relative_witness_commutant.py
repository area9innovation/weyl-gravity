#!/usr/bin/env python3
"""Verify the coefficientwise SO(3) relative-witness commutants."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_commutant import (
    ExpandedRelativeWitnessCommutant,
)


OUTPUT = ROOT / "covariant_completion/certificates/curved_expanded_relative_witness_commutant.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--claim-douglis", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    if args.claim_green or args.claim_douglis or args.promote_flag:
        raise SystemExit(
            "REFUSED: rotation commutants and a temporal numerator do not "
            "construct a Douglis symbol or Green witness"
        )

    audit = ExpandedRelativeWitnessCommutant.build()
    certificate = audit.certificate()
    hom = certificate["relative_Hom_commutants"]
    pair = certificate["pair_1_plus_6_coefficients"]
    outcome = certificate["outcome"]
    checks = {
        "sixteen_blocks": len(certificate["rotation_generators"]["block_sizes"]) == 16,
        "hom_dimension_162": hom["total_dimension"] == 162,
        "expected_ledger": hom["nullities"] == [4, 18, 4, 36, 14, 14, 22, 36, 14],
        "pair16_intertwines": pair["coefficientwise_SO3_intertwiners"] and not any(
            value for key, value in pair.items() if key.endswith("_defect")
        ),
        "fail_closed": (
            certificate["fail_closed"]
            and not outcome["full_Douglis_symbol_assembled"]
            and not outcome["green_realization_proved"]
            and not outcome["flag_promoted"]
        ),
    }
    if not all(checks.values()):
        raise AssertionError({key: value for key, value in checks.items() if not value})
    if args.guards:
        broken = replace(
            audit,
            r1_defect=1,
        )
        try:
            broken.verify()
        except AssertionError:
            checks["broken_R1_intertwiner_rejected"] = True
        else:
            raise AssertionError("a mutated pair-(1,6) intertwiner was accepted")
    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    if args.emit:
        print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
