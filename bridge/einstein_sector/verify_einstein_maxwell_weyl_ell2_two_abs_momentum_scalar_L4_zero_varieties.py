#!/usr/bin/env python3
"""Independent verifier for the five scalar-internal L4 zero varieties."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == sha(SCHEMA)
    parent = ROOT / value["provenance"]["parent"]
    assert value["provenance"]["parent_sha256"] == sha(parent)
    parent_value = json.loads(parent.read_text())
    conversions = {
        fibre["candidate_index"]: parse(
            fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"]
        )
        for fibre in parent_value["physical_fibres"]
        if fibre["output_ell"] == 4
    }
    assert [item["candidate_index"] for item in value["decompositions"]] == [3, 5, 9, 15, 21]

    for item in value["decompositions"]:
        coefficients = {key: parse(entry) for key, entry in item["coefficients"].items()}
        assert set(coefficients) == {"aa", "pp", "ap", "pa"}
        for key, coefficient in coefficients.items():
            interval = item["axisymmetric_source_coordinate_nonzero_intervals"][key]
            lower = Fraction(interval["lower"])
            upper = Fraction(interval["upper"])
            assert interval["excludes_zero"] and (lower > 0 or upper < 0)
            approximation = sp.N(coefficient * conversions[item["candidate_index"]], 80)
            assert sp.N(lower, 80) < approximation < sp.N(upper, 80)
        r_squared = canonical(
            coefficients["aa"] * coefficients["ap"]
            / (coefficients["pp"] * coefficients["pa"])
        )
        assert canonical(r_squared - parse(item["r_squared"])) == 0
        r_interval = item["r_squared_interval"]
        assert r_interval["positive"] and Fraction(r_interval["lower"]) > 0
        s_over_r = canonical(-coefficients["pa"] / coefficients["ap"])
        assert canonical(s_over_r - parse(item["s_over_r"])) == 0
        components = item["irreducible_components_over_C"]
        assert [component["component_id"] for component in components] == [
            "first_fibre_zero",
            "second_fibre_zero",
            "mixed_plus",
            "mixed_minus",
        ]
        assert all(component["dimension_over_C"] == 10 for component in components)
        for component in components[2:]:
            r_value = parse(component["r"])
            s_value = parse(component["s"])
            assert canonical(r_value**2 - r_squared) == 0
            assert canonical(s_value - s_over_r * r_value) == 0
            assert canonical(coefficients["aa"] + coefficients["pp"] * r_value * s_value) == 0
            assert canonical(coefficients["ap"] * s_value + coefficients["pa"] * r_value) == 0

    summary = value["summary"]
    assert (
        summary["classified_physical_fibres"],
        summary["irreducible_components_per_fibre_over_C"],
        summary["mixed_components_real_on_declared_coefficient_embedding"],
        summary["remaining_cross_fibre_physical_fibres_open"],
    ) == (5, 4, 10, 16)
    classification = value["classification"]
    assert classification["complete_scalar_internal_L4_zero_varieties_classified"]
    assert classification["all_m_mixed_components_classified"]
    assert classification["all_five_r_squared_values_positive_exactly"]
    assert not classification["remaining_sixteen_cross_fibre_zero_varieties_classified"]
    assert not classification["same_fibre_quadratic_sources_classified"]
    assert not classification["taub_common_zero_intersection_classified"]
    assert not classification["complete_two_fibre_tangent_cone_classified"]
    assert not classification["causal_or_quantum_claim"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_SCALAR_L4_ZERO_VARIETIES independent verification: PASS")
