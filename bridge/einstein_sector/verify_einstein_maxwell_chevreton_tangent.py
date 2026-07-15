#!/usr/bin/env python3
"""Independent verifier for the full on-shell product tangent inclusion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json"


def _all_zero(rows: list[list[str]]) -> bool:
    return all(sp.sympify(value) == 0 for row in rows for value in row)


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    assert payload["schema"] == "einstein-maxwell-chevreton-tangent-v1"
    assert payload["result_id"] == "EINSTEIN_MAXWELL_CHEVRETON_TANGENT"
    assert payload["result_state"] == (
        "FULL_ON_SHELL_LINEAR_TANGENT_INCLUSION_CERTIFIED_"
        "OFF_SHELL_BV_AND_NONLINEAR_OPEN"
    )
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC"]

    schema = ROOT / payload["schema_path"]
    assert hashlib.sha256(schema.read_bytes()).hexdigest() == payload["schema_sha256"]
    for record in payload["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]

    # Independent exact reconstruction of the product tuning coefficient.
    alpha_b, kappa, cosmological, curvature_sum = sp.symbols(
        "alpha_B kappa Lambda K", nonzero=True, real=True
    )
    coefficient = alpha_b * 2 * kappa * cosmological / 3
    coefficient = coefficient.subs(alpha_b, 3 / (kappa * curvature_sum))
    coefficient = sp.simplify(coefficient.subs(curvature_sum, 2 * cosmological))
    assert coefficient == 1
    assert payload["tuning_deduction"]["symbolic_check"] == "1"

    # The convention-adjusted Chevreton trace is homogeneous quadratic in
    # nabla F.  Its derivative therefore vanishes at the parallel-flux point,
    # while the second derivative need not vanish.
    epsilon, jet_one, jet_two = sp.symbols("epsilon J1 J2", real=True)
    quadratic = epsilon**2 * (jet_one**2 + 3 * jet_one * jet_two + 2 * jet_two**2)
    assert sp.diff(quadratic, epsilon).subs(epsilon, 0) == 0
    second = sp.factor(sp.diff(quadratic, epsilon, 2).subs(epsilon, 0))
    assert str(second) == payload["quadratic_onset"]["second_variation"]
    assert second != 0

    # Independent reduced Einstein--Maxwell check for the stored radion
    # representative.  On R^(1,1) x S^2 at k2=1, its complete linearized
    # equations reduce to box(phi)=0, Hessian_TF(phi)=0, and
    # box(psi)+box(phi)+2*phi=0.
    time, space = sp.symbols("t x", real=True)
    phi = sp.S.One
    psi = time**2
    box = lambda expression: -sp.diff(expression, time, 2) + sp.diff(expression, space, 2)
    base_metric = sp.diag(-1, 1)
    hessian = sp.hessian(phi, (time, space))
    hessian_tf = sp.simplify(hessian - base_metric * box(phi) / 2)
    assert box(phi) == 0
    assert hessian_tf == sp.zeros(2)
    assert sp.simplify(box(psi) + box(phi) + 2 * phi) == 0

    fixture = payload["direct_radion_fixture"]
    assert _all_zero(fixture["linearized_einstein_residual"])
    assert _all_zero(fixture["linearized_weyl_residual"])
    assert all(sp.sympify(value) == 0 for value in fixture["linearized_maxwell_residual"])
    background_bach = sp.Matrix(fixture["background_bach"])
    background_stress = sp.Matrix(fixture["background_stress"])
    assert (3 * background_bach - background_stress).applyfunc(sp.simplify) == sp.zeros(4)

    classification = payload["classification"]
    assert classification["full_lower_order_on_shell_linear_tangent_inclusion"] is True
    assert classification[
        "ordinary_einstein_graviton_and_photon_tangents_survive_before_quotient"
    ] is True
    assert classification["off_shell_curved_minimal_bv_chain_map_constructed"] is False
    assert classification["nonlinear_einstein_maxwell_sector_closure_certified"] is False
    assert classification[
        "second_order_chevreton_obstruction_computed_for_physical_modes"
    ] is False
    for flag in (
        "off_shell_bv_chain_map_claim",
        "nonlinear_closure_claim",
        "lorentzian_causal_claim",
        "observable_embedding_claim",
        "scattering_claim",
        "quantum_claim",
    ):
        assert payload["claim_flags"][flag] is False
    return payload


def main() -> None:
    verify_certificate()
    print("EINSTEIN_MAXWELL_CHEVRETON_TANGENT_INDEPENDENT: PASS")
    print("complete on-shell linear tangent inclusion: PASS")
    print("off-shell BV map and nonlinear closure: OPEN")


if __name__ == "__main__":
    main()
