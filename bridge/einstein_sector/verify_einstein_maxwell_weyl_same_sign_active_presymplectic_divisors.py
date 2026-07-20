"""Independent verifier for the smooth active presymplectic divisors."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_presymplectic_divisors.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_conormal_identity() -> None:
    # Independent exact fixture: H|ker(J) and J H^{-1} J^T must have equal nullity.
    H = sp.diag(2, -3, 5, -7)
    J = sp.Matrix([[1, 2, 0, 1], [0, 1, 1, -1]])
    tangent = sp.Matrix.hstack(*J.nullspace())
    restricted = tangent.T * H * tangent
    conormal = J * H.inv() * J.T
    assert restricted.cols - restricted.rank() == conormal.cols - conormal.rank()


def verify_third_transvectant(payload: dict[str, object]) -> None:
    f = sp.symbols("f0:5")
    g = sp.symbols("g0:5")
    M = sp.Matrix(
        [
            [-f[3], 3 * f[2], -3 * f[1], f[0], 0],
            [-f[4], 2 * f[3], 0, -2 * f[1], f[0]],
            [0, -f[4], 3 * f[3], -3 * f[2], f[1]],
        ]
    )
    equations = M * sp.Matrix(g)
    J = equations.jacobian((*f, *g))
    point = (1, 0, 0, 0, 1, 1, 0, 1, 0, 1)
    J0 = J.subs(dict(zip((*f, *g), point)))
    W = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    H = sp.diag(*list((-W).diagonal()), *list((sp.Rational(1, 16) * W).diagonal()))
    K = J0 * H.inv() * J0.T
    T = sp.Matrix.hstack(*J0.nullspace())
    G = T.T * H * T
    assert J0.rank() == 3
    assert K == sp.Matrix([[24, 0, 24], [0, 30, 0], [24, 0, 24]])
    assert K.rank() == 2 and G.rank() == 6
    assert K.cols - K.rank() == G.cols - G.rank() == 1
    witness = payload["candidate17_20_third_transvectant"]["exact_smooth_witness"]
    assert witness["K"] == [[str(value) for value in row] for row in K.tolist()]


def verify_rank_one(payload: dict[str, object]) -> None:
    wx, wy, b, r = sp.symbols("w_x w_y b r", positive=True)
    A = sp.Matrix(
        [
            [wx / 12 + wy / 4, -wx / 12 + wy / 4],
            [-wx / 12 + wy / 4, wx / 12 + wy / 4],
        ]
    )
    C = sp.simplify(r * A.inv() - sp.eye(2) / b)
    determinant = sp.factor(C.det())
    expected = (2 * b * r - wy) * (6 * b * r - wx) / (b**2 * wx * wy)
    assert determinant == expected
    roots = (
        (wy / (2 * b), sp.Matrix([1, 1])),
        (wx / (6 * b), sp.Matrix([1, -1])),
    )
    for root, vector in roots:
        at_root = C.subs(r, root).applyfunc(sp.factor)
        assert at_root.rank() == 1
        assert at_root * vector == sp.zeros(2, 1)
    stored = payload["candidate18_rank_one"]["aligned_section"]
    assert sp.factor(sp.sympify(stored["det_C"], locals={"w_x": wx, "w_y": wy, "b": b, "r": r}) - expected) == 0
    assert [row["full_conormal_nullity"] for row in stored["divisor_branches"]] == [4, 4]


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
    verify_conormal_identity()
    verify_third_transvectant(payload)
    verify_rank_one(payload)
    flags = payload["classification"]
    assert all(flags[name] for name in (
        "candidate17_smooth_divisor_classified",
        "candidate18_smooth_divisor_classified",
        "candidate20_smooth_divisor_classified",
        "presymplectic_linear_quotient_on_every_smooth_stratum_classified",
    ))
    assert not flags["global_quotient_topology_classified"]
    assert not flags["singular_locus_quotient_classified"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_PRESYMPLECTIC_DIVISORS verifier: PASS")


if __name__ == "__main__":
    verify()
