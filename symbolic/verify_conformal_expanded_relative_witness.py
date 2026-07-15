#!/usr/bin/env python3
"""Verify the complete invariant expanded-relative-witness incidence audit."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness import (
    ExpandedRelativeWitnessAudit,
)


OUTPUT = ROOT / "covariant_completion/certificates/curved_expanded_relative_witness.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--no-mutation-tests", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if args.claim_green or args.promote_flag:
        raise SystemExit(
            "REFUSED: incidence and temporal-rank bounds do not construct a "
            "Green witness or promote a causal flag"
        )
    audit = ExpandedRelativeWitnessAudit.build()
    certificate = audit.certificate()
    checks = {
        "nine_pair_coverage": certificate["complete_relative_space"]["odd_adjoint_pairs"] == 9,
        "declared_multiplicity_family": (
            certificate["complete_relative_space"][
                "SO3_invariant_parameter_dimension"
            ]
            == 162
            and not certificate["complete_relative_space"][
                "rotation_generator_commutants_constructed"
            ]
        ),
        "three_minimal_global_saddles": certificate["minimal_all_auxiliary_degree_reciprocal_saddles"]["pair_sets"] == ["1+6", "1+7", "2+7"],
        "central_cross_rank21": certificate["invariant_cross_rank"]["maximum_ranks_through_all_reciprocal_curvature_partners"] == [9, 21, 21, 9],
        "central_rank_bound113": certificate["scoped_temporal_no_go"]["central_temporal_rank_upper_bound"] == 113,
        "rank_defect3": certificate["scoped_temporal_no_go"]["central_temporal_rank_defect_lower_bound"] == 3,
        "fail_closed": certificate["fail_closed"] and not certificate["status_flags_promoted"],
    }
    if not all(checks.values()):
        raise AssertionError({key: value for key, value in checks.items() if not value})
    if not args.no_mutation_tests:
        bad = deepcopy(certificate)
        bad["invariant_cross_rank"]["maximum_ranks_through_all_reciprocal_curvature_partners"][1] = 24
        if bad["invariant_cross_rank"]["maximum_ranks_through_all_reciprocal_curvature_partners"] == [9, 21, 21, 9]:
            raise AssertionError("central-rank mutation was not detected")
    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    if args.emit:
        print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
