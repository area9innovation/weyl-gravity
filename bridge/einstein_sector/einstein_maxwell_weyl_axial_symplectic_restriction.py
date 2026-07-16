"""Certify the symbolic-k axial ell=2 Weyl--Maxwell restriction kill test."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_symplectic_restriction.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_symplectic_restriction.schema.json"
CURRENT_ENGINE = ROOT / "bridge/einstein_sector/weyl_maxwell_lee_wald_current.py"
FIXTURE_GENERATOR = ROOT / "bridge/einstein_sector/weyl_maxwell_axial_lee_wald_fixture.py"
INPUTS = {
    "preflight": ROOT / "bridge/certificates/einstein_maxwell_weyl_symplectic_preflight.json",
    "axial_complex": ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json",
    "einstein_form": ROOT / "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json",
    "direct_fixture": ROOT / "bridge/certificates/weyl_maxwell_axial_lee_wald_fixture.json",
}


class WeylAxialRestrictionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WeylAxialRestrictionError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _branch_reduction(fixture: dict[str, Any]) -> dict[str, Any]:
    momentum, frequency, metric_master, maxwell_master = sp.symbols(
        "k omega H Q", real=True
    )
    locals_map = {
        "k": momentum,
        "omega": frequency,
        "H": metric_master,
        "Q": maxwell_master,
        "I": sp.I,
        "pi": sp.pi,
    }
    einstein = sp.sympify(
        fixture["axial_ell2"]["einstein_integrated_coordinate_current"],
        locals=locals_map,
    )
    weyl = sp.sympify(
        fixture["axial_ell2"]["weyl_maxwell_integrated_coordinate_current"],
        locals=locals_map,
    )
    expected_einstein = (
        8
        * sp.I
        * sp.pi
        * frequency
        * (3 * metric_master**2 + maxwell_master**2)
        * (momentum**2 - frequency**2)
        / 5
    )
    expected_weyl = (
        -8
        * sp.I
        * sp.pi
        * frequency
        * (momentum**2 - frequency**2)
        * (
            9 * metric_master**2 * momentum**2
            - 9 * metric_master**2 * frequency**2
            + 51 * metric_master**2
            - maxwell_master**2
        )
        / 5
    )
    _require(sp.simplify(einstein - expected_einstein) == 0, "Einstein fixture current changed")
    _require(sp.simplify(weyl - expected_weyl) == 0, "Weyl fixture current changed")

    branch_rows = []
    ratios = []
    for name, sign in (("plus", 1), ("minus", -1)):
        mass = 6 + sign * 2 * sp.sqrt(3)
        branch_vector = {maxwell_master: sign * sp.sqrt(3) * metric_master}
        einstein_branch = sp.factor(
            sp.expand(einstein.subs(branch_vector)).subs(
                momentum**2, frequency**2 - mass
            )
        )
        weyl_branch = sp.factor(
            sp.expand(weyl.subs(branch_vector)).subs(
                momentum**2, frequency**2 - mass
            )
        )
        ratio = sp.simplify(weyl_branch / einstein_branch)
        expected_ratio = 1 + sign * 3 * sp.sqrt(3)
        _require(sp.simplify(ratio - expected_ratio) == 0, f"{name} branch ratio changed")
        _require(ratio != 0, f"{name} branch restriction became null")
        ratios.append(ratio)
        branch_rows.append(
            {
                "branch": name,
                "mass_squared": str(mass),
                "Q_over_H": str(sign * sp.sqrt(3)),
                "einstein_coordinate_current": str(einstein_branch),
                "weyl_maxwell_coordinate_current": str(weyl_branch),
                "restriction_over_einstein": str(ratio),
                "relative_sign": "POSITIVE" if sign == 1 else "NEGATIVE",
            }
        )
    _require(sp.simplify(ratios[0] - ratios[1]) != 0, "two branches became proportional")
    _require(ratios[0].is_positive is True, "plus ratio lost positivity")
    _require(ratios[1].is_negative is True, "minus ratio lost negativity")
    return {
        "off_shell_integrated_coordinate_currents": {
            "einstein_maxwell": str(sp.factor(einstein)),
            "weyl_maxwell": str(sp.factor(weyl)),
        },
        "on_shell_branches": branch_rows,
        "branch_orthogonality": "the Lee-Wald current is conserved for any pair of linearized solutions; at fixed k the distinct positive frequencies omega_+!=omega_- force the cross-branch pairing to vanish by time-translation covariance",
        "branch_weight_matrix_relative_to_einstein": [
            [str(ratios[0]), "0"],
            ["0", str(ratios[1])],
        ],
        "rank": 2,
        "signature_relative_to_positive_einstein_branch_form": {
            "positive": 1,
            "negative": 1,
            "zero": 0,
        },
        "universal_scalar_multiple_exists": False,
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _require(
        records["preflight"]["classification"]["induced_linear_tangent_quotient_map_injective"] is True,
        "quotient-injectivity input changed",
    )
    _require(
        records["preflight"]["classification"]["weyl_maxwell_symplectic_restriction_computed"] is False,
        "preflight claim boundary changed",
    )
    _require(
        records["axial_complex"]["ell_ge_2_theorem"]["branches"]
        == [
            {"name": "plus", "Q_over_H": "sqrt(lambda/2)", "omega_squared": "k_n^2+lambda+sqrt(2*lambda)"},
            {"name": "minus", "Q_over_H": "-sqrt(lambda/2)", "omega_squared": "k_n^2+lambda-sqrt(2*lambda)"},
        ],
        "axial branch input changed",
    )
    _require(
        records["einstein_form"]["classification"]["covariant_Lee_Wald_integrated_matching"] is True,
        "Einstein reference form input changed",
    )
    fixture = records["direct_fixture"]
    _require(fixture["result_id"] == "WEYL_MAXWELL_AXIAL_LEE_WALD_FIXTURE", "direct fixture changed")
    _require(fixture["background_bach_orthonormal"] == [["1/6", "0", "0", "0"], ["0", "-1/6", "0", "0"], ["0", "0", "1/6", "0"], ["0", "0", "0", "1/6"]], "Bach convention control changed")
    _require(fixture["flat_tt_control"]["restricted_value"] == "0", "flat TT control changed")
    _require(fixture["pure_weyl_gauge_control"]["pointwise_current"] == "0", "Weyl gauge control changed")
    _require(fixture["axial_ell2"]["einstein_curvature_momentum_pointwise_remainder"] == "0", "Einstein current normalization control changed")
    restriction = _branch_reduction(fixture)
    return {
        "schema": "einstein-maxwell-weyl-axial-symplectic-restriction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_SYMPLECTIC_RESTRICTION",
        "result_state": "AXIAL_ELL2_SYMBOLIC_K_NONDEGENERATE_BRANCH_DEPENDENT_RESTRICTION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_AXIAL_ELL2_SYMBOLIC_K_KILL_TEST",
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
        "domain": "axial ell=2,m=0 Einstein-Maxwell radiative tangent at arbitrary periodic S1 momentum k on the fixed-P_N product background; both physical master branches; before final residual SO(4,2) quotient",
        "current_derivation": {
            "weyl_action": "S_WM=int sqrt(-g)[(alpha_B/8)C^2-F^2/4] with alpha_B=3",
            "curvature_momentum": "P^abcd=(alpha_B/4)C^abcd",
            "critical_term": "the first variation of nabla_d P^(m a b d) is retained even though nabla Cbar=0",
            "euler_density_rule": "the literal C^2 action is used; no Ricci-squared replacement drops the Euler improvement",
            "maxwell_rule": "the full metric variation of sqrt(-g)F^(mu nu) is retained at nonzero background flux",
        },
        "controls": {
            "background_bach_matches_incidence": True,
            "einstein_curvature_momentum_matches_independent_lee_wald_pointwise": True,
            "flat_tt_einstein_restriction_zero": True,
            "pure_weyl_direction_pointwise_kernel": True,
            "paired_fixture_current_conserved": True,
        },
        "restriction": restriction,
        "classification": {
            "axial_ell2_both_physical_branches_nonnull": True,
            "axial_ell2_restriction_nondegenerate": True,
            "single_universal_proportionality_to_einstein_form": False,
            "relative_branch_form_indefinite": True,
            "target_weyl_gauge_removes_einstein_class": False,
            "all_axial_ell_ge2_restriction_computed": False,
            "polar_restriction_computed": False,
            "global_restriction_computed": False,
            "nonlinear_solution_embedding_certified": False,
            "final_residual_quotient_computed": False,
            "lorentzian_causal_or_scattering_theorem": False,
        },
        "interpretation": "The first curved/flux Weyl-Maxwell kill test is nonzero, so the flat zero-pairing theorem does not persist unchanged on the product background. However, the two ordinary axial Einstein-Maxwell branches acquire different restriction factors, 1+3*sqrt(3) and 1-3*sqrt(3); the latter is negative. Thus the identity tangent inclusion is not a single action-normalized symplectic copy of Einstein-Maxwell even inside ell=2. The modes remain solutions and survive target Weyl gauge; the distinction lies in their Weyl-Maxwell symplectic weights.",
        "next_gate": "derive the arbitrary-lambda axial restriction matrix and then compute the polar, physical ell=1, homogeneous ell=0, and axial-twist blocks under the frozen preflight contract",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem is exact for the axial ell=2,m=0 symbolic-k fixture and both of its physical branches. It refutes universal proportionality on that declared subspace and proves its restricted branch form is nondegenerate but relatively indefinite. It does not yet classify all axial ell, polar or global blocks, the complete fourth-order Weyl-Maxwell phase space, nonlinear closure, final SO(4,2) reduction, causal scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_axial_symplectic_restriction.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_symplectic_restriction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_symplectic_restriction",
            "python3 -m bridge.einstein_sector.weyl_maxwell_axial_lee_wald_fixture --verify bridge/certificates/weyl_maxwell_axial_lee_wald_fixture.json",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale axial restriction certificate: {path}")


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
