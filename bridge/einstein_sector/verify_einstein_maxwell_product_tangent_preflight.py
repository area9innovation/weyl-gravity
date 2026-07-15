#!/usr/bin/env python3
"""Independent verifier for the product-background principal BV preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_product_tangent_preflight.json"
PAIRS = tuple((first, second) for first in range(4) for second in range(first, 4))


def _matrix(
    rows: list[list[str]], alpha_b: sp.Symbol, kappa: sp.Symbol
) -> sp.Matrix:
    return sp.Matrix(
        [
            [
                sp.sympify(
                    value, locals={"alpha_B": alpha_b, "kappa": kappa}
                )
                for value in row
            ]
            for row in rows
        ]
    )


def _independent_symbols(
    values: tuple[int, int, int, int], alpha_b: sp.Symbol, kappa: sp.Symbol
) -> dict[str, sp.Matrix | int]:
    eta = sp.diag(-1, 1, 1, 1)
    p = sp.Matrix(values)
    p_up = eta * p
    p_squared = int((p.T * eta * p)[0])

    def components(matrix: sp.Matrix) -> sp.Matrix:
        return sp.Matrix([matrix[first, second] for first, second in PAIRS])

    metric_hessian_columns = []
    q_columns = []
    for first, second in PAIRS:
        basis = sp.zeros(4)
        basis[first, second] = 1
        basis[second, first] = 1
        trace = sp.trace(eta * basis)
        pp = (p_up.T * basis * p_up)[0]
        delta_ricci = sp.Matrix(
            4,
            4,
            lambda mu, nu: (
                p[mu] * (p_up.T * basis[:, nu])[0]
                + p[nu] * (p_up.T * basis[:, mu])[0]
                - p_squared * basis[mu, nu]
                - p[mu] * p[nu] * trace
            )
            / 2,
        )
        delta_scalar = pp - p_squared * trace
        metric_hessian_columns.append(
            components(sp.simplify(delta_ricci - eta * delta_scalar / 2))
        )
        q_columns.append(
            components(
                sp.simplify(
                    p_squared * basis / 2
                    - (eta * p_squared - p * p.T) * trace / 6
                )
            )
        )
    einstein = sp.Matrix.hstack(*metric_hessian_columns)
    q_operator = sp.Matrix.hstack(*q_columns)
    bach = sp.simplify(q_operator * einstein)
    maxwell = sp.simplify(p_squared * eta - p_up * p_up.T)
    hessian_e = sp.diag(einstein / kappa, maxwell)
    hessian_w = sp.diag(alpha_b * bach, maxwell)

    gauge_e = sp.zeros(14, 5)
    for ghost in range(4):
        for row, (mu, nu) in enumerate(PAIRS):
            gauge_e[row, ghost] = (p[mu] if nu == ghost else 0) + (
                p[nu] if mu == ghost else 0
            )
    gauge_e[10:, 4] = p
    gauge_w = sp.zeros(14, 6)
    gauge_w[:, :5] = gauge_e
    for row, (mu, nu) in enumerate(PAIRS):
        gauge_w[row, 5] = 2 * eta[mu, nu]

    noether_e = sp.zeros(5, 14)
    for nu in range(4):
        for row, (mu, rho) in enumerate(PAIRS):
            noether_e[nu, row] = (
                (p_up[mu] if rho == nu else 0)
                + (p_up[rho] if mu == nu and rho != mu else 0)
            )
    noether_e[4, 10:] = p.T
    noether_w = sp.zeros(6, 14)
    noether_w[:5, :] = noether_e
    for row, (mu, nu) in enumerate(PAIRS):
        noether_w[5, row] = eta[mu, nu] if mu == nu else 2 * eta[mu, nu]

    equation_map = sp.diag(alpha_b * kappa * q_operator, sp.eye(4))
    ghost_map = sp.zeros(6, 5)
    ghost_map[:5, :] = sp.eye(5)
    identity_map = sp.zeros(6, 5)
    identity_map[:4, :4] = alpha_b * kappa * p_squared * sp.eye(4) / 2
    identity_map[4, 4] = 1

    assert hessian_e * gauge_e == sp.zeros(14, 5)
    assert noether_e * hessian_e == sp.zeros(5, 14)
    assert hessian_w * gauge_w == sp.zeros(14, 6)
    assert noether_w * hessian_w == sp.zeros(6, 14)
    assert gauge_w * ghost_map == gauge_e
    assert equation_map * hessian_e == hessian_w
    assert identity_map * noether_e == noether_w * equation_map
    return {
        "p_squared": p_squared,
        "gauge_e": gauge_e,
        "hessian_e": hessian_e,
        "noether_e": noether_e,
        "gauge_w": gauge_w,
        "hessian_w": hessian_w,
        "noether_w": noether_w,
        "einstein": einstein,
        "bach": bach,
        "maxwell": maxwell,
    }


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    assert payload["result_id"] == "EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT"
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC"]
    schema = ROOT / payload["schema_path"]
    assert hashlib.sha256(schema.read_bytes()).hexdigest() == payload["schema_sha256"]
    for record in payload["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]

    alpha_b, kappa = sp.symbols("alpha_B kappa", nonzero=True, real=True)
    nonnull = _independent_symbols((1, 2, 3, 5), alpha_b, kappa)
    null = _independent_symbols((1, 0, 0, 1), alpha_b, kappa)
    stored = payload["principal_operators"]["exact_symbol_matrices_at_nonnull_fixture"]
    for key in ("gauge_e", "hessian_e", "noether_e", "gauge_w", "hessian_w", "noether_w"):
        assert _matrix(stored[key], alpha_b, kappa) == nonnull[key]

    nonnull_ranks = payload["symbol_cohomology"]["noncharacteristic_fixture"]["ranks"]
    null_ranks = payload["symbol_cohomology"]["null_fixture"]["ranks"]
    assert nonnull_ranks == {"R_E": 5, "H_E": 9, "N_E": 5, "R_W": 6, "H_W": 8, "N_W": 6}
    assert null_ranks == {"R_E": 5, "H_E": 5, "N_E": 5, "R_W": 6, "H_W": 2, "N_W": 6}
    assert {
        "R_E": nonnull["gauge_e"].rank(),
        "H_E": nonnull["hessian_e"].rank(),
        "N_E": nonnull["noether_e"].rank(),
        "R_W": nonnull["gauge_w"].rank(),
        "H_W": nonnull["hessian_w"].rank(),
        "N_W": nonnull["noether_w"].rank(),
    } == nonnull_ranks
    assert {
        "R_E": null["gauge_e"].rank(),
        "H_E": null["hessian_e"].rank(),
        "N_E": null["noether_e"].rank(),
        "R_W": null["gauge_w"].rank(),
        "H_W": null["hessian_w"].rank(),
        "N_W": null["noether_w"].rank(),
    } == null_ranks

    kernel_e = sp.Matrix.hstack(*null["hessian_e"].nullspace())
    intersection = kernel_e.cols + null["gauge_w"].rank() - sp.Matrix.hstack(kernel_e, null["gauge_w"]).rank()
    assert intersection == null["gauge_e"].rank() == 5
    induced = payload["symbol_cohomology"]["null_fixture"]["induced_field_cohomology_map"]
    assert induced["induced_map_injective"] is True
    assert induced["source_dimension"] == 4
    assert induced["target_dimension"] == 6
    assert induced["cokernel_dimension"] == 2

    classification = payload["classification"]
    assert classification["principal_bv_chain_map_constructed"] is True
    assert classification["full_curved_tangent_chain_map_constructed"] is False
    assert classification["generalized_fourth_order_modes_classified"] is False
    assert payload["claim_flags"]["lorentzian_causal_claim"] is False
    assert payload["claim_flags"]["quantum_claim"] is False
    return payload


def main() -> None:
    verify_certificate()
    print("EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT_INDEPENDENT: PASS")
    print("two principal BV complexes, three chain squares, and null injection: PASS")
    print("curvature/flux lower-order completion: OPEN")


if __name__ == "__main__":
    main()
