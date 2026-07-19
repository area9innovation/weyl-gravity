"""Classify the scalar-internal candidate-2 L=3 amplitude zero variety."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import certified_nonzero_interval, fraction_string


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L3_zero_variety.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L3_zero_variety.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def interval(value: sp.Expr) -> dict[str, object]:
    witness = certified_nonzero_interval(value)
    if witness is None:
        raise AssertionError("zero entered a nonzero interval")
    bounds, digits = witness
    return {
        "lower": fraction_string(bounds[0]),
        "upper": fraction_string(bounds[1]),
        "decimal_digits": digits,
        "positive": bounds[0] > 0,
        "excludes_zero": bounds[0] > 0 or bounds[1] < 0,
    }


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    fibre = next(item for item in parent["physical_fibres"] if item["candidate_index"] == 2)
    if not (
        fibre["output_ell"] == 3
        and fibre["first_branch_multiplicity_per_parity"] == 1
        and fibre["second_branch_multiplicity_per_parity"] == 1
        and fibre["target_cokernel_dimension_per_parity"] == 1
    ):
        raise AssertionError("candidate-2 scalar L3 scope changed")
    coefficients = {
        term["first_parity"][0] + term["second_parity"][0]:
        parse(term["coefficient_matrices"][0][0][0])
        for target in fibre["target_equations"]
        for term in target["terms"]
    }
    if set(coefficients) != {"aa", "pp", "ap", "pa"}:
        raise AssertionError("candidate-2 parity pencil changed")
    coefficient_intervals = {key: interval(value) for key, value in coefficients.items()}
    if not all(item["excludes_zero"] for item in coefficient_intervals.values()):
        raise AssertionError("candidate-2 parity pencil became singular")
    lambda_squared = canonical(
        coefficients["ap"] * coefficients["pa"]
        / (coefficients["aa"] * coefficients["pp"])
    )
    lambda_interval = interval(lambda_squared)
    if not lambda_interval["positive"]:
        raise AssertionError("real parity eigenvalues disappeared")
    lambda_value = f"sqrt({sp.sstr(lambda_squared)})"
    a, b = coefficients["aa"], coefficients["pp"]
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-scalar-L3-zero-variety-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_SCALAR_L3_ZERO_VARIETY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "candidate-2 compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "scalar-internal all-m L3 cross-|n| resonance block",
            "degree": 2,
            "parity": "both axial and polar amplitudes on both momentum fibres",
            "ell": "2 times 2 -> L=3",
            "m": "all magnetic components",
            "k": "signed momenta (1,-2)",
            "omega": "positive-frequency SUM channel",
        },
        "candidate_index": 2,
        "fibre_id": fibre["fibre_id"],
        "rho": fibre["rho"],
        "coefficients": {key: sp.sstr(value) for key, value in coefficients.items()},
        "coefficient_nonzero_intervals": coefficient_intervals,
        "parity_pencil": {
            "C0": [[sp.sstr(a), "0"], ["0", sp.sstr(b)]],
            "C1": [["0", sp.sstr(coefficients["ap"])], [sp.sstr(coefficients["pa"]), "0"]],
            "lambda_squared": sp.sstr(lambda_squared),
            "lambda_squared_interval": lambda_interval,
            "lambda": lambda_value,
            "Q": [["c_ap/(c_aa*lambda)", "-c_ap/(c_aa*lambda)"], ["1", "1"]],
            "P_transpose": "inverse(C0*Q)",
            "transformed_coordinates": {
                "A_plus": "(c_ap/lambda)*A_axial+c_pp*A_polar",
                "A_minus": "-(c_ap/lambda)*A_axial+c_pp*A_polar",
                "B_plus": "(c_aa*lambda/(2*c_ap))*B_axial+(1/2)*B_polar",
                "B_minus": "-(c_aa*lambda/(2*c_ap))*B_axial+(1/2)*B_polar"
            },
            "normal_form": [
                "T1(A_plus,B_plus)+T1(A_minus,B_minus)=0",
                "lambda*(T1(A_plus,B_plus)-T1(A_minus,B_minus))=0"
            ]
        },
        "representation_theorem": {
            "model": "V_2=Sym^4(C^2), and the V_3 Clebsch-Gordan projection is the unique first transvectant, proportional to the binary-quartic Jacobian",
            "jacobian_kernel": "in characteristic zero J(f,g)=0 implies d(f/g)=0 on g!=0, hence f/g is constant and the equal-degree binary quartics are proportional",
            "normal_form_consequence": "lambda is nonzero, so the two original resonance equations are equivalent to T1(A_plus,B_plus)=T1(A_minus,B_minus)=0",
        },
        "zero_variety": {
            "ambient_dimension_over_C": 20,
            "dimension_over_C": 12,
            "irreducible_components_over_C": 1,
            "description": "after the displayed invertible parity transformations, each 5-by-2 matrix [A_plus B_plus] and [A_minus B_minus] has rank at most one",
            "defining_minors": "all twenty 2-by-2 minors, ten for each transformed parity eigenchannel",
            "factorization": "the Cartesian product DetRank1(5x2)_plus x DetRank1(5x2)_minus",
        },
        "classification": {
            "candidate_2_scalar_L3_zero_variety_classified": True,
            "all_m_irreducible_decomposition_classified": True,
            "parity_pencil_diagonalized_exactly": True,
            "lambda_squared_positive_exactly": True,
            "remaining_fifteen_cross_fibre_zero_varieties_classified": False,
            "same_fibre_quadratic_sources_classified": False,
            "taub_common_zero_intersection_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {"parent": str(PARENT.relative_to(ROOT)), "parent_sha256": sha(PARENT)},
        "claim_boundary": "This classifies the candidate-2 scalar-internal L3 cross-fibre resonance variety. Fifteen other cross-fibre varieties, same-fibre sources, Taub intersections and higher correction classes remain fail-closed.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("scalar L3 zero-variety certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_SCALAR_L3_ZERO_VARIETY: PASS")


if __name__ == "__main__":
    main()
