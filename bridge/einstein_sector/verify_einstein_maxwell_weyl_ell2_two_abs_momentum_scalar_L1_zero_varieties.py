#!/usr/bin/env python3
"""Independent verifier for the three scalar-internal L1 zero varieties."""
from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def monic_strings(polynomials: list[sp.Expr], variables: tuple[sp.Symbol, ...]) -> list[str]:
    result = {
        sp.sstr(sp.Poly(sp.expand(expression), *variables).monic().as_expr())
        for expression in polynomials
        if expression != 0
    }
    return sorted(result)


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == sha(SCHEMA)
    parent_path = ROOT / value["provenance"]["parent"]
    assert value["provenance"]["parent_sha256"] == sha(parent_path)
    parent = json.loads(parent_path.read_text())
    fibres = [item for item in parent["physical_fibres"] if item["output_ell"] == 1]
    assert [item["candidate_index"] for item in fibres] == [14, 17, 20]
    assert [item["candidate_index"] for item in value["decompositions"]] == [14, 17, 20]

    for source, item in zip(fibres, value["decompositions"], strict=True):
        assert source["fibre_id"] == item["fibre_id"]
        assert source["temporal_channel"] == item["temporal_channel"] == "DIFFERENCE"
        assert source["temporal_signs"] == item["temporal_signs"] == [1, -1]
        parent_coefficients = {
            term["first_parity"][0] + term["second_parity"][0]:
            parse(term["coefficient_matrices"][0][0][0])
            for target in source["target_equations"]
            for term in target["terms"]
        }
        coefficients = {key: parse(entry) for key, entry in item["coefficients"].items()}
        assert coefficients == parent_coefficients
        for key, coefficient in coefficients.items():
            witness = item["coefficient_nonzero_intervals"][key]
            lower, upper = Fraction(witness["lower"]), Fraction(witness["upper"])
            assert witness["excludes_zero"] and (lower > 0 or upper < 0)
            assert sp.N(lower, 80) < sp.N(coefficient, 80) < sp.N(upper, 80)
        assert canonical(coefficients["pp"] - 3 * coefficients["aa"]) == 0
        assert canonical(coefficients["ap"] - coefficients["pa"]) == 0
        lambda_squared = canonical(coefficients["ap"] * coefficients["pa"] / (coefficients["aa"] * coefficients["pp"]))
        assert canonical(lambda_squared - sp.Rational(128, 5)) == 0
        zero = item["zero_variety"]
        assert (
            zero["ambient_dimension_over_C"],
            zero["dimension_over_C"],
            zero["codimension_over_C"],
            zero["irreducible_components_over_C"],
        ) == (20, 14, 6, 1)

    # Independently reconstruct the third transvectant and its rank strata.
    f = sp.symbols("f0:5")
    f0, f1, f2, f3, f4 = f
    matrix = sp.Matrix([
        [-f3, 3 * f2, -3 * f1, f0, 0],
        [-f4, 2 * f3, 0, -2 * f1, f0],
        [0, -f4, 3 * f3, -3 * f2, f1],
    ])
    certificate = value["third_transvectant_certificate"]
    assert certificate["matrix_A_f"] == [[sp.sstr(entry) for entry in row] for row in matrix.tolist()]
    three_minors = [matrix[:, columns].det() for columns in itertools.combinations(range(5), 3)]
    rank_drop = monic_strings(three_minors, f)
    assert len(rank_drop) == 7
    assert rank_drop == certificate["rank_at_most_two_monic_groebner_basis"]
    a, b, c = sp.symbols("a b c")
    relations = [f0-a**2, f1-a*b, 3*f2-a*c-2*b**2, f3-b*c, f4-c**2]
    elimination = sp.groebner(relations, a, b, c, *f, order="lex")
    eliminated = [polynomial.as_expr() for polynomial in elimination.polys if not any(polynomial.as_expr().has(variable) for variable in (a,b,c))]
    assert monic_strings(eliminated, f) == rank_drop
    assert certificate["square_elimination_monic_groebner_basis"] == rank_drop
    two_minors = [matrix.extract(rows, columns).det() for rows in itertools.combinations(range(3),2) for columns in itertools.combinations(range(5),2)]
    rank_one = sp.groebner(two_minors, *f, order="grevlex")
    rank_one_basis = monic_strings([polynomial.as_expr() for polynomial in rank_one.polys], f)
    expected_rank_one = monic_strings([f[i]*f[j] for i in range(5) for j in range(i,5)], f)
    assert rank_one_basis == expected_rank_one == certificate["rank_at_most_one_monic_groebner_basis"]
    assert matrix.subs({f0:1,f1:0,f2:0,f3:0,f4:1})[:,(0,1,3)].det() == 1

    for m1 in range(-2, 3):
        for m2 in range(-2, 3):
            magnetic = m1 + m2
            if -1 <= magnetic <= 1:
                left = clebsch_gordan(2, 2, 1, m1, m2, magnetic)
                right = clebsch_gordan(2, 2, 1, m2, m1, magnetic)
                assert sp.simplify(left + right) == 0
    assert clebsch_gordan(2, 2, 1, 2, -1, 1) != 0

    summary = value["summary"]
    assert (
        summary["classified_physical_fibres"],
        summary["irreducible_components_per_fibre_over_C"],
        summary["dimension_per_fibre_over_C"],
        summary["parent_physical_fibres_outside_this_certificate"],
    ) == (3, 1, 14, 18)
    classification = value["classification"]
    assert classification["all_three_scalar_L1_zero_varieties_classified"]
    assert classification["all_m_irreducible_decomposition_classified"]
    assert classification["third_transvectant_rank_stratification_certified"]
    assert classification["parity_pencils_diagonalized_exactly"]
    assert not classification["other_eighteen_parent_fibre_zero_varieties_classified"]
    assert not classification["same_fibre_quadratic_sources_classified"]
    assert not classification["taub_common_zero_intersection_classified"]
    assert not classification["complete_two_fibre_tangent_cone_classified"]
    assert not classification["causal_or_quantum_claim"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_SCALAR_L1_ZERO_VARIETIES independent verification: PASS")
