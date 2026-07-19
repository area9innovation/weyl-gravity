#!/usr/bin/env python3
"""Independent exact verifier for the multiplicity-two L=3 varieties."""
from __future__ import annotations

import gc
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator
from sympy.core.cache import clear_cache
from sympy.polys.numberfields import to_number_field


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def exact_square(left: sp.Expr, right: sp.Expr, factor: int) -> None:
    residual = sp.sqrtdenest(left**2 - factor * right**2)
    algebraic = to_number_field(residual)
    assert algebraic.as_expr() == 0
    del residual, algebraic
    clear_cache()
    gc.collect()


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == sha(SCHEMA)
    parent_path = ROOT / value["provenance"]["parent"]
    assert value["provenance"]["parent_sha256"] == sha(parent_path)
    parent = json.loads(parent_path.read_text())
    fibres = {
        item["candidate_index"]: item
        for item in parent["physical_fibres"]
        if item["candidate_index"] in (6, 10, 18)
    }
    assert list(fibres) == [6, 10, 18]
    assert [item["candidate_index"] for item in value["decompositions"]] == [6, 10, 18]
    for item in value["decompositions"]:
        fibre = fibres[item["candidate_index"]]
        expected = {}
        for target in fibre["target_equations"]:
            for term in target["terms"]:
                matrix = sp.Matrix([
                    [parse(entry) for entry in row]
                    for row in term["coefficient_matrices"][0]
                ])
                row = matrix if matrix.rows == 1 else matrix.T
                expected[term["first_parity"][0] + term["second_parity"][0]] = list(row)
        rows = {key: [parse(entry) for entry in row] for key, row in item["coefficient_rows"].items()}
        assert rows == expected
        if item["candidate_index"] == 6:
            relations = (
                [(rows["pa"][j], rows["aa"][j], 1152) for j in range(2)]
                + [(rows["ap"][j], rows["pp"][j], 128) for j in range(2)]
            )
        else:
            relations = (
                [(rows["ap"][j], rows["aa"][j], 1152) for j in range(2)]
                + [(rows["pa"][j], rows["pp"][j], 128) for j in range(2)]
            )
        for index, (left, right, factor) in enumerate(relations):
            exact_square(left, right, factor)
            witness = item["exact_relation_interval_witnesses"][index]
            assert witness["square_factor"] == factor
            left_interval, right_interval = witness["left"], witness["right"]
            for number, stored in ((left, left_interval), (right, right_interval)):
                lower, upper = Fraction(stored["lower"]), Fraction(stored["upper"])
                assert sp.N(lower, 80) < sp.N(number, 80) < sp.N(upper, 80)
            assert left_interval["sign"] != right_interval["sign"]
        pencil = item["reduced_parity_pencil"]
        assert pencil["lambda_squared"] == "384"
        zero = item["zero_variety"]
        assert zero["ambient_dimension_over_C"] == 30
        assert zero["active_dimension_over_C"] == 12
        assert zero["spectator_dimension_over_C"] == 10
        assert zero["dimension_over_C"] == 22
        assert zero["irreducible_components_over_C"] == 1
    classification = value["classification"]
    assert classification["all_three_multiplicity_two_L3_zero_varieties_classified"]
    assert classification["all_m_irreducible_decomposition_classified"]
    assert classification["internal_spectator_split_certified"]
    assert classification["real_parity_pencils_diagonalizable"]
    assert not classification["other_eighteen_parent_fibre_zero_varieties_classified"]
    assert not classification["same_fibre_quadratic_sources_classified"]
    assert not classification["taub_common_zero_intersection_classified"]
    assert not classification["complete_two_fibre_tangent_cone_classified"]
    assert not classification["smooth_secular_classified"]
    assert not classification["causal_or_quantum_claim"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_MULTIPLICITY_TWO_L3_ZERO_VARIETIES independent verification: PASS")
