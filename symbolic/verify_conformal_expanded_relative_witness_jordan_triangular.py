#!/usr/bin/env python3
"""Verify the exact triangular Green algebra of the Jordan helicity block."""

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

from covariant_completion.curved_operator.expanded_relative_witness_jordan_triangular import (
    ExpandedRelativeJordanTriangular,
)


OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_jordan_triangular.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-full-filtration", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if args.claim_full_filtration or args.claim_green or args.promote_flag:
        raise SystemExit(
            "REFUSED: the exact result is the aligned helicity-block recursion. "
            "It does not yet embed that filtration support-locally in all 116 "
            "rows or construct the complete BV Green homotopy"
        )

    diagnostic = ExpandedRelativeJordanTriangular.build()
    certificate = diagnostic.certificate()
    shift = certificate["auxiliary_BV_shift"]
    witness = certificate["fixed_witness_block"]
    recursion = certificate["triangular_Green_recursion"]
    interpretation = certificate["interpretation"]
    checks = {
        "exact_biwave_contractible_split": shift["physical_metric_block"]
        == "L^2 (biwave)"
        and shift["generalized_auxiliary_block"]
        == "-1 (pointwise invertible)"
        and shift["off_diagonal_defect"] == 0
        and shift["field_shift_finite_order_local"],
        "closed_Jordan_block": witness["formula"] == "[[L,0],[4,L]]"
        and witness["full_116_row_leakage"] == 0
        and witness["full_116_column_leakage"] == 0,
        "shift_does_not_fake_diagonalization": not witness[
            "field_shift_removes_Jordan_extension"
        ]
        and witness["contractible_filtration_invariant"]
        and witness["associated_graded_blocks"]
        == ["L on f_hat", "L on h quotient"],
        "triangular_inverse_exact": recursion["left_inverse_defect"] == 0
        and recursion["right_inverse_defect"] == 0
        and recursion["off_diagonal_formula"] == "-G (4) G"
        and recursion["same_sign_composition_only"],
        "recursion_has_no_projector": not recursion["inverse_curl_used"]
        and not recursion["inverse_Laplacian_used"]
        and not recursion["TT_projector_used_in_recursion"]
        and not recursion["helicity_projector_used_in_recursion"],
        "full_embedding_left_open": not recursion[
            "projector_free_full_BV_embedding_certified"
        ]
        and not certificate["scope"]["full_116_support_local_filtration_certified"],
        "interpretation_scoped": interpretation[
            "strong_hyperbolicity_obstruction_and_Green_recursion_compatible"
        ],
        "fail_closed": certificate["fail_closed"]
        and not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"]
        and not certificate["status_flags_promoted"],
    }

    if args.guards:
        mutated_witness = diagnostic.witness_block.copy()
        mutated_witness[0, 1] = 1
        broken_witness = replace(diagnostic, witness_block=mutated_witness)
        try:
            broken_witness.verify()
        except AssertionError:
            checks["mutated_witness_rejected"] = True
        else:
            checks["mutated_witness_rejected"] = False

        mutated_q = sp.Matrix(diagnostic.shifted_bv_block)
        mutated_q[0, 0] = 1
        broken_q = replace(diagnostic, shifted_bv_block=mutated_q)
        try:
            broken_q.verify()
        except AssertionError:
            checks["mutated_Q_split_rejected"] = True
        else:
            checks["mutated_Q_split_rejected"] = False

        broken_green = replace(
            diagnostic,
            formal_left_defect=sp.Matrix([[1, 0], [0, 0]]),
        )
        try:
            broken_green.verify()
        except AssertionError:
            checks["mutated_Green_identity_rejected"] = True
        else:
            checks["mutated_Green_identity_rejected"] = False

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
