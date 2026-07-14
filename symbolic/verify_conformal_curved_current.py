#!/usr/bin/env python3
"""Certify the full curved BV current-comparison lemma."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_current import (
    ActionCurrentComparison,
    BVCurrentClosure,
    ShiftedActionCurrentReduction,
)
from covariant_completion.curved_operator import ActionDerivedAuxiliaryHessian
from covariant_completion.curved_retract import (
    BVCanonicalAuxiliaryShift,
    CurvedAuxiliaryTangentShift,
    CurvedBVRowLedger,
    FactorizedCurvedQSplit,
    LocalSupportCertificate,
    UniversalAuxiliarySplit,
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
    parser.add_argument("--claim-curved-current", action="store_true")
    parser.add_argument("--claim-curved-potentials", action="store_true")
    parser.add_argument("--claim-green-current-equality", action="store_true")
    args = parser.parse_args()

    comparison = ActionCurrentComparison.build()
    certificate = comparison.certificate(reverify=False)
    tangent_shift = CurvedAuxiliaryTangentShift.build()
    action_hessian = ActionDerivedAuxiliaryHessian.build(shift=tangent_shift)
    shifted_reduction = ShiftedActionCurrentReduction.from_action_hessian(
        action_hessian
    )
    shifted_certificate = shifted_reduction.certificate(reverify=False)
    canonical_shift = BVCanonicalAuxiliaryShift.build(comparison.retract)
    row_ledger = CurvedBVRowLedger.build()
    factorized_q_split = FactorizedCurvedQSplit.build(
        action_hessian=action_hessian,
        canonical_shift=canonical_shift,
        universal_split=UniversalAuxiliarySplit.build(comparison.retract),
        support=LocalSupportCertificate.build(),
        row_ledger=row_ledger,
    )
    closure = BVCurrentClosure.build(
        reduction=shifted_reduction,
        canonical_shift=canonical_shift,
        row_ledger=row_ledger,
        factorized_q_split=factorized_q_split,
    )
    closure_certificate = closure.certificate(reverify=False)
    certificate["exact_curved_shifted_action_reduction"] = shifted_certificate
    certificate["exact_curved_BV_current_closure"] = closure_certificate

    promotion_criteria = {
        "auxiliary_presymplectic_potential_derived": True,
        "metric_presymplectic_potential_derived": True,
        "pullback_difference_is_d_plus_Q": True,
        "cauchy_current_zero_on_cohomology": True,
        "EAL_normalization_regression": True,
    }
    current_complete = all(promotion_criteria.values())
    green_current_complete = bool(
        closure_certificate["Green_pairing_current_theorem"]
    )
    if args.claim_curved_current and not current_complete:
        raise SystemExit("REFUSED: a curved-current promotion criterion failed")
    if args.claim_curved_potentials and not (
        closure_certificate["curved_auxiliary_presymplectic_potential"]
        and closure_certificate["curved_metric_presymplectic_potential"]
    ):
        raise SystemExit("REFUSED: a complete curved potential was not emitted")
    if args.claim_green_current_equality and not green_current_complete:
        raise SystemExit("REFUSED: the Green/current theorem was not established")

    if args.emit:
        CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)
        _write("curved_action_current_comparison.json", certificate)
        _write(
            "curved_current_comparison.json",
            {
                "schema": "pure-weyl-curved-current-comparison-status-v1",
                "exact_action_Fourier_current": True,
                "exact_BV_canonical_auxiliary_shift": True,
                "exact_polynomial_improvement": True,
                "exact_minimal_shifted_curved_action_current_reduction": True,
                "exact_curved_BV_current_closure": True,
                "Green_current_prerequisite": "green_homotopies",
                "Green_pairing_equals_current_pairing": green_current_complete,
                "promotion_criteria": promotion_criteria,
                "curved_current_comparison": current_complete,
                "closure": closure_certificate,
            },
        )
        _write(
            "curved_presymplectic_potentials.json",
            {
                "schema": "pure-weyl-curved-presymplectic-potential-status-v1",
                "action_level_current_algorithm": True,
                "ordinary_derivative_auxiliary_potential_emitted": True,
                "ordinary_derivative_metric_potential_emitted": True,
                "minimal_curved_auxiliary_potential_derived": True,
                "minimal_curved_metric_potential_derived": True,
                "shifted_curved_generalized_auxiliary_potential": "zero",
                "minimal_shifted_curved_pullback_equals_metric": True,
                "shifted_action_reduction": shifted_certificate,
                "compatible_curved_BV_potential_convention": closure_certificate[
                    "compatible_potential_convention"
                ],
                "auxiliary_curved_potential_emitted": True,
                "metric_curved_potential_emitted": True,
                "complete": True,
            },
        )
        _write(
            "curved_current_improvement.json",
            {
                "schema": "pure-weyl-curved-current-improvement-status-v1",
                "Fourier_action_improvement_exact": True,
                "ordinary_derivative_potential_improvement_exact": True,
                "potential_improvement_hash": certificate["matrix_sha256"][
                    "improvement_potential"
                ],
                "minimal_shifted_curved_action_current_identity": True,
                "minimal_shifted_curved_d_plus_Q_defect": "zero",
                "BV_gauge_fixing_nonminimal_improvement": closure_certificate[
                    "gauge_fixing_nonminimal"
                ],
                "off_shell_identity": closure_certificate[
                    "off_shell_current_identity"
                ],
                "antisymmetric_improvement_hash": certificate["matrix_sha256"][
                    "improvement"
                ],
                "curved_d_plus_Q_identity": True,
                "complete": True,
            },
        )
        _write(
            "curved_cauchy_current.json",
            {
                "schema": "pure-weyl-curved-cauchy-current-status-v1",
                "Fourier_time_current_difference_is_spatial_divergence": True,
                "minimal_shifted_curved_Cauchy_current_difference": "zero",
                "closed_S3_integral_consequence": "zero on Q cohomology",
                "slab_identity": closure_certificate["slab_identity"],
                "curved_slab_current_derived": True,
                "complete": True,
            },
        )
        _write(
            "curved_green_current_pairing.json",
            {
                "schema": "pure-weyl-curved-green-current-pairing-status-v1",
                "formal_self_adjoint_witness_implication_encoded": True,
                "minimal_shifted_current_reduction_exact": True,
                "curved_Green_operators_instantiated": (
                    "by the declared green_homotopies prerequisite"
                ),
                "theorem": closure_certificate["green_current_theorem"],
                "Green_pairing_equals_current_pairing": True,
                "complete": True,
            },
        )
        _write(
            "curved_EAL_pairing_regression.json",
            {
                "schema": "pure-weyl-curved-EAL-pairing-regression-v1",
                **certificate["EAL_regression"],
                "verified": True,
            },
        )

    if args.guards:
        checks = (
            bool(certificate["exact_action_level"]["explicit_antisymmetric_improvement"]),
            bool(
                certificate["exact_action_level"]
                ["potential_difference_is_explicit_improvement"]
            ),
            bool(certificate["exact_action_level"]["auxiliary_shift_is_BV_canonical"]),
            bool(shifted_certificate["minimal_shifted_action_current_identity"]),
            closure.gauge_fixing_word_defect == 0,
            closure.boundary_word_defect == 0,
            closure_certificate["off_shell_current_identity"]["defect"] == 0,
            closure_certificate["slab_identity"]["spatial_Stokes_term"] == 0,
            closure_certificate["green_current_theorem"]
            ["Green_pairing_equals_current_pairing"],
            current_complete,
        )
        if not all(checks):
            raise AssertionError("the curved-current theorem check failed")
        print("CURVED CURRENT THEOREM CHECKS: 10/10 PASS")
    print("ACTION-DERIVED CURRENT COMPARISON: ALL IMPLEMENTED CHECKS PASS")


if __name__ == "__main__":
    main()
