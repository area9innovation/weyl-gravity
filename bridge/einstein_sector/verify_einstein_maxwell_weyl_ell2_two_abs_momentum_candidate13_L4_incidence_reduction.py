"""Independent verifier for the candidate-13 L4 incidence reduction."""
from __future__ import annotations

import hashlib
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
    classification = certificate["classification"]
    if not (
        classification["candidate_13_exact_pencil_reduction_certified"]
        and classification["four_distinct_real_generalized_roots_certified"]
        and classification["generic_rank_18_open_component_certified"]
        and classification["generic_component_dimension_22_certified"]
        and classification["three_root_cancellation_witness_certified"]
    ):
        raise AssertionError("candidate-13 reduction was weakened")
    if (
        classification["complete_rank_stratification_certified"]
        or classification["full_candidate_13_zero_variety_classified"]
        or classification["same_fibre_quadratic_sources_classified"]
        or classification["taub_common_zero_intersection_classified"]
        or classification["complete_two_fibre_tangent_cone_classified"]
        or classification["smooth_secular_classified"]
        or classification["causal_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 reduction exceeded its scope")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_L4_INCIDENCE_REDUCTION independent verification: PASS")


if __name__ == "__main__":
    verify()
