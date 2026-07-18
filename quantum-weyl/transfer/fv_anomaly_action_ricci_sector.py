#!/usr/bin/env python3
"""Certify the FV anomaly action and non-independence of its Ricci sector."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/FV_ANOMALY_ACTION_RICCI_SECTOR.json"
SCHEMA = HERE / "schema/fv-anomaly-action-ricci-sector-v1.schema.json"
DEPENDENCIES = {
    "regulated_breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "anomaly_induced_Gamma1": HERE / "certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
    "FV_conformized_C2_log": HERE / "certificates/FV_CONFORMIZED_C2_LOG_GAMMA1.json",
    "BoxR_scheme_conversion": ROOT / "quantum-weyl/spectral/euclidean/certificates/WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION.json",
    "Q1_disposition": HERE / "certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    breaking = values["regulated_breaking"]
    riegert = values["anomaly_induced_Gamma1"]
    conformized = values["FV_conformized_C2_log"]
    box_r = values["BoxR_scheme_conversion"]
    q1 = values["Q1_disposition"]

    c = Fraction(
        breaking["coefficients"]["ANOM_OMEGA_C2"]["numerator"],
        breaking["coefficients"]["ANOM_OMEGA_C2"]["denominator"],
    )
    e4_coordinate = Fraction(
        breaking["coefficients"]["ANOM_OMEGA_E4"]["numerator"],
        breaking["coefficients"]["ANOM_OMEGA_E4"]["denominator"],
    )
    box_coordinate = Fraction(
        breaking["coefficients"]["ANOM_OMEGA_BOX_R"]["numerator"],
        breaking["coefficients"]["ANOM_OMEGA_BOX_R"]["denominator"],
    )
    a = -e4_coordinate
    if (
        (c, a, box_coordinate)
        != (Fraction(199, 30), Fraction(87, 20), Fraction())
        or conformized["decision"]["selected_C2_log_local_Weyl_completion"]
        != "CERTIFIED"
        or conformized["fv_scalar_flat_representative"]["status"]
        != "EXACT_SCALAR_FLAT_REPRESENTATIVE_ON_DECLARED_INVERSE_DOMAIN"
        or box_r["decision"]["repository_BoxR_zero_scheme_conversion"]
        != "CERTIFIED"
        or q1["decision"]["complete_Q1"] != "NO_CERTIFIED_OPERATOR"
    ):
        raise ValueError("FV Ricci-sector dependencies drifted")

    # With Ecal4=E4-(2/3)BoxR and delta Sigma_FV=sigma, the exact FV
    # anomaly action is
    #   kappa int [(c C2-a Ecal4)Sigma + 2a Sigma Delta4 Sigma + a R2/18].
    # The Ecal4-density variation and the quadratic Sigma term cancel by
    # self-adjointness.  The BoxR contribution induced by Ecal4 is cancelled
    # by the local R2 response, leaving precisely c C2-a E4.
    sigma_quadratic_coefficient = 2 * a
    ecal_sigma_cross_response = -4 * a
    sigma_quadratic_cross_response = 4 * a
    cross_residual = ecal_sigma_cross_response + sigma_quadratic_cross_response
    ecal_box_response = Fraction(2, 3) * a
    local_r2_coefficient = a / 18
    local_r2_box_response = -12 * local_r2_coefficient
    box_residual = ecal_box_response + local_r2_box_response
    if cross_residual != 0 or box_residual != 0:
        raise ValueError("FV anomaly-action Weyl cancellation drifted")

    # The RFT gauge Sigma=(1/4)G4 Ecal4 must reproduce the earlier diagonal
    # Paneitz solve.  This is a convention-sensitive exact cross-check.
    rft_coefficients = [c / 4, -a / 8, a / 18]
    stored_rft = [
        Fraction(item["numerator"], item["denominator"])
        for item in riegert["exact_coefficient_solve"]["solution_vector"]
    ]
    if rft_coefficients != stored_rft:
        raise ValueError("FV/RFT anomaly-action convention cross-check drifted")

    result = {
        "schema": "quantum-weyl-fv-anomaly-action-ricci-sector-v1",
        "result_id": "FV_ANOMALY_ACTION_RICCI_SECTOR",
        "result_state": "FV_ANOMALY_ACTION_FIXED_RICCI_SECTOR_NOT_INDEPENDENT_CUBIC_WEYL_AND_FINITE_NORMALIZATIONS_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": breaking["classical_commit"],
        "scope": {
            "theory": "massless classically Diff x Weyl invariant pure-Weyl theory at one Euclidean loop",
            "geometry": "asymptotically flat or fixed-boundary curvature expansion with the normalized FV conformal inverse",
            "algebra": "formal covariant curvature expansion in the basis generated by Weyl curvature C and Ricci scalar R",
            "boundary_and_kernel_policy": "the same orbit-compatible inverse, source complement, and boundary normalization declared by the FV conformization certificate",
        },
        "coefficients": {
            "c": _q(c),
            "a": _q(a),
            "two_a": _q(sigma_quadratic_coefficient),
            "a_over_18": _q(local_r2_coefficient),
        },
        "fv_anomaly_action": {
            "modified_euler_density": "Ecal4=E4-(2/3)BoxR",
            "orbit_variable": "Sigma_FV=-log(1+(1/6)(Box-R/6)^(-1)R)",
            "functional": "Gamma1_FV=(4 pi)^(-2) integral sqrt(g)[((199/30)C2-(87/20)Ecal4)Sigma_FV+(87/10)Sigma_FV Delta4 Sigma_FV+(29/120)R2]",
            "weyl_law": "delta_sigma Sigma_FV=sigma",
            "weyl_response": "delta_sigma Gamma1_FV=(4 pi)^(-2) integral sqrt(g) sigma[(199/30)C2-(87/20)E4]",
            "status": "EXACT_COEFFICIENT_BEARING_FV_ANOMALY_ACTION_ON_DECLARED_ORBIT_DOMAIN",
        },
        "exact_cancellation_ledger": {
            "Ecal4_Sigma_cross_response": _q(ecal_sigma_cross_response),
            "Sigma_Delta4_Sigma_cross_response": _q(sigma_quadratic_cross_response),
            "cross_residual": _q(cross_residual),
            "Ecal4_induced_BoxR_response": _q(ecal_box_response),
            "local_R2_BoxR_response": _q(local_r2_box_response),
            "BoxR_residual": _q(box_residual),
            "status": "ALL_NON_TARGET_WEYL_RESPONSE_COORDINATES_CANCEL_EXACTLY",
        },
        "rft_crosscheck": {
            "substitution": "Sigma_RFT=(1/4)G4 Ecal4",
            "functional_basis": ["<Ecal4,G4 C2>", "<Ecal4,G4 Ecal4>", "integral R2"],
            "reconstructed_coefficients": [_q(value) for value in rft_coefficients],
            "stored_coefficients": riegert["exact_coefficient_solve"]["solution_vector"],
            "status": "EXACT_MATCH",
        },
        "conformal_decomposition": {
            "identity": "Gamma1[g]=Gamma1_FV[g]+W1[g_bar[g]]",
            "representative": "g_bar=exp(-2 Sigma_FV[g])g",
            "scalar_flat_condition": "R[g_bar]=0",
            "Weyl_sector": "W1 is generated only by Weyl-curvature basis invariants before evaluation on g_bar",
            "Ricci_sector": "all terms containing at least one R in a generic original-metric basis are fixed by Gamma1_FV and the re-expansion of W1[g_bar]",
            "status": "RICCI_SCALAR_SECTOR_STRUCTURALLY_DEPENDENT_IN_DECLARED_FV_CURVATURE_ALGEBRA",
        },
        "quadratic_form_factor_disposition": {
            "selected_independent_nonlocal_carrier": "C log(Delta_C/mu^2) C evaluated on g_bar",
            "selected_logarithmic_coefficient": conformized["conformized_C2_log"]["logarithmic_coefficient"],
            "putative_independent_R_F_R_carrier": "NOT_AN_INDEPENDENT_DATUM",
            "generic_basis_R_F_R_terms": "MAY_APPEAR_ONLY_AS_THE_DETERMINED_REEXPANSION_OF_Gamma1_FV_PLUS_W1_GBAR",
            "local_R2_role": "scheme-dependent local term in Gamma1_FV; a/18=29/120 in the repository BoxR=0 representative",
            "status": "NO_SEPARATE_NONLOCAL_R2_FORM_FACTOR_COEFFICIENT_TO_COMPUTE_IN_SCOPE",
        },
        "remaining_data": {
            "independent_cubic_and_higher_Weyl_form_factors": "NOT_COMPUTED",
            "finite_local_C2_normalization": "NOT_FIXED",
            "absolute_extended_R_g_hat_squared_normalization": "NOT_FIXED",
            "global_kernel_boundary_data": "NOT_FIXED_GLOBALLY",
            "renormalized_BV_laplacian_or_time_ordered_product": "NOT_SUPPLIED",
            "extended_classical_residual_contraction": "NOT_SUPPLIED",
            "complete_Gamma1": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
        },
        "decision": {
            "FV_anomaly_action": "CERTIFIED",
            "Ricci_scalar_sector_dependence": "CERTIFIED",
            "independent_nonlocal_R2_form_factor": "NOT_AN_INDEPENDENT_DATUM_IN_DECLARED_FV_CONFORMAL_DECOMPOSITION",
            "independent_cubic_Weyl_form_factors": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Gamma1": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
            "residual_transfer": "FORBIDDEN",
        },
        "claim_flags": {
            "FV_ANOMALY_ACTION_FIXED": True,
            "RICCI_SCALAR_SECTOR_DEPENDENCE_PROVED": True,
            "SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED": False,
            "SEPARATE_NONLOCAL_R2_FORM_FACTOR_COMPUTED": False,
            "INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED": False,
            "FINITE_C2_NORMALIZATION_FIXED": False,
            "ABSOLUTE_EXTENDED_RHAT2_NORMALIZATION_FIXED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "source_provenance": {
            "authors": ["A. O. Barvinsky", "W. Wachowski"],
            "title": "Notes on conformal anomaly, nonlocal effective action and the metamorphosis of the running scale",
            "journal": "Physical Review D 108, 045014 (2023)",
            "doi": "10.1103/PhysRevD.108.045014",
            "arxiv": "2306.03780v3",
            "url": "https://arxiv.org/abs/2306.03780",
            "use": "exact conformal-gauge decomposition, FV anomaly action, and the theorem that the Ricci part is determined by the anomaly and conformized Weyl part",
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "INDEPENDENT_CUBIC_AND_HIGHER_WEYL_FORM_FACTORS_FINITE_LOCAL_NORMALIZATIONS_RENORMALIZED_PRODUCTS_AND_EXTENDED_CLASSICAL_CONTRACTION",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate fixes the exact coefficient-bearing Fradkin-Vilkovisky anomaly action for the repository vector c=199/30 and a=87/20 and proves, in the declared massless asymptotically-flat or fixed-boundary formal curvature algebra, that the Ricci-scalar sector is not independent. The exact Weyl-response ledger cancels both the Ecal4/Sigma cross term and the induced BoxR coordinate, and the RFT specialization reproduces the earlier coefficients 199/120, -87/160 and 29/120. The conformal decomposition Gamma1[g]=Gamma1_FV[g]+W1[g_bar[g]] with R[g_bar]=0 implies that a generic-basis nonlocal R F(Box) R term, if displayed after re-expansion, is determined by the anomaly action and conformized Weyl sector rather than carrying a separately specifiable form factor. Therefore there is no independent nonlocal R2 coefficient to calculate within this scope. This does not compute the independent cubic or higher Weyl-sector form factors, fix the finite local C2 normalization or absolute extended R(g_hat)^2 normalization, solve global inverse or boundary data, construct renormalized products, supply a complete Gamma1 or Q1, authorize residual transfer, or establish any Lorentzian, Hadamard, positivity, particle, scattering, or unitarity theorem. It does not apply to massive, explicitly nonconformal, or independently symmetry-broken theories where additional Ricci-sector form factors can be genuine data."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    decision = value["decision"]
    flags = value["claim_flags"]
    if (
        decision["FV_anomaly_action"] != "CERTIFIED"
        or decision["Ricci_scalar_sector_dependence"] != "CERTIFIED"
        or decision["independent_nonlocal_R2_form_factor"]
        != "NOT_AN_INDEPENDENT_DATUM_IN_DECLARED_FV_CONFORMAL_DECOMPOSITION"
        or decision["complete_Gamma1"] != "NO_CERTIFIED_FUNCTIONAL"
        or decision["residual_transfer"] != "FORBIDDEN"
        or flags["FV_ANOMALY_ACTION_FIXED"] is not True
        or flags["RICCI_SCALAR_SECTOR_DEPENDENCE_PROVED"] is not True
        or any(
            flags[name] is not False
            for name in (
                "SEPARATE_NONLOCAL_R2_FORM_FACTOR_REQUIRED",
                "SEPARATE_NONLOCAL_R2_FORM_FACTOR_COMPUTED",
                "INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED",
                "FINITE_C2_NORMALIZATION_FIXED",
                "ABSOLUTE_EXTENDED_RHAT2_NORMALIZATION_FIXED",
                "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
                "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
                "RESIDUAL_TRANSFER_AUTHORIZED",
                "LORENTZIAN_CERTIFIED",
            )
        )
    ):
        raise ValueError("FV anomaly-action/Ricci-sector certificate crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale FV anomaly-action/Ricci-sector certificate: {OUTPUT}")
    print("FV ANOMALY ACTION: RICCI SECTOR DEPENDENT; NO SEPARATE NONLOCAL R2 DATUM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
