"""Independent verifier for complete deformable-kernel contraction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = (
    ROOT
    / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(
        ROOT / payload["provenance"]["generator_path"]
    )
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])

    # Rebuild the normalized magnetic generators and time reversal without
    # importing the producer.
    W = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    ms = list(range(-2, 3))
    idx = {m: i for i, m in enumerate(ms)}
    jp = sp.zeros(5)
    jm = sp.zeros(5)
    for m in ms:
        if m < 2:
            jp[idx[m + 1], idx[m]] = 2 - m
        if m > -2:
            jm[idx[m - 1], idx[m]] = 2 + m
    generators = ((jp + jm) / 4, (jp - jm) / (4 * sp.I), sp.diag(*ms) / 2)
    R = sp.zeros(5)
    for i, sign in enumerate((1, -1, 1, -1, 1)):
        R[i, 4 - i] = sign
    assert R.T * W * R == W
    assert R**2 == sp.eye(5)
    for J in generators:
        assert sp.simplify(J.conjugate().T * W - W * J) == sp.zeros(5)
        assert sp.simplify(R * J.conjugate() * R + J) == sp.zeros(5)
        assert sp.simplify((W * J * R).T + W * J * R) == sp.zeros(5)
    bad_R = sp.zeros(5)
    for i in range(5):
        bad_R[i, 4 - i] = 1
    assert sp.simplify(
        bad_R * generators[0].conjugate() * bad_R + generators[0]
    ) != sp.zeros(5)

    theta, sigma = sp.symbols("theta sigma", real=True)
    q = sp.cos(2 * theta) / (1 + sigma * sp.sin(2 * theta))
    expected = -2 * (sigma + sp.sin(2 * theta)) / (
        1 + sigma * sp.sin(2 * theta)
    ) ** 2
    assert sp.trigsimp(sp.diff(q, theta) - expected) == 0
    assert q.subs(theta, 0) == 1
    assert sp.simplify(q.subs(theta, sp.pi / 4)) == 0

    # Rebuild both affine coefficient interpolations and incidence values.
    a, b, delta, t = sp.symbols("a b delta t", nonzero=True, real=True)
    alpha = delta + a - b
    assert sp.expand(
        delta + a - b * t - ((1 - t) * (delta + a) + t * alpha)
    ) == 0
    assert sp.expand(
        b - delta - a * t - ((1 - t) * (b - delta) + t * (-alpha))
    ) == 0
    assert sp.factor(delta + a * (-delta / a)) == 0
    assert sp.factor(delta - b * (delta / b)) == 0
    assert (delta - b).subs({delta: -1, b: 1}) < 0
    assert (delta + a).subs({delta: 1, a: 1}) > 0

    flags = payload["classification"]
    assert flags["normalized_spin_two_moment_unit_ball_bound_certified"]
    assert flags["time_reversal_zero_moment_homotopy_certified"]
    assert flags["time_reversal_moment_norm_monotone"]
    assert flags["delta_negative_convex_positive_node_deletion_certified"]
    assert flags["delta_positive_convex_negative_node_deletion_certified"]
    assert flags["every_admissible_component_meets_incidence"]
    assert flags["strict_opposite_sign_complete_deformable_kernel_contraction"]
    assert flags["candidate17_complete_singular_rotation_zero_fibre_connected"]
    assert flags["candidate20_balance_complete_singular_rotation_zero_fibre_connected"]
    assert flags["candidate20_off_balance_complete_singular_rotation_zero_fibre_connected"]
    assert flags["candidate20_complete_singular_rotation_zero_fibre_connected"]
    assert flags["all_positive_fixed_active_occupations_covered"]
    assert not flags["candidate17_candidate20_identified"]
    assert not flags["occupation_strata_glued"]
    assert not flags["final_residual_descent"]
    assert not flags["all_orders_integration"]
    assert "does not identify the candidates" in payload["claim_boundary"]
    controls = payload["convex_one_node_deletion"]["wrong_node_controls"]
    assert "hits the wall" in controls["delta_negative"]
    assert "hits the wall" in controls["delta_positive"]
    print(
        "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_DEFORMABLE_KERNEL_COMPLETE_CONTRACTION verifier: PASS"
    )


if __name__ == "__main__":
    verify()
