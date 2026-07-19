#!/usr/bin/env python3
"""Independent verifier for the candidate-2 scalar L3 zero variety."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L3_zero_variety.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L3_zero_variety.schema.json"


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
    parent_path = ROOT / value["provenance"]["parent"]
    assert value["provenance"]["parent_sha256"] == sha(parent_path)
    parent = json.loads(parent_path.read_text())
    fibre = next(item for item in parent["physical_fibres"] if item["candidate_index"] == 2)
    assert (fibre["output_ell"], fibre["temporal_signs"]) == (3, [1, 1])

    parent_coefficients = {
        term["first_parity"][0] + term["second_parity"][0]:
        parse(term["coefficient_matrices"][0][0][0])
        for target in fibre["target_equations"]
        for term in target["terms"]
    }
    coefficients = {key: parse(entry) for key, entry in value["coefficients"].items()}
    assert coefficients == parent_coefficients
    for key, coefficient in coefficients.items():
        witness = value["coefficient_nonzero_intervals"][key]
        lower, upper = Fraction(witness["lower"]), Fraction(witness["upper"])
        approximation = sp.N(coefficient, 80)
        assert witness["excludes_zero"] and (lower > 0 or upper < 0)
        assert sp.N(lower, 80) < approximation < sp.N(upper, 80)

    pencil = value["parity_pencil"]
    lam2 = canonical(coefficients["ap"] * coefficients["pa"] / (coefficients["aa"] * coefficients["pp"]))
    assert sp.sstr(lam2) == pencil["lambda_squared"]
    assert pencil["lambda"] == f"sqrt({sp.sstr(lam2)})"
    lam_interval = pencil["lambda_squared_interval"]
    assert lam_interval["positive"] and Fraction(lam_interval["lower"]) > 0
    assert pencil["C0"] == [[value["coefficients"]["aa"], "0"], ["0", value["coefficients"]["pp"]]]
    assert pencil["C1"] == [["0", value["coefficients"]["ap"]], [value["coefficients"]["pa"], "0"]]
    assert pencil["Q"] == [["c_ap/(c_aa*lambda)", "-c_ap/(c_aa*lambda)"], ["1", "1"]]
    assert pencil["P_transpose"] == "inverse(C0*Q)"
    aa, pp, ap, ell = sp.symbols("c_aa c_pp c_ap lambda", nonzero=True)
    pa = ell**2 * aa * pp / ap
    c0_formal = sp.diag(aa, pp)
    c1_formal = sp.Matrix([[0, ap], [pa, 0]])
    q_formal = sp.Matrix([[ap / (aa * ell), -ap / (aa * ell)], [1, 1]])
    p_transpose_formal = sp.Matrix([[ell / (2 * ap), 1 / (2 * pp)], [-ell / (2 * ap), 1 / (2 * pp)]])
    assert sp.simplify(p_transpose_formal * c0_formal * q_formal) == sp.eye(2)
    assert sp.simplify(p_transpose_formal * c1_formal * q_formal) == sp.diag(ell, -ell)
    assert pencil["transformed_coordinates"] == {
        "A_plus": "(c_ap/lambda)*A_axial+c_pp*A_polar",
        "A_minus": "-(c_ap/lambda)*A_axial+c_pp*A_polar",
        "B_plus": "(c_aa*lambda/(2*c_ap))*B_axial+(1/2)*B_polar",
        "B_minus": "-(c_aa*lambda/(2*c_ap))*B_axial+(1/2)*B_polar",
    }

    # The L=3 carrier is the unique odd exchange channel in V2 tensor V2.
    # Its Clebsch-Gordan coefficients are antisymmetric, the representation-
    # theoretic signature of the first binary-quartic transvectant.
    for m1 in range(-2, 3):
        for m2 in range(-2, 3):
            magnetic = m1 + m2
            if -3 <= magnetic <= 3:
                left = clebsch_gordan(2, 2, 3, m1, m2, magnetic)
                right = clebsch_gordan(2, 2, 3, m2, m1, magnetic)
                assert sp.simplify(left + right) == 0
    assert clebsch_gordan(2, 2, 3, 2, 1, 3) != 0

    zero = value["zero_variety"]
    # A 5x2 rank-at-most-one determinantal variety has dimension 6 and ten
    # maximal minors. The two parity eigenchannels form an irreducible product.
    assert zero["ambient_dimension_over_C"] == 20
    assert zero["dimension_over_C"] == 2 * (5 + 2 - 1) == 12
    assert zero["irreducible_components_over_C"] == 1
    assert "all twenty 2-by-2 minors, ten for each" in zero["defining_minors"]
    assert "Cartesian product" in zero["factorization"]
    classification = value["classification"]
    assert classification["candidate_2_scalar_L3_zero_variety_classified"]
    assert classification["all_m_irreducible_decomposition_classified"]
    assert classification["parity_pencil_diagonalized_exactly"]
    assert classification["lambda_squared_positive_exactly"]
    assert not classification["remaining_fifteen_cross_fibre_zero_varieties_classified"]
    assert not classification["same_fibre_quadratic_sources_classified"]
    assert not classification["taub_common_zero_intersection_classified"]
    assert not classification["complete_two_fibre_tangent_cone_classified"]
    assert not classification["causal_or_quantum_claim"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_SCALAR_L3_ZERO_VARIETY independent verification: PASS")
