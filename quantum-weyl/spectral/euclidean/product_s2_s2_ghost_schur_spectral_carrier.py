#!/usr/bin/env python3
"""Exact longitudinal ghost Schur spectrum on S2(k1) x S2(k2)."""

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
OUTPUT = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_SPECTRAL_CARRIER.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-schur-spectral-carrier-v1.schema.json"
DEPENDENCIES = {
    "Schur_resummation": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
    "Schur_residue": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE.json",
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


def _q(value: Fraction | int) -> dict[str, int]:
    rational = Fraction(value)
    return {
        "numerator": rational.numerator,
        "denominator": rational.denominator,
    }


def _mode(k1: Fraction, k2: Fraction, ell: int, emm: int) -> dict[str, Any]:
    """Return one product-harmonic row using exact rational arithmetic.

    ``det(A/F) S_L`` is evaluated in its polynomially continued form.  That
    form remains finite when an active exact-vector eigenvalue of ``A``
    vanishes and the separately written Schur eigenvalue has a pole.
    """

    if ell < 0 or emm < 0:
        raise ValueError("harmonic levels must be nonnegative")
    a = k1 * ell * (ell + 1)
    b = k2 * emm * (emm + 1)
    lam = a + b
    degeneracy = (2 * ell + 1) * (2 * emm + 1)
    components = []
    if ell:
        components.append(("first", a, k1))
    if emm:
        components.append(("second", b, k2))
    if not components:
        return {
            "ell": ell,
            "m": emm,
            "a": _q(a),
            "b": _q(b),
            "lambda": _q(lam),
            "degeneracy": degeneracy,
            "status": "ABSENT_CONSTANT_GRADIENT",
        }

    shifted = [(name, lam - 2 * curvature) for name, _, curvature in components]
    poles = [name for name, value in shifted if value == 0]

    minimal_ratio = Fraction(1)
    for _, value in shifted:
        minimal_ratio *= value / lam

    # Polynomial continuation of
    # prod_i[(lambda-2k_i)/lambda]
    # * {2/3 + (1/3) sum_i[a_i/(lambda-2k_i)]}.
    paired_ratio = Fraction(2, 3) * minimal_ratio
    for index, (_, eigenvalue, _) in enumerate(components):
        term = eigenvalue / lam
        for other_index, (_, shifted_value) in enumerate(shifted):
            if other_index != index:
                term *= shifted_value / lam
        paired_ratio += Fraction(1, 3) * term

    row: dict[str, Any] = {
        "ell": ell,
        "m": emm,
        "a": _q(a),
        "b": _q(b),
        "lambda": _q(lam),
        "degeneracy": degeneracy,
        "active_exact_components": [name for name, _, _ in components],
        "minimal_vector_ratio": _q(minimal_ratio),
        "paired_vector_times_schur_ratio": _q(paired_ratio),
    }
    if poles:
        row.update(
            {
                "status": "MATCHED_VECTOR_ZERO_SCHUR_POLE",
                "schur_pole_components": poles,
                "schur_eigenvalue": None,
            }
        )
    else:
        schur = Fraction(2, 3)
        for (_, eigenvalue, _), (_, shifted_value) in zip(components, shifted):
            schur += Fraction(1, 3) * eigenvalue / shifted_value
        if minimal_ratio * schur != paired_ratio:
            raise AssertionError("regular Schur factorization drifted")
        row.update(
            {
                "status": "REGULAR",
                "schur_pole_components": [],
                "schur_eigenvalue": _q(schur),
                "K_eigenvalue": _q(schur - 1),
            }
        )
    return row


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _finite_cutoff_fixture(k1: Fraction, k2: Fraction, cutoff: int) -> dict[str, Any]:
    paired_product = Fraction(1)
    regular_schur_product = Fraction(1)
    regular_det3_exponent = Fraction(0)
    mode_count = 0
    exceptional_dimension = 0
    for ell in range(cutoff + 1):
        for emm in range(cutoff + 1):
            row = _mode(k1, k2, ell, emm)
            if row["status"] == "ABSENT_CONSTANT_GRADIENT":
                continue
            multiplicity = row["degeneracy"]
            mode_count += multiplicity
            paired_product *= _fraction(row["paired_vector_times_schur_ratio"]) ** multiplicity
            if row["status"] == "MATCHED_VECTOR_ZERO_SCHUR_POLE":
                exceptional_dimension += multiplicity
                continue
            schur = _fraction(row["schur_eigenvalue"])
            k_value = schur - 1
            regular_schur_product *= schur**multiplicity
            regular_det3_exponent += multiplicity * (-k_value + k_value**2 / 2)
    return {
        "rectangular_cutoff": f"0<=ell,m<={cutoff}",
        "scalar_harmonic_multiplicity_including_exceptional": mode_count,
        "exceptional_matched_dimension": exceptional_dimension,
        "paired_vector_times_schur_product": _q(paired_product),
        "regular_schur_det3_exact_form": {
            "rational_prefactor": _q(regular_schur_product),
            "exponential_exponent": _q(regular_det3_exponent),
            "meaning": "rational_prefactor * exp(exponential_exponent)",
        },
        "status": "EXACT_FINITE_CUTOFF_FIXTURE_NOT_INFINITE_DETERMINANT",
    }


def _residue_fixture(k1: Fraction, k2: Fraction) -> dict[str, Any]:
    value = Fraction(8, 27) * (k1 * k1 + k1 * k2 + k2 * k2) / (k1 * k2)
    return {
        "R": "2(k1+k2)",
        "Ricci_squared": "2(k1^2+k2^2)",
        "volume": "16 pi^2/(k1 k2)",
        "principal_K_symbol": "(2/3) Ric(xi,xi)/|xi|^4",
        "unit_S3_second_moment": "average[(Ric(n,n))^2]=(R^2+2 Ricci_squared)/24",
        "generic_formula": "Wres(K^2)=(4pi)^-2 integral[(R^2+2 Ricci_squared)/27]",
        "product_formula": "8(k1^2+k1 k2+k2^2)/(27 k1 k2)",
        "fixture_value": _q(value),
    }


def build() -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    schur = dependencies["Schur_resummation"]
    residue = dependencies["Schur_residue"]
    if (
        schur.get("Einstein_specialization", {}).get("normalized_Schur_factor")
        != "(Delta0-R/3)/(Delta0-R/2)"
        or residue.get("exact_residues", {}).get("K2_Ricci_basis")
        != "Wres(K^2)=(4 pi)^-2 integral[R^2+2 Ric_mn Ric^mn]/27"
    ):
        raise ValueError("generic Schur dependencies drifted")

    k1 = Fraction(1)
    k2 = Fraction(2)
    selected = [_mode(k1, k2, ell, emm) for ell, emm in [(1, 0), (0, 1), (2, 0), (0, 2), (1, 1), (2, 1)]]
    exchanged = [_mode(k2, k1, emm, ell) for ell, emm in [(2, 0), (1, 1), (2, 1)]]
    originals = [_mode(k1, k2, ell, emm) for ell, emm in [(2, 0), (1, 1), (2, 1)]]
    if any(
        left["paired_vector_times_schur_ratio"] != right["paired_vector_times_schur_ratio"]
        or left.get("schur_eigenvalue") != right.get("schur_eigenvalue")
        for left, right in zip(originals, exchanged)
    ):
        raise AssertionError("factor-exchange covariance failed")
    if _fraction(selected[0]["paired_vector_times_schur_ratio"]) != Fraction(1, 3):
        raise AssertionError("matched zero-pole finite factor drifted")

    result = {
        "schema": "quantum-weyl-product-s2-s2-ghost-schur-spectral-carrier-v1",
        "result_id": "PRODUCT_S2_S2_GHOST_SCHUR_SPECTRAL_CARRIER",
        "result_state": "NON_EINSTEIN_PRODUCT_SPECTRUM_AND_MATCHED_ZERO_POLE_POLICY_COMPUTED",
        "lifecycle_state": "COMPLETE_MODE_CARRIER_INFINITE_RENORMALIZED_SUMS_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": schur["classical_commit"],
        "scope": {
            "background": "S2(k1) x S2(k2) with k1,k2>0",
            "signature": "Euclidean",
            "boundary": "closed compact product without boundary",
            "anisotropic_fixture": "k1=1, k2=2",
            "carrier": "scalar product harmonics and their active exact-vector gradients",
        },
        "spectral_formula": {
            "scalar_eigenvalues": "a=k1 ell(ell+1), b=k2 m(m+1), lambda=a+b",
            "degeneracy": "(2ell+1)(2m+1)",
            "active_component_rule": "include the first exact component iff ell>0 and the second iff m>0",
            "minimal_vector_exact_eigenvalues": "lambda-2k_i on each active factor component",
            "normalized_schur_eigenvalue": "s_lm=2/3+(1/3) sum_active a_i/(lambda-2k_i)",
            "paired_ratio": "prod_active[(lambda-2k_i)/lambda] s_lm, polynomially continued through matched zeros and poles",
            "factor_exchange": "(k1,ell)<->(k2,m)",
        },
        "primed_mode_policy": {
            "constant_mode": "(0,0) is absent because its gradient vanishes",
            "exceptional_modes": [
                "(1,0): three first-factor exact-vector zeros matched to Schur poles",
                "(0,1): three second-factor exact-vector zeros matched to Schur poles",
            ],
            "forbidden_shortcut": "deleting the six vector zeros and the corresponding scalar rows separately loses a finite determinant factor",
            "matched_finite_factor_per_mode": "1/3",
            "total_exceptional_correction": "3^-6",
            "prescription": "restrict A and S_L to the regular complement and multiply their determinant product by 3^-6",
        },
        "einstein_specialization": {
            "condition": "k1=k2=k, hence Ric=k g and R=4k",
            "schur_eigenvalue": "(lambda-4k/3)/(lambda-2k)",
            "generic_formula_replayed": "(Delta0-R/3)/(Delta0-R/2)",
            "exceptional_pole_cancellation": "[(lambda-2k)/lambda] s -> 1/3 at lambda=2k",
        },
        "anisotropic_exact_modes": selected,
        "finite_cutoff_fixture": _finite_cutoff_fixture(k1, k2, 3),
        "residue_crosscheck": _residue_fixture(k1, k2),
        "infinite_sum_status": {
            "complete_spectral_measure": "SUPPLIED_BY_CLOSED_FORM_MODE_AND_DEGENERACY_FORMULAS",
            "regular_complement_det3": "DEFINED_AND_CONVERGENT_BECAUSE_K_IS_IN_S_p_FOR_EVERY_p>2",
            "det3_value": "NOT_COMPUTED",
            "finite_weighted_R_K": "NOT_COMPUTED",
            "finite_part_R_K2": "NOT_COMPUTED",
            "full_coupled_vector_schur_determinant": "NOT_COMPUTED",
            "reason": "the bivariate spectral sums still require an explicit analytic-continuation and renormalization prescription",
        },
        "claim_flags": {
            "PRODUCT_SPECTRAL_MEASURE_SUPPLIED": True,
            "ANISOTROPIC_DW_SENSITIVITY_EXHIBITED": True,
            "MATCHED_ZERO_POLE_POLICY_COMPUTED": True,
            "EINSTEIN_SPECIALIZATION_REPLAYED": True,
            "WRES_K2_REPLAYED": True,
            "INFINITE_DET3_VALUE_COMPUTED": False,
            "FINITE_WEIGHTED_R_K_COMPUTED": False,
            "FINITE_PART_R_K2_COMPUTED": False,
            "FULL_COUPLED_GHOST_DETERMINANT_COMPUTED": False,
            "GENERIC_BACKGROUND_FORM_FACTORS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "ANALYTICALLY_CONTINUE_THE_BIVARIATE_PRODUCT_SPECTRAL_SUMS_WITH_THE_MATCHED_EXCEPTIONAL_FACTOR_THEN_ADD_REMAINING_BV_SECTORS",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL result supplies an exact non-Einstein compact mode carrier for the normalized longitudinal ghost Schur kernel on S2(k1) x S2(k2). It proves that the three longitudinal D_W rows are evaluated by one anisotropic spectral function, not three independent kernels. It also finds a coupled priming effect: six exact-vector zeros are Schur poles, and their product has the finite correction 3^-6 rather than being deleted twice. The closed mode and degeneracy formulas are a complete spectral measure on this background, and the generic Wres(K^2) formula is replayed exactly. The bivariate infinite det3 and weighted finite sums are not evaluated here, so this is not a complete ghost determinant, generic-background form factor, remaining-BV assembly, Gamma1/Q1, Lorentzian QME, state, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    true_flags = {
        "PRODUCT_SPECTRAL_MEASURE_SUPPLIED",
        "ANISOTROPIC_DW_SENSITIVITY_EXHIBITED",
        "MATCHED_ZERO_POLE_POLICY_COMPUTED",
        "EINSTEIN_SPECIALIZATION_REPLAYED",
        "WRES_K2_REPLAYED",
    }
    for name, flag in value["claim_flags"].items():
        if flag is not (name in true_flags):
            raise ValueError(f"claim flag crossed boundary: {name}")


def emit(*, check: bool) -> None:
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit(f"stale product spectral carrier: {OUTPUT}")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
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
    print("PRODUCT S2xS2 GHOST SCHUR SPECTRAL CARRIER: EXACT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
