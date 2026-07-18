#!/usr/bin/env python3
"""Certify the raw BoxR coefficient and its repository scheme conversion.

The external analytic input is the zeta/proper-time conformal-transverse
calculation of Barvinsky--Camargo--Kalugin--Ohta--Shapiro.  This module does
not replay their universal functional traces.  It independently reconstructs
their final coefficient from the published tensor, gauge-weight and ghost
rows, then composes it with the repository's exact BRST primitive for
omega BoxR and with the anomaly-induced Gamma1 convention.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION.json"
SCHEMA = HERE / "schema/weyl-graviton-box-r-scheme-conversion-v1.schema.json"

DEPENDENCIES = {
    "regulated_breaking": ROOT
    / "quantum-weyl/anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json",
    "regularization_dependence": ROOT
    / "quantum-weyl/anomalies/certificates/REGULATED_SLAVNOV_REGULARIZATION_DEPENDENCE.json",
    "anomaly_induced_Gamma1": ROOT
    / "quantum-weyl/transfer/certificates/ANOMALY_INDUCED_NONLOCAL_GAMMA1.json",
    "Q1_disposition": ROOT
    / "quantum-weyl/transfer/certificates/ONE_LOOP_SLAVNOV_Q1_DISPOSITION.json",
    "even_local_quotient": ROOT
    / "quantum-weyl/local_bv/certificates/AFN0_H14_EVEN_CANONICAL_QUOTIENT.json",
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


def _linear(rational: Fraction, log_coefficient: Fraction) -> dict[str, Any]:
    """Represent rational + log_coefficient*log(3/2) exactly."""

    return {
        "basis": ["1", "log(3/2)"],
        "rational": _q(rational),
        "log_3_over_2": _q(log_coefficient),
    }


def _add(
    left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]
) -> tuple[Fraction, Fraction]:
    return left[0] + right[0], left[1] + right[1]


def _scale(
    scalar: Fraction, value: tuple[Fraction, Fraction]
) -> tuple[Fraction, Fraction]:
    return scalar * value[0], scalar * value[1]


def _alternating_log_bounds(terms: int = 4) -> tuple[Fraction, Fraction]:
    """Exact alternating-series bounds for log(1+1/2)."""

    if terms <= 0 or terms % 2:
        raise ValueError("an even positive truncation is required")
    partial = sum(
        (
            (Fraction(1) if index % 2 else Fraction(-1))
            * Fraction(1, index * 2**index)
            for index in range(1, terms + 1)
        ),
        Fraction(),
    )
    next_term = Fraction(1, (terms + 1) * 2 ** (terms + 1))
    return partial, partial + next_term


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    breaking = values["regulated_breaking"]
    regularization = values["regularization_dependence"]
    gamma1 = values["anomaly_induced_Gamma1"]
    q1 = values["Q1_disposition"]
    quotient = values["even_local_quotient"]

    exact_rows = quotient.get("exact_classes", [])
    box_row = next(
        (row for row in exact_rows if row.get("representative_id") == "ANOM_OMEGA_BOX_R"),
        None,
    )
    if (
        breaking["normalization"]["gauge"]
        != "conformal transverse gauge with exact Diff-Weyl scalar reduction"
        or breaking["coefficients"]["ANOM_OMEGA_BOX_R"] != _q(Fraction())
        or regularization["chosen_scheme"]
        != "BoxR=0 via the local R2 counterterm convention"
        or regularization["primitive"]
        != "(-1/12) R2 for omega BoxR in project conventions"
        or box_row is None
        or box_row["primitive_coefficient"] != _q(Fraction(-1, 12))
        or gamma1["exact_coefficient_solve"]["solution_vector"][2]
        != _q(Fraction(29, 120))
        or q1["finite_counterterm_ambiguity"]["bulk_response_rank"] != 2
    ):
        raise ValueError("BoxR scheme-conversion dependency drifted")

    # Published local heat-kernel rows in the source convention:
    #   tr a2^H = 13/135 BoxR,
    #   tr a2^Y = (911/720 - 8/3 log(3/2)) BoxR,
    #   tr a2^M = (247/540 - 5/12 log(3/2)) BoxR.
    # The fourth/second-order determinant weights are 2,-1,-2.
    tensor = (Fraction(13, 135), Fraction())
    gauge_weight = (Fraction(911, 720), Fraction(-8, 3))
    ghost = (Fraction(247, 540), Fraction(-5, 12))
    raw_box = _add(
        _add(_scale(Fraction(2), tensor), _scale(Fraction(-1), gauge_weight)),
        _scale(Fraction(-2), ghost),
    )
    if raw_box != (Fraction(-159, 80), Fraction(7, 2)):
        raise ValueError("published BoxR row reconstruction drifted")

    # Since s int R^2 = -12 int omega BoxR modulo d_h, adding z_R int R^2
    # changes the BoxR coordinate by -12 z_R.  Thus z_R=raw_box/12 maps the
    # raw zeta/proper-time scheme to the repository BoxR=0 scheme.
    r2_shift = _scale(Fraction(1, 12), raw_box)
    if r2_shift != (Fraction(-53, 320), Fraction(7, 24)):
        raise ValueError("R2 scheme-shift arithmetic drifted")

    euler = Fraction(-87, 20)
    raw_local_r2 = _scale(
        Fraction(-1, 36),
        _add(_scale(Fraction(3), raw_box), (2 * euler, Fraction())),
    )
    repository_local_r2 = _add(raw_local_r2, r2_shift)
    if (
        raw_local_r2 != (Fraction(391, 960), Fraction(-7, 24))
        or repository_local_r2 != (Fraction(29, 120), Fraction())
    ):
        raise ValueError("anomaly-induced R2 conversion drifted")

    lower, upper = _alternating_log_bounds(4)
    if not (
        lower == Fraction(77, 192)
        and upper == Fraction(391, 960)
        and lower > Fraction(2, 5)
        and upper < Fraction(41, 100)
        and Fraction(7, 2) * upper - Fraction(159, 80) < 0
    ):
        raise ValueError("exact sign bound for raw BoxR coefficient drifted")

    result = {
        "schema": "quantum-weyl-graviton-box-r-scheme-conversion-v1",
        "result_id": "WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION",
        "result_state": "RAW_ZETA_BOX_R_COEFFICIENT_AND_REPOSITORY_BOXR_ZERO_R2_CONVERSION_CERTIFIED_NONLOCAL_R2_FORM_FACTOR_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": breaking["classical_commit"],
        "scope": {
            "signature": "Euclidean",
            "theory": "strict four-dimensional Weyl-squared quantum gravity",
            "gauge": "minimal conformal-transverse background gauge with traceless metric fluctuation",
            "regularization": "zeta-functional or covariant proper-time local heat-kernel prescription",
            "boundary": "local bulk density; integrated BoxR boundary contribution kept separate",
            "normalization": "overall (4 pi)^(-2); project Weyl convention delta_sigma g=2 sigma g",
        },
        "external_analytic_input": {
            "authors": [
                "A. O. Barvinsky",
                "G. H. S. Camargo",
                "A. E. Kalugin",
                "N. Ohta",
                "I. L. Shapiro",
            ],
            "title": "On the local term in the anomaly-induced action of Weyl quantum gravity",
            "arxiv": "2308.05251v2",
            "url": "https://arxiv.org/abs/2308.05251",
            "imported_equations": ["tr a2^H", "tr a2^Y", "tr a2^M", "2H-Y-2M", "raw BoxR coefficient"],
            "C2_convention_guard": "the source 199/15 coefficient is repository beta2=2c; it is not imported as a replacement for the certified c=199/30 anomaly coordinate",
            "E4_convention_check": "the source -87/20 coordinate agrees with the repository E4 coordinate",
            "BoxR_convention_map": "the source and repository both use -2 g_(mu nu) delta/delta g_(mu nu) integral R2=12 BoxR",
            "source_calculation_replayed": False,
            "reason": "the universal functional-trace derivation is imported; its exact final-row arithmetic and repository convention map are independently replayed here",
        },
        "heat_kernel_row_reconstruction": {
            "basis": ["1", "log(3/2)"],
            "tensor_H": _linear(*tensor),
            "gauge_weight_Y": _linear(*gauge_weight),
            "diffeomorphism_ghost_M": _linear(*ghost),
            "determinant_weights": {"H": 2, "Y": -1, "M": -2},
            "sum_rule": "2 tr(a2^H)-tr(a2^Y)-2 tr(a2^M)",
            "raw_BoxR_coefficient": _linear(*raw_box),
            "raw_anomaly": "(4 pi)^(-2)[(7/2)log(3/2)-159/80] BoxR",
        },
        "exact_nonzero_sign_witness": {
            "series": "log(3/2)=sum_(n>=1)(-1)^(n+1)/(n 2^n)",
            "even_truncation_terms": 4,
            "lower_bound": _q(lower),
            "upper_bound": _q(upper),
            "coarse_bounds": "2/5 < log(3/2) < 41/100",
            "raw_coefficient_sign": "STRICTLY_NEGATIVE",
        },
        "repository_scheme_conversion": {
            "BRST_primitive": "omega BoxR=-(1/12) s(R2) modulo d_h",
            "coordinate_law": "b_Box -> b_Box-12 z_R under Gamma1 -> Gamma1+z_R integral R2",
            "raw_to_BoxR_zero_counterterm": _linear(*r2_shift),
            "counterterm_formula": "z_R=(7/24)log(3/2)-53/320",
            "reconstructed_BoxR_coordinate": _linear(Fraction(), Fraction()),
            "C2_E4_and_parity_odd_coordinates_unchanged": True,
            "all_loop_theory_equivalence": False,
            "all_loop_boundary": "adding strict-metric R2 changes the scalar dynamics beyond the one-loop scheme conversion and is not an equivalence theorem for fixed-field-content Weyl gravity",
        },
        "anomaly_induced_local_R2_cross_check": {
            "general_law": "z_R,induced=-(3 b_Box+2 b_E4)/36",
            "Euler_coordinate": _q(euler),
            "raw_scheme_local_R2_coefficient": _linear(*raw_local_r2),
            "raw_scheme_formula": "391/960-(7/24)log(3/2)",
            "plus_scheme_conversion": _linear(*r2_shift),
            "repository_BoxR_zero_coefficient": _linear(*repository_local_r2),
            "repository_target": _q(Fraction(29, 120)),
            "status": "EXACT_MATCH",
        },
        "distinct_R2_directions": {
            "strict_metric_R2": "conformally noninvariant counterterm changing the exact omega BoxR coordinate",
            "dressed_Rhat2": "BRST-invariant H04 class in the tau-adic compensator theory changing Q1 without changing the strict BoxR coordinate",
            "nonlocal_R2_form_factor": "finite momentum-dependent Weyl-invariant remainder requiring the full off-shell determinant expansion",
            "conflation_forbidden": True,
        },
        "minimal_missing_form_factor_theorem": {
            "result": "NONLOCAL_R2_FORM_FACTOR_NOT_DETERMINED_BY_LOCAL_A2_OR_ANOMALY_DATA",
            "reason": "the local a2 rows fix the BoxR anomaly and its local R2 integration term but not the finite momentum-dependent form factor",
            "required_calculation": "covariant nonlocal curvature expansion for the minimal fourth-order traceless-tensor operator together with both nonminimal second-order vector determinants in the matched gauge and measure",
            "current_repository_carrier": "local heat-kernel coefficient and Einstein-background factor ledger only",
        },
        "decision": {
            "raw_zeta_BoxR_coefficient": "COEFFICIENT_COMPUTED",
            "repository_BoxR_zero_scheme_conversion": "CERTIFIED",
            "relative_strict_R2_normalization": "FIXED_BETWEEN_RAW_ZETA_AND_REPOSITORY_BOXR_ZERO_SCHEMES",
            "absolute_dressed_Rhat2_normalization": "NOT_FIXED",
            "nonlocal_R2_form_factor": "NOT_COMPUTED",
            "complete_Gamma1": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
            "residual_transfer": "FORBIDDEN",
        },
        "claim_flags": {
            "RAW_ZETA_BOXR_COEFFICIENT_COMPUTED": True,
            "RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED": True,
            "REPOSITORY_29_OVER_120_LOCAL_R2_REPRODUCED": True,
            "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED": False,
            "NONLOCAL_R2_FORM_FACTOR_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "COVARIANT_NONLOCAL_R2_FORM_FACTOR_AND_C2_CUBIC_COMPLETION",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate imports the "
            "published zeta/proper-time universal-functional-trace result for the raw "
            "BoxR coefficient and independently replays its exact H/Y/M arithmetic. "
            "It composes that coefficient with the repository primitive "
            "omega BoxR=-(1/12)s(R2) modulo d_h, fixes the relative strict-metric R2 "
            "counterterm between the raw and BoxR=0 schemes, and exactly reproduces "
            "the stored 29/120 anomaly-induced local R2 coefficient. It does not "
            "rederive the source functional traces, fix the independent dressed "
            "R(g_hat)^2 finite counterterm, compute a finite momentum-dependent R2 "
            "form factor or the cubic C2 completion, supply complete Gamma1 or Q1, "
            "authorize residual transfer, identify the two schemes as all-loop-equivalent "
            "strict theories, or establish a Lorentzian result."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    flags = value["claim_flags"]
    decision = value["decision"]
    if (
        decision["raw_zeta_BoxR_coefficient"] != "COEFFICIENT_COMPUTED"
        or decision["repository_BoxR_zero_scheme_conversion"] != "CERTIFIED"
        or decision["nonlocal_R2_form_factor"] != "NOT_COMPUTED"
        or flags["RAW_ZETA_BOXR_COEFFICIENT_COMPUTED"] is not True
        or flags["RAW_TO_REPOSITORY_R2_SCHEME_SHIFT_FIXED"] is not True
        or flags["REPOSITORY_29_OVER_120_LOCAL_R2_REPRODUCED"] is not True
        or any(
            flags[name] is not False
            for name in (
                "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED",
                "NONLOCAL_R2_FORM_FACTOR_COMPUTED",
                "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
                "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
                "RESIDUAL_TRANSFER_AUTHORIZED",
            )
        )
    ):
        raise ValueError("BoxR scheme certificate crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale BoxR scheme-conversion certificate: {OUTPUT}")
    print("WEYL BOXR: RAW ZETA COEFFICIENT AND EXACT BOXR=0 R2 CONVERSION CERTIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
