#!/usr/bin/env python3
"""Independent exact verifier for the product-background incidence theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"


def _matrix(rows: list[list[str]], symbols: dict[str, sp.Symbol]) -> sp.Matrix:
    return sp.Matrix(
        [[sp.sympify(value, locals=symbols) for value in row] for row in rows]
    )


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    assert payload["result_id"] == "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE"
    assert payload["lifecycle_state"] == "CLASSIFIED"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC"]

    schema_path = ROOT / payload["schema_path"]
    assert hashlib.sha256(schema_path.read_bytes()).hexdigest() == payload["schema_sha256"]
    generator_path = ROOT / payload["provenance"]["generator_path"]
    assert (
        hashlib.sha256(generator_path.read_bytes()).hexdigest()
        == payload["provenance"]["generator_sha256"]
    )

    k_1, k_2 = sp.symbols("k_1 k_2", real=True)
    electric, magnetic = sp.symbols("E P", real=True)
    alpha_b, kappa = sp.symbols("alpha_B kappa", positive=True, real=True)
    symbols = {
        "k_1": k_1,
        "k_2": k_2,
        "E": electric,
        "P": magnetic,
        "alpha_B": alpha_b,
        "kappa": kappa,
    }
    tensors = payload["exact_tensors"]
    metric = _matrix(tensors["metric_orthonormal"], symbols)
    ricci = _matrix(tensors["ricci_orthonormal"], symbols)
    bach = _matrix(tensors["bach_orthonormal"], symbols)
    stress = _matrix(tensors["maxwell_stress_orthonormal"], symbols)
    einstein = _matrix(tensors["einstein_tensor_orthonormal"], symbols)
    scalar = sp.sympify(tensors["scalar_curvature"], locals=symbols)

    # Reconstruct the locally symmetric product curvature independently from
    # the certificate's stored Ricci and Bach blocks.
    blocks = (0, 0, 1, 1)
    curvatures = (k_1, k_2)
    riemann = {}
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    value = sp.S.Zero
                    if blocks[a] == blocks[b] == blocks[c] == blocks[d]:
                        value = curvatures[blocks[a]] * (
                            metric[a, c] * metric[b, d]
                            - metric[a, d] * metric[b, c]
                        )
                    riemann[a, b, c, d] = value
    derived_ricci = sp.Matrix(
        4,
        4,
        lambda b, d: sp.simplify(
            sum(
                metric[a, c] * riemann[a, b, c, d]
                for a in range(4)
                for c in range(4)
            )
        ),
    )
    derived_scalar = sp.factor(sp.trace(metric * derived_ricci))
    schouten = sp.simplify((derived_ricci - derived_scalar * metric / 6) / 2)
    schouten_up = sp.simplify(metric * schouten * metric)

    def weyl(a: int, b: int, c: int, d: int) -> sp.Expr:
        return sp.simplify(
            riemann[a, b, c, d]
            - (
                metric[a, c] * schouten[d, b]
                - metric[a, d] * schouten[c, b]
                - metric[b, c] * schouten[d, a]
                + metric[b, d] * schouten[c, a]
            )
        )

    derived_bach = sp.Matrix(
        4,
        4,
        lambda a, c: sp.factor(
            sum(
                schouten_up[b, d] * weyl(a, b, c, d)
                for b in range(4)
                for d in range(4)
            )
        ),
    )

    assert metric == sp.diag(-1, 1, 1, 1)
    assert derived_ricci == ricci
    assert sp.simplify(derived_bach - bach) == sp.zeros(4)
    assert ricci == sp.diag(-k_1, k_1, k_2, k_2)
    assert sp.simplify(sp.trace(metric * ricci) - scalar) == 0
    assert sp.simplify(scalar - 2 * (k_1 + k_2)) == 0
    assert sp.simplify(einstein - (ricci - scalar * metric / 2)) == sp.zeros(4)
    assert sp.simplify(sp.trace(metric * bach)) == 0
    assert sp.simplify(sp.trace(metric * stress)) == 0

    amplitude = (k_1 - k_2) * (k_1 + k_2) / 6
    assert sp.simplify(
        bach - sp.diag(-amplitude, amplitude, -amplitude, -amplitude)
    ) == sp.zeros(4)
    rho = (electric**2 + magnetic**2) / 2
    assert sp.simplify(stress - sp.diag(rho, -rho, rho, rho)) == sp.zeros(4)

    cosmological = (k_1 + k_2) / 2
    magnetic_squared = (k_2 - k_1) / kappa - electric**2
    tuned_alpha = 3 / (kappa * (k_1 + k_2))
    einstein_residual = einstein + cosmological * metric - kappa * stress
    weyl_residual = tuned_alpha * bach - stress
    assert einstein_residual.applyfunc(
        lambda value: sp.factor(value.subs(magnetic**2, magnetic_squared))
    ) == sp.zeros(4)
    assert weyl_residual.applyfunc(
        lambda value: sp.factor(value.subs(magnetic**2, magnetic_squared))
    ) == sp.zeros(4)

    flat = payload["flat_critical_branch"]
    assert flat["curvatures"]["k_2"] == "3/(alpha_B*kappa)"
    assert flat["energy_density"] == "3/(2*alpha_B*kappa**2)"
    assert flat["pure_magnetic_field_squared"] == "3/(alpha_B*kappa**2)"
    assert flat["compact_cauchy_topology"] == "S^1 x S^2"
    assert flat["relational_matter_clock"] is False
    assert flat["asymptotically_flat"] is False

    # Independently redo the optional U(1) quantization elimination.
    charge, integer = sp.symbols("q_min N", positive=True, real=True)
    flat_k_2 = 3 / (alpha_b * kappa)
    quantized_magnetic = integer * flat_k_2 / (2 * charge)
    quantization_residual = sp.factor(
        quantized_magnetic**2 - flat_k_2 / kappa
    )
    solved_alpha = sp.solve(quantization_residual, alpha_b)
    assert solved_alpha == [3 * integer**2 / (4 * charge**2)]
    assert (
        payload["u1_flux_quantization"]["flat_branch_discrete_coupling"]
        == "alpha_B=3*N**2/(4*q_min**2)"
    )

    fixture = payload["rational_fixture"]
    fixture_symbols = {
        k_1: 0,
        k_2: 1,
        alpha_b: 3,
        kappa: 1,
        electric: 0,
        magnetic: 1,
    }
    fixture_locals = symbols | {"Lambda": sp.Symbol("Lambda")}
    assert _matrix(fixture["ricci_orthonormal"], fixture_locals) == ricci.subs(
        fixture_symbols
    )
    assert _matrix(fixture["bach_orthonormal"], fixture_locals) == bach.subs(
        fixture_symbols
    )
    assert _matrix(
        fixture["maxwell_stress_orthonormal"], fixture_locals
    ) == stress.subs(fixture_symbols)
    assert _matrix(fixture["einstein_residual"], fixture_locals) == sp.zeros(4)
    assert _matrix(fixture["weyl_residual"], fixture_locals) == sp.zeros(4)

    classification = payload["classification"]
    assert (
        classification[
            "exact_common_einstein_maxwell_weyl_maxwell_background_exists"
        ]
        is True
    )
    assert classification["linearized_tangent_complex_map_constructed"] is False
    assert classification["theories_proved_equivalent"] is False
    assert payload["claim_flags"]["lorentzian_green_complex_certified"] is False
    assert payload["claim_flags"]["quantum_claim"] is False
    return payload


def main() -> None:
    verify_certificate()
    print("EINSTEIN_MAXWELL_PRODUCT_INCIDENCE_INDEPENDENT: PASS")
    print("curvature, Bach, Maxwell stress, both metric equations, and flux relation: PASS")
    print("tangent BV comparison: OPEN")


if __name__ == "__main__":
    main()
