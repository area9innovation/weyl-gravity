#!/usr/bin/env python3
"""Verify the homological classification of the intrinsic Jordan chain."""

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

from covariant_completion.curved_operator.expanded_relative_witness_jordan_homology import (
    FIELD_RANK,
    ExpandedRelativeJordanHomology,
)


OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_jordan_homology.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--claim-chain-entirely-contractible", action="store_true")
    parser.add_argument("--claim-global-mode-cocycle", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if (
        args.claim_green
        or args.claim_chain_entirely_contractible
        or args.claim_global_mode_cocycle
        or args.promote_flag
    ):
        raise SystemExit(
            "REFUSED: the certificate classifies the aligned polynomial "
            "amplitudes relative to the exact support-local BV split.  It does "
            "not construct a Green inverse, make the physical h23 amplitude "
            "contractible, or assert that an arbitrary global h23 section is "
            "a curved Bach solution"
        )

    diagnostic = ExpandedRelativeJordanHomology.build()
    certificate = diagnostic.certificate()
    ledger = certificate["component_ledger"]
    differential = certificate["BV_differential_at_aligned_anchor"]
    contraction = certificate["existing_contractible_pair"]
    curvature = certificate["curvature_and_constraints"]
    extension = certificate["representation_and_extension"]
    architecture = certificate["architectural_consequence"]
    checks = {
        "component_blocks_exact": ledger["a0"]["M_aux_index"] == 18
        and ledger["a1"]["M_aux_index"] == 8
        and ledger["equation_partner_of_a0"]["Ebar_aux_index"] == 8,
        "polynomial_and_BV_Q_distinguished": certificate["scope"][
            "polynomial_Q_is_not_BV_Q"
        ],
        "full_BV_images_exact": differential["full_QBV_a0"] == [[8, "-2"]]
        and differential["full_QBV_a1"] == []
        and not differential["a0_is_BV_cocycle"]
        and differential["a1_is_aligned_BV_cocycle"],
        "principal_images_exact": differential["principal_QBV_a0"] == []
        and differential["principal_QBV_a1"] == [[18, "4"]],
        "not_gauge": not differential["a0_is_gauge_symbol"]
        and not differential["a1_is_gauge_symbol"],
        "existing_pair_contracts": contraction["identity_defect"] == 0
        and contraction["a0_is_in_Q_contractible_summand"]
        and not contraction["a1_is_in_Q_contractible_summand"]
        and not contraction["additional_acyclic_pair_required_for_homological_split"],
        "curvature_assignment_exact": curvature["Weyl_symbol_on_a1_nonzero"]
        and curvature["Weyl_symbol_on_a0"] == 0
        and not curvature["a0_is_curvature_mapping_cone_coordinate"]
        and not curvature["a1_is_curvature_mapping_cone_coordinate"],
        "constraint_scope_honest": not curvature[
            "standard_212_Jordan_lift_satisfies_gradient_constraints"
        ]
        and curvature["intrinsic_116_polynomial_chain_independent_of_that_lift"],
        "extension_classified": extension["splits_as_SO2_bundle_representation"]
        and not extension["splits_as_fixed_witness_pencil_module"]
        and extension["splits_as_QBV_complex_after_existing_local_shift"]
        and not extension["Jordan_extension_survives_Q_cohomology"],
        "architecture_scoped": not architecture["Jordan_block_entirely_contractible"]
        and architecture["Jordan_block_touches_physical_curvature_through_a1"]
        and architecture["Jordan_eigenvector_is_contractible"]
        and not architecture["triangular_Green_inverse_constructed_here"],
        "fail_closed": certificate["fail_closed"]
        and not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"]
        and not certificate["causal_quasi_isomorphism"]
        and not certificate["status_flags_promoted"],
    }

    if args.guards:
        mutated_q = diagnostic.q_a0.copy()
        mutated_q[0] = 1
        broken_q = replace(diagnostic, q_a0=mutated_q)
        try:
            broken_q.verify()
        except AssertionError:
            checks["mutated_BV_image_rejected"] = True
        else:
            checks["mutated_BV_image_rejected"] = False

        mutated_homotopy = diagnostic.pair_homotopy.copy()
        mutated_homotopy[0, FIELD_RANK] = 1
        broken_homotopy = replace(
            diagnostic, pair_homotopy=mutated_homotopy
        )
        try:
            broken_homotopy.verify()
        except AssertionError:
            checks["mutated_contraction_rejected"] = True
        else:
            checks["mutated_contraction_rejected"] = False

        mutated_rotation = diagnostic.little_group_on_hf.copy()
        mutated_rotation[0, 0] = 1
        broken_rotation = replace(
            diagnostic, little_group_on_hf=mutated_rotation
        )
        try:
            broken_rotation.verify()
        except AssertionError:
            checks["mutated_representation_rejected"] = True
        else:
            checks["mutated_representation_rejected"] = False

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
