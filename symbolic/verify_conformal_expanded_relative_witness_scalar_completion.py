#!/usr/bin/env python3
"""Verify the exact scalar completion of the expanded relative witness."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_scalar_completion import (
    ExpandedRelativeScalarCompletion,
)


OUTPUT = ROOT / "covariant_completion/certificates/curved_expanded_relative_witness_scalar_completion.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--claim-symmetric-hyperbolic", action="store_true")
    parser.add_argument("--claim-rank116", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if (
        args.claim_green
        or args.claim_symmetric_hyperbolic
        or args.claim_rank116
        or args.promote_flag
    ):
        raise SystemExit(
            "REFUSED: the verified pair-(1,6) product is the numerator B C, "
            "not B D^-1 C; no 116-rank, symmetrizer, or Green claim follows"
        )
    completion = ExpandedRelativeScalarCompletion.build()
    certificate = completion.certificate()
    scalar = certificate["minimal_support_local_scalar_diagonal"]
    target = certificate["algebraic_numerator_target"]
    boundary = certificate["analytic_boundary"]
    checks = {
        "missing_scalars_exact": certificate["exact_missing_scalar_directions"] == ["h_00", "f_00", "v_0"],
        "minimal_scalar_rank3": scalar["rank"] == 3 and scalar["determinant"] == -1,
        "pair16_orders": certificate["pair_1_plus_6_explicit_temporal_maps"]["relative_orders"] == {"R1": 0, "R6": 1},
        "actual_Ncurv_table": certificate["pair_1_plus_6_explicit_temporal_maps"]["certified_Ncurv_temporal_matrix"] == "[0_(14x26),I_14]",
        "coefficientwise_pair16_product": certificate["pair_1_plus_6_explicit_temporal_maps"]["coefficientwise_product_defect"] == 0,
        "algebraic_target_only": target["formal_target_rank"] == 24
        and target["formal_target_determinant"] == 1
        and not target["is_actual_saddle_Schur_complement"],
        "curvature_inverse_missing": target["missing_factor"].startswith("inverse of the actual 92x92"),
        "no_rank116_claim": "complete_temporal_rank" not in target,
        "analytic_boundary_open": not any(boundary.values()),
        "fail_closed": certificate["fail_closed"] and not certificate["status_flags_promoted"],
    }
    if not all(checks.values()):
        raise AssertionError({key: value for key, value in checks.items() if not value})
    if args.guards:
        broken = replace(
            completion,
            relative_r1_temporal=completion.relative_r1_temporal * 0,
        )
        try:
            broken.verify()
        except AssertionError:
            checks["broken_R1_rejected"] = True
        else:
            checks["broken_R1_rejected"] = False
        if not checks["broken_R1_rejected"]:
            raise AssertionError("coefficientwise R1 mutation was not rejected")
    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    if args.emit:
        print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
