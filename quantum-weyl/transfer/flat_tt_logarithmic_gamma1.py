#!/usr/bin/env python3
"""Certify the universal one-loop logarithmic C2 form factor on flat TT data."""

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
OUTPUT = HERE / "certificates/FLAT_TT_LOGARITHMIC_GAMMA1.json"
SCHEMA = HERE / "schema/flat-tt-logarithmic-gamma1-v1.schema.json"
DEPENDENCIES = {
    "regulated_breaking": ROOT / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "background_coefficients": ROOT / "quantum-weyl/spectral/euclidean/certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json",
    "Q1_disposition": ROOT / "quantum-weyl/transfer/certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json",
    "anomaly_induced_Gamma1": ROOT / "quantum-weyl/transfer/certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
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


def _flat_tt_curvature_response() -> tuple[Fraction, Fraction, Fraction]:
    """Return C1^2, R1 and R1^2 for the normalized p=(1,0,0,0) TT fixture."""

    dimension = 4
    momentum = [Fraction(1), Fraction(), Fraction(), Fraction()]
    h = [
        [Fraction(), Fraction(), Fraction(), Fraction()],
        [Fraction(), Fraction(1), Fraction(), Fraction()],
        [Fraction(), Fraction(), Fraction(-1), Fraction()],
        [Fraction(), Fraction(), Fraction(), Fraction()],
    ]
    riemann: dict[tuple[int, int, int, int], Fraction] = {}
    for a in range(dimension):
        for b in range(dimension):
            for c_index in range(dimension):
                for d in range(dimension):
                    riemann[a, b, c_index, d] = Fraction(1, 2) * (
                        momentum[c_index] * momentum[b] * h[a][d]
                        + momentum[d] * momentum[a] * h[b][c_index]
                        - momentum[d] * momentum[b] * h[a][c_index]
                        - momentum[c_index] * momentum[a] * h[b][d]
                    )
    ricci = [
        [
            sum((riemann[a, b, a, d] for a in range(dimension)), Fraction())
            for d in range(dimension)
        ]
        for b in range(dimension)
    ]
    scalar = sum((ricci[index][index] for index in range(dimension)), Fraction())
    riemann_squared = sum((entry * entry for entry in riemann.values()), Fraction())
    ricci_squared = sum((entry * entry for row in ricci for entry in row), Fraction())
    c_squared = riemann_squared - 2 * ricci_squared + Fraction(1, 3) * scalar * scalar
    return c_squared, scalar, scalar * scalar


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    breaking = values["regulated_breaking"]
    background = values["background_coefficients"]
    q1 = values["Q1_disposition"]
    anomaly_induced = values["anomaly_induced_Gamma1"]

    c = Fraction(
        breaking["coefficients"]["ANOM_OMEGA_C2"]["numerator"],
        breaking["coefficients"]["ANOM_OMEGA_C2"]["denominator"],
    )
    beta2 = Fraction(background["coefficient_calculation"]["derived_beta2_equals_2c"])
    if (
        c != Fraction(199, 30)
        or beta2 != Fraction(199, 15)
        or beta2 != 2 * c
        or q1["finite_counterterm_ambiguity"]["bulk_quadratic_response_matrix"][0][0]
        != _q(Fraction(1))
        or anomaly_induced["decision"]["complete_finite_nonlocal_Gamma1"]
        != "NO_CERTIFIED_FUNCTIONAL"
    ):
        raise ValueError("flat-TT logarithmic Gamma1 inputs drifted")

    c2_response, scalar_linear, scalar_squared = _flat_tt_curvature_response()
    if (c2_response, scalar_linear, scalar_squared) != (
        Fraction(1),
        Fraction(),
        Fraction(),
    ):
        raise ValueError("normalized flat-TT curvature fixture drifted")

    # With delta_sigma g=2 sigma g, p^2 -> exp(-2 sigma) p^2.
    # Therefore delta_sigma log(p^2/mu^2)=-2 sigma.  The coefficient
    # A=-c/2 gives (-2)A=c, exactly the certified C2 anomaly coordinate.
    logarithmic_coefficient = -c / 2
    scale_kernel_derivative = Fraction(-2)
    scale_response = logarithmic_coefficient * scale_kernel_derivative
    if (
        logarithmic_coefficient != Fraction(-199, 60)
        or logarithmic_coefficient != -beta2 / 4
        or scale_response != c
    ):
        raise ValueError("universal logarithmic coefficient solve drifted")

    result = {
        "schema": "quantum-weyl-flat-tt-logarithmic-gamma1-v1",
        "result_id": "FLAT_TT_LOGARITHMIC_GAMMA1",
        "result_state": "FLAT_TT_UNIVERSAL_LOGARITHMIC_GAMMA1_FORM_FACTOR_CERTIFIED_FINITE_CONSTANT_AND_CURVED_COMPLETION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": breaking["classical_commit"],
        "scope": {
            "signature": "Euclidean",
            "background": "flat R4 momentum-space local fixture",
            "carrier": "nonzero-momentum real transverse-traceless metric perturbation",
            "momentum_domain": "p_squared>0",
            "normalization": "the p=(1,0,0,0), h_11=1, h_22=-1 fixture has integral C1^2 coefficient one",
        },
        "flat_TT_fixture": {
            "momentum": [1, 0, 0, 0],
            "polarization": [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 0]],
            "C1_squared_response": _q(c2_response),
            "R1_response": _q(scalar_linear),
            "R1_squared_response": _q(scalar_squared),
            "anomaly_induced_Riegert_pure_TT_onset": "O(h^4)",
            "onset_reason": "C2 and Ecal4 begin at O(h^2) on the pure TT slice, while R1=0",
        },
        "exact_logarithmic_form_factor": {
            "kappa": "(4 pi)^(-2)",
            "functional": "Gamma1_TT_log=kappa[-(199/60)<C1,log(p^2/mu^2)C1>+z_C(mu)<C1,C1>]",
            "anomaly_C2_coefficient_c": _q(c),
            "heat_kernel_beta2": _q(beta2),
            "logarithmic_coefficient": _q(logarithmic_coefficient),
            "coefficient_identities": ["A_log=-c/2", "A_log=-beta2/4"],
            "log_kernel_mu_derivative": _q(scale_kernel_derivative),
            "RG_scale_response": _q(scale_response),
            "global_Weyl_response": _q(scale_response),
            "scheme_independent_difference": "F_C(p^2;mu)-F_C(q^2;mu)=-(199/60) log(p^2/q^2)",
            "status": "UNIVERSAL_MOMENTUM_DEPENDENCE_AND_SCALE_RESPONSE_CERTIFIED",
        },
        "finite_normalization_family": {
            "form_factor": "F_C(p^2;mu)=-(199/60)log(p^2/mu^2)+z_C(mu)",
            "reference_condition": "F_C(kappa_ref^2;mu)=N_C",
            "solution": "z_C(mu)=N_C+(199/60)log(kappa_ref^2/mu^2)",
            "running_at_fixed_N_C_and_kappa_ref": "mu d z_C/d mu=-199/30",
            "RG_cancellation": "mu d F_C/d mu=199/30+mu d z_C/d mu=0 after the reference condition is imposed",
            "N_C": "NOT_FIXED",
            "kappa_ref": "NOT_FIXED",
            "finite_C2_constant": "NOT_FIXED",
        },
        "excluded_promotions": {
            "zero_momentum": "OPEN_IR_ZERO_MODE_LOG_UNDEFINED",
            "general_curved_background_form_factor": "NOT_COMPUTED",
            "higher_curvature_Weyl_invariant_remainder": "NOT_COMPUTED",
            "finite_R2_normalization": "NOT_FIXED",
            "Lorentzian_analytic_continuation_and_branch_cut": "NOT_COMPUTED",
            "renormalized_BV_laplacian_or_time_ordered_product": "NOT_SUPPLIED",
            "extended_classical_residual_contraction": "NOT_SUPPLIED",
        },
        "decision": {
            "flat_TT_universal_logarithmic_form_factor": "CERTIFIED",
            "complete_Weyl_invariant_remainder": "NO_CERTIFIED_FUNCTIONAL",
            "complete_finite_nonlocal_Gamma1": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
            "residual_transfer": "FORBIDDEN",
            "Bridge_4": "NO_CERTIFIED_MAP",
            "Bridge_5": "NO_CERTIFIED_MAP_BRIDGE_2_ABSENT",
        },
        "claim_flags": {
            "FLAT_TT_LOG_COEFFICIENT_FIXED": True,
            "SCHEME_INDEPENDENT_MOMENTUM_DIFFERENCE_FIXED": True,
            "FINITE_C2_NORMALIZATION_FIXED": False,
            "GENERAL_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
        },
        "source_provenance": {
            "structural_reference": {
                "authors": ["A. O. Barvinsky", "W. Wachowski"],
                "title": "Notes on conformal anomaly, nonlocal effective action and the metamorphosis of the running scale",
                "arxiv": "2306.03780v3",
                "url": "https://arxiv.org/abs/2306.03780",
                "use": "separation of anomaly-induced and conformal parts and the role of logarithmic nonlocal curvature form factors",
            }
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "CURVED_WEYL_INVARIANT_GAMMA1_REMAINDER_FINITE_C2_R2_NORMALIZATION_AND_EXTENDED_CLASSICAL_CONTRACTION",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate fixes the "
            "universal scale-dependent quadratic C2 form factor on the declared "
            "nonzero-momentum flat Euclidean TT carrier. Exact repository normalization "
            "gives A_log=-c/2=-199/60=-beta2/4, so differentiation of "
            "log(p^2/mu^2) reproduces the certified c=199/30 coordinate and the "
            "scheme-independent difference between two positive momenta is fixed. The "
            "additive local C2 constant remains an unfixed normalization condition. "
            "This scoped result does not construct a general curved-background conformal "
            "form factor, higher-curvature Weyl-invariant remainder, zero-momentum "
            "definition, finite R2 normalization, Lorentzian analytic continuation, "
            "renormalized BV Laplacian or time-ordered product, compensator-inclusive "
            "classical contraction, complete Gamma1 or Q1, residual transfer, a "
            "Hadamard state, Bridge 4, Bridge 5, or a particle interpretation."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    flags = value.get("claim_flags", {})
    decision = value.get("decision", {})
    form_factor = value.get("exact_logarithmic_form_factor", {})
    if (
        form_factor.get("status")
        != "UNIVERSAL_MOMENTUM_DEPENDENCE_AND_SCALE_RESPONSE_CERTIFIED"
        or decision.get("complete_Weyl_invariant_remainder")
        != "NO_CERTIFIED_FUNCTIONAL"
        or decision.get("complete_Q1") != "NO_CERTIFIED_OPERATOR"
        or decision.get("residual_transfer") != "FORBIDDEN"
        or flags.get("FLAT_TT_LOG_COEFFICIENT_FIXED") is not True
        or flags.get("FINITE_C2_NORMALIZATION_FIXED") is not False
        or flags.get("GENERAL_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED") is not False
        or flags.get("COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED") is not False
        or flags.get("COMPLETE_RENORMALIZED_Q1_SUPPLIED") is not False
        or flags.get("RESIDUAL_TRANSFER_AUTHORIZED") is not False
    ):
        raise ValueError("flat-TT logarithmic Gamma1 certificate crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale flat-TT logarithmic Gamma1 certificate: {OUTPUT}")
    print("FLAT-TT GAMMA1: UNIVERSAL LOG COEFFICIENT -199/60 CERTIFIED; FINITE CONSTANT OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
