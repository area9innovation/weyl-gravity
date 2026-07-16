"""Exact preflight for compact Einstein--Maxwell harmonic/adjoint blocks.

The certificate closes an exact all-(ell,m) homogeneous axial H_x/a_x tower
and freezes the universal compact adjoint targets.  Completeness of the axial
gauge quotient, polar blocks, nonzero S1 momentum, and possible extra
fourth-order adjoint classes remain fail-closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import (
    _curvature,
    _stress,
    _trunc,
)


ROOT = Path(__file__).resolve().parents[2]
DOMAIN_CERTIFICATE = ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json"
PHOTON_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_periodic_photon_second_order.json"
GRAVITON_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_periodic_graviton_second_order.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_harmonic_adjoint_blocks.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_harmonic_adjoint_blocks.schema.json"


class HarmonicBlockError(RuntimeError):
    """Raised when an exact harmonic-block check fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HarmonicBlockError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _axial_geometry(ell: int) -> tuple[dict[str, object], sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    metric_amplitude = sp.Function("H")(time)
    maxwell_amplitude = sp.Function("q")(time)
    harmonic = sp.legendre(ell, sp.cos(theta))
    axial_one_form = -sine * sp.diff(harmonic, theta)

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[1, 3] = metric[3, 1] = epsilon * metric_amplitude * axial_one_form
    inverse = metric.inv().applyfunc(lambda value: _trunc(value, epsilon, 1))
    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for first in range(4):
            for second in range(4):
                connection[target][first][second] = _trunc(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, second], coordinates[first])
                            + sp.diff(metric[index, first], coordinates[second])
                            - sp.diff(metric[first, second], coordinates[index])
                        )
                        for index in range(4)
                    )
                    / 2,
                    epsilon,
                    1,
                )

    field = sp.zeros(4)
    field[2, 3] = sine
    field[3, 2] = -sine
    field[0, 1] = epsilon * sp.diff(maxwell_amplitude, time) * harmonic
    field[1, 0] = -field[0, 1]
    field[1, 2] = -epsilon * maxwell_amplitude * sp.diff(harmonic, theta)
    field[2, 1] = -field[1, 2]
    return (
        {
            "epsilon": epsilon,
            "coordinates": coordinates,
            "metric": metric,
            "inverse": inverse,
            "connection": connection,
            "field": field,
        },
        metric_amplitude,
        maxwell_amplitude,
        harmonic,
        axial_one_form,
    )


def _direct_axial_check(ell: int) -> dict[str, Any]:
    """Check the complete linear tensor equations for one new ell fixture."""

    raw, metric_amplitude, maxwell_amplitude, harmonic, axial_one_form = _axial_geometry(ell)
    data = _curvature(raw, 1)
    epsilon = data["epsilon"]
    coordinates = data["coordinates"]
    metric = data["metric"]
    inverse = data["inverse"]
    field = data["field"]
    assert isinstance(epsilon, sp.Symbol)
    assert isinstance(coordinates, tuple)
    assert isinstance(metric, sp.MatrixBase)
    assert isinstance(inverse, sp.MatrixBase)
    assert isinstance(field, sp.MatrixBase)
    eigenvalue = sp.Integer(ell * (ell + 1))

    einstein = (
        data["ricci"] - metric * data["scalar"] / 2 + metric / 2 - _stress(data, 1)
    ).applyfunc(lambda value: sp.factor(sp.trigsimp(sp.diff(value, epsilon).subs(epsilon, 0))))
    expected_einstein = sp.zeros(4)
    reduced_metric = (
        sp.diff(metric_amplitude, coordinates[0], 2)
        + eigenvalue * metric_amplitude
        + 2 * maxwell_amplitude
    )
    expected_einstein[1, 3] = expected_einstein[3, 1] = axial_one_form * reduced_metric / 2
    difference = (einstein - expected_einstein).applyfunc(
        lambda value: sp.simplify(sp.trigsimp(sp.expand_trig(value)))
    )
    _require(difference == sp.zeros(4), f"ell={ell} Einstein block changed")

    sine = sp.sin(coordinates[2])
    field_up = sp.zeros(4)
    for first in range(4):
        for second in range(4):
            field_up[first, second] = _trunc(
                sum(
                    inverse[first, left] * inverse[second, right] * field[left, right]
                    for left in range(4)
                    for right in range(4)
                ),
                epsilon,
                1,
            )
    maxwell = sp.Matrix(
        [
            sp.diff(
                sum(
                    sp.diff(sine * field_up[first, second], coordinates[first])
                    for first in range(4)
                )
                / sine,
                epsilon,
            ).subs(epsilon, 0)
            for second in range(4)
        ]
    )
    expected_maxwell = sp.zeros(4, 1)
    reduced_maxwell = (
        sp.diff(maxwell_amplitude, coordinates[0], 2)
        + eigenvalue * maxwell_amplitude
        + eigenvalue * metric_amplitude
    )
    expected_maxwell[1] = -harmonic * reduced_maxwell
    maxwell_difference = (maxwell - expected_maxwell).applyfunc(
        lambda value: sp.simplify(sp.trigsimp(sp.expand_trig(value)))
    )
    _require(maxwell_difference == sp.zeros(4, 1), f"ell={ell} Maxwell block changed")
    return {
        "ell": ell,
        "lambda": int(eigenvalue),
        "einstein_nonzero_row": "E_(x,axial)=X_(ell,m)*(H''+lambda*H+2*q)/2",
        "maxwell_nonzero_row": "M_x=-Y_(ell,m)*(q''+lambda*q+lambda*H)",
        "all_other_linear_rows_zero": True,
    }


def _abstract_axial_identity_check() -> dict[str, Any]:
    """Prove the tower using only the scalar-harmonic eigenvalue identity."""

    theta = sp.symbols("theta", real=True)
    eigenvalue = sp.symbols("lambda", positive=True)
    harmonic = sp.Function("Y")(theta)
    first = sp.diff(harmonic, theta)
    second = sp.diff(harmonic, theta, 2)
    third = sp.diff(harmonic, theta, 3)
    harmonic_equation = second + sp.cot(theta) * first + eigenvalue * harmonic
    second_rule = -sp.cot(theta) * first - eigenvalue * harmonic
    third_rule = (
        (sp.csc(theta) ** 2 + sp.cot(theta) ** 2 - eigenvalue) * first
        + eigenvalue * sp.cot(theta) * harmonic
    )
    _require(
        sp.simplify(sp.diff(harmonic_equation, theta).xreplace({second: second_rule, third: third_rule})) == 0,
        "differentiated harmonic identity changed",
    )
    # These are the angular remainders left by the full tensor calculation
    # after subtracting the claimed reduced Einstein and Maxwell rows.
    einstein_remainder = (
        eigenvalue * sp.sin(theta) * first
        + sp.sin(theta) * third
        + sp.cos(theta) * second
        - first / sp.sin(theta)
    )
    maxwell_remainder = second + sp.cot(theta) * first + eigenvalue * harmonic
    reduced_einstein = sp.simplify(
        sp.trigsimp(einstein_remainder.xreplace({third: third_rule, second: second_rule}))
    )
    reduced_maxwell = sp.simplify(
        sp.trigsimp(maxwell_remainder.xreplace({second: second_rule}))
    )
    _require(reduced_einstein == 0, "abstract Einstein harmonic reduction changed")
    _require(reduced_maxwell == 0, "abstract Maxwell harmonic reduction changed")
    return {
        "input_identity": "Y''+cot(theta)Y'+lambda*Y=0",
        "differentiated_identity": "Y'''+cot(theta)Y''+(lambda-csc(theta)^2)Y'=0",
        "Einstein_angular_remainder_reduces_to": str(reduced_einstein),
        "Maxwell_angular_remainder_reduces_to": str(reduced_maxwell),
        "scope": "arbitrary scalar harmonic eigenvalue lambda; SO(3) equivariance supplies all m",
    }


def _spectral_check() -> dict[str, Any]:
    eigenvalue, spectral = sp.symbols("lambda mu", positive=True)
    coupling = sp.Matrix([[eigenvalue, 2], [eigenvalue, eigenvalue]])
    characteristic = sp.factor((spectral * sp.eye(2) - coupling).det())
    expected = sp.expand((spectral - eigenvalue) ** 2 - 2 * eigenvalue)
    _require(sp.expand(characteristic - expected) == 0, "axial characteristic polynomial changed")
    root = sp.sqrt(eigenvalue / 2)
    plus = sp.Matrix([1, root])
    minus = sp.Matrix([1, -root])
    omega_plus = eigenvalue + sp.sqrt(2 * eigenvalue)
    omega_minus = eigenvalue - sp.sqrt(2 * eigenvalue)
    _require((coupling * plus - omega_plus * plus).applyfunc(sp.simplify) == sp.zeros(2, 1), "plus branch changed")
    _require((coupling * minus - omega_minus * minus).applyfunc(sp.simplify) == sp.zeros(2, 1), "minus branch changed")

    symmetrizer = sp.diag(eigenvalue, 2)
    _require(symmetrizer * coupling == coupling.T * symmetrizer, "reduced symmetrizer changed")
    plus_norm = sp.simplify((plus.T * symmetrizer * plus)[0])
    minus_norm = sp.simplify((minus.T * symmetrizer * minus)[0])
    _require(plus_norm == 2 * eigenvalue and minus_norm == 2 * eigenvalue, "branch Wronskian norm changed")
    return {
        "lambda_ell": "ell*(ell+1)",
        "coupling_matrix": [["lambda", "2"], ["lambda", "lambda"]],
        "characteristic_polynomial": str(characteristic),
        "branches": {
            "plus": {"q_over_H": "sqrt(lambda/2)", "omega_squared": "lambda+sqrt(2*lambda)"},
            "minus": {"q_over_H": "-sqrt(lambda/2)", "omega_squared": "lambda-sqrt(2*lambda)"},
        },
        "reduced_action_symmetrizer": [["lambda", "0"], ["0", "2"]],
        "conserved_wronskian": "Omega_red(u,v)=u^T W v'-u'^T W v",
        "branch_wronskian_norm": str(plus_norm),
        "covariant_symplectic_normalization_matched": False,
    }


def _ell_one_global_check() -> dict[str, Any]:
    time, space, theta, length, amplitude = sp.symbols("t x theta L H_0", real=True)
    harmonic = sp.cos(theta)
    xi_phi = amplitude * space
    gauge_parameter = -amplitude * space * harmonic
    i_xi_f_theta = -amplitude * space * sp.sin(theta)
    d_lambda_theta = sp.diff(gauge_parameter, theta)
    d_lambda_x = sp.diff(gauge_parameter, space)
    _require(sp.simplify(i_xi_f_theta + d_lambda_theta) == 0, "local angular gauge cancellation changed")
    _require(d_lambda_x == -amplitude * harmonic, "local Maxwell zero branch changed")
    monodromy_xi = sp.expand(xi_phi.subs(space, space + length) - xi_phi)
    monodromy_lambda = sp.expand(
        gauge_parameter.subs(space, space + length) - gauge_parameter
    )
    _require(monodromy_xi == amplitude * length, "diffeomorphism monodromy changed")
    _require(monodromy_lambda == -amplitude * length * harmonic, "gauge monodromy changed")
    return {
        "branch": "ell=1 minus, omega^2=0, q/H=-1",
        "local_generator": "xi^phi=H_0*x, lambda=-H_0*x*cos(theta)",
        "local_field_check": "L_xi g gives h_(x,phi)=H_0*sin(theta)^2 and i_xi F+d lambda=-H_0*cos(theta) dx",
        "S1_monodromy": {"Delta_xi_phi": str(monodromy_xi), "Delta_lambda": str(monodromy_lambda)},
        "global_classification": "LOCALLY_GAUGE_BUT_NOT_GENERATED_BY_A_SMOOTH_PERIODIC_INFINITESIMAL_GAUGE_PARAMETER_FOR_H_0_NONZERO",
        "interpretation": "a global zero-mode/twist tangent in the fixed product-periodicity domain; its nonlinear integrability and possible discrete large-gauge identification remain open",
    }


def build_certificate() -> dict[str, Any]:
    domain = _load(DOMAIN_CERTIFICATE)
    photon = _load(PHOTON_CERTIFICATE)
    graviton = _load(GRAVITON_CERTIFICATE)
    _require(domain["result_id"] == "COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT", "domain gate changed")
    _require(photon["first_order_mode"]["frequency_squared_matrix"] == [[2, 2], [2, 2]], "ell=1 fixture changed")
    _require(graviton["first_order_mode"]["frequency_squared_matrix"] == [[6, 2], [6, 6]], "ell=2 fixture changed")

    direct_checks = [_direct_axial_check(ell) for ell in (3, 4)]
    spectral = _spectral_check()
    exceptional = _ell_one_global_check()
    return {
        "schema": "einstein-maxwell-harmonic-adjoint-blocks-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPACT_EM_HARMONIC_AND_ADJOINT_BLOCK_PREFLIGHT",
        "result_state": "AXIAL_N0_TOWER_AND_UNIVERSAL_ADJOINT_TARGETS_CERTIFIED_OTHER_BLOCKS_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_BLOCK_PREFLIGHT_AXIAL_N0_TOWER",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (DOMAIN_CERTIFICATE, PHOTON_CERTIFICATE, GRAVITON_CERTIFICATE)
            },
        },
        "domain": {
            "spacetime": "R_t x S1_L x S2 on fixed compact U(1) bundle P_N, N=2",
            "harmonic_labels": "n in Z, ell>=0, -ell<=m<=ell, parity, polarization, normal branch, frequency sign",
            "gauge_group": "smooth periodic identity-component Diff x U(1) on the Einstein-Maxwell domain",
            "residual_stage": "before the final residual quotient",
        },
        "axial_n0_tower": {
            "status": "EXACT_ALL_ELL_M_TOWER_WITHIN_THE_DECLARED_HX_AX_REPRESENTATIVE",
            "representative": "h_(x,a)=H(t) X_a^(ell,m), a_x=q(t)Y_(ell,m), ell>=1",
            "reduced_equations": ["H''+lambda_ell*H+2*q=0", "q''+lambda_ell*q+lambda_ell*H=0"],
            "spectral_data": spectral,
            "all_ell_identity_proof": _abstract_axial_identity_check(),
            "SO3_completion": "the m=0 tensor checks extend to every m by SO(3) equivariance of the background and operator",
            "imported_regressions": {
                "ell_1": "K_1=[[2,2],[2,2]], plus omega^2=4, minus omega^2=0",
                "ell_2": "K_2=[[6,2],[6,6]], omega^2=6+/-2*sqrt(3)",
            },
            "new_direct_tensor_regressions": direct_checks,
            "physical_branch_classification": {
                "ell_ge_2": "both branches have positive omega^2 and nonzero reduced Wronskian norm",
                "ell_1_plus": "the certified omega^2=4 photon-metric branch",
                "ell_1_minus": exceptional,
            },
        },
        "block_ledger": [
            {"block": "n=0 axial H_x/a_x tower, ell>=1, all m", "status": "CERTIFIED_TOWER", "missing": "proof that this representative exhausts the full axial gauge quotient, covariant symplectic normalization, and quadratic coefficients"},
            {"block": "n!=0 axial", "status": "OPEN", "missing": "base-vector constraints, gauge-invariant master reconstruction, exact dispersion"},
            {"block": "polar/even metric-Maxwell, all n", "status": "OPEN", "missing": "gauge-invariant masters, constraints, reconstruction, exact dispersion"},
            {"block": "ell=0 homogeneous scalar/radion/duality", "status": "FIXTURES_ONLY", "missing": "complete zero-mode and Jordan-chain classification"},
            {"block": "ell=1 exceptional polar and global modes", "status": "OPEN_EXCEPT_AXIAL_ZERO_MODE", "missing": "complete periodic gauge and global-modulus classification"},
        ],
        "universal_adjoint_targets": {
            "conformal_stabilizer_argument": [
                "the nonzero product Weyl tensor has distinct factor-plane eigendistributions, so a connected conformal stabilizer preserves the product splitting",
                "the common conformal factor on the two factors is constant; integrating the S2 divergence forces it to zero",
                "periodicity removes the flat-cylinder boost, leaving partial_t, partial_x, and the three SO(3) rotations",
                "there is no nonzero Weyl compensator in a background stabilizer",
            ],
            "metric_KID_basis": ["H=partial_t", "P_x=partial_x", "J_1", "J_2", "J_3"],
            "metric_KID_dimension": 5,
            "source_projectors": {
                "H": "integral_Sigma n^a S_ab (partial_t)^b",
                "P_x": "integral_Sigma n^a S_ab (partial_x)^b",
                "J_i": "integral_Sigma n^a S_ab (J_i)^b with the patchwise Maxwell compensation",
            },
            "maxwell_harmonic_target": "the electric harmonic-flux row dual to the H^1(S1) generator dx; it is separate from the constant U(1) Noether identity",
            "magnetic_target": "excluded from the tangent/correction space because c_1(P_N) is fixed",
            "constant_u1_reducibility": "its integrated Gauss identity on closed Sigma is a boundary-zero identity, not an additional independent Taub charge",
            "complete_full_weyl_maxwell_adjoint_cokernel": False,
            "open_extra_targets": "fourth-order constraint-adjoint classes not generated by background stabilizers must still be solved blockwise",
        },
        "selection_and_projection_interface": {
            "scalar_targets_H_Px_QE": "n1+n2=0, ell1=ell2, m1+m2=0, opposite frequency signs for a conserved pairing",
            "rotation_targets_J": "n1+n2=0 and the Clebsch-Gordan product must contain L=1 with m1+m2=M; unlike the scalar target this can mix adjacent ell sectors subject to parity",
            "required_block_output": [
                "gauge-invariant master variables and reconstruction map",
                "exact linear operator and branch eigenvectors",
                "reduced Wronskian plus covariant-symplectic matching status",
                "all universal and extra adjoint projectors",
                "quadratic source pairing with each projector",
                "explicit second-order correction whenever every pairing vanishes",
            ],
        },
        "decision_protocol": {
            "nonzero_any_adjoint_pairing": "NO_SECOND_ORDER_CORRECTION_IN_THE_DECLARED_FIXED_BUNDLE_BLOCK",
            "zero_constant_lapse_only": "INCONCLUSIVE",
            "zero_all_certified_pairings_without_cokernel_completeness": "INCONCLUSIVE",
            "extension_certificate": "requires a complete adjoint target for the block and an explicit Phi^(2), not merely vanishing pairings",
        },
        "classification": {
            "declared_axial_n0_tower_all_ell_m": True,
            "complete_axial_n0_gauge_quotient": False,
            "ell1_zero_branch_global_scope_classified": True,
            "reduced_conserved_wronskian": True,
            "covariant_symplectic_normalization": False,
            "universal_background_stabilizer_targets": True,
            "complete_full_adjoint_cokernel": False,
            "complete_all_parity_momentum_blocks": False,
            "full_harmonic_obstruction_theorem": False,
            "lorentzian_causal_theorem": False,
        },
        "next_gate": "derive the n!=0 axial and all polar gauge-invariant master complexes, match their reduced Wronskians to the covariant symplectic form, and solve for any extra fourth-order adjoint classes before quadratic source enumeration",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE preflight certifies an exact all-(ell,m) n=0 axial H_x/a_x tower, its branches and reduced Wronskian, the global status of the ell=1 zero branch, and the universal compact stabilizer projectors. It does not prove that this representative exhausts the axial gauge quotient, or certify nonzero S1 momentum, polar blocks, covariant symplectic normalization, the complete fourth-order adjoint cokernel, quadratic coefficients, causal evolution, scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_harmonic_adjoint_blocks --verify bridge/certificates/einstein_maxwell_harmonic_adjoint_blocks.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_harmonic_adjoint_blocks.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_harmonic_adjoint_blocks",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"harmonic block certificate stale or altered: {path}")


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
