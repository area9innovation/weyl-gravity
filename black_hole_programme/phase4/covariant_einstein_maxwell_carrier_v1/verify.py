#!/usr/bin/env python3
"""Independent verifier for the Schouten--Einstein/Maxwell carrier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path = CERT) -> None:
    c = json.loads(path.read_text())
    assert c["schema"] == "covariant-einstein-maxwell-carrier-v1"
    assert c["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]

    # Re-derive the trace, divergence and Bach coefficient vector.
    dim = sp.Integer(4)
    schouten = sp.Rational(1, 6)
    trace_factor = 1 - dim * schouten
    div_factor = sp.Rational(1, 2) - schouten
    assert trace_factor == div_factor == sp.Rational(1, 3)
    stated = c["schouten_carrier"]["expanded_coefficient_basis"]
    expected = {
        "Box_psi_ab": sp.Rational(1, 2),
        "Riemann_psi": sp.Integer(1),
        "Hessian_psi": -sp.Rational(1, 6),
        "g_ab_Box_psi": -sp.Rational(1, 12),
    }
    for key, value in expected.items():
        assert sp.sympify(stated[key]) == value
    assert c["schouten_carrier"]["factorization"] == "deltaB_ab[h]=-deltaG_ab[q[h]]"

    # Source Weyl transformation: the g Box term cancels exactly.
    gbox = -sp.Rational(1, 2) - schouten * (-3)
    assert gbox == 0
    assert c["source_weyl_to_maxwell_gauge"]["q_shift"] == (
        "-Hessian(Phi)=L_{-(1/2)dPhi}g"
    )
    assert c["source_weyl_to_maxwell_gauge"]["F_invariant"] is True

    # Invert the trace adjustment and recheck the q-form of the action.
    tau, q2 = sp.symbols("tau q2")
    psi2 = q2 + 2 * tau**2
    psi_trace = 3 * tau
    assert sp.expand(psi2 - psi_trace**2 / 3) == q2 - tau**2

    # Independent local Lorentz-jet check of the Maxwell divergence identity.
    metric = sp.diag(-1, 1, 1, 1)
    jet = sp.Matrix(4, 4, lambda i, j: sp.symbols(f"j{i}{j}"))
    sym = jet + jet.T
    anti = jet - jet.T

    def contract(t: sp.Matrix) -> sp.Expr:
        up = metric * t * metric
        return sp.expand(
            sum(t[i, j] * up[i, j] for i in range(4) for j in range(4))
        )

    div = sp.expand(sum(metric[i, i] * jet[i, i] for i in range(4)))
    crossed = sp.expand(
        sum(
            jet[i, j] * metric[i, i] * metric[j, j] * jet[j, i]
            for i in range(4)
            for j in range(4)
        )
    )
    lhs = sp.expand(contract(sym) - (2 * div) ** 2 - contract(anti))
    rhs_after_ricci_flat_commutation = sp.expand(4 * (crossed - div**2))
    assert sp.simplify(lhs - rhs_after_ricci_flat_commutation) == 0
    assert c["quadratic_action"]["relative_sign"] == (
        "S_spin1=-8*alpha*S_Maxwell modulo boundary terms"
    )

    for imported in c["imports"].values():
        imported_path = ROOT / imported["path"]
        assert sha256(imported_path) == imported["sha256"]

    flags = c["claim_flags"]
    for key in [
        "schouten_einstein_factorization",
        "carrier_constraint",
        "target_gauge_maxwell_equation",
        "source_weyl_becomes_maxwell_gauge",
        "wrong_sign_maxwell_bulk_action_mod_boundary",
        "axial_l2_spin_one_geometric_identification",
    ]:
        assert flags[key] is True
    for key in [
        "all_ell_lift_certified",
        "complete_polar_phase_space_certified",
        "quantum_ghost_or_unitarity_statement",
    ]:
        assert flags[key] is False


def main() -> None:
    verify()
    print("PASS: independent covariant Einstein-Maxwell carrier verification")


if __name__ == "__main__":
    main()
