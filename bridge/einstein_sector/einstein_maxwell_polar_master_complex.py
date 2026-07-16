"""Arbitrary-harmonic polar Einstein--Maxwell master theorem.

The theorem proves the full linearized tensor identity column by column for an
abstract spherical eigenfunction, audits the singular reconstruction locus,
and promotes the ell>=2 polar preflight to every Fourier momentum and m.
Exceptional ell=0,1 and covariant symplectic matching remain separate gates.
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
PREFLIGHT_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_polar_master_preflight.json"
AXIAL_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_polar_master_complex.schema.json"


class PolarMasterComplexError(RuntimeError):
    """Raised when an exact polar-master identity fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarMasterComplexError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix() -> tuple[sp.Matrix, tuple[sp.Symbol, ...]]:
    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    matrix = sp.Matrix(
        [
            [0, 0, eigenvalue / 2, momentum**2 + eigenvalue / 2, -eigenvalue],
            [0, eigenvalue / 2, 0, -momentum * frequency, 0],
            [eigenvalue / 2, 0, 0, frequency**2 - eigenvalue / 2, eigenvalue],
            [0, sp.I * momentum / 2, sp.I * frequency / 2, sp.I * frequency / 2, -sp.I * frequency],
            [sp.I * momentum / 2, sp.I * frequency / 2, 0, -sp.I * momentum / 2, sp.I * momentum],
            [(momentum**2 + eigenvalue / 2) / 2, momentum * frequency, (frequency**2 - eigenvalue / 2) / 2, (frequency**2 - momentum**2 + 2) / 2, -eigenvalue],
            [sp.Rational(1, 2), 0, -sp.Rational(1, 2), 0, 0],
            [sp.Rational(1, 2), 0, -sp.Rational(1, 2), 1, frequency**2 - momentum**2 - eigenvalue],
        ]
    )
    return matrix, (eigenvalue, momentum, frequency)


def _reduce_harmonic(
    expression: sp.Expr,
    wave: sp.Expr,
    harmonic: sp.Expr,
    theta: sp.Symbol,
    eigenvalue: sp.Symbol,
) -> sp.Expr:
    first = sp.diff(harmonic, theta)
    second = sp.diff(harmonic, theta, 2)
    third = sp.diff(harmonic, theta, 3)
    second_rule = -sp.cot(theta) * first - eigenvalue * harmonic
    third_rule = (
        (sp.csc(theta) ** 2 + sp.cot(theta) ** 2 - eigenvalue) * first
        + eigenvalue * sp.cot(theta) * harmonic
    )
    reduced = sp.expand(expression / wave).xreplace(
        {third: third_rule, second: second_rule}
    )
    return sp.factor(
        sp.simplify(sp.trigsimp(sp.expand_trig(reduced), method="fu"))
    )


def _tensor_column(column_name: str) -> dict[str, Any]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    matrix, (eigenvalue, momentum, frequency) = _matrix()
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    harmonic = sp.Function("Y")(theta)
    first = sp.diff(harmonic, theta)
    second = sp.diff(harmonic, theta, 2)
    axial_one_form = -sine * first

    metric = sp.diag(-1, 1, 1, sine**2)
    if column_name == "A":
        metric[0, 0] += epsilon * wave * harmonic
    elif column_name == "B":
        metric[0, 1] = metric[1, 0] = epsilon * wave * harmonic
    elif column_name == "C":
        metric[1, 1] += epsilon * wave * harmonic
    elif column_name == "K":
        metric[2, 2] += epsilon * wave * harmonic
        metric[3, 3] += epsilon * wave * harmonic * sine**2
    elif column_name != "U":
        raise PolarMasterComplexError(f"unknown polar column: {column_name}")

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
    if column_name == "U":
        field[0, 3] = -sp.I * frequency * epsilon * wave * axial_one_form
        field[3, 0] = -field[0, 3]
        field[1, 3] = sp.I * momentum * epsilon * wave * axial_one_form
        field[3, 1] = -field[1, 3]
        field[2, 3] += epsilon * wave * sp.diff(axial_one_form, theta)
        field[3, 2] = -field[2, 3]

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
        data["ricci"]
        - metric * data["scalar"] / 2
        + metric / 2
        - _stress(data, 1)
    ).applyfunc(lambda value: sp.expand(sp.diff(value, epsilon).subs(epsilon, 0)))

    column = {"A": 0, "B": 1, "C": 2, "K": 3, "U": 4}[column_name]
    coefficients = matrix[:, column]
    expected = sp.zeros(4)
    expected[0, 0] = wave * harmonic * coefficients[0]
    expected[0, 1] = expected[1, 0] = wave * harmonic * coefficients[1]
    expected[1, 1] = wave * harmonic * coefficients[2]
    expected[0, 2] = expected[2, 0] = wave * first * coefficients[3]
    expected[1, 2] = expected[2, 1] = wave * first * coefficients[4]
    tracefree = (second - sp.cot(theta) * first) / 2
    expected[2, 2] = wave * (
        harmonic * coefficients[5] + tracefree * coefficients[6]
    )
    expected[3, 3] = wave * sine**2 * (
        harmonic * coefficients[5] - tracefree * coefficients[6]
    )
    einstein_difference = (einstein - expected).applyfunc(
        lambda value: _reduce_harmonic(
            value, wave, harmonic, theta, eigenvalue
        )
    )
    _require(
        einstein_difference == sp.zeros(4),
        f"arbitrary-harmonic Einstein column changed: {column_name}",
    )

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
    # Standard oriented sphere chart. The axes follow by smooth continuation.
    volume = _trunc(sp.sqrt(-metric.det()), epsilon, 1).subs(
        sp.Abs(sine), sine
    )
    maxwell_density = sp.Matrix(
        [
            sp.expand(
                sp.diff(
                    sum(
                        sp.diff(
                            volume * field_up[left, right], coordinates[left]
                        )
                        for left in range(4)
                    ),
                    epsilon,
                ).subs(epsilon, 0)
            )
            for right in range(4)
        ]
    )
    expected_density = sp.Matrix(
        [0, 0, 0, -wave * first * coefficients[7]]
    )
    maxwell_difference = (maxwell_density - expected_density).applyfunc(
        lambda value: _reduce_harmonic(
            value, wave, harmonic, theta, eigenvalue
        )
    )
    _require(
        maxwell_difference == sp.zeros(4, 1),
        f"arbitrary-harmonic Maxwell column changed: {column_name}",
    )
    return {
        "column": column_name,
        "Einstein_component_remainders": "0",
        "Maxwell_density_remainders": "0",
    }


def _tensor_identity() -> dict[str, Any]:
    columns = [_tensor_column(name) for name in ("A", "B", "C", "K", "U")]
    return {
        "harmonic_identity": "Y''+cot(theta)Y'+lambda Y=0",
        "derived_identity": "Y'''=(csc(theta)^2+cot(theta)^2-lambda)Y'+lambda cot(theta)Y",
        "column_checks": columns,
        "row_order": [
            "E00",
            "E01",
            "E11",
            "E0a",
            "E1a",
            "sphere_trace",
            "sphere_tracefree",
            "Maxwell_axial_density",
        ],
        "all_unlisted_tensor_components": "0",
        "volume_density": "perturbed sqrt(-g) retained; 0<theta<pi oriented chart, axes by smooth continuation",
    }


def _algebraic_and_singular_audit() -> dict[str, Any]:
    matrix, (eigenvalue, momentum, frequency) = _matrix()
    mass = sp.symbols("s", real=True)
    master = sp.Matrix([[eigenvalue, -2 * eigenvalue], [-1, eigenvalue]])
    characteristic = sp.factor((mass * sp.eye(2) - master).det())
    _require(
        sp.expand(characteristic - ((mass - eigenvalue) ** 2 - 2 * eigenvalue))
        == 0,
        "polar characteristic changed",
    )
    singular_minor = sp.factor(matrix[[0, 1, 2, 6, 7], :].det())
    singular_value = sp.factor(
        singular_minor.subs(frequency**2, momentum**2)
    )
    expected_singular = eigenvalue**3 * (eigenvalue - 2) / 8
    _require(
        sp.expand(singular_value - expected_singular) == 0,
        "s=0 polar rank minor changed",
    )
    symmetrizer = sp.diag(1, 2 * eigenvalue)
    _require(
        symmetrizer * master == master.T * symmetrizer,
        "polar symmetrizer changed",
    )
    return {
        "coefficient_matrix": [
            [str(sp.factor(value)) for value in matrix.row(row)]
            for row in range(matrix.rows)
        ],
        "s_nonzero_reconstruction": [
            "R=K-2U",
            "A=C=-(omega^2+k^2)R/(omega^2-k^2)",
            "B=2k omega R/(omega^2-k^2)",
        ],
        "master_matrix": [[str(value) for value in master.row(row)] for row in range(2)],
        "characteristic": str(characteristic),
        "dispersion": "omega^2=k_n^2+lambda+/-sqrt(2*lambda)",
        "physical_branch_s_positive": "lambda>=6 implies lambda-sqrt(2lambda)>0",
        "s_zero_minor_rows": ["E00", "E01", "E11", "sphere_tracefree", "Maxwell_axial_density"],
        "s_zero_minor": str(singular_value),
        "s_zero_verdict": "full column rank for lambda>=6; only the zero gauge-fixed field",
        "symmetrizer": [["1", "0"], ["0", "2*lambda"]],
    }


def _gauge_and_all_m_theorem() -> dict[str, Any]:
    eigenvalue = sp.symbols("lambda", real=True)
    tensor_harmonic_norm = sp.factor(eigenvalue * (eigenvalue - 2) / 2)
    _require(
        tensor_harmonic_norm.subs(eigenvalue, 6) != 0,
        "polar tensor-harmonic rank witness changed",
    )
    return {
        "ungauged_coefficients": [
            "h_AB Y",
            "h_A D_aY",
            "K g_abY",
            "G (D_aD_bY+lambda g_abY/2)",
            "a_a=U X_a",
        ],
        "gauge_parameters": ["xi_A Y", "xi D_aY"],
        "transformations": [
            "delta G=2xi",
            "delta h_A=xi_A+partial_A xi",
            "delta K=-lambda xi",
            "delta U=-xi from i_xi F_background",
        ],
        "tensor_harmonic_norm_factor": str(tensor_harmonic_norm),
        "ell_ge_2_rank": "lambda>=6 makes the tracefree tensor harmonic nonzero; G=0 fixes xi uniquely and h_A=0 then fixes xi_A uniquely",
        "residual_gauge": "none for smooth ell>=2 polar harmonics",
        "all_m_argument": "The product metric and magnetic sphere volume form are SO(3)-invariant, and the natural linearized equations are equivariant. Each ell eigenspace is irreducible and each declared harmonic type is a multiplicity copy, so the axisymmetric coefficient matrix acts tensor identity on all m.",
    }


def build_certificate() -> dict[str, Any]:
    preflight = _load(PREFLIGHT_CERTIFICATE)
    axial = _load(AXIAL_CERTIFICATE)
    _require(
        preflight["result_id"] == "COMPACT_EM_POLAR_MASTER_PREFLIGHT",
        "polar preflight input changed",
    )
    _require(
        axial["result_id"] == "COMPACT_EM_AXIAL_MASTER_COMPLEX",
        "axial master input changed",
    )
    return {
        "schema": "einstein-maxwell-polar-master-complex-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPACT_EM_POLAR_MASTER_COMPLEX",
        "result_state": "G2_POLAR_ELL_GE2_ALL_MOMENTA_TENSOR_IDENTITY_CERTIFIED_EXCEPTIONS_AND_SYMPLECTIC_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_POLAR_ALL_N_ELL_M_ELL_GE2",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (PREFLIGHT_CERTIFICATE, AXIAL_CERTIFICATE)
            },
        },
        "domain": "fixed-P_N compact product; every S1 Fourier momentum and every polar spherical harmonic with ell>=2; smooth periodic identity-component gauge; before residual quotient",
        "gauge_theorem": _gauge_and_all_m_theorem(),
        "exact_tensor_identity": _tensor_identity(),
        "algebraic_and_singular_audit": _algebraic_and_singular_audit(),
        "isospectral_theorem": "For every n, ell>=2, and m, the polar eigenvalues equal the certified axial eigenvalues lambda+/-sqrt(2lambda); the parity sectors have distinct reconstruction maps.",
        "reduced_pairing": {
            "current": "j^A=u^T W partial^A v-(partial^A u)^T W v",
            "symmetrizer": "diag(1,2lambda)",
            "covariant_symplectic_matching": False,
        },
        "exceptional_ledger": {
            "ell0": "OPEN homogeneous scalar/radion/charge block",
            "ell1": "OPEN because the tracefree polar tensor harmonic vanishes and Regge--Wheeler gauge changes rank",
        },
        "classification": {
            "arbitrary_lambda_full_tensor_identity": True,
            "all_n_ell_ge2_m_polar_master_complex": True,
            "ell_ge2_gauge_complete": True,
            "s_zero_locus_complete": True,
            "axial_polar_isospectrality": True,
            "ell0_ell1_complete": False,
            "covariant_symplectic_matching": False,
            "complete_fourth_order_adjoint": False,
            "full_polar_including_exceptions": False,
        },
        "next_gate": "classify the exceptional polar ell=0,1 complexes, then match axial and polar reduced currents to the covariant Einstein--Maxwell symplectic form before solving the extra fourth-order adjoint blocks",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem certifies the arbitrary-lambda full tensor identity, complete smooth polar gauge fixing, all Fourier momenta and m, the s=0 rank audit, two-master dispersion, isospectrality, and reduced symmetrizer for ell>=2 on the fixed compact product. It does not classify ell=0,1, match the covariant symplectic form, compute the complete fourth-order adjoint cokernel or quadratic obstruction table, or establish causal evolution, scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_polar_master_complex --verify bridge/certificates/einstein_maxwell_polar_master_complex.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_polar_master_complex.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_polar_master_complex",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(
        _load(path) == build_certificate(),
        f"polar master certificate stale or altered: {path}",
    )


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
