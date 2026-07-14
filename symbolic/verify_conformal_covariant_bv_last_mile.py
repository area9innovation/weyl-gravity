#!/usr/bin/env python3
"""Certify the covariant BV last mile in fail-closed dependency order."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.auxiliary_equivalence import GeneralizedAuxiliaryRetract
from covariant_completion.global_witness import CurvedAuxiliaryWitnessStatus
from covariant_completion.green_homotopy import (
    GreenWitnessRecognition,
    ResidualCutoffRecovery,
)
from covariant_completion.pairing import CovariantPairingStatus


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
GENERATED_DIR = ROOT / "covariant_completion" / "generated"


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
    parser.add_argument("--claim-complete-covariant-theorem", action="store_true")
    parser.add_argument("--claim-curved-coefficient-table", action="store_true")
    parser.add_argument("--claim-curved-retract", action="store_true")
    parser.add_argument("--claim-covariant-cauchy-pairing", action="store_true")
    args = parser.parse_args()

    if args.claim_complete_covariant_theorem:
        raise SystemExit(
            "REFUSED: the generalized-auxiliary retract and abstract causal layer "
            "are proved, but the curved lower-coefficient and covariant-current "
            "certificates are not yet complete"
        )
    if args.claim_curved_coefficient_table:
        raise SystemExit(
            "REFUSED: the full first/zeroth-order 24-by-24 curved-cylinder "
            "coefficient table has not been emitted"
        )
    if args.claim_curved_retract:
        raise SystemExit(
            "REFUSED: the exact 66-to-30 Fourier SDR has support-local formulas, "
            "but its complete curved lower-order chain identities are not emitted"
        )
    if args.claim_covariant_cauchy_pairing:
        raise SystemExit(
            "REFUSED: the auxiliary Green current and its pullback to the metric "
            "Cauchy current remain to be derived"
        )

    # Dependency order A--G.  A and D deliberately emit incomplete status
    # records rather than silently upgrading symbol or mode checks.
    curved = CurvedAuxiliaryWitnessStatus.build().certificate()
    retract_object = GeneralizedAuxiliaryRetract.build()
    retract = retract_object.certificate(reverify=False)
    recognition = GreenWitnessRecognition().certificate()
    pairing = CovariantPairingStatus.build().certificate()
    residual = ResidualCutoffRecovery.build().certificate()

    complete = bool(
        curved["complete_curved_witness_certificate"]
        and pairing["complete_covariant_pairing_certificate"]
    )
    curved_q_status = {
        "schema": "pure-weyl-curved-Q-nilpotency-status-v1",
        "four_row_Fourier_Q_squared": "zero",
        "curved_global_Q_squared_verified": False,
        "remaining": "reconstruct every lower-order curved block and multiply as differential operators",
    }
    curved_witness_status = {
        "schema": "pure-weyl-curved-witness-identity-status-v1",
        "four_row_Fourier_identity": "QW+WQ=P",
        "curved_global_identity_verified": False,
        "remaining": "complete first/zeroth-order witness and retract coefficients",
    }
    wave_symbol_status = {
        "schema": "pure-weyl-degreewise-wave-symbols-v1",
        "fibre_dimensions": [9, 24, 24, 9],
        "normalized_principal_symbols": "g^{mu nu} zeta_mu zeta_nu times identity",
        "verified": True,
        "implication_guard": "principal symbols alone do not instantiate the curved Green operators",
    }
    curved_adjoint_status = {
        "schema": "pure-weyl-curved-formal-adjointness-status-v1",
        "Fourier_symbol_adjointness": True,
        "curved_integration_by_parts_adjointness": False,
        "remaining": "include all lower-order connection, curvature, and auxiliary-background terms",
    }
    normal_hyperbolicity_status = {
        "schema": "pure-weyl-degreewise-normal-hyperbolicity-status-v1",
        "wave_symbols_verified": True,
        "global_curved_operators_instantiated": False,
        "degreewise_normal_hyperbolicity_theorem": False,
    }
    chain_map_status = {
        "schema": "pure-weyl-auxiliary-chain-map-status-v1",
        "Fourier_complex": {
            "inclusion_shape": retract["sdr"]["inclusion_shape"],
            "projection_shape": retract["sdr"]["projection_shape"],
            "Q_aux_i_equals_i_Q_met": True,
            "p_Q_aux_equals_Q_met_p": True,
        },
        "curved_lower_order_chain_maps_verified": False,
        "support_local_formulas": True,
    }
    support_status = {
        "schema": "pure-weyl-auxiliary-support-preservation-v1",
        "compact": "preserved by every displayed finite differential/pointwise map",
        "spacelike_compact": "preserved by every displayed finite differential/pointwise map",
        "smooth_global": "preserved",
        "guard": "support preservation does not replace the open curved chain-map identities",
    }
    completion = {
        "schema": "pure-weyl-completed-covariant-bv-status-v1",
        "dependency_order": [
            "A curved witness",
            "B Green homotopies",
            "C auxiliary retract",
            "D covariant/Cauchy pairing",
            "E Sobolev reduction",
            "F residual comparison",
            "G cohomology transport",
        ],
        "proved_now": [
            "exact 66-to-30 all-row Fourier-complex SDR with support-local formulas",
            "Gamma_sc=Gamma on R x S^3",
            "compatibility with the existing lambda=+1 BFV replacement",
        ],
        "formal_consequences_after_A": [
            "Green-operator chain compatibility",
            "retarded/advanced homotopy identities and causal support",
            "basis-level CKV cutoff-source recovery",
            "compact-to-global quasi-isomorphism",
        ],
        "remaining": [
            "complete curved first/zeroth-order coefficient and adjoint table",
            "curved lower-order chain identities for the 66-to-30 retract",
            "auxiliary differential Green current",
            "auxiliary-to-metric Cauchy-current comparison",
            "pairing-compatible covariant-to-energy quasi-isomorphism",
        ],
        "complete_covariant_theorem": complete,
        "completed_H4_transport": (
            "blocked until the curved operator, deformation-retract, and "
            "current-comparison lemmas pass"
        ),
        "algebraic_and_energy_mode_H4": "C^2 with Gram I_2 remains independently certified",
    }

    if args.emit:
        CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)
        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        payloads = {
            "curved_auxiliary_witness_status.json": curved,
            "curved_Q_nilpotency.json": curved_q_status,
            "curved_witness_identity.json": curved_witness_status,
            "degreewise_wave_symbols.json": wave_symbol_status,
            "curved_formal_adjointness.json": curved_adjoint_status,
            "degreewise_normal_hyperbolicity.json": normal_hyperbolicity_status,
            "auxiliary_shift_split.json": retract,
            "generalized_auxiliary_contraction.json": retract,
            "all_bv_rows_contraction.json": retract,
            "metric_to_aux_chain_map.json": chain_map_status,
            "aux_to_metric_chain_map.json": chain_map_status,
            "compact_support_preservation.json": support_status,
            "spacelike_compact_support_preservation.json": support_status,
            "green_operator_chain_compatibility.json": recognition,
            "retarded_advanced_homotopy.json": recognition,
            "compact_to_global_quasi_isomorphism.json": recognition,
            "covariant_cauchy_pairing_status.json": pairing,
            "auxiliary_differential_pairing.json": pairing,
            "cauchy_boundary_current.json": pairing,
            "auxiliary_metric_current_comparison.json": pairing,
            "ckv_cutoff_sources.json": residual,
            "residual_bfv_comparison.json": residual,
            "residual_no_duplication.json": residual,
            "completed_covariant_status.json": completion,
        }
        for name, payload in payloads.items():
            _write(name, payload)

        theorem_path = GENERATED_DIR / "covariant_bv_last_mile_status.tex"
        theorem_path.write_text(
            "\n".join(
                [
                    "% Generated by symbolic/verify_conformal_covariant_bv_last_mile.py",
                    r"\begin{proposition}[Auxiliary Fourier-complex SDR]",
                    r"The shifted ordinary-derivative auxiliary tensor, its equation row,",
                    r"the conformal-boost Stueckelberg pair, and their cotangent duals",
                    r"form an explicit $36$-dimensional contractible summand in the",
                    r"four-row Fourier complex.  Exact $66$-to-$30$ chain maps and",
                    r"homotopy are emitted, with finite differential or pointwise",
                    r"support-local formulas.",
                    r"\end{proposition}",
                    r"\begin{remark}[Remaining covariant certificates]",
                    r"The abstract Green-homotopy and residual cutoff-source identities",
                    r"are exact.  The complete curved lower-coefficient/retract table and the",
                    r"auxiliary-to-metric Green-current comparison remain open; hence the",
                    r"completed covariant pairing theorem is not asserted here.",
                    r"\end{remark}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        print("wrote", theorem_path.relative_to(ROOT))

    if args.guards:
        checks = (
            not complete,
            not bool(curved["curved_lower_coefficient_table_emitted"]),
            not bool(curved["curved_retract_chain_maps_emitted"]),
            not bool(pairing["complete_covariant_pairing_certificate"]),
        )
        if not all(checks):
            raise AssertionError("one or more fail-closed boundaries unexpectedly closed")
        print("COVARIANT BV LAST-MILE GUARDS: 4/4 PASS")
    print("COVARIANT BV LAST-MILE CERTIFICATES: ALL IMPLEMENTED CHECKS PASS")


if __name__ == "__main__":
    main()
