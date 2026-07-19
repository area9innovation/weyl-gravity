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
LINEAR_TRIANGLE = (
    ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json"
)
RELATIVE_FUNCTOR = (
    ROOT
    / "d_quotient_classical/certificates/RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1.json"
)
POLAR_LIFT = (
    ROOT
    / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json"
)
PH_STABILIZER = (
    ROOT
    / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json"
)
LINEAR_TRIANGLE_COMMIT = "7d2f639c907161e6d7455c8ce0fdc6c1d7c4bc25"
RELATIVE_FUNCTOR_COMMIT = "8ee473621f8c3c1875aaee83f26477c6f6a3686c"
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
    triangle = json.loads(LINEAR_TRIANGLE.read_text())
    functor = json.loads(RELATIVE_FUNCTOR.read_text())
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
    triangle_flags = triangle.get("acceptance_flags", {})
    if (
        triangle.get("result_id") != "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1"
        or triangle.get("claim_status") != "CERTIFIED_OFF_SHELL_LINEAR_TRIANGLE"
        or any(value is not True for value in triangle_flags.values())
        or triangle.get("pairing_disposition", {}).get(
            "standard_pairing_cyclic_map_exists"
        )
        is not False
        or triangle.get("pairing_disposition", {}).get("three_forms_kept_distinct")
        is not True
    ):
        raise ValueError("complete relative linear triangle boundary drifted")
    classification = functor.get("classification", {})
    if (
        functor.get("result_id") != "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1"
        or functor.get("result_state")
        != "LINEAR_OBSERVABLE_PULLBACK_AND_RELATIVE_COFIBER_DETECTORS_CERTIFIED"
        or classification.get("relative_observable_pullback_constructed") is not True
        or classification.get("observable_pullback_is_chain_map") is not True
        or classification.get("observable_pullback_support_local") is not True
        or classification.get("H_product_equivariance_exact") is not True
        or classification.get("cofiber_detectors_constructed") is not True
        or classification.get("full_relative_arity_two_morphism") is not False
        or classification.get("quantum_lift") is not False
    ):
        raise ValueError("relative observable functor boundary drifted")
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
        "triangle_evidence": _pinned_path(LINEAR_TRIANGLE, LINEAR_TRIANGLE_COMMIT),
        "functor_evidence": _pinned_path(RELATIVE_FUNCTOR, RELATIVE_FUNCTOR_COMMIT),
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
        "result_state": "LINEAR_RELATIVE_TRIANGLE_AND_OBSERVABLE_PULLBACK_IMPORTED_NONLINEAR_QME_OPEN",
        "generality_level": "G1_COMPLETE_LINEAR_RELATIVE_COMPLEX_ONE_BACKGROUND",
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
            "relative_linear_triangle": _dependency(LINEAR_TRIANGLE),
            "relative_observable_functor": _dependency(RELATIVE_FUNCTOR),
            "polar_ungauged_noether_lift": _dependency(POLAR_LIFT),
            "Plebanski_Hacyan_stabilizer_authority": _dependency(PH_STABILIZER),
        },
        "pinned_classical_evidence": {
            "standard_harmonic_inclusion": inputs["inclusion_evidence"],
            "quadratic_channel_preflight": inputs["quadratic_evidence"],
            "relative_linear_triangle": inputs["triangle_evidence"],
            "relative_observable_functor": inputs["functor_evidence"],
            "polar_ungauged_noether_lift": inputs["polar_lift_evidence"],
            "Plebanski_Hacyan_stabilizer_authority": inputs[
                "stabilizer_evidence"
            ],
        },
        "classical_import_gate": {
            "status": "LINEAR_GATE_SATISFIED_NONLINEAR_GATE_OPEN",
            "current_map_disposition": "COMPLETE_NONCYCLIC_LINEAR_TRIANGLE_AND_OBSERVABLE_PULLBACK_IMPORTED",
            "received_result_ids": [
                "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
                "RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1",
            ],
            "remaining_result_ids": [
                "EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE"
            ],
            "forbidden_fallback": "do not reconstruct the classical triangle or its maps inside quantum-weyl",
        },
        "shared_relative_row": {
            "setting": "compact Einstein-Maxwell product; complete standard harmonic tangent; fixed compact bundle; before any optional stabilizer reduction",
            "map_iota": "COMPLETE_ALL_ROW_SUPPORT_LOCAL_NONCYCLIC_LINEAR_TRIANGLE_IMPORTED",
            "cofiber": "SUPPORT_LOCAL_MAPPING_COFIBER_AND_EXACT_EXTRA_DETECTORS_IMPORTED",
            "relative_pairing": "THREE_ACTION_FORMS_DISTINCT_STANDARD_CYCLIC_MAP_OBSTRUCTED_NOT_RENORMALIZED",
            "O2": "PARTIAL_QUADRATIC_FIXTURES_ONLY_ARITY_THREE_DISPOSITION_OPEN",
            "residual_action": "H_PRODUCT_EQUIVARIANCE_IMPORTED_FINAL_RESIDUAL_QUOTIENT_OPEN",
            "observable_map": "SUPPORT_LOCAL_LINEAR_BRST_DGA_PULLBACK_IMPORTED",
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
                    "sector": "complete_all_row_linear_triangle",
                    "status": "SUPPORT_LOCAL_NONCYCLIC_CHAIN_MAP_CERTIFIED",
                },
                {
                    "sector": "relative_mapping_cofiber",
                    "status": "GLOBAL_ENDPOINTS_AND_H_PRODUCT_EQUIVARIANCE_CERTIFIED",
                },
                {
                    "sector": "linear_local_observables",
                    "status": "CONTRAVARIANT_SUPPORT_LOCAL_BRST_DGA_PULLBACK_CERTIFIED",
                },
                {
                    "sector": "solution_cohomology_detectors",
                    "status": "EXTRA_COFIBER_DETECTORS_CERTIFIED_REDUCED_MODE",
                },
            ],
            "remaining_beyond_V1": [
                {
                    "sector": "cyclic_relative_structure",
                    "missing": [
                        "standard_pairing_cyclic_map_or_replacement",
                        "renormalized_relative_pairing",
                    ],
                },
                {
                    "sector": "nonlinear_relative_morphism",
                    "missing": [
                        "complete_f2",
                        "arity_three_relative_identity",
                    ],
                },
                {
                    "sector": "quantum_relative_lift",
                    "missing": [
                        "matched_Einstein_and_Weyl_QME_dispositions",
                        "renormalized_observable_pullback",
                        "causal_state_restriction",
                    ],
                },
            ],
        },
        "relative_anomaly_contract": {
            "formal_expression": "[A_rel]=[A_Weyl-iota_* A_Einstein]",
            "status": "CLASSICAL_PULLBACK_AVAILABLE_QUANTUM_CLASS_UNDEFINED",
            "required_before_definition": [
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
                "status": "COMPLETE_LINEAR_CLASSICAL_IMPORT_INTERACTING_QUANTUM_OPEN",
                "evidence": "the all-row support-local noncyclic triangle, mapping cofiber, H_product equivariance and observable pullback are imported; a cyclic relative structure, f2/arity three and matched QME dispositions remain open",
            },
            "EUCLIDEAN_SPECTRAL": {
                "status": "NOT_COMPUTED_RELATIVELY",
                "evidence": "no matched Einstein/Weyl determinant and measure subtraction is imported",
            },
            "REDUCED_MODE": {
                "status": "CLASSICAL_COFIBER_DETECTORS_IMPORTED",
                "evidence": "exact coefficient detectors separate the certified extra cofibers but are not support-local spacetime, Peierls or renormalized quantum observables",
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
            "CLASSICAL_RELATIVE_TRIANGLE_IMPORTED": True,
            "RELATIVE_OBSERVABLE_PULLBACK_IMPORTED": True,
            "RELATIVE_EQUIVARIANCE_IMPORTED": True,
            "RELATIVE_ANOMALY_CLASS_DEFINED": False,
            "RELATIVE_QME_RESTORED": False,
            "RELATIVE_PAIRING_RENORMALIZED": False,
            "RELATIVE_HADAMARD_STATE": False,
            "RELATIVE_D_CARTAN_VERDICT": False,
            "QUANTUM_RELATIVE_LIFT": False,
        },
        "verdict": "ANALYTIC_FRAMEWORK_MISSING",
        "next_gate": "IMPORT_EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_AND_COMPUTE_MATCHED_QME",
        "provenance": {
            "standard_inclusion_setting_id": inputs["inclusion"]["setting_id"],
            "quadratic_preflight_setting_id": inputs["quadratic"]["setting_id"],
            "triangle_result_id": inputs["triangle"]["result_id"],
            "relative_functor_result_id": inputs["functor"]["result_id"],
            "polar_lift_result_id": inputs["polar"]["result_id"],
            "stabilizer_authority_result_id": inputs["stabilizer"]["result_id"],
        },
        "claim_boundary": (
            "Registers a G1 complete linear relative import for the compact standard-harmonic "
            "Einstein-Maxwell to Weyl-Maxwell relative problem. It imports exact on-shell "
            "inclusion, classical reduced-mode pairing, partial quadratic evidence, and the "
            "all-row support-local noncyclic triangle and its mapping cofiber by content hash. "
            "The polar precursor also "
            "replays its exact polynomial contraction, Noether and chain-map identities, while "
            "retaining the certified 184+184-term local Green identity boundary. The partial "
            "import also applies the correct Plebanski-Hacyan stabilizer authority: the "
            "connected algebra is R H plus R P_x plus so(3), universal nullity is refuted, "
            "and no absolute quotient is authorized before a common moment-map/Taub-zero "
            "derived sector and null subalgebra are certified. The final linear observable "
            "functor supplies a contravariant support-local BRST-DGA pullback, exact H_product "
            "equivariance and reduced cofiber detectors. The standard-pairing cyclic route, "
            "complete f2, arity three and final residual quotient remain open. It does not construct "
            "a relative anomaly class, QME restoration, renormalized pairing, state restriction, "
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
        != "LINEAR_RELATIVE_TRIANGLE_AND_OBSERVABLE_PULLBACK_IMPORTED_NONLINEAR_QME_OPEN"
        or result.get("generality_level")
        != "G1_COMPLETE_LINEAR_RELATIVE_COMPLEX_ONE_BACKGROUND"
        or result.get("verdict") != "ANALYTIC_FRAMEWORK_MISSING"
    ):
        raise ValueError("relative quantum readiness identity drifted")
    gate = result.get("classical_import_gate", {})
    if (
        gate.get("status") != "LINEAR_GATE_SATISFIED_NONLINEAR_GATE_OPEN"
        or gate.get("current_map_disposition")
        != "COMPLETE_NONCYCLIC_LINEAR_TRIANGLE_AND_OBSERVABLE_PULLBACK_IMPORTED"
    ):
        raise ValueError("classical relative import gate drifted")
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
        or flags.get("CLASSICAL_RELATIVE_TRIANGLE_IMPORTED") is not True
        or flags.get("RELATIVE_OBSERVABLE_PULLBACK_IMPORTED") is not True
        or flags.get("RELATIVE_EQUIVARIANCE_IMPORTED") is not True
    ):
        raise ValueError("relative dependency ledger flag missing")
    allowed_true = {
        "QUANTUM_RELATIVE_DEPENDENCY_LEDGER",
        "POLAR_UNGAUGED_NOETHER_LIFT_IMPORTED",
        "PLEBANSKI_HACYAN_STABILIZER_AUTHORITY_IMPORTED",
        "CLASSICAL_RELATIVE_TRIANGLE_IMPORTED",
        "RELATIVE_OBSERVABLE_PULLBACK_IMPORTED",
        "RELATIVE_EQUIVARIANCE_IMPORTED",
    }
    if any(value is not False for key, value in flags.items() if key not in allowed_true):
        raise ValueError("relative quantum theorem was over-promoted")
