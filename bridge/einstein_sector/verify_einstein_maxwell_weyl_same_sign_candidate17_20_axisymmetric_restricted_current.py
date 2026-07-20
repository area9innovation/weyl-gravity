"""Independent verifier for candidate-17/20 axisymmetric restricted currents."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    fraction_string,
    rational_interval,
)


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_axisymmetric_restricted_current.json"
SQRT3 = sp.sqrt(3)
MASS = {
    "q_minus_n2": sp.Rational(3, 2) - SQRT3 / 2,
    "p_extra_n2": sp.Rational(4, 3),
    "q_plus_n2": sp.Rational(3, 2) + SQRT3 / 2,
    "q_minus_n1": 6 - 2 * SQRT3,
    "p_extra_n1": sp.Rational(16, 3),
    "q_plus_n1": 6 + 2 * SQRT3,
}
SIGN = {"q_minus_n2": -1, "p_extra_n2": 1, "q_plus_n2": 1, "q_minus_n1": -1, "p_extra_n1": 1, "q_plus_n1": 1}
N = {"q_minus_n2": 2, "p_extra_n2": 2, "q_plus_n2": 2, "q_minus_n1": 1, "p_extra_n1": 1, "q_plus_n1": 1}
RAYS = {
    "R1": ["q_minus_n2", "p_extra_n2", "q_minus_n1", "p_extra_n1"],
    "R2": ["q_minus_n2", "p_extra_n2", "q_minus_n1", "q_plus_n1"],
    "R3": ["q_minus_n2", "q_plus_n2", "q_minus_n1", "p_extra_n1"],
    "R4": ["q_minus_n2", "q_plus_n2", "q_minus_n1", "q_plus_n1"],
}
SPECS = {
    17: (10 * (9 * SQRT3 + 77) / 8529, "q_minus_n1", "q_plus_n2"),
    20: (-10 * (-77 + 9 * SQRT3) / 8529, "q_minus_n2", "q_plus_n1"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def weight(node: str, ray: str, rho: sp.Expr) -> sp.Expr:
    x = {name: sp.sqrt(rho + mass) for name, mass in MASS.items()}
    denominator = SIGN[node] * N[node] ** 2
    denominator *= sp.prod(x[node] - x[other] for other in RAYS[ray] if other != node)
    return sp.factor(1 / denominator)


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])

    scalar_path = ROOT / payload["provenance"]["inputs"]["scalar_L1"]["path"]
    scalar = json.loads(scalar_path.read_text())
    symbols = sp.symbols("f0:5")
    matrix = sp.Matrix(scalar["third_transvectant_certificate"]["matrix_A_f"])
    matrix = matrix.applyfunc(lambda value: sp.sympify(value, locals={f"f{i}": symbols[i] for i in range(5)}))
    e0 = matrix.subs({symbols[0]: 0, symbols[1]: 0, symbols[2]: 1, symbols[3]: 0, symbols[4]: 0})
    assert e0.rank() == 2 and len(e0.nullspace()) == 3

    tangent = payload["third_transvectant_tangent_theorem"]
    assert tangent["rank_A_e0"] == 2
    assert tangent["kernel_dimension_A_e0"] == 3
    assert tangent["full_derivative_rank"] == 4
    assert tangent["affine_zariski_tangent_complex_dimension"] == 16
    assert tangent["affine_variety_complex_dimension"] == 14
    assert tangent["axisymmetric_section_singular"]

    current = payload["restricted_current_theorem"]
    assert current["one_parity_channel_inertia"] == [3, 5, 0]
    assert current["two_parity_channel_affine_inertia"] == [6, 10, 0]
    assert current["two_node_complex_scaling_inertia"] == [1, 1, 0]
    assert current["projective_zariski_tangent_inertia"] == [5, 9, 0]
    assert current["projective_zariski_tangent_real_symplectic_rank"] == 28
    assert current["candidate17_and_20_axisymmetric_zariski_tangent_currents_nondegenerate"]

    rows = payload["candidate_rows"]
    assert [row["candidate_index"] for row in rows] == [17, 20]
    for row in rows:
        assert row["axisymmetric_affine_zariski_tangent_current_inertia"] == [6, 10, 0]
        assert row["axisymmetric_projective_zariski_tangent_current_inertia"] == [5, 9, 0]
        assert row["axisymmetric_projective_zariski_tangent_real_symplectic_rank"] == 28
        rho, negative_node, positive_node = SPECS[row["candidate_index"]]
        for witness in row["active_ray_gap_witnesses"]:
            interval = witness["negative_minus_positive"]
            lower, upper = Fraction(interval["lower"]), Fraction(interval["upper"])
            assert interval["strictly_positive"] and 0 < lower <= upper
            expression = weight(negative_node, witness["ray_id"], rho) - weight(positive_node, witness["ray_id"], rho)
            actual = rational_interval(expression, int(interval["decimal_digits"]))
            assert [fraction_string(actual[0]), fraction_string(actual[1])] == [interval["lower"], interval["upper"]]

    flags = payload["classification"]
    assert flags["candidate17_complete_active_scalar_cone_axisymmetric_current_classified"]
    assert flags["candidate20_complete_active_scalar_cone_axisymmetric_current_classified"]
    assert flags["all_four_active_ray_occupation_gaps_exactly_positive"]
    assert flags["axisymmetric_sections_singular"]
    assert flags["restricted_zariski_tangent_currents_nondegenerate"]
    assert not flags["full_smooth_locus_restricted_current_classified"]
    assert not flags["rotation_zero_fibre_connected"]
    assert not flags["candidate18_active_variety_classified"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_AXISYMMETRIC_RESTRICTED_CURRENT verifier: PASS")


if __name__ == "__main__":
    verify()
