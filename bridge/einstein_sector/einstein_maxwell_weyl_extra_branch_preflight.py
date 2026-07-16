"""Fail-closed preflight for complementary Weyl--Maxwell harmonic branches."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_extra_branch_preflight.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_extra_branch_preflight.schema.json"
CURRENT_ENGINE = ROOT / "bridge/einstein_sector/weyl_maxwell_lee_wald_current.py"
INPUTS = {
    "background": ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json",
    "target_principal_complex": ROOT / "bridge/certificates/einstein_maxwell_product_tangent_preflight.json",
    "linear_inclusion": ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json",
    "axial_source_complex": ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json",
    "polar_source_complex": ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json",
    "exceptional_source_complex": ROOT / "bridge/certificates/einstein_maxwell_polar_exceptional_complex.json",
    "standard_inclusion": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "mixed_orthogonality": ROOT / "bridge/certificates/einstein_maxwell_weyl_mixed_block_orthogonality.json",
}


class ExtraBranchPreflightError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExtraBranchPreflightError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_inputs(records: dict[str, dict[str, Any]]) -> None:
    expected = {
        "background": "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE",
        "target_principal_complex": "EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT",
        "linear_inclusion": "EINSTEIN_MAXWELL_CHEVRETON_TANGENT",
        "axial_source_complex": "COMPACT_EM_AXIAL_MASTER_COMPLEX",
        "polar_source_complex": "COMPACT_EM_POLAR_MASTER_COMPLEX",
        "exceptional_source_complex": "COMPACT_EM_POLAR_EXCEPTIONAL_COMPLEX",
        "standard_inclusion": "EINSTEIN_MAXWELL_WEYL_STANDARD_HARMONIC_SYMPLECTIC_INCLUSION",
        "mixed_orthogonality": "EINSTEIN_MAXWELL_WEYL_MIXED_BLOCK_ORTHOGONALITY",
    }
    for name, result_id in expected.items():
        _require(records[name]["result_id"] == result_id, f"{name} result id changed")
    _require(records["linear_inclusion"]["classification"]["full_lower_order_on_shell_linear_tangent_inclusion"] is True, "linear inclusion input incomplete")
    _require(records["standard_inclusion"]["classification"]["restricted_target_form_nondegenerate"] is True, "standard pullback input incomplete")
    _require(records["mixed_orthogonality"]["classification"]["all_standard_mixed_blocks_zero"] is True, "standard mixed-block input incomplete")
    _require(records["target_principal_complex"]["classification"]["generalized_fourth_order_modes_classified"] is False, "principal preflight was silently promoted")


def _block_ledger() -> list[dict[str, Any]]:
    common = [
        "derive the complete target coefficient operator from the Weyl-Maxwell Hessian without imposing Einstein-Maxwell equations",
        "compute the exact target solution kernel modulo target Diff x Weyl x U(1) gauge",
        "identify the certified Einstein image and compute the canonical quotient with explicit representatives and independence/trivialization witnesses",
        "compute characteristic and minimal polynomials, algebraic multiplicities, geometric multiplicities, and all Jordan chains",
        "compute Einstein-extra and extra-extra Lee-Wald matrices, their ranks, radicals, and real mode multiplicities",
    ]
    return [
        {"block": "generic axial", "range": "symbolic lambda=ell(ell+1)>=6 and symbolic periodic k", "first": True, "required_outputs": common},
        {"block": "generic polar", "range": "symbolic lambda=ell(ell+1)>=6 and symbolic periodic k", "first": False, "required_outputs": common},
        {"block": "physical and generalized ell=1", "range": "both parities, all real m and periodic k; n=0 twist separate", "first": False, "required_outputs": common + ["audit exceptional residual gauge descent directly; no lambda-to-2 continuation"]},
        {"block": "homogeneous ell=0", "range": "potential-level fixed-bundle generalized solutions including W_x", "first": False, "required_outputs": common + ["retain all polynomial-in-time Jordan partners and prove full-time current conservation"]},
    ]


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _validate_inputs(records)
    return {
        "schema": "einstein-maxwell-weyl-extra-branch-preflight-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXTRA_BRANCH_PREFLIGHT",
        "result_state": "CANONICAL_TARGET_QUOTIENT_AND_BLOCK_SOLVE_CONTRACT_FROZEN_EXTRA_BRANCH_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_EXTRA_BRANCH_FULL_BLOCK_PREFLIGHT",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
            "current_engine": {"path": str(CURRENT_ENGINE.relative_to(ROOT)), "sha256": _sha256(CURRENT_ENGINE)},
        },
        "domain": "candidate full smooth periodic fixed-P_N linearized Weyl-Maxwell harmonic solution complex on R_t x S1_L x S2, before final residual SO(4,2) quotient; no boundary selection imposed",
        "canonical_object_contract": {
            "source_object": "H^0(C_EM^std), the complete certified standard Einstein-Maxwell harmonic solution quotient",
            "target_object_to_construct": "H^0(C_WM^full), the full target harmonic solution quotient by identity-component Diff x Weyl x U(1)",
            "certified_map": "injective i_*:H^0(C_EM^std)->H^0(C_WM^full)",
            "extra_object_definition": "Q_extra=H^0(C_WM^full)/i_*H^0(C_EM^std)",
            "definition_is_canonical_quotient_not_complement": True,
            "symplectic_complement_is_not_the_definition": True,
            "symplectic_complement_gate": "only after the full target reduced form and its radical are computed may a target-form orthogonal representative of Q_extra be claimed",
        },
        "result_kind_separation": {
            "extra_solution_class": "a nonzero class in Q_extra with an explicit target on-shell representative",
            "adjoint_cokernel_class": "a dual obstruction/source class for an inhomogeneous equation",
            "presymplectic_radical_class": "an on-shell direction pairing to zero with the declared target solution domain",
            "gauge_class": "a target Diff x Weyl x U(1) exact representative",
            "rule": "none of these four result kinds may be identified without an explicit map and witness",
        },
        "function_space_and_gauge_contract": {
            "spatial_space": "smooth periodic S1 Fourier modes times smooth real S2 harmonics",
            "bundle": "fixed compact U(1) bundle P_N with N=2; uniform magnetic variation excluded",
            "potential_level_data": "retain flat S1 holonomy W_x and its large-gauge periodic identification at the nonlinear level",
            "temporal_solution_space": "complete exponential and generalized polynomial/Jordan solutions of each exact harmonic ODE",
            "bounded_in_time_restriction": False,
            "target_gauge": "smooth periodic identity-component Diff x Weyl x U(1); exceptional nonperiodic would-be generators are not gauge",
            "final_residual_SO42_quotient": "not imposed in this preflight",
        },
        "exact_algebra_contract": {
            "generic_ring": "exact rational-function algebra in symbolic lambda,k and the temporal spectral variable; algebraic extensions retained exactly",
            "exceptional_rule": "ell=0 and ell=1 are derived directly, never by analytic continuation from generic ell",
            "no_finite_ell_interpolation": True,
            "no_floating_point_rank_or_root_tests": True,
            "fourth_order_counting_rule": "equation order alone does not certify a doubled physical mode count; use the prolonged gauge complex and exact quotient",
        },
        "forbidden_inferences": [
            "zeros of the relative symplectic weights on Einstein modes are not target characteristic roots or extra-branch dispersions",
            "the principal-symbol cohomology injection does not determine lower-order target modes or Jordan chains",
            "a chosen vector-space complement is not Q_extra and is not invariant data",
            "an adjoint cokernel witness is not an extra propagating solution",
            "a negative classical relative coefficient is not by itself a negative-norm particle or quantum ghost",
            "discarding a branch at future and past time boundaries is not a causal selection theorem",
        ],
        "block_solve_ledger": _block_ledger(),
        "completion_and_stop_go": {
            "complete_extra_classification": "all ledger blocks have exact quotient dimensions, representatives, gauge witnesses, spectral/Jordan data, and full mixed/extra pairing matrices",
            "if_Q_extra_zero": "certify equality of the declared linear solution quotients only; nonlinear and boundary equivalence remain open",
            "if_Q_extra_nonzero_and_mixed_pairing_nonzero": "the Einstein image is retained but not symplectically decoupled from the extra sector",
            "if_Q_extra_nonzero_and_orthogonal_with_nondegenerate_extra_form": "a target-form direct-sum representative is available on the declared compact reduced-mode domain",
            "if_extra_form_has_radical": "audit target gauge completeness, boundary/edge data, and genuine presymplectic degeneracy before interpretation",
        },
        "first_computation": {
            "block": "generic axial ell>=2 at symbolic lambda and k",
            "reason": "the certified source axial quotient and reconstruction are simplest, while still testing the full fourth-order target operator",
            "required_fixture": "one exact ell=2 branch-independent full-tensor replay plus the symbolic-lambda derivation",
            "required_output": "target quotient presentation and complete  Einstein/extra Lee-Wald matrix; a merely new dispersion polynomial is insufficient",
        },
        "classification": {
            "canonical_extra_quotient_definition_frozen": True,
            "solution_adjoint_radical_gauge_result_kinds_separated": True,
            "complete_function_space_and_gauge_contract_frozen": True,
            "complete_block_ledger_frozen": True,
            "generic_axial_declared_first": True,
            "full_target_harmonic_complex_constructed": False,
            "any_extra_solution_class_certified": False,
            "extra_branch_pairing_computed": False,
            "boundary_selected_Einstein_sector_certified": False,
            "final_residual_quotient_computed": False,
            "lorentzian_causal_or_quantum_theorem": False,
        },
        "interpretation": "The standard Einstein-Maxwell image is now a certified nondegenerate subspace, but the remaining target physics cannot be defined by choosing coordinates around it. The invariant next object is the quotient of the full target solution cohomology by that image. This preflight prevents fourth-order equation counting, adjoint obstructions, relative symplectic zeros, or arbitrary complements from being mislabeled as extra particles.",
        "next_gate": "derive the full generic axial Weyl-Maxwell harmonic operator, quotient its exact on-shell kernel by target gauge and the certified Einstein image, and compute the complete Einstein/extra Lee-Wald matrix",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE result freezes definitions, function spaces, exact algebra, block outputs, and stop/go rules. It certifies no extra target solution, dispersion, mode count, symplectic complement, boundary selection, causal propagation, particle interpretation, or quantum theorem.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_extra_branch_preflight --verify bridge/certificates/einstein_maxwell_weyl_extra_branch_preflight.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_extra_branch_preflight.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_extra_branch_preflight",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale extra-branch preflight: {path}")


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
