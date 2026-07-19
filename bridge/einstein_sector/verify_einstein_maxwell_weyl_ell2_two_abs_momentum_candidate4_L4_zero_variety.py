#!/usr/bin/env python3
"""Independent verifier for the candidate-4 target-doublet L=4 variety."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_L4_zero_variety.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_L4_zero_variety.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == sha(SCHEMA)

    parent_path = ROOT / value["provenance"]["parent"]
    assert value["provenance"]["parent_sha256"] == sha(parent_path)
    parent = json.loads(parent_path.read_text())
    fibre = next(item for item in parent["physical_fibres"] if item["candidate_index"] == 4)
    assert (
        fibre["output_ell"],
        fibre["first_branch_multiplicity_per_parity"],
        fibre["second_branch_multiplicity_per_parity"],
        fibre["target_cokernel_dimension_per_parity"],
        fibre["temporal_signs"],
    ) == (4, 1, 1, 2, [1, 1])
    assert value["fibre_id"] == fibre["fibre_id"] and value["rho"] == fibre["rho"]

    expected = {
        term["first_parity"][0] + term["second_parity"][0]:
        [parse(component[0][0]) for component in term["coefficient_matrices"]]
        for target in fibre["target_equations"]
        for term in target["terms"]
    }
    coefficients = {
        key: [parse(component) for component in vector]
        for key, vector in value["coefficients"].items()
    }
    assert coefficients == expected
    assert all((coefficients["ap"][i] + coefficients["pa"][i]).equals(0) for i in range(2))
    assert coefficients["aa"][0] == coefficients["pp"][0] == 0
    assert (coefficients["pp"][1] + 3 * coefficients["aa"][1]).equals(0)

    indexed = {
        "cross_target_0": coefficients["ap"][0],
        "cross_target_1": coefficients["ap"][1],
        "same_target_1": coefficients["aa"][1],
    }
    conversion = parse(value["axisymmetric_to_reduced_conversion"])
    assert conversion == parse(fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"])
    for key, coefficient in indexed.items():
        witness = value["coefficient_nonzero_intervals"][key]
        lower, upper = Fraction(witness["lower"]), Fraction(witness["upper"])
        assert witness["excludes_zero"] and (lower > 0 or upper < 0)
        assert sp.N(lower, 80) < sp.N(coefficient * conversion, 80) < sp.N(upper, 80)

    # Independently replay the two factorizations in a polynomial ring.
    aa, ap, ba, bp = sp.symbols("A_a A_p B_a B_p")
    cross = aa * bp - ap * ba
    same = aa * ba - 3 * ap * bp
    assert sp.expand(same + sp.sqrt(3) * cross - (aa - sp.sqrt(3) * ap) * (ba + sp.sqrt(3) * bp)) == 0
    assert sp.expand(same - sp.sqrt(3) * cross - (aa + sp.sqrt(3) * ap) * (ba - sp.sqrt(3) * bp)) == 0

    components = value["zero_variety"]["irreducible_components_over_C"]
    assert [component["component_id"] for component in components] == [
        "first_fibre_zero",
        "second_fibre_zero",
        "mixed_plus",
        "mixed_minus",
    ]
    assert all(component["dimension_over_C"] == 10 for component in components)
    assert value["zero_variety"]["all_mixed_components_real"]
    classification = value["classification"]
    assert classification["candidate_4_target_doublet_L4_zero_variety_classified"]
    assert classification["all_m_irreducible_decomposition_classified"]
    assert classification["two_target_components_reduced_exactly"]
    assert not classification["other_twenty_parent_fibre_zero_varieties_classified"]
    assert not classification["same_fibre_quadratic_sources_classified"]
    assert not classification["taub_common_zero_intersection_classified"]
    assert not classification["complete_two_fibre_tangent_cone_classified"]
    assert not classification["smooth_secular_classified"]
    assert not classification["causal_or_quantum_claim"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE4_L4_ZERO_VARIETY independent verification: PASS")
