"""Reduce candidate 13 to a universal two-row binary-quartic incidence problem."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    certified_nonzero_interval,
    fraction_string,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def interval(value: sp.Expr) -> dict[str, object]:
    witness = certified_nonzero_interval(value)
    if witness is None:
        raise AssertionError("candidate-13 pencil invariant vanished")
    bounds, digits = witness
    return {
        "lower": fraction_string(bounds[0]),
        "upper": fraction_string(bounds[1]),
        "decimal_digits": digits,
        "excludes_zero": bounds[0] > 0 or bounds[1] < 0,
        "sign": "positive" if bounds[0] > 0 else "negative",
    }


def det2(matrix: sp.Matrix) -> sp.Expr:
    return matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0]


def adj2(matrix: sp.Matrix) -> sp.Matrix:
    return sp.Matrix([[matrix[1, 1], -matrix[0, 1]], [-matrix[1, 0], matrix[0, 0]]])


def matrices(fibre: dict[str, object]) -> dict[str, sp.Matrix]:
    conversion = parse(fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"])
    result = {}
    for target in fibre["target_equations"]:
        for term in target["terms"]:
            key = term["first_parity"][0] + term["second_parity"][0]
            components = term["coefficient_matrices"]
            if len(components) != 1:
                raise AssertionError("candidate-13 target ceased to be scalar")
            matrix = sp.Matrix(
                [[parse(value) * conversion for value in row] for row in components[0]]
            )
            if matrix.shape != (2, 2):
                raise AssertionError("candidate-13 source ceased to be doublet by doublet")
            result[key] = matrix
    if set(result) != {"aa", "ap", "pa", "pp"}:
        raise AssertionError("candidate-13 parity census changed")
    if any(value.has(sp.pi) for matrix in result.values() for value in matrix):
        raise AssertionError("candidate-13 common conversion failed to cancel pi")
    return result


def generic_rank_minor() -> sp.Expr:
    lambdas = sp.symbols("lambda_1:5")
    quartics = []
    for basis_index in (0, 0, 4, 4):
        value = [0] * 5
        value[basis_index] = 1
        quartics.append(value)

    def multiplication(value: list[int]) -> sp.Matrix:
        matrix = sp.zeros(9, 5)
        for left_index, coefficient in enumerate(value):
            for right_index in range(5):
                matrix[left_index + right_index, right_index] = coefficient
        return matrix

    first = sp.Matrix.hstack(*(multiplication(value) for value in quartics))
    second = sp.Matrix.hstack(
        *(lambdas[index] * multiplication(value) for index, value in enumerate(quartics))
    )
    sylvester = sp.Matrix.vstack(first, second)
    retained = [index for index in range(20) if index not in (4, 9)]
    determinant = sp.factor(sylvester[:, retained].det(method="domain-ge"))
    expected = -(lambdas[0] - lambdas[1]) ** 4 * (lambdas[2] - lambdas[3]) ** 5
    if determinant != expected:
        raise AssertionError("candidate-13 generic rank witness changed")
    return determinant


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    fibre = next(item for item in parent["physical_fibres"] if item["candidate_index"] == 13)
    if (
        fibre["output_ell"] != 4
        or fibre["first_branch_multiplicity_per_parity"] != 2
        or fibre["second_branch_multiplicity_per_parity"] != 2
        or fibre["target_cokernel_dimension_per_parity"] != 1
        or fibre["complex_amplitude_variables"] != 40
        or fibre["scalar_magnetic_equations"] != 18
    ):
        raise AssertionError("candidate-13 incidence scope changed")
    current = matrices(fibre)
    determinants = {key: det2(value) for key, value in current.items()}
    denominator = determinants["pp"] * determinants["aa"]
    product = adj2(current["pp"]) * current["pa"] * adj2(current["aa"]) * current["ap"]
    trace = (product[0, 0] + product[1, 1]) / denominator
    determinant = determinants["pa"] * determinants["ap"] / denominator
    discriminant = trace**2 - 4 * determinant
    invariants = {
        **{f"det_{key}": value for key, value in determinants.items()},
        "trace_square_pencil": trace,
        "determinant_square_pencil": determinant,
        "discriminant_square_pencil": discriminant,
    }
    witnesses = {key: interval(value) for key, value in invariants.items()}
    if any(witnesses[key]["sign"] != "positive" for key in (
        "trace_square_pencil", "determinant_square_pencil", "discriminant_square_pencil"
    )):
        raise AssertionError("candidate-13 real simple pencil criterion failed")
    rank_minor = generic_rank_minor()
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-candidate13-L4-incidence-reduction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_L4_INCIDENCE_REDUCTION",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "candidate-13 tuned compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "complete all-m L4 cross-|n| resonance block with two multiplicity-two p_extra source branches and scalar q_plus targets",
            "degree": 2,
            "parity": "both axial and polar amplitudes",
            "ell": "2 times 2 -> L=4",
            "m": "all magnetic components through binary-quartic multiplication",
            "k": "signed |n|=1 and |n|=2 momenta (1,-2)",
            "omega": "positive-frequency SUM channel",
        },
        "candidate_index": 13,
        "fibre_id": fibre["fibre_id"],
        "rho": fibre["rho"],
        "internal_matrices": {
            key: [[sp.sstr(value) for value in row] for row in matrix.tolist()]
            for key, matrix in current.items()
        },
        "exact_interval_witnesses": witnesses,
        "pencil_reduction": {
            "same_form": "K_0=diag(C_aa,C_pp)",
            "cross_form": "K_1=[[0,C_ap],[C_pa,0]]",
            "squared_operator": "T=C_pp^{-1} C_pa C_aa^{-1} C_ap",
            "root_structure": "four distinct nonzero real generalized roots lambda_i",
            "normal_form_equations": [
                "sum_i A_i*B_i=0 in Sym^8(C^2)",
                "sum_i lambda_i*A_i*B_i=0 in Sym^8(C^2)"
            ],
            "ambient_dimension_over_C": 40,
            "scalar_equations": 18,
        },
        "generic_open_stratum": {
            "source_choice": ["A_1=A_2=x^4", "A_3=A_4=y^4"],
            "retained_columns": [index for index in range(20) if index not in (4, 9)],
            "rank_18_minor": sp.sstr(rank_minor),
            "linear_rank": 18,
            "kernel_dimension": 2,
            "incidence_dimension_over_C": 22,
            "interpretation": "over the rank-18 source open set the solution is a rank-two vector bundle, hence irreducible there",
        },
        "remaining_rank_stratification_gate": {
            "statement": "prove that every source rank-drop stratum has total incidence dimension at most 21, then use complete-intersection unmixedness and the rank-18 Jacobian witness to prove the full ideal prime",
            "required_bound": "dim{A: kernel_dimension>=k}+k <= 21 for every k>=3",
            "full_zero_variety_classified": False,
        },
        "classification": {
            "candidate_13_exact_pencil_reduction_certified": True,
            "four_distinct_real_generalized_roots_certified": True,
            "generic_rank_18_open_component_certified": True,
            "generic_component_dimension_22_certified": True,
            "complete_rank_stratification_certified": False,
            "full_candidate_13_zero_variety_classified": False,
            "same_fibre_quadratic_sources_classified": False,
            "taub_common_zero_intersection_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {"parent": str(PARENT.relative_to(ROOT)), "parent_sha256": sha(PARENT)},
        "claim_boundary": "This certificate reduces candidate 13 exactly and certifies its generic dimension-22 incidence component. It does not classify the degenerate rank strata or the full zero variety. Same-fibre, Taub and correction-class joins remain fail-closed.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("candidate-13 incidence reduction certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_L4_INCIDENCE_REDUCTION: PASS")


if __name__ == "__main__":
    main()
