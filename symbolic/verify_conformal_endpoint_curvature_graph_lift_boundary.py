#!/usr/bin/env python3
"""Verify the exact boundary for the 30-row endpoint graph Green lift."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.endpoint_curvature_graph_lift_boundary import (
    EndpointCurvatureGraphLiftBoundary,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATES / "curved_endpoint_curvature_graph_lift_boundary.json"
REPORT = (
    ROOT
    / "covariant_completion"
    / "generated"
    / "curved_endpoint_curvature_graph_lift_boundary.md"
)


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate {name} is not an object")
    return value


def _rejects(action: object) -> bool:
    try:
        if callable(action):
            action()
        else:
            raise AssertionError("guard action is not callable")
    except AssertionError:
        return True
    return False


def _report(certificate: dict[str, object]) -> str:
    obstruction = certificate["canonical_middle_graph_lift_obstruction"]
    upper = certificate["upper_graph_lift"]
    remaining = certificate["minimum_remaining_operator_identity"]
    return f"""# Endpoint curvature-graph Green-lift boundary

The retained endpoint is the support-local 30-row metric-curvature graph.
The upper canonical curvature backward map lifts exactly:

```text
{upper['target_equation']}
rank(R) = {upper['R_rank']}
```

The middle canonical Weyl--Cotton backward map does not preserve that graph.
It would require `{obstruction['required_equation']}`.  Exact factorization
`{obstruction['T_factorization']}`, together with
`pi_EB J_WC=1`, `pi_EB A_F=0` and `rank(A_F)=5`, proves that equation
inconsistent on the leading Douglis page.  The exact rank regression gives
zero intersection on the generic, timelike, spacelike, null and temporal
representatives.

This is a scoped no-go for restricting the canonical zeroth-order `p_F`; it
is not a no-go for a relative Green witness.  The minimum remaining target is:

> {remaining['preferred_relative_form']}

Compatible sourced propagation and the graded adjoint Green identity remain
mandatory.  No causal or final-cohomology flag is promoted by this receipt.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    hybrid = _load("curved_prolonged_hybrid_algebraic_projector.json")
    core = _load("curved_core_curvature_chain_map.json")
    curvature = _load("curved_weyl_cotton_block_green_witness.json")
    ghost = _load("ghost_biwave_factorization.json")
    tt = _load("tt_local_factorization.json")
    theorem = EndpointCurvatureGraphLiftBoundary.build()
    certificate = theorem.certificate(
        hybrid_certificate=hybrid,
        core_chain_certificate=core,
        curvature_witness_certificate=curvature,
        ghost_factor_certificate=ghost,
        tt_factor_certificate=tt,
        reverify=False,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        REPORT.write_text(_report(certificate), encoding="utf-8")
        print("wrote", OUTPUT.relative_to(ROOT))
        print("wrote", REPORT.relative_to(ROOT))

    obstruction = certificate["canonical_middle_graph_lift_obstruction"]
    upper = certificate["upper_graph_lift"]
    decision = certificate["decision"]
    checks = {
        "upper_lift_exact": upper["exact"] and upper["R_rank"] == 4,
        "middle_factorization_exact": obstruction["T_factorization"]
        == "T_core=J_WC W_EB"
        and obstruction["pi_EB_J_WC"] == "identity",
        "middle_support_disjoint": obstruction["pi_EB_A_F"] == "zero"
        and obstruction["rank_A_F"] == 5,
        "canonical_middle_lift_rejected": not obstruction[
            "canonical_p_F_graph_lift_exists"
        ],
        "all_strata_zero_intersection": all(
            values["intersection_dimension"] == 0
            and values["rank_T_join_A_F"] == 10
            for values in obstruction["sample_rank_regression"].values()
        ),
        "no_false_green_promotion": not decision["actual_W_end_constructed"]
        and not decision["actual_L_end_two_sided_Green"]
        and not decision["prolonged_green_witness"]
        and not decision["curvature_causal_green_operators"]
        and not decision["causal_green_homotopy"],
    }
    if args.guards:
        bad_hybrid = deepcopy(hybrid)
        bad_hybrid["composite_SDR"]["P_end_idempotent"] = False
        bad_curvature = deepcopy(curvature)
        bad_curvature["exact_block_identities"]["P_equals_QW_plus_WQ"] = False
        checks.update(
            {
                "missing_endpoint_projector_rejected": _rejects(
                    lambda: theorem.certificate(
                        hybrid_certificate=bad_hybrid,
                        core_chain_certificate=core,
                        curvature_witness_certificate=curvature,
                        ghost_factor_certificate=ghost,
                        tt_factor_certificate=tt,
                        reverify=False,
                    )
                ),
                "broken_WC_witness_rejected": _rejects(
                    lambda: theorem.certificate(
                        hybrid_certificate=hybrid,
                        core_chain_certificate=core,
                        curvature_witness_certificate=bad_curvature,
                        ghost_factor_certificate=ghost,
                        tt_factor_certificate=tt,
                        reverify=False,
                    )
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "ENDPOINT CURVATURE GRAPH LIFT BOUNDARY: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
