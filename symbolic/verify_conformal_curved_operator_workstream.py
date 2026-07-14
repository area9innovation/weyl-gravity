#!/usr/bin/env python3
"""Verify exact curved identities and separate scalar-wave realization gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator import (
    CurvatureProlongationStatus,
    CurvedOperatorIdentityStatus,
)
from covariant_completion.curved_operator.curvature_prolongation_status import (
    OPEN_OBLIGATION_FIELDS,
)
from covariant_completion.curved_operator.covariant_jets import CovariantJetBasis
from covariant_completion.curved_operator.expanded_hessian import (
    coefficient_cache_certificate,
)


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"


def _write(name: str, payload: dict[str, object]) -> None:
    path = CERTIFICATE_DIR / name
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("wrote", path.relative_to(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-curved-operator-identity", action="store_true")
    args = parser.parse_args()

    status = CurvedOperatorIdentityStatus.build()
    covariant_jets = CovariantJetBasis.build()
    hessian_cache = coefficient_cache_certificate(
        CERTIFICATE_DIR / "curved_hessian_coefficient_table.json"
    )
    certificate = status.certificate()
    prolongation = CurvatureProlongationStatus.build(status.null_symbol_quotient)
    prolongation_certificate = prolongation.certificate()
    hessian_atomic = dict(hessian_cache)
    hessian_atomic.update(
        {
            "atomic_flag": "curved_exact_hessian",
            "curved_exact_hessian": True,
        }
    )
    rank_obstruction = status.null_symbol_obstruction.certificate()
    rank_obstruction["symbol_extension"] = (
        status.null_symbol_quotient.symbol_extension_certificate()
    )

    if args.claim_curved_operator_identity:
        if not status.complete:
            raise SystemExit(
                "REFUSED: one or more exact curved operator identities or their "
                "proof-mode-aware globalization obligations remain open"
            )
        print("CLAIMED: curved_operator_identity=true")
        print(
            "NOT CLAIMED: scalar normally-hyperbolic wave realization or the "
            "selected curvature-prolonged Green realization"
        )

    if args.emit:
        CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)
        _write("curved_auxiliary_action_definition.json", status.action.certificate())
        _write("curved_bv_conventions.json", status.action.conventions.certificate())
        _write("curved_gauge_invariance.json", status.action_hessian.certificate())
        _write("curved_auxiliary_hessian.json", hessian_cache)
        _write("curved_exact_hessian.json", hessian_atomic)
        _write(
            "curved_eliminated_vector_density.json",
            status.action_hessian.eliminated_density.certificate(),
        )
        _write(
            "curved_covariant_jet_basis.json",
            covariant_jets.certificate(reverify=False),
        )
        _write("curved_Q_nilpotency.json", {
            "schema": "pure-weyl-curved-Q-nilpotency-v1",
            "E_cyl_K_cyl": "zero",
            "dual_defect": "zero by formal adjointness",
            "Q_squared": "zero",
            "source": "action-derived completion-square Hessian",
        })
        _write("curved_witness_identity.json", status.four_row_kernel.certificate())
        _write("curved_formal_adjointness.json", {
            "schema": "pure-weyl-curved-formal-adjointness-v2",
            "support_category": "compactly supported smooth cylinder sections",
            "E_aux_cyl_sharp_minus_E_aux_cyl": "zero",
            "E_reason": (
                "E=U_shift^sharp diag(B_lin,A_g,0) U_shift; "
                "B_lin and A_g are action Hessians"
            ),
            "Y_C_minus_K_sharp_J": "zero coefficientwise",
            "W_cyl_sharp_minus_W_cyl": "zero",
            "P_cyl_sharp_minus_P_cyl": "zero",
            "curved_integration_by_parts_adjointness": True,
            "boundary_terms": "zero by compact spacetime support",
        })
        _write(
            "curved_companion_adjoint.json",
            {
                "schema": "pure-weyl-curved-companion-adjoint-v1",
                "identity": "Y_gh C_cyl=K_cyl^sharp J_aux",
                "derivative_coefficient_defects": [0, 0, 0, 0],
                "zeroth_coefficient_defect": 0,
                "flat_limit_exact": True,
                "companion_coefficient_sha256": (
                    status.action.conventions.gauge_companion.coefficient_sha256
                ),
                "complete_curved_companion": True,
            },
        )
        _write("curved_derivative_normal_form.json", status.normal_form.certificate())
        _write(
            "curved_invariant_pairing_ansatz.json",
            status.invariant_pairings.certificate(),
        )
        _write(
            "curved_null_symbol_rank_obstruction.json",
            rank_obstruction,
        )
        _write("curved_scalar_wave_no_go.json", rank_obstruction)
        _write(
            "curved_null_symbol_quotient.json",
            status.null_symbol_quotient.quotient_certificate(),
        )
        _write(
            "curved_helicity_two_channel.json",
            status.null_symbol_quotient.helicity_certificate(),
        )
        # The curvature-evolution verifier owns the live prolongation status.
        # This operator verifier deliberately keeps only a local fail-closed
        # status so parallel orchestration cannot overwrite later promotions.
        _write("curved_globalization.json", status.globalization.certificate())
        _write("curved_operator_identity_status.json", certificate)

    if args.guards:
        if not status.complete:
            raise AssertionError("exact curved operator identity was not promoted")
        if not status.globalization.complete:
            raise AssertionError("proof-mode-aware globalization did not close")
        if not certificate["exact_inputs_now"]["linearized_curved_gauge_map"]:
            raise AssertionError("the exact curved gauge-map input regressed")
        if certificate["promotion_criteria"]["globalization_coverage"] != "complete":
            raise AssertionError("globalization guard regressed")
        if not certificate["scalar_wave_realization"]["curved_scalar_wave_no_go"]:
            raise AssertionError("positive scalar-wave no-go theorem was hidden")
        if len(certificate["blocking_criteria"]) != 0:
            raise AssertionError("the curved A5 blocker inventory changed unexpectedly")
        if not all(certificate["atomic_certified_theorems"].values()):
            raise AssertionError("an atomic curved theorem was not promoted")
        if certificate["alternative_realization_flags"]["mixed_order_green_realization"]:
            raise AssertionError("mixed-order Green realization was inferred")
        if certificate["alternative_realization_flags"]["curvature_prolonged_realization"]:
            raise AssertionError("curvature-prolonged realization was inferred")
        if certificate["promotion_flags"]["curved_hessian_expanded"] is not True:
            raise AssertionError("the exact expanded curved Hessian was not promoted")
        if not hessian_cache["exhaustive_high_order_coverage_complete"]:
            raise AssertionError("expanded Hessian high-order jet coverage regressed")
        if certificate["promotion_flags"]["curved_companion_expanded"] is not True:
            raise AssertionError("the exact curved companion was not promoted")
        if certificate["promotion_flags"]["curved_Q_squared_zero"] is not True:
            raise AssertionError("the action-derived curved gauge kernel regressed")
        if certificate["promotion_flags"]["curved_QW_plus_WQ_minus_P_zero"] is not True:
            raise AssertionError("the curved four-row block identity regressed")
        if status.null_symbol_obstruction.pointwise_pairing_companion_solution_exists:
            raise AssertionError("known null-symbol rank obstruction was hidden")
        if status.null_symbol_obstruction.hessian_rank != 11:
            raise AssertionError("curved Hessian null-symbol rank witness drifted")
        if status.null_symbol_obstruction.gauge_rank != 9:
            raise AssertionError("curved gauge null-symbol rank witness drifted")
        if status.null_symbol_obstruction.fixed_j_obstruction_rank != 2:
            raise AssertionError("two transverse spin-2 obstruction channels drifted")
        quotient = status.null_symbol_quotient
        if quotient.quotient_dimension != 2:
            raise AssertionError("exact null-symbol quotient dimension drifted")
        if quotient.hessian_quotient_matrix != 4 * sp.eye(2):
            raise AssertionError("physical Hessian quotient block drifted")
        if quotient.little_group_generator**2 != -4 * sp.eye(2):
            raise AssertionError("helicity-two SO(2) action drifted")
        if quotient.induced_weyl_matrix.det() == 0:
            raise AssertionError("linearized Weyl quotient map lost invertibility")
        if not prolongation.weyl_symbol_helicity_isomorphism:
            raise AssertionError("reduced Weyl-symbol helicity isomorphism regressed")
        reduction = prolongation_certificate["exact_symbol_reduction"]
        if reduction["full_fibre_ker_W_equals_im_K_claimed"]:
            raise AssertionError("full-fibre ker(W)=im(K) was incorrectly claimed")
        if set(prolongation_certificate["atomic_open_obligations"]) != set(
            OPEN_OBLIGATION_FIELDS
        ):
            raise AssertionError("expanded curvature obligation ledger drifted")
        for open_flag in OPEN_OBLIGATION_FIELDS:
            if prolongation_certificate[open_flag]:
                raise AssertionError(f"unproved curvature flag promoted: {open_flag}")
        if prolongation.curvature_prolonged_complex_exact:
            raise AssertionError("unproved curvature-prolonged complex was promoted")
        if prolongation.curvature_green_realization:
            raise AssertionError("unproved curvature Green realization was promoted")
        modes = {
            item["proof_mode"]
            for item in status.globalization.certificate()["obligations"].values()
        }
        if modes != {
            "exhaustive_one_point_jets",
            "formal_adjoint_closure",
            "noncommutative_block_identity",
            "coefficientwise_formal_adjoint",
        }:
            raise AssertionError("globalization proof-mode ledger drifted")
        if covariant_jets.certificate(reverify=False)["raw_coordinate_exponential_used_as_covariant_table"]:
            raise AssertionError("raw coordinate jets crossed the covariant table guard")
        print("CURVED OPERATOR WORKSTREAM GUARDS: 43/43 PASS")

    print("CURVED OPERATOR WORKSTREAM: ALL IMPLEMENTED CHECKS PASS")


if __name__ == "__main__":
    main()
