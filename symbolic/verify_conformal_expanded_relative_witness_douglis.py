#!/usr/bin/env python3
"""Verify the actual pair-(1,6) central temporal Douglis matrix."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_douglis import (
    ExpandedRelativeDouglisCandidate,
)


OUTPUT = ROOT / "covariant_completion/certificates/curved_expanded_relative_witness_douglis.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--claim-symmetrizer", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if args.claim_green or args.claim_symmetrizer or args.promote_flag:
        raise SystemExit(
            "REFUSED: temporal Douglis invertibility alone does not prove a "
            "causal characteristic polynomial, symmetrizer, or Green witness"
        )
    candidate = ExpandedRelativeDouglisCandidate.build()
    certificate = candidate.certificate()
    diagonal = certificate["actual_curvature_temporal_diagonal"]
    schur = certificate["actual_pair16_Schur_term"]
    complete = certificate["assembled_temporal_Douglis_symbol"]
    boundary = certificate["scope_and_open_work"]
    checks = {
        "actual_D_rank92": diagonal["rank"] == 92
        and diagonal["formula"] == "diag(+I_26,-I_40,-I_26)",
        "actual_D_inverse": diagonal["inverse_equals_itself"],
        "actual_BDinvC": schur["defect"] == 0
        and schur["equals_minus_vector_gauge_projector"],
        "actual_order2": schur["differential_order"] == 2,
        "full_rank116": complete["rank"] == 116
        and complete["rank_defect"] == 0,
        "determinant1": complete["determinant"] == 1,
        "intertwining_cross_reference": boundary["SO3_intertwining_certificate"]
        == "curved_expanded_relative_witness_commutant.json",
        "open_work_fail_closed": not any(
            value
            for key, value in boundary.items()
            if key != "SO3_intertwining_certificate"
        ),
        "no_flag": certificate["fail_closed"]
        and not certificate["status_flags_promoted"],
    }
    if args.guards:
        broken_d = candidate.curvature_temporal_diagonal.copy()
        broken_d[0, 0] = 0
        broken = replace(candidate, curvature_temporal_diagonal=broken_d)
        try:
            broken.verify()
        except AssertionError:
            checks["singular_D_rejected"] = True
        else:
            checks["singular_D_rejected"] = False
    if not all(checks.values()):
        raise AssertionError({key: value for key, value in checks.items() if not value})
    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    if args.emit:
        print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
