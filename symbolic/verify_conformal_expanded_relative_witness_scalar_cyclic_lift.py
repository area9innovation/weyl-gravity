#!/usr/bin/env python3
"""Verify the odd-cyclic all-row lift of the retained scalar diagonal."""

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

from covariant_completion.curved_operator.expanded_relative_witness_scalar_cyclic_lift import (
    ExpandedRelativeScalarCyclicLift,
)
from covariant_completion.minimal_witness.formal_operators import OperatorPolynomial


OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_scalar_cyclic_lift.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--claim-symmetrizer", action="store_true")
    parser.add_argument("--claim-arbitrary-covector", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if (
        args.claim_green
        or args.claim_symmetrizer
        or args.claim_arbitrary_covector
        or args.promote_flag
    ):
        raise SystemExit(
            "REFUSED: a temporal cyclic scalar lift does not prove an "
            "arbitrary-covector characteristic, common symmetrizer, or Green witness"
        )

    lift = ExpandedRelativeScalarCyclicLift.build()
    certificate = lift.certificate()
    actual = certificate["actual_degree_minus_one_lift"]
    sparse = certificate["sparse_retained_diagonal"]
    natural = certificate["natural_scalar_ghost_projection"]
    alternative = certificate["diagonalizable_alternative"]
    boundary = certificate["analytic_boundary"]
    checks = {
        "actual_degree_minus_one_all_row_lift": (
            actual["split_odd_cyclicity_defect"] == 0
            and actual["prolonged_odd_cyclicity_defect"] == 0
            and actual["split_P_equals_Q_DeltaW_plus_DeltaW_Q"]
            and actual["prolonged_P_equals_Q_DeltaW_plus_DeltaW_Q"]
            and actual["all_16_rows_enumerated"]
        ),
        "complete_base_anticommutator": actual["complete_split_anticommutator"]
        == {
            "G_aux": "Sscalar K",
            "M_aux": "K Sscalar",
            "Ebar_aux": "Sscalarsharp C",
            "I_aux": "C Sscalarsharp",
            "all_curvature_cone_rows": "zero",
        },
        "no_split_cross_pollution": actual["split_unwanted_cross_blocks"] == 0
        and actual["split_affected_blocks"]
        == [
            ["G_aux", "G_aux"],
            ["M_aux", "M_aux"],
            ["Ebar_aux", "Ebar_aux"],
            ["I_aux", "I_aux"],
        ],
        "support_local": actual["support_local"]
        and actual["finite_differential_order"]
        and actual["uses_parallel_cylinder_time_normal"],
        "sparse_factorization_exact": sparse["lies_in_image_K_dt"]
        and sparse["rank_K_dt"] == sparse["rank_K_augmented_D"] == 9
        and sparse["companion_factor_unique"],
        "sparse_cyclic_boundary_exact": (
            sparse["D_sparse_sharp_minus_D_sparse_rank"] == 4
            and not sparse["identical_same_block_cyclic_lift_exists"]
            and sparse["cyclic_lift_with_formal_adjoint_partner_exists"]
            and sparse["nonidentical_partner_is_valid_for_BV_witness"]
        ),
        "natural_projection_cyclic": natural["projector_Y_self_adjoint"]
        and natural["all_derivative_and_zeroth_adjoint_defects"] == 0
        and natural["M_and_Ebar_diagonals_identical"]
        and natural["J_self_adjoint"],
        "natural_not_sparse": not natural["equals_sparse_diagonal"]
        and natural["difference_from_sparse_rank"] == 2
        and natural["same_3_by_3_retained_scalar_restriction"],
        "corrected_schur_sign": sparse["field_Schur_formula"]
        == "Eaux_2(dt)+D-Pi_vector",
        "sparse_and_natural_Jordan_remains": (
            sparse["field_Schur_characteristic_polynomial"] == "(lambda + 1)**24"
            and not sparse["field_Schur_diagonalizable"]
            and natural["field_Schur_characteristic_polynomial"]
            == "(lambda + 1)**24"
            and not natural["field_Schur_diagonalizable"]
        ),
        "alternative_removes_temporal_Jordan": (
            alternative["formula"] == "-2 Pi_(h00,f00,v0)"
            and alternative["field_Schur_rank"] == 24
            and alternative["field_Schur_determinant"] == 8
            and alternative["field_Schur_characteristic_polynomial"]
            == "(lambda + 1)**21*(lambda + 2)**3"
            and alternative["field_Schur_diagonalizable"]
            and alternative["temporal_Jordan_obstruction_removed"]
        ),
        "alternative_BV_partner_valid": (
            alternative["D_alt_sharp_minus_D_alt_rank"] == 4
            and not alternative["identical_same_block_cyclic_lift_exists"]
            and alternative["cyclic_lift_with_formal_adjoint_partner_exists"]
            and alternative["nonidentical_partner_is_valid_for_BV_witness"]
        ),
        "open_work_fail_closed": not any(boundary.values()),
        "no_green_promotion": certificate["fail_closed"]
        and not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"]
        and not certificate["status_flags_promoted"],
    }

    if args.guards:
        broken_w = [row[:] for row in lift.split_delta_w]
        broken_w[2][3] = OperatorPolynomial.zero()
        try:
            replace(lift, split_delta_w=broken_w).verify()
        except AssertionError:
            checks["missing_cyclic_partner_rejected"] = True
        else:
            checks["missing_cyclic_partner_rejected"] = False

        broken_factor = sp.Matrix(lift.sparse_companion_temporal)
        broken_factor[0, 0] += 1
        try:
            replace(lift, sparse_companion_temporal=broken_factor).verify()
        except AssertionError:
            checks["broken_sparse_factor_rejected"] = True
        else:
            checks["broken_sparse_factor_rejected"] = False

        broken_projector = sp.Matrix(lift.scalar_ghost_projector)
        broken_projector[0, 0] = 0
        try:
            replace(lift, scalar_ghost_projector=broken_projector).verify()
        except AssertionError:
            checks["broken_Y_projector_rejected"] = True
        else:
            checks["broken_Y_projector_rejected"] = False

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
