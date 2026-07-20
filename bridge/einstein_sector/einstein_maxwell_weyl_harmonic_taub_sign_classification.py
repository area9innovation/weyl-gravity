"""Exact harmonic Taub-sign stratification on the compact PH background."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_harmonic_taub_sign_classification.schema.json"
INPUTS = {
    "generic_taub": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "axial_q": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.json",
    "polar_q": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.json",
    "exceptional_k0": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "exceptional_nonzero_k": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
    "global_moments": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "homogeneous_cofiber": ROOT / "bridge/certificates/einstein_weyl_homogeneous_solution_cofiber.json",
    "twist_cofiber": ROOT / "bridge/certificates/einstein_weyl_twist_solution_cofiber.json",
    "opposite_momentum": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_pure_extra_taub_join.json",
}


class HarmonicTaubSignError(RuntimeError):
    """Raised when a certified input no longer supports the sign theorem."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HarmonicTaubSignError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_exact_algebra() -> dict[str, Any]:
    lam = sp.symbols("lambda", real=True)
    root = sp.sqrt(2 * lam)
    relative_plus = 1 + sp.Rational(3, 2) * root
    relative_minus = 1 - sp.Rational(3, 2) * root

    a, b, d, charge = sp.symbols("a b d Q_e", real=True)
    homogeneous = -a**2 - b**2 + b * d - charge**2
    homogeneous_matrix = sp.hessian(homogeneous, (a, b, d, charge)) / 2
    _require(homogeneous_matrix.det() == -sp.Rational(1, 4), "homogeneous quadratic block changed")

    # The (b,d) minor has negative determinant and hence one sign of each
    # type; the a and Q_e axes supply two further negative directions.
    bd_matrix = homogeneous_matrix.extract((1, 2), (1, 2))
    _require(bd_matrix.det() == -sp.Rational(1, 4), "homogeneous (b,d) inertia witness changed")
    _require(homogeneous_matrix[0, 0] == -1 and homogeneous_matrix[3, 3] == -1, "negative axes changed")

    return {
        "generic_root": "r=sqrt(2*lambda)>2 for lambda=ell*(ell+1)>=6",
        "q_relative_weights": {"plus": str(relative_plus), "minus": str(relative_minus)},
        "q_sign_witnesses": {
            "plus": "1+(3/2)*sqrt(2*lambda)>0",
            "minus": "1-(3/2)*sqrt(2*lambda)<0 because sqrt(2*lambda)>=sqrt(12)>2",
        },
        "homogeneous_quadratic_matrix_on_a_b_d_Qe": [
            [str(value) for value in row] for row in homogeneous_matrix.tolist()
        ],
        "homogeneous_determinant": str(homogeneous_matrix.det()),
        "homogeneous_inertia": {"positive": 1, "negative": 3, "zero": 0},
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}

    generic = records["generic_taub"]["classification"]
    _require(generic["generic_extra_H_Taub_negative_definite"], "generic p-primary sign input changed")
    _require(
        generic["all_nonzero_generic_pure_extra_fixed_bundle_tangents_second_order_obstructed"],
        "generic p-primary obstruction input changed",
    )
    _require(
        records["axial_q"]["classification"]["all_axial_ell_ge2_relative_branch_form_indefinite"],
        "axial q-primary sign input changed",
    )
    _require(
        records["polar_q"]["classification"]["all_polar_ell_ge2_relative_branch_form_indefinite"],
        "polar q-primary sign input changed",
    )
    _require(
        records["exceptional_k0"]["classification"]["pure_exceptional_ell1_nonzero_tangents_second_order_obstructed"],
        "exceptional k=0 sign input changed",
    )
    _require(
        records["exceptional_nonzero_k"]["classification"]["action_pairing_nonradical_positive_on_extra_cofiber"],
        "exceptional nonzero-k current input changed",
    )
    _require(
        records["homogeneous_cofiber"]["classification"]["homogeneous_solution_cofiber_zero"],
        "homogeneous cofiber is no longer zero",
    )
    _require(records["twist_cofiber"]["classification"]["twist_solution_cofiber_zero"], "twist cofiber is no longer zero")
    _require(
        records["opposite_momentum"]["classification"]["candidate_13_pure_extra_H_Taub_negative_definite"],
        "opposite-momentum sign control changed",
    )

    algebra = _check_exact_algebra()
    return {
        "schema": "einstein-maxwell-weyl-harmonic-taub-sign-classification-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_HARMONIC_TAUB_SIGN_CLASSIFICATION",
        "result_state": "CERTIFIED_EXTRA_COFIBER_SIGN_AND_STANDARD_GLOBAL_STRATIFICATION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPACT_PH_ALL_CERTIFIED_HARMONIC_SIGN_BLOCKS",
        "scope": {
            "theory": "Einstein-Maxwell source included in Weyl-Maxwell target",
            "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
            "boundaries": "closed Cauchy slice S1_L x S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N; electric tangent Q_e retained where declared",
            "carrier": "generic q/p oscillators, exceptional ell=1 oscillators, homogeneous generalized-zero block and axial twist block",
            "degree": 2,
            "parity": "axial and polar where present",
            "ell": "generic ell>=2, exceptional ell=1 and homogeneous ell=0",
            "m": "all certified SO(3) multiplicities",
            "k": "every allowed compact momentum on oscillator blocks; k=0 on homogeneous and twist blocks",
            "omega": "stationary q/p shells or the separately declared generalized-zero polynomial class",
        },
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "normalization": {
            "definition": "mu_X(u)=1/2*Omega_WM(u,L_X u)",
            "stationary_H_formula": "mu_H=-(L/4)*omega^2*c^dagger*G*c",
            "meaning": "signs are classical action-derived Taub/current signs before final residual quotient, not quantum norms",
        },
        "exact_algebra": algebra,
        "harmonic_sign_ledger": {
            "generic_extra_p_primary": {
                "scope": "ell>=2, all allowed k, all m, both parities",
                "current_inertia_per_parity": [2, 0],
                "frequency_squared": "k^2+lambda-2/3>0",
                "mu_H": "negative definite on every nonzero real finite harmonic tangent",
                "bounded": "OBSTRUCTED",
                "smooth_secular": "OBSTRUCTED",
                "causal_retarded": "NO_CERTIFIED_MAP",
            },
            "exceptional_extra_ell1": {
                "scope": "ell=1, every allowed k, all m, axial and polar",
                "k_zero_Gram": ["16", "3"],
                "nonzero_k_Gram": {
                    "axial": "4*(3*k^2+4)",
                    "polar": "4*(3*k^2+4)",
                },
                "frequency_squared": "k^2+4/3>0",
                "mu_H": "negative definite on every nonzero real exceptional extra tangent",
                "bounded": "OBSTRUCTED",
                "smooth_secular": "OBSTRUCTED",
                "causal_retarded": "NO_CERTIFIED_MAP",
            },
            "generic_Einstein_q_primary": {
                "scope": "ell>=2, all allowed k, all m, both parities",
                "plus": "positive current, hence negative mu_H",
                "minus": "negative current, hence positive mu_H",
                "role": "the q-minus Einstein image supplies the opposite sign required for mixed Einstein-extra cancellation",
                "pure_Einstein_extension": "OPEN",
            },
            "physical_ell1_standard": {
                "scope": "ell=1 standard shell",
                "mu_H": "negative definite",
                "role": "same sign as q-plus and the extra cofiber; cannot balance a pure-extra tangent",
            },
            "homogeneous_generalized_zero": {
                "scope": "ell=0,k=0 coordinates (a,b,c,d,Q_e,W_x)",
                "solution_cofiber": "0; this is entirely the Einstein image, not an additional-Weyl branch",
                "mu_H": "-a^2-b^2+b*d-Q_e^2",
                "inertia_on_a_b_d_Qe": {"positive": 1, "negative": 3, "zero": 0},
                "kernel": ["c", "W_x"],
                "common_zero": "a^2+b^2-b*d+Q_e^2=0 with c,W_x free",
                "extension": "OPEN except on separately certified fixtures",
            },
            "axial_twist_generalized_zero": {
                "scope": "ell=1,k=0 real twist position A and velocity B",
                "solution_cofiber": "0; this is entirely the Einstein image, not an additional-Weyl branch",
                "mu_H": "2*|B|^2",
                "inertia_on_A_B": {"positive": 3, "negative": 0, "zero": 3},
                "common_zero": "B=0 with arbitrary A",
                "constant_position_extension": "CERTIFIED exact mapping-torus family",
                "velocity_extension_in_isolation": "OBSTRUCTED",
            },
        },
        "finite_sum_theorem": {
            "orthogonality": "H is diagonal across unequal (ell,m,k,parity,shell) blocks after the reality pairing",
            "opposite_momenta": "k and -k have the same omega^2 and current Gram; relative phases do not change mu_H",
            "multiple_abs_k": "pure-extra contributions add with the same strict negative sign",
            "consequence": "every nonzero finite real tangent supported only on certified p-primary extra cofiber blocks has mu_H<0",
            "independence_from_other_moment_maps": "P_x and rotation charges may cancel across fibres, but they cannot cancel the strictly negative H sum",
        },
        "charge_fibre_theorem": {
            "fixed_magnetic_bundle": "uniform magnetic flux variation is not a tangent because c_1(P_N) is locally constant",
            "electric_tangent": {
                "allowed": True,
                "contribution": "-Q_e^2",
                "pure_extra": "cannot cancel the negative pure-extra mu_H",
                "mixed": "can balance a positive q-minus or twist-velocity contribution only as first-order data",
            },
            "second_order_charge_shift": "cannot change an already nonzero adjoint-cokernel pairing",
            "enlarged_continuous_flux_family": {
                "status": "OPEN",
                "effect": "may absorb the scalar constant-lapse component but defines a different phase space",
                "full_second_order_extension": "NO_CERTIFIED_MAP",
            },
        },
        "maximal_theorem": {
            "statement": "On the fixed magnetic bundle, the complete certified additional-Weyl solution cofiber is Taub-negative on every nonzero finite real harmonic tangent. The only certified opposite oscillator sign is the Einstein q-minus primary. Homogeneous and twist generalized-zero blocks do not weaken the extra-cofiber theorem because their solution cofibers vanish; instead they form separate Einstein-image strata with an indefinite homogeneous cone and exact constant-twist moduli.",
            "universal_target_definiteness": False,
            "counterexample": "nonzero constant twist position A has mu_H=0 and extends along an exact mapping-torus family",
        },
        "classification": {
            "generic_extra_all_ell_all_k_both_parities_negative": True,
            "exceptional_extra_ell1_all_k_both_parities_negative": True,
            "finite_pure_extra_harmonic_sums_negative": True,
            "opposite_momentum_and_relative_phase_independence": True,
            "Einstein_q_minus_opposite_sign_all_ell_both_parities": True,
            "homogeneous_and_twist_solution_cofibers_zero": True,
            "homogeneous_inertia_and_charge_role_classified": True,
            "constant_twist_exact_zero_energy_counterexample": True,
            "variable_magnetic_flux_extension_classified": False,
            "full_mixed_second_order_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "claim_boundary": "This theorem is exact only on the compact Plebanski-Hacyan background and the declared local-gauge-reduced harmonic carriers. It classifies Taub signs and the fixed-bundle charge effect, not every resonance functional, the full mixed tangent cone, final residual descent, all-orders integration, causal propagation, particles, ghosts or quantum norms.",
        "next_gate": "combine this sign stratification with the finite-harmonic resonance-functionals ledger to classify the complete bounded and smooth-secular second-order cones; keep causal/retarded corrections fail-closed",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_harmonic_taub_sign_classification --verify bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_harmonic_taub_sign_classification.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_harmonic_taub_sign_classification",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"harmonic Taub-sign certificate stale: {path}")


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
