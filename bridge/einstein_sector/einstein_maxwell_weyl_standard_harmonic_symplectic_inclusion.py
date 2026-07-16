"""Assemble the complete standard-harmonic Einstein--Maxwell inclusion theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.schema.json"
INPUTS = {
    "einstein_radiative": ROOT / "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json",
    "einstein_global": ROOT / "bridge/certificates/einstein_maxwell_exceptional_global_symplectic.json",
    "radiative_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
    "physical_ell1_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
    "homogeneous_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
    "twist_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
    "mixed_orthogonality": ROOT / "bridge/certificates/einstein_maxwell_weyl_mixed_block_orthogonality.json",
    "preflight": ROOT / "bridge/certificates/einstein_maxwell_weyl_symplectic_preflight.json",
}


class StandardHarmonicInclusionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StandardHarmonicInclusionError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _theorem(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    radiative = records["radiative_restriction"]
    ell1 = records["physical_ell1_restriction"]
    homogeneous = records["homogeneous_restriction"]
    twist = records["twist_restriction"]
    mixed = records["mixed_orthogonality"]
    _require(radiative["classification"]["restricted_target_form_nondegenerate"] is True, "radiative block changed")
    _require(ell1["classification"]["physical_ell1_restriction_nondegenerate"] is True, "physical ell1 block changed")
    _require(homogeneous["classification"]["restricted_target_form_nondegenerate"] is True, "homogeneous block changed")
    _require(twist["classification"]["restricted_target_form_nondegenerate"] is True, "twist block changed")
    _require(mixed["classification"]["all_standard_mixed_blocks_zero"] is True, "mixed-block theorem changed")

    lam = sp.symbols("lam", real=True)
    weight_text = radiative["theorem"]["all_ell_ge_2_classification"]["common_relative_weights"]
    weights = [sp.sympify(value.replace("lambda", "lam"), locals={"lam": lam}) for value in weight_text]
    _require(weights[0].subs(lam, 6) > 0 and weights[1].subs(lam, 6) < 0, "radiative sign endpoint changed")
    _require(ell1["theorem"]["normalized_direct_sum_theorem"]["relative_operator"] == [["4", "0"], ["0", "4"]], "ell1 factor changed")
    _require(twist["theorem"]["cauchy_forms_after_common_factor_L_N_1m"]["identity"] == "Omega_WM|twist=-2*Omega_EM|twist", "twist factor changed")
    _require(homogeneous["theorem"]["relative_endomorphism"]["N_squared"] == "0", "homogeneous shear changed")

    return {
        "solution_space_decomposition": {
            "identity": "T_EM^std=T_rad^(ell>=2) direct_sum T_phys^(ell=1) direct_sum T_hom^(ell=0) direct_sum T_twist^(axial ell=1,omega=0)",
            "scope": "fixed magnetic bundle, smooth periodic identity-component gauge transformations, generalized polynomial global solutions retained",
            "source_completeness_receipts": [
                "COMPACT_EM_RADIATIVE_SYMPLECTIC_MATCHING",
                "COMPACT_EM_EXCEPTIONAL_GLOBAL_SYMPLECTIC",
            ],
        },
        "block_table": [
            {
                "block": "standard axial plus polar radiative",
                "labels": "ell>=2, all m and periodic n, both master branches",
                "pullback_relative_operator": "p_lambda(M_rad), with common parity-independent branch weights " + ", ".join(str(value) for value in weights),
                "nondegeneracy": True,
                "special_feature": "relative coefficient signature (2,2) per real spatial harmonic",
                "certificate": "EINSTEIN_MAXWELL_WEYL_RADIATIVE_SYMPLECTIC_RESTRICTION",
            },
            {
                "block": "physical axial plus polar ell=1 quotient",
                "labels": "all m and periodic n",
                "pullback_relative_operator": "4*I in source-normalized parity coordinates",
                "nondegeneracy": True,
                "special_feature": "literal exceptional current has zero residual-gauge rows and columns",
                "certificate": "EINSTEIN_MAXWELL_WEYL_ELL1_PHYSICAL_SYMPLECTIC_RESTRICTION",
            },
            {
                "block": "homogeneous generalized global",
                "labels": "(a,b,c,d,Q_e,W_x)",
                "pullback_relative_operator": "I+N, rank(N)=2, N^2=0",
                "nondegeneracy": True,
                "special_feature": "identity is not symplectic; S=I+N/2 gives S^T Omega_EM S=Omega_WM",
                "certificate": "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_GLOBAL_SYMPLECTIC_RESTRICTION",
            },
            {
                "block": "axial ell=1 generalized twist",
                "labels": "three real m, each (A_m,B_m)",
                "pullback_relative_operator": "-2*I",
                "nondegeneracy": True,
                "special_feature": "zero-frequency Jordan block computed directly, not by a radiative limit",
                "certificate": "EINSTEIN_MAXWELL_WEYL_AXIAL_TWIST_SYMPLECTIC_RESTRICTION",
            },
        ],
        "cross_block_orthogonality": {
            "different_ell_or_m": "SO(3) invariance and real-harmonic orthogonality",
            "different_periodic_momentum": "S1 Fourier orthogonality",
            "axial_vs_polar": "spatial parity invariance",
            "radiative_branches": "the master operator is Omega_EM-self-adjoint and has distinct eigenvalues",
            "twist_vs_physical_axial_ell1": "direct literal current at the only shared label (ell=1,n=0,same m) has exact factor omega^2-4 and vanishes on the physical shell for arbitrary twist A+B*t; all m follow by SO(3)",
            "homogeneous_vs_nonzero_ell": "SO(3) harmonic orthogonality",
            "certificate": "EINSTEIN_MAXWELL_WEYL_MIXED_BLOCK_ORTHOGONALITY",
            "conclusion": "the target pullback is the displayed block-diagonal direct sum",
        },
        "inclusion_theorem": {
            "restricted_target_form_nondegenerate_on_every_block": True,
            "restricted_target_form_nondegenerate_on_complete_standard_tangent": True,
            "kernel_of_pullback_on_standard_tangent": "0",
            "ordinary_Einstein_Maxwell_tangent_removed_before_final_residual_quotient": False,
            "identity_inclusion_is_symplectic": False,
            "identity_inclusion_has_nondegenerate_target_pullback": True,
            "meaning": "the linear solution inclusion retains all certified standard Einstein-Maxwell tangent directions and equips them with another nondegenerate form; it does not identify the two Hamiltonian structures under the identity map",
        },
        "observable_consequence_and_limit": {
            "linear_observables_on_the_restricted_subspace": "because the pullback is nondegenerate, every linear source observable has a unique Hamiltonian vector with respect to the restricted target form after applying the invertible relative operator",
            "automatic_embedding_into_full_target_observable_algebra": False,
            "reason": "extension away from the Einstein subspace and descent through the final SO(4,2) quotient are separate problems",
        },
        "graviton_interpretation": {
            "before_final_residual_quotient": "the usual helicity-like axial and polar radiative modes occur in the physical ell=1 and ell>=2 oscillator blocks and have nonzero target pullback pairings",
            "vanishing_final_one_particle_residual_cohomology_not_in_conflict": "that statement concerns a later global SO(4,2) quotient on the closed cylinder, not the existence of these local/reduced-mode radiative solutions before that quotient and not asymptotically flat radiation",
            "closed_cylinder_vs_scattering": "the present compact Cauchy surface has no null infinity and certifies no asymptotically flat scattering space",
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    expected_ids = {
        "einstein_radiative": "COMPACT_EM_RADIATIVE_SYMPLECTIC_MATCHING",
        "einstein_global": "COMPACT_EM_EXCEPTIONAL_GLOBAL_SYMPLECTIC",
        "radiative_restriction": "EINSTEIN_MAXWELL_WEYL_RADIATIVE_SYMPLECTIC_RESTRICTION",
        "physical_ell1_restriction": "EINSTEIN_MAXWELL_WEYL_ELL1_PHYSICAL_SYMPLECTIC_RESTRICTION",
        "homogeneous_restriction": "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_GLOBAL_SYMPLECTIC_RESTRICTION",
        "twist_restriction": "EINSTEIN_MAXWELL_WEYL_AXIAL_TWIST_SYMPLECTIC_RESTRICTION",
        "mixed_orthogonality": "EINSTEIN_MAXWELL_WEYL_MIXED_BLOCK_ORTHOGONALITY",
        "preflight": "EINSTEIN_MAXWELL_WEYL_SYMPLECTIC_PREFLIGHT",
    }
    for name, result_id in expected_ids.items():
        _require(records[name]["result_id"] == result_id, f"{name} result id changed")
    _require(records["einstein_global"]["classification"]["fixed_bundle_standard_harmonic_symplectic_completion"] is True, "Einstein global completeness changed")
    return {
        "schema": "einstein-maxwell-weyl-standard-harmonic-symplectic-inclusion-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_STANDARD_HARMONIC_SYMPLECTIC_INCLUSION",
        "result_state": "COMPLETE_FIXED_BUNDLE_STANDARD_EINSTEIN_TANGENT_PULLBACK_NONDEGENERATE_BEFORE_FINAL_RESIDUAL_QUOTIENT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_FIXED_BUNDLE_STANDARD_HARMONIC_LINEAR_TANGENT",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "the complete certified fixed-bundle standard-harmonic linearized Einstein-Maxwell solution tangent on R_t x S1_L x S2, including radiative and generalized global blocks, before the final residual SO(4,2) quotient",
        "theorem": _theorem(records),
        "classification": {
            "complete_standard_harmonic_linear_restriction": True,
            "radiative_ell_ge2_included": True,
            "physical_ell1_included": True,
            "homogeneous_ell0_included": True,
            "axial_twist_included": True,
            "restricted_target_form_nondegenerate": True,
            "identity_inclusion_symplectic": False,
            "all_standard_tangent_directions_survive_before_final_residual_quotient": True,
            "complete_standard_mixed_block_orthogonality_directly_certified": True,
            "extra_fourth_order_target_solutions_classified": False,
            "nonlinear_inclusion_or_closure_certified": False,
            "full_target_observable_embedding_certified": False,
            "final_residual_quotient_computed": False,
            "asymptotically_flat_boundary_conditions_constructed": False,
            "lorentzian_causal_or_scattering_theorem": False,
            "one_particle_or_quantum_theorem": False,
        },
        "interpretation": "At linear order on the closed cylinder and before the final residual quotient, the complete certified standard Einstein-Maxwell tangent is retained inside Weyl-Maxwell theory without any symplectic null directions. This is stronger than solution inclusion but weaker than equivalence: the identity map changes the Hamiltonian structure block by block, additional fourth-order target solutions remain open, and neither full observable descent nor asymptotically flat scattering follows. Thus the graviton has not disappeared at this stage; any vanishing final residual one-particle cohomology belongs to a later global quotient and a different physical question.",
        "next_gate": "classify the complementary fourth-order Weyl-Maxwell solution branches and then test whether Lorentzian boundary conditions select a dynamically closed Einstein scattering sector; separately compute descent through the final residual quotient",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE assembly theorem is linear, fixed-bundle, compact-cylinder, and pre-final-quotient. It proves nondegeneracy of the target pullback on the complete certified standard Einstein-Maxwell harmonic tangent. It does not prove nonlinear closure, equality of theories, a full observable-algebra embedding, removal of extra Weyl solutions, asymptotically flat boundary selection, a causal scattering theorem, or quantum unitarity.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion --verify bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_homogeneous_global_symplectic_restriction bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_twist_symplectic_restriction bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell1_physical_symplectic_restriction bridge.einstein_sector.tests.test_einstein_maxwell_weyl_radiative_symplectic_restriction",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_mixed_block_orthogonality.py",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale standard-harmonic inclusion certificate: {path}")


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
