#!/usr/bin/env python3
"""Verify the shifted filtration and exact restricted physical Green witness."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_shifted_green_filtration import (  # noqa: E402
    ExpandedRelativeShiftedGreenFiltration,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
RETRACT = CERTIFICATES / "curved_deformation_retract_status.json"
CANONICAL = CERTIFICATES / "curved_auxiliary_canonical_split.json"
TT_FACTOR = CERTIFICATES / "tt_local_factorization.json"
JORDAN = CERTIFICATES / "curved_expanded_relative_witness_jordan_homology.json"
OUTPUT = CERTIFICATES / "curved_expanded_relative_witness_shifted_green_filtration.json"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {path}")
    return value


def _rejects(
    audit: ExpandedRelativeShiftedGreenFiltration,
    retract: dict[str, object],
    canonical: dict[str, object],
    tt_factor: dict[str, object],
    jordan: dict[str, object],
) -> bool:
    try:
        audit.certificate(
            retract_certificate=retract,
            canonical_shift_certificate=canonical,
            tt_factor_certificate=tt_factor,
            jordan_homology_certificate=jordan,
        )
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-full-green", action="store_true")
    args = parser.parse_args()
    if args.claim_full_green:
        raise SystemExit(
            "REFUSED: restricted TT+auxiliary homotopy is not the all-row BV homotopy"
        )

    retract = _load(RETRACT)
    canonical = _load(CANONICAL)
    tt_factor = _load(TT_FACTOR)
    jordan = _load(JORDAN)
    audit = ExpandedRelativeShiftedGreenFiltration.build()
    certificate = audit.certificate(
        retract_certificate=retract,
        canonical_shift_certificate=canonical,
        tt_factor_certificate=tt_factor,
        jordan_homology_certificate=jordan,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    fixed = certificate["fixed_witness_after_shift"]
    actual = certificate["actual_local_physical_replacement_witness"]
    atomic = certificate["warranted_atomic_flags"]
    boundary = certificate["full_complex_boundary"]
    checks = {
        "actual_curved_Q_shift": certificate["auxiliary_shift"][
            "actual_curved_Q_conjugation_verified"
        ],
        "fixed_witness_SCC_not_hidden": not fixed[
            "f_hat_shift_splits_fixed_witness_SCC"
        ]
        and fixed["reciprocal_component_rank"] == 34,
        "actual_P_identity": actual["P_identity_defect"] == 0,
        "actual_left_Green": actual["left_Green_defect"] == 0,
        "actual_right_Green": actual["right_Green_defect"] == 0,
        "actual_restricted_homotopy": actual[
            "Q_Lambda_plus_Lambda_Q_defect"
        ] == 0,
        "operator_not_symbol": actual["operator_level_not_principal_symbol"],
        "physical_biwave_atomic_flag": atomic[
            "physical_biwave_block_green_hyperbolic"
        ],
        "physical_Jordan_causal_atomic_flag": atomic[
            "physical_Jordan_extension_causal"
        ],
        "atomic_flags_promoted": certificate["status_flags_promoted"] == atomic,
        "full_boundary_visible": not boundary["complete_QLambda_identity"]
        and not boundary["arbitrary_source_TT_projection_support_local"],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    if args.guards:
        bad_retract = deepcopy(retract)
        bad_retract["factorized_actual_curved_Q"][
            "actual_curved_Q_conjugation_verified"
        ] = False
        bad_tt = deepcopy(tt_factor)
        bad_tt["reduced_green_hyperbolic"] = False
        bad_jordan = deepcopy(jordan)
        bad_jordan["existing_contractible_pair"][
            "a0_is_in_Q_contractible_summand"
        ] = False
        checks.update(
            {
                "broken_curved_Q_split_rejected": _rejects(
                    audit, bad_retract, canonical, tt_factor, jordan
                ),
                "broken_TT_Green_rejected": _rejects(
                    audit, retract, canonical, bad_tt, jordan
                ),
                "broken_auxiliary_contraction_rejected": _rejects(
                    audit, retract, canonical, tt_factor, bad_jordan
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "SHIFTED GREEN FILTRATION: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
