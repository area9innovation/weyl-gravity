"""Independent verifier for the candidate-17/20 current-radical witness."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_L1_active_restricted_current_degeneracy.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positive(interval: dict[str, object]) -> bool:
    numerator, denominator = interval["lower"].split("/")
    return Fraction(int(numerator), int(denominator)) > 0 and interval["positive"]


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


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

    # Reconstruct the parity-channel algebra without importing the producer.
    a, lam = sp.symbols("a lambda", nonzero=True, real=True)
    D = sp.diag(1, 3)
    for row in payload["parity_current_reduction"]["exact_transform_audit"]:
        epsilon = row["epsilon"]
        r = epsilon * sp.sqrt(3)
        b = a * lam * r
        Q = sp.Matrix([[r, -r], [1, 1]])
        C0 = sp.Matrix([[a, b], [b, 3 * a]])
        P = sp.simplify((C0 * Q).inv().T)
        diagonal = sp.diag(1 / (6 * a * (lam + 1)), -1 / (6 * a * (lam - 1)))
        assert sp.simplify(P - Q * diagonal) == sp.zeros(2)
        assert Q.T * D * Q == 6 * sp.eye(2)
        S = sp.diag(sp.Rational(3, 2) * a * (lam + 1), sp.Rational(3, 2) * a * (lam - 1))
        normalized = sp.simplify(P * S)
        assert normalized == Q * sp.diag(sp.Rational(1, 4), -sp.Rational(1, 4))
        assert sp.simplify(normalized.T * D * normalized) == sp.Rational(3, 8) * sp.eye(2)
        assert row["normalized_positive_to_negative_current_ratio"] == "1/16"

    current_audit = payload["parity_current_reduction"]["direct_action_current_shell_audit"]
    assert current_audit["q_minus"]["polar_over_axial_ratio"] == "3"
    assert current_audit["q_plus"]["polar_over_axial_ratio"] == "3"
    assert current_audit["q_minus"]["common_sign"] == "negative"
    assert current_audit["q_plus"]["common_sign"] == "positive"

    # Reconstruct the smooth T3 point, tangent, restricted Gram and radical.
    f_symbols = sp.symbols("f0:5")
    g_symbols = sp.symbols("g0:5")
    f0, f1, f2, f3, f4 = f_symbols
    matrix = sp.Matrix([[-f3, 3 * f2, -3 * f1, f0, 0], [-f4, 2 * f3, 0, -2 * f1, f0], [0, -f4, 3 * f3, -3 * f2, f1]])
    equations = matrix * sp.Matrix(g_symbols)
    f = sp.Matrix([1, 0, 0, 0, 1])
    g = sp.Matrix([1, 0, 1, 0, 1])
    substitution = dict(zip(f_symbols, f)) | dict(zip(g_symbols, g))
    jacobian = equations.jacobian((*f_symbols, *g_symbols)).subs(substitution)
    tangent = sp.Matrix.hstack(*jacobian.nullspace())
    angular = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    current = sp.diag(*[-value for value in angular.diagonal()], *[sp.Rational(1, 16) * value for value in angular.diagonal()])
    restricted = sp.simplify(tangent.T * current * tangent)
    nullspace = restricted.nullspace()
    reconstructed_radical = sp.simplify(tangent * nullspace[0])
    expected_radical = sp.Matrix([0, sp.Rational(1, 4), 0, sp.Rational(1, 4), 0, 0, 1, 0, 1, 0])
    assert equations.subs(substitution) == sp.zeros(3, 1)
    assert jacobian.rank() == 3 and tangent.shape == (10, 7)
    assert restricted.rank() == 6 and len(nullspace) == 1
    assert reconstructed_radical == expected_radical
    assert jacobian * reconstructed_radical == sp.zeros(3, 1)
    assert reconstructed_radical.T * current * tangent == sp.zeros(1, 7)
    assert (f.T * angular * reconstructed_radical[:5, 0])[0] == 0
    assert (g.T * angular * reconstructed_radical[5:, 0])[0] == 0
    assert sp.factor(sp.Rational(1, 16) * (g.T * angular * g)[0] / (f.T * angular * f)[0]) == sp.Rational(13, 192)

    radical = payload["universal_smooth_radical"]
    assert radical["jacobian_rank"] == 3
    assert radical["affine_tangent_complex_dimension"] == 7
    assert radical["restricted_tangent_rank"] == 6
    assert radical["restricted_tangent_nullity"] == 1
    assert radical["normalized_positive_to_negative_current_coefficient_ratio"] == "1/16"
    assert radical["absolute_current_occupation_ratio_positive_over_negative"] == "13/192"
    assert radical["fixed_norm_tangency"] == {"f_inner_delta_f": "0", "g_inner_delta_g": "0"}
    assert all(value == "0" for pair in radical["individual_rotation_moments"].values() for value in pair)
    assert radical["ambient_radical_vector_delta_f_delta_g"] == ["0", "1/4", "0", "1/4", "0", "0", "1", "0", "1", "0"]

    input_map = payload["provenance"]["inputs"]
    scalar_rays = json.loads((ROOT / input_map["scalar_rays"]["path"]).read_text())
    resonance_faces = json.loads((ROOT / input_map["resonance_faces"]["path"]).read_text())
    rays = {row["ray_id"]: row for row in scalar_rays["extreme_rays"]}
    faces = {row["candidate_index"]: row for row in resonance_faces["face_rows"]}
    rows = payload["scalar_cone_witnesses"]
    assert [row["candidate_index"] for row in rows] == [17, 20]
    assert [row["active_ray"] for row in rows] == ["R3", "R2"]
    assert all(row["automatic_ray"] == "R1" for row in rows)
    assert all(row["resulting_positive_over_negative_ratio"] == "13/192" for row in rows)
    assert all(positive(row["automatic_ray_coefficient_interval"]) for row in rows)
    assert all(positive(row["active_ray_ratio_minus_13_over_192_interval"]) for row in rows)
    for row in rows:
        rho = parse(faces[row["candidate_index"]]["rho"])
        active = ray_weights(rays[row["active_ray"]], rho)
        automatic = ray_weights(rays[row["automatic_ray"]], rho)
        positive_node = row["positive_resonant_node"]
        negative_node = row["negative_resonant_node"]
        target = sp.Rational(13, 192)
        coefficient = sp.factor((active[positive_node] / target - active[negative_node]) / automatic[negative_node])
        assert sp.simplify(coefficient - parse(row["automatic_ray_coefficient_s"])) == 0
        resulting = sp.cancel(active[positive_node] / (active[negative_node] + coefficient * automatic[negative_node]))
        assert sp.simplify(resulting - target) == 0

    flags = payload["classification"]
    assert flags["candidate17_smooth_active_restricted_current_degeneracy"]
    assert flags["candidate20_smooth_active_restricted_current_degeneracy"]
    assert flags["degeneracy_occurs_inside_each_exact_scalar_cone"]
    assert flags["degenerate_points_have_all_five_stabilizer_moment_maps_zero"]
    assert flags["degenerate_points_are_bounded_second_order_tangents"]
    assert not flags["global_active_component_symplectic_orbifold"]
    assert not flags["proper_moment_map_connected_fibre_theorem_applicable_globally"]
    assert not flags["candidate18_active_restricted_current_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_L1_ACTIVE_RESTRICTED_CURRENT_DEGENERACY verifier: PASS")


if __name__ == "__main__":
    verify()
