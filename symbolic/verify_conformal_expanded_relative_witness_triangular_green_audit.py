#!/usr/bin/env python3
"""Verify the exact triangular-Green/Jordan classification audit."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_triangular_green_audit import (  # noqa: E402
    ExpandedRelativeTriangularGreenAudit,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
NO_GO = CERTIFICATES / "curved_expanded_relative_witness_r6_first_order_no_go.json"
HELICITY = CERTIFICATES / "curved_helicity_two_channel.json"
TT_FACTOR = CERTIFICATES / "tt_local_factorization.json"
GREEN_BRIDGE = CERTIFICATES / "curved_prolonged_green_bridge.json"
OUTPUT = CERTIFICATES / "curved_expanded_relative_witness_triangular_green_audit.json"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {path}")
    return value


def _rejects(
    no_go: dict[str, object],
    helicity: dict[str, object],
    tt_factor: dict[str, object],
    bridge: dict[str, object],
) -> bool:
    try:
        ExpandedRelativeTriangularGreenAudit.build().certificate(
            no_go_certificate=no_go,
            helicity_certificate=helicity,
            tt_factor_certificate=tt_factor,
            green_bridge_certificate=bridge,
        )
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    args = parser.parse_args()
    if args.claim_green:
        raise SystemExit(
            "REFUSED: the rank-34 reciprocal and rank-four vector components "
            "have no certified Green inverses"
        )

    no_go = _load(NO_GO)
    helicity = _load(HELICITY)
    tt_factor = _load(TT_FACTOR)
    bridge = _load(GREEN_BRIDGE)
    certificate = ExpandedRelativeTriangularGreenAudit.build().certificate(
        no_go_certificate=no_go,
        helicity_certificate=helicity,
        tt_factor_certificate=tt_factor,
        green_bridge_certificate=bridge,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    physical = certificate["aligned_physical_reducing_block"]
    recursive = certificate["finite_recursive_Green_candidate"]
    filtration = certificate["natural_bundle_filtration"]
    obstruction = certificate["precise_remaining_obstruction"]
    checks = {
        "physical_block_reducing": physical["invariance_defect"] == 0
        and physical["coinvariance_defect"] == 0,
        "physical_Jordan_exact": physical["null_block_rank"] == 2
        and physical["null_block_square_zero"],
        "physical_Weyl_classification": physical[
            "linearized_Weyl_symbol_isomorphism"
        ]
        and not physical["entirely_Q_contractible"],
        "triangular_left_inverse": recursive["left_inverse_defect"] == 0,
        "triangular_right_inverse": recursive["right_inverse_defect"] == 0,
        "causal_formula": recursive["same_sided_causal_support"],
        "central_SCC_rank": filtration["central_reciprocal_rank"] == 34,
        "curvature_singletons_certified": filtration[
            "certified_symmetric_hyperbolic_singletons"
        ] == ["U", "F_sharp", "U_sharp"],
        "vector_singleton_open": filtration["open_singleton_blocks"] == ["v"],
        "central_SCC_open": not filtration[
            "central_SCC_Green_inverse_constructed"
        ],
        "no_nonlocal_projector_claim": not obstruction[
            "support_local_full_bundle_split_constructed"
        ],
        "scoped_positive_flags": certificate["status_flags_promoted"]
        == certificate["warranted_atomic_flags"],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    if args.guards:
        bad_no_go = deepcopy(no_go)
        bad_no_go["intrinsic_polynomial_Jordan_chain"][
            "all_46_parameter_directions_preserve_both_identities"
        ] = False
        bad_helicity = deepcopy(helicity)
        bad_helicity["linearized_Weyl_symbol"]["is_isomorphism"] = False
        bad_tt = deepcopy(tt_factor)
        bad_tt["reduced_green_hyperbolic"] = False
        bad_bridge = deepcopy(bridge)
        bad_bridge["finite_triangular_green_theorem"][
            "finite_no_Neumann_convergence_assumption"
        ] = False
        checks.update(
            {
                "broken_uniform_chain_rejected": _rejects(
                    bad_no_go, helicity, tt_factor, bridge
                ),
                "broken_helicity_map_rejected": _rejects(
                    no_go, bad_helicity, tt_factor, bridge
                ),
                "broken_TT_factor_rejected": _rejects(
                    no_go, helicity, bad_tt, bridge
                ),
                "broken_triangular_theorem_rejected": _rejects(
                    no_go, helicity, tt_factor, bad_bridge
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "TRIANGULAR GREEN AUDIT: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
