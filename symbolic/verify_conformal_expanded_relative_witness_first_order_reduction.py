#!/usr/bin/env python3
"""Verify the exact first-order reduction and its scoped Jordan obstruction."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_first_order_reduction import (
    ExpandedRelativeFirstOrderReduction,
)


OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_first_order_reduction.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-symmetric-hyperbolic", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--claim-full-family-no-go", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if (
        args.claim_symmetric_hyperbolic
        or args.claim_green
        or args.claim_full_family_no_go
        or args.promote_flag
    ):
        raise SystemExit(
            "REFUSED: this certificate proves a Jordan obstruction only for "
            "the time-only R6sharp, cyclic -2Pi weighted symbol.  It neither "
            "supplies a symmetrizer/Green inverse nor rules out the complete "
            "invariant spatial R6sharp family"
        )

    diagnostic = ExpandedRelativeFirstOrderReduction.build()
    certificate = diagnostic.certificate()
    reduction = certificate["support_local_first_order_reduction"]
    equivalence = certificate["exact_equivalence"]
    characteristic = certificate["aligned_characteristic"]
    obstruction = certificate["exact_positive_symmetrizer_obstruction"]
    intrinsic = certificate["intrinsic_weighted_symbol_chain"]
    scope = certificate["scope"]
    checks = {
        "regular_212_reduction": reduction["state_rank"] == 212
        and reduction["temporal_rank"] == 212
        and reduction["temporal_determinant"] == 8,
        "support_local": reduction["finite_order"] and reduction["support_local"],
        "exact_weighted_recovery": equivalence["coefficientwise_defect"] == 0,
        "constraint_propagation": equivalence["constraint_propagation_defect"] == 0
        and equivalence["equivalence_requires_constraint_initial_data"]
        and not equivalence["unconstrained_212_state_system_identified_with_original"],
        "causal_real_roots": characteristic["all_characteristic_speeds_real"]
        and characteristic["all_characteristic_speeds_absolute_value_at_most_one"],
        "Jordan_multiplicity_defect": characteristic["algebraic_multiplicities"]
        == [120, 8, 8, 30, 30, 8, 8]
        and characteristic["geometric_multiplicities"]
        == [96, 6, 6, 28, 28, 8, 8]
        and not characteristic["diagonalizable"],
        "positive_symmetrizer_empty": obstruction["positive_feasible_set_empty"]
        and obstruction["one_direction_already_obstructs_simultaneous_system"],
        "intrinsic_polynomial_chain": intrinsic["defect"] == 0
        and not intrinsic["gradient_constraint_artifact"]
        and intrinsic["tangent_constraint_compatible"],
        "scope_narrow": not scope["full_invariant_spatial_R6sharp_family_tested"],
        "no_flag": certificate["fail_closed"]
        and not certificate["status_flags_promoted"]
        and not certificate["warranted_atomic_flags"],
    }

    if args.guards:
        mutated_vector = diagnostic.jordan_generalized_vector.copy()
        mutated_vector[0] += 1
        broken = replace(diagnostic, jordan_generalized_vector=mutated_vector)
        try:
            broken.verify()
        except AssertionError:
            checks["mutated_reduced_chain_rejected"] = True
        else:
            checks["mutated_reduced_chain_rejected"] = False

        mutated_polynomial = diagnostic.polynomial_jordan_generalized_vector.copy()
        mutated_polynomial[0] += 1
        broken_polynomial = replace(
            diagnostic,
            polynomial_jordan_generalized_vector=mutated_polynomial,
        )
        try:
            broken_polynomial.verify()
        except AssertionError:
            checks["mutated_polynomial_chain_rejected"] = True
        else:
            checks["mutated_polynomial_chain_rejected"] = False

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
