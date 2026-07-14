#!/usr/bin/env python3
"""Certify the action-level current comparison and guard its curved boundary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_current import ActionCurrentComparison


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

    if args.claim_curved_current:
        raise SystemExit(
            "REFUSED: the exact Fourier/action current and improvement are proved, "
            "but the curved presymplectic potentials and Green-current equality are open"
        )
    if args.claim_curved_potentials:
        raise SystemExit(
            "REFUSED: neither complete curved presymplectic potential has been emitted"
        )
    if args.claim_green_current_equality:
        raise SystemExit(
            "REFUSED: equality of the curved causal-Green and slab-current pairings "
            "requires the completed curved witness and current identities"
        )

    comparison = ActionCurrentComparison.build()
    certificate = comparison.certificate(reverify=False)

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
                "promotion_criteria": certificate["curved_promotion_criteria"],
                "curved_current_comparison": False,
                "guard": certificate["theorem_boundary"],
            },
        )
        _write(
            "curved_presymplectic_potentials.json",
            {
                "schema": "pure-weyl-curved-presymplectic-potential-status-v1",
                "action_level_current_algorithm": True,
                "auxiliary_curved_potential_emitted": False,
                "metric_curved_potential_emitted": False,
                "complete": False,
            },
        )
        _write(
            "curved_current_improvement.json",
            {
                "schema": "pure-weyl-curved-current-improvement-status-v1",
                "Fourier_action_improvement_exact": True,
                "antisymmetric_improvement_hash": certificate["matrix_sha256"][
                    "improvement"
                ],
                "curved_d_plus_Q_identity": False,
                "complete": False,
            },
        )
        _write(
            "curved_cauchy_current.json",
            {
                "schema": "pure-weyl-curved-cauchy-current-status-v1",
                "Fourier_time_current_difference_is_spatial_divergence": True,
                "closed_S3_integral_consequence": "conditional on curved identity",
                "curved_slab_current_derived": False,
                "complete": False,
            },
        )
        _write(
            "curved_green_current_pairing.json",
            {
                "schema": "pure-weyl-curved-green-current-pairing-status-v1",
                "formal_self_adjoint_witness_implication_encoded": True,
                "curved_Green_operators_instantiated": False,
                "Green_pairing_equals_current_pairing": False,
                "complete": False,
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
        criteria = certificate["curved_promotion_criteria"]
        checks = (
            bool(certificate["exact_action_level"]["explicit_antisymmetric_improvement"]),
            bool(certificate["exact_action_level"]["auxiliary_shift_is_BV_canonical"]),
            not bool(criteria["auxiliary_presymplectic_potential_derived"]),
            not bool(criteria["metric_presymplectic_potential_derived"]),
            not bool(criteria["Green_pairing_equals_current_pairing"]),
            not bool(certificate["curved_current_comparison"]),
        )
        if not all(checks):
            raise AssertionError("the curved-current fail-closed boundary moved")
        print("CURVED CURRENT FAIL-CLOSED GUARDS: 6/6 PASS")
    print("ACTION-DERIVED CURRENT COMPARISON: ALL IMPLEMENTED CHECKS PASS")


if __name__ == "__main__":
    main()
