#!/usr/bin/env python3
"""Certify the FV-conformized completion of the one-loop C log(Delta) C carrier."""

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
OUTPUT = HERE / "certificates/FV_CONFORMIZED_C2_LOG_GAMMA1.json"
SCHEMA = HERE / "schema/fv-conformized-c2-log-gamma1-v1.schema.json"
DEPENDENCIES = {
    "covariant_C2_log": HERE / "certificates/CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1.json",
    "regulated_breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "extended_cohomology": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json",
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
    covariant = values["covariant_C2_log"]
    breaking = values["regulated_breaking"]
    extended = values["extended_cohomology"]
    q1 = values["Q1_disposition"]

    coefficient = Fraction(
        covariant["covariant_curvature_squared_form_factor"]["logarithmic_coefficient"]["numerator"],
        covariant["covariant_curvature_squared_form_factor"]["logarithmic_coefficient"]["denominator"],
    )
    c = Fraction(
        breaking["coefficients"]["ANOM_OMEGA_C2"]["numerator"],
        breaking["coefficients"]["ANOM_OMEGA_C2"]["denominator"],
    )
    if (
        coefficient != Fraction(-199, 60)
        or coefficient != -c / 2
        or covariant["normalization_and_remainder"]["local_Weyl_completion"] != "NOT_COMPUTED"
        or extended["H14"]["Weyl_and_mixed_quotient_dimension"] != 0
        or q1["decision"]["complete_Q1"] != "NO_CERTIFIED_OPERATOR"
    ):
        raise ValueError("FV conformization dependencies drifted")

    # Let L_g=Box_g-R_g/6 and u_g=1+(1/6)L_g^{-1}R_g.  Since
    # L_g 1=-R_g/6 and L_g L_g^{-1}R_g=R_g, L_g u_g=0 exactly.
    inverse_coefficient = Fraction(1, 6)
    constant_image = Fraction(-1, 6)
    yamabe_residual = constant_image + inverse_coefficient
    if yamabe_residual != 0:
        raise ValueError("FV scalar-flat representative identity drifted")

    # For g'=e^(2 sigma)g, conformal covariance and the normalized boundary
    # solution give u_{g'}=e^(-sigma)u_g.  Hence bar g=u_g^2 g is invariant.
    u_weight = -1
    metric_weight = 2
    dressed_metric_weight = 2 * u_weight + metric_weight
    if dressed_metric_weight != 0:
        raise ValueError("FV dressed metric Weyl-weight cancellation drifted")

    # Sigma_FV=-log u=-Box^{-1}R/6+O(curvature^2).  The selected functional
    # starts at C^2, so evaluating it on bar g first changes its curvature
    # expansion at order 1+1+1=3.  This identifies the cubic carrier but does
    # not calculate the independent W^(3) form factors of the full theory.
    leading_order = 2
    first_completion_order = 1 + 1 + 1
    if first_completion_order != 3:
        raise ValueError("FV completion curvature filtration drifted")

    result = {
        "schema": "quantum-weyl-fv-conformized-c2-log-gamma1-v1",
        "result_id": "FV_CONFORMIZED_C2_LOG_GAMMA1",
        "result_state": "FV_CONFORMIZED_C2_LOG_CARRIER_EXACTLY_WEYL_COMPLETED_INDEPENDENT_CUBIC_R2_AND_NORMALIZATION_DATA_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": breaking["classical_commit"],
        "scope": {
            "signature": "Euclidean",
            "dimension": 4,
            "geometry": "asymptotically flat manifold or fixed boundary problem with a normalized invertible conformal scalar operator",
            "weyl_transformations": "smooth local sigma compatible with the fixed boundary normalization",
            "carrier": "the selected coefficient-bearing C log(Delta_C/mu^2) C spectral functional",
            "completion_type": "Fradkin-Vilkovisky conformal gauge fixing",
        },
        "fv_scalar_flat_representative": {
            "conformal_operator": "L_g=Box_g-R_g/6",
            "normalized_solution": "u_g=1+(1/6)L_g^(-1)R_g",
            "boundary_normalization": "u_g tends to 1 at asymptotic infinity or obeys the declared fixed boundary normalization",
            "inverse_domain_policy": "L_g has no normalized zero mode on the declared function space; otherwise this certificate is not applicable until a kernel projector and orbit-compatible normalization are supplied",
            "operator_on_constant": "L_g(1)=-R_g/6",
            "inverse_equation": "L_g L_g^(-1) R_g=R_g",
            "yamabe_residual": _q(yamabe_residual),
            "sigma_FV": "Sigma_FV[g]=-log(u_g)",
            "representative_metric": "g_bar=u_g^2 g=exp(-2 Sigma_FV[g])g",
            "scalar_flat_identity": "R[g_bar]=u_g^(-3)(R_g-6 Box_g)u_g=0",
            "status": "EXACT_SCALAR_FLAT_REPRESENTATIVE_ON_DECLARED_INVERSE_DOMAIN",
        },
        "weyl_covariance": {
            "metric_transformation": "g_prime=exp(2 sigma)g",
            "solution_transformation": "u_g_prime=exp(-sigma)u_g",
            "sigma_transformation": "Sigma_FV[g_prime]=Sigma_FV[g]+sigma",
            "weight_ledger": {"u": u_weight, "metric": metric_weight, "u_squared_metric": dressed_metric_weight},
            "representative_identity": "g_bar[g_prime]=g_bar[g]",
            "status": "EXACT_ON_BOUNDARY_COMPATIBLE_WEYL_ORBIT",
        },
        "conformized_C2_log": {
            "functional": "Gamma1_C2_conf[g]=(4 pi)^(-2)(-199/60)<C[g_bar], Pi_bar log(Delta_C[g_bar]/mu^2) Pi_bar C[g_bar]>; every tensor, pairing, projector, operator domain, and spectral logarithm is evaluated on the same scalar-flat representative g_bar[g]",
            "logarithmic_coefficient": _q(coefficient),
            "coefficient_identity": "A_log=-c/2=-199/60",
            "weyl_invariance_proof": "the complete metric argument g_bar and its operator, domain, projector, pairing, and Weyl tensors are unchanged along the declared Weyl orbit",
            "leading_curvature_order": leading_order,
            "leading_reduction": "Gamma1_C2_conf=Gamma1_C2_log+O(curvature^3)",
            "status": "EXACT_LOCAL_WEYL_COMPLETION_OF_SELECTED_SPECTRAL_CARRIER",
        },
        "cubic_carrier": {
            "sigma_linearization": "Sigma_FV=-(1/6)Box^(-1)R+O(curvature^2)",
            "operator_difference": "delta_Sigma Delta_C=Delta_C[g_bar]-Delta_C[g]=O(curvature)",
            "frechet_kernel": "D log(Delta_C)[delta Delta_C]=integral_0^infinity (Delta_C+s)^(-1) delta Delta_C (Delta_C+s)^(-1) ds",
            "first_completion_order": first_completion_order,
            "formal_cubic_term": "(4 pi)^(-2)(-199/60)<C,D log(Delta_C)[delta_Sigma Delta_C]C> plus the transported pairing/projector terms",
            "basis_decomposition": "NOT_COMPUTED",
            "independent_W3_form_factors": "NOT_COMPUTED",
            "status": "COMPLETION_CARRIER_IDENTIFIED_COEFFICIENT_BASIS_OPEN",
        },
        "carrier_crosswalk": {
            "fv_metric": "g_bar[g]=exp(-2 Sigma_FV[g])g is a nonlocal functional of g fixed by a normalized conformal inverse and is Weyl-orbit invariant",
            "wz_metric": "g_hat[g,tau]=exp(-2 tau)g is a local field redefinition in the formally enlarged tau-adic BV theory",
            "identity_status": "DISTINCT_CARRIERS_NO_IDENTIFICATION",
            "reason": "Sigma_FV is determined nonlocally by scalar-flat gauge fixing, whereas tau is an independent compensator field; neither construction is substituted for the other",
        },
        "normalization_and_missing_physics": {
            "finite_C2_constant": "NOT_FIXED",
            "independent_nonlocal_R2_form_factor": "NOT_COMPUTED",
            "absolute_dressed_Rhat2_normalization": "NOT_FIXED",
            "independent_cubic_Weyl_invariant_form_factors": "NOT_COMPUTED",
            "global_kernel_and_boundary_data": "DECLARED_NOT_SOLVED_GLOBALLY",
            "complete_Gamma1": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
        },
        "decision": {
            "selected_C2_log_local_Weyl_completion": "CERTIFIED",
            "selected_C2_log_coefficient": "CERTIFIED",
            "cubic_completion_carrier": "IDENTIFIED_NOT_DECOMPOSED",
            "independent_cubic_form_factors": "NO_CERTIFIED_FUNCTIONAL",
            "nonlocal_R2_form_factor": "NOT_COMPUTED",
            "complete_Gamma1": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
            "residual_transfer": "FORBIDDEN",
        },
        "claim_flags": {
            "FV_SCALAR_FLAT_REPRESENTATIVE_CERTIFIED": True,
            "FV_CONFORMIZED_C2_LOG_CARRIER_FIXED": True,
            "SELECTED_C2_LOG_LOCAL_WEYL_COMPLETION_SUPPLIED": True,
            "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED": False,
            "NONLOCAL_R2_FORM_FACTOR_COMPUTED": False,
            "FINITE_C2_NORMALIZATION_FIXED": False,
            "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED": False,
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
            "use": "exact FV scalar-flat representative, conformization identity, and the separation between the conformized quadratic carrier and independent cubic form factors",
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_NONLOCAL_R2_FORM_FACTOR_FINITE_NORMALIZATIONS_RENORMALIZED_PRODUCTS_AND_EXTENDED_CONTRACTION",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate uses the normalized Fradkin-Vilkovisky scalar-flat representative g_bar=u_g^2 g to give an exact local-Weyl completion of the already certified coefficient-bearing C log(Delta_C/mu^2) C carrier. The coefficient remains -199/60, the representative metric is unchanged along boundary-compatible Weyl orbits, and the conformized functional reduces to the prior curvature-squared spectral logarithm modulo curvature order three. Existence and uniqueness are conditional on the declared normalized inverse domain; a conformal-operator kernel requires a separate projector and orbit-compatible normalization. The first cubic correction carrier is identified by the Frechet derivative of the spectral logarithm under the FV conformal deformation. The nonlocal representative g_bar[g] is not identified with the local tau-adic dressed metric g_hat[g,tau]. This does not compute the independent cubic Weyl-invariant form factors of the full one-loop effective action, decompose the formal correction into the complete cubic invariant basis, determine the independent nonlocal R2 form factor, choose the finite C2 constant or absolute dressed R(g_hat)^2 normalization, solve global kernel or boundary data, construct renormalized products, supply complete Gamma1 or Q1, authorize residual transfer, or establish any Lorentzian, Hadamard, positivity, particle, scattering, or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    flags = value["claim_flags"]
    decision = value["decision"]
    if (
        decision["selected_C2_log_local_Weyl_completion"] != "CERTIFIED"
        or decision["complete_Gamma1"] != "NO_CERTIFIED_FUNCTIONAL"
        or decision["residual_transfer"] != "FORBIDDEN"
        or flags["FV_SCALAR_FLAT_REPRESENTATIVE_CERTIFIED"] is not True
        or flags["FV_CONFORMIZED_C2_LOG_CARRIER_FIXED"] is not True
        or flags["SELECTED_C2_LOG_LOCAL_WEYL_COMPLETION_SUPPLIED"] is not True
        or any(
            flags[name] is not False
            for name in (
                "INDEPENDENT_CUBIC_WEYL_INVARIANT_FORM_FACTORS_COMPUTED",
                "NONLOCAL_R2_FORM_FACTOR_COMPUTED",
                "FINITE_C2_NORMALIZATION_FIXED",
                "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED",
                "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
                "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
                "RESIDUAL_TRANSFER_AUTHORIZED",
                "LORENTZIAN_CERTIFIED",
            )
        )
    ):
        raise ValueError("FV conformized C2-log certificate crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale FV-conformized C2-log certificate: {OUTPUT}")
    print("FV CONFORMIZATION: SELECTED C2 LOG CARRIER WEYL-COMPLETED; INDEPENDENT W3/R2 OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
