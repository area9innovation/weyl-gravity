"""Combine the axial and polar Weyl--Maxwell radiative restrictions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_radiative_symplectic_restriction.schema.json"
INPUTS = {
    "einstein_radiative_form": ROOT / "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json",
    "axial_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.json",
    "polar_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.json",
}


class WeylRadiativeRestrictionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WeylRadiativeRestrictionError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse(value: str, eigenvalue: sp.Symbol) -> sp.Expr:
    return sp.sympify(value.replace("lambda", "lam"), locals={"lam": eigenvalue})


def _matrix(rows: list[list[str]], eigenvalue: sp.Symbol) -> sp.Matrix:
    return sp.Matrix([[_parse(value, eigenvalue) for value in row] for row in rows])


def _is_zero_matrix(matrix: sp.Matrix) -> bool:
    return all(sp.simplify(value) == 0 for value in matrix)


def _spectral_theorem(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    eigenvalue = sp.symbols("lambda", positive=True)
    root = sp.sqrt(2 * eigenvalue)
    identity = sp.eye(2)
    polynomial_text = "p_lambda(x)=1+(3/2)*(x-lambda)"

    einstein = records["einstein_radiative_form"]
    axial = records["axial_restriction"]
    polar = records["polar_restriction"]

    master_rows = einstein["master_matching"]
    masters = {
        "axial": _matrix(master_rows["axial_master_matrix"], eigenvalue),
        "polar": _matrix(master_rows["polar_master_matrix"], eigenvalue),
    }
    einstein_forms = {
        "axial": _matrix(
            master_rows["axial_rest_frame_coefficient_matrix_without_N_over_2"],
            eigenvalue,
        ),
        "polar": _matrix(
            master_rows["action_normalized_matrices_without_N_over_2"]["polar"],
            eigenvalue,
        ),
    }
    expected_masters = {
        "axial": sp.Matrix([[eigenvalue, 2], [eigenvalue, eigenvalue]]),
        "polar": sp.Matrix([[eigenvalue, -2 * eigenvalue], [-1, eigenvalue]]),
    }
    expected_forms = {
        "axial": sp.diag(eigenvalue, 2),
        "polar": sp.Matrix([[1, -2], [-2, 2 * eigenvalue]]),
    }
    _require(masters == expected_masters, "Einstein master operators changed")
    _require(einstein_forms == expected_forms, "Einstein coefficient forms changed")

    branch_vectors = {
        "axial": {
            "plus": sp.Matrix([1, sp.sqrt(eigenvalue / 2)]),
            "minus": sp.Matrix([1, -sp.sqrt(eigenvalue / 2)]),
        },
        "polar": {
            "plus": sp.Matrix([1, -1 / root]),
            "minus": sp.Matrix([1, 1 / root]),
        },
    }
    branch_eigenvalues = {
        "plus": eigenvalue + root,
        "minus": eigenvalue - root,
    }
    expected_ratios = {
        "plus": 1 + sp.Rational(3, 2) * root,
        "minus": 1 - sp.Rational(3, 2) * root,
    }

    parity_rows: dict[str, Any] = {}
    spectral_parameter = sp.symbols("x")
    for parity, input_name in (
        ("axial", "axial_restriction"),
        ("polar", "polar_restriction"),
    ):
        master = masters[parity]
        form = einstein_forms[parity]
        relative_operator = sp.simplify(identity + sp.Rational(3, 2) * (master - eigenvalue * identity))
        target_form = sp.simplify(form * relative_operator)
        _require(form * master == master.T * form, f"{parity} master lost Einstein self-adjointness")
        _require(target_form == target_form.T, f"{parity} spectral target form is not symmetric")
        _require(
            sp.factor(master.charpoly(spectral_parameter).as_expr())
            == sp.factor((spectral_parameter - eigenvalue) ** 2 - 2 * eigenvalue),
            f"{parity} characteristic polynomial changed",
        )

        stored_rows = records[input_name]["restriction"]["on_shell_branches"]
        branch_rows: list[dict[str, str]] = []
        for stored, branch in zip(stored_rows, ("plus", "minus"), strict=True):
            vector = branch_vectors[parity][branch]
            mass = branch_eigenvalues[branch]
            _require(
                _is_zero_matrix(master * vector - mass * vector),
                f"{parity} {branch} eigenvector changed",
            )
            denominator = sp.simplify((vector.T * form * vector)[0])
            numerator = sp.simplify((vector.T * target_form * vector)[0])
            ratio = sp.simplify(numerator / denominator)
            _require(sp.simplify(ratio - expected_ratios[branch]) == 0, f"{parity} {branch} spectral ratio changed")
            stored_ratio = _parse(stored["restriction_over_einstein"], eigenvalue)
            _require(sp.simplify(stored_ratio - ratio) == 0, f"{parity} {branch} imported ratio changed")
            branch_rows.append(
                {
                    "branch": branch,
                    "master_eigenvalue_mu": str(mass),
                    "relative_eigenvalue": str(sp.expand(expected_ratios[branch])),
                    "ell_ge_2_sign": "POSITIVE" if branch == "plus" else "NEGATIVE",
                }
            )

        plus = branch_vectors[parity]["plus"]
        minus = branch_vectors[parity]["minus"]
        _require(sp.simplify((plus.T * form * minus)[0]) == 0, f"{parity} Einstein branch orthogonality failed")
        _require(sp.simplify((plus.T * target_form * minus)[0]) == 0, f"{parity} target branch orthogonality failed")
        parity_rows[parity] = {
            "master_operator": [[str(value) for value in row] for row in master.tolist()],
            "einstein_coefficient_form": [[str(value) for value in row] for row in form.tolist()],
            "relative_operator_p_of_M": [[str(value) for value in row] for row in relative_operator.tolist()],
            "spectral_target_form_E_times_p_of_M": [[str(value) for value in row] for row in target_form.tolist()],
            "self_adjointness_remainder": [["0", "0"], ["0", "0"]],
            "cross_branch_E_pairing": "0",
            "cross_branch_target_pairing": "0",
            "branches": branch_rows,
        }

    plus_lower = sp.simplify(expected_ratios["plus"].subs(eigenvalue, 6))
    minus_upper = sp.simplify(expected_ratios["minus"].subs(eigenvalue, 6))
    _require(plus_lower.is_positive is True, "plus-branch sign proof failed")
    _require(minus_upper.is_negative is True, "minus-branch sign proof failed")

    return {
        "common_spectral_polynomial": polynomial_text,
        "solution_space_identity": "Omega_WM|Sol_rad(u,v)=Omega_EM(u,p_lambda(M_rad)v)",
        "direct_sum_master_operator": "M_rad=M_axial direct_sum M_polar",
        "direct_sum_relative_operator": "R_rad=p_lambda(M_rad)=p_lambda(M_axial) direct_sum p_lambda(M_polar)",
        "parity_blocks": parity_rows,
        "orthogonality_proof": {
            "different_ell_or_m": "SO(3) invariance and harmonic orthogonality (equivalently Schur orthogonality) kill inequivalent harmonic labels; complex m pairs with -m under the reality convention",
            "different_periodic_momentum": "S1 Fourier orthogonality pairs n with -n and kills nonconjugate momenta",
            "axial_vs_polar": "spatial parity acts by (-1)^(ell+1) on axial and (-1)^ell on polar representatives; invariance of both Lee-Wald forms therefore makes their cross-pairing equal to its negative",
            "plus_vs_minus_same_parity": "at fixed (n,ell,m), conservation and time-translation covariance kill pairings with unequal frequency phase; algebraically M is E-self-adjoint, so its distinct eigenspaces are E-orthogonal and remain orthogonal for E*p_lambda(M)",
            "frequency_noncollision": "omega_plus^2-omega_minus^2=2*sqrt(2*lambda)>0 for ell>=2",
        },
        "all_ell_ge_2_classification": {
            "lambda_range": "lambda=ell*(ell+1)>=6",
            "common_relative_weights": [
                str(sp.expand(expected_ratios["plus"])),
                str(sp.expand(expected_ratios["minus"])),
            ],
            "plus_weight_sign": "positive",
            "minus_weight_sign": "negative",
            "branch_coefficient_rank_per_real_spatial_harmonic": 4,
            "branch_coefficient_relative_signature_per_real_spatial_harmonic": {
                "positive": 2,
                "negative": 2,
                "zero": 0,
            },
            "identity_inclusion_preserves_Einstein_symplectic_form": False,
            "restricted_target_form_nondegenerate": True,
        },
        "mode_counting_convention": {
            "complex_basis": "a coefficient labelled (n,ell,m) is paired with the reality-conjugate coefficient (-n,ell,-m); it is not counted as an independent real oscillator",
            "real_basis": "use 2ell+1 real spherical harmonics and one constant S1 harmonic for n=0 or the cosine/sine pair for each n>0",
            "real_spatial_multiplicity_q_n_ell": "q=(2*ell+1) for n=0 and q=2*(2*ell+1) for n>0",
            "oscillators_per_real_spatial_harmonic": 4,
            "darboux_blocks_per_q": "4*q: two relative-positive and two relative-negative",
            "real_phase_space_dimension_per_q": "8*q",
            "relative_operator_eigenspace_dimensions_on_real_Cauchy_data": "positive=4*q, negative=4*q, zero=0",
        },
        "quantum_norm_boundary": {
            "classical_relative_symmetric_coefficient_signature_only": True,
            "positive_frequency_complex_structure_constructed": False,
            "one_particle_norm_certified": False,
            "ghost_or_unitarity_theorem": False,
            "warning": "the negative relative branch coefficient is not, by itself, a certified negative-norm particle or quantum ghost",
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _require(
        records["einstein_radiative_form"]["classification"]["all_n_ell_ge_2_m_radiative_pairing"] is True,
        "Einstein radiative completeness input changed",
    )
    _require(
        records["axial_restriction"]["classification"]["all_axial_ell_ge2_restriction_nondegenerate"] is True,
        "axial restriction input changed",
    )
    _require(
        records["polar_restriction"]["classification"]["all_polar_ell_ge2_restriction_nondegenerate"] is True,
        "polar restriction input changed",
    )
    theorem = _spectral_theorem(records)
    return {
        "schema": "einstein-maxwell-weyl-radiative-symplectic-restriction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_RADIATIVE_SYMPLECTIC_RESTRICTION",
        "result_state": "STANDARD_RADIATIVE_ALL_ELL_GE2_COMMON_SPECTRAL_RELATIVE_OPERATOR_NONDEGENERATE_INDEFINITE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_STANDARD_RADIATIVE_ALL_ELL_GE2_SYMBOLIC_K",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "domain": "the direct sum of all standard axial and polar Einstein-Maxwell radiative harmonics on R_t x S1_L x S2 with lambda=ell(ell+1), ell>=2, all real harmonic multiplicities, every periodic S1 momentum, and both master branches, before the final residual SO(4,2) quotient",
        "theorem": theorem,
        "classification": {
            "complete_standard_axial_polar_ell_ge2_restriction": True,
            "common_parity_independent_spectral_polynomial": True,
            "cross_parity_orthogonality_certified": True,
            "cross_branch_orthogonality_certified": True,
            "restricted_target_form_nondegenerate": True,
            "relative_branch_coefficient_form_indefinite": True,
            "identity_inclusion_symplectic": False,
            "ordinary_radiative_modes_removed_by_target_weyl_gauge": False,
            "positive_frequency_complex_structure_constructed": False,
            "one_particle_norm_certified": False,
            "quantum_ghost_or_unitarity_theorem": False,
            "physical_ell1_restriction_computed": False,
            "homogeneous_and_twist_restriction_computed": False,
            "complete_fourth_order_weyl_maxwell_phase_space_classified": False,
            "nonlinear_solution_embedding_certified": False,
            "final_residual_quotient_computed": False,
            "lorentzian_causal_or_scattering_theorem": False,
        },
        "interpretation": "Every standard ell>=2 Einstein-Maxwell radiative direction survives as a nonnull direction of the Weyl-Maxwell restriction before the final residual quotient. On the full axial-plus-polar radiative solution space the pullback is Omega_EM composed with the single spectral polynomial p_lambda(M)=1+(3/2)(M-lambda). Each real spatial harmonic has two relative-positive and two relative-negative branch blocks. Thus the identity tangent inclusion is injective and target-nondegenerate but is not symplectic. This is a classical relative coefficient statement, not a one-particle negative-norm, ghost, unitarity, causal, or scattering theorem.",
        "next_gate": "compute the physical ell=1 Weyl-Maxwell restriction using the certified quotient representatives, then the homogeneous ell=0 and axial-twist generalized global restrictions by direct Lee-Wald currents",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem combines the already certified direct-current axial and polar ell>=2 restrictions and proves their common spectral-operator, orthogonality, and real-mode multiplicity structure. It does not cover exceptional ell=1, homogeneous ell=0, axial twist, extra fourth-order Weyl-Maxwell solutions, nonlinear closure, the final SO(4,2) quotient, a positive-frequency Hilbert space, causal scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_radiative_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_radiative_symplectic_restriction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_radiative_symplectic_restriction",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale radiative restriction certificate: {path}")


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
