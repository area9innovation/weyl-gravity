"""Certify the all-ell axial Weyl--Maxwell symplectic restriction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.schema.json"
CURRENT_ENGINE = ROOT / "bridge/einstein_sector/weyl_maxwell_lee_wald_current.py"
FIXTURE_GENERATOR = ROOT / "bridge/einstein_sector/weyl_maxwell_axial_arbitrary_lambda_fixture.py"
INPUTS = {
    "preflight": ROOT / "bridge/certificates/einstein_maxwell_weyl_symplectic_preflight.json",
    "axial_complex": ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json",
    "einstein_form": ROOT / "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json",
    "ell2_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_symplectic_restriction.json",
    "arbitrary_lambda_fixture": ROOT / "bridge/certificates/weyl_maxwell_axial_arbitrary_lambda_fixture.json",
}


class WeylAxialAllEllRestrictionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WeylAxialAllEllRestrictionError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _restriction_theorem(fixture: dict[str, Any]) -> dict[str, Any]:
    eigenvalue, mass = sp.symbols("lambda mu", positive=True)
    expected_weyl = sp.diag(
        eigenvalue * (3 * mass - 3 * eigenvalue + 1), sp.Integer(2)
    )
    matrix_locals = {"lam": eigenvalue, "mu": mass}
    stored_weyl = sp.Matrix(
        [
            [sp.sympify(value.replace("lambda", "lam"), locals=matrix_locals) for value in row]
            for row in fixture["current"]["coefficient_matrix_in_minus_i_omega_mu_N_convention"]
        ]
    )
    _require(stored_weyl == expected_weyl, "arbitrary-lambda Weyl coefficient matrix changed")
    einstein = sp.diag(eigenvalue, sp.Integer(2))

    branch_rows: list[dict[str, Any]] = []
    ratios: list[sp.Expr] = []
    for name, sign in (("plus", 1), ("minus", -1)):
        branch_mass = eigenvalue + sign * sp.sqrt(2 * eigenvalue)
        branch_vector = sp.Matrix([1, sign * sp.sqrt(eigenvalue / 2)])
        einstein_weight = sp.simplify((branch_vector.T * einstein * branch_vector)[0])
        weyl_weight = sp.simplify(
            (branch_vector.T * expected_weyl.subs(mass, branch_mass) * branch_vector)[0]
        )
        ratio = sp.simplify(weyl_weight / einstein_weight)
        expected_ratio = 1 + sign * sp.Rational(3, 2) * sp.sqrt(2 * eigenvalue)
        _require(sp.simplify(ratio - expected_ratio) == 0, f"{name} branch ratio changed")
        ratios.append(ratio)
        branch_rows.append(
            {
                "branch": name,
                "mu": str(branch_mass),
                "Q_over_H": str(sign * sp.sqrt(eigenvalue / 2)),
                "einstein_coefficient_weight": str(einstein_weight),
                "weyl_maxwell_coefficient_weight": str(weyl_weight),
                "restriction_over_einstein": str(ratio),
                "ell_ge_2_relative_sign": "POSITIVE" if sign == 1 else "NEGATIVE",
            }
        )

    ell2 = {eigenvalue: sp.Integer(6)}
    _require(
        [sp.simplify(value.subs(ell2)) for value in ratios]
        == [1 + 3 * sp.sqrt(3), 1 - 3 * sp.sqrt(3)],
        "ell=2 normalization ratios changed",
    )
    _require(
        sp.simplify(ratios[0] - ratios[1]) != 0,
        "the two arbitrary-lambda branch factors became equal",
    )

    lower_endpoint = sp.Integer(6)
    plus_lower = sp.simplify(ratios[0].subs(eigenvalue, lower_endpoint))
    minus_upper = sp.simplify(ratios[1].subs(eigenvalue, lower_endpoint))
    _require(plus_lower.is_positive is True, "plus lower-bound sign failed")
    _require(minus_upper.is_negative is True, "minus upper-bound sign failed")

    ell1_masses = [
        sp.simplify((eigenvalue + sign * sp.sqrt(2 * eigenvalue)).subs(eigenvalue, 2))
        for sign in (1, -1)
    ]
    _require(ell1_masses == [4, 0], "ell=1 dispersion control changed")

    return {
        "pairing_convention": "omega^t=-i*omega*mu*N_lambda*v_1^T G(lambda,mu) v_2, with N_lambda=integral_(S2)Y^2 dOmega>0",
        "einstein_maxwell_off_shell_coefficient_matrix": [
            ["lambda", "0"],
            ["0", "2"],
        ],
        "weyl_maxwell_off_shell_coefficient_matrix": [
            ["lambda*(3*mu-3*lambda+1)", "0"],
            ["0", "2"],
        ],
        "matrix_difference": [
            ["3*lambda*(mu-lambda)", "0"],
            ["0", "0"],
        ],
        "off_shell_weyl_determinant": str(sp.factor(expected_weyl.det())),
        "on_shell_branches": branch_rows,
        "branch_weight_matrix_relative_to_einstein": [
            [str(ratios[0]), "0"],
            ["0", str(ratios[1])],
        ],
        "ell_ge_2_proof": {
            "lambda_range": "lambda=ell*(ell+1)>=6",
            "mu_minus_positive": "lambda-sqrt(2*lambda)>0 because lambda>2",
            "plus_weight_sign": "1+(3/2)*sqrt(2*lambda)>0",
            "minus_weight_sign": "1-(3/2)*sqrt(2*lambda)<=1-3*sqrt(3)<0",
            "rank": 2,
            "signature_relative_to_positive_einstein_branch_form": {
                "positive": 1,
                "negative": 1,
                "zero": 0,
            },
            "single_universal_proportionality": False,
        },
        "ell1_consistency_control": {
            "lambda": 2,
            "formal_branch_masses": [str(value) for value in ell1_masses],
            "minus_curl_current": "0 because the common prefactor mu_minus vanishes",
            "quotient_scope": "for nonzero periodic momentum the mu=0 row is the certified axial ell=1 gauge branch; the n=0 global twist uses a different representative and is not computed by this curl fixture",
            "not_an_all_ell_physical_claim": True,
        },
        "branch_orthogonality": "for ell>=2 the Lee-Wald current is conserved for any pair of linearized solutions; at fixed k the distinct positive frequencies force the cross-branch pairing to vanish by time-translation covariance",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _require(
        records["preflight"]["classification"]["induced_linear_tangent_quotient_map_injective"] is True,
        "quotient-injectivity input changed",
    )
    _require(
        records["einstein_form"]["classification"]["covariant_Lee_Wald_integrated_matching"] is True,
        "Einstein reference form input changed",
    )
    _require(
        records["ell2_restriction"]["classification"]["axial_ell2_restriction_nondegenerate"] is True,
        "ell=2 restriction control changed",
    )
    fixture = records["arbitrary_lambda_fixture"]
    _require(
        fixture["result_id"] == "WEYL_MAXWELL_AXIAL_ARBITRARY_LAMBDA_FIXTURE",
        "direct arbitrary-lambda fixture changed",
    )
    _require(
        fixture["current"]["ode_plus_total_derivative_remainder"] == "0",
        "harmonic reduction witness changed",
    )
    _require(
        fixture["current"]["ell2_normalization_remainder"] == "0",
        "ell=2 normalization control changed",
    )
    theorem = _restriction_theorem(fixture)
    return {
        "schema": "einstein-maxwell-weyl-axial-all-ell-symplectic-restriction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_ALL_ELL_SYMPLECTIC_RESTRICTION",
        "result_state": "AXIAL_ALL_ELL_GE2_NONDEGENERATE_BRANCH_DEPENDENT_INDEFINITE_RESTRICTION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_AXIAL_ALL_ELL_GE2_SYMBOLIC_K",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
            "direct_implementation": {
                "current_engine": {
                    "path": str(CURRENT_ENGINE.relative_to(ROOT)),
                    "sha256": _sha256(CURRENT_ENGINE),
                },
                "fixture_generator": {
                    "path": str(FIXTURE_GENERATOR.relative_to(ROOT)),
                    "sha256": _sha256(FIXTURE_GENERATOR),
                },
            },
        },
        "domain": "all standard axial Einstein-Maxwell radiative harmonics lambda=ell(ell+1), ell>=2, all m by spherical symmetry, arbitrary periodic S1 momentum k, both physical master branches, before final residual SO(4,2) quotient",
        "derivation": {
            "harmonic_method": "direct arbitrary Y(theta), exact reduction by Y''+cot(theta)Y'+lambda Y=0, and a certified total-derivative primitive",
            "interpolation_used": False,
            "literal_action": "S_WM=int sqrt(-g)[(3/8)C^2-F^2/4]",
            "representative": "(h_A,q_A)=epsilon_A^B partial_B(H,Q) in Regge-Wheeler/Maxwell-angular gauge",
            "pole_rule": "regular spherical harmonics make the displayed primitive vanish at theta=0,pi",
        },
        "restriction": theorem,
        "classification": {
            "all_axial_ell_ge2_restriction_computed": True,
            "all_axial_ell_ge2_both_branches_nonnull": True,
            "all_axial_ell_ge2_restriction_nondegenerate": True,
            "all_axial_ell_ge2_relative_branch_form_indefinite": True,
            "single_universal_proportionality_to_einstein_form": False,
            "target_weyl_gauge_removes_einstein_class": False,
            "physical_ell1_and_global_twist_restriction_computed": False,
            "polar_restriction_computed": False,
            "homogeneous_restriction_computed": False,
            "complete_fourth_order_weyl_maxwell_phase_space_classified": False,
            "nonlinear_solution_embedding_certified": False,
            "final_residual_quotient_computed": False,
            "lorentzian_causal_or_scattering_theorem": False,
        },
        "interpretation": "Every ordinary axial Einstein-Maxwell wave with ell>=2 remains nonnull in the literal Weyl-Maxwell presymplectic restriction, but the plus and minus master branches carry exact relative weights 1+(3/2)*sqrt(2*lambda) and 1-(3/2)*sqrt(2*lambda). Their opposite signs persist for every ell>=2. Thus the axial Einstein tangent sector embeds linearly and symplectically as a nondegenerate subspace, but not as a positive or universally rescaled copy of the Einstein-Maxwell phase space.",
        "next_gate": "compute the polar all-ell restriction, then treat the physical ell=1, homogeneous ell=0, and axial-twist global blocks with their certified quotient representatives",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem covers the complete standard axial ell>=2 Einstein-Maxwell tangent block at symbolic periodic momentum and all spherical m by symmetry. The ell=1 calculation is only a common curl/gauge degeneration check. It does not compute the physical ell=1 or global twist pairing, polar or homogeneous blocks, extra fourth-order Weyl-Maxwell modes, nonlinear closure, final SO(4,2) reduction, causal scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_all_ell_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_all_ell_symplectic_restriction",
            "python3 -m bridge.einstein_sector.weyl_maxwell_axial_arbitrary_lambda_fixture --verify bridge/certificates/weyl_maxwell_axial_arbitrary_lambda_fixture.json",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale all-ell axial restriction certificate: {path}")


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
