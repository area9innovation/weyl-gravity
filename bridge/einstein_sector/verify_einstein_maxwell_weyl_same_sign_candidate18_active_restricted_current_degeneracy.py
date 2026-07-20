"""Independent verifier for candidate 18's smooth active current radicals."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate18_active_restricted_current_degeneracy.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


def positive_interval(interval: dict[str, object]) -> bool:
    lower = Fraction(interval["lower"])
    upper = Fraction(interval["upper"])
    return lower > 0 and upper > lower and interval["positive"] and interval["excludes_zero"]


def negative_interval(interval: dict[str, object]) -> bool:
    lower = Fraction(interval["lower"])
    upper = Fraction(interval["upper"])
    return upper < 0 and upper > lower and not interval["positive"] and interval["excludes_zero"]


def ray_weights(ray: dict[str, object], rho: sp.Expr) -> dict[str, sp.Expr]:
    signs = {"q_minus": -1, "p_extra": 1, "q_plus": 1}
    masses = {"q_minus": 6 - 2 * sp.sqrt(3), "p_extra": sp.Rational(16, 3), "q_plus": 6 + 2 * sp.sqrt(3)}
    labels = {node: (node.rsplit("_n", 1)[0], int(node.rsplit("_n", 1)[1])) for node in ray["support"]}
    frequencies = {node: sp.sqrt(rho + masses[branch] / n**2) for node, (branch, n) in labels.items()}
    result = {}
    for node, (branch, n) in labels.items():
        denominator = sp.Integer(signs[branch] * n**2)
        for other in labels:
            if other != node:
                denominator *= frequencies[node] - frequencies[other]
        result[node] = sp.factor(1 / denominator)
    return result


def rank_one_jacobian_rank() -> int:
    f = sp.symbols("f0:5")
    g = sp.symbols("g0:5")
    equations = [f[i] * g[j] - f[j] * g[i] for i in range(5) for j in range(i + 1, 5)]
    e0 = [0, 0, 1, 0, 0]
    substitution = dict(zip(f, e0)) | dict(zip(g, e0))
    return sp.Matrix(equations).jacobian((*f, *g)).subs(substitution).rank()


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

    current = payload["active_current_reduction"]
    Q = sp.Matrix([[sp.sqrt(3), -sp.sqrt(3)], [1, 1]])
    P = Q.inv().T
    C = sp.Matrix([[0, 3], [1, 0]])
    assert P.T * Q == sp.eye(2)
    assert sp.simplify(P.T * C * Q) == sp.diag(sp.sqrt(3), -sp.sqrt(3))

    wx, wy, h = sp.symbols("w_x w_y h", positive=True)
    positive = sp.simplify(P.T * sp.diag(wx, wy) * P)
    negative = sp.simplify(Q.T * sp.diag(h, 3 * h) * Q)
    assert positive == sp.Matrix([[wx / 12 + wy / 4, -wx / 12 + wy / 4], [-wx / 12 + wy / 4, wx / 12 + wy / 4]])
    assert negative == 6 * h * sp.eye(2)
    for sign, expected in ((1, wy / 2), (-1, wx / 6)):
        z = sp.Matrix([1, sign])
        assert positive * z == expected * z
        assert (positive - expected / (6 * h) * negative) * z == sp.zeros(2, 1)
    assert rank_one_jacobian_rank() == 4
    assert all(row["active_rank_one_factors_nonzero"] for row in current["smooth_radical_families"])
    assert all(row["projective_current_radical_complex_dimension"] == 4 for row in current["smooth_radical_families"])
    assert positive_interval(current["active_positive_weights"]["w_x_interval"])
    assert positive_interval(current["active_positive_weights"]["w_y_interval"])
    assert positive_interval(current["active_positive_weights"]["3w_y_minus_w_x_interval"])
    assert all(positive_interval(row["node_scale_squared_interval"]) for row in current["smooth_radical_families"])

    input_map = payload["provenance"]["inputs"]
    rays_payload = json.loads((ROOT / input_map["scalar_rays"]["path"]).read_text())
    rays = {row["ray_id"]: row for row in rays_payload["extreme_rays"]}
    rho = parse(payload["rho"])
    r1 = ray_weights(rays["R1"], rho)
    r3 = ray_weights(rays["R3"], rho)
    positive_node, negative_node = "p_extra_n1", "q_minus_n2"
    coefficient = sp.factor((r3[positive_node] - r3[negative_node]) / (r1[negative_node] - r1[positive_node]))
    stored_coefficient = parse(payload["scalar_cone_witness"]["s18_exact"])
    assert sp.cancel(sp.together(coefficient - stored_coefficient)) == 0
    assert sp.cancel(r3[positive_node] + coefficient * r1[positive_node] - r3[negative_node] - coefficient * r1[negative_node]) == 0
    scalar = payload["scalar_cone_witness"]
    assert negative_interval(scalar["R1_positive_over_negative_minus_one_interval"])
    assert positive_interval(scalar["R3_positive_over_negative_minus_one_interval"])
    assert positive_interval(scalar["s18_interval"])

    flags = payload["classification"]
    assert flags["candidate18_active_restricted_current_degeneracy"]
    assert flags["degenerate_points_are_smooth_on_the_complete_active_resonance_variety"]
    assert flags["degenerate_points_have_all_five_stabilizer_moment_maps_zero"]
    assert flags["degenerate_points_are_bounded_second_order_tangents"]
    assert not flags["candidate18_global_active_component_symplectic_orbifold"]
    assert not flags["complete_candidate18_degeneracy_divisor_classified"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE18_ACTIVE_RESTRICTED_CURRENT_DEGENERACY verifier: PASS")


if __name__ == "__main__":
    verify()
