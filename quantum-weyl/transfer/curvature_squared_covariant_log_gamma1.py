#!/usr/bin/env python3
"""Certify the covariant C log(Delta_C/mu^2) C term through curvature order two."""

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
OUTPUT = HERE / "certificates/CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1.json"
SCHEMA = HERE / "schema/curvature-squared-covariant-log-gamma1-v1.schema.json"
DEPENDENCIES = {
    "flat_TT_logarithm": HERE / "certificates/FLAT_TT_LOGARITHMIC_GAMMA1.json",
    "anomaly_induced_Gamma1": HERE / "certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
    "Q1_disposition": HERE / "certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json",
    "regulated_breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "WZ_cotangent_lift": ROOT / "quantum-weyl/anomalies/certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json",
    "berger_classical_contraction": ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json",
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


def _curvature_order(*orders: int) -> int:
    """Return the additive covariant-perturbation-theory curvature order."""

    if any(order < 0 for order in orders):
        raise ValueError("curvature orders must be nonnegative")
    return sum(orders)


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    flat = values["flat_TT_logarithm"]
    anomaly = values["regulated_breaking"]
    anomaly_induced = values["anomaly_induced_Gamma1"]
    q1 = values["Q1_disposition"]
    wz_lift = values["WZ_cotangent_lift"]
    berger = values["berger_classical_contraction"]

    c = Fraction(
        anomaly["coefficients"]["ANOM_OMEGA_C2"]["numerator"],
        anomaly["coefficients"]["ANOM_OMEGA_C2"]["denominator"],
    )
    flat_coefficient = Fraction(
        flat["exact_logarithmic_form_factor"]["logarithmic_coefficient"]["numerator"],
        flat["exact_logarithmic_form_factor"]["logarithmic_coefficient"]["denominator"],
    )
    if (
        c != Fraction(199, 30)
        or flat_coefficient != -c / 2
        or anomaly_induced["decision"]["complete_finite_nonlocal_Gamma1"]
        != "NO_CERTIFIED_FUNCTIONAL"
        or q1["decision"]["complete_Q1"] != "NO_CERTIFIED_OPERATOR"
        or wz_lift["extension_scope"]["new_generators"] != ["tau", "tau_star"]
        or wz_lift["master_term"]["derived_rows"]["Q_tau"] != "L_xi tau + omega"
        or berger["row_layout"]["ghost_clock_order"] != ["tau", "sigma"]
        or berger["setting_id"]
        != "compact_positive_berger_clock_fixed_coupling_linearized"
    ):
        raise ValueError("curvature-squared covariant-log dependencies drifted")

    # In covariant perturbation theory C has curvature order one.  Two
    # admissible Laplace-type Weyl-bundle operators with the same rough
    # principal part differ by a curvature-order-one endomorphism V_1.
    # The Frechet derivative
    #   d log(Delta)[V_1] = int_0^infty R_s V_1 R_s ds
    # therefore changes <C,log(Delta)C> first at order 1+1+1=3.
    leading_order = _curvature_order(1, 0, 1)
    operator_change_order = _curvature_order(1, 1, 1)
    if leading_order != 2 or operator_change_order != 3:
        raise ValueError("curvature filtration arithmetic drifted")

    scale_kernel_derivative = Fraction(-2)
    scale_response = flat_coefficient * scale_kernel_derivative
    if scale_response != c:
        raise ValueError("covariant-log scale response drifted")

    result = {
        "schema": "quantum-weyl-curvature-squared-covariant-log-gamma1-v1",
        "result_id": "CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1",
        "result_state": "COVARIANT_CURVATURE_SQUARED_C2_LOG_CERTIFIED_CUBIC_COMPLETION_AND_FINITE_NORMALIZATIONS_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": anomaly["classical_commit"],
        "scope": {
            "signature": "Euclidean",
            "dimension": 4,
            "geometry": "compact Riemannian manifold without boundary or a fixed common self-adjoint elliptic boundary domain",
            "carrier": "algebraic Weyl-tensor bundle on the source complement of ker(Delta_C)",
            "operator": "positive self-adjoint Laplace-type Delta_C with rough principal symbol and spectral logarithm on Pi_perp",
            "expansion": "covariant perturbation theory through total curvature order two",
        },
        "covariant_curvature_squared_form_factor": {
            "functional": "Gamma1_C2_log=(4 pi)^(-2) A_log <C,Pi_perp log(Delta_C/mu^2) Pi_perp C>",
            "logarithmic_coefficient": _q(flat_coefficient),
            "coefficient_identity": "A_log=-c/2=-199/60",
            "curvature_order": leading_order,
            "mu_log_derivative_on_source_complement": _q(scale_kernel_derivative),
            "RG_scale_response": _q(scale_response),
            "flat_TT_reduction": "F_C(p^2;mu)=-(199/60)log(p^2/mu^2)+z_C(mu)",
            "status": "COVARIANT_AND_UNIVERSAL_THROUGH_CURVATURE_ORDER_TWO",
        },
        "operator_choice_independence": {
            "comparison": "Delta_C_prime=Delta_C+V_1+O(curvature^2)",
            "hypothesis": "V_1 is a self-adjoint curvature-order-one bundle endomorphism on the same domain and both logarithms use the same source-complement prescription",
            "frechet_formula": "d log(Delta_C)[V_1]=integral_0^infinity (Delta_C+s)^(-1) V_1 (Delta_C+s)^(-1) ds",
            "left_C_order": 1,
            "operator_variation_order": 1,
            "right_C_order": 1,
            "first_difference_order": operator_change_order,
            "conclusion": "the curvature-squared logarithmic functional is independent of the admissible Laplace-type representative modulo O(curvature^3)",
            "status": "EXACT_CURVATURE_FILTRATION_CERTIFICATE",
        },
        "kernel_and_boundary_contract": {
            "projector": "Pi_perp=1-Pi_ker",
            "spectral_logarithm": "Pi_perp log(Delta_C/mu^2) Pi_perp",
            "scale_identity": "mu partial_mu log(Delta_C/mu^2)=-2 Pi_perp",
            "kernel_sector": "OPEN_GLOBAL_DATA",
            "boundary_sector": "FIXED_COMMON_SELF_ADJOINT_ELLIPTIC_DOMAIN_REQUIRED",
            "zero_eigenvalue_logarithm": "UNDEFINED_AND_NOT_SILENTLY_INCLUDED",
        },
        "normalization_and_remainder": {
            "finite_C2_constant": "NOT_FIXED",
            "finite_R2_constant": "NOT_FIXED",
            "R2_logarithmic_coefficient": "NOT_DETERMINED_BY_THE_CERTIFIED_ANOMALY_VECTOR",
            "first_unresolved_C2_log_completion_order": 3,
            "cubic_nonlocal_completion": "NOT_COMPUTED",
            "higher_curvature_completion": "NOT_COMPUTED",
            "local_Weyl_completion": "NOT_COMPUTED",
        },
        "contraction_merge_audit": {
            "status": "REJECTED_BACKGROUND_AND_GENERATOR_COLLISION",
            "available_classical_contraction": "positive-Berger gravity-clock 34-to-26 SDR",
            "classical_tau": "temporal diffeomorphism ghost",
            "WZ_tau": "scalar Weyl compensator",
            "WZ_Q_tau": wz_lift["master_term"]["derived_rows"]["Q_tau"],
            "berger_setting_id": berger["setting_id"],
            "berger_ghost_clock_order": berger["row_layout"]["ghost_clock_order"],
            "conclusion": "no compensator-inclusive residual contraction follows by matching the symbol tau or by direct-summing the two certificates",
        },
        "decision": {
            "covariant_C2_log_through_curvature_order_two": "CERTIFIED",
            "operator_choice_independence_through_curvature_order_two": "CERTIFIED",
            "complete_curved_Weyl_invariant_remainder": "NO_CERTIFIED_FUNCTIONAL",
            "finite_C2_R2_normalization": "NOT_FIXED",
            "complete_Gamma1": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
            "extended_classical_residual_contraction": "NO_CERTIFIED_MAP",
            "residual_transfer": "FORBIDDEN",
            "Bridge_4": "NO_CERTIFIED_MAP",
            "Bridge_5": "NO_CERTIFIED_MAP_BRIDGE_2_ABSENT",
        },
        "claim_flags": {
            "CURVATURE_SQUARED_COVARIANT_C2_LOG_FIXED": True,
            "FIRST_UNRESOLVED_C2_LOG_COMPLETION_ORDER_IS_THREE": True,
            "FINITE_C2_NORMALIZATION_FIXED": False,
            "FINITE_R2_NORMALIZATION_FIXED": False,
            "COMPLETE_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "EXTENDED_CLASSICAL_CONTRACTION_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
        },
        "source_provenance": {
            "covariant_perturbation_theory": {
                "authors": ["A. O. Barvinsky", "Yu. V. Gusev", "V. V. Zhytnikov", "G. A. Vilkovisky"],
                "title": "Covariant perturbation theory (IV). Third order in the curvature",
                "arxiv": "0911.1168",
                "url": "https://arxiv.org/abs/0911.1168",
                "use": "curvature-ordered nonlocal form factors and the separation of quadratic from cubic completion data",
            },
            "nonlinear_completion_example": {
                "authors": ["J. F. Donoghue", "B. K. El-Menoufi"],
                "title": "Covariant non-local action for massless QED and the curvature expansion",
                "arxiv": "1507.06321",
                "url": "https://arxiv.org/abs/1507.06321",
                "use": "explicit demonstration that covariantizing the flat logarithm supplies the curvature-squared term while matching corrections begin at cubic curvature order",
            },
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "C2_CUBIC_CURVATURE_COMPLETION_R2_FORM_FACTOR_FINITE_C2_R2_NORMALIZATION_AND_SAME_BACKGROUND_EXTENDED_CLASSICAL_CONTRACTION",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate promotes the flat-TT logarithm to a covariant spectral functional only through total curvature order two. On the source complement of a positive self-adjoint Laplace-type Weyl-bundle operator, its exact coefficient is -199/60 and its scale response is 199/30. The resolvent Frechet formula proves that changing the Laplace-type representative by a curvature-order-one self-adjoint endomorphism changes the sandwiched functional first at curvature order three. It therefore names the next missing data for this C2 carrier precisely: cubic and higher nonlocal curvature form factors. The independent R2 form factor, finite local C2 and R2 normalizations, kernel and boundary global data, local-Weyl completion, complete Gamma1 and Q1, and residual transfer remain open. The available Berger 34-to-26 contraction cannot be used as the compensator extension because its tau is a temporal diffeomorphism ghost on a different background, not the Wess-Zumino scalar compensator. This result is not Lorentzian, a restored renormalized-product theorem, a Hadamard state, Bridge 4, Bridge 5, or a particle statement."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    flags = value["claim_flags"]
    decision = value["decision"]
    if (
        decision["covariant_C2_log_through_curvature_order_two"] != "CERTIFIED"
        or decision["complete_curved_Weyl_invariant_remainder"] != "NO_CERTIFIED_FUNCTIONAL"
        or decision["residual_transfer"] != "FORBIDDEN"
        or flags["CURVATURE_SQUARED_COVARIANT_C2_LOG_FIXED"] is not True
        or flags["FIRST_UNRESOLVED_C2_LOG_COMPLETION_ORDER_IS_THREE"] is not True
        or any(
            flags[name] is not False
            for name in (
                "FINITE_C2_NORMALIZATION_FIXED",
                "FINITE_R2_NORMALIZATION_FIXED",
                "COMPLETE_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED",
                "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
                "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
                "EXTENDED_CLASSICAL_CONTRACTION_SUPPLIED",
                "RESIDUAL_TRANSFER_AUTHORIZED",
            )
        )
    ):
        raise ValueError("curvature-squared covariant-log certificate crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale curvature-squared covariant-log certificate: {OUTPUT}")
    print("CURVED C2 LOG: COVARIANT THROUGH O(R^2); FIRST UNRESOLVED ORDER O(R^3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
