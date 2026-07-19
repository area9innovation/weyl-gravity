#!/usr/bin/env python3
"""Independent exact verifier for the multiplicity-two-source L=4 varieties."""
from __future__ import annotations

import gc
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator
from sympy.core.cache import clear_cache
from sympy.polys.numberfields import to_number_field


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_rank_one_branch_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_rank_one_branch_zero_varieties.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def exact_squared_relation_vanishes(
    relation: tuple[sp.Expr, sp.Expr, int, int],
) -> bool:
    left, right, numerator, denominator = relation
    residual = sp.sqrtdenest(denominator * left**2 - numerator * right**2)
    algebraic = to_number_field(residual)
    result = algebraic.as_expr() == 0
    del algebraic, residual
    clear_cache()
    gc.collect()
    return result


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
        if item["candidate_index"] in (8, 12)
    }
    assert list(fibres) == [8, 12]
    assert [item["candidate_index"] for item in value["decompositions"]] == [8, 12]
    exact_relations = []
    for item in value["decompositions"]:
        fibre = fibres[item["candidate_index"]]
        expected = {}
        for target in fibre["target_equations"]:
            for term in target["terms"]:
                matrix = sp.Matrix(
                    [[parse(entry) for entry in row] for row in term["coefficient_matrices"][0]]
                )
                row = matrix if matrix.rows == 1 else matrix.T
                expected[term["first_parity"][0] + term["second_parity"][0]] = list(row)
        rows = {key: [parse(entry) for entry in row] for key, row in item["coefficient_rows"].items()}
        assert rows == expected
        conversion = parse(fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"])
        if item["candidate_index"] == 8:
            relations = (
                [(rows["pa"][j], rows["aa"][j], 3, 40) for j in range(2)]
                + [(rows["pp"][j], rows["ap"][j], 120, 1) for j in range(2)]
            )
            scalar = {"aa": sp.S.One, "pp": -2 * sp.sqrt(30), "ap": sp.S.One, "pa": -sp.sqrt(30) / 20}
        else:
            relations = (
                [(rows["ap"][j], rows["aa"][j], 3, 40) for j in range(2)]
                + [(rows["pp"][j], rows["pa"][j], 120, 1) for j in range(2)]
            )
            scalar = {"aa": sp.S.One, "pp": -2 * sp.sqrt(30), "ap": -sp.sqrt(30) / 20, "pa": sp.S.One}
        relations = [
            (sp.radsimp(left * conversion), sp.radsimp(right * conversion), numerator, denominator)
            for left, right, numerator, denominator in relations
        ]
        exact_relations.extend(relations)
        assert item["axisymmetric_to_reduced_conversion"] == fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"]
        for relation, witness in zip(relations, item["exact_relation_interval_witnesses"]):
            left, right, numerator, denominator = relation
            assert (witness["squared_ratio_numerator"], witness["squared_ratio_denominator"]) == (numerator, denominator)
            for number, stored in ((left, witness["left"]), (right, witness["right"])):
                lower, upper = Fraction(stored["lower"]), Fraction(stored["upper"])
                assert sp.N(lower, 80) < sp.N(number, 80) < sp.N(upper, 80)
            assert witness["left"]["sign"] != witness["right"]["sign"]
        r_squared = sp.cancel(scalar["aa"] * scalar["ap"] / (scalar["pp"] * scalar["pa"]))
        s_over_r = sp.cancel(-scalar["pa"] / scalar["ap"])
        generalized_eigenvalue_square = sp.cancel(
            scalar["ap"] * scalar["pa"] / (scalar["aa"] * scalar["pp"])
        )
        assert generalized_eigenvalue_square == sp.Rational(1, 40)
        assert item["generalized_eigenvalue_square"] == "1/40"
        assert r_squared == parse(item["r_squared"])
        assert s_over_r == parse(item["s_over_r"])
        for sign in (1, -1):
            r_value = sp.radsimp(sign * sp.sqrt(r_squared))
            s_value = sp.radsimp(s_over_r * r_value)
            assert sp.radsimp(scalar["aa"] + scalar["pp"] * r_value * s_value) == 0
            assert sp.radsimp(scalar["ap"] * s_value + scalar["pa"] * r_value) == 0
        zero = item["zero_variety"]
        assert zero["ambient_dimension_over_C"] == 30
        assert zero["spectator_dimension_over_C"] == 10
        assert zero["dimension_per_component_over_C"] == 20
        assert len(zero["irreducible_components_over_C"]) == 4
        assert zero["all_mixed_components_real"]
    with ProcessPoolExecutor(max_workers=len(exact_relations)) as pool:
        assert all(pool.map(exact_squared_relation_vanishes, exact_relations))
    summary = value["summary"]
    assert summary["classified_candidates"] == [8, 12]
    assert summary["irreducible_components_per_fibre_over_C"] == 4
    classification = value["classification"]
    assert classification["both_multiplicity_two_L4_zero_varieties_classified"]
    assert classification["all_m_irreducible_decomposition_classified"]
    assert classification["internal_spectator_split_certified"]
    assert classification["all_mixed_components_real"]
    assert not classification["other_nineteen_parent_fibre_zero_varieties_classified"]
    assert not classification["same_fibre_quadratic_sources_classified"]
    assert not classification["taub_common_zero_intersection_classified"]
    assert not classification["complete_two_fibre_tangent_cone_classified"]
    assert not classification["smooth_secular_classified"]
    assert not classification["causal_or_quantum_claim"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_RANK_ONE_BRANCH_ZERO_VARIETIES independent verification: PASS")
