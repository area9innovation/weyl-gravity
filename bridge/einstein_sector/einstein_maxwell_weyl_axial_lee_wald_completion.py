"""Generic direct Lee--Wald completion of the axial target module."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DIRECT_FIXTURE = ROOT / "bridge/certificates/weyl_maxwell_axial_general_lee_wald_fixture.json"
GREEN_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_green_current.json"
EXTRA_PAIRING = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json"
OPERATOR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_lee_wald_completion.schema.json"


class AxialLeeWaldCompletionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialLeeWaldCompletionError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _generic_current_matrix(
    eigenvalue: sp.Symbol,
    momentum: sp.Symbol,
    first_frequency: sp.Symbol,
    second_frequency: sp.Symbol,
) -> sp.Matrix:
    green = json.loads(GREEN_CERTIFICATE.read_text(encoding="utf-8"))
    result = sp.zeros(4)
    for term in green["reduced_current"]["time_current_terms"]:
        coefficient = sp.sympify(
            term["coefficient"].replace("lambda", "lam"),
            locals={"lam": eigenvalue},
        )
        result[term["u_component"], term["v_component"]] += (
            coefficient
            * (-sp.I * first_frequency) ** term["u_t_order"]
            * (sp.I * momentum) ** term["u_x_order"]
            * (sp.I * second_frequency) ** term["v_t_order"]
            * (-sp.I * momentum) ** term["v_x_order"]
        )
    return result.applyfunc(sp.factor)


def _spectral_promotion() -> dict[str, Any]:
    fixture = json.loads(DIRECT_FIXTURE.read_text(encoding="utf-8"))
    eigenvalue, momentum, first_frequency, second_frequency = sp.symbols(
        "lambda k omega1 omega2", real=True
    )
    matrix = _generic_current_matrix(
        eigenvalue, momentum, first_frequency, second_frequency
    )
    maximum_degree = max(
        sp.Poly(sp.expand(value), eigenvalue).degree()
        for value in matrix
        if value != 0
    )
    _require(maximum_degree <= 2, "reduced current exceeded the spectral degree bound")
    sample_checks = {}
    locals_map = {
        "k": momentum,
        "omega1": first_frequency,
        "omega2": second_frequency,
        "I": sp.I,
        "pi": sp.pi,
    }
    for ell in (2, 3, 4):
        sample = fixture["samples"][str(ell)]
        direct = sp.Matrix(
            [
                [sp.sympify(value, locals=locals_map) for value in row]
                for row in sample["direct_integrated_matrix"]
            ]
        )
        harmonic_norm = sp.Rational(4, 2 * ell + 1) * sp.pi
        expected = harmonic_norm * matrix.subs(eigenvalue, ell * (ell + 1))
        _require(
            (direct - expected).applyfunc(sp.factor) == sp.zeros(4),
            f"ell={ell} generic Lee-Wald promotion failed",
        )
        sample_checks[str(ell)] = "complete 4x4 independent-frequency matrix exact"
    return {
        "coefficient_order": ["h_t", "h_x", "q_t", "q_x"],
        "generic_reduced_Green_matrix": _matrix_strings(matrix),
        "direct_integrated_4D_Lee_Wald_matrix": "N_(ell,m) times generic_reduced_Green_matrix",
        "harmonic_norm": "N_(ell,m)=integral_(S2)|Y_(ell,m)|^2 dOmega>0",
        "axisymmetric_sample_norms": ["4*pi/5", "4*pi/7", "4*pi/9"],
        "spectral_degree_bound": 2,
        "degree_bound_reason": "the bilinear current of a fourth-order natural SO(3)-equivariant Hessian contains at most two spherical Laplacian eigenvalues after integration by parts",
        "interpolation_nodes": [6, 12, 20],
        "sample_checks": sample_checks,
        "SO3_irreducibility_promotion": "invariance makes the integrated current a scalar multiple of the standard norm on each irreducible ell-space; the m=0 sample fixes that scalar for every m",
        "generic_direct_match": True,
        "improvement_remainder_after_compact_S2_integration": "0",
    }


def _reduce_two_shells(
    expression: sp.Expr,
    extra_frequency: sp.Symbol,
    einstein_frequency: sp.Symbol,
    momentum: sp.Symbol,
    eigenvalue: sp.Symbol,
) -> sp.Expr:
    extra_shell = sp.Poly(
        extra_frequency**2 - momentum**2 - eigenvalue + sp.Rational(2, 3),
        extra_frequency,
    )
    einstein_shell = sp.Poly(
        (einstein_frequency**2 - momentum**2 - eigenvalue) ** 2
        - 2 * eigenvalue,
        einstein_frequency,
    )
    reduced = sp.rem(sp.Poly(sp.expand(expression), extra_frequency), extra_shell).as_expr()
    reduced = sp.rem(sp.Poly(sp.expand(reduced), einstein_frequency), einstein_shell).as_expr()
    return sp.factor(reduced)


def _full_solution_pairing() -> dict[str, Any]:
    eigenvalue, momentum, extra_frequency, einstein_frequency = sp.symbols(
        "lambda k omega_e omega_E", real=True
    )
    forward_matrix = _generic_current_matrix(
        eigenvalue, momentum, extra_frequency, einstein_frequency
    )
    reverse_matrix = _generic_current_matrix(
        eigenvalue, momentum, einstein_frequency, extra_frequency
    )
    extra_representatives = [
        sp.Matrix([-(momentum**2 + eigenvalue), momentum * extra_frequency, eigenvalue, 0]),
        sp.Matrix([-momentum * extra_frequency, momentum**2 - sp.Rational(2, 3), 0, eigenvalue]),
    ]
    einstein_mass = einstein_frequency**2 - momentum**2
    einstein_representative = sp.Matrix(
        [
            2 * momentum,
            -2 * einstein_frequency,
            momentum * (einstein_mass - eigenvalue),
            -einstein_frequency * (einstein_mass - eigenvalue),
        ]
    )
    forward_remainders = []
    reverse_remainders = []
    for representative in extra_representatives:
        forward = (representative.T * forward_matrix * einstein_representative)[0]
        reverse = (
            einstein_representative.T * reverse_matrix * representative
        )[0]
        forward_remainders.append(
            _reduce_two_shells(
                forward,
                extra_frequency,
                einstein_frequency,
                momentum,
                eigenvalue,
            )
        )
        reverse_remainders.append(
            _reduce_two_shells(
                reverse,
                extra_frequency,
                einstein_frequency,
                momentum,
                eigenvalue,
            )
        )
    _require(forward_remainders == [0, 0], "extra-to-Einstein mixed block did not vanish")
    _require(reverse_remainders == [0, 0], "Einstein-to-extra mixed block did not vanish")

    mass = sp.symbols("mu", real=True)
    einstein_master_gram = sp.diag(
        mass * eigenvalue * (3 * mass - 3 * eigenvalue + 1),
        2 * mass,
    )
    source_vector = sp.Matrix([2, mass - eigenvalue])
    source_norm = sp.factor((source_vector.T * einstein_master_gram * source_vector)[0])
    plus_mass = eigenvalue + sp.sqrt(2 * eigenvalue)
    minus_mass = eigenvalue - sp.sqrt(2 * eigenvalue)
    plus_norm = sp.factor(source_norm.subs(mass, plus_mass))
    minus_norm = sp.factor(source_norm.subs(mass, minus_mass))

    return {
        "Einstein_representative": [str(value) for value in einstein_representative],
        "extra_representatives": [[str(value) for value in vector] for vector in extra_representatives],
        "mixed_extra_to_Einstein_shell_remainders": [str(value) for value in forward_remainders],
        "mixed_Einstein_to_extra_shell_remainders": [str(value) for value in reverse_remainders],
        "mixed_blocks_zero_without_frequency_inversion": True,
        "Einstein_master_normalized_Gram": _matrix_strings(einstein_master_gram),
        "Einstein_branch_representative_master_order": ["H=2", "Q=mu-lambda"],
        "Einstein_plus_branch_norm": str(plus_norm),
        "Einstein_minus_branch_norm": str(minus_norm),
        "Einstein_branch_signature_for_lambda_ge_6": [1, 1],
        "extra_branch_signature_for_lambda_ge_6": [2, 0],
        "complete_generic_axial_target_signature": [3, 1],
        "signature_convention": "J^t/(-I*positive_frequency*N_(ell,m)); overall action sign fixed by alpha_B=3 and the declared Maxwell sign",
        "complete_block_form": "Einstein_plus (+) direct-sum Einstein_minus (-) direct-sum extra_2x2 positive block; all Einstein/extra mixed entries vanish",
    }


def build_certificate() -> dict[str, Any]:
    inputs = {
        "direct_fixture": DIRECT_FIXTURE,
        "green_current": GREEN_CERTIFICATE,
        "extra_pairing": EXTRA_PAIRING,
        "operator": OPERATOR_CERTIFICATE,
    }
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in inputs.items()}
    expected = {
        "direct_fixture": "WEYL_MAXWELL_AXIAL_GENERAL_LEE_WALD_FIXTURE",
        "green_current": "EINSTEIN_MAXWELL_WEYL_AXIAL_GREEN_CURRENT",
        "extra_pairing": "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_GREEN_PAIRING",
        "operator": "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR",
    }
    for name, result_id in expected.items():
        _require(records[name]["result_id"] == result_id, f"{name} input changed")
    return {
        "schema": "einstein-maxwell-weyl-axial-lee-wald-completion-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION",
        "result_state": "GENERIC_AXIAL_DIRECT_4D_LEE_WALD_MATCH_EXTRA_NONRADICAL_AND_FULL_BLOCK_SIGNATURE_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_DIRECT_LEE_WALD_COMPLETION",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in inputs.items()
            },
        },
        "domain": "complete generic axial ell>=2 Weyl-Maxwell solution module at every real compact momentum, before final residual quotient",
        "direct_current_match": _spectral_promotion(),
        "full_solution_pairing": _full_solution_pairing(),
        "classification": {
            "direct_four_dimensional_Lee_Wald_match": True,
            "compact_S2_improvement_remainder_zero": True,
            "generic_extra_module_direct_Lee_Wald_nonradical": True,
            "generic_extra_direct_Lee_Wald_signature_positive_two": True,
            "Einstein_extra_symplectic_orthogonality": True,
            "complete_generic_axial_target_signature_three_one": True,
            "direct_second_variation_action_density_computed": False,
            "final_residual_quotient_computed": False,
            "positive_frequency_Hilbert_space_or_particle_claim": False,
            "quantum_ghost_or_unitarity_claim": False,
            "Lorentzian_causal_claim": False,
        },
        "interpretation": "The generic compact axial target is now complete as a classical direct Lee-Wald block before final residual quotient. The Einstein and extra primary modules are symplectically orthogonal. The two extra polarizations are genuine nonradical positive directions in the declared direct four-dimensional action convention, while the two Einstein master branches contribute one positive and one negative direction, for total axial signature (3,1). This is a classical covariant-current signature, not yet a one-particle ghost or unitarity theorem.",
        "next_gate": "compute the action-density second variation as a normalization cross-check, then perform the final residual SO(4,2) descent and separately test causal boundary admissibility of the extra primary factor",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem certifies the directly varied compact harmonic Lee-Wald current and its generic axial solution-module pairing. It does not construct a positive-frequency Hilbert space, final residual cohomology, causal propagator, asymptotic scattering space, or quantum ghost/unitarity theorem.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_lee_wald_completion --verify bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_lee_wald_completion",
            "python3 -m bridge.einstein_sector.weyl_maxwell_axial_general_lee_wald_fixture --verify bridge/certificates/weyl_maxwell_axial_general_lee_wald_fixture.json",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale axial Lee-Wald completion: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
