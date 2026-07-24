#!/usr/bin/env python3
"""Independent exact verifier for the universal Hessian/intertwiner certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
CERT = HERE / "certificate.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path = CERT) -> None:
    c = json.loads(path.read_text())
    assert c["schema"] == "axial-universal-hessian-intertwiner-v1"
    assert c["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]

    # Re-derive the four-dimensional invariant identity coefficient by coefficient.
    # C^2 = Riem^2 - 2 Ric^2 + R^2/3 and
    # E4  = Riem^2 - 4 Ric^2 + R^2.
    riem, ric, scalar = sp.symbols("riem ric scalar")
    c2 = riem - 2 * ric + sp.Rational(1, 3) * scalar
    e4_form = riem - 4 * ric + scalar
    assert sp.expand(c2 - (e4_form + 2 * ric - sp.Rational(2, 3) * scalar)) == 0
    assert c["weyl_action_hessian"]["identity"] == "C2=E4+2*Ric2-(2/3)*R2"
    assert "-(1/3)*psi1*psi2" in c["weyl_action_hessian"]["mixed_bulk_hessian_mod_euler"]

    # Recheck the two-dimensional linear-algebra obstruction exactly.
    ar, ai, b = sp.symbols("ar ai b", real=True)
    gram = sp.Matrix([[0, ar + sp.I * ai], [ar - sp.I * ai, b]])
    assert sp.factor(gram.det()) == -(ar**2 + ai**2)
    assert c["positivity_obstruction"]["determinant"] == "-Abs(a)**2"

    # Re-derive the rational intertwiner obstruction without importing producer code.
    r, w = sp.symbols("r w", nonzero=True)
    a = sp.Function("a")(r)
    f = (r - 2) / r
    deriv = lambda z: sp.factor(f * sp.diff(z, r))
    potentials = [
        6 * (r - 2) * (r - 1) / r**4,
        6 * (r - 2) / r**3,
    ]

    residuals = []
    for source, target in (potentials, potentials[::-1]):
        q = source - w**2
        delta = source - target
        b_expr = sp.factor(
            (
                deriv(deriv(deriv(a)))
                + deriv(a) * delta
                + a * deriv(delta)
                - 4 * deriv(a) * q
                - 2 * a * deriv(q)
            )
            / (2 * delta)
        )
        residuals.append(
            sp.factor(deriv(b_expr) + (deriv(deriv(a)) + a * delta) / 2)
        )

    H = sp.expand(
        r**4 * (r - 2) ** 2 * sp.diff(a, r, 4)
        + r**3 * (r - 2) * (3 * r + 4) * sp.diff(a, r, 3)
        + r**2 * (4 * w**2 * r**4 - 24 * r**2 + 62 * r - 12) * sp.diff(a, r, 2)
        + r * (12 * w**2 * r**4 - 90 * r + 60) * sp.diff(a, r)
        + (90 * r - 60) * a
    )
    assert sp.simplify(residuals[0] + (r - 2) * H / (12 * r**4)) == 0
    assert sp.simplify(residuals[1] - (r - 2) * H / (12 * r**4)) == 0

    rho = sp.symbols("rho")
    p0 = 4 * (rho + 1) * (rho - 1) * (rho - 3) * (rho - 5)
    p2 = rho * (rho - 1) * (rho**2 + 16 * w**2)
    stated_p0 = sp.sympify(
        c["axial_factor_intertwiner"]["indicial_factors"]["r=0"],
        locals={"rho": rho},
    )
    stated_p2 = sp.sympify(
        c["axial_factor_intertwiner"]["indicial_factors"]["r=2"],
        locals={"rho": rho, "omega": w},
    )
    assert sp.simplify(stated_p0 - p0) == 0
    assert sp.simplify(stated_p2 - p2) == 0

    A0, B0 = sp.symbols("A0 B0")
    trial = A0 + B0 / r
    trial_residual = sp.factor(H.xreplace({a: trial}).doit())
    expected = 90 * A0 * r - 60 * A0 - 4 * B0 * w**2 * r**3 - 42 * B0 * r + 220 * B0
    assert sp.expand(trial_residual - expected) == 0
    stated_residual = sp.sympify(
        c["axial_factor_intertwiner"]["ansatz_residual"],
        locals={"A0": A0, "B0": B0, "r": r, "omega": w},
    )
    assert sp.expand(stated_residual - expected) == 0
    assert c["axial_factor_intertwiner"]["hom_M2_to_M1"] == 0
    assert c["axial_factor_intertwiner"]["hom_M1_to_M2"] == 0

    imported = c["imports"]["projective_nonsplitting"]
    imported_path = HERE.parent.parent.parent / imported["path"]
    assert _sha256(imported_path) == imported["sha256"]
    imported_data = json.loads(imported_path.read_text())
    assert imported_data["claim_flags"]["generic_rational_cocycle_nontrivial"] is True
    assert c["claim_flags"]["no_generic_rational_branch_resolving_C"] is True

    forbidden_promotions = [
        "literal_boundary_current_equals_bulk_hessian_without_euler_audit",
        "nonlocal_intertwiner_excluded",
        "quantum_positive_metric_excluded",
    ]
    for flag in forbidden_promotions:
        assert c["claim_flags"][flag] is False


def main() -> None:
    verify()
    print("PASS: independent universal Hessian/intertwiner verification")


if __name__ == "__main__":
    main()
