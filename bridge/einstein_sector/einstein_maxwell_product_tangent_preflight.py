"""Principal minimal-BV comparison at the common Einstein--Maxwell product.

This is a fail-closed preflight, not the full curved tangent theorem.  It
freezes both minimal field/ghost layouts and constructs the exact principal
symbol chain map from Einstein--Maxwell to pure-Weyl--Maxwell.  Curvature,
background-flux, and connection terms are explicitly left for the next gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
BACKGROUND = ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_product_tangent_preflight.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_product_tangent_preflight.schema.json"
PAIRS = tuple((first, second) for first in range(4) for second in range(first, 4))


class ProductTangentPreflightError(RuntimeError):
    """Raised when a principal complex or import gate fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProductTangentPreflightError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _principal_complex(
    covector: tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr],
    alpha_b: sp.Expr,
    kappa: sp.Expr,
) -> dict[str, sp.Matrix | sp.Expr]:
    """Construct both exact principal BV symbols in a symmetric-tensor basis."""

    eta = sp.diag(-1, 1, 1, 1)
    p = sp.Matrix(covector)
    p_up = eta * p
    p_squared = sp.factor((p.T * eta * p)[0])

    einstein = sp.zeros(10)
    for column, (first, second) in enumerate(PAIRS):
        h = sp.zeros(4)
        h[first, second] = 1
        h[second, first] = 1
        trace_h = sp.trace(eta * h)
        pp_h = (p_up.T * h * p_up)[0]
        delta_g = sp.zeros(4)
        for mu in range(4):
            for nu in range(4):
                delta_ricci = sp.Rational(1, 2) * (
                    p[mu] * sum(p_up[index] * h[nu, index] for index in range(4))
                    + p[nu]
                    * sum(p_up[index] * h[mu, index] for index in range(4))
                    - p_squared * h[mu, nu]
                    - p[mu] * p[nu] * trace_h
                )
                delta_scalar = pp_h - p_squared * trace_h
                delta_g[mu, nu] = sp.simplify(
                    delta_ricci - eta[mu, nu] * delta_scalar / 2
                )
        for row, (mu, nu) in enumerate(PAIRS):
            einstein[row, column] = delta_g[mu, nu]

    bach_from_einstein = sp.zeros(10)
    for column, (first, second) in enumerate(PAIRS):
        source = sp.zeros(4)
        source[first, second] = 1
        source[second, first] = 1
        trace_source = sp.trace(eta * source)
        output = sp.zeros(4)
        for mu in range(4):
            for nu in range(4):
                output[mu, nu] = sp.simplify(
                    p_squared * source[mu, nu] / 2
                    - (eta[mu, nu] * p_squared - p[mu] * p[nu])
                    * trace_source
                    / 6
                )
        for row, (mu, nu) in enumerate(PAIRS):
            bach_from_einstein[row, column] = output[mu, nu]

    bach = sp.simplify(bach_from_einstein * einstein)
    maxwell = sp.simplify(p_squared * eta - p_up * p_up.T)
    hessian_e = sp.diag(einstein / kappa, maxwell)
    hessian_w = sp.diag(alpha_b * bach, maxwell)

    gauge_e = sp.zeros(14, 5)
    for ghost in range(4):
        for row, (mu, nu) in enumerate(PAIRS):
            gauge_e[row, ghost] = (
                (p[mu] if nu == ghost else 0)
                + (p[nu] if mu == ghost else 0)
            )
    for mu in range(4):
        gauge_e[10 + mu, 4] = p[mu]
    gauge_w = sp.zeros(14, 6)
    gauge_w[:, :5] = gauge_e
    for row, (mu, nu) in enumerate(PAIRS):
        gauge_w[row, 5] = 2 * eta[mu, nu]

    noether_e = sp.zeros(5, 14)
    for nu in range(4):
        for row, (mu, rho) in enumerate(PAIRS):
            coefficient = sp.S.Zero
            if rho == nu:
                coefficient += p_up[mu]
            if mu == nu and rho != mu:
                coefficient += p_up[rho]
            noether_e[nu, row] = coefficient
    for nu in range(4):
        noether_e[4, 10 + nu] = p[nu]
    noether_w = sp.zeros(6, 14)
    noether_w[:5, :] = noether_e
    for row, (mu, nu) in enumerate(PAIRS):
        noether_w[5, row] = eta[mu, nu] if mu == nu else 2 * eta[mu, nu]

    ghost_map = sp.zeros(6, 5)
    ghost_map[:5, :] = sp.eye(5)
    field_map = sp.eye(14)
    equation_map = sp.diag(alpha_b * kappa * bach_from_einstein, sp.eye(4))
    identity_map = sp.zeros(6, 5)
    for index in range(4):
        identity_map[index, index] = alpha_b * kappa * p_squared / 2
    identity_map[4, 4] = 1

    _require(hessian_e * gauge_e == sp.zeros(14, 5), "Einstein gauge identity failed")
    _require(noether_e * hessian_e == sp.zeros(5, 14), "Einstein Noether identity failed")
    _require(hessian_w * gauge_w == sp.zeros(14, 6), "Weyl gauge identity failed")
    _require(noether_w * hessian_w == sp.zeros(6, 14), "Weyl Noether identity failed")
    _require(gauge_w * ghost_map == field_map * gauge_e, "ghost/field chain square failed")
    _require(equation_map * hessian_e == hessian_w * field_map, "field/equation chain square failed")
    _require(identity_map * noether_e == noether_w * equation_map, "equation/identity chain square failed")

    return {
        "eta": eta,
        "p": p,
        "p_squared": p_squared,
        "einstein_metric": einstein,
        "bach_from_einstein": bach_from_einstein,
        "weyl_metric": bach,
        "maxwell": maxwell,
        "hessian_e": hessian_e,
        "hessian_w": hessian_w,
        "gauge_e": gauge_e,
        "gauge_w": gauge_w,
        "noether_e": noether_e,
        "noether_w": noether_w,
        "ghost_map": ghost_map,
        "field_map": field_map,
        "equation_map": equation_map,
        "identity_map": identity_map,
    }


def _cohomology_dimensions(data: dict[str, sp.Matrix | sp.Expr]) -> dict[str, int]:
    hessian_e = data["hessian_e"]
    hessian_w = data["hessian_w"]
    gauge_e = data["gauge_e"]
    gauge_w = data["gauge_w"]
    noether_e = data["noether_e"]
    noether_w = data["noether_w"]
    assert isinstance(hessian_e, sp.MatrixBase)
    assert isinstance(hessian_w, sp.MatrixBase)
    assert isinstance(gauge_e, sp.MatrixBase)
    assert isinstance(gauge_w, sp.MatrixBase)
    assert isinstance(noether_e, sp.MatrixBase)
    assert isinstance(noether_w, sp.MatrixBase)
    return {
        "einstein_field": 14 - hessian_e.rank() - gauge_e.rank(),
        "einstein_equation": 14 - noether_e.rank() - hessian_e.rank(),
        "weyl_field": 14 - hessian_w.rank() - gauge_w.rank(),
        "weyl_equation": 14 - noether_w.rank() - hessian_w.rank(),
    }


def _null_injection_data(data: dict[str, sp.Matrix | sp.Expr]) -> dict[str, int | bool]:
    hessian_e = data["hessian_e"]
    hessian_w = data["hessian_w"]
    gauge_e = data["gauge_e"]
    gauge_w = data["gauge_w"]
    assert isinstance(hessian_e, sp.MatrixBase)
    assert isinstance(hessian_w, sp.MatrixBase)
    assert isinstance(gauge_e, sp.MatrixBase)
    assert isinstance(gauge_w, sp.MatrixBase)
    kernel_e = sp.Matrix.hstack(*hessian_e.nullspace())
    intersection_dimension = (
        kernel_e.cols
        + gauge_w.rank()
        - sp.Matrix.hstack(kernel_e, gauge_w).rank()
    )
    induced_kernel_dimension = intersection_dimension - gauge_e.rank()
    source_dimension = 14 - hessian_e.rank() - gauge_e.rank()
    target_dimension = 14 - hessian_w.rank() - gauge_w.rank()
    return {
        "intersection_ker_HE_with_im_RW": intersection_dimension,
        "induced_kernel_dimension": induced_kernel_dimension,
        "induced_map_injective": induced_kernel_dimension == 0,
        "source_dimension": source_dimension,
        "target_dimension": target_dimension,
        "cokernel_dimension": target_dimension - source_dimension + induced_kernel_dimension,
    }


def build_certificate() -> dict[str, Any]:
    background = _load(BACKGROUND)
    _require(
        background.get("result_id") == "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE"
        and background.get("claim_flags", {}).get("exact_nonlinear_background_incidence_certified") is True
        and background.get("classification", {}).get("linearized_tangent_complex_map_constructed") is False,
        "common-background import gate changed",
    )

    alpha_b, kappa = sp.symbols("alpha_B kappa", nonzero=True, real=True)
    noncharacteristic = _principal_complex((1, 2, 3, 5), alpha_b, kappa)
    null = _principal_complex((1, 0, 0, 1), alpha_b, kappa)
    noncharacteristic_cohomology = _cohomology_dimensions(noncharacteristic)
    null_cohomology = _cohomology_dimensions(null)
    null_injection = _null_injection_data(null)

    _require(noncharacteristic["p_squared"] == 37, "nonnull fixture changed")
    _require(null["p_squared"] == 0, "null fixture changed")
    _require(
        noncharacteristic_cohomology
        == {
            "einstein_field": 0,
            "einstein_equation": 0,
            "weyl_field": 0,
            "weyl_equation": 0,
        },
        "noncharacteristic exactness changed",
    )
    _require(
        null_cohomology
        == {
            "einstein_field": 4,
            "einstein_equation": 4,
            "weyl_field": 6,
            "weyl_equation": 6,
        },
        "null cohomology dimensions changed",
    )
    _require(null_injection["induced_map_injective"] is True, "null cohomology map lost injectivity")
    _require(null_injection["cokernel_dimension"] == 2, "null cohomology cokernel changed")

    return {
        "schema": "einstein-maxwell-product-tangent-preflight-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT",
        "result_state": "PRINCIPAL_BV_CHAIN_MAP_CERTIFIED_CURVED_LOWER_ORDER_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                "common_background": {
                    "path": str(BACKGROUND.relative_to(ROOT)),
                    "sha256": _sha256(BACKGROUND),
                }
            },
        },
        "background": {
            "geometry": "R^(1,1) x S^2 and its R_t x S^1_L x S^2_r quotient",
            "field": "aligned source-free Maxwell flux",
            "coupling_relation": "alpha_B*kappa*(k_1+k_2)=3",
            "same_base_point": True,
        },
        "minimal_complex_layouts": {
            "einstein_maxwell": {
                "dimensions": [5, 14, 14, 5],
                "ghosts": ["xi^0", "xi^1", "xi^2", "xi^3", "lambda_U1"],
                "fields": ["h_mn (10)", "a_m (4)"],
                "equations": ["delta Einstein-Maxwell metric equation (10)", "delta Maxwell equation (4)"],
                "identities": ["Diff Noether identities (4)", "U(1) identity (1)"],
            },
            "weyl_maxwell": {
                "dimensions": [6, 14, 14, 6],
                "ghosts": ["xi^0", "xi^1", "xi^2", "xi^3", "lambda_U1", "sigma_Weyl"],
                "fields": ["h_mn (10)", "a_m (4)"],
                "equations": ["delta pure-Weyl-Maxwell metric equation (10)", "delta Maxwell equation (4)"],
                "identities": ["Diff Noether identities (4)", "U(1) identity (1)", "Weyl trace identity (1)"],
            },
            "covariant_gauge_generators": {
                "metric": "delta h_mn=2 nabla_(m xi_n)+2 sigma gbar_mn (sigma absent in Einstein-Maxwell)",
                "maxwell_potential": "delta a_m=(i_xi Fbar)_m+nabla_m lambda in a bundle-covariant splitting",
                "principal_maxwell_generator": "delta a_m=p_m lambda; i_xi Fbar is lower order",
            },
        },
        "principal_operators": {
            "covector_convention": "p_m; p^2=eta^mn p_m p_n; symmetric metric basis (00,01,02,03,11,12,13,22,23,33)",
            "einstein_metric": "sigma_2(delta G)/kappa in the action-normalized Euler row",
            "maxwell": "sigma_2(delta M)^nu_mu=p^2 eta^nu_mu-p^nu p^mu",
            "bach_from_einstein": "Q_p(S)_mn=(p^2/2)S_mn-(eta_mn p^2-p_m p_n)tr(S)/6",
            "weyl_metric": "sigma_4(alpha_B delta B)=alpha_B Q_p sigma_2(delta G)",
            "exact_symbol_matrices_at_nonnull_fixture": {
                "p": ["1", "2", "3", "5"],
                "p_squared": "37",
                "gauge_e": _matrix_strings(noncharacteristic["gauge_e"]),
                "hessian_e": _matrix_strings(noncharacteristic["hessian_e"]),
                "noether_e": _matrix_strings(noncharacteristic["noether_e"]),
                "gauge_w": _matrix_strings(noncharacteristic["gauge_w"]),
                "hessian_w": _matrix_strings(noncharacteristic["hessian_w"]),
                "noether_w": _matrix_strings(noncharacteristic["noether_w"]),
            },
        },
        "principal_chain_map": {
            "ghost_map": "(xi,lambda) -> (xi,lambda,sigma=0)",
            "field_map": "identity on (h,a)",
            "equation_map": "diag(alpha_B*kappa Q_p, identity_Maxwell)",
            "identity_map": "diag((alpha_B*kappa p^2/2) identity_Diff, identity_U1, zero_Weyl)",
            "ghost_field_square": "PASS",
            "field_equation_square": "PASS",
            "equation_identity_square": "PASS",
            "einstein_nilpotency_rows": "PASS",
            "weyl_nilpotency_rows": "PASS",
        },
        "symbol_cohomology": {
            "noncharacteristic_fixture": {
                "ranks": {
                    "R_E": noncharacteristic["gauge_e"].rank(),
                    "H_E": noncharacteristic["hessian_e"].rank(),
                    "N_E": noncharacteristic["noether_e"].rank(),
                    "R_W": noncharacteristic["gauge_w"].rank(),
                    "H_W": noncharacteristic["hessian_w"].rank(),
                    "N_W": noncharacteristic["noether_w"].rank(),
                },
                "cohomology_dimensions": noncharacteristic_cohomology,
                "verdict": "both principal complexes exact away from the characteristic cone",
            },
            "null_fixture": {
                "p": ["1", "0", "0", "1"],
                "ranks": {
                    "R_E": null["gauge_e"].rank(),
                    "H_E": null["hessian_e"].rank(),
                    "N_E": null["noether_e"].rank(),
                    "R_W": null["gauge_w"].rank(),
                    "H_W": null["hessian_w"].rank(),
                    "N_W": null["noether_w"].rank(),
                },
                "block_field_cohomology": {
                    "einstein_metric": 10 - null["einstein_metric"].rank() - null["gauge_e"][:10, :4].rank(),
                    "photon_in_einstein_maxwell": 4 - null["maxwell"].rank() - 1,
                    "weyl_metric_simple_symbol": 10 - null["weyl_metric"].rank() - null["gauge_w"][:10, [0, 1, 2, 3, 5]].rank(),
                    "photon_in_weyl_maxwell": 4 - null["maxwell"].rank() - 1,
                },
                "total_cohomology_dimensions": null_cohomology,
                "induced_field_cohomology_map": null_injection,
                "interpretation": "the ordinary Einstein graviton-plus-photon symbol classes inject; two additional simple-symbol Weyl metric classes remain",
                "warning": "a fourth-order generalized/Jordan mode count requires a prolonged characteristic complex and is not inferred from this simple null symbol",
            },
        },
        "curved_completion_gate": {
            "status": "OPEN",
            "missing_terms": [
                "all curvature-dependent order-three-and-lower terms in delta B",
                "background-flux metric/Maxwell Hessian mixing",
                "the lower-order i_xi Fbar part of the bundle-covariant diffeomorphism generator",
                "formal adjoints and cyclic BV pairing with the product volume form",
                "global patching across the magnetic U(1) bundle",
                "prolonged null complex for fourth-order generalized modes",
            ],
            "required_identity": "construct full differential operators F_2,F_3 with F_2 H_EM=H_WM and F_3 N_EM=N_WM F_2, or produce an exact curvature/flux obstruction",
        },
        "classification": {
            "both_minimal_bv_layouts_frozen": True,
            "maxwell_ghost_and_identity_included": True,
            "principal_bv_chain_map_constructed": True,
            "ordinary_null_einstein_symbol_cohomology_injects": True,
            "additional_simple_symbol_weyl_metric_classes": 2,
            "full_curved_tangent_chain_map_constructed": False,
            "covariant_presymplectic_map_constructed": False,
            "helicity_assignment_on_product_background_completed": False,
            "generalized_fourth_order_modes_classified": False,
        },
        "claim_flags": {
            "local_algebraic_principal_result": True,
            "full_minimal_bv_operator_certificate": False,
            "lorentzian_causal_claim": False,
            "observable_embedding_claim": False,
            "scattering_claim": False,
            "quantum_claim": False,
        },
        "claim_boundary": "This certificate freezes the two minimal BV layouts and proves their exact principal-symbol chain map, noncharacteristic exactness, and injective ordinary null-symbol cohomology map at the common product base point. It does not certify the curvature/flux lower-order Hessians, a full differential chain map, cyclic pairing, product-space helicities, generalized fourth-order modes, causal propagation, observables, scattering, or quantum equivalence.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_product_tangent_preflight --verify bridge/certificates/einstein_maxwell_product_tangent_preflight.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_product_tangent_preflight.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_product_tangent_preflight",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"product tangent preflight is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
