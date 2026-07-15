#!/usr/bin/env python3
"""Verify the exact arbitrary-covector pair-(1,6) Douglis candidate."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_full_symbol import (
    ExpandedRelativeFullSymbol,
)


OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_full_symbol.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--claim-full-symmetrizer", action="store_true")
    parser.add_argument("--claim-cyclic-lift", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if (
        args.claim_green
        or args.claim_full_symmetrizer
        or args.claim_cyclic_lift
        or args.promote_flag
    ):
        raise SystemExit(
            "REFUSED: the causal characteristic polynomial does not provide "
            "the missing first-order reduction, full symmetrizer, cyclic "
            "scalar witness lift, lower-order completion, or Green inverse"
        )

    diagnostic = ExpandedRelativeFullSymbol.build()
    certificate = diagnostic.certificate()
    ordinary_certificate = json.loads(
        (ROOT / "covariant_completion/certificates/ordinary_derivative_auxiliary_system.json").read_text()
    )
    convention_certificate = json.loads(
        (ROOT / "covariant_completion/certificates/curved_bv_conventions.json").read_text()
    )
    exact_inputs = certificate["exact_inputs"]
    complete = certificate["complete_arbitrary_covector_symbol"]
    formal = certificate["formal_adjoint_correction"]
    schur = certificate["curvature_Schur_polynomial"]
    retained = certificate["retained_scalar_candidate"]
    separated = certificate["separated_scalar_candidate"]
    characteristic = certificate["characteristic_conclusion"]
    no_go = certificate["field_Schur_simultaneous_multiplier_no_go"]
    boundary = certificate["scope_and_open_work"]
    checks = {
        "complete_116_symbol": complete["shape"] == [116, 116]
        and complete["coefficient_tables_complete"]
        and complete["Douglis_orders"] == {"A": 2, "B": 1, "C": 2, "D": 1},
        "correct_adjoint_sign": formal["identity"]
        == "Ncurvsharp(zeta)=-Ncurv(zeta)^T"
        and formal["old_coordinate_transpose_without_minus_rejected"],
        "field_pairing_provenance": exact_inputs["field_pairing_sha256"]
        == ordinary_certificate["matrix_sha256"]["field_fibre_pairing"],
        "gauge_generator_provenance": exact_inputs[
            "gauge_K_full_coefficient_sha256"
        ]
        == convention_certificate["gauge_generator"]["coefficient_sha256"],
        "local_polynomial_schur": schur["aligned_rational_identity_exact"]
        and schur["SO3_covariance_defect"] == 0,
        "retained_temporal_rank": retained["temporal_rank"] == 116,
        "retained_jordan_exact": retained["nilpotent_ranks_N_N2_N3"]
        == [2, 1, 0]
        and not retained["temporal_field_diagonalizable"],
        "separated_temporal_positive": separated["temporal_field_diagonalizable"]
        and all(value == "1" for value in separated["temporal_positive_multiplier_leading_minors"])
        and all(
            sp.sympify(value) > 0
            for value in separated["weighted_temporal_leading_minors"]
        ),
        "separated_not_full_symmetrizer": any(
            separated["full_spatial_symmetrizer_defects"]
        )
        and not separated["cyclic_scalar_lift_claimed_in_this_certificate"]
        and separated["cyclic_scalar_lift_cross_certificate"]
        == "curved_expanded_relative_witness_scalar_cyclic_lift.json",
        "causal_characteristics": characteristic["all_roots_real"]
        and characteristic["all_speeds_causal"]
        and characteristic["generic_covector_invertible"],
        "simultaneous_multiplier_no_go": no_go["solution_dimension"] == 1
        and no_go["generator_rank"] == 4
        and not no_go["nondegenerate_pointwise_field_multiplier_exists"]
        and not no_go["positive_pointwise_field_symmetrizer_exists"],
        "fail_closed_boundary": boundary["arbitrary_covector_characteristic_certified_for_candidate"]
        and not boundary["positive_full_Douglis_symmetrizer_certified"]
        and not boundary["first_order_reduction_constructed"]
        and boundary["cyclic_scalar_lift_cross_certificate_required"]
        and not boundary["lower_order_completion_certified"]
        and not boundary["all_BV_degrees_certified"],
        "no_flag": certificate["fail_closed"]
        and not certificate["status_flags_promoted"]
        and not certificate["warranted_atomic_flags"],
    }
    if args.guards:
        broken = replace(
            diagnostic,
            retained_temporal_field_jordan_ranks=(2, 0, 0),
        )
        try:
            broken.verify()
        except AssertionError:
            checks["mutated_Jordan_chain_rejected"] = True
        else:
            checks["mutated_Jordan_chain_rejected"] = False

        broken_sign = replace(
            diagnostic,
            aligned_retained_determinant=-diagnostic.aligned_retained_determinant,
        )
        try:
            broken_sign.verify()
        except AssertionError:
            checks["mutated_characteristic_rejected"] = True
        else:
            checks["mutated_characteristic_rejected"] = False

    if not all(checks.values()):
        raise AssertionError(
            {name: passed for name, passed in checks.items() if not passed}
        )
    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    if args.emit:
        print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
