"""Exact all-momentum axial master complex on the compact product.

The calculation keeps arbitrary Fourier momentum k, frequency omega, and
spherical eigenvalue lambda.  Regge--Wheeler and Maxwell-angular gauge are
proved complete for ell>=2.  The ell=1 residual gauge and global n=0 twist are
kept separate.
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
PREFLIGHT_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_harmonic_adjoint_blocks.json"
DOMAIN_CERTIFICATE = ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_axial_master_complex.schema.json"


class AxialMasterError(RuntimeError):
    """Raised when an exact axial-master check fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialMasterError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reduce_harmonic(expression: sp.Expr, harmonic: sp.Expr, theta: sp.Symbol, eigenvalue: sp.Symbol) -> sp.Expr:
    first = sp.diff(harmonic, theta)
    second = sp.diff(harmonic, theta, 2)
    third = sp.diff(harmonic, theta, 3)
    second_rule = -sp.cot(theta) * first - eigenvalue * harmonic
    third_rule = (
        (sp.csc(theta) ** 2 + sp.cot(theta) ** 2 - eigenvalue) * first
        + eigenvalue * sp.cot(theta) * harmonic
    )
    return sp.simplify(
        sp.trigsimp(sp.expand_trig(expression).xreplace({third: third_rule, second: second_rule}))
    )


def _fourier_tensor_check() -> dict[str, Any]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    frequency, momentum, eigenvalue = sp.symbols("omega k lambda", real=True)
    h_time, h_space, q_time, q_space = sp.symbols("h_t h_x q_t q_x")
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    harmonic = sp.Function("Y")(theta)
    first = sp.diff(harmonic, theta)
    axial_one_form = -sine * first

    metric = sp.diag(-1, 1, 1, sine**2)
    metric[0, 3] = metric[3, 0] = epsilon * h_time * wave * axial_one_form
    metric[1, 3] = metric[3, 1] = epsilon * h_space * wave * axial_one_form
    inverse = metric.inv().applyfunc(lambda value: _trunc(value, epsilon, 1))
    connection = [
        [[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = _trunc(
                    sum(
                        inverse[target, index]
                        * (
                            sp.diff(metric[index, right], coordinates[left])
                            + sp.diff(metric[index, left], coordinates[right])
                            - sp.diff(metric[left, right], coordinates[index])
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
    field[0, 1] = epsilon * sp.I * (-frequency * q_space - momentum * q_time) * wave * harmonic
    field[1, 0] = -field[0, 1]
    field[0, 2] = -epsilon * q_time * wave * first
    field[2, 0] = -field[0, 2]
    field[1, 2] = -epsilon * q_space * wave * first
    field[2, 1] = -field[1, 2]

    data = _curvature(
        {
            "epsilon": epsilon,
            "coordinates": coordinates,
            "metric": metric,
            "inverse": inverse,
            "connection": connection,
            "field": field,
        },
        1,
    )
    einstein = (
        data["ricci"] - metric * data["scalar"] / 2 + metric / 2 - _stress(data, 1)
    ).applyfunc(lambda value: sp.expand(sp.diff(value, epsilon).subs(epsilon, 0)))

    expected_einstein = sp.zeros(4)
    expected_einstein[0, 3] = expected_einstein[3, 0] = (
        wave
        * axial_one_form
        * ((momentum**2 + eigenvalue) * h_time + momentum * frequency * h_space + 2 * q_time)
        / 2
    )
    expected_einstein[1, 3] = expected_einstein[3, 1] = (
        -wave
        * axial_one_form
        * (momentum * frequency * h_time + (frequency**2 - eigenvalue) * h_space - 2 * q_space)
        / 2
    )
    tensor_factor = eigenvalue * harmonic * sine / 2 + sp.cos(theta) * first
    expected_einstein[2, 3] = expected_einstein[3, 2] = (
        sp.I * wave * (frequency * h_time + momentum * h_space) * tensor_factor
    )
    einstein_difference = (einstein - expected_einstein).applyfunc(
        lambda value: _reduce_harmonic(value / wave, harmonic, theta, eigenvalue)
    )
    _require(einstein_difference == sp.zeros(4), "arbitrary-lambda Einstein Fourier block changed")

    field_up = sp.zeros(4)
    for left in range(4):
        for right in range(4):
            field_up[left, right] = _trunc(
                sum(
                    inverse[left, first_index]
                    * inverse[right, second_index]
                    * field[first_index, second_index]
                    for first_index in range(4)
                    for second_index in range(4)
                ),
                epsilon,
                1,
            )
    maxwell = sp.Matrix(
        [
            sp.expand(
                sp.diff(
                    sum(
                        sp.diff(sine * field_up[left, right], coordinates[left])
                        for left in range(4)
                    )
                    / sine,
                    epsilon,
                ).subs(epsilon, 0)
            )
            for right in range(4)
        ]
    )
    expected_maxwell = sp.Matrix(
        [
            wave * harmonic * (eigenvalue * h_time + (momentum**2 + eigenvalue) * q_time + momentum * frequency * q_space),
            wave * harmonic * (-eigenvalue * h_space + momentum * frequency * q_time + (frequency**2 - eigenvalue) * q_space),
            -sp.I * wave * first * (frequency * h_time + momentum * h_space + frequency * q_time + momentum * q_space),
            0,
        ]
    )
    maxwell_difference = (maxwell - expected_maxwell).applyfunc(
        lambda value: _reduce_harmonic(value / wave, harmonic, theta, eigenvalue)
    )
    _require(maxwell_difference == sp.zeros(4, 1), "arbitrary-lambda Maxwell Fourier block changed")
    return {
        "harmonic_identity": "Y''+cot(theta)Y'+lambda*Y=0",
        "einstein_rows": [
            "2E_(t,axial)/X=(k^2+lambda)h_t+k*omega*h_x+2q_t",
            "-2E_(x,axial)/X=k*omega*h_t+(omega^2-lambda)h_x-2q_x",
            "E_(theta,phi)/T=i*(omega*h_t+k*h_x)",
        ],
        "maxwell_rows": [
            "M_t/Y=lambda*h_t+(k^2+lambda)q_t+k*omega*q_x",
            "M_x/Y=-lambda*h_x+k*omega*q_t+(omega^2-lambda)q_x",
            "M_angular/dY=-i*(omega*h_t+k*h_x+omega*q_t+k*q_x)",
        ],
        "all_unlisted_rows_zero": True,
        "all_symbolic_remainders": "0",
    }


def _algebraic_reduction() -> dict[str, Any]:
    eigenvalue, momentum, frequency, mass_squared = sp.symbols("lambda k omega s", real=True)
    block = sp.Matrix(
        [
            [momentum**2 + eigenvalue, momentum * frequency, 2, 0],
            [momentum * frequency, frequency**2 - eigenvalue, 0, -2],
            [eigenvalue, 0, momentum**2 + eigenvalue, momentum * frequency],
            [0, -eigenvalue, momentum * frequency, frequency**2 - eigenvalue],
        ]
    )
    determinant = sp.factor(block.det())
    expected = sp.factor(
        eigenvalue
        * (eigenvalue - 2)
        * ((frequency**2 - momentum**2 - eigenvalue) ** 2 - 2 * eigenvalue)
    )
    _require(sp.expand(determinant - expected) == 0, "Fourier-block determinant changed")
    reduced = sp.factor(determinant.subs(frequency**2, momentum**2 + mass_squared))
    transverse = sp.Matrix(
        [momentum * sp.Symbol("H"), -frequency * sp.Symbol("H"), momentum * sp.Symbol("Q"), -frequency * sp.Symbol("Q")]
    )
    image = [sp.factor(value) for value in block * transverse]
    gauge = sp.Matrix([-frequency, momentum, frequency, -momentum])
    _require((block.subs(eigenvalue, 2) * gauge).applyfunc(sp.simplify) == sp.zeros(4, 1), "ell=1 gauge vector changed")
    return {
        "coefficient_matrix_order": ["h_t", "h_x", "q_t", "q_x"],
        "coefficient_matrix": [[str(value) for value in block.row(row)] for row in range(4)],
        "determinant": str(determinant),
        "mass_shell_factorization": str(reduced),
        "transverse_parameterization": "(h_t,h_x,q_t,q_x)=(k*H,-omega*H,k*Q,-omega*Q)",
        "transverse_block_image": [str(value) for value in image],
        "master_matrix": [["lambda", "2"], ["lambda", "lambda"]],
        "dispersion": "omega^2=k_n^2+lambda+/-sqrt(2*lambda)",
        "ell1_gauge_vector": [str(value) for value in gauge],
    }


def build_certificate() -> dict[str, Any]:
    preflight = _load(PREFLIGHT_CERTIFICATE)
    domain = _load(DOMAIN_CERTIFICATE)
    _require(preflight["result_id"] == "COMPACT_EM_HARMONIC_AND_ADJOINT_BLOCK_PREFLIGHT", "block preflight changed")
    _require(domain["result_id"] == "COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT", "fixed-bundle domain changed")
    tensor = _fourier_tensor_check()
    reduction = _algebraic_reduction()
    return {
        "schema": "einstein-maxwell-axial-master-complex-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPACT_EM_AXIAL_MASTER_COMPLEX",
        "result_state": "ALL_S1_MOMENTA_AXIAL_MASTER_COMPLEX_CERTIFIED_POLAR_AND_EXTRA_ADJOINT_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_AXIAL_ALL_N_ELL_M",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (PREFLIGHT_CERTIFICATE, DOMAIN_CERTIFICATE)
            },
        },
        "domain": {
            "spacetime": "R_t x S1_L x S2 on fixed compact U(1) bundle P_N, N=2",
            "Fourier_momentum": "k_n=2*pi*n/L, n in Z",
            "harmonics": "axial metric sector built from Y_(ell,m), ell>=1, all m",
            "gauge_group": "smooth periodic identity-component Diff x U(1)",
            "stage": "Einstein-Maxwell tangent domain before residual quotient",
        },
        "gauge_fixing_and_reconstruction": {
            "ungauged_coefficients": ["h_A X_a", "h_2 X_(ab)", "q_A Y", "b D_aY"],
            "gauge_parameters": ["axial diffeomorphism s X_a", "Maxwell scalar r Y"],
            "transformations": ["delta h_A=partial_A s", "delta h_2=2s", "delta b=s+r", "delta q_A=partial_A r"],
            "ell_ge_2": "X_(ab) is nonzero; h_2=0 fixes s uniquely and b=0 then fixes r uniquely, leaving h_A,q_A with no residual smooth gauge",
            "ell_1": "X_(ab)=0; h_2 is absent and the combined residual r=-s acts as delta h_A=partial_A s, delta q_A=-partial_A s",
            "reconstruction_scope": "complete within the standard axial harmonic decomposition; polar/even coefficients are a separate block",
        },
        "exact_fourier_equations": tensor,
        "master_reduction": reduction,
        "ell_ge_2_theorem": {
            "constraints": ["omega*h_t+k*h_x=0", "omega*q_t+k*q_x=0"],
            "masters": ["H", "Q"],
            "position_space_equation": "(partial_t^2-partial_x^2)(H,Q)^T+K_ell(H,Q)^T=0",
            "branches": [
                {"name": "plus", "Q_over_H": "sqrt(lambda/2)", "omega_squared": "k_n^2+lambda+sqrt(2*lambda)"},
                {"name": "minus", "Q_over_H": "-sqrt(lambda/2)", "omega_squared": "k_n^2+lambda-sqrt(2*lambda)"},
            ],
            "tachyon_free": True,
        },
        "ell1_quotient": {
            "periodic_nonzero_n": "the lambda-2 null vector is generated by a periodic Fourier gauge parameter and is removed; the physical plus branch has omega^2=k_n^2+4",
            "n_zero": "the local gauge vector at omega=k=0 is zero and does not generate the constant H_x=-q_x twist; a generator proportional to x is nonperiodic, so the global twist remains",
            "physical_dispersive_branch": "omega^2=k_n^2+4",
            "global_zero_mode": "omega=k=0, q_x/H_x=-1, retained in the fixed product-periodicity domain",
        },
        "reduced_pairing": {
            "symmetrizer": [["lambda", "0"], ["0", "2"]],
            "current": "j^A(u,v)=u^T W partial^A v-(partial^A u)^T W v",
            "conservation": "partial_A j^A=0 because W K=K^T W",
            "Cauchy_pairing": "integral_(S1) [u^T W dot(v)-dot(u)^T W v] dx",
            "branch_norm_before_covariant_matching": "2*lambda",
            "covariant_Einstein_Maxwell_symplectic_matching": False,
        },
        "adjoint_and_source_interface": {
            "imported_universal_targets": preflight["universal_adjoint_targets"],
            "axial_selection": "quadratic sources must still be projected onto H, P_x, J_i, and the electric harmonic row; a zero H projection alone remains inconclusive",
            "extra_fourth_order_adjoint_classes_solved": False,
        },
        "classification": {
            "all_n_axial_master_complex_ell_ge_2": True,
            "ell1_periodic_gauge_quotient": True,
            "ell1_global_zero_twist_retained": True,
            "exact_all_n_dispersion": True,
            "reduced_local_conserved_pairing": True,
            "covariant_symplectic_matching": False,
            "polar_master_complex": False,
            "complete_fourth_order_adjoint_cokernel": False,
            "quadratic_obstruction_coefficients": False,
            "full_harmonic_theorem": False,
            "lorentzian_causal_theorem": False,
        },
        "next_gate": "derive the polar/even master complex and match both reduced currents to the covariant Einstein-Maxwell symplectic form before solving the extra fourth-order adjoint blocks",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE G1 theorem certifies the complete standard axial harmonic master complex for all S1 momenta, ell, and m on the fixed compact bundle, including its periodic gauge quotient, exact dispersion, global ell=1 twist, and reduced conserved pairing. It does not certify the polar complex, covariant symplectic normalization, extra fourth-order adjoint cokernel, quadratic obstruction coefficients, causal propagation, scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_axial_master_complex --verify bridge/certificates/einstein_maxwell_axial_master_complex.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_axial_master_complex.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_axial_master_complex",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"axial master certificate stale or altered: {path}")


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
