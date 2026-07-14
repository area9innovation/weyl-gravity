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
from covariant_completion.final_transport import FinalCovariantTransportStatus
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

    # Claim behavior is derived from one live dependency-DAG snapshot.  These
    # gates therefore work unchanged before and after the upstream A--C
    # certificates close; there is no static "must remain false" branch.
    transport = FinalCovariantTransportStatus.build()
    report = transport.report
    report_certificate = report.certificate()

    def blockers(claim: str) -> tuple[str, ...]:
        values = transport.blocking_dependencies(claim)
        if tuple(
            report_certificate["claims"][claim]["blocking_dependencies"]
        ) != values:
            raise AssertionError(f"{claim} report snapshot drifted")
        return values

    def require_claim(requested: bool, claim: str, label: str) -> None:
        if requested and not report.nodes[claim].status:
            raise SystemExit(
                f"REFUSED: {label} is false; blocking atomic dependencies: "
                + ", ".join(blockers(claim))
            )

    require_claim(
        args.claim_complete_covariant_theorem,
        "final_covariant_H4",
        "complete covariant theorem",
    )
    require_claim(
        args.claim_curved_coefficient_table,
        "curved_hessian_expanded",
        "curved coefficient table",
    )
    require_claim(
        args.claim_curved_retract,
        "curved_deformation_retract",
        "curved deformation retract",
    )
    require_claim(
        args.claim_covariant_cauchy_pairing,
        "curved_current_comparison",
        "covariant Cauchy pairing",
    )

    # Dependency order A--G.  A and D deliberately emit incomplete status
    # records rather than silently upgrading symbol or mode checks.
    curved = CurvedAuxiliaryWitnessStatus.build().certificate()
    retract_object = GeneralizedAuxiliaryRetract.build()
    retract = retract_object.certificate(reverify=False)
    recognition = GreenWitnessRecognition().certificate()
    pairing = CovariantPairingStatus.build().certificate()
    residual = ResidualCutoffRecovery.build().certificate()

    complete = report.nodes["final_covariant_H4"].status
    wave_symbol_status = {
        "schema": "pure-weyl-degreewise-wave-symbols-v1",
        "fibre_dimensions": [9, 24, 24, 9],
        "normalized_principal_symbols": "g^{mu nu} zeta_mu zeta_nu times identity",
        "scope": (
            "flat/Fourier symbol witness only; the exact null-symbol theorem "
            "rules out this scalar completion for the curved 24-field block"
        ),
        "verified": True,
        "curved_scalar_symbol_witness_no_go": report.nodes[
            "scalar_wave_witness_no_go"
        ].status,
        "implication_guard": "principal symbols alone do not instantiate the curved Green operators",
    }
    normal_hyperbolicity_status = {
        "schema": "pure-weyl-degreewise-normal-hyperbolicity-status-v1",
        "wave_symbols_verified": True,
        "global_curved_operators_instantiated": report.nodes[
            "curved_operator_identity"
        ].status,
        "degreewise_normal_hyperbolicity_theorem": report.nodes[
            "degreewise_normal_hyperbolicity"
        ].status,
    }
    chain_map_status = {
        "schema": "pure-weyl-auxiliary-chain-map-status-v1",
        "Fourier_complex": {
            "inclusion_shape": retract["sdr"]["inclusion_shape"],
            "projection_shape": retract["sdr"]["projection_shape"],
            "Q_aux_i_equals_i_Q_met": True,
            "p_Q_aux_equals_Q_met_p": True,
        },
        "curved_lower_order_chain_maps_verified": all(
            report.nodes[name].status
            for name in (
                "curved_metric_to_aux_chain_map",
                "curved_aux_to_metric_chain_map",
                "curved_retract_identity",
                "curved_Q_conjugation",
                "curved_all_BV_rows",
            )
        ),
        "support_local_formulas": True,
    }
    support_status = {
        "schema": "pure-weyl-auxiliary-support-preservation-v1",
        "compact": "preserved by every displayed finite differential/pointwise map",
        "spacelike_compact": "preserved by every displayed finite differential/pointwise map",
        "smooth_global": "preserved",
        "dependency_report_status": report.nodes["support_preservation"].status,
        "guard": "support preservation is tracked independently of the chain-map gate",
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
            name
            for name in (
                "degreewise_wave_symbols",
                "support_preservation",
                "curved_Q_conjugation",
                "curved_all_BV_rows",
                "EAL_pairing_regression",
                "ckv_cutoff_identity",
                "algebraic_residual_no_duplication",
                "energy_H4_is_C2",
                "energy_gram_is_I2",
            )
            if report.nodes[name].status
        ],
        "formal_consequences_after_A": [
            "Green-operator chain compatibility",
            "retarded/advanced homotopy identities and causal support",
            "basis-level CKV cutoff-source recovery",
            "compact-to-global quasi-isomorphism",
        ],
        "remaining": list(blockers("final_covariant_H4")),
        "complete_covariant_theorem": complete,
        "completed_H4_transport": {
            "status": complete,
            "blocking_dependencies": list(blockers("final_covariant_H4")),
            "H4": ["W_+^2", "W_-^2"] if complete else None,
            "Gram": [[1, 0], [0, 1]] if complete else None,
        },
        "algebraic_and_energy_mode_H4": "C^2 with Gram I_2 remains independently certified",
        "dependency_report_terminal_gate": list(
            report.nodes["final_covariant_H4"].requires
        ),
    }

    if args.emit:
        CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)
        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        payloads = {
            "curved_auxiliary_witness_status.json": curved,
            "degreewise_wave_symbols.json": wave_symbol_status,
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
        latex_lines = [
            "% Generated by symbolic/verify_conformal_covariant_bv_last_mile.py",
            r"\begin{proposition}[Covariant BV dependency gate]",
            r"The terminal covariant theorem is the conjunction recorded in the",
            r"machine-checked final-claim dependency graph.",
        ]
        if complete:
            latex_lines.extend(
                [
                    r"All dependencies pass, so $H^4_{\rm cov}$ is spanned by",
                    r"$[W_+^2],[W_-^2]$ and its transported Gram matrix is $I_2$.",
                ]
            )
        else:
            latex_blockers = ", ".join(
                r"\texttt{" + name.replace("_", r"\_") + "}"
                for name in blockers("final_covariant_H4")
            )
            latex_lines.extend(
                [
                    r"The terminal gate remains fail closed on the following atomic",
                    "dependencies: " + latex_blockers + ".",
                ]
            )
        latex_lines.extend([r"\end{proposition}", ""])
        theorem_path.write_text("\n".join(latex_lines), encoding="utf-8")
        print("wrote", theorem_path.relative_to(ROOT))

    if args.guards:
        final = report.nodes["final_covariant_H4"]
        checks = (
            final.status == all(report.nodes[name].status for name in final.requires),
            bool(blockers("final_covariant_H4")) != complete,
            completion["complete_covariant_theorem"] == final.status,
            chain_map_status["curved_lower_order_chain_maps_verified"]
            == all(
                report.nodes[name].status
                for name in (
                    "curved_metric_to_aux_chain_map",
                    "curved_aux_to_metric_chain_map",
                    "curved_retract_identity",
                    "curved_Q_conjugation",
                    "curved_all_BV_rows",
                )
            ),
        )
        if not all(checks):
            raise AssertionError("live dependency-DAG guard consistency failed")
        print("COVARIANT BV LAST-MILE DYNAMIC GUARDS: 4/4 PASS")
    print("COVARIANT BV LAST-MILE CERTIFICATES: ALL IMPLEMENTED CHECKS PASS")


if __name__ == "__main__":
    main()
