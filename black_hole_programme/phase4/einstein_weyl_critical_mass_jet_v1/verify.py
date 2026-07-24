#!/usr/bin/env python3
"""Independent verifier for the critical Einstein--Weyl mass jet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_document(data: dict) -> None:
    assert data["schema"] == "einstein-weyl-critical-mass-jet-v1"
    assert data["status"] == "EXACT_CRITICAL_MASS_PARENT_JET_RADIAL_CROSSWALK_OPEN"
    assert set(data["dependency_tags"]) == {"LOCAL-ALGEBRAIC", "REDUCED-MODE"}

    # Independent exact variation with concrete nonsingular symmetric matrices.
    m = sp.symbols("m")
    h1, h2, p1, p2 = sp.symbols("h1 h2 p1 p2")
    h = sp.Matrix([h1, h2])
    p = sp.Matrix([p1, p2])
    E = sp.Matrix([[3, -1], [-1, 2]])
    A = sp.Matrix([[2, 1], [1, -1]])
    S = (p.T * E * h)[0] - (p.T * A * p)[0] / 2 + m * (h.T * E * h)[0] / 2
    assert sp.simplify(
        sp.Matrix([sp.diff(S, p1), sp.diff(S, p2)]) - (E * h - A * p)
    ) == sp.zeros(2, 1)
    assert sp.simplify(
        sp.Matrix([sp.diff(S, h1), sp.diff(S, h2)]) - (E * p + m * E * h)
    ) == sp.zeros(2, 1)

    # Independent difference quotient and singular-C checks.
    assert sp.simplify(
        (E * (E + m * sp.eye(2))).inv()
        - (E.inv() - (E + m * sp.eye(2)).inv()) / m
    ) == sp.zeros(2)
    C = sp.Matrix([[1, -2 / m], [0, -1]])
    assert C**2 == sp.eye(2)
    N = -m * (C + sp.eye(2)) / 2
    assert N.applyfunc(lambda x: sp.limit(x, m, 0)) == sp.Matrix([[0, 1], [0, 0]])

    # Independently expand the massive momentum and Coulomb exponent.
    w, M = sp.symbols("w M", nonzero=True)
    z = sp.symbols("z")
    k_series = w * sp.sqrt(1 - z)
    assert sp.series(k_series, z, 0, 3) == w - w * z / 2 - w * z**2 / 8 + sp.Order(z**3)
    x_series = M * w * (z - 2) / (sp.I * sp.sqrt(1 - z))
    assert sp.expand(sp.series(x_series, z, 0, 3).removeO()).coeff(z, 1) == 0

    flags = data["claim_flags"]
    for key in [
        "parent_mass_variation_exact",
        "mass_derivative_modulo_einstein_kernel_exact",
        "tt_difference_quotient_exact",
        "finite_mass_branch_sign_singular_limit_exact",
        "nilpotent_residue_exact",
        "massive_momentum_derivative_exact",
        "coulomb_exponent_first_mass_derivative_zero",
        "intrinsic_horizon_dot_lambda_zero_imported",
    ]:
        assert flags[key], key
    for key in [
        "physical_mass_jet_equals_intrinsic_radial_tau",
        "physical_b_equals_minus_mass_derivative_of_jost",
        "physical_massive_qnm_slope_certified",
        "threshold_inverse_shear_asymptotic_certified",
        "maxwell_stueckelberg_limit_certified",
        "fredholm_double_pole_established",
        "quantum_statement",
    ]:
        assert not flags[key], key

    assert data["crosswalk_gate"]["status"] == "OPEN_NOT_ASSUMED"
    assert "C(r)/K_U C(r)" in data["crosswalk_gate"]["decisive_test"]
    assert data["endpoint_phase"]["coulomb_values"]["partial_mass_x_at_zero"] == "0"

    for item in data["imports"].values():
        path = ROOT / item["path"]
        assert path.exists()
        assert digest(path) == item["sha256"]

    horizon = json.loads(
        (ROOT / data["imports"]["intrinsic_horizon_moving_phase"]["path"]).read_text()
    )
    assert horizon["claim_flags"]["dot_lambda_H_exactly_zero"]
    radial = json.loads(
        (ROOT / data["imports"]["intrinsic_radial_partial_jet"]["path"]).read_text()
    )
    assert radial["claim_flags"]["partial_spin_two_row_jet_exact"]
    assert not radial["conditional_endpoint_derivative"]["hypothesis_verified_here"]


def main() -> None:
    data = json.loads((HERE / "certificate.json").read_text())
    verify_document(data)
    print("EXACT_CRITICAL_MASS_PARENT_JET_VERIFIED_RADIAL_CROSSWALK_OPEN")


if __name__ == "__main__":
    main()
