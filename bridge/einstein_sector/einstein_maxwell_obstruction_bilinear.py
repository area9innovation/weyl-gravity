"""Certified constant-lapse obstruction bilinear on the compact fixture span.

This is the first reusable restriction of

    O : H^0_lin x H^0_lin -> coker(L_Weyl-Maxwell).

Its declared domain is the four-dimensional span of the certified compact
radion, duality, l=1 photon, and plus-branch l=2 gravitational tangents.  It
does not claim the complete infinite harmonic classification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_second_order_inclusion import (
    _second_coefficient,
    _spherical_weyl_maxwell,
)


ROOT = Path(__file__).resolve().parents[2]
SECOND_ORDER_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_second_order_inclusion.json"
PHOTON_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_periodic_photon_second_order.json"
GRAVITON_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_periodic_graviton_second_order.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_obstruction_bilinear.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_obstruction_bilinear.schema.json"


class ObstructionBilinearError(RuntimeError):
    """Raised when the exact obstruction-bilinear checks fail."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ObstructionBilinearError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sympify(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


def _mixed_l0_source() -> dict[str, str]:
    """Polarize the only symmetry-allowed off-diagonal fixture pair."""

    epsilon = sp.symbols("epsilon")
    time = sp.symbols("t", real=True)
    radion, duality = sp.symbols("a_R a_D", real=True)
    base_factor = 1 + 2 * epsilon * radion * time**2
    sphere_factor = 1 + 2 * epsilon * radion
    tensors = _spherical_weyl_maxwell(
        sp.log(base_factor) / 2,
        sp.sqrt(sphere_factor),
        epsilon,
        magnetic_amplitude=1,
        electric_amplitude=epsilon * duality,
    )
    residual = tensors["weyl_maxwell_residual"]
    assert isinstance(residual, sp.MatrixBase)
    source_tt = sp.factor(_second_coefficient(residual, epsilon)[0, 0])
    mixed_derivative = sp.factor(sp.diff(source_tt, radion, duality))
    expected = -2 * radion**2 - sp.Rational(1, 2) * duality**2
    _require(sp.simplify(source_tt - expected) == 0, "combined l=0 source changed")
    _require(mixed_derivative == 0, "radion-duality mixed obstruction changed")
    return {
        "combined_quadratic_source_tt": str(source_tt),
        "twice_polarized_entry": str(mixed_derivative),
        "polarized_entry": "0",
    }


def build_certificate() -> dict[str, Any]:
    second_order = _load(SECOND_ORDER_CERTIFICATE)
    photon = _load(PHOTON_CERTIFICATE)
    graviton = _load(GRAVITON_CERTIFICATE)
    _require(second_order.get("result_id") == "EINSTEIN_MAXWELL_SECOND_ORDER_INCLUSION_TEST", "second-order fixture gate changed")
    _require(photon.get("result_id") == "EINSTEIN_MAXWELL_PERIODIC_PHOTON_SECOND_ORDER", "photon fixture gate changed")
    _require(graviton.get("result_id") == "EINSTEIN_MAXWELL_PERIODIC_GRAVITON_SECOND_ORDER", "graviton fixture gate changed")

    q_radion = _sympify(second_order["certified_constant_radion"]["affine_quadratic_weyl_maxwell_source"][0][0])
    q_duality = _sympify(second_order["maxwell_duality_tangent"]["affine_fixed_magnetic_flux_source"][0][0])
    q_photon = _sympify(photon["quadratic_weyl_maxwell_source"]["normalized_sphere_average_tt"])
    q_graviton = _sympify(graviton["quadratic_weyl_maxwell_source_time_zero"]["normalized_sphere_average_tt"])
    expected_diagonal = [
        -2,
        -sp.Rational(1, 2),
        -sp.Rational(16, 3),
        -12 * sp.sqrt(3) - sp.Rational(72, 5),
    ]
    diagonal = [q_radion, q_duality, q_photon, q_graviton]
    _require(all(sp.simplify(left - right) == 0 for left, right in zip(diagonal, expected_diagonal)), "imported diagonal obstruction changed")

    mixed_l0 = _mixed_l0_source()
    matrix = sp.diag(*diagonal)
    coefficients = sp.Matrix(sp.symbols("a_R a_D a_P a_G", real=True))
    quadratic = sp.factor((coefficients.T * matrix * coefficients)[0])
    polarized = lambda left, right: sp.factor(
        ((left + right).T * matrix * (left + right))[0]
        - (left.T * matrix * left)[0]
        - (right.T * matrix * right)[0]
    ) / 2
    for first in range(4):
        for second in range(4):
            left = sp.eye(4)[:, first]
            right = sp.eye(4)[:, second]
            _require(sp.simplify(polarized(left, right) - matrix[first, second]) == 0, "polarization identity changed")

    return {
        "schema": "einstein-maxwell-obstruction-bilinear-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_OBSTRUCTION_BILINEAR_G1",
        "result_state": "CONSTANT_LAPSE_BILINEAR_CERTIFIED_ON_COMPACT_FIXTURE_SPAN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_DECLARED_FIXTURE_SPAN",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (SECOND_ORDER_CERTIFICATE, PHOTON_CERTIFICATE, GRAVITON_CERTIFICATE)
            },
        },
        "domain": {
            "name": "H_fixture",
            "definition": "span_R{R,D,P,G} inside the complete on-shell linear Einstein--Maxwell tangent space before residual quotient",
            "basis_order": ["R_constant_radion", "D_maxwell_duality", "P_l1_photon", "G_l2_gravitational_plus"],
            "basis_quantum_numbers": {
                "R_constant_radion": {"k": 0, "ell": 0, "m": 0, "type": "scalar/radion", "time": "polynomial zero-mode representative"},
                "D_maxwell_duality": {"k": 0, "ell": 0, "m": 0, "type": "global Maxwell duality", "time": "constant"},
                "P_l1_photon": {"k": 0, "ell": 1, "m": 0, "type": "photon--metric normal mode", "omega_squared": "4"},
                "G_l2_gravitational_plus": {"k": 0, "ell": 2, "m": 0, "type": "odd-parity gravitational mode with Maxwell dressing", "omega_squared": "6+2*sqrt(3)"},
            },
            "not_the_complete_domain": "The other m values, nonzero S1 momenta, polarizations, the l2 minus branch, and all higher harmonics remain outside this certificate.",
        },
        "codomain": {
            "name": "C_H",
            "definition": "the one-dimensional constant-lapse/time-translation component span{zeta_H} of coker(L_WM) on the compact fixed-charge domain",
            "pairing": "normalized spatial average of the tt quadratic source on S1 x S2",
            "evaluation": "R,D,P entries are time-independent; G is certified on the t=0 Cauchy slice",
            "not_complete_cokernel": "No claim is made that C_H exhausts the full adjoint cokernel.",
        },
        "bilinear": {
            "definition": "O_H(v,w)=<zeta_H,(1/2)D^2E_WM[v,w]>",
            "polarization_convention": "O_H(v,w)=(Q(v+w)-Q(v)-Q(w))/2 with Q(v)=O_H(v,v)",
            "matrix_basis_order": ["R", "D", "P", "G"],
            "matrix": [[str(sp.factor(matrix[row, column])) for column in range(4)] for row in range(4)],
            "quadratic_form": str(quadratic),
            "symmetric": matrix == matrix.T,
            "radion_duality_direct_tensor_check": mixed_l0,
        },
        "selection_rules": {
            "source": "SO(3) x S1 equivariance of the bilinear differential operator followed by projection to the invariant constant-lapse row",
            "necessary_rules_for_general_harmonics": [
                "S1 momenta must sum to zero: k1+k2=0",
                "an SO(3) scalar occurs only for ell1=ell2 with conjugate m pairing m1+m2=0",
                "the product parity must be even for the scalar constant-lapse projection",
                "within a surviving (k,ell,polarization) block the coefficient still requires tensor calculation",
            ],
            "fixture_consequence": "All pairs with distinct ell vanish. The only same-ell off-diagonal pair R,D is zero by the direct full-tensor polarization check.",
            "full_harmonic_coefficients_certified": False,
        },
        "charge_fibres": {
            "fixed_electric_fixed_magnetic": {
                "condition": "delta^2 Q_E=delta^2 P_M=0",
                "constant_lapse_cokernel": "C_H survives",
                "extension_condition": "Q(v)=0 is necessary on H_fixture",
            },
            "variable_electric_fixed_magnetic": {
                "condition": "delta^2 Q_E allowed, delta^2 P_M=0 at the purely magnetic background",
                "constant_lapse_cokernel": "C_H survives because an averaged electric correction has zero linear tt stress pairing with Fbar",
            },
            "variable_magnetic": {
                "condition": "the second-order magnetic coefficient p is admitted",
                "augmented_linear_pairing": "<zeta_H,L(Phi2,p)> = -p",
                "constant_lapse_cokernel": "C_H is removed from the augmented cokernel",
                "required_lift": "p=Q(v) cancels this component of the extension equation",
                "warning": "Removing C_H is not a full extension theorem when other source components or cokernel directions remain.",
            },
        },
        "taub_relation": {
            "classification": "RELATIVE_TAUB_MOMENT_MAP_COMPONENT",
            "reason": "zeta_H is the adjoint constraint zero-mode associated with the product time-translation Killing field; pairing the quadratic source with it is the standard Taub/linearization-stability construction, restricted here to the Einstein--Maxwell tangent subspace inside Weyl--Maxwell and to a declared charge fibre.",
            "distinction": "This is a relative embedding obstruction, not a proof that the same tangent fails to integrate in Einstein--Maxwell itself.",
            "covariant_symplectic_moment_map_identification_certified": False,
        },
        "fixture_regression": {
            "radion": "Q(R)=-2; magnetic lift p=-2 matches the explicit charge-relaxed extension",
            "duality": "Q(D)=-1/2; magnetic lift p=-1/2 matches the exact duality rotation",
            "photon": "Q(P)=-16/3; fixed-charge obstruction certified, but p=Q(P) has not been shown to solve the other rows",
            "gravitational_plus": "Q(G)=-12*sqrt(3)-72/5 at t=0; fixed-charge obstruction certified, but a charge-relaxed full correction is open",
            "null_universal_cover": "outside H_fixture and outside the compact constant-lapse domain; its nonzero local Chevreton source is explicitly removable and is not a counterexample to O_H",
        },
        "classification": {
            "reusable_symmetric_obstruction_bilinear_on_fixture_span": True,
            "constant_lapse_selection_rules_certified": True,
            "fixed_vs_variable_charge_cokernel_change_certified": True,
            "relative_taub_component_identified": True,
            "complete_H0_linear_domain_classified": False,
            "complete_adjoint_cokernel_classified": False,
            "full_harmonic_obstruction_theorem": False,
            "general_nonlinear_closure_certified": False,
        },
        "next_gate": "promote from H_fixture to the complete periodic harmonic domain by computing every surviving equal-(k,ell) polarization block and the full adjoint cokernel",
        "claim_boundary": "This G1 LOCAL-ALGEBRAIC/REDUCED-MODE theorem constructs the constant-lapse component of the second-order obstruction bilinear on the declared four-dimensional compact fixture span and proves its charge-fibre behavior and symmetry selection rules. It does not classify the complete linear cohomology, every harmonic coefficient, the full cokernel, charge-relaxed photon/graviton extensions, covariant symplectic moment-map equality, causal evolution, scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_obstruction_bilinear --verify bridge/certificates/einstein_maxwell_obstruction_bilinear.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_obstruction_bilinear.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_obstruction_bilinear",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"obstruction bilinear certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
