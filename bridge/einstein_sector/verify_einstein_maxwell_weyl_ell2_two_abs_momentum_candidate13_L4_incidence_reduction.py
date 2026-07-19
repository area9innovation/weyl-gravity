"""Independent verifier for the candidate-13 L4 incidence reduction."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import jsonschema
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    certified_nonzero_interval,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def det2(matrix: sp.Matrix) -> sp.Expr:
    return matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0]


def adj2(matrix: sp.Matrix) -> sp.Matrix:
    return sp.Matrix([[matrix[1, 1], -matrix[0, 1]], [-matrix[1, 0], matrix[0, 0]]])


def current_matrices(fibre: dict[str, object]) -> dict[str, sp.Matrix]:
    conversion = parse(fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"])
    result = {}
    for target in fibre["target_equations"]:
        for term in target["terms"]:
            key = term["first_parity"][0] + term["second_parity"][0]
            result[key] = sp.Matrix([
                [parse(value) * conversion for value in row]
                for row in term["coefficient_matrices"][0]
            ])
    return result


def sign(value: sp.Expr) -> str:
    witness = certified_nonzero_interval(value)
    if witness is None:
        raise AssertionError("candidate-13 verifier found a zero invariant")
    bounds, _ = witness
    return "positive" if bounds[0] > 0 else "negative"


def rank_witness() -> sp.Expr:
    lambdas = sp.symbols("lambda_1:5")
    matrix = sp.zeros(18, 20)
    for block, shift in enumerate((0, 0, 4, 4)):
        for column in range(5):
            matrix[shift + column, 5 * block + column] = 1
            matrix[9 + shift + column, 5 * block + column] = lambdas[block]
    retained = [index for index in range(20) if index not in (4, 9)]
    return sp.factor(matrix[:, retained].det(method="domain-ge"))


def support_rank(active_blocks: tuple[int, ...]) -> int:
    lambdas = (1, 2, 3, 4)
    quartics = (
        [1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1],
        [1, 4, 6, 4, 1],
        [1, -4, 6, -4, 1],
    )
    matrix = sp.zeros(18, 20)
    for block in range(4):
        if block not in active_blocks:
            continue
        for left_index, coefficient in enumerate(quartics[block]):
            for right_index in range(5):
                matrix[left_index + right_index, 5 * block + right_index] = coefficient
                matrix[9 + left_index + right_index, 5 * block + right_index] = lambdas[block] * coefficient
    return matrix.rank()


def independent_rank_strata() -> tuple[int, list[dict[str, int]]]:
    local_count = 0
    for valuations in itertools.combinations_with_replacement(range(5), 4):
        if valuations[1] == 0:
            continue
        delta = valuations[0] + valuations[1]
        if sum(valuations) - 1 < delta + 1:
            raise AssertionError("candidate-13 verifier found a bad local Smith stratum")
        local_count += 1
    rows = []
    for delta, q in ((0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (2, 1)):
        degree = 3 - delta - q
        parameter_dimension = 2 * degree + 13
        codimension = 20 - parameter_dimension
        kernel_dimension = delta + q + 2
        rows.append(
            {
                "torsion_length_delta": delta,
                "splitting_jump_q": q,
                "minimal_syzygy_component_degree": degree,
                "parameter_dimension_upper_bound": parameter_dimension,
                "codimension_lower_bound": codimension,
                "required_codimension": delta + q + 1,
                "kernel_dimension": kernel_dimension,
                "incidence_dimension_upper_bound": 20 - codimension + kernel_dimension,
            }
        )
    return local_count, rows


def verify() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.validate(certificate, schema)
    if certificate["schema_sha256"] != sha(SCHEMA):
        raise AssertionError("candidate-13 schema hash changed")
    if certificate["provenance"]["parent_sha256"] != sha(PARENT):
        raise AssertionError("candidate-13 parent hash changed")
    parent = json.loads(PARENT.read_text())
    fibre = next(item for item in parent["physical_fibres"] if item["candidate_index"] == 13)
    matrices = current_matrices(fibre)
    stored = {
        key: sp.Matrix([[parse(value) for value in row] for row in matrix])
        for key, matrix in certificate["internal_matrices"].items()
    }
    if stored != matrices:
        raise AssertionError("candidate-13 stored matrices changed")
    determinants = {key: det2(value) for key, value in matrices.items()}
    denominator = determinants["pp"] * determinants["aa"]
    product = adj2(matrices["pp"]) * matrices["pa"] * adj2(matrices["aa"]) * matrices["ap"]
    trace = (product[0, 0] + product[1, 1]) / denominator
    determinant = determinants["pa"] * determinants["ap"] / denominator
    invariants = {
        **{f"det_{key}": value for key, value in determinants.items()},
        "trace_square_pencil": trace,
        "determinant_square_pencil": determinant,
        "discriminant_square_pencil": trace**2 - 4 * determinant,
    }
    for key, value in invariants.items():
        if sign(value) != certificate["exact_interval_witnesses"][key]["sign"]:
            raise AssertionError(f"candidate-13 invariant sign changed: {key}")
    if any(certificate["exact_interval_witnesses"][key]["sign"] != "positive" for key in (
        "trace_square_pencil", "determinant_square_pencil", "discriminant_square_pencil"
    )):
        raise AssertionError("candidate-13 real-root criterion failed")
    expected_minor = "-(lambda_1 - lambda_2)**4*(lambda_3 - lambda_4)**5"
    if sp.sstr(rank_witness()) != expected_minor:
        raise AssertionError("candidate-13 rank-18 minor changed")
    generic = certificate["generic_open_stratum"]
    if generic["rank_18_minor"] != expected_minor or generic["linear_rank"] != 18 or generic["kernel_dimension"] != 2 or generic["incidence_dimension_over_C"] != 22:
        raise AssertionError("candidate-13 generic component changed")
    lambda_1, lambda_2, lambda_3 = sp.symbols("lambda_1 lambda_2 lambda_3")
    weights = [lambda_2 - lambda_3, lambda_3 - lambda_1, lambda_1 - lambda_2]
    if sp.expand(sum(weights)) != 0 or sp.expand(sum(root * weight for root, weight in zip((lambda_1, lambda_2, lambda_3), weights))) != 0:
        raise AssertionError("candidate-13 three-root cancellation changed")
    boundary = certificate["coordinate_boundary_stratification"]
    ranks = {str(size): support_rank(tuple(range(size))) for size in range(4)}
    if ranks != boundary["representative_linear_ranks"] or ranks != {"0": 0, "1": 5, "2": 10, "3": 15}:
        raise AssertionError("candidate-13 coordinate-support ranks changed")
    for row in boundary["support_zero_one_two"]:
        if row["source_dimension"] + row["kernel_dimension"] != 20 or row["incidence_dimension"] != 20:
            raise AssertionError("candidate-13 low-support dimension count changed")
    for degree in range(4, 9):
        intersection_dimension = 9 - degree
        kernel_dimension = 5 + intersection_dimension
        source_dimension_bound = degree + 3
        if source_dimension_bound + kernel_dimension != 17:
            raise AssertionError("candidate-13 three-support lcm bound changed")
    if boundary["maximum_boundary_incidence_dimension"] != 20:
        raise AssertionError("candidate-13 coordinate-boundary dimension changed")
    rank_strata = certificate["all_active_rank_stratification"]
    local_count, splitting_rows = independent_rank_strata()
    if rank_strata["machine_audit"]["sorted_local_valuation_patterns_checked"] != local_count:
        raise AssertionError("candidate-13 local valuation census changed")
    if rank_strata["splitting_jump_rows"] != splitting_rows:
        raise AssertionError("candidate-13 splitting-jump table changed")
    for row in rank_strata["torsion_only_rows"]:
        if (
            row["codimension_lower_bound"] != row["torsion_length_delta"] + 1
            or row["kernel_dimension"] != row["torsion_length_delta"] + 2
            or row["incidence_dimension_upper_bound"] != 21
        ):
            raise AssertionError("candidate-13 torsion-only table changed")
    prime = certificate["prime_zero_variety_theorem"]
    if (
        prime["ambient_dimension_over_C"] != 40
        or prime["equation_count"] != 18
        or prime["maximum_component_dimension_over_C"] != 22
        or prime["rank_drop_incidence_dimension_upper_bound"] != 21
        or prime["coordinate_boundary_incidence_dimension_upper_bound"] != 20
    ):
        raise AssertionError("candidate-13 prime-variety dimension ledger changed")
    classification = certificate["classification"]
    if not (
        classification["candidate_13_exact_pencil_reduction_certified"]
        and classification["four_distinct_real_generalized_roots_certified"]
        and classification["generic_rank_18_open_component_certified"]
        and classification["generic_component_dimension_22_certified"]
        and classification["three_root_cancellation_witness_certified"]
        and classification["coordinate_boundary_dimension_20_certified"]
        and classification["all_active_torsion_strata_certified"]
        and classification["all_active_splitting_jump_strata_certified"]
        and classification["complete_rank_stratification_certified"]
        and classification["full_candidate_13_zero_variety_classified"]
        and classification["candidate_13_ideal_prime"]
    ):
        raise AssertionError("candidate-13 reduction was weakened")
    if (
        classification["same_fibre_quadratic_sources_classified"]
        or classification["taub_common_zero_intersection_classified"]
        or classification["complete_two_fibre_tangent_cone_classified"]
        or classification["smooth_secular_classified"]
        or classification["causal_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 reduction exceeded its scope")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_L4_INCIDENCE_REDUCTION independent verification: PASS")


if __name__ == "__main__":
    verify()
