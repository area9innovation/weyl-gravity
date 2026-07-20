#!/usr/bin/env python3
"""Generate the fail-closed classical causal/gauge/carrier atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "classical-causal-atlas-fragment.json"
VACUUM_EVIDENCE = HERE / "CLASSICAL_VACUUM_CYLINDER_ATLAS_EVIDENCE_V1.json"
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
AXES = ["causal", "symplectic", "nonlinear", "observational", "quantum"]

LEGACY_VACUUM = {
    "four_flags": ROOT / "covariant_completion/certificates/four_flag_closure_status.json",
    "gram_transport": ROOT / "covariant_completion/certificates/covariant_gram_transport.json",
    "one_particle": ROOT / "analytic_completion/certificates/one_particle_krein.json",
    "positive_frequency": ROOT / "covariant_completion/certificates/positive_frequency_transform.json",
}
CERTS = {
    "vacuum": VACUUM_EVIDENCE,
    "green_transfer_theorem": ROOT / "d_quotient_classical/certificates/GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json",
    "weak_background_stability": ROOT / "d_quotient_classical/certificates/WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1.json",
    "vacuum_WZ_D_Cartan": ROOT / "d_quotient_classical/certificates/WESS_ZUMINO_D_CARTAN_CONTRACTION_V1.json",
    "vacuum_WZ_causal_trace_obstruction": ROOT / "d_quotient_classical/certificates/TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json",
    "complex_compensator_action_preflight": ROOT / "d_quotient_classical/certificates/COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json",
    "complex_compensator_causal_parent": ROOT / "d_quotient_classical/certificates/COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1.json",
    "complex_compensator_candidate_a_obstruction": ROOT / "d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1.json",
    "complex_compensator_candidate_b_obstruction": ROOT / "d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1.json",
    "complex_compensator_candidate_ab_neither": ROOT / "d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1.json",
    "complex_compensator_minimal_action_no_go": ROOT / "d_quotient_classical/certificates/COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1.json",
    "complex_compensator_active_clock_px2_no_go": ROOT / "d_quotient_classical/certificates/COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1.json",
    "complex_compensator_active_clock_px2_freeze_audit": ROOT / "d_quotient_classical/certificates/COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json",
    "complex_compensator_active_clock_background_stability": ROOT / "d_quotient_classical/certificates/COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1.json",
    "Berger_green": ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json",
    "Berger_bikernel_support_gate": ROOT / "d_quotient_classical/certificates/BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1.json",
    "Berger_Cartan": ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json",
    "Berger_charge": ROOT / "d_quotient_classical/certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json",
    "Berger_redshift": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "Berger_projector": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json",
    "Berger_bridge1_disposition": ROOT / "d_quotient_classical/certificates/BERGER_BRIDGE1_ADMISSIBLE_CARRIER_DISPOSITION_V1.json",
    "Berger_apparatus_Z2_receiver_disposition": ROOT / "d_quotient_classical/certificates/BERGER_APPARATUS_Z2_INTEGRABILITY_RECEIVER_DISPOSITION_V1.json",
    "Berger_q26_Cauchy_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json",
    "Berger_q26_six_row_cyclic_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1.json",
    "Berger_q26_module_closure_bound": ROOT / "d_quotient_classical/certificates/BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1.json",
    "Berger_q26_canonical_104_cone_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1.json",
    "Berger_q26_canonical_cone_next_defect": ROOT / "d_quotient_classical/certificates/BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1.json",
    "Berger_q26_fully_mixed_cone_SDR_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1.json",
    "Berger_q26_noncone_rational_nilpotence_feasibility": ROOT / "d_quotient_classical/certificates/BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_FEASIBILITY_V1.json",
    "Berger_q26_noncone_evolution_extension_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_Q26_104_ROW_NONCONE_EVOLUTION_EXTENSION_OBSTRUCTION_V1.json",
    "Nariai_conformal": ROOT / "d_quotient_classical/certificates/CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1.json",
    "Nariai_single": ROOT / "d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json",
    "Nariai_bridge_disposition": ROOT / "d_quotient_classical/certificates/NARIAI_CURVATURE_METRIC_BRIDGE_DISPOSITION_V1.json",
    "Nariai_transverse": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json",
    "Nariai_transverse_KS_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1.json",
    "Nariai_incidence": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1.json",
    "Nariai_PBW_gate": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1.json",
    "Nariai_jet_aware_parent": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json",
    "Nariai_first_order_schur": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FIRST_ORDER_SCHUR_SOLVE_V1.json",
    "Nariai_Phi_only_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_ONLY_SHIFTED_CHAIN_OBSTRUCTION_V1.json",
    "Nariai_incidence_L1_rigidity": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_INCIDENCE_L1_RIGIDITY_V1.json",
    "Nariai_normalized_L0_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_NORMALIZED_L0_COUPLED_OBSTRUCTION_V1.json",
    "Nariai_K_admissibility": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_K_SENSITIVITY_ADMISSIBILITY_V1.json",
    "Nariai_Phi2_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PHI_SECOND_ORDER_OBSTRUCTION_V1.json",
    "Nariai_PBW_associativity": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1.json",
    "Nariai_coefficient_jets": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1.json",
    "Nariai_splitting_jets": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1.json",
    "Nariai_middle_replay": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1.json",
    "Nariai_factorized_schur": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1.json",
    "Nariai_upper_chain": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1.json",
    "Nariai_endpoint_target": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1.json",
    "Nariai_action_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json",
    "Nariai_rank310_SDR_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1.json",
    "Nariai_formal_metric_green_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FORMAL_METRIC_GREEN_VARIATION_V1.json",
    "Nariai_global_HPL_rank310_causal_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1.json",
    "Nariai_finite_HPL_incidence": ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1.json",
    "Nariai_KS_four_block_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1.json",
    "Nariai_six_block_HPL": ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1.json",
    "Nariai_KS_common_slab": ROOT / "d_quotient_classical/certificates/NARIAI_KS_COMMON_SLAB_CAUSAL_DOMAIN_V1.json",
    "Einstein_metric_biwave": ROOT / "d_quotient_classical/certificates/EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
    "Nariai_KS_rank310_transfer": ROOT / "d_quotient_classical/certificates/NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1.json",
    "Bach_parent": ROOT / "d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json",
    "Bach_rank310_SDR": ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_NATURAL_SDR_V1.json",
    "Bach_metric_biwave": ROOT / "d_quotient_classical/certificates/BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
    "Bach_rank310_causal": ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_CAUSAL_TRANSFER_V1.json",
    "candidate13_local_upgrade_obstruction": ROOT / "d_quotient_classical/certificates/CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1.json",
    "five_current_de_rham_carrier": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1.json",
    "five_current_de_rham_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1.json",
    "relative_238_cyclic_rank_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_238_ROW_CYCLIC_RANK_OBSTRUCTION_V1.json",
    "relative_316_cotangent_completion": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1.json",
    "relative_316_block_q2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_BLOCK_DIAGONAL_Q2_OBSTRUCTION_V1.json",
    "relative_derived_taub_zero_pullback": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_DERIVED_TAUB_ZERO_PULLBACK_PREFLIGHT_V1.json",
    "relative_reduced_taub_factorization": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_REDUCED_TAUB_FACTORIZATION_V1.json",
    "relative_shifted_current_cone_preflight": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_SHIFTED_CURRENT_CONE_PREFLIGHT_V1.json",
    "relative_full_five_current_pbw": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_PBW_EXPORT_V1.json",
    "relative_order_zero_lift_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1.json",
    "relative_endpoint_normalization": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1.json",
    "relative_order_one_invariant_ansatz": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_INVARIANT_ANSATZ_V1.json",
    "relative_hessian_second_current_input": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_HESSIAN_SECOND_CURRENT_INPUT_V1.json",
    "relative_full_five_current_second_jet": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_SECOND_JET_EXPORT_V1.json",
    "relative_order_one_chain_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_CHAIN_OBSTRUCTION_V1.json",
    "relative_order_two_obstruction_sensitivity": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_TWO_OBSTRUCTION_SENSITIVITY_V1.json",
    "relative_order_two_top_descent_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_TWO_TOP_DESCENT_OBSTRUCTION_V1.json",
    "relative_order_three_descent_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_THREE_DESCENT_OBSTRUCTION_V1.json",
    "relative_all_order_endpoint_pairing_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ALL_ORDER_ENDPOINT_PAIRING_OBSTRUCTION_V1.json",
    "relative_compensated_endpoint_chain_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPENSATED_ENDPOINT_CHAIN_OBSTRUCTION_V1.json",
    "cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _legacy_id(path: Path) -> str:
    payload = json.loads(path.read_text())
    return str(payload.get("result_id", payload.get("schema", "UNIDENTIFIED")))


def vacuum_evidence() -> dict[str, Any]:
    records = {name: json.loads(path.read_text()) for name, path in LEGACY_VACUUM.items()}
    if not records["four_flags"]["flags"]["final_covariant_H4"]:
        raise AssertionError("vacuum covariant closure changed")
    if not records["gram_transport"]["status"]:
        raise AssertionError("vacuum Gram transport changed")
    if records["one_particle"]["classification"] != "infinite-index Krein space":
        raise AssertionError("vacuum one-particle carrier changed")
    if not (
        records["positive_frequency"]["harmonic_transform_isometry_on_algebraic_core"]
        and records["positive_frequency"]["normalized_metric_modes_map_to_unit_coefficients"]
        and records["positive_frequency"]["krein_signs"] == {"E": 1, "A": -1, "L": -1}
    ):
        raise AssertionError("vacuum positive-frequency transform changed")
    return {
        "schema": "classical-vacuum-cylinder-atlas-evidence-v1",
        "result_id": "CLASSICAL_VACUUM_CYLINDER_ATLAS_EVIDENCE_V1",
        "result_state": "VACUUM_CYLINDER_CAUSAL_SYMPLECTIC_AND_RESIDUAL_CARRIER_EVIDENCE_WRAPPED",
        "dependencies": {
            name: {"path": str(path.relative_to(ROOT)), "artifact_id": _legacy_id(path), "sha256": _sha(path)}
            for name, path in LEGACY_VACUUM.items()
        },
        "flags": {
            "causal_quasi_isomorphism": True,
            "EAL_Krein_carrier": True,
            "pairing_transport": True,
            "residual_H4_two_deformation_classes": True,
            "one_particle_residual_cohomology_zero": True,
            "Hadamard_or_interacting_quantum_theorem": False,
        },
        "claim_boundary": "This is a content-addressed adapter for legacy certificates that use schema identifiers instead of result_id. It adds no theorem and does not turn E/A/L modes or W-square deformation classes into quantum particles.",
    }


def _evidence(*names: str) -> list[dict[str, str]]:
    rows = []
    for name in names:
        path = CERTS[name]
        payload = json.loads(path.read_text())
        rows.append({"path": str(path.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": _sha(path)})
    return rows


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _second(bounded: tuple[str, str], secular: tuple[str, str], causal: tuple[str, str]) -> dict[str, Any]:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": _claim(*bounded),
        "smooth_secular": _claim(*secular),
        "causal_retarded": _claim(*causal),
    }


def _entry(identifier: str, scope: dict[str, Any], descriptions: dict[str, str], dispersion: tuple[str, str], lee_wald: tuple[str, str], taub: tuple[str, str], resonance: tuple[str, str], second: dict[str, Any], evidence: list[dict[str, str]], boundary: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "scope": scope,
        "descriptions": descriptions,
        "mode_data": {
            "dispersion": _claim(*dispersion),
            "lee_wald": _claim(*lee_wald),
            "taub_maps": _claim(*taub),
            "resonance": _claim(*resonance),
            "second_order": second,
        },
        "evidence": evidence,
        "claim_boundary": boundary,
    }


VACUUM = {
    "theory": "free pure-Weyl gravity",
    "background": "unit conformal cylinder R_t x S3",
    "boundaries": "closed compact Cauchy surface S3; no spatial boundary",
    "charge_sector": "selected closed-universe absolute residual SO(4,2) quotient including D",
}
BERGER = {
    "theory": "pure-Weyl gravity plus two standard-sign rotating conformal scalars and retained Maxwell sector",
    "background": "fixed rational positive Berger clock",
    "boundaries": "R_t x compact Berger S3; no spatial boundary",
    "charge_sector": "fixed-coupling Taub/moment-map-zero clock sector; K_Berger=D-omega R is the stationary unary generator",
}
NARIAI = {
    "theory": "free pure-Weyl metric BV complex and normal-adjoint-tractor parent",
    "background": "unit Nariai dS2 x S2 and declared bounded smooth conformal orbit",
    "boundaries": "global compact Cauchy surface S1 x S2; no timelike boundary",
    "charge_sector": "unquotiented linear gauge complex; no residual state quotient imported",
}


def _scope(base: dict[str, Any], **updates: Any) -> dict[str, Any]:
    value = dict(base)
    value.update(updates)
    return value


def entries() -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    family_data = {
        "E": ("+1", "Einstein/lower-TT family, both chiralities"),
        "A": ("-1", "vector-descendant family, both chiralities"),
        "L": ("-1", "upper-TT/logarithmic family, both chiralities"),
    }
    for family, (sign, carrier) in family_data.items():
        values.append(_entry(
            f"classical.vacuum_cylinder.one_particle.{family.lower()}",
            _scope(VACUUM, carrier=carrier, degree=1, parity="both chiralities", ell="all allowed SO(4) levels", m="all", k="not a separate cylinder label", omega="positive and negative cylinder-energy shells"),
            {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
            ("CERTIFIED", f"The {family} all-level cylinder mode family is part of the exact E/A/L causal Cauchy carrier."),
            ("CERTIFIED", f"The normalized one-particle Krein sign is {sign} on {family}."),
            ("CERTIFIED", "The selected absolute residual CE complex has zero one-particle cohomology; this does not erase the causal solution family."),
            ("NOT_APPLICABLE", "No second-order resonance claim is needed for this linear carrier entry."),
            _second(("OPEN", "No all-mode bounded second-order classification."), ("OPEN", "No all-mode smooth-secular second-order classification."), ("OPEN", "No nonlinear retarded second-order classification.")),
            _evidence("vacuum", "green_transfer_theorem", "cone"),
            "This is a classical causal one-particle mode family with an indefinite Krein sign, not a positive residual particle and not either W-square degree-four class.",
        ))
    for chirality in ("plus", "minus"):
        symbol = "+" if chirality == "plus" else "-"
        values.append(_entry(
            f"classical.vacuum_cylinder.deformation.w_{chirality}_squared",
            _scope(VACUUM, carrier=f"ghost-dressed degree-four deformation/vertex class [W_{symbol}^2], not a one-particle mode", degree=4, parity=f"chirality {symbol}", ell="NOT_APPLICABLE", m="NOT_APPLICABLE", k="NOT_APPLICABLE", omega="centered total residual weight zero"),
            {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
            ("NOT_APPLICABLE", "A composite deformation class has no one-particle dispersion relation."),
            ("CERTIFIED", "The complementary-degree residual pairing is positive definite and normalized to I2 on the two chiral classes."),
            ("CERTIFIED", "The covariant and residual H4 transports identify exactly these two classes."),
            ("NOT_APPLICABLE", "No propagation resonance is assigned to a deformation class."),
            _second(("NOT_APPLICABLE", "Not a first-order tangent mode."), ("NOT_APPLICABLE", "Not a first-order tangent mode."), ("NOT_APPLICABLE", "Not a first-order tangent mode.")),
            _evidence("vacuum", "green_transfer_theorem"),
            "This is a vertex/deformation class. It must never be relabelled as a positive-norm graviton or one-particle state.",
        ))
    values.append(_entry(
        "classical.vacuum_cylinder.local_bv.wz_tau_adic_d_cartan",
        _scope(
            VACUUM,
            theory="formal tau-adic Wess-Zumino-compensator extension of pure-Weyl minimal BV",
            charge_sector="closed-universe derived residual sector P_der with raw D_compact constrained",
            carrier="support-local formal tau-adic dressed-jet algebra with the contractible (tau,omega,omega_star,tau_hat_star) quartet; not a mode or particle carrier",
            degree="all local BV ghost/antifield degrees in the imported minimal complex",
            parity="graded BV parity",
            ell="NOT_APPLICABLE",
            m="NOT_APPLICABLE",
            k="arbitrary support-local covariant jets",
            omega="all cylinder D weights; exact fixtures at -2,0,3 and paired +/-2",
        ),
        {"causal": "NOT_APPLICABLE", "symplectic": "CERTIFIED", "nonlinear": "NOT_APPLICABLE", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NOT_APPLICABLE", "This is a local BV quartet and Cartan contraction, not a propagating mode family."),
        ("CERTIFIED", "The dressed canonical odd BV pairing, quartet differential, homotopy and opposite-D-weight cyclicity identities are exact."),
        ("CERTIFIED", "On P_der, raw D_compact=partial_t has zero Weyl component and the tau-adic augmentation projection is D-equivariant; the same projection is obstructed for Minkowski dilation with sigma_D=-1."),
        ("NOT_APPLICABLE", "No harmonic resonance is assigned to a formal local BV quartet."),
        _second(("NOT_APPLICABLE", "Not a first-order tangent mode."), ("NOT_APPLICABLE", "Not a first-order tangent mode."), ("NOT_APPLICABLE", "No causal second-order statement follows from the local quartet contraction.")),
        _evidence("vacuum_WZ_D_Cartan"),
        "This LOCAL-ALGEBRAIC entry closes only the same-background classical Q0/iota_D0/L_D0 and cyclic contraction requested for the vacuum-cylinder raw-D_compact row. Wess-Zumino tau is not the Berger clock, raw D_compact is not K_Berger, and the Minkowski D_M projection is explicitly not exported. Complete Q1, iota_D1, L_D1, renormalized products, the local-insertion-to-Cartan map, quantum defect classification, residual quantum transfer, Hadamard data, positivity and particles remain OPEN or NOT_APPLICABLE.",
    ))
    values.append(_entry(
        "classical.vacuum_cylinder.local_bv.wz_tau_adic_causal_trace_obstruction",
        _scope(
            VACUUM,
            theory="formal tau-adic Wess-Zumino-compensator extension of the classical pure-Weyl BV complex",
            charge_sector="complete compact-support unary carrier before any physical or residual quotient",
            carrier="strict 386-row causal BV carrier plus the convention-correct tau/tau_hat_star extension; not a mode or particle carrier",
            degree="unary BV degrees -1,0,1,2; obstruction represented at degree 0",
            parity="even scalar dressed-trace direction",
            ell="all compact-support scalar profiles; not harmonic-reduced",
            m="all compact-support scalar profiles; not harmonic-reduced",
            k="all local covectors",
            omega="all compact-support time profiles",
        ),
        {"causal": "OBSTRUCTED", "symplectic": "CERTIFIED", "nonlinear": "NOT_APPLICABLE", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("OBSTRUCTED", "The classical dressed conformal trace has identically zero Bach Hessian and no Green inverse on the complete tau-adic carrier."),
        ("CERTIFIED", "The convention-correct scalar change is BV canonical and leaves a nondegenerate u/u_star pairing; this does not contract the u class."),
        ("NOT_APPLICABLE", "This is a compact-support unary homology obstruction, not a Taub or residual-charge calculation."),
        ("NOT_APPLICABLE", "No harmonic resonance or particle frequency is assigned to this local BV carrier obstruction."),
        _second(("NOT_APPLICABLE", "Not a second-order tangent problem."), ("NOT_APPLICABLE", "Not a second-order tangent problem."), ("OBSTRUCTED", "An advanced or retarded identity q0 Lambda+Lambda q0=1 would produce a smooth primitive for a compact trace profile chosen outside the finite global conformal-Killing-factor span.")),
        _evidence("vacuum_WZ_causal_trace_obstruction"),
        "The exact obstruction covers the declared class generated by the mandated tau/tau_hat_star rows, finite-order support-local cyclic isomorphisms, contractible nonminimal or generalized-auxiliary additions, gauge-fermion transforms and finite differential cyclic SDR lifts. The arbitrary compact-support dressed trace is not a finite zero mode. Adding a second conformal gauge generator or a classical dressed-trace kinetic term can evade the theorem only by changing the theory. No full tau-adic Hadamard kernel, positivity, Lorentzian QME, particle, scattering or unitarity claim is made.",
    ))
    values.append(_entry(
        "classical.complex_compensator.local_bv.action_quartet_preflight",
        _scope(
            VACUUM,
            theory="pure-Weyl gravity plus one formal polar complex compensator with global internal U(1)",
            background="local covariant rho!=0 chart; no spacetime background selected",
            boundaries="integrated local identities modulo compact-support total derivatives",
            charge_sector="unreduced local Diff semidirect Weyl BV complex; global U(1) is not gauged",
            carrier="complete declared two-scalar-derivative/four-curvature-derivative local action and its 18 generator-type minimal/nonminimal BV cotangent carrier; not a mode or particle carrier",
            degree="all local BV ghost/antifield degrees; phase and invariant metric at degree zero",
            parity="even scalar sector plus independent even/odd curvature couplings",
            ell="NOT_APPLICABLE",
            m="NOT_APPLICABLE",
            k="arbitrary local covariant jets within the declared derivative bound",
            omega="NOT_APPLICABLE",
        ),
        {"causal": "NOT_APPLICABLE", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "OPEN"},
        ("NOT_APPLICABLE", "No background or principal operator is selected, so no dispersion relation is assigned."),
        ("CERTIFIED", "The action-derived odd cotangent pairing, Weyl quartet and both nonminimal cotangent doublets are exact and nondegenerate after reduction."),
        ("NOT_APPLICABLE", "The global U(1) current is classified locally, but no background Taub or time-generator charge is computed."),
        ("NOT_APPLICABLE", "No harmonic or nonlinear resonance problem is posed at this local action gate."),
        _second(("NOT_APPLICABLE", "Not a background tangent-cone calculation."), ("NOT_APPLICABLE", "Not a background tangent-cone calculation."), ("NOT_APPLICABLE", "Causal analysis is the next changed-action gate.")),
        _evidence("complex_compensator_action_preflight"),
        "The formal rho!=0 polar theory permits independent kappa_r and kappa_theta: kappa_r<0 and kappa_theta>0 give positive Einstein and phase residues only after the exact radial/Weyl quartet contraction. The regular Cartesian-analytic |nabla Phi|^2 subfamily kappa_r=kappa_theta is sign-obstructed. The unequal-coefficient action is not regular at Phi=0, rho=f is a gauge chart rather than spontaneous Weyl breaking, and f is introduced rather than generated. Local U(1) is absent; adding it requires a connection and a new complete BV sector. No background, causal Green, Hadamard, anomaly, QME, particle, scattering or unitarity claim follows.",
    ))
    values.append(_entry(
        "classical.complex_compensator.vacuum_cylinder.changed_action_causal_parent",
        _scope(
            VACUUM,
            theory="changed formal rho!=0 unequal-kinetic polar complex-compensator gravity; not strict pure-Weyl gravity",
            charge_sector="unreduced Diff semidirect Weyl BV action with global U(1); raw-D scalar charge recomputed before any residual or quantum quotient",
            carrier="superseded rank-390 direct-sum proposal plus the exact action-derived auxiliary h/psi Hessian and its consistent homogeneous scalar restriction; not a particle identification",
            degree="local BV action in all degrees; physical-sign obstruction in the degree-zero (u,psi) block",
            parity="real even scalar auxiliary/Jordan sector",
            ell="all scalar harmonics, with a decisive homogeneous ell=0 full-Hessian sector",
            m="all",
            k="all local covectors",
            omega="repeated P2=Box+2 roots; ell=0 has real D roots +/-sqrt(2) and size-two Jordan blocks",
        ),
        {"causal": "OBSTRUCTED", "symplectic": "OBSTRUCTED", "nonlinear": "NOT_APPLICABLE", "observational": "NO_CERTIFIED_MAP", "quantum": "OPEN"},
        ("OBSTRUCTED", "The reduced scalar block has exact Green inverses, but the complete rank-390 direct-sum promotion omitted nonzero h-psi rows and is superseded."),
        ("OBSTRUCTED", "The action-derived homogeneous Lee-Wald form is nondegenerate with velocity inertia (1,1), so Candidate A fails the required physical-sign gate."),
        ("OBSTRUCTED", "Raw D is Hamiltonian with a both-sign nonconstant charge; its zero-charge set is only a proper quadratic cone."),
        ("CERTIFIED", "The full-Hessian scalar restriction has repeated real ell=0 roots +/-sqrt(2) with size-two Jordan blocks."),
        _second(("NOT_APPLICABLE", "Candidate A terminates at the unary physical-sign gate."), ("NOT_APPLICABLE", "Candidate A terminates at the unary physical-sign gate."), ("OBSTRUCTED", "No complete mixed-metric causal parent is promoted after the terminal physical-sign failure.")),
        _evidence("complex_compensator_action_preflight", "vacuum_WZ_causal_trace_obstruction", "complex_compensator_causal_parent", "complex_compensator_candidate_a_obstruction"),
        "COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1 supersedes the earlier complete-direct-sum rank-390 promotion. The rational double-root tuning, trace Schur complement H_u=-(Box+2)^2/8, reduced iterated Green identity and phase wave remain exact subclaims. The auxiliary action exposes L_ab psi=(nabla_a nabla_b-g_ab Box-Ric_ab)psi, which changes the strict complement on the non-Einstein cylinder. A consistent sector satisfying both metric and auxiliary equations has split Lee-Wald kinetic inertia, real repeated D roots and an indefinite D Hamiltonian. The frozen positive Berger fixture also has a nonzero changed-action Euler residual. Candidate A is therefore OBSTRUCTED; no compatible complex structure, Hadamard/Feynman state, anomaly/QME, particle, scattering or unitarity conclusion follows.",
    ))
    values.append(_entry(
        "classical.complex_compensator.vacuum_cylinder.unimodular_threeform_candidate_b",
        _scope(
            VACUUM,
            theory="changed formal rho!=0 complex-compensator gravity with a Henneaux-Teitelboim three-form sector; not strict pure-Weyl gravity",
            charge_sector="small reducible three-form gauge group with all H3 flux and constant lambda_HT sectors retained; no fixed-flux superselection imposed",
            carrier="action-derived reducible A3/C2/C1/C0 BV tower plus the dressed metric trace and global flux/multiplier Lee-Wald pair; not a particle carrier",
            degree="local BV tower through ghost number three and its cotangent rows; decisive degree-zero (u,a,lambda_HT) block",
            parity="real even three-form potential and multiplier with alternating reducibility-ghost parity",
            ell="all local scalar traces; harmonic spatial H3 generator is the decisive global sector",
            m="all",
            k="all local covectors plus the compact-support Hc4 class",
            omega="polynomial kernel u=(partial_t/2)a; zero-frequency H3 flux",
        ),
        {"causal": "OBSTRUCTED", "symplectic": "OBSTRUCTED", "nonlinear": "NOT_APPLICABLE", "observational": "NO_CERTIFIED_MAP", "quantum": "OPEN"},
        ("OBSTRUCTED", "The frozen non-Einstein unit cylinder is off shell for every lambda_HT, and the linear HT Hessian has a nonzero polynomial kernel over Q(D)."),
        ("OBSTRUCTED", "The ambient flux/multiplier Lee-Wald matrix is nondegenerate, but the frozen lambda_HT=0 solution tangent leaves an uncontrolled null flux history not generated by the small reducible gauge tower."),
        ("OBSTRUCTED", "Raw D has Hamiltonian V_S3 lambda_HT and is not a presymplectic null direction without a new fixed-lambda superselection condition."),
        ("OBSTRUCTED", "The zero-frequency kernel is the nonexact H3(S3) flux generator; compactly supported top forms retain Hc4=R."),
        _second(("NOT_APPLICABLE", "Candidate B terminates at the unary/background and global-topology gates."), ("NOT_APPLICABLE", "Candidate B terminates at the unary/background and global-topology gates."), ("OBSTRUCTED", "No complete retarded/advanced parent exists on the off-shell fixture or across the polynomial HT kernel.")),
        _evidence("complex_compensator_action_preflight", "vacuum_WZ_causal_trace_obstruction", "complex_compensator_candidate_b_obstruction"),
        "The action-derived three-form tower is locally consistent, but Candidate B does not contract the dressed trace: H_B(D) has kernel (D/2,1,0), so u is re-encoded as arbitrary harmonic-flux history. The multiplier cannot repair the nonzero trace-free Ricci Euler row of the frozen unit cylinder. Globally H3(S3)=R and Hc4(R x S3)=R survive, and the frozen Berger constraint requires A3=t vol_Berger with a nonexact raw-D shift. Candidate B is therefore OBSTRUCTED unless the background/action, global gauge group or flux/lambda superselection data are changed. No Hadamard, anomaly/QME, particle, scattering or unitarity conclusion follows.",
    ))
    values.append(_entry(
        "classical.complex_compensator.vacuum_cylinder.candidate_ab_neither_selection",
        _scope(
            VACUUM,
            theory="comparison of the declared Candidate-A R(g_hat)^2 auxiliary-scalar action and Candidate-B Henneaux-Teitelboim three-form action; no hybrid theory",
            charge_sector="common unreduced raw-D comparison; Candidate B retains all H3 flux and constant lambda_HT sectors; no new superselection quotient",
            carrier="two separately action-derived classical BV carriers compared by one exact seven-gate rule; no selected carrier and not a particle carrier",
            degree="all local BV degrees required by each candidate; terminal comparison at background, causal, pairing, sign, charge and Berger gates",
            parity="real even scalar and three-form comparison sectors",
            ell="all declared scalar harmonics; harmonic H3 is retained for Candidate B",
            m="all",
            k="all local covectors and declared compact/one-sided support domains",
            omega="raw D=partial_t; no selected positive-frequency carrier",
        ),
        {"causal": "OBSTRUCTED", "symplectic": "OBSTRUCTED", "nonlinear": "NOT_APPLICABLE", "observational": "NO_CERTIFIED_MAP", "quantum": "OPEN"},
        ("OBSTRUCTED", "Candidate A has no promoted complete mixed-metric parent after its physical-sign failure; Candidate B is off shell and has a polynomial HT kernel."),
        ("OBSTRUCTED", "Candidate A has split Lee-Wald inertia; Candidate B retains an uncontrolled global flux/multiplier direction on the declared sector."),
        ("OBSTRUCTED", "Neither candidate supplies the required complete zero-charge raw-D receiver, so no selected-action nonlinear consumer is activated."),
        ("NO_CERTIFIED_MAP", "The exact comparison exports no selected carrier, complex structure, positive-frequency splitting or observational mode."),
        _second(("NOT_APPLICABLE", "No selected action exists for a bounded second-order cone."), ("NOT_APPLICABLE", "No selected action exists for a smooth-secular second-order cone."), ("OBSTRUCTED", "The two declared minimal actions fail the common causal/physical seven-gate receiver rule.")),
        _evidence("complex_compensator_candidate_a_obstruction", "complex_compensator_candidate_b_obstruction", "complex_compensator_candidate_ab_neither"),
        "The exact comparison pins both terminal obstruction artifacts, their scientific and lifecycle commits, action hashes and the common unit-cylinder, coupling, raw-D, frozen-Berger-clock and small-gauge conventions. Candidate A fails gates 3, 5, 6 and 7; Candidate B fails gates 2, 3, 5, 6 and 7. The terminal selection is NEITHER. No score averaging or hybrid is permitted, and no selected action hash or carrier is exported. This is not a universal compensator no-go: differently tuned/backgrounded R(g_hat)^2, active-clock fixed-flux/lambda, enlarged-gauge and bounded minimal-action classes remain open. No Hadamard, anomaly/QME, particle, scattering, positivity or unitarity conclusion follows.",
    ))
    values.append(_entry(
        "classical.complex_compensator.vacuum_cylinder.minimal_action_good_locus",
        _scope(
            VACUUM,
            theory="complete declared minimal formal-polar action family with four metric and at most two compensator derivatives, one R^2 auxiliary presentation and optional minimal HT sector",
            charge_sector="unreduced raw-D sector; optional HT branch retains all H3 flux and constant multiplier sectors under the small reducible gauge group",
            carrier="coefficient-locus comparison of bulk scalar/metric and optional topological carriers; good locus empty, no Candidate C carrier and not a particle carrier",
            degree="all BV degrees inherited from the action preflight and optional reducible A3/C2/C1/C0 cotangent tower",
            parity="parity-even bulk action; Euler is topological and Pontryagin excluded",
            ell="all cylinder scalar harmonics; frozen Berger clock at q=9/40",
            m="all",
            k="all local covectors plus compact/global H3 and Hc4 classes",
            omega="raw D=partial_t; scalar auxiliary roots +/-sqrt(2); HT harmonic D=0 mode retained",
        ),
        {"causal": "OBSTRUCTED", "symplectic": "OBSTRUCTED", "nonlinear": "NOT_APPLICABLE", "observational": "NO_CERTIFIED_MAP", "quantum": "OPEN"},
        ("OBSTRUCTED", "Without HT the exact cylinder-plus-Berger stationary matrix is invertible and leaves only a dynamically empty coefficient vector; with HT a global D=0 kernel survives."),
        ("OBSTRUCTED", "The nonzero-R^2 cylinder branch has split Lee-Wald inertia, while the HT branch retains the flux/multiplier pair and uncontrolled global direction."),
        ("OBSTRUCTED", "No coefficient point passes all seven gates, so no action-specific nonlinear receiver is active."),
        ("NO_CERTIFIED_MAP", "No Candidate C, selected action hash, carrier, complex structure, two-point function or observational mode is exported."),
        _second(("NOT_APPLICABLE", "No selected action exists for a bounded second-order tangent cone."), ("NOT_APPLICABLE", "No selected action exists for a smooth-secular tangent cone."), ("OBSTRUCTED", "The declared minimal action family has empty causal/physical seven-gate locus.")),
        _evidence("complex_compensator_candidate_ab_neither", "complex_compensator_minimal_action_no_go"),
        "The no-HT stationary equations have exact determinant -91791/81920 on the common unit-cylinder and frozen-Berger fixtures, so only the zero bulk vector remains; it has no phase pairing or causal trace parent. Independently, every nonzero-R^2 cylinder repair has velocity inertia (1,1), real roots +/-sqrt(2), size-two Jordan blocks and a both-sign raw-D Hamiltonian. The optional HT branch retains H3/Hc4, a D=0 kernel, nonconstant ambient raw-D Hamiltonian and the nonexact Berger volume shift. The declared minimal good locus is EMPTY and no Candidate C is selected. This is not a universal compensator no-go: higher-derivative phase EFT, multiplier extensions, fixed-flux/global-quotient and independent-conformal-gauge theories remain outside scope. No Hadamard, anomaly/QME, particle, scattering, positivity or unitarity conclusion follows.",
    ))
    values.append(_entry(
        "classical.complex_compensator.cylinder_berger.active_clock_px2_good_locus",
        _scope(
            VACUUM,
            theory="dressed parity-even C^2+R^2+R gravity with the complete quadratic shift-symmetric phase polynomial P(X)=p0+p1 X+p2 X^2; no HT sector or new fields",
            background="joint exact family with inverse squared cylinder radius 15/16<kappa<17/16 and constant phase, plus Berger a=1, 1/5<q<1/4 and stationary clock theta=nu t with 2/3<nu<5/6; includes the frozen point (1,9/40,3/4)",
            charge_sector="unreduced unit-cylinder raw-D sector and frozen-Berger K_Berger=D-(3/4)R stabilizer; no fixed-charge quotient",
            carrier="parameter-dependent one-dimensional exact stationary coefficient locus with coupled homogeneous dressed-trace, R^2 auxiliary-scalar and phase fluctuation; couplings vary with the background and this is not a particle carrier",
            degree="classical action/Euler, homogeneous quadratic and Lee-Wald levels; no all-row selected-action q2 export",
            parity="real parity-even scalar sector",
            ell="homogeneous cylinder scalar sector; frozen Berger clock background",
            m="0 in the decisive homogeneous sector",
            k="homogeneous D-polynomial operator; Berger sound covectors evaluated as exact rational functions of kappa,q,nu",
            omega="clock gradient nu in (2/3,5/6); scalar roots +/-sqrt(2kappa), clock root 0",
        ),
        {"causal": "OBSTRUCTED", "symplectic": "OBSTRUCTED", "nonlinear": "NOT_APPLICABLE", "observational": "NO_CERTIFIED_MAP", "quantum": "OPEN"},
        ("OBSTRUCTED", "The common stationary locus is one-dimensional, but every nonzero point has a split (+3,-3) gravity-auxiliary principal pair; no complete support-local parent is promoted."),
        ("OBSTRUCTED", "The exact reduced Lee-Wald form is nondegenerate for nonzero locus parameter but its velocity inertia is split for both signs."),
        ("OBSTRUCTED", "The unit-cylinder raw-D Hamiltonian takes the exact values +3 and -3; raw D is not null on the declared ambient sector."),
        ("NO_CERTIFIED_MAP", "The coefficient-locus obstruction exports no selected action, compatible complex structure, two-point function or observational/particle mode."),
        _second(("NOT_APPLICABLE", "No selected active-clock action exists for a bounded tangent cone."), ("NOT_APPLICABLE", "No selected active-clock action exists for a smooth-secular tangent cone."), ("OBSTRUCTED", "The quadratic active-clock seven-gate locus is empty before a complete causal parent can be selected.")),
        _evidence("complex_compensator_minimal_action_no_go", "complex_compensator_active_clock_px2_no_go", "complex_compensator_active_clock_px2_freeze_audit", "complex_compensator_active_clock_background_stability"),
        "The theorem-frozen point has exact rank five and kernel t(81/20,27/3290,-324/1645,486/1645,18/25,1), independently reconstructed from integer maximal cofactors, with sound speed squared 9/59. The background-stability theorem promotes inverse squared cylinder radius kappa, Berger squashing q and clock gradient nu to exact parameters. On the rational open box 15/16<kappa<17/16, 1/5<q<1/4, 2/3<nu<5/6, one signed maximal cofactor is everywhere nonzero and the full stationary action-space locus is the parameter-dependent ray lambda K(kappa,q,nu). Couplings vary with the background; this is not a fixed-action stability claim. Every nonzero ray retains the exact split (+3,-3) gravity-auxiliary velocity pair and raw-D witnesses +3,-3. The cylinder and Berger clock-health half-lines are opposite throughout the box, while the Berger sound speed is exactly -q/(32qkappa-3q-8kappa) in (0,1). The common good locus is EMPTY at every box point. Along kappa=1, nu=3/4, lambda=1, q=1/4 is the first clock/principal bifurcation: q=9/40 has incompatible clock signs while q=21/80 makes both clocks standard-sign, but the full verdict remains empty because the split gravity-auxiliary and raw-D defects persist. Stationary rank changes separately, including the q=1/4 intersection kappa=5/16, and no Candidate C_active is selected. This is not a universal k-essence or compensator no-go, nor a fixed-action or generic-background theorem. It constructs no complete causal parent and establishes no Hadamard, anomaly/QME, particle, scattering, positivity or unitarity result.",
    ))
    values.append(_entry(
        "classical.berger.retained_gravity_clock_maxwell",
        _scope(BERGER, carrier="complete 54-row gauge-fixed gravity-clock complex with typed retained 36-row gravity-clock-Maxwell carrier", degree="all BV degrees; physical local fields at degree 0", parity="all local tensor and Maxwell parities", ell="arbitrary four-dimensional jets; no harmonic truncation", m="all", k="all local covectors", omega="K_Berger weight; raw D action is affine"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "CERTIFIED", "quantum": "OPEN"},
        ("OPEN", "No complete Berger harmonic dispersion catalogue is asserted."),
        ("CERTIFIED", "The full and retained odd cyclic pairings and advanced/retarded adjoint reversal are exact."),
        ("CERTIFIED", "The clock momentum is nonzero but its variation vanishes on the declared fixed-coupling tangent; K_Berger, not raw affine D, is the stationary unary generator."),
        ("OPEN", "No complete Berger second-order resonance catalogue exists."),
        _second(("OPEN", "No finite-harmonic bounded Berger tangent cone."), ("OPEN", "No smooth-secular Berger tangent cone."), ("OPEN", "The unary retarded complex is certified, but the nonlinear causal second-order tangent cone is open.")),
        _evidence("Berger_green", "Berger_bikernel_support_gate", "Berger_Cartan", "Berger_charge", "Berger_redshift", "cone"),
        "Causality is unary and the cyclic Cartan theorem stops at arity three. The retained-26 homotopy extends to one-sided past/future/time-compact smooth bikernel LF classes with cyclic adjoint control, but the certified factorization has a cutoff-escape continuity obstruction on the full smooth Frechet class. The imported smooth Ward kernel has no one-sided support profile, so no Ward or Hadamard promotion follows. Raw affine D, arity four, Hadamard/QME, and a branch-resolved physical projector remain false.",
    ))
    values.append(_entry(
        "classical.berger.apparatus.z2_integrability_receiver",
        _scope(
            BERGER,
            theory="same-background Berger gravity-clock-Maxwell system plus the action-derived material apparatus",
            carrier="requested combined q1/q2 apparatus carrier for the two detector-selected preparations u0,u1; first combined unary operator missing and not a particle carrier",
            degree="all BV degrees required by the 108-row base and 56-row apparatus parent",
            parity="all declared BV parities with an odd pairing required before reduction",
            ell="all output blocks generated by finite sums of u0,u1; no compact-product import",
            m="all generated same-background Berger labels",
            k="all generated same-background Berger shells",
            omega="K_Berger weights only after a background-preserving combined action is certified",
        ),
        {
            "causal": "NO_CERTIFIED_MAP",
            "symplectic": "NO_CERTIFIED_MAP",
            "nonlinear": "NO_CERTIFIED_MAP",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        ("NO_CERTIFIED_MAP", "The preparations are not rows of one certified combined unary carrier."),
        ("NO_CERTIFIED_MAP", "A pairing exists on the 108-row base, but no descended pairing exists on the requested combined apparatus complex."),
        ("NO_CERTIFIED_MAP", "No complete stabilizer moment-map/Taub receiver exists for D2E[a0*u0+a1*u1,a0*u0+a1*u1]."),
        ("NO_CERTIFIED_MAP", "No complete same-background nonzero-shell adjoint cokernel or resonant pairing is available."),
        _second(
            ("NO_CERTIFIED_MAP", "No bounded/quasiperiodic receiver has been formed."),
            ("NO_CERTIFIED_MAP", "No smooth-secular receiver has been formed."),
            ("NO_CERTIFIED_MAP", "No causal/retarded receiver has been formed."),
        ),
        _evidence("Berger_apparatus_Z2_receiver_disposition"),
        "The two detector-selected preparations and leading rank-two response remain certified only in their original linear scope. The first blocked object is the combined background-preserving K_Berger-equivariant q1, pairing, real structure and row-level chain crosswalk: the declared constant typed-identification class has global-rod closure rank 8 from a six-dimensional span and zero material-row mixing nullity. The scoped minimal repair adds two global rods and two cotangents before recomputing a 112-row base and retrying the 160-row union. The available 108-row q2 tensor also has a certified arity-two obstruction and cannot be relabelled as the quadratic Euler source. Consequently the three symmetric source pairs, stabilizer and resonance projections, Z2_Berger ideal, nonlinear response rank and memory transport are all NO_CERTIFIED_MAP. This is not a global nonexistence theorem for a repaired or affine combined carrier, imports no compact-product modes and establishes no q3, redshift, particle, stability or quantum claim.",
    ))
    values.append(_entry(
        "classical.berger.crosswalk.retained36_to_einstein_extra",
        _scope(BERGER, carrier="support-local Einstein-like/extra-Weyl dynamical branch projector on the retained 36-row carrier", degree="crosswalk", parity="all", ell="all", m="all", k="all", omega="all"),
        {axis: "NO_CERTIFIED_MAP" for axis in AXES},
        ("NO_CERTIFIED_MAP", "No support-local branch-resolved dispersion map exists on this carrier."),
        ("NO_CERTIFIED_MAP", "No branch-resolved pairing pullback exists."),
        ("NO_CERTIFIED_MAP", "No branch-resolved Taub map exists."),
        ("OBSTRUCTED", "The canonical support-local same-bundle projector is obstructed by the certified subprincipal witness."),
        _second(("NO_CERTIFIED_MAP", "No branch projector."), ("NO_CERTIFIED_MAP", "No branch projector."), ("NO_CERTIFIED_MAP", "No branch projector.")),
        _evidence("Berger_projector", "Berger_bridge1_disposition"),
        "Bridge 1 is not activated on Berger. The certified disposition selects the unsplit retained cyclic causal carrier as authoritative: the rank-36 projector and contractible rank-46 graph anchor are obstructed, while a relative cofiber, noncontractible mixed-bundle construction, and any all-mode REDUCED-MODE map remain open.",
    ))
    values.append(_entry(
        "classical.berger.crosswalk.retained26_to_frozen104_cauchy_bv",
        _scope(
            BERGER,
            carrier="normalized retained-26 companion solution graph -> frozen 104-row stationary formal Cauchy carrier",
            degree="104 rows with degree profile (12,40,40,12) in degrees -1,0,1,2",
            parity="BV grading; real/Krein structure not supplied",
            ell="not harmonic-reduced",
            m="not harmonic-reduced",
            k="finite-order support-local PBW derivatives",
            omega="stationary A104 formal evolution; no spectral split",
        ),
        {"causal": "OBSTRUCTED", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "NOT_APPLICABLE", "observational": "NOT_APPLICABLE", "quantum": "NO_CERTIFIED_MAP"},
        ("OBSTRUCTED", "The unique frozen-graph compatible q_C has 157 nonzero square entries and 207 nonzero A104-commutator entries."),
        ("NO_CERTIFIED_MAP", "No Cauchy/Krein form, real involution or graded-adjoint carrier survives an absent compatible differential."),
        ("NOT_APPLICABLE", "This is a unary formal Cauchy-carrier obstruction, not a Taub or tangent-cone map."),
        ("NOT_APPLICABLE", "No mode or resonance identification is made on the rejected carrier."),
        _second(("NOT_APPLICABLE", "This is a unary carrier crosswalk."), ("NOT_APPLICABLE", "This is a unary carrier crosswalk."), ("NOT_APPLICABLE", "This is a unary carrier crosswalk.")),
        _evidence(
            "Berger_q26_Cauchy_obstruction",
            "Berger_q26_six_row_cyclic_obstruction",
            "Berger_q26_module_closure_bound",
            "Berger_q26_canonical_104_cone_obstruction",
            "Berger_q26_canonical_cone_next_defect",
            "Berger_q26_fully_mixed_cone_SDR_obstruction",
            "Berger_q26_noncone_rational_nilpotence_feasibility",
            "Berger_q26_noncone_evolution_extension_obstruction",
        ),
        "The no-lift theorem is complete only for the frozen 104-row formal Cauchy graph with the normalized q52 solution-map identity. It holds at every finite PBW differential order because that identity fixes q_C uniquely. Factorization first requires five new degree-zero rows and one new degree-one row; cyclic rank completion raises this to ten. The exact defect/free-dual module closure then fills all 936 dimensions of the nine-dimensional rational spin-four representation, with two independent nonzero finite-field determinants. Therefore every free support-local carrier for that closure requires at least 104 added rows with degree profile (12,40,40,12). The first rank-saturating doubled-cone strictification is nilpotent, but exact rational cokernel witnesses obstruct its upper-triangular evolution lift Dq=qA and its free-adjoint orientation. A fully mixed evolution lift does exist identically, but its rational-specialized cone cohomology (13,57,57,13) differs from retained q26 cohomology (1,1,1,1), so it cannot admit the required SDR. Closing the upper-cone right/adjoint defect regenerates all 936 represented dimensions, so that repair tower needs at least another 104 rows (208 added, 312 total). In contrast, an exact rational non-cone specialization with frozen old-old q blocks has ranks (23,56,23), squares to zero and reproduces retained cohomology (1,1,1,1); therefore nilpotency and cohomology rank alone do not obstruct every non-cone 104-row factorization. That particular feasibility differential nevertheless has an exact left-endpoint evolution obstruction: d_-1 e16=(e5,0), the old covector e25* kills the projected boundary space, and e25* A104 e5=-51/2. Hence it admits no A104 chain extension even with unrestricted new-row evolution blocks. This candidate remains not a PBW operator extension and its obstruction is candidate-specific, not a global non-cone no-go. Evolution equivariance for a simultaneous differential solve, cyclic pairing, reality and retained SDR remain open. Changed companions, changed A104 data, non-free/projective presentations and larger carriers also remain open. No Cauchy/Krein pairing, Hadamard, positivity, QME, particle or quantum claim follows.",
    ))
    values.append(_entry(
        "classical.nariai.conformal_orbit.rank310_metric",
        _scope(NARIAI, background="bounded smooth global conformal orbit g_phi=exp(2phi)g_N with sup|exp(phi)-1|<1/9", carrier="metric four-row Bach complex and repaired rank-310 parent-detour graph", degree="all BV degrees", parity="all", ell="all smooth modes", m="all", k="all", omega="all"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "The exact metric biwave endpoint and rank-310 graph carry advanced/retarded propagation on the declared class."),
        ("CERTIFIED", "The support-local SDR is cyclic and the causal homotopies satisfy adjoint reversal."),
        ("OPEN", "No nonlinear Taub/tangent-cone classification on the conformal orbit."),
        ("OPEN", "No nonlinear resonance classification."),
        _second(("OPEN", "No bounded nonlinear cone."), ("OPEN", "No smooth-secular nonlinear cone."), ("OPEN", "Unary causal homotopy is certified; nonlinear causal correction is open.")),
        _evidence("Nariai_conformal", "Nariai_single", "green_transfer_theorem", "cone"),
        "This is the metric theorem on the conformal Nariai orbit only. The abstract transfer theorem consumes the unit-Nariai carrier independently and does not identify it with the conformal-cylinder modes. Transverse Bach-flat directions and Hadamard/nonlinear/quantum claims remain open.",
    ))
    values.append(_entry(
        "classical.nariai.crosswalk.normal_tractor_cylinder_to_metric",
        _scope(NARIAI, background="unit Nariai dS2 x S2", carrier="eight-block normal-tractor curvature-incidence cylinder -> four-row metric Bach complex", degree="crosswalk", parity="all", ell="all smooth modes", m="all", k="all", omega="all"),
        {axis: "NO_CERTIFIED_MAP" for axis in AXES},
        ("NO_CERTIFIED_MAP", "The normal-tractor cylinder and metric carriers have incompatible reducibility cohomology."),
        ("NO_CERTIFIED_MAP", "No pairing pullback is inferred across an obstructed quasi-isomorphism."),
        ("NOT_APPLICABLE", "No nonlinear Taub map is part of this unary carrier disposition."),
        ("OBSTRUCTED", "The H^-1 mismatch is at least 6-1=5 noncontractible reducibility directions."),
        _second(("NOT_APPLICABLE", "This is a unary crosswalk disposition."), ("NOT_APPLICABLE", "This is a unary crosswalk disposition."), ("NO_CERTIFIED_MAP", "The rejected cylinder does not transfer the metric Green homotopy.")),
        _evidence("Nariai_bridge_disposition"),
        "The direct normal-tractor cylinder-to-metric bridge is obstructed, but unit-Nariai causality is certified on the separate rank-310 curvature-corrected automorphism/parent-detour replacement. This row does not demote that replacement or promote a metric/parent bridge on every Bach-flat background.",
    ))
    values.append(_entry(
        "classical.bach_flat.open_parent_detour",
        _scope(NARIAI, background="every globally hyperbolic Bach-flat four-manifold; explicit relative ADM radius-1/4 ball around Nariai", carrier="normal-adjoint-tractor Yang-Mills detour parent, plus the natural rank-310 mapping cone and its four-row metric retract", degree="parent, rank-310 and metric complex degrees", parity="all", ell="NOT_APPLICABLE without additional symmetry", m="NOT_APPLICABLE", k="all local covectors", omega="all"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "The parent detour, four-row metric Bach complex and all-row rank-310 mapping cone have advanced/retarded causal contractions on every background in the declared Bach-flat ADM class."),
        ("CERTIFIED", "The parent is cyclic under its tractor fibre pairing; the metric Volterra homotopy and cyclic rank-310 SDR give complementary-degree adjoint reversal and exact metric descent."),
        ("OPEN", "No class-wide nonlinear tangent cone."),
        ("NOT_APPLICABLE", "No finite harmonic resonance decomposition is assumed on the open parent class."),
        _second(("OPEN", "No bounded harmonic class is declared."), ("OPEN", "No smooth-secular class-wide theorem."), ("OPEN", "Unary parent Green homotopy does not by itself solve nonlinear sourced second order.")),
        _evidence("Bach_parent", "Bach_rank310_SDR", "Bach_metric_biwave", "Bach_rank310_causal", "cone"),
        "The metric endpoint closes without exact same-bundle factorization: the bare covariant companion gives scalar biwave leading symbol, the third-order covariant layer vanishes, and the remaining order-at-most-two operator is covered by the typed Volterra theorem. The natural cyclic SDR then lifts the metric homotopy to all 310 rows. The pure normal-tractor-parent-to-metric crosswalk remains fail-closed; the certified SDR has the curvature-corrected rank-310 cone, not the bare parent, as its source. Hadamard, nonlinear and quantum claims remain open.",
    ))
    values.append(_entry(
        "classical.crosswalk.weak_background_causal_vs_residual_d",
        _scope(
            NARIAI,
            theory="free pure-Weyl classical BV complex; comparison of background-stability domains",
            background="global conformal-cylinder orbit; relative radius-1/4 Bach-flat ADM class around Nariai; exact small Kantowski-Sachs Einstein family on common finite slabs",
            boundaries="closed compact Cauchy surfaces and no timelike boundary; Kantowski-Sachs result only on declared open slabs",
            charge_sector="unquotiented causal complex versus a separately declared fixed residual D target",
            carrier="background-family crosswalk, not a mode or particle carrier",
            degree="all unary BV degrees for causal transfer; residual D complement only when its activation gates hold",
            parity="all",
            ell="NO_CERTIFIED_MAP without a background symmetry decomposition",
            m="NO_CERTIFIED_MAP without a background symmetry decomposition",
            k="all local covectors in the causal theorem",
            omega="D weights only on a declared symmetry- and gap-compatible residual carrier",
        ),
        {"causal": "CERTIFIED", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "NOT_APPLICABLE", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "Advanced/retarded cyclic Green homotopies persist on the declared conformal, relative Bach-flat and finite-slab Einstein domains."),
        ("NO_CERTIFIED_MAP", "A broad-class residual D pairing or weight decomposition is not inferred; it requires a declared conformal-Killing family, D-equivariant contraction and nonzero-weight gap."),
        ("CERTIFIED", "Inside the conformal-cylinder class, the fixed tau-adic target persists when D(phi)=0 and has the exact augmentation defect sigma_D when D(phi) is nonzero."),
        ("OBSTRUCTED", "For Omega=1+1/(10(1+t^2)) and D=partial_t, the fixed augmentation defect is sigma_D(1)=-1/21 although the causal complex remains certified."),
        _second(("NOT_APPLICABLE", "This is a unary background-stability crosswalk."), ("NOT_APPLICABLE", "This is a unary background-stability crosswalk."), ("NOT_APPLICABLE", "No nonlinear sourced equation is solved by this theorem.")),
        _evidence("weak_background_stability"),
        "Causal stability and residual-D stability are separate lifecycle statements. The Bach-flat class is open only relative to the smooth Bach-flat locus. The Kantowski-Sachs family is causal on every certified common finite slab but the declared nonzero branch is not a whole-cylinder neighbourhood. If the conformal-Killing generator is absent, the D row is NO_CERTIFIED_MAP; causal persistence does not remove a mode or establish a D quotient. Hadamard and quantum claims remain open.",
    ))
    values.append(_entry(
        "classical.nariai.transverse_kantowski_sachs_tangent",
        _scope(NARIAI, background="unit Nariai with transverse Kantowski-Sachs linearized Einstein tangent", carrier="complete ten-block rank-310 cyclic parent-detour graph through first variation", degree="all BV degrees along one background tangent", parity="homogeneous scalar anisotropy", ell=0, m=0, k=0, omega="nonstationary sinh(t), sinh(2t) profile"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "The displayed tangent solves the complete linearized fixed-Lambda Einstein equations and is linearized Bach-flat."),
        ("CERTIFIED", "The cyclic HPL variation preserves inclusion/projection adjunction and the opposite-sided Green adjoint identity through formal first order; no standalone physical Lee-Wald norm is assigned to the tangent."),
        ("OPEN", "No second-order Taub classification or exact nonlinear family is certified."),
        ("CERTIFIED", "The global natural full-complex variation and normalized cyclic basic perturbation lemma give support-local rank-310 inclusion, projection and homotopy variations. For every finite differential retaining the certified four-block incidence, both HPL resolvents terminate after one correction and the full cyclic SDR identities hold coefficientwise in Q[epsilon]. The induced formal advanced/retarded chain contraction is exact through first order. No exact nonzero-epsilon geometric family is claimed."),
        _second(("OPEN", "No bounded correction theorem."), ("OPEN", "No smooth-secular correction theorem."), ("OPEN", "No transverse retarded SDR theorem.")),
        _evidence("Nariai_transverse", "Nariai_incidence", "Nariai_PBW_gate", "Nariai_jet_aware_parent", "Nariai_first_order_schur", "Nariai_Phi_only_obstruction", "Nariai_incidence_L1_rigidity", "Nariai_normalized_L0_obstruction", "Nariai_K_admissibility", "Nariai_Phi2_obstruction", "Nariai_PBW_associativity", "Nariai_coefficient_jets", "Nariai_splitting_jets", "Nariai_middle_replay", "Nariai_factorized_schur", "Nariai_upper_chain", "Nariai_endpoint_target", "Nariai_action_variation", "Nariai_rank310_SDR_variation", "Nariai_formal_metric_green_variation", "Nariai_global_HPL_rank310_causal_variation", "Nariai_finite_HPL_incidence", "cone"),
        "The replacement coefficient-jet algebra agrees with direct symbolic composition. Corrected HPL splittings close the first square; the associative replay closes the parent and shifted-chain identities; factorized adjunction before PBW normal ordering gives the exact cyclic Hom adjoint and compressed Schur; the upper relative-saddle chain closes; the endpoint solve has a unique 15-term algebraic cyclic completion; direct action-leading coefficients plus Noether uniqueness identify the full Bach-Hessian variation; and all twenty-one differentiated ten-block SDR identities vanish with no dropped row, including the explicit inclusion/projection adjunction. The global tangent is generated by a slabwise exact Einstein family. The normalized basic perturbation lemma globalizes the full SDR without treating the one-point Taylor table as a coefficient field, and the induced Duhamel formula gives an all-row same-sided formal causal contraction. The finite-incidence theorem removes any HPL convergence or nonlocal-denominator issue. This row remains the tangent theorem at epsilon=0; the separate exact-branch atlas row carries the nonzero-epsilon common-slab geometric and causal promotion, while the whole-cylinder nonzero family remains false.",
    ))
    values.append(_entry(
        "classical.nariai.transverse_kantowski_sachs_exact_branch",
        _scope(NARIAI, background="exact transverse Kantowski-Sachs Einstein branch through unit Nariai", boundaries="for every finite T, a certified small-parameter family on the open globally hyperbolic slab (-T,T) x S1 x S2 with one common wider causal cone; no whole-cylinder nonzero branch", carrier="complete ten-block rank-310 normal-tractor/BGG mapping cone and its four-row trace-free metric Bach retract", degree="all rank-310 and metric BV degrees on the slab; homogeneous background parameter at degree 0", parity="homogeneous scalar anisotropy background; all BV-complex parities", ell="all smooth complex modes; background tangent ell=0", m="all; background tangent m=0", k="all local covectors; background tangent k=0", omega="nonstationary exact Einstein evolution"),
        {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("CERTIFIED", "On every common slab, the natural six-block rank-310 cyclic SDR transports the Einstein/partially-massless metric biwave homotopies to exact all-row advanced and retarded Green homotopies, with metric descent."),
        ("CERTIFIED", "The rank-310 SDR is cyclic and its all-row Green homotopies satisfy complementary-degree adjoint reversal; no global Lee-Wald phase space is assigned across the finite-time singular endpoint."),
        ("OPEN", "No second-order Taub classification beyond the exact homogeneous branch."),
        ("OBSTRUCTED", "The areal radius reaches zero with divergent Weyl curvature at finite proper time in one direction."),
        _second(("OBSTRUCTED", "The nonzero branch is not bounded or globally quasiperiodic on all R."), ("OBSTRUCTED", "The exact branch cannot remain smooth on the whole cylinder."), ("NO_CERTIFIED_MAP", "Slabwise evolution does not supply a whole-cylinder retarded causal bridge.")),
        _evidence("Nariai_transverse_KS_obstruction", "Nariai_KS_four_block_obstruction", "Nariai_six_block_HPL", "Nariai_KS_common_slab", "Einstein_metric_biwave", "Nariai_KS_rank310_transfer"),
        "The branch integrates the certified tangent on every fixed compact time slab but is globally singular for every nonzero 0<|epsilon|<1. In the declared fixed-coordinate tracefree transport, the finite conformal-Killing symbol first changes at order epsilon squared, so the four-block HPL theorem cannot be applied unchanged. The complete six-block operator algebra including k and ksharp has terminating HPL resolvents, an exact cyclic SDR, and two forced quadratic metric cross terms. The natural normal-BGG splittings, Yang--Mills detour middle, action Bach Hessian and their adjoints bind those six blocks on each common slab; the curved triangular graph transform includes the automorphism and first-splitting rows. Combining that support-local cyclic SDR with the complete four-row metric endpoint gives exact rank-310 advanced/retarded homotopies and metric descent. No component-expanded PBW dump is claimed or required. The nonzero family remains singular at finite time, so this is not a whole-cylinder theorem, a non-Einstein Bach-flat metric transfer, or a Hadamard/quantum result. This singularity is not a no-go for other non-Einstein Bach-flat deformations or alternative declared causal subdomains.",
    ))
    values.append(_entry(
        "classical.crosswalk.bach_flat_parent_to_metric",
        _scope(NARIAI, background="open Bach-flat parent class <-> metric Bach complexes away from the certified conformal Nariai orbit", carrier="support-local parent/metric SDR", degree="crosswalk", parity="all", ell="all", m="all", k="all", omega="all"),
        {axis: "NO_CERTIFIED_MAP" for axis in AXES},
        ("NO_CERTIFIED_MAP", "No class-wide metric endpoint crosswalk."),
        ("NO_CERTIFIED_MAP", "No class-wide metric current pullback."),
        ("NO_CERTIFIED_MAP", "No class-wide charge-sector crosswalk."),
        ("NO_CERTIFIED_MAP", "No class-wide mode/resonance crosswalk."),
        _second(("NO_CERTIFIED_MAP", "No metric crosswalk."), ("NO_CERTIFIED_MAP", "No metric crosswalk."), ("NO_CERTIFIED_MAP", "No metric crosswalk.")),
        _evidence("Bach_parent"),
        "The universal parent theorem must not be promoted to a metric theorem outside the certified conformal Nariai orbit.",
    ))
    values.append(_entry(
        "classical.crosswalk.candidate13_reduced_source_to_local_bv",
        _scope(NARIAI, theory="Einstein-Maxwell source relative to Weyl-Maxwell target", background="candidate-13 compact magnetic Plebanski-Hacyan product", boundaries="R_t x closed S1_L x S2 before final residual quotient", charge_sector="fixed magnetic U(1) bundle P_N with N=2", carrier="finite generic candidate-13 bounded/smooth derived-source receiver -> support-local equation-level BV cofiber", degree=2, parity="both axial and polar", ell="input ell=2; outputs L=0,...,4", m="all allowed m,M", k="signed n=1,-2 fibres and conjugates", omega="zero and eighteen selected finite-frequency receiver components"),
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "OBSTRUCTED", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NO_CERTIFIED_MAP", "The declared Fourier/harmonic receiver and modewise inverses are not support-local causal operators."),
        ("NO_CERTIFIED_MAP", "The noncyclic three-form triangle does not supply one transported cyclic pairing on the reduced-source pullback."),
        ("OBSTRUCTED", "Direct promotion of the declared reduced receiver is blocked by an exact support-expansion witness."),
        ("CERTIFIED", "The bounded and smooth coefficientwise receivers remain exact REDUCED-MODE results."),
        _second(("CERTIFIED", "The bounded finite-quasiperiodic zero locus is exact in mode space."), ("CERTIFIED", "The smooth exponential-polynomial zero locus is exact in mode space."), ("NO_CERTIFIED_MAP", "No causal-retarded derived-source crosswalk is supplied.")),
        _evidence("candidate13_local_upgrade_obstruction"),
        "The obstruction applies to direct reuse of the declared global mode projectors and inverses. It does not rule out a new local equation-level cofiber or a larger noncontractible mixed-bundle carrier, and it does not demote the support-local unary relative triangle.",
    ))
    values.append(_entry(
        "classical.crosswalk.compact_product_five_current_de_rham_carrier",
        _scope(NARIAI, theory="Einstein-Maxwell source relative to Weyl-Maxwell target", background="compact magnetic Plebanski-Hacyan product, including candidate-13", boundaries="R_t x closed oriented S1_L x S2 with fixed N=2 magnetic bundle", charge_sector="H,P_x,J_1,J_2,J_3 simultaneous zero-charge derived sector", carrier="160-row shifted de Rham current resolution and cyclic cotangent completion", degree="-2,...,3 with ranks (5,25,50,50,25,5)", parity="odd cotangent pairing; both source parities", ell="not harmonic-reduced", m="not harmonic-reduced", k="not harmonic-reduced", omega="not harmonic-reduced"),
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "CERTIFIED", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NO_CERTIFIED_MAP", "The support-local unary carrier is selected, but no Green homotopy has been constructed."),
        ("CERTIFIED", "The 160-row carrier has an exact odd pairing and Stokes-compatible unary differential."),
        ("CERTIFIED", "The action-derived current q2 and density-dual equation-field operation replay exactly on the 188-row physical-current interface; the full 238-row relative mapping-cofiber morphism remains open."),
        ("NOT_APPLICABLE", "This is an equation-level derived-source carrier, not an observable or particle map."),
        _second(("NOT_APPLICABLE", "No bounded-mode claim is made by the local de Rham carrier."), ("CERTIFIED", "For closed currents, dB=-j presents the five zero-charge conditions without projectors."), ("NO_CERTIFIED_MAP", "Causal Green data remain open.")),
        _evidence("five_current_de_rham_carrier", "five_current_de_rham_q2"),
        "The carrier resolves only the five stabilizer-current classes. Its q2 theorem covers the 14+14 Hessian interface and all 160 current-carrier rows, not every ghost, identity and antifield row of the 78-row relative mapping cofiber. It does not encode candidate-13's eighteen spectral resonance receivers, repair the relative f2, authorize arity three, or supply causal or quantum transport.",
    ))
    values.append(_entry(
        "classical.crosswalk.compact_product_relative_238_cyclic_completion",
        _scope(NARIAI, theory="Einstein-Maxwell source relative to Weyl-Maxwell target", background="compact magnetic Plebanski-Hacyan product", boundaries="support-local off-shell bundle complex before harmonic or causal reduction", charge_sector="H,P_x,J_1,J_2,J_3 simultaneous derived zero-charge sector", carrier="fixed direct sum of the 78-row relative mapping cofiber and 160-row five-current de Rham/cotangent carrier", degree="-2,...,3 with ranks (10,45,78,69,31,5)", parity="candidate nondegenerate BV odd pairing of degree one", ell="not harmonic-reduced", m="not harmonic-reduced", k="not harmonic-reduced", omega="not harmonic-reduced"),
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "OBSTRUCTED", "nonlinear": "OBSTRUCTED", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NO_CERTIFIED_MAP", "The fixed support-local carrier has no causal Green construction."),
        ("OBSTRUCTED", "Degree-one odd nondegeneracy would require equal ranks in degrees d and 1-d; the exact deficits are 5, 14 and 9."),
        ("OBSTRUCTED", "No coefficient or cross-incidence choice can make this fixed 238-row carrier a cyclic BV q1/q2 complex."),
        ("NOT_APPLICABLE", "This is a carrier-rank obstruction, not a harmonic resonance calculation."),
        _second(("NOT_APPLICABLE", "No reduced-mode tangent claim is made."), ("NOT_APPLICABLE", "No smooth-secular tangent claim is made."), ("NO_CERTIFIED_MAP", "No causal-retarded completion is supplied.")),
        _evidence("five_current_de_rham_carrier", "five_current_de_rham_q2", "relative_238_cyclic_rank_obstruction"),
        "The obstruction is only to a nondegenerate degree-one odd pairing on the fixed 238-row direct sum. An add-only repair needs at least 28 rows, with one rank-minimal profile adding 9 rows in degree 1, 14 in degree 2 and 5 in degree 3, but this is necessary rather than sufficient. Noncyclic or presymplectic 238-row complexes, regradings or quotients, and larger mixed-bundle cyclic carriers remain open; no causal or quantum conclusion follows.",
    ))
    values.append(_entry(
        "classical.crosswalk.compact_product_relative_316_cotangent_carrier",
        _scope(NARIAI, theory="Einstein-Maxwell source relative to Weyl-Maxwell target", background="compact magnetic Plebanski-Hacyan product", boundaries="support-local off-shell bundle complex before harmonic or causal reduction", charge_sector="H,P_x,J_1,J_2,J_3 simultaneous derived zero-charge sector", carrier="160-row current resolution direct-summed with T*[1] of the complete 78-row relative mapping cone", degree="-2,...,3 with ranks (10,51,97,97,51,10)", parity="canonical nondegenerate BV odd pairing of degree one", ell="not harmonic-reduced", m="not harmonic-reduced", k="not harmonic-reduced", omega="not harmonic-reduced"),
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "CERTIFIED", "nonlinear": "OBSTRUCTED", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NO_CERTIFIED_MAP", "The unary cotangent carrier has no advanced/retarded Green homotopy."),
        ("CERTIFIED", "The canonical cone/cotangent pairing is nondegenerate and q1-cyclic on all 316 rows."),
        ("OBSTRUCTED", "The block-diagonal full-domain q2 projects to the certified nonzero direct-f2 Taub obstruction."),
        ("NOT_APPLICABLE", "This is an off-shell carrier, not an observable or particle map."),
        _second(("NOT_APPLICABLE", "No reduced-mode tangent claim is made."), ("NOT_APPLICABLE", "No smooth-secular tangent claim is made."), ("NO_CERTIFIED_MAP", "No causal-retarded completion is supplied.")),
        _evidence("relative_238_cyclic_rank_obstruction", "relative_316_cotangent_completion", "relative_316_block_q2_obstruction"),
        "This carrier resolves the 238-row rank obstruction by adjoining the full 78-row odd cotangent of the relative cone, not by identifying unlike bundles at the 28-row rank lower bound. Its pairing is the canonical cone/cotangent pairing, not either standard action-derived form; the generic inertia obstruction is therefore retained rather than refuted. The cotangent adjoint is factorized and not PBW-expanded. Projection proves that a complete full-domain q2 is obstructed while the unary operator remains block diagonal. A genuine derived Taub-zero homotopy pullback, nonzero typed unary cross-incidence, modified endpoint or different background remains open; current comparison, causal and quantum claims are absent.",
    ))
    values.append(_entry(
        "classical.crosswalk.compact_product_derived_taub_zero_pullback",
        _scope(NARIAI, theory="Einstein-Maxwell source relative to Weyl-Maxwell target", background="compact magnetic Plebanski-Hacyan product", boundaries="support-local off-shell derived zero locus before harmonic or causal reduction", charge_sector="quadratic zero locus of the H,P_x,J_1,J_2,J_3 relative moment map", carrier="full unary tangent complex with 160-row local current resolution, 188-row q1/q2 interface and shifted 316-row cyclic candidate T*[1](Cone(iota) direct_sum K_P[1])", degree="unary tangent unchanged; first derived constraint at Taylor arity two; shifted candidate ranks (5,25,56,72,72,56,25,5) in degrees -3,...,4", parity="canonical current/cotangent parity, relative morphism pairing still open", ell="not harmonic-reduced", m="not harmonic-reduced", k="not harmonic-reduced", omega="not harmonic-reduced"),
        {"causal": "NO_CERTIFIED_MAP", "symplectic": "OPEN", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
        ("NO_CERTIFIED_MAP", "No advanced/retarded homotopy has been constructed for the derived relative pullback."),
        ("OPEN", "The local current and unary cotangent pairings are certified separately, but their relative action-pairing comparison is not."),
        ("OBSTRUCTED", "The relative obstruction class factors exactly through the five Taub charges in normalized smooth finite-harmonic quotient coordinates. The endpoint-normalized order-one system has rank 398 and augmented rank 399. Although unrestricted invariant A1 order-two symbols reach that defect, the complete legal top-descent system has shape 1056 by 712, rank 516 and kernel dimension 196; adjoining the sensitivity row leaves rank 516. A four-row exact rowspace identity proves that every legal order-two top symbol has zero sensitivity. At order three, direct cubic sensitivity and the indirect relaxation -y2 D3 both vanish identically, the latter on all 5,600 raw cubic A1 coefficients. The invariant formal-pairing theorem then closes the fixed diffeomorphism-only endpoint at every finite order. The correlated Maxwell-compensator endpoint removes that pairing obstruction, but its exact flat H-current block has rank 3 and augmented rank 4 on the existing symmetric carrier. The remaining normal form is xi modulo (tau,xi^2), so every finite-order product-equivariant support-local unary lift on that carrier is obstructed and f2 remains inactive."),
        ("NOT_APPLICABLE", "This is an equation-level derived source, not an observable or particle identification."),
        _second(("OPEN", "The five-charge factorization does not include the extra polynomial and resonant obstruction functionals of the bounded category."), ("CERTIFIED", "On Sym^2 H0 of every finite real standard-mode set in the smooth-secular category, ker D equals ker M_pol and the normalized quotient-coordinate factor is I5."), ("NO_CERTIFIED_MAP", "No causal-retarded lift of the factorization is available.")),
        _evidence("five_current_de_rham_carrier", "five_current_de_rham_q2", "relative_316_cotangent_completion", "relative_316_block_q2_obstruction", "relative_derived_taub_zero_pullback", "relative_reduced_taub_factorization", "relative_shifted_current_cone_preflight", "relative_full_five_current_pbw", "relative_order_zero_lift_obstruction", "relative_endpoint_normalization", "relative_order_one_invariant_ansatz", "relative_hessian_second_current_input", "relative_full_five_current_second_jet", "relative_order_one_chain_obstruction", "relative_order_two_obstruction_sensitivity", "relative_order_two_top_descent_obstruction", "relative_order_three_descent_obstruction", "relative_all_order_endpoint_pairing_obstruction", "relative_compensated_endpoint_chain_obstruction"),
        "The relative moment map has zero constant and linear terms, so the derived Taub-zero condition does not restrict the unary tangent complex and does not require a nonzero unary cross-incidence. Its first local equation is d_H B_X+j_X(u,u)/2=0 at arity two. In the finite-harmonic smooth-secular target quotient, the complete five-dimensional cokernel theorem makes the normalized evaluation map an isomorphism and gives D=A M_pol with quotient-coordinate matrix I5 on Sym^2 H0, including cross-block pairs. This is not a serialized all-mode PBW matrix or a support-local lift. The current-level lift is typed as a degree-zero chain map A:K_P->C_W. Because K_P[1] belongs inside the derived mapping cone before cotangent completion, its canonical cyclic candidate is a regraded 316-row carrier with degree profile (5,25,56,72,72,56,25,5), not the existing block-diagonal 316 profile. The V1 current table has 30,494 canonical terms and coefficient jets through order one. The action-depth audit then proves that 278 raw target fifth jets and 36 raw source third jets cancel to the required relative parity pattern instead of being silently truncated. The streamed V2 current export contains 36,539 canonical terms and 72,953 ordered terms in twenty independently hashed chunks, complete through coefficient-jet order two. The complete unrestricted order-zero ansatz has 310 coefficients and a 480-equation rational top-descent system of rank 305. Its five-dimensional kernel consists only of Maxwell de Rham tails. Endpoint duality originally fixed A2(P_X^4)=X^mu c_mu_star with positive orientation sign and no U1 or Weyl-identity component. The complete endpoint-normalized SO(2)-invariant order-one chain system has 406 unknowns and 822 nonzero coefficient rows, with rank 398 and augmented rank 399. Its two-row left-null witness compares c_1_star partial_t and c_0_star partial_x on the same H-current three-form: every order-one ansatz coefficient cancels while the fixed endpoint evaluates to one, so that order-one route is obstructed before f2 can be tested. Before imposing top descent, the complete 626-dimensional invariant A1 order-two symbol space reaches the defect: the induced sensitivity has rank one and is surjective, with two symbols evaluating to -1 and +1. Those directions must also satisfy the top-order chain equation. The complete legal top-symbol system couples 626 A1 and 86 A2 invariants. Its 1056-by-712 matrix has 2,484 nonzero entries, rank 516 and kernel dimension 196. Appending the sensitivity row leaves rank 516, and a four-row exact rowspace witness proves that sensitivity vanishes on the entire legal kernel. Order two is therefore closed negatively: the complete endpoint-normalized chain map is obstructed through order two. At order three, the invariant cubic dimensions are 1,108 for A1 and 144 for A2. All third stabilizer-vector jets and second source-action jets vanish, so direct cubic sensitivity is zero. The indirect relaxation identity L2 x2=-y2 D3 x3 also vanishes coefficientwise on all 5,600 raw cubic A1 coefficients, before isotropy or the cubic top equation. The complete endpoint-normalized chain map is obstructed through order three. The basis-independent pairing theorem now proves more: pairing q_W A1=A2 d_H with a target reducibility forces d g(X,Y)=0, but g(J_1,J_1)=sin(theta)^2, so the fixed diffeomorphism-only endpoint is obstructed at every finite differential order without extrapolating the finite screens. The existing fixed-bundle Maxwell compensators satisfy d lambda_X+i_X F=0, and the corrected endpoint A2_comp(P_X^4)=X^mu c_mu_star+lambda_X lambda_cov_star has constant Gram matrix diag(-1,1,1,1,1), with no new row or independent U1 current. The corrected endpoint still fails the unary chain equation on the translation-invariant flat H-current block: the lowest coefficient matrix has rank 3 and augmented rank 4, equivalently xi has nonzero normal form modulo (tau,xi^2). Higher finite differential order cannot repair that lowest filtration component on the existing carrier. The unique minimal GL(4)-covariant tensor-symbol repair adjoins Lambda^2(T^*M), whose B_01 component supplies u=w=0 and v=b=1/2. This is only a symbol-level carrier repair: its cyclic dual completion and full chain map are absent, f2 remains inactive, and no causal or quantum transfer follows.",
    ))
    return values


def build() -> dict[str, Any]:
    value = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "d_quotient_classical",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha(Path(__file__)),
        "status_vocabulary": STATUSES,
        "description_axes": AXES,
        "entries": entries(),
        "verification_commands": [
            "python3 -m d_quotient_classical.atlas.generate_classical_atlas_fragment --check",
            "python3 residual_atlas/validate_fragment.py d_quotient_classical/atlas/classical-causal-atlas-fragment.json",
            "python3 d_quotient_classical/atlas/verify_classical_atlas_fragment.py",
            "python3 -m unittest d_quotient_classical.atlas.tests.test_classical_atlas_fragment",
        ],
    }
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    wrapper = vacuum_evidence()
    if args.write:
        VACUUM_EVIDENCE.write_text(json.dumps(wrapper, indent=2, sort_keys=True) + "\n")
        OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    else:
        if json.loads(VACUUM_EVIDENCE.read_text()) != wrapper:
            raise AssertionError("vacuum evidence wrapper is stale")
        if json.loads(OUTPUT.read_text()) != build():
            raise AssertionError("classical atlas fragment is stale")
    print("CLASSICAL_CAUSAL_RESIDUAL_ATLAS_FRAGMENT_V1: PASS")


if __name__ == "__main__":
    main()
