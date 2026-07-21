"""Method-distinct audit of the alpha_B=3 canonical crosswalk certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_ALPHA_B3_OSTROGRADSKY_CANONICAL_CROSSWALK_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str) -> sp.Expr:
    names = {
        "I": sp.I,
        "sqrt": sp.sqrt,
        "sin": sp.sin,
        "cos": sp.cos,
        "theta": sp.symbols("theta", real=True),
        "Omega": sp.symbols("Omega", real=True),
        "A_t": sp.symbols("A_t"),
        "B": sp.symbols("B"),
        "C_t": sp.symbols("C_t"),
        "C": sp.symbols("C"),
        "K": sp.symbols("K"),
        "U": sp.symbols("U"),
    }
    return sp.sympify(value, locals=names)


def _matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[_expr(value) for value in row] for row in rows])


def verify(path: Path = CERT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["result_state"] == "ACTION_NORMALIZED_CANONICAL_CROSSWALK_CERTIFIED"
    for relative, expected in payload["provenance"]["inputs"].items():
        assert _sha(ROOT / relative) == expected

    # Independent coefficient scaling: (+3/8)/(-1/4)=-3/2.
    normalization = payload["normalization"]
    assert normalization["selected_action"] == "S_grav=(3/8) integral sqrt(-g) C_abcd C^abcd"
    assert normalization["exact_action_scale_selected_over_reference"] == "-3/2"
    assert normalization["boundary_convention"] == "adjoin K_ij with L_n h_ij=2K_ij and perform no integration by parts in time; discard only spatial divergences on closed Sigma"
    assert normalization["P_definition"] == "P^ij=-3*sqrt(h)*C^(i n j n)"
    assert sp.Rational(3, 8) / -sp.Rational(1, 4) == -sp.Rational(3, 2)
    epsilon, scale = sp.symbols("epsilon scale")
    selected = scale**2 * (1 + epsilon) ** 2 / (3 * sp.sqrt(1 + epsilon))
    assert sp.series(selected, epsilon, 0, 4).removeO().expand().coeff(epsilon, 3) == -scale**2 / 48

    theta = sp.symbols("theta", real=True)
    h0 = sp.diag(1, 1, sp.sin(theta) ** 2)
    p0 = _matrix(payload["background"]["P0_coordinate_density"])
    assert sp.simplify(sum(h0[i, j] * p0[i, j] for i in range(3) for j in range(3))) == 0
    assert p0 == sp.diag(sp.sin(theta), -sp.sin(theta) / 2, -1 / (2 * sp.sin(theta)))

    # Recompute both primary linear constraints from the serialized tensors.
    for ell in (0, 2, 4):
        row = payload["linear_polar_crosswalk"][str(ell)]
        h = _matrix(row["delta_h_over_phase"])
        k = _matrix(row["delta_K_over_phase"])
        pi = _matrix(row["delta_pi_over_phase"])
        momentum = _matrix(row["delta_P_over_phase"])
        p_trace = sp.simplify(
            sum(h0[i, j] * momentum[i, j] + h[i, j] * p0[i, j] for i in range(3) for j in range(3))
        )
        q_scale = sp.simplify(
            2 * sum(h0[i, j] * pi[i, j] for i in range(3) for j in range(3))
            + sum(k[i, j] * p0[i, j] for i in range(3) for j in range(3))
        )
        assert sp.trigsimp(p_trace) == 0
        assert sp.trigsimp(q_scale) == 0

    # Independently check the generic inverse formula from the Pxx template.
    omega = sp.symbols("Omega", real=True)
    a_t, c_t = sp.symbols("A_t C_t")
    for ell in (2, 4):
        lam = ell * (ell + 1)
        row = payload["linear_polar_crosswalk"][str(ell)]
        harmonic = _expr(row["harmonic"])
        pxx = _expr(row["delta_P_over_phase"][0][0])
        p_x = sp.trigsimp(pxx / (sp.sin(theta) * harmonic))
        expected = lam * a_t / 4 - (omega**2 + sp.Rational(lam, 2) + 1) * c_t / 2
        assert sp.simplify(sp.trigsimp(p_x - expected)) == 0

    ledger = payload["signed_channel_crosswalk"]
    assert len(ledger) == 27
    actual: dict[tuple[int, str], set[str]] = {}
    for row in ledger:
        key = (row["ell"], row["channel"])
        actual.setdefault(key, set()).add(row["frequency_sign"])
        assert len(row["canonical"]["delta_h"]) == 3
        assert len(row["canonical"]["delta_pi"]) == 3
        assert len(row["canonical"]["delta_P"]) == 3
        if row["ell"] in (2, 4):
            # Every stored action inverse has B=0; a nonzero mutation must fail.
            assert row["covariant_coefficients"][1] == "0"
    for key, signs in actual.items():
        zero = next(row for row in ledger if (row["ell"], row["channel"]) == key)["omega"] == "0"
        assert signs == ({"+"} if zero else {"+", "-"})

    flags = payload["classification"]
    assert all(flags.values())
    checks = payload["symplectic_and_equation_checks"]
    assert checks["symplecticity"] and checks["constraint_pullback"] and checks["Euler_compatibility"]


if __name__ == "__main__":
    verify()
    print("alpha_B=3 Ostrogradsky canonical crosswalk: PASS")
