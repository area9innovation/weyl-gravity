#!/usr/bin/env python3
"""Verify the complete R6sharp family and its intrinsic Jordan no-go."""

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

from covariant_completion.curved_operator.expanded_relative_witness_r6_family import (
    COMPLETE_RANK,
    REDUCED_RANK,
    ExpandedRelativeR6Family,
    ExpandedRelativeR6FirstOrderNoGo,
)


FAMILY_OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_r6_family.json"
)
NO_GO_OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_r6_first_order_no_go.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-all-temporal-normalizations", action="store_true")
    parser.add_argument("--claim-other-incidences", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if (
        args.claim_all_temporal_normalizations
        or args.claim_other_incidences
        or args.claim_green
        or args.promote_flag
    ):
        raise SystemExit(
            "REFUSED: the exact no-go fixes the certified temporal R6sharp "
            "normalization, pair-(1,6) incidence, and cyclic -2Pi scalar "
            "branch; it does not decide other temporal coefficients, relative "
            "incidences, enlarged systems, or a Green witness"
        )

    diagnostic = ExpandedRelativeR6FirstOrderNoGo.build()
    family_certificate = diagnostic.family.certificate()
    certificate = diagnostic.certificate()
    temporal = family_certificate["temporal_family"]
    spatial = family_certificate["spatial_family"]
    complete = family_certificate["complete_first_order_family"]
    douglis = certificate["complete_aligned_Douglis_family"]
    intrinsic = certificate["intrinsic_polynomial_Jordan_chain"]
    symmetrizer = certificate["positive_symmetrizer_obstruction"]
    scope = certificate["constraint_scope"]
    checks = {
        "actual_temporal_family_complete": temporal["equations_shape"]
        == [1008, 336]
        and temporal["rank"] == 314
        and temporal["nullity"] == 22
        and temporal["certified_normalization_is_member"],
        "actual_spatial_family_complete": spatial["equations_shape"]
        == [3024, 1008]
        and spatial["equations_nonzero_entries"] == 6012
        and spatial["rank"] == 962
        and spatial["nullity"] == 46
        and spatial["all_basis_covariance_defects"] == 0,
        "complete_parameter_ledger": complete["unfixed_parameter_count"] == 68
        and complete["after_certified_temporal_normalization"] == 46
        and complete["complete_under_SO3_equivariance"],
        "corrected_Douglis_family": douglis["block_shape"] == [116, 116]
        and douglis["scalar_branch"]
        == "cyclic D_alt=-2 Pi_(h00,f00,v0)"
        and douglis["formal_adjoint_identity"] == "Nsharp(zeta)=-N(zeta)^T"
        and douglis["parameter_count"] == 46
        and douglis["coefficientwise_exact"],
        "intrinsic_base_chain_exact": intrinsic["base_identity_defects"] == [0, 0]
        and intrinsic["characteristic_root"] == "z=1",
        "all_parameter_directions_preserve_chain": intrinsic[
            "delta_Q1_a0_rank_over_all_parameters"
        ]
        == 0
        and intrinsic["delta_Q1_a1_plus_delta_Qprime1_a0_rank"] == 0
        and intrinsic["all_46_parameter_directions_preserve_both_identities"],
        "faithful_semisimplicity_no_go": not intrinsic[
            "polynomial_elementary_divisor_semisimple"
        ]
        and not intrinsic["semisimple_faithful_strong_linearization_exists"],
        "positive_symmetrizer_no_go": not symmetrizer[
            "positive_H_exists_for_any_faithful_strong_linearization"
        ]
        and symmetrizer["parameter_uniform"],
        "constraint_scope_honest": not scope[
            "Jordan_chain_lies_in_constraint_subspace"
        ]
        and scope["intrinsic_116_polynomial_chain_independently_certified"]
        and scope["scope_not_based_on_constraint_violating_chain"],
        "diagnostic_flags_promoted": certificate["status_flags_promoted"]
        == [
            "fixed_temporal_16_family_complete",
            "intrinsic_sensitivity_matrix_zero",
            "parameter_uniform_Jordan_chain",
            "fixed_temporal_16_no_go",
        ]
        and "strong_hyperbolicity_in_16_family=false"
        in certificate["warranted_atomic_flags"]
        and "symmetric_hyperbolicity_in_16_family=false"
        in certificate["warranted_atomic_flags"],
        "fail_closed": certificate["fail_closed"]
        and not certificate["prolonged_green_witness"],
    }

    if args.guards:
        bad_actions = list(diagnostic.intrinsic_chain_delta_actions)
        mutation = sp.zeros(COMPLETE_RANK, 1)
        mutation[0] = 1
        bad_actions[0] = mutation
        broken = replace(
            diagnostic,
            intrinsic_chain_delta_actions=tuple(bad_actions),
        )
        try:
            broken.verify()
        except AssertionError:
            checks["mutated_intrinsic_chain_rejected"] = True
        else:
            checks["mutated_intrinsic_chain_rejected"] = False

        bad_reduced = list(diagnostic.eigenvector_delta_actions)
        reduced_mutation = sp.zeros(REDUCED_RANK, 1)
        reduced_mutation[0] = 1
        bad_reduced[0] = reduced_mutation
        broken = replace(
            diagnostic,
            eigenvector_delta_actions=tuple(bad_reduced),
        )
        try:
            broken.verify()
        except AssertionError:
            checks["mutated_reduction_action_rejected"] = True
        else:
            checks["mutated_reduction_action_rejected"] = False

        broken_family = replace(
            diagnostic.family,
            spatial_rank=diagnostic.family.spatial_rank - 1,
        )
        try:
            broken_family.verify()
        except AssertionError:
            checks["mutated_family_rank_rejected"] = True
        else:
            checks["mutated_family_rank_rejected"] = False

    if not all(checks.values()):
        raise AssertionError(
            {name: passed for name, passed in checks.items() if not passed}
        )
    if args.emit:
        FAMILY_OUTPUT.write_text(
            json.dumps(family_certificate, indent=2, sort_keys=True) + "\n"
        )
        NO_GO_OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        )
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    if args.emit:
        print(f"wrote {FAMILY_OUTPUT.relative_to(ROOT)}")
        print(f"wrote {NO_GO_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
