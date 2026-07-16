"""Fail-closed preflight for the compact Weyl--Maxwell symplectic restriction.

The certified map is presently a map of linear on-shell tangent spaces, not a
nonlinear embedding of solution spaces.  This module freezes that distinction,
proves injectivity after the target Weyl quotient, and declares the complete
block and ambiguity ledger required by the subsequent Lee--Wald calculation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_symplectic_preflight.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_symplectic_preflight.schema.json"
INPUTS = {
    "common_background": ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json",
    "linear_tangent_inclusion": ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json",
    "second_order_extension": ROOT / "bridge/certificates/einstein_maxwell_second_order_inclusion.json",
    "flat_restriction_control": ROOT / "bridge/certificates/flat_einstein_symplectic_restriction.json",
    "radiative_einstein_form": ROOT / "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json",
    "global_einstein_form": ROOT / "bridge/certificates/einstein_maxwell_exceptional_global_symplectic.json",
}


class WeylSymplecticPreflightError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WeylSymplecticPreflightError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _quotient_injectivity() -> dict[str, Any]:
    """Exclude a pure Weyl representative in the Einstein tangent kernel."""

    sigma, sigma_tt, sigma_xx, sphere_laplacian = sp.symbols(
        "sigma sigma_tt sigma_xx Delta_S2_sigma", real=True
    )
    box_sigma = -sigma_tt + sigma_xx + sphere_laplacian

    # For h_ab=2 sigma gbar_ab and delta A=0,
    # delta E_ab/2=-nabla_a nabla_b sigma+g_ab Box sigma
    #              +Lambda sigma g_ab+kappa sigma T_ab.
    # At Lambda=rho=1/2 the algebraic terms cancel in the tt and xx rows.
    equation_tt = sp.expand(-sigma_tt - box_sigma)
    equation_xx = sp.expand(-sigma_xx + box_sigma)
    equation_sphere_trace = sp.expand(
        -sphere_laplacian + 2 * box_sigma + 2 * sigma
    )
    _require(equation_tt == -sigma_xx - sphere_laplacian, "tt Weyl-kernel row changed")
    _require(equation_xx == -sigma_tt + sphere_laplacian, "xx Weyl-kernel row changed")

    reduced_sphere = sp.expand(
        equation_sphere_trace.subs(
            {sigma_tt: sphere_laplacian, sigma_xx: -sphere_laplacian}
        )
    )
    _require(reduced_sphere == 2 * sigma - 3 * sphere_laplacian, "sphere reduction changed")

    ell = sp.symbols("ell", integer=True, nonnegative=True)
    harmonic_coefficient = sp.factor(
        reduced_sphere.subs(sphere_laplacian, -ell * (ell + 1) * sigma) / sigma
    )
    _require(
        sp.simplify(harmonic_coefficient - (3 * ell * (ell + 1) + 2)) == 0,
        "harmonic coefficient changed",
    )
    _require(
        sp.ask(sp.Q.nonnegative(ell * (ell + 1))) is True,
        "symbolic nonnegative harmonic-spectrum check failed",
    )

    return {
        "source_quotient": "ker(L_EM)/(identity-component Diff x U(1)) on fixed P_N",
        "target_quotient": "ker(L_WM)/(identity-component Diff x Weyl x U(1)) on fixed P_N",
        "common_gauge_subtraction": "if an Einstein class maps to zero, subtract the same Diff x U(1) transformation; the remaining representative is (h_ab,a_a)=(2*sigma*gbar_ab,0)",
        "conformal_stress_variation": "delta_sigma T_ab=-2*sigma*T_ab for fixed F in four dimensions",
        "linearized_metric_row": "delta E_ab/2=-nabla_a nabla_b sigma+gbar_ab Box sigma+Lambda*sigma*gbar_ab+kappa*sigma*T_ab",
        "fixture": {"Lambda": "1/2", "kappa": "1", "rho": "1/2"},
        "independent_component_equations": {
            "tt": str(equation_tt),
            "xx": str(equation_xx),
            "sphere_trace": str(equation_sphere_trace),
        },
        "elimination": str(reduced_sphere),
        "harmonic_convention": "Delta_S2 Y_ellm=-ell*(ell+1)Y_ellm",
        "harmonic_coefficient": str(harmonic_coefficient),
        "conclusion": "3*ell*(ell+1)+2 is strictly positive for every integer ell>=0, hence sigma=0 and the induced linear tangent quotient map is injective",
        "status": "CERTIFIED",
    }


def _validate_inputs(records: dict[str, dict[str, Any]]) -> None:
    background = records["common_background"]
    tangent = records["linear_tangent_inclusion"]
    second_order = records["second_order_extension"]
    flat = records["flat_restriction_control"]
    radiative = records["radiative_einstein_form"]
    global_form = records["global_einstein_form"]
    _require(background["result_id"] == "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE", "background input changed")
    _require(
        background["rational_fixture"]["parameters"]
        == {"E": "0", "Lambda": "1/2", "P": "1", "alpha_B": "3", "k_1": "0", "k_2": "1", "kappa": "1"},
        "rational common-background fixture changed",
    )
    _require(
        tangent["classification"]["full_lower_order_on_shell_linear_tangent_inclusion"] is True,
        "linear on-shell inclusion is not certified",
    )
    _require(
        second_order["classification"]["general_nonlinear_einstein_sector_closure_certified"] is False,
        "nonlinear claim boundary changed",
    )
    _require(flat["verdict"] == "REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED", "flat control changed")
    _require(
        radiative["classification"]["covariant_Lee_Wald_integrated_matching"] is True
        and radiative["classification"]["all_n_ell_ge_2_m_radiative_pairing"] is True,
        "radiative Einstein pairing input incomplete",
    )
    _require(
        global_form["classification"]["fixed_bundle_standard_harmonic_symplectic_completion"] is True,
        "global Einstein pairing input incomplete",
    )


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _validate_inputs(records)
    quotient = _quotient_injectivity()
    return {
        "schema": "einstein-maxwell-weyl-symplectic-preflight-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SYMPLECTIC_PREFLIGHT",
        "result_state": "LINEAR_RESTRICTION_DOMAIN_AND_QUOTIENT_INJECTION_CERTIFIED_CURRENT_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_FIXED_BUNDLE_STANDARD_HARMONIC_PREFLIGHT",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "domain": "complete standard Einstein-Maxwell harmonic tangent on R_t x S1_L x S2 at fixed P_N with N=2, including radiative modes and generalized ell=0/axial-ell=1 global modes; smooth periodic identity-component gauges; before the final residual SO(4,2) quotient",
        "terminology_contract": {
            "certified_map": "the identity field map i_1:(h,a)_EM -> (h,a)_WM on complete linear on-shell tangent spaces",
            "object_to_compute": "Omega_WM restricted along i_1 at the common background",
            "preferred_name": "linear tangent symplectic restriction",
            "forbidden_promotion": "do not call i_1 a nonlinear solution-space embedding or the restriction a nonlinear pullback",
            "reason": "fixed-flux radion and Maxwell-duality tangents have certified second-order extension obstructions, while general nonlinear closure remains open",
        },
        "action_and_current_contract": {
            "signature": "(-,+,+,+)",
            "einstein_maxwell_action": "S_EM=int sqrt(-g)[(R-2*Lambda)/(2*kappa)-(1/4)F_ab F^ab]",
            "weyl_maxwell_action": "S_WM=int sqrt(-g)[(alpha_B/8)C_abcd C^abcd-(1/4)F_ab F^ab]",
            "fixture": {"alpha_B": "3", "kappa": "1", "Lambda": "1/2", "P": "1", "N": "2", "k_1": "0", "k_2": "1"},
            "lee_wald_convention": "omega^mu(delta1,delta2)=delta1 theta^mu(delta2)-delta2 theta^mu(delta1); Omega_Sigma uses the future normal on S1 x S2",
            "calculation_level": "exact second variation of each declared action at the common background, evaluated on certified linear solutions",
            "mandatory_terms": [
                "the complete C^2 metric current",
                "the complete Maxwell current including background-flux metric/potential mixing",
                "all curvature lower-order terms",
                "symbolic time dependence of generalized zero-frequency representatives",
            ],
            "forbidden_shortcuts": [
                "principal-symbol-only current",
                "adding a pure metric Weyl current to a decoupled photon current while dropping flux mixing",
                "setting t=0 before proving current conservation",
            ],
        },
        "quotient_injectivity_theorem": quotient,
        "flat_control_contract": {
            "imported_verdict": records["flat_restriction_control"]["verdict"],
            "required_gravitational_limit": "on Fbar=0 and flat curvature, the restricted pure-Weyl TT current vanishes pointwise on Einstein waves",
            "required_maxwell_limit": "with metric variations disabled, reproduce the standard Maxwell Lee-Wald current with the action normalization -F^2/4",
            "interpretation": "a nonzero product-background gravitational restriction must be carried by curvature and/or background-flux terms, not by the flat biwave root",
        },
        "block_inventory": [
            {"block": "axial radiative", "range": "all Fourier n, m, ell>=2", "required_output": "exact matrix, rank, kernel, Einstein-form comparison"},
            {"block": "polar radiative", "range": "all Fourier n, m, ell>=2", "required_output": "exact matrix, rank, kernel, Einstein-form comparison"},
            {"block": "physical ell=1 quotient", "range": "both parities after ordinary gauge quotient", "required_output": "exact quotient matrix and kernel audit"},
            {"block": "homogeneous ell=0", "range": "(a,b,c,d,Q_e,W_x)", "required_output": "symbolic-t 6x6 matrix, rank, determinant, conservation"},
            {"block": "axial ell=1 twist", "range": "three real pairs (A_m,B_m)", "required_output": "one SO(3)-equivariant 2x2 block, rank, conservation"},
        ],
        "ambiguity_and_corner_contract": {
            "potential_ambiguity": "theta -> theta+dY+delta B",
            "closed_slice_rule": "a globally defined local dY integrates to zero on the closed Cauchy slice S1 x S2; delta B cancels after antisymmetrization",
            "bundle_rule": "at fixed P_N, differences of Maxwell connections are global one-forms; any claimed Cech corner must be exhibited explicitly and cannot be inferred from the monopole potential alone",
            "required_output": "state separately the bulk restriction, exact improvement, and any genuinely non-global corner contribution",
        },
        "comparison_contract": {
            "matrix_tests": ["rank", "kernel", "Pfaffian/determinant where applicable", "blockwise proportionality factor", "single-factor compatibility across all blocks"],
            "admissible_verdicts": [
                "UNIVERSAL_NONZERO_PROPORTIONAL_LINEAR_RESTRICTION",
                "BLOCK_DEPENDENT_NONDEGENERATE_LINEAR_RESTRICTION",
                "PARTIALLY_DEGENERATE_LINEAR_RESTRICTION",
                "ZERO_LINEAR_RESTRICTION",
            ],
            "target_gauge_loss": "excluded on the declared smooth fixed-bundle tangent domain by the quotient-injectivity theorem; a computed loss is a failed invariant, not an admissible reinterpretation",
            "embedding_language_gate": "only universal nonzero proportionality plus the certified quotient injection permits 'linear symplectic embedding'; no verdict here proves nonlinear closure",
        },
        "classification": {
            "complete_linear_on_shell_tangent_domain_imported": True,
            "complete_einstein_maxwell_reference_form_imported": True,
            "induced_linear_tangent_quotient_map_injective": True,
            "flat_zero_gravitational_restriction_control_imported": True,
            "nonlinear_solution_space_embedding_certified": False,
            "weyl_maxwell_symplectic_restriction_computed": False,
            "universal_nonzero_proportionality_certified": False,
            "final_residual_SO42_quotient_computed": False,
            "lorentzian_causal_or_scattering_theorem": False,
        },
        "interpretation": "Ordinary Einstein-Maxwell radiative and global tangent classes survive the target Diff x Weyl x U(1) quotient at the common product background. The remaining question is not whether Weyl gauge removes them, but whether the Weyl-Maxwell Lee-Wald form restricts nondegenerately and with the Einstein-Maxwell normalization on those classes.",
        "next_gate": "derive the full Weyl-Maxwell Lee-Wald current and evaluate the exact radiative and generalized-global restriction matrices under this contract",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE preflight certifies the calculation domain, terminology, action conventions, complete block ledger, and injectivity of the induced linear tangent quotient map. It does not compute the Weyl-Maxwell symplectic restriction, construct a nonlinear solution embedding, classify the extra fourth-order phase space, perform the final SO(4,2) quotient, or establish causal scattering or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_symplectic_preflight --verify bridge/certificates/einstein_maxwell_weyl_symplectic_preflight.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_symplectic_preflight.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_symplectic_preflight",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale symplectic preflight certificate: {path}")


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
