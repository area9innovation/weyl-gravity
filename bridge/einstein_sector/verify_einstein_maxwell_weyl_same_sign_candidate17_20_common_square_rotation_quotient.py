"""Independent exact verifier for the candidate-17/20 common-square quotient."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_ray_weight(
    node: str,
    support: list[str],
    rho: sp.Expr,
    node_data: dict[str, tuple[int, int, sp.Expr]],
) -> sp.Expr:
    sign, momentum, mass = node_data[node]
    x = {
        name: sp.sqrt(rho + node_data[name][2] / node_data[name][1] ** 2)
        for name in support
    }
    product = sp.prod(x[node] - x[other] for other in support if other != node)
    return sp.factor(1 / (sign * momentum**2 * product))


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

    # Reconstruct the Cartan-square covariance without importing the producer.
    a, b, c = sp.symbols("a b c")
    q = sp.Matrix([a, b, c])
    square = sp.Matrix([a**2, a * b, (a * c + 2 * b**2) / 3, b * c, c**2])
    d_square = square.jacobian(q)
    j1 = (
        sp.diag(1, 0, -1),
        sp.Matrix([[0, 2, 0], [0, 0, 1], [0, 0, 0]]),
        sp.Matrix([[0, 0, 0], [1, 0, 0], [0, 2, 0]]),
    )
    j2 = (
        sp.diag(2, 1, 0, -1, -2),
        sp.Matrix([[0, 4, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, 0, 2, 0], [0, 0, 0, 0, 1], [0, 0, 0, 0, 0]]),
        sp.Matrix([[0, 0, 0, 0, 0], [1, 0, 0, 0, 0], [0, 2, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, 0, 4, 0]]),
    )
    assert all(sp.simplify(d_square * left * q - right * square) == sp.zeros(5, 1) for left, right in zip(j1, j2))

    z = sp.Matrix(sp.symbols("z0:3"))
    zb = sp.Matrix(sp.symbols("w0:3"))
    s = z * z.T - (z.T * z)[0] * sp.eye(3) / 3
    sb = zb * zb.T - (zb.T * zb)[0] * sp.eye(3) / 3
    lhs = sp.simplify(s * sb - sb * s)
    rhs = sp.simplify((zb.T * z)[0] * (z * zb.T - zb * z.T))
    assert sp.simplify(lhs - rhs) == sp.zeros(3, 3)

    # Independently reconstruct all four decisive frequency-weighted signs.
    sqrt3 = sp.sqrt(3)
    masses = {
        "q_minus_n1": 6 - 2 * sqrt3,
        "q_minus_n2": 6 - 2 * sqrt3,
        "q_plus_n1": 6 + 2 * sqrt3,
        "q_plus_n2": 6 + 2 * sqrt3,
        "p_extra_n1": sp.Rational(16, 3),
        "p_extra_n2": sp.Rational(16, 3),
    }
    signs_momenta = {
        "q_minus_n2": (-1, 2),
        "p_extra_n2": (1, 2),
        "q_plus_n2": (1, 2),
        "q_minus_n1": (-1, 1),
        "p_extra_n1": (1, 1),
        "q_plus_n1": (1, 1),
    }
    node_data = {
        name: (signs_momenta[name][0], signs_momenta[name][1], masses[name])
        for name in masses
    }
    rays_input = payload["provenance"]["inputs"]["scalar_rays"]
    rays_record = json.loads((ROOT / rays_input["path"]).read_text())
    supports = {
        row["ray_id"]: [item["node_id"] for item in row["weight_formula"]]
        for row in rays_record["extreme_rays"]
    }

    def delta(rho: sp.Expr, minus: str, plus: str, ray_id: str) -> sp.Expr:
        minus_frequency = sp.sqrt(signs_momenta[minus][1] ** 2 * rho + masses[minus])
        plus_frequency = sp.sqrt(signs_momenta[plus][1] ** 2 * rho + masses[plus])
        return sp.factor(
            plus_frequency * independent_ray_weight(plus, supports[ray_id], rho, node_data)
            - minus_frequency * independent_ray_weight(minus, supports[ray_id], rho, node_data)
        )

    rho17 = 10 * (9 * sqrt3 + 77) / 8529
    d17_r3 = delta(rho17, "q_minus_n1", "q_plus_n2", "R3")
    d17_r4 = delta(rho17, "q_minus_n1", "q_plus_n2", "R4")
    assert d17_r3.is_negative is True and d17_r4.is_negative is True

    rho20 = -10 * (-77 + 9 * sqrt3) / 8529
    d20_r2 = delta(rho20, "q_minus_n2", "q_plus_n1", "R2")
    d20_r4 = delta(rho20, "q_minus_n2", "q_plus_n1", "R4")
    assert d20_r2.is_negative is True and d20_r4.is_positive is True
    balance = sp.factor(d20_r4 / (-d20_r2))
    assert balance.is_positive is True
    assert sp.simplify(balance * d20_r2 + d20_r4) == 0

    flags = payload["classification"]
    assert flags["candidate17_common_square_rotation_zero_quotient_always_one_point"]
    assert flags["candidate20_rotation_balance_divisor_nonempty"]
    assert flags["candidate20_on_balance_common_square_rotation_zero_quotient_closed_interval"]
    assert not flags["unweighted_occupation_gap_sufficient_for_rotation_imbalance"]
    assert not flags["complete_two_parity_singular_union_quotient_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_COMMON_SQUARE_ROTATION_QUOTIENT verifier: PASS")


if __name__ == "__main__":
    verify()
