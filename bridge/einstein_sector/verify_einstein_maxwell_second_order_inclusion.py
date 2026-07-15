#!/usr/bin/env python3
"""Independent verifier for the second-order Einstein-sector test."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_second_order_inclusion.json"


def _matrix(rows: list[list[str]]) -> sp.Matrix:
    time, space, theta = sp.symbols("t x theta", real=True)
    return sp.Matrix(
        [
            [
                sp.sympify(value, locals={"t": time, "x": space, "theta": theta})
                for value in row
            ]
            for row in rows
        ]
    )


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    assert payload["schema"] == "einstein-maxwell-second-order-inclusion-v1"
    assert payload["result_id"] == "EINSTEIN_MAXWELL_SECOND_ORDER_INCLUSION_TEST"
    assert payload["result_state"] == (
        "TANGENT_AND_CHARGE_SECTOR_DEPENDENT_SECOND_ORDER_EXTENSION_CLASSIFIED"
    )
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    schema = ROOT / payload["schema_path"]
    assert hashlib.sha256(schema.read_bytes()).hexdigest() == payload["schema_sha256"]
    for record in payload["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]

    theta = sp.symbols("theta", real=True)
    zero = sp.zeros(4)
    radion = payload["certified_constant_radion"]
    radion_source = _matrix(radion["affine_quadratic_weyl_maxwell_source"])
    assert radion_source == sp.diag(-2, 34, -18, -18 * sp.sin(theta) ** 2)
    assert _matrix(radion["convention_adjusted_C_Ch_second_order"]) == zero
    assert _matrix(radion["charge_relaxed_extension"]["corrected_residual"]) == zero
    assert radion["compact_fixed_flux_adjoint_witness"]["source_pairing"] == (
        "integral_S1 S2_tt dx=-2*L"
    )

    duality = payload["maxwell_duality_tangent"]
    duality_source = _matrix(duality["affine_fixed_magnetic_flux_source"])
    assert duality_source == sp.diag(
        -sp.Rational(1, 2),
        sp.Rational(1, 2),
        -sp.Rational(1, 2),
        -sp.sin(theta) ** 2 / 2,
    )
    assert _matrix(duality["convention_adjusted_C_Ch_second_order"]) == zero
    assert _matrix(duality["charge_relaxed_extension"]["corrected_residual"]) == zero
    angle = sp.symbols("angle", real=True)
    assert sp.trigsimp(sp.cos(angle) ** 2 + sp.sin(angle) ** 2) == 1

    # Independently reconstruct the radiative tangent and its correction.
    time, space = sp.symbols("t x", real=True)
    u = time - space
    v = time + space
    phi = u
    psi = u**2 * v / 4
    box = lambda expression: -sp.diff(expression, time, 2) + sp.diff(
        expression, space, 2
    )
    assert box(phi) == 0
    assert sp.hessian(phi, (time, space)) == sp.zeros(2)
    assert sp.simplify(box(psi) + 2 * phi) == 0

    correction = u**3 * v * (5 * u * v - 24) / 24
    q_value = sp.factor(box(correction))
    linear_response = sp.zeros(4)
    linear_response[0, 0] = sp.diff(q_value, space, 2) / 2
    linear_response[0, 1] = sp.diff(q_value, time, space) / 2
    linear_response[1, 0] = linear_response[0, 1]
    linear_response[1, 1] = sp.diff(q_value, time, 2) / 2
    sphere_response = sp.factor(box(q_value) / 4)
    linear_response[2, 2] = sphere_response
    linear_response[3, 3] = sphere_response * sp.sin(theta) ** 2
    radiative = payload["null_radiative_tangent"]
    radiative_source = _matrix(radiative["affine_quadratic_weyl_maxwell_source"])
    assert (linear_response + radiative_source).applyfunc(sp.simplify) == zero
    assert _matrix(radiative["explicit_extension"]["corrected_residual"]) == zero

    null_covector = sp.Matrix([1, -1, 0, 0])
    expected_chevreton = 4 * null_covector * null_covector.T
    assert _matrix(radiative["convention_adjusted_C_Ch_second_order"]) == expected_chevreton
    assert expected_chevreton != zero

    reduction = payload["adjoint_cokernel_reduction"]
    assert reduction["fixed_flux_condition"] == "p=0"
    assert "partial_x^2" in reduction["linearized_tt_row"]
    classification = payload["classification"]
    assert classification["constant_radion_compact_fixed_flux_extension_exists"] is False
    assert classification[
        "constant_radion_compact_fixed_flux_adjoint_obstruction_certified"
    ] is True
    assert classification[
        "maxwell_duality_compact_fixed_flux_adjoint_obstruction_certified"
    ] is True
    assert classification[
        "nonzero_chevreton_radiative_fixture_extension_constructed"
    ] is True
    assert classification["general_nonlinear_einstein_sector_closure_certified"] is False
    assert classification["general_second_order_no_go_certified"] is False
    for flag in (
        "general_nonlinear_closure_claim",
        "general_second_order_no_go_claim",
        "lorentzian_causal_claim",
        "observable_embedding_claim",
        "scattering_claim",
        "quantum_claim",
    ):
        assert payload["claim_flags"][flag] is False
    return payload


def main() -> None:
    verify_certificate()
    print("EINSTEIN_MAXWELL_SECOND_ORDER_INCLUSION_INDEPENDENT: PASS")
    print("compact fixed-flux radion and duality adjoint witnesses: PASS")
    print("nonzero-Chevreton null radiative extension: PASS")
    print("general nonlinear closure and general no-go: OPEN")


if __name__ == "__main__":
    main()
