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


def support_rank(active_blocks: tuple[int, ...]) -> int:
    """Rank of an exact representative on a declared coordinate-support stratum."""
    lambdas = (1, 2, 3, 4)
    representatives = (
        [1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1],
        [1, 4, 6, 4, 1],
        [1, -4, 6, -4, 1],
    )

    def multiplication(value: list[int]) -> sp.Matrix:
        matrix = sp.zeros(9, 5)
        for left_index, coefficient in enumerate(value):
            for right_index in range(5):
                matrix[left_index + right_index, right_index] = coefficient
        return matrix

    blocks = [multiplication(representatives[index]) if index in active_blocks else sp.zeros(9, 5) for index in range(4)]
    matrix = sp.Matrix.vstack(
        sp.Matrix.hstack(*blocks),
        sp.Matrix.hstack(*(lambdas[index] * blocks[index] for index in range(4))),
    )
    return matrix.rank()


def all_active_rank_table() -> dict[str, object]:
    """Audit the integer inequalities in the all-active P1 argument."""
    local_pattern_count = 0
    for m_1 in range(5):
        for m_2 in range(m_1, 5):
            for m_3 in range(m_2, 5):
                for m_4 in range(m_3, 5):
                    if m_2 == 0:
                        continue
                    delta = m_1 + m_2
                    codimension = m_1 + m_2 + m_3 + m_4 - 1
                    if codimension < delta + 1:
                        raise AssertionError("candidate-13 local torsion codimension bound failed")
                    local_pattern_count += 1

    splitting_rows = []
    for delta in range(3):
        for q in range(1, 4 - delta):
            component_degree = 3 - delta - q
            parameter_dimension = 2 * component_degree + 13
            codimension_lower_bound = 20 - parameter_dimension
            required_codimension = delta + q + 1
            if codimension_lower_bound < required_codimension:
                raise AssertionError("candidate-13 splitting-jump codimension bound failed")
            kernel_dimension = delta + q + 2
            incidence_dimension_upper_bound = 20 - codimension_lower_bound + kernel_dimension
            splitting_rows.append(
                {
                    "torsion_length_delta": delta,
                    "splitting_jump_q": q,
                    "minimal_syzygy_component_degree": component_degree,
                    "parameter_dimension_upper_bound": parameter_dimension,
                    "codimension_lower_bound": codimension_lower_bound,
                    "required_codimension": required_codimension,
                    "kernel_dimension": kernel_dimension,
                    "incidence_dimension_upper_bound": incidence_dimension_upper_bound,
                }
            )
    if max(row["incidence_dimension_upper_bound"] for row in splitting_rows) > 20:
        raise AssertionError("candidate-13 splitting incidence bound changed")
    return {
        "local_pattern_count": local_pattern_count,
        "splitting_rows": splitting_rows,
    }


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
    boundary_ranks = {str(size): support_rank(tuple(range(size))) for size in range(4)}
    if boundary_ranks != {"0": 0, "1": 5, "2": 10, "3": 15}:
        raise AssertionError("candidate-13 coordinate-support ranks changed")
    all_active = all_active_rank_table()
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
        "mixed_root_cancellation_witness": {
            "common_forms": "nonzero binary quartics F,G",
            "A": ["F", "F", "F", "0"],
            "B": ["(lambda_2-lambda_3)G", "(lambda_3-lambda_1)G", "(lambda_1-lambda_2)G", "0"],
            "verification": ["sum_i A_i*B_i=0", "sum_i lambda_i*A_i*B_i=0"],
            "nonfactorization": "the first three coefficients are nonzero because the generalized roots are distinct, so cancellation genuinely crosses three pencil eigenlines",
        },
        "coordinate_boundary_stratification": {
            "support_variable": "s=number of nonzero A_i blocks; the same result holds after interchanging A and B",
            "representative_linear_ranks": boundary_ranks,
            "support_zero_one_two": [
                {
                    "active_blocks": 0,
                    "source_dimension": 0,
                    "kernel_dimension": 20,
                    "incidence_dimension": 20,
                },
                {
                    "active_blocks": 1,
                    "source_dimension": 5,
                    "kernel_dimension": 15,
                    "incidence_dimension": 20,
                },
                {
                    "active_blocks": 2,
                    "source_dimension": 10,
                    "kernel_dimension": 10,
                    "incidence_dimension": 20,
                },
            ],
            "support_three": {
                "active_kernel_formula": "d=dim(intersection_i A_i*Sym^4)=max(9-deg(lcm(A_1,A_2,A_3)),0)",
                "total_kernel_dimension": "5+d",
                "generic_lcm_degree_at_least_9": {
                    "source_dimension_upper_bound": 15,
                    "kernel_dimension": 5,
                    "incidence_dimension_upper_bound": 20,
                },
                "special_lcm_degree_r_at_most_8": {
                    "source_dimension_upper_bound": "r+3",
                    "reason": "choose the projective degree-r lcm in dimension r and three nonzero affine scales; its degree-four divisors are a finite choice on each factorization type",
                    "kernel_dimension": "14-r",
                    "incidence_dimension_upper_bound": 17,
                },
            },
            "maximum_boundary_incidence_dimension": 20,
            "consequence": "no irreducible component of dimension at least 21 is contained in the coordinate boundary; its generic point lies in the torus where every A_i and every B_i is nonzero",
        },
        "all_active_rank_stratification": {
            "sheaf_map": "phi_A: O_P1(-4)^4 -> O_P1^2 with columns A_i*(1,lambda_i)^T",
            "kernel_and_cokernel": "0 -> K_A -> O(-4)^4 -> O^2 -> T_A -> 0",
            "torsion_length": "delta=length(T_A)",
            "local_smith_formula": "at a point with sorted valuations m_1<=m_2<=m_3<=m_4, delta_z=m_1+m_2 because every 2x2 direction minor lambda_j-lambda_i is nonzero",
            "local_torsion_codimension": "sum_i m_i-1 >= delta_z+1; over several support points this gives codim{length(T_A)>=delta}>=delta+1",
            "kernel_splitting": "K_A=O(-a) plus O(-b), a<=b, a+b=16-delta",
            "cohomology_formula": "ker(L_A)=H^0(K_A(8)); k=delta+2+q with q=h^1(K_A(8))",
            "torsion_only_rows": [
                {
                    "torsion_length_delta": delta,
                    "splitting_jump_q": 0,
                    "codimension_lower_bound": delta + 1,
                    "kernel_dimension": delta + 2,
                    "incidence_dimension_upper_bound": 21,
                }
                for delta in range(1, 9)
            ],
            "splitting_jump_argument": "If q>0 then b=9+q, a=7-delta-q and a nonzero minimal syzygy has component degree d=a-4=3-delta-q. Writing X_i=A_i B_i in the fixed two-dimensional pencil kernel gives X_i=alpha_i H+beta_i J with H,J in Sym^(d+4). Projectivizing (H,J), choosing the four affine A_i scales and using the finite divisor choices gives dimension at most 2d+13. If one X_i vanishes identically, the smaller bound d+12 applies; two cannot vanish because the four pencil directions are distinct.",
            "splitting_jump_rows": all_active["splitting_rows"],
            "machine_audit": {
                "sorted_local_valuation_patterns_checked": all_active["local_pattern_count"],
                "valuation_range": "0<=m_i<=4",
                "all_local_torsion_bounds_pass": True,
                "all_possible_positive_q_rows_pass": True,
            },
            "rank_drop_bound": "dim{A:kernel_dimension>=k}+k<=21 for every k>=3; q=0 torsion strata are at most 21 and q>0 strata are at most 20",
        },
        "prime_zero_variety_theorem": {
            "ambient_dimension_over_C": 40,
            "equation_count": 18,
            "maximum_component_dimension_over_C": 22,
            "rank_drop_incidence_dimension_upper_bound": 21,
            "coordinate_boundary_incidence_dimension_upper_bound": 20,
            "complete_intersection": "the 18 generators have height 18 in the polynomial ring, hence form a complete intersection and the ideal is unmixed",
            "unique_component": "the nonempty rank-18 source open set is a rank-two vector bundle over an irreducible open subset of A^20; every complementary stratum has dimension at most 21, so unmixedness leaves its closure as the unique component",
            "generic_reducedness": "the rank-18 derivative with respect to B gives Jacobian rank 18 on the generic fixture",
            "primality": "an unmixed one-minimal-prime complete intersection that is reduced at its generic point is radical; therefore the candidate-13 ideal is prime",
            "zero_variety": "one irreducible complex dimension-22 affine cone in ambient dimension 40",
        },
        "next_gate": "join the certified cross-fibre prime incidence cone to the same-fibre quadratic sources and five Taub moment maps before deciding bounded or smooth-secular extension",
        "classification": {
            "candidate_13_exact_pencil_reduction_certified": True,
            "four_distinct_real_generalized_roots_certified": True,
            "generic_rank_18_open_component_certified": True,
            "generic_component_dimension_22_certified": True,
            "three_root_cancellation_witness_certified": True,
            "coordinate_boundary_dimension_20_certified": True,
            "all_active_torsion_strata_certified": True,
            "all_active_splitting_jump_strata_certified": True,
            "complete_rank_stratification_certified": True,
            "full_candidate_13_zero_variety_classified": True,
            "candidate_13_ideal_prime": True,
            "same_fibre_quadratic_sources_classified": False,
            "taub_common_zero_intersection_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {"parent": str(PARENT.relative_to(ROOT)), "parent_sha256": sha(PARENT)},
        "claim_boundary": "This certificate classifies the complete candidate-13 cross-fibre all-m L4 resonance ideal as one prime complex dimension-22 cone. It does not join same-fibre quadratic sources, Taub maps or any correction class, and makes no residual, causal, observational or quantum claim.",
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
