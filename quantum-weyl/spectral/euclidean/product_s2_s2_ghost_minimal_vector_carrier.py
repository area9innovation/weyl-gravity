#!/usr/bin/env python3
"""Exact minimal-vector relative determinant carrier on S2(1) x S2(2)."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .product_s2_s2_ghost_schur_spectral_carrier import _mode


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_CARRIER.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-minimal-vector-carrier-v1.schema.json"
DEPENDENCY = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_SPECTRAL_CARRIER.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _vector_mode(ell: int, emm: int) -> dict[str, Any]:
    scalar = _mode(Fraction(1), Fraction(2), ell, emm)
    if scalar["status"] == "ABSENT_CONSTANT_GRADIENT":
        return {"ell": ell, "m": emm, "status": "ABSENT_CONSTANT_ONE_FORM"}
    lam = _fraction(scalar["lambda"])
    factors = []
    if ell:
        factors.append(("first", Fraction(2), ell == 1 and emm == 0))
    if emm:
        factors.append(("second", Fraction(4), emm == 1 and ell == 0))
    regular_ratio = Fraction(1)
    polarizations = []
    for name, shift, exceptional in factors:
        ratio = (lam - shift) / lam
        if exceptional:
            polarizations.extend(
                [
                    {
                        "factor": name,
                        "polarization": "exact",
                        "status": "MATCHED_WITH_SCHUR_POLE",
                        "A_eigenvalue": _q(0),
                        "F_eigenvalue": _q(lam),
                    },
                    {
                        "factor": name,
                        "polarization": "coexact",
                        "status": "KILLING_ZERO_PRIMED_OUT",
                        "A_eigenvalue": _q(0),
                        "F_eigenvalue": _q(lam),
                    },
                ]
            )
        else:
            regular_ratio *= ratio**2
            for polarization in ("exact", "coexact"):
                polarizations.append(
                    {
                        "factor": name,
                        "polarization": polarization,
                        "status": "REGULAR",
                        "A_eigenvalue": _q(lam - shift),
                        "F_eigenvalue": _q(lam),
                        "relative_eigenvalue": _q(ratio),
                    }
                )
    result = {
        "ell": ell,
        "m": emm,
        "degeneracy": scalar["degeneracy"],
        "lambda": scalar["lambda"],
        "polarizations": polarizations,
    }
    if any(item["status"] != "REGULAR" for item in polarizations):
        result.update(
            {
                "status": "EXCEPTIONAL_EXACT_SCHUR_MATCH_COEXACT_KILLING_PRIME",
                "regular_minimal_vector_ratio": None,
                "paired_exact_vector_times_schur_ratio": scalar["paired_vector_times_schur_ratio"],
            }
        )
    else:
        schur = _fraction(scalar["schur_eigenvalue"])
        result.update(
            {
                "status": "REGULAR",
                "regular_minimal_vector_ratio": _q(regular_ratio),
                "full_vector_times_schur_ratio": _q(regular_ratio * schur),
            }
        )
    return result


def build() -> dict[str, Any]:
    source = json.loads(DEPENDENCY.read_text())
    if (
        source["claim_flags"]["PRODUCT_SPECTRAL_MEASURE_SUPPLIED"] is not True
        or source["primed_mode_policy"]["total_exceptional_correction"] != "3^-6"
    ):
        raise ValueError("product Schur carrier dependency drifted")
    modes = [_vector_mode(ell, emm) for ell, emm in [(1, 0), (0, 1), (2, 0), (0, 2), (1, 1), (2, 1)]]
    exceptional = [row for row in modes if row["status"].startswith("EXCEPTIONAL")]
    if sum(row["degeneracy"] for row in exceptional) != 6:
        raise AssertionError("product Killing/exact exceptional dimension drifted")
    scalar_a0 = Fraction(1, 2)
    wres_inverse_square = 2 * scalar_a0
    defects = {
        "first_factor_one_polarization": -Fraction(2**2, 4) * wres_inverse_square,
        "second_factor_one_polarization": -Fraction(4**2, 4) * wres_inverse_square,
    }
    total_defect = 2 * sum(defects.values(), Fraction(0))
    if total_defect != -10:
        raise AssertionError("minimal-vector zeta/weighted defect drifted")
    result = {
        "schema": "quantum-weyl-product-s2-s2-ghost-minimal-vector-carrier-v1",
        "result_id": "PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_CARRIER",
        "result_state": "MINIMAL_VECTOR_EXACT_COEXACT_SPECTRUM_AND_PRIMING_COMPUTED",
        "lifecycle_state": "COMPLETE_MODE_CARRIER_INFINITE_RENORMALIZED_SUMS_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": source["classical_commit"],
        "scope": {
            "background": "S2(1) x S2(2)",
            "signature": "Euclidean",
            "boundary": "closed compact product without boundary",
            "operators": "F=-Box I+Ric and A=F-2 Ric on one-forms",
        },
        "one_form_hodge_decomposition": {
            "first_factor": "for ell>0: dY_ell and star_2 dY_ell, tensored with Y_m",
            "second_factor": "for m>0: Y_ell tensored with dY_m and star_2 dY_m",
            "multiplicity_per_polarization": "(2ell+1)(2m+1)",
            "F_eigenvalue": "lambda=ell(ell+1)+2m(m+1)",
            "A_first_factor_eigenvalue": "lambda-2",
            "A_second_factor_eigenvalue": "lambda-4",
        },
        "priming_policy": {
            "exact_exceptional_rows": "(1,0) and (0,1) pair with the Schur poles and contribute 1/3 per scalar harmonic",
            "coexact_exceptional_rows": "the three first-factor and three second-factor Killing zeros are primed out",
            "Killing_zero_dimension": 6,
            "matched_exact_exceptional_dimension": 6,
            "forbidden_double_count": "do not square the exceptional 3^-6 factor; only the exact polarization participates in the Schur cancellation",
        },
        "regular_relative_determinant": {
            "first_factor_component": "J_1=-2/lambda on ell>0, with (1,0) removed",
            "second_factor_component": "J_2=-4/lambda on m>0, with (0,1) removed",
            "polarization_multiplicity": 2,
            "weighted_modified_formula": "2 sum_i[log det_3(I+J_i)+R_F(J_i)-(1/2)FP R_F(J_i^2)]",
            "full_regular_vector_times_schur_mode": "prod_active[(lambda-2k_i)/lambda]^2 s_lm",
        },
        "heat_carriers": {
            "H_1": "sum_ell>=0 (2ell+1) exp[-t ell(ell+1)]",
            "H_2": "sum_m>=0 (2m+1) exp[-2t m(m+1)]",
            "first_active": "[H_1(t)-1] H_2(t), then subtract the (1,0) exceptional row",
            "second_active": "H_1(t)[H_2(t)-1], then subtract the (0,1) exceptional row",
        },
        "zeta_weighted_local_defect": {
            "formula_per_polarization": "log det_zeta(F-c)-log det_zeta(F)-tr^F log(1-c F^-1)=-(c^2/4)Wres(F^-2)",
            "scalar_a0_per_polarization": _q(scalar_a0),
            "Wres_F_inverse_square": _q(wres_inverse_square),
            "first_shift_c": _q(2),
            "second_shift_c": _q(4),
            "first_defect_per_polarization": _q(defects["first_factor_one_polarization"]),
            "second_defect_per_polarization": _q(defects["second_factor_one_polarization"]),
            "two_polarization_total_defect": _q(total_defect),
            "lower_dimensional_active_projection_effect_on_four_dimensional_residue": "ZERO",
        },
        "selected_exact_modes": modes,
        "claim_flags": {
            "PRODUCT_MINIMAL_VECTOR_MODE_CARRIER_SUPPLIED": True,
            "EXACT_COEXACT_POLARIZATIONS_ENUMERATED": True,
            "KILLING_ZERO_PRIMING_COMPUTED": True,
            "MATCHED_EXACT_SCHUR_POLICY_COMPUTED": True,
            "MINIMAL_VECTOR_ZETA_WEIGHTED_LOCAL_DEFECT_COMPUTED": True,
            "MINIMAL_VECTOR_INFINITE_WEIGHTED_DETERMINANT_COMPUTED": False,
            "FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {
            "product_schur_carrier": {
                "path": str(DEPENDENCY.relative_to(ROOT)),
                "result_id": source["result_id"],
                "sha256": _sha256(DEPENDENCY),
            }
        },
        "next_gate": "EVALUATE_THE_TWO_ACTIVE_SCALAR_PRODUCT_ZETA_WEIGHTED_MODIFIED_DETERMINANTS_WITH_THE_DECLARED_EXCEPTIONAL_ROWS_REMOVED",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate supplies the complete exact/coexact minimal-vector mode carrier, distinguishes the six exact zeros paired with Schur poles from the six coexact Killing zeros that are primed out, and computes the local zeta-to-weighted determinant defect on S2(1) x S2(2). It does not evaluate the two infinite weighted modified determinants, the full coupled ghost factor, remaining BV sectors, complete Gamma1/Q1, a restored QME, or any Lorentzian causal, Hadamard, state-space, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def emit(*, check: bool) -> None:
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit(f"stale minimal-vector carrier: {OUTPUT}")
    else:
        OUTPUT.write_text(rendered)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.emit:
        emit(check=False)
    if args.check:
        emit(check=True)
    if not args.emit and not args.check:
        print(json.dumps(build(), indent=2, sort_keys=True))
    print("PRODUCT S2xS2 GHOST MINIMAL VECTOR: CARRIER PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
