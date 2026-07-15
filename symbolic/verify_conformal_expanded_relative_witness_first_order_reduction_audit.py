#!/usr/bin/env python3
"""Verify the exact constraint and polynomial-Jordan reduction audit."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_first_order_reduction_audit import (
    ExpandedRelativeFirstOrderReductionAudit,
)


OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_first_order_reduction_audit.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-naive-fixed-constraint", action="store_true")
    parser.add_argument("--claim-universal-no-go", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if (
        args.claim_naive_fixed_constraint
        or args.claim_universal_no_go
        or args.claim_green
        or args.promote_flag
    ):
        raise SystemExit(
            "REFUSED: the generalized vector is tangent-compatible rather "
            "than in the fixed prolongation image, and the scoped Jordan "
            "obstruction proves neither a universal first-order no-go nor a "
            "Green witness"
        )

    audit = ExpandedRelativeFirstOrderReductionAudit.build()
    certificate = audit.certificate()
    operator = certificate["principal_model_operator_intertwining"]
    determinant = certificate["aligned_determinant_audit"]
    jordan = certificate["intrinsic_polynomial_Jordan_chain"]
    scope = certificate["positive_symmetrizer_scope"]
    checks = {
        "principal_model_coefficientwise": operator["coefficientwise_defect"] == 0
        and not operator["curved_lower_order_completion_included"],
        "determinant_schur_exact": determinant["schur_elimination_defect"] == 0,
        "determinant_power_and_sign": determinant["net_tau_power"] == 72
        and determinant["column_permutation_parity"] == 0
        and determinant["sign"] == "+1",
        "original_polynomial_chain": jordan["Q1_a0_defect"] == 0
        and jordan["Q1_a1_plus_Qprime1_a0_defect"] == 0,
        "spectral_intertwining": jordan["spectral_intertwining_defect"] == 0,
        "reduced_chain_is_tangent_lift": jordan["u_equals_T1_a0_defect"] == 0
        and jordan["v_equals_T1_a1_plus_Tprime1_a0_defect"] == 0
        and jordan["u_in_fixed_spectral_prolongation_image"]
        and not jordan["v_in_fixed_spectral_prolongation_image"]
        and jordan["v_in_first_spectral_jet"],
        "not_constraint_artifact": not jordan["constraint_artifact"],
        "symmetrizer_scope_narrow": scope["explicit_212_reduction_obstructed"]
        and scope[
            "strong_polynomial_linearizations_preserving_finite_elementary_divisors_obstructed"
        ]
        and not scope["arbitrary_support_local_first_order_realizations_obstructed"]
        and not scope["generalized_or_compositional_Green_hyperbolicity_obstructed"]
        and not scope["full_invariant_spatial_R6sharp_family_obstructed"],
        "no_flag": certificate["fail_closed"]
        and not certificate["status_flags_promoted"]
        and not certificate["warranted_atomic_flags"],
    }
    if args.guards:
        broken = replace(audit, polynomial_generalized_defect=1)
        try:
            broken.verify()
        except AssertionError:
            checks["mutated_polynomial_chain_rejected"] = True
        else:
            checks["mutated_polynomial_chain_rejected"] = False

        broken_scope = replace(
            audit,
            generalized_fixed_image_constraint_defect=0,
        )
        try:
            broken_scope.verify()
        except AssertionError:
            checks["mutated_constraint_scope_rejected"] = True
        else:
            checks["mutated_constraint_scope_rejected"] = False

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
