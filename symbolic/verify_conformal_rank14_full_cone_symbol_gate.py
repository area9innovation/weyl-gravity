#!/usr/bin/env python3
"""Verify the fail-closed full graded rank-14 cone symbol gate."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_full_cone_symbol_gate import (  # noqa: E402
    Rank14FullConeSymbolGate,
)


OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_rank14_full_cone_symbol_gate.json"
)


def _checks(certificate: dict[str, object]) -> dict[str, bool]:
    degrees = certificate["degree_ledger"]
    auxiliary = certificate["ordinary_auxiliary_BV_layer"]
    curved = certificate["curved_identity_comparison"]
    valid = certificate["valid_subcomplex_squares"]
    strata = certificate["causal_strata"]
    decision = certificate["decision"]
    return {
        "full_degrees": degrees["degrees"] == [-2, -1, 0, 1, 2]
        and degrees["ranks"] == [9, 24, 50, 49, 14]
        and degrees["incoming_gauge_row_included"],
        "ordinary_Caux": auxiliary["Caux"] == "K_ordinary(-zeta)^T J_aux"
        and auxiliary["Caux_Eaux_defect"] == 0
        and auxiliary["Eaux_K_defect"] == 0
        and not auxiliary["gauge_companion_is_Caux"]
        and not auxiliary["exact_curved_K_used"],
        "curved_Caux_scoped": curved[
            "curved_minus_ordinary_rank_on_all_tested_strata"
        ] == 4,
        "subcomplexes": valid["T_K_defect"] == 0
        and valid["Ncurv_Ecurv_defect"] == 0
        and valid["incoming_cone_square_defect"] == 0,
        "generic_defects": strata["generic_(2,1,3,5)"]["square_ranks"]
        == [0, 11, 4],
        "causal_defects": all(
            strata[name]["square_ranks"] == expected
            for name, expected in {
                "timelike_(2,1,0,0)": [0, 11, 4],
                "spacelike_(0,1,0,0)": [0, 11, 4],
                "temporal_(1,0,0,0)": [0, 11, 4],
                "null_(1,1,0,0)": [0, 7, 4],
            }.items()
        ),
        "cohomology_refused": not certificate["full_cone_symbol_is_a_complex"]
        and not certificate["full_cone_symbol_cohomology_computed"],
        "filtration_required": certificate["required_repair"]["object"]
        == "one componentwise Douglis/Rees filtration",
        "cycle_gate_demoted": "witness-cycle diagnostic"
        in certificate["certificate_corrections"]["rank14_equation_cycle_gate"],
        "no_overpromotion": not decision["principal_full_cone_acyclic"]
        and decision["principal_full_cone_residual_rank"]
        == "undefined until d^2=0"
        and not decision["support_local_contraction_constructed"]
        and not decision["prolonged_green_witness"]
        and not decision["causal_green_homotopy"]
        and certificate["status_flags_promoted"] == [],
        "fail_closed": certificate["fail_closed"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    certificate = Rank14FullConeSymbolGate.build().certificate()
    checks = _checks(certificate)
    if not all(checks.values()):
        raise AssertionError(
            "full cone symbol gate failed: "
            + ", ".join(name for name, passed in checks.items() if not passed)
        )

    guards: dict[str, bool] = {}
    if args.guards:
        bad = deepcopy(certificate)
        bad["ordinary_auxiliary_BV_layer"]["gauge_companion_is_Caux"] = True
        guards["companion_as_Caux_rejected"] = not all(_checks(bad).values())
        bad = deepcopy(certificate)
        bad["full_cone_symbol_cohomology_computed"] = True
        guards["cohomology_before_complex_rejected"] = not all(
            _checks(bad).values()
        )
        bad = deepcopy(certificate)
        bad["decision"]["causal_green_homotopy"] = True
        guards["premature_green_promotion_rejected"] = not all(
            _checks(bad).values()
        )
        if not all(guards.values()):
            raise AssertionError("full cone symbol mutation guard failed")

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
