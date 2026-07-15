#!/usr/bin/env python3
"""Verify the fail-closed common-Rees rank-14 cone extraction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_full_cone_rees_gate import (  # noqa: E402
    Rank14FullConeReesGate,
)


OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_rank14_full_cone_rees_gate.json"
)


def _checks(certificate: dict[str, object]) -> dict[str, bool]:
    degrees = certificate["degree_ledger"]
    maps = certificate["map_components"]
    cone = certificate["degree_zero_cone"]
    correction = certificate["coordinate_correction"]
    decision = certificate["decision"]
    strata = certificate["causal_strata"]
    return {
        "full_degree_ledger": degrees["cochain_degrees"] == [-2, -1, 0, 1, 2]
        and degrees["ranks"] == [9, 24, 50, 49, 14]
        and degrees["incoming_gauge_row_included"],
        "complete_component_ledger": {
            name: item["emitted_degrees"] for name, item in maps.items()
        }
        == {
            "K": [0],
            "E": [0, -2, -4],
            "C": [0, -2, -4],
            "T": [0],
            "A": [0, -2],
            "B": [0],
            "Ewc": [0, -2],
            "N": [0, -2],
        },
        "actual_Q_coordinates": correction["actual_Q_identity_block"]
        == "system.gauge_condition"
        and correction["actual_Caux_emitted_degrees"] == [0, -2, -4]
        and not correction["raw_action_dual_is_the_fibre_identified_Q_block"]
        and correction["previous_Caux_degree_minus_two_demotion_corrected"],
        "authoritative_A": certificate["authoritative_full_A"][
            "coefficient_occurrences"
        ]
        == 149
        and certificate["authoritative_full_A"][
            "direct_equal_weight_A0_included"
        ],
        "first_two_squares": cone["square_nonzero_entries"][:2] == [0, 0],
        "last_square_exact": cone["square_nonzero_entries"] == [0, 0, 68]
        and cone["last_square"]
        == {
            "operator": "N[0] A[0]-B[0] Caux[0]",
            "N0_A0_nonzero_entries": 68,
            "B0_C0_nonzero_entries": 28,
            "defect_nonzero_entries": 68,
            "nonzero_identity_rows": [6, 7, 8, 12],
            "row_types": "a[3],s[1]",
            "rank_on_all_tested_strata": 4,
        },
        "cohomology_refused": not cone["is_complex"]
        and not cone["cohomology_computed"]
        and all(
            item["square_ranks"] == [0, 0, 4]
            and not item["cohomology_defined"]
            for item in strata.values()
        ),
        "no_overpromotion": not decision[
            "leading_associated_graded_cone_is_a_complex"
        ]
        and not decision["leading_associated_graded_cohomology_computed"]
        and not decision["complete_Rees_PBW_cone_constructed"]
        and not decision["support_local_contraction_constructed"]
        and not decision["prolonged_green_witness"]
        and not decision["causal_green_homotopy"]
        and not decision["rank14_SDR_constructed"]
        and certificate["status_flags_promoted"] == [],
        "scoped_boundary": "attachment-consistency obstruction"
        in certificate["refined_boundary"],
        "fail_closed": certificate["fail_closed"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    certificate = Rank14FullConeReesGate.build().certificate()
    checks = _checks(certificate)
    if not all(checks.values()):
        raise AssertionError(
            "rank-14 Rees gate failed: "
            + ", ".join(name for name, passed in checks.items() if not passed)
        )

    guards: dict[str, bool] = {}
    if args.guards:
        bad = deepcopy(certificate)
        bad["coordinate_correction"][
            "raw_action_dual_is_the_fibre_identified_Q_block"
        ] = True
        guards["raw_action_dual_as_Q_rejected"] = not all(_checks(bad).values())
        bad = deepcopy(certificate)
        bad["degree_zero_cone"]["cohomology_computed"] = True
        guards["cohomology_before_d2_rejected"] = not all(_checks(bad).values())
        bad = deepcopy(certificate)
        bad["decision"]["leading_associated_graded_cone_is_a_complex"] = True
        guards["false_complex_promotion_rejected"] = not all(_checks(bad).values())
        bad = deepcopy(certificate)
        bad["decision"]["causal_green_homotopy"] = True
        guards["premature_green_promotion_rejected"] = not all(
            _checks(bad).values()
        )
        if not all(guards.values()):
            raise AssertionError("rank-14 Rees mutation guard failed")

    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "certificate": str(OUTPUT.relative_to(ROOT)),
                "checks": checks,
                "guards": guards,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
