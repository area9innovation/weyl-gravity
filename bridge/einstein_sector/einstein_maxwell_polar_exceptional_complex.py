"""Exceptional ell=0,1 polar Einstein--Maxwell complexes."""

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
POLAR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json"
DOMAIN_CERTIFICATE = ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_polar_exceptional_complex.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_polar_exceptional_complex.schema.json"


class PolarExceptionalError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarExceptionalError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ell0_column(name: str) -> list[sp.Expr]:
    epsilon = sp.symbols("epsilon")
    time, space, theta, azimuth = sp.symbols("t x theta phi", real=True)
    frequency, momentum = sp.symbols("omega k", real=True)
    coordinates = (time, space, theta, azimuth)
    sine = sp.sin(theta)
    wave = sp.exp(sp.I * (momentum * space - frequency * time))
    metric = sp.diag(-1, 1, 1, sine**2)
    if name == "A":
        metric[0, 0] += epsilon * wave
    elif name == "B":
        metric[0, 1] = metric[1, 0] = epsilon * wave
    elif name == "C":
        metric[1, 1] += epsilon * wave
    elif name == "K":
        metric[2, 2] += epsilon * wave
        metric[3, 3] += epsilon * wave * sine**2
    else:
        raise PolarExceptionalError(f"unknown ell=0 column: {name}")
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
    ).applyfunc(
        lambda value: sp.factor(
            sp.trigsimp(sp.diff(value, epsilon).subs(epsilon, 0) / wave)
        )
    )
    trace = sp.factor((einstein[2, 2] + einstein[3, 3] / sine**2) / 2)
    expected_unlisted = sp.zeros(4)
    expected_unlisted[0, 0] = einstein[0, 0]
    expected_unlisted[0, 1] = expected_unlisted[1, 0] = einstein[0, 1]
    expected_unlisted[1, 1] = einstein[1, 1]
    expected_unlisted[2, 2] = trace
    expected_unlisted[3, 3] = sine**2 * trace
    _require(
        (einstein - expected_unlisted).applyfunc(sp.simplify) == sp.zeros(4),
        f"ell=0 unlisted tensor row changed: {name}",
    )
    return [einstein[0, 0], einstein[0, 1], einstein[1, 1], trace]


def _ell0_theorem() -> dict[str, Any]:
    frequency, momentum = sp.symbols("omega k", real=True)
    columns = [_ell0_column(name) for name in ("A", "B", "C", "K")]
    matrix = sp.Matrix(4, 4, lambda row, column: columns[column][row])
    expected = sp.Matrix(
        [
            [0, 0, 0, momentum**2],
            [0, 0, 0, -momentum * frequency],
            [0, 0, 0, frequency**2],
            [momentum**2 / 2, momentum * frequency, frequency**2 / 2, (frequency**2 - momentum**2 + 2) / 2],
        ]
    )
    _require((matrix - expected).applyfunc(sp.simplify) == sp.zeros(4), "ell=0 matrix changed")
    gauge = sp.Matrix(
        [
            [-2 * sp.I * frequency, 0],
            [sp.I * momentum, -sp.I * frequency],
            [0, 2 * sp.I * momentum],
            [0, 0],
        ]
    )
    _require((matrix * gauge).applyfunc(sp.simplify) == sp.zeros(4, 2), "ell=0 gauge image changed")
    k_minor = sp.factor(matrix[[0, 3], [3, 0]].det())
    omega_minor = sp.factor(matrix[[2, 3], [3, 2]].det())
    _require(k_minor == momentum**4 / 2, "ell=0 k-rank minor changed")
    _require(omega_minor == frequency**4 / 2, "ell=0 omega-rank minor changed")

    electric = sp.symbols("E")
    maxwell_rows = sp.Matrix([sp.I * momentum * electric, sp.I * frequency * electric])
    return {
        "variables": ["A", "B", "C", "K", "E_electric"],
        "absent_fixed_bundle_variable": "uniform magnetic delta F is excluded because the Chern class of P_N is fixed; X_a vanishes at ell=0",
        "Einstein_row_order": ["E00", "E01", "E11", "sphere_trace"],
        "Einstein_matrix": [[str(sp.factor(value)) for value in matrix.row(row)] for row in range(4)],
        "electric_Maxwell_rows": [str(value) for value in maxwell_rows],
        "gauge_parameters": ["xi_t", "xi_x"],
        "gauge_matrix": [[str(value) for value in gauge.row(row)] for row in range(4)],
        "nonzero_Fourier_rank_witnesses": {"k_nonzero": str(k_minor), "k_zero_omega_nonzero": str(omega_minor)},
        "nonzero_Fourier_quotient": "kernel(Einstein matrix)=image(periodic Diff) and E_electric=0; no local ell=0 propagating mode",
        "strict_zero_block": "K=0; affine-in-time periodic diffeomorphisms remove constant A,B; constant C is the global S1 circumference modulus; constant E is electric charge",
        "generalized_zero_frequency_equations": ["ddot K=0", "ddot C=2K", "dot E=0"],
        "generalized_zero_frequency_solution": ["K=a+b t", "C=a t^2+(b/3)t^3+c+d t", "E=Q_e"],
        "certified_radion_representative": "a=2,b=c=d=0 gives K=2,C=2t^2",
        "global_moduli": ["a,b radion Jordan pair", "c,d S1 circumference pair", "Q_e electric charge"],
    }


def _ell1_theorem() -> dict[str, Any]:
    frequency, momentum = sp.symbols("omega k", real=True)
    eigenvalue = sp.Integer(2)
    full = sp.Matrix(
        [
            [0, 0, eigenvalue / 2, momentum**2 + eigenvalue / 2, -eigenvalue],
            [0, eigenvalue / 2, 0, -momentum * frequency, 0],
            [eigenvalue / 2, 0, 0, frequency**2 - eigenvalue / 2, eigenvalue],
            [0, sp.I * momentum / 2, sp.I * frequency / 2, sp.I * frequency / 2, -sp.I * frequency],
            [sp.I * momentum / 2, sp.I * frequency / 2, 0, -sp.I * momentum / 2, sp.I * momentum],
            [(momentum**2 + eigenvalue / 2) / 2, momentum * frequency, (frequency**2 - eigenvalue / 2) / 2, (frequency**2 - momentum**2 + 2) / 2, -eigenvalue],
            [sp.Rational(1, 2), 0, -sp.Rational(1, 2), 1, frequency**2 - momentum**2 - eigenvalue],
        ]
    )
    gauge = sp.Matrix([2 * frequency**2, -2 * momentum * frequency, 2 * momentum**2, -2, -1])
    _require((full * gauge).applyfunc(sp.simplify) == sp.zeros(7, 1), "ell=1 residual gauge changed")
    quotient = full[:, [0, 1, 2, 4]]
    minors = []
    from itertools import combinations

    for rows in combinations(range(7), 4):
        determinant = sp.factor(quotient[list(rows), :].det())
        if determinant != 0:
            minors.append(determinant)
    common_factor = minors[0]
    for determinant in minors[1:]:
        common_factor = sp.gcd(common_factor, determinant)
    common_factor = sp.factor(common_factor)
    expected_characteristic = frequency**2 - momentum**2 - 4
    if sp.expand(common_factor + expected_characteristic) == 0:
        common_factor = -common_factor
    _require(
        sp.expand(common_factor - expected_characteristic) == 0,
        "ell=1 quotient characteristic changed",
    )
    physical = sp.Matrix([-2, 0, 2, 1])
    shell_image = (quotient * physical).applyfunc(
        lambda value: sp.factor(value.subs(frequency**2, momentum**2 + 4))
    )
    _require(shell_image == sp.zeros(7, 1), "ell=1 physical vector changed")
    theta = sp.symbols("theta", real=True)
    harmonic = sp.cos(theta)
    tracefree_theta = sp.simplify(sp.diff(harmonic, theta, 2) + harmonic)
    tracefree_phi = sp.simplify(sp.sin(theta) * sp.cos(theta) * sp.diff(harmonic, theta) + sp.sin(theta) ** 2 * harmonic)
    _require(tracefree_theta == 0 and tracefree_phi == 0, "ell=1 tracefree harmonic changed")
    return {
        "smooth_harmonic": "Y=cos(theta), lambda=2",
        "tracefree_tensor_harmonic": "identically zero; its equation row is absent",
        "post_hA_gauge_variables": ["A", "B", "C", "K", "U"],
        "residual_parameter": "xi with xi_A=-partial_A xi",
        "residual_gauge_vector": [str(value) for value in gauge],
        "gauge_invariant_master": "Psi=U-K/2",
        "algebraic_gauge": "K=0 fixes xi for every Fourier block, including omega=k=0",
        "quotient_characteristic": str(common_factor),
        "physical_dispersion": "omega^2=k_n^2+4",
        "K_zero_physical_vector_order_A_B_C_U": [str(value) for value in physical],
        "physical_reconstruction": "K=0: (A,B,C,U)=(-2Psi,0,2Psi,Psi)",
        "removed_zero_branch": "the s=0 eigenvector (K,U)=(2,1) is exactly the smooth residual diffeomorphism; no global exception remains because K shifts algebraically",
        "reduced_current_weight": "2 for Psi, inherited from the physical eigenvector before covariant normalization",
        "all_m_argument": "SO(3) equivariance carries the m=0 quotient to the full irreducible ell=1 triplet",
    }


def build_certificate() -> dict[str, Any]:
    polar = _load(POLAR_CERTIFICATE)
    domain = _load(DOMAIN_CERTIFICATE)
    _require(polar["result_id"] == "COMPACT_EM_POLAR_MASTER_COMPLEX", "polar input changed")
    _require(domain["result_id"] == "COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT", "domain input changed")
    return {
        "schema": "einstein-maxwell-polar-exceptional-complex-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPACT_EM_POLAR_EXCEPTIONAL_COMPLEX",
        "result_state": "ELL0_GLOBAL_MODULI_AND_ELL1_PHYSICAL_TRIPLET_CERTIFIED_SYMPLECTIC_AND_ADJOINT_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_POLAR_ALL_ELL_LINEAR_COMPLEX",
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": _sha256(Path(__file__)), "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in (POLAR_CERTIFICATE, DOMAIN_CERTIFICATE)}},
        "domain": "fixed-P_N compact product; smooth periodic identity-component gauge; all S1 momenta; exceptional polar ell=0,1; before residual quotient",
        "ell0_complex": _ell0_theorem(),
        "ell1_complex": _ell1_theorem(),
        "combined_interpretation": "The polar sector has no local ell=0 wave, but retains global radion/circumference Jordan data and electric charge at the homogeneous zero block. The ell=1 sector has one physical massive two-dimensional master for each m with omega^2=k_n^2+4; its apparent zero branch is gauge.",
        "classification": {"ell0_nonzero_fourier_quotient_complete": True, "ell0_generalized_zero_modes_complete": True, "fixed_bundle_magnetic_exclusion": True, "ell1_residual_quotient_complete": True, "ell1_all_n_m_physical_triplet": True, "all_polar_ell_linear_complex": True, "covariant_symplectic_matching": False, "complete_fourth_order_adjoint": False},
        "next_gate": "match the axial and complete polar reduced currents, including ell=1 and homogeneous global moduli, to the covariant Einstein--Maxwell presymplectic form; then solve the extra fourth-order adjoint blocks",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem completes the standard polar linear harmonic quotient on the fixed compact bundle by classifying ell=0 and ell=1. It does not normalize the covariant symplectic form, decide physical norm signs, compute the complete fourth-order adjoint cokernel or quadratic coefficient table, or establish causal evolution, scattering, or quantum theory.",
        "verification_commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_polar_exceptional_complex --verify bridge/certificates/einstein_maxwell_polar_exceptional_complex.json", "python3 bridge/einstein_sector/verify_einstein_maxwell_polar_exceptional_complex.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_polar_exceptional_complex"],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"exceptional certificate stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--verify", type=Path); args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
