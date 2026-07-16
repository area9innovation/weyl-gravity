"""Certify the all-ell polar Weyl--Maxwell symplectic restriction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.schema.json"
CURRENT_ENGINE = ROOT / "bridge/einstein_sector/weyl_maxwell_lee_wald_current.py"
NORMAL_FORM_ENGINE = ROOT / "bridge/einstein_sector/quadratic_harmonic_density.py"
FIXTURE_GENERATOR = ROOT / "bridge/einstein_sector/weyl_maxwell_polar_arbitrary_lambda_fixture.py"
INPUTS = {
    "preflight": ROOT / "bridge/certificates/einstein_maxwell_weyl_symplectic_preflight.json",
    "polar_complex": ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json",
    "einstein_form": ROOT / "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json",
    "axial_all_ell": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.json",
    "arbitrary_lambda_fixture": ROOT / "bridge/certificates/weyl_maxwell_polar_arbitrary_lambda_fixture.json",
}


class WeylPolarAllEllRestrictionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WeylPolarAllEllRestrictionError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse(value: str, eigenvalue: sp.Symbol, mass: sp.Symbol) -> sp.Expr:
    return sp.sympify(
        value.replace("lambda", "lam"), locals={"lam": eigenvalue, "mu": mass}
    )


def _restriction_theorem(
    fixture: dict[str, Any],
    polar: dict[str, Any],
    einstein_record: dict[str, Any],
    axial: dict[str, Any],
) -> dict[str, Any]:
    eigenvalue, mass = sp.symbols("lambda mu", positive=True)
    expected_weyl = sp.Matrix(
        [
            [4 * (mass - eigenvalue), 5 * eigenvalue - 4 * mass],
            [5 * eigenvalue - 4 * mass, 4 * (mass - eigenvalue)],
        ]
    )
    stored_weyl = sp.Matrix(
        [
            [_parse(value, eigenvalue, mass) for value in row]
            for row in fixture["current"]["coefficient_matrix"]
        ]
    )
    _require(stored_weyl == expected_weyl, "arbitrary-lambda polar matrix changed")
    einstein = sp.Matrix([[1, -2], [-2, 2 * eigenvalue]])
    stored_einstein = sp.Matrix(
        [
            [_parse(value, eigenvalue, mass) for value in row]
            for row in einstein_record["master_matching"]["action_normalized_matrices_without_N_over_2"]["polar"]
        ]
    )
    _require(stored_einstein == einstein, "Einstein polar reference form changed")
    _require(
        polar["algebraic_and_singular_audit"]["master_matrix"]
        == [["lambda", "-2*lambda"], ["-1", "lambda"]],
        "polar master matrix changed",
    )

    root = sp.sqrt(2 * eigenvalue)
    branch_rows: list[dict[str, Any]] = []
    ratios: list[sp.Expr] = []
    for name, sign in (("plus", 1), ("minus", -1)):
        branch_mass = eigenvalue + sign * root
        branch_vector = sp.Matrix([1, -sign / root])
        einstein_weight = sp.factor((branch_vector.T * einstein * branch_vector)[0])
        weyl_weight = sp.factor(
            (branch_vector.T * expected_weyl.subs(mass, branch_mass) * branch_vector)[0]
        )
        ratio = sp.factor(weyl_weight / einstein_weight)
        expected_ratio = 1 + sign * sp.Rational(3, 2) * root
        _require(sp.simplify(ratio - expected_ratio) == 0, f"{name} polar ratio changed")
        expected_einstein_weight = 2 * (root + 2 * sign) / root
        expected_weyl_weight = (
            sign * (root + 2 * sign) * (3 * root + 2 * sign) / root
        )
        _require(
            sp.simplify(einstein_weight - expected_einstein_weight) == 0,
            f"{name} Einstein weight changed",
        )
        _require(
            sp.simplify(weyl_weight - expected_weyl_weight) == 0,
            f"{name} Weyl-Maxwell weight changed",
        )
        ratio = sp.expand(expected_ratio)
        ratios.append(ratio)
        branch_rows.append(
            {
                "branch": name,
                "mu": str(branch_mass),
                "normalized_vector_K_U": ["1", str(-sign / root)],
                "einstein_weight": str(sp.factor(expected_einstein_weight)),
                "weyl_maxwell_weight": str(sp.factor(expected_weyl_weight)),
                "restriction_over_einstein": str(ratio),
                "ell_ge_2_relative_sign": "POSITIVE" if sign == 1 else "NEGATIVE",
            }
        )

    axial_ratios = [
        _parse(row["restriction_over_einstein"], eigenvalue, mass)
        for row in axial["restriction"]["on_shell_branches"]
    ]
    _require(
        all(sp.simplify(left - right) == 0 for left, right in zip(ratios, axial_ratios, strict=True)),
        "axial-polar on-shell restriction factors no longer match",
    )
    determinant = sp.factor(expected_weyl.det())
    _require(
        sp.simplify(determinant - eigenvalue * (8 * mass - 9 * eigenvalue)) == 0,
        "off-shell determinant changed",
    )

    return {
        "pairing_convention": "omega_P^t=-i*omega*N_lambda*v_1^T G_P(lambda,mu) v_2",
        "einstein_maxwell_off_shell_matrix": [["1", "-2"], ["-2", "2*lambda"]],
        "weyl_maxwell_off_shell_matrix": [
            ["4*(mu-lambda)", "5*lambda-4*mu"],
            ["5*lambda-4*mu", "4*(mu-lambda)"],
        ],
        "off_shell_weyl_determinant": str(determinant),
        "on_shell_branches": branch_rows,
        "branch_weight_matrix_relative_to_einstein": [
            [str(ratios[0]), "0"],
            ["0", str(ratios[1])],
        ],
        "ell_ge_2_proof": {
            "root_variable": "a=sqrt(2*lambda)>2 because lambda>=6",
            "einstein_plus_weight": "2*(a+2)/a>0",
            "einstein_minus_weight": "2*(a-2)/a>0",
            "weyl_plus_weight": "(a+2)*(3*a+2)/a>0",
            "weyl_minus_weight": "-(a-2)*(3*a-2)/a<0",
            "rank": 2,
            "signature_relative_to_positive_einstein_branch_form": {
                "positive": 1,
                "negative": 1,
                "zero": 0,
            },
        },
        "parity_comparison": {
            "axial_and_polar_on_shell_relative_factors_equal": True,
            "common_factors": [str(ratios[0]), str(ratios[1])],
            "off_shell_matrices_equal": False,
            "interpretation": "axial-polar isospectrality extends to the two on-shell Weyl-Maxwell/Einstein-Maxwell relative weights, although the off-shell coefficient matrices and reconstruction maps differ",
        },
        "mu_zero_closure": {
            "reconstructed_fixture_domain": "mu!=0",
            "imported_rank_witness": polar["algebraic_and_singular_audit"]["s_zero_minor"],
            "verdict": "for lambda>=6 the gauge-fixed mu=0 coefficient matrix has full column rank, so only the zero field exists and no nonzero polar solution is omitted",
        },
        "branch_orthogonality": "for ell>=2 the conserved Lee-Wald current and distinct positive branch frequencies force the cross-branch pairing to vanish at fixed k",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _require(
        records["preflight"]["classification"]["induced_linear_tangent_quotient_map_injective"] is True,
        "quotient-injectivity input changed",
    )
    _require(
        records["polar_complex"]["classification"]["all_n_ell_ge2_m_polar_master_complex"] is True,
        "polar complex input changed",
    )
    fixture = records["arbitrary_lambda_fixture"]
    _require(fixture["current"]["normal_form_remainder"] == "0", "normal-form witness changed")
    _require(fixture["current"]["ell2_normalization_remainder"] == "0", "ell=2 control changed")
    restriction = _restriction_theorem(
        fixture,
        records["polar_complex"],
        records["einstein_form"],
        records["axial_all_ell"],
    )
    return {
        "schema": "einstein-maxwell-weyl-polar-all-ell-symplectic-restriction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_POLAR_ALL_ELL_SYMPLECTIC_RESTRICTION",
        "result_state": "POLAR_ALL_ELL_GE2_NONDEGENERATE_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_POLAR_ALL_ELL_GE2_SYMBOLIC_K",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
            "direct_implementation": {
                "current_engine": {"path": str(CURRENT_ENGINE.relative_to(ROOT)), "sha256": _sha256(CURRENT_ENGINE)},
                "normal_form_engine": {"path": str(NORMAL_FORM_ENGINE.relative_to(ROOT)), "sha256": _sha256(NORMAL_FORM_ENGINE)},
                "fixture_generator": {"path": str(FIXTURE_GENERATOR.relative_to(ROOT)), "sha256": _sha256(FIXTURE_GENERATOR)},
            },
        },
        "domain": "all standard polar Einstein-Maxwell radiative harmonics lambda=ell(ell+1), ell>=2, all m by spherical symmetry, arbitrary periodic S1 momentum k, both physical branches, before final residual SO(4,2) quotient",
        "derivation": {
            "harmonic_method": "direct arbitrary Y(theta), harmonic ODE, and a coefficientwise solved pole-vanishing quadratic primitive in z=cos(theta)",
            "interpolation_used": False,
            "literal_action": "S_WM=int sqrt(-g)[(3/8)C^2-F^2/4]",
            "bilinear_amplitudes": "independent (K1,U1) and (K2,U2), retaining the full off-diagonal entry",
            "mu_zero_rule": "the 1/mu reconstruction is used only for mu!=0; the independent full-rank mu=0 audit closes the omitted locus",
        },
        "restriction": restriction,
        "classification": {
            "all_polar_ell_ge2_restriction_computed": True,
            "all_polar_ell_ge2_both_branches_nonnull": True,
            "all_polar_ell_ge2_restriction_nondegenerate": True,
            "all_polar_ell_ge2_relative_branch_form_indefinite": True,
            "axial_polar_on_shell_relative_weights_equal": True,
            "single_universal_proportionality_to_einstein_form": False,
            "target_weyl_gauge_removes_einstein_class": False,
            "physical_ell1_and_global_restriction_computed": False,
            "homogeneous_restriction_computed": False,
            "complete_fourth_order_weyl_maxwell_phase_space_classified": False,
            "nonlinear_solution_embedding_certified": False,
            "final_residual_quotient_computed": False,
            "lorentzian_causal_or_scattering_theorem": False,
        },
        "interpretation": "Every ordinary polar Einstein-Maxwell wave with ell>=2 remains nonnull in the literal Weyl-Maxwell restriction. The target form restricted along the linear inclusion is nondegenerate but indefinite, with the same two relative branch factors as the axial parity. This is not a symplectic embedding of the Einstein-Maxwell form: the off-shell matrices differ and the on-shell factors are branch dependent.",
        "next_gate": "combine axial and polar radiative blocks into one standard-wave restriction theorem, then compute the physical ell=1, homogeneous ell=0, and axial-twist global restrictions",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem covers the complete standard polar ell>=2 Einstein-Maxwell tangent block at symbolic periodic momentum and all m by symmetry, including closure of the mu=0 locus. It does not compute physical ell=1 or global pairings, extra fourth-order Weyl-Maxwell modes, nonlinear closure, final SO(4,2) reduction, causal scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_all_ell_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_all_ell_symplectic_restriction bridge.einstein_sector.tests.test_quadratic_harmonic_density",
            "python3 -m bridge.einstein_sector.weyl_maxwell_polar_arbitrary_lambda_fixture --verify bridge/certificates/weyl_maxwell_polar_arbitrary_lambda_fixture.json",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale all-ell polar restriction certificate: {path}")


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
