"""Quantum readiness ledger for the relative Einstein--Weyl QME defect.

This module imports the strongest registered inclusion, partial off-shell
triangle, and relative pairing evidence.  It does not synthesize the missing
all-sector off-shell BV triangle.  The relative anomaly and state maps
therefore remain undefined.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STANDARD_INCLUSION = ROOT / "d_quotient_programme/contributions/einstein-maxwell-weyl-standard-harmonic-inclusion.json"
QUADRATIC_PREFLIGHT = ROOT / "d_quotient_programme/contributions/einstein-maxwell-weyl-axial-quadratic-channel-preflight.json"
LOCAL_CARTAN = ROOT / "quantum-weyl/cartan/certificates/LOCAL_ANOMALY_TO_D_CARTAN_COMPARISON.json"
GLOBAL_A104 = ROOT / "quantum-weyl/lorentzian/certificates/BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY.json"
PLANNING_BRIEF = ROOT / "notes/d-quotient-quantum-team-brief.md"
ROADMAP = ROOT / "notes/universe-building-roadmap.md"
TRIANGLE_PREFLIGHT = (
    ROOT / "bridge/certificates/einstein_weyl_relative_linear_triangle_preflight.json"
)
RELATIVE_FUNCTOR_PREFLIGHT = (
    ROOT
    / "d_quotient_classical/certificates/RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1.json"
)
POLAR_LIFT = (
    ROOT
    / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json"
)
PH_STABILIZER = (
    ROOT
    / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json"
)
TRIANGLE_PREFLIGHT_COMMIT = "9570f03c2a880dfbf600567a4d06ca9009b2cb8e"
RELATIVE_FUNCTOR_PREFLIGHT_COMMIT = "1cd9f8e68774e68821b130ee01353075a42eae07"
POLAR_LIFT_COMMIT = "427e479db7b3d7bd15a01ca8e0940c27bb21ed4f"
PH_STABILIZER_COMMIT = "607be99928ca94515af4b8d96e0faff2229329d7"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text()) if path.suffix == ".json" else None
    identity = (
        payload.get("result_id") or payload.get("setting_id") or payload.get("schema")
        if isinstance(payload, dict)
        else path.name
    )
    if not isinstance(identity, str) or not identity:
        raise ValueError(f"dependency identity missing: {path}")
    return {
        "artifact_id": identity,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _committed_evidence(contribution: dict[str, Any]) -> dict[str, str]:
    evidence = contribution.get("evidence", {})
    if set(evidence) != {"commit", "path", "sha256"}:
        raise ValueError("relative classical contribution evidence is malformed")
    content = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{evidence['commit']}:./{evidence['path']}"]
    )
    if hashlib.sha256(content).hexdigest() != evidence["sha256"]:
        raise ValueError("relative classical contribution evidence hash mismatch")
    working = ROOT / evidence["path"]
    if not working.is_file() or working.read_bytes() != content:
        raise ValueError("working relative evidence differs from pinned commit")
    return deepcopy(evidence)


def _pinned_path(path: Path, commit: str) -> dict[str, str]:
    relative = str(path.relative_to(ROOT))
    prefix = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "--show-prefix"], text=True
    ).strip()
    content = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{commit}:{prefix}{relative}"]
    )
    if not path.is_file() or path.read_bytes() != content:
        raise ValueError(f"working evidence differs from pinned commit: {relative}")
    return {
        "commit": commit,
        "path": relative,
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _polar_matrix(values: object, local: dict[str, sp.Expr]) -> sp.Matrix:
    if not isinstance(values, list) or not values or not all(
        isinstance(row, list) for row in values
    ):
        raise ValueError("polar matrix record is malformed")
    try:
        return sp.Matrix(
            [
                [
                    sp.sympify(str(value).replace("lambda", "lam"), locals=local)
                    for value in row
                ]
                for row in values
            ]
        )
    except (TypeError, ValueError, sp.SympifyError) as error:
        raise ValueError("polar matrix coefficient is malformed") from error


def _polar_zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(
        matrix.rows, matrix.cols
    )


def _polar_exact_replay(polar: dict[str, Any]) -> dict[str, Any]:
    lam, k, omega = sp.symbols("lambda k omega", real=True)
    local = {"lam": lam, "k": k, "omega": omega, "I": sp.I}
    contractions = polar["contractions"]
    complexes = polar["complexes"]
    chain = polar["chain_map"]
    Gs = _polar_matrix(contractions["source_gauge_map"], local)
    Gt = _polar_matrix(contractions["target_gauge_map"], local)
    Ps = _polar_matrix(contractions["source_invariant_projection"], local)
    Pt = _polar_matrix(contractions["target_invariant_projection"], local)
    Js = _polar_matrix(contractions["source_section"], local)
    Jt = _polar_matrix(contractions["target_section"], local)
    Hs = _polar_matrix(contractions["source_homotopy"], local)
    Ht = _polar_matrix(contractions["target_homotopy"], local)
    Es = _polar_matrix(complexes["source_ungauged_Euler_operator"], local)
    Lt = _polar_matrix(complexes["target_ungauged_Hessian_operator"], local)
    Ns = _polar_matrix(complexes["source_Bianchi_map"], local)
    Nt = _polar_matrix(complexes["target_Noether_map"], local)
    ghost = _polar_matrix(chain["ghost_map_source_to_target"], local)
    field = _polar_matrix(chain["field_map_source_to_target"], local)
    equation = _polar_matrix(chain["equation_map_source_to_target"], local)
    identity = _polar_matrix(chain["identity_map_source_to_target"], local)
    adjoint_Lt = Lt.subs({omega: -omega, k: -k}, simultaneous=True).T
    checks = {
        "source_projection_kills_gauge": _polar_zero(Ps * Gs),
        "target_projection_kills_gauge": _polar_zero(Pt * Gt),
        "source_projection_section_identity": Ps * Js == sp.eye(5),
        "target_projection_section_identity": Pt * Jt == sp.eye(4),
        "source_contraction_identity": _polar_zero(
            Js * Ps - sp.eye(8) - Gs * Hs
        ),
        "target_contraction_identity": _polar_zero(
            Jt * Pt - sp.eye(8) - Gt * Ht
        ),
        "source_right_Noether_identity": _polar_zero(Es * Gs),
        "source_left_Noether_identity": _polar_zero(Ns * Es),
        "target_right_Noether_identity": _polar_zero(Lt * Gt),
        "target_left_Noether_identity": _polar_zero(Nt * Lt),
        "ghost_field_square": _polar_zero(field * Gs - Gt * ghost),
        "field_equation_square": _polar_zero(Lt * field - equation * Es),
        "equation_identity_square": _polar_zero(Nt * equation - identity * Ns),
        "target_formal_self_adjoint": _polar_zero(Lt - adjoint_Lt),
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise ValueError("polar exact replay failed: " + ", ".join(failed))
    return {
        "coefficient_ring": "Q[lambda,k,omega,I]",
        "source_field_rank": 8,
        "target_field_rank": 8,
        "source_gauge_rank": 3,
        "target_gauge_rank": 4,
        "exact_check_count": len(checks),
        "checks": checks,
    }


def _semantic_inputs() -> dict[str, Any]:
    inclusion = json.loads(STANDARD_INCLUSION.read_text())
    quadratic = json.loads(QUADRATIC_PREFLIGHT.read_text())
    cartan = json.loads(LOCAL_CARTAN.read_text())
    a104 = json.loads(GLOBAL_A104.read_text())
    triangle = json.loads(TRIANGLE_PREFLIGHT.read_text())
    functor = json.loads(RELATIVE_FUNCTOR_PREFLIGHT.read_text())
    polar = json.loads(POLAR_LIFT.read_text())
    stabilizer = json.loads(PH_STABILIZER.read_text())
    if (
        inclusion.get("team_id") != "einstein_boundary"
        or inclusion.get("claim_status") != "CERTIFIED"
        or inclusion.get("verdict")
        != "G4_COMPLETE_STANDARD_HARMONIC_PULLBACK_NONDEGENERATE_BEFORE_FINAL_QUOTIENT"
    ):
        raise ValueError("standard harmonic inclusion boundary drifted")
    if "off-shell BV" not in " ".join(inclusion.get("not_established", [])):
        # The current contribution phrases this as nonlinear/final-residual
        # absence.  The roadmap supplies the explicit off-shell gate.
        if "nonlinear" not in " ".join(inclusion.get("not_established", [])).lower():
            raise ValueError("standard inclusion no longer records its nonlinear boundary")
    if (
        quadratic.get("claim_status") != "CERTIFIED"
        or quadratic.get("verdict")
        != "G2_AXIAL_EE_FINITE_RESONANCE_WINDOW_AND_FIRST_REMOVABLE_BLOCK"
    ):
        raise ValueError("quadratic relative preflight boundary drifted")
    if (
        cartan.get("result_state")
        != "LOCAL_D_PULLBACK_COMPUTED_TARGET_CHAIN_MAP_UNDEFINED"
        or cartan.get("cartan_defect_comparison", {}).get("classification_status")
        != "NO_VERDICT"
    ):
        raise ValueError("local Cartan/QME boundary drifted")
    if (
        a104.get("result_state")
        != "GLOBAL_A104_104_BY_104_KNOWN_MASK_EXACT_TWO_A12_SLOTS_OPEN"
        or a104.get("claim_flags", {}).get("BERGER_HADAMARD_DATA") is not False
    ):
        raise ValueError("Lorentzian A104/Hadamard boundary drifted")
    classification = triangle.get("classification", {})
    if (
        triangle.get("result_id") != "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_PREFLIGHT"
        or triangle.get("result_state")
        != "PRINCIPAL_AND_GENERIC_AXIAL_OFFSHELL_CHAIN_MAPS_CERTIFIED_FULL_CURVED_ALL_SECTOR_TRIANGLE_OPEN"
        or classification.get("principal_BV_chain_map_and_cone_certified") is not True
        or classification.get("generic_axial_offshell_chain_map_certified") is not True
        or classification.get("generic_axial_solution_cofiber_and_pairing_certified") is not True
        or classification.get("full_curved_all_sector_chain_map_certified") is not False
        or classification.get("global_mapping_cofiber_complex_certified") is not False
        or classification.get("relative_linear_triangle_V1_certified") is not False
        or classification.get("quantum_import_gate_satisfied") is not False
    ):
        raise ValueError("partial relative triangle boundary drifted")
    flags = functor.get("flags", {})
    if (
        functor.get("result_id") != "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1"
        or functor.get("result_state")
        != "PARTIAL_OFFSHELL_PREFLIGHT_IMPORTED_FULL_TRIANGLE_MISSING"
        or flags.get("RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_PREFLIGHT_V1") is not True
        or flags.get("EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_IMPORTED") is not False
        or flags.get("RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1") is not False
    ):
        raise ValueError("relative functor preflight boundary drifted")
    polar_flags = polar.get("classification", {})
    if (
        polar.get("result_id")
        != "EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_NOETHER_LIFT"
        or polar.get("result_state")
        != "POLAR_UNGAUGED_DIFF_WEYL_EQUATION_NOETHER_COMPLEX_AND_CHAIN_MAP_CERTIFIED"
        or polar.get("generality_level")
        != "G2_POLAR_ALL_PHYSICAL_ELL_K_UNGAUGED_NOETHER_COMPLEX"
        or polar_flags.get(
            "polynomial_ghost_field_equation_identity_chain_map_certified"
        )
        is not True
        or polar_flags.get("ungauged_local_Green_identity_certified") is not True
        or polar_flags.get("cyclic_BV_chain_map_certified") is not False
        or polar_flags.get("final_residual_descent_certified") is not False
        or polar_flags.get("quantum_classical_import_gate_satisfied") is not False
        or polar_flags.get("Lorentzian_causal_claim") is not False
    ):
        raise ValueError("polar ungauged Noether lift boundary drifted")
    polar_current = polar.get("local_Green_current", {})
    if (
        polar_current.get("time_current_term_count") != 184
        or polar_current.get("space_current_term_count") != 184
        or polar_current.get("off_shell_jet_identity_remainder") != []
        or polar_current.get("restriction_to_reduced_section_exact") is not True
    ):
        raise ValueError("polar local Green identity boundary drifted")
    polar_replay = _polar_exact_replay(polar)
    stabilizer_flags = stabilizer.get("classification", {})
    if (
        stabilizer.get("result_id")
        != "EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_DESCENT"
        or stabilizer.get("result_state")
        != "PH_STABILIZER_AUTHORITY_AND_GENERIC_PRIMARY_EQUIVARIANCE_CERTIFIED_GAUGE_QUOTIENT_NOT_AUTHORIZED"
        or stabilizer_flags.get("connected_background_stabilizer_certified")
        is not True
        or stabilizer_flags.get("full_SO42_stabilizer_rejected") is not True
        or stabilizer_flags.get("generic_axial_polar_primary_equivariance_certified")
        is not True
        or stabilizer_flags.get("generic_axial_polar_Lee_Wald_invariance_certified")
        is not True
        or stabilizer_flags.get("universal_stabilizer_nullity_refuted") is not True
        or stabilizer_flags.get("Taub_zero_derived_sector_complete") is not False
        or stabilizer_flags.get("absolute_residual_gauge_quotient_certified")
        is not False
        or stabilizer_flags.get("cyclic_BV_enhancement_certified") is not False
        or stabilizer_flags.get("quantum_claim") is not False
    ):
        raise ValueError("Plebanski-Hacyan stabilizer authority drifted")
    return {
        "inclusion": inclusion,
        "quadratic": quadratic,
        "cartan": cartan,
        "a104": a104,
        "triangle": triangle,
        "functor": functor,
        "polar": polar,
        "polar_replay": polar_replay,
        "stabilizer": stabilizer,
        "inclusion_evidence": _committed_evidence(inclusion),
        "quadratic_evidence": _committed_evidence(quadratic),
        "triangle_evidence": _pinned_path(
            TRIANGLE_PREFLIGHT, TRIANGLE_PREFLIGHT_COMMIT
        ),
        "functor_evidence": _pinned_path(
            RELATIVE_FUNCTOR_PREFLIGHT, RELATIVE_FUNCTOR_PREFLIGHT_COMMIT
        ),
        "polar_lift_evidence": _pinned_path(POLAR_LIFT, POLAR_LIFT_COMMIT),
        "stabilizer_evidence": _pinned_path(
            PH_STABILIZER, PH_STABILIZER_COMMIT
        ),
    }


def build() -> dict[str, Any]:
    inputs = _semantic_inputs()
    result = {
        "schema": "quantum-weyl-relative-einstein-weyl-qme-readiness-v1",
        "result_id": "QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS",
        "result_state": "G0_DEPENDENCY_LEDGER_READY_CLASSICAL_TRIANGLE_AND_QME_MISSING",
        "generality_level": "G0",
        "lifecycle_layer": "QUANTUM",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "setting": {
            "theory_pair": "Einstein-Maxwell_to_Weyl-Maxwell",
            "background": "compact_Einstein-Maxwell_product",
            "sector": "complete_standard_harmonic_tangent_before_optional_stabilizer_reduction",
            "boundary_conditions": "compact_periodic_S1_x_S2_fixed_bundle_no_asymptotic_boundary",
            "generator": "D_compact",
        },
        "dependency_refs": {
            "standard_harmonic_inclusion_contribution": _dependency(STANDARD_INCLUSION),
            "quadratic_channel_preflight_contribution": _dependency(QUADRATIC_PREFLIGHT),
            "local_D_Cartan_comparison": _dependency(LOCAL_CARTAN),
            "Berger_global_A104_partial": _dependency(GLOBAL_A104),
            "quantum_team_brief": _dependency(PLANNING_BRIEF),
            "universe_building_roadmap": _dependency(ROADMAP),
            "relative_linear_triangle_preflight": _dependency(TRIANGLE_PREFLIGHT),
            "relative_functor_preflight": _dependency(RELATIVE_FUNCTOR_PREFLIGHT),
            "polar_ungauged_noether_lift": _dependency(POLAR_LIFT),
            "Plebanski_Hacyan_stabilizer_authority": _dependency(PH_STABILIZER),
        },
        "pinned_classical_evidence": {
            "standard_harmonic_inclusion": inputs["inclusion_evidence"],
            "quadratic_channel_preflight": inputs["quadratic_evidence"],
            "relative_linear_triangle_preflight": inputs["triangle_evidence"],
            "relative_functor_preflight": inputs["functor_evidence"],
            "polar_ungauged_noether_lift": inputs["polar_lift_evidence"],
            "Plebanski_Hacyan_stabilizer_authority": inputs[
                "stabilizer_evidence"
            ],
        },
        "classical_import_gate": {
            "status": "NOT_SATISFIED",
            "current_map_disposition": "PARTIAL_GENERIC_AXIAL_AND_POLAR_UNGAUGED_OFFSHELL_PREFLIGHT",
            "required_result_ids": [
                "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
                "EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE",
                "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1",
            ],
            "forbidden_fallback": "do not reconstruct the classical triangle or its maps inside quantum-weyl",
        },
        "shared_relative_row": {
            "setting": "compact Einstein-Maxwell product; complete standard harmonic tangent; fixed compact bundle; before any optional stabilizer reduction",
            "map_iota": "PRINCIPAL_GENERIC_AXIAL_AND_GENERIC_POLAR_UNGAUGED_OFFSHELL_PREFLIGHT_IMPORTED_GLOBAL_V1_OPEN",
            "cofiber": "GENERIC_AXIAL_SOLUTION_COFIBER_CERTIFIED_POLAR_PRERESIDUAL_INCLUSION_CERTIFIED_GLOBAL_COFIBER_OPEN",
            "relative_pairing": "REDUCED_MODE_CLASSICAL_PULLBACK_NONDEGENERATE_NOT_RENORMALIZED",
            "O2": "PARTIAL_QUADRATIC_FIXTURES_ONLY_ARITY_THREE_DISPOSITION_OPEN",
            "residual_action": "OPEN_RELATIVE_EQUIVARIANCE_NOT_EXPORTED",
            "observable_map": "OPEN_RELATIVE_OBSERVABLE_PULLBACK_NOT_EXPORTED",
            "quantum_lift": "ANALYTIC_FRAMEWORK_MISSING",
        },
        "polar_exact_replay": {
            **inputs["polar_replay"],
            "local_Green_time_term_count": 184,
            "local_Green_space_term_count": 184,
            "off_shell_Green_remainder_count": 0,
            "cyclic_BV_chain_map_certified": False,
            "final_residual_descent_certified": False,
        },
        "background_stabilizer_authority": {
            "connected_algebra": "R_H_direct_sum_R_Px_direct_sum_so3",
            "full_SO42_stabilizer_rejected": True,
            "generic_axial_polar_primary_equivariance_certified": True,
            "generic_axial_polar_Lee_Wald_invariance_certified": True,
            "universal_stabilizer_nullity_refuted": True,
            "common_Taub_zero_derived_sector_complete": False,
            "absolute_residual_gauge_quotient_certified": False,
            "authorized_sequence": [
                "local_gauge_quotient",
                "five_generator_background_stabilizer_representation",
                "common_moment_map_Taub_zero_locus",
                "quotient_only_by_a_certified_null_subalgebra",
            ],
        },
        "relative_linear_triangle_gap_ledger": {
            "established": [
                {
                    "sector": "principal_BV_symbol",
                    "status": "CHAIN_MAP_AND_NONCHARACTERISTIC_CONE_CERTIFIED",
                },
                {
                    "sector": "generic_axial_ell_ge_2_all_allowed_k",
                    "status": "STRICT_OFFSHELL_CHAIN_MAP_SOLUTION_COFIBER_AND_DIRECT_PAIRING_CERTIFIED",
                },
                {
                    "sector": "generic_polar_ell_ge_2_all_allowed_k",
                    "status": "UNGAUGED_GHOST_FIELD_EQUATION_IDENTITY_CHAIN_MAP_AND_LOCAL_GREEN_IDENTITY_CERTIFIED",
                },
            ],
            "remaining_for_V1": [
                {
                    "sector": "generic_polar_ell_ge_2",
                    "missing": [
                        "cyclic_BV_enhancement_or_normalized_obstruction",
                        "H_Px_Ji_moment_maps_on_Einstein_q_primary_and_extra_p_primary",
                        "common_Taub_zero_locus_and_null_subalgebra_classification",
                        "post_derived_sector_polar_relative_cofiber_and_pairing",
                    ],
                },
                {
                    "sector": "exceptional_ell_1",
                    "missing": [
                        "relative_offshell_equation_and_identity_row_maps",
                        "exceptional_stabilizer_moment_maps_and_common_Taub_zero_locus",
                        "mapping_cofiber_and_action_derived_cyclic_pairing",
                    ],
                },
                {
                    "sector": "ell_0_and_global_twists",
                    "missing": [
                        "relative_offshell_equation_and_identity_row_maps",
                        "global_stabilizer_moment_maps_and_common_Taub_zero_locus",
                        "fixed_charge_domain_and_global_mapping_cofiber",
                        "action_derived_cyclic_pairing",
                    ],
                },
                {
                    "sector": "global_all_sector_assembly",
                    "missing": [
                        "degreewise_injective_or_derived_replacement_triangle",
                        "global_mapping_cone_nilpotency_and_cohomology",
                        "magnetic_bundle_patching_and_boundary_closure",
                        "relative_linear_triangle_V1_certificate",
                    ],
                },
            ],
        },
        "relative_anomaly_contract": {
            "formal_expression": "[A_rel]=[A_Weyl-iota_* A_Einstein]",
            "status": "NOT_CONSTRUCTED",
            "required_before_definition": [
                "off_shell_BV_chain_map_iota",
                "local_QME_disposition_for_Einstein_and_Weyl",
                "renormalized_observable_algebras",
                "renormalized_restriction_map",
                "antifield_and_boundary_sector_maps",
            ],
            "separate_ledgers": [
                "bulk_local", "antifield", "boundary_corner", "zero_mode",
                "measure_Jacobian", "central_extension", "D_Cartan_component",
            ],
        },
        "framework_ledger": {
            "LOCAL_ALGEBRAIC": {
                "status": "PARTIAL_INPUT_ONLY",
                "evidence": "principal and generic-axial chain maps plus the generic-polar ungauged equation/Noether chain map exist; polar cyclic BV enhancement, residual descent, exceptional/global rows and restored QME do not",
            },
            "EUCLIDEAN_SPECTRAL": {
                "status": "NOT_COMPUTED_RELATIVELY",
                "evidence": "no matched Einstein/Weyl determinant and measure subtraction is imported",
            },
            "REDUCED_MODE": {
                "status": "CLASSICAL_PAIRING_INPUT_ONLY",
                "evidence": "standard harmonic on-shell pullback is nondegenerate but not a renormalized relative pairing",
            },
            "LORENTZIAN_CAUSAL": {
                "status": "ANALYTIC_FRAMEWORK_MISSING",
                "evidence": "partial A104 exists; full A104, q_Cauchy, Cauchy pairing and Hadamard state remain open",
            },
        },
        "qme_and_transfer_gate": {
            "Einstein_QME": "NOT_COMPUTED",
            "Weyl_QME": "NOT_RESTORED",
            "relative_QME_defect": "UNDEFINED_ANALYTICALLY",
            "relative_state_restriction": "UNDEFINED_ANALYTICALLY",
            "relative_D_Cartan_defect": "UNDEFINED_ANALYTICALLY",
            "residual_quantum_transfer_authorized": False,
        },
        "claim_flags": {
            "QUANTUM_RELATIVE_DEPENDENCY_LEDGER": True,
            "POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED": True,
            "PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED": True,
            "CLASSICAL_RELATIVE_TRIANGLE_IMPORTED": False,
            "RELATIVE_ANOMALY_CLASS_DEFINED": False,
            "RELATIVE_QME_RESTORED": False,
            "RELATIVE_PAIRING_RENORMALIZED": False,
            "RELATIVE_HADAMARD_STATE": False,
            "RELATIVE_D_CARTAN_VERDICT": False,
            "QUANTUM_RELATIVE_LIFT": False,
        },
        "verdict": "ANALYTIC_FRAMEWORK_MISSING",
        "next_gate": "IMPORT_EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1_BY_HASH",
        "provenance": {
            "standard_inclusion_setting_id": inputs["inclusion"]["setting_id"],
            "quadratic_preflight_setting_id": inputs["quadratic"]["setting_id"],
            "triangle_preflight_result_id": inputs["triangle"]["result_id"],
            "relative_functor_preflight_result_id": inputs["functor"]["result_id"],
            "polar_lift_result_id": inputs["polar"]["result_id"],
            "stabilizer_authority_result_id": inputs["stabilizer"]["result_id"],
        },
        "claim_boundary": (
            "Registers a G0 quantum dependency ledger for the compact standard-harmonic "
            "Einstein-Maxwell to Weyl-Maxwell relative problem. It imports exact on-shell "
            "inclusion, classical reduced-mode pairing, partial quadratic evidence, and the "
            "principal/generic-axial off-shell triangle preflight and the generic-polar ungauged "
            "ghost-field-equation-identity chain map by content hash. The polar import also "
            "replays its exact polynomial contraction, Noether and chain-map identities, while "
            "retaining the certified 184+184-term local Green identity boundary. The partial "
            "import also applies the correct Plebanski-Hacyan stabilizer authority: the "
            "connected algebra is R H plus R P_x plus so(3), universal nullity is refuted, "
            "and no absolute quotient is authorized before a common moment-map/Taub-zero "
            "derived sector and null subalgebra are certified. The partial "
            "triangle is explicitly rejected as EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1: "
            "polar cyclic BV enhancement and stabilizer descent, exceptional/global relative "
            "rows, and the global all-sector cone remain open. It does not construct "
            "the full off-shell BV triangle, global mapping cofiber, "
            "relative anomaly, QME restoration, renormalized pairing, state restriction, "
            "D-Cartan verdict, particle interpretation or Lorentzian quantum theory."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id")
        != "QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS"
        or result.get("result_state")
        != "G0_DEPENDENCY_LEDGER_READY_CLASSICAL_TRIANGLE_AND_QME_MISSING"
        or result.get("generality_level") != "G0"
        or result.get("verdict") != "ANALYTIC_FRAMEWORK_MISSING"
    ):
        raise ValueError("relative quantum readiness identity drifted")
    gate = result.get("classical_import_gate", {})
    if (
        gate.get("status") != "NOT_SATISFIED"
        or gate.get("current_map_disposition")
        != "PARTIAL_GENERIC_AXIAL_AND_POLAR_UNGAUGED_OFFSHELL_PREFLIGHT"
    ):
        raise ValueError("classical relative import gate was over-promoted")
    row = result.get("shared_relative_row", {})
    if row.get("quantum_lift") != "ANALYTIC_FRAMEWORK_MISSING":
        raise ValueError("relative quantum lift was over-promoted")
    qme = result.get("qme_and_transfer_gate", {})
    if qme.get("residual_quantum_transfer_authorized") is not False:
        raise ValueError("relative residual transfer was authorized before QME restoration")
    flags = result.get("claim_flags", {})
    if (
        flags.get("QUANTUM_RELATIVE_DEPENDENCY_LEDGER") is not True
        or flags.get("POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED") is not True
        or flags.get("PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED") is not True
    ):
        raise ValueError("relative dependency ledger flag missing")
    allowed_true = {
        "QUANTUM_RELATIVE_DEPENDENCY_LEDGER",
        "POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED",
        "PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED",
    }
    if any(value is not False for key, value in flags.items() if key not in allowed_true):
        raise ValueError("relative quantum theorem was over-promoted")
