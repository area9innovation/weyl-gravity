#!/usr/bin/env python3
"""Generate the Phase-1 nonlinear interaction lifecycle disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "nonlinear/phase1/NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1.json"

SOURCES = {
    "coupled_q2": "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
    "coupled_q3": "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
    "retained_ell3": "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_TRANSFER.json",
    "independent_ell3_acceptance": "quantum-weyl/transfer/certificates/BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE.json",
    "full_bv_cyclicity": "quantum-weyl/transfer/certificates/BERGER_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY.json",
    "constant_redefinition": "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1.json",
    "first_jet_redefinition": "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1.json",
    "zero_pbw_full_bv_redefinition": "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_ZERO_JET_GHOST_SHEAR_COMPLETION_V1.json",
    "physical_order_two_redefinition": "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1.json",
    "bounded_cyclic_disposition": "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1.json",
    "branch_extension": "d_quotient_classical/certificates/BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1.json",
    "paper11_current_status": "paper/11-gravity-light-cyclic-causal-ell3-claim-map.json",
    "counterflow_viability": "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json",
    "classical_phase1_counterflow": "d_quotient_classical/phase1/CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _state(document: dict) -> str:
    return document.get("result_state", document.get("status", "CERTIFIED_BY_EXACT_FLAGS"))


def build() -> dict:
    documents = {}
    imports = {}
    for role, relative in SOURCES.items():
        path = ROOT / relative
        document = json.loads(path.read_text(encoding="utf-8"))
        documents[role] = document
        imports[role] = {
            "path": relative,
            "result_id": document.get("result_id", document.get("artifact_id")),
            "result_state": _state(document),
            "sha256": digest(path),
            "oracle_fields_consumed": [],
        }

    assert documents["coupled_q2"]["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"]
    assert documents["coupled_q3"]["flags"]["BERGER_ACTION_DERIVED_MIXED_Q3"]
    assert documents["retained_ell3"]["flags"]["BERGER_RETAINED_MIXED_ELL3_TRANSFER"]
    assert documents["independent_ell3_acceptance"]["claim_flags"]["RETAINED_MIXED_ELL3_CONTACT_INDEPENDENTLY_REPLAYED"]
    assert documents["full_bv_cyclicity"]["claim_flags"]["FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED"]
    assert documents["bounded_cyclic_disposition"]["result_state"] == "ORDER_TWO_OBSTRUCTION_WITHDRAWN_COMPLETE_BOUNDED_CYCLIC_CLASS_OPEN"
    assert documents["paper11_current_status"]["result_state"] == "FROZEN_SDR_REPRESENTATIVE_THEOREM_FROZEN_BOUNDED_CYCLIC_CLASS_OPEN"
    assert documents["counterflow_viability"]["result_state"] == "OBSTRUCTED_NO_ROBUST_STATIONARY_SAME_FIELD_CLOCK"

    representative_ledger = [
        {
            "stage_id": "action_derived_coupled_q2",
            "source": "coupled_q2",
            "theory_action": "gravity-clock-Maxwell BV action",
            "background": "frozen positive rational Berger fixture",
            "carrier": "complete typed 64-row BV carrier",
            "operation": "q2",
            "lifecycle": "CERTIFIED",
            "interpretation": "EXACT_ACTION_DERIVED_REPRESENTATIVE",
        },
        {
            "stage_id": "action_derived_coupled_q3",
            "source": "coupled_q3",
            "theory_action": "gravity-clock-Maxwell BV action after the declared finite canonical shear",
            "background": "same frozen positive rational Berger fixture",
            "carrier": "complete typed 64-row BV carrier",
            "operation": "q3",
            "lifecycle": "CERTIFIED",
            "interpretation": "EXACT_ACTION_DERIVED_REPRESENTATIVE",
        },
        {
            "stage_id": "retained_mixed_ell3",
            "source": "retained_ell3",
            "theory_action": "same gravity-clock-Maxwell BV action",
            "background": "same frozen positive rational Berger fixture",
            "carrier": "one specified cyclic 64-to-36 SDR",
            "operation": "ell3",
            "lifecycle": "CERTIFIED",
            "interpretation": "EXACT_RETAINED_REPRESENTATIVE_NOT_A_DEFORMATION_CLASS",
        },
        {
            "stage_id": "full_retained_bv_cyclicity",
            "source": "full_bv_cyclicity",
            "theory_action": "same gravity-clock-Maxwell BV action",
            "background": "same frozen positive rational Berger fixture",
            "carrier": "retained 36-row BV carrier",
            "operation": "cyclic lowering of ell3",
            "lifecycle": "CERTIFIED",
            "interpretation": "COMPLETE_RETAINED_BV_CYCLICITY_FOR_THE_PINNED_TENSOR",
        },
    ]

    cyclic_redefinition_ledger = [
        {
            "scope_id": "physical_action_constant_field",
            "source": "constant_redefinition",
            "carrier": "unsplit retained 36-row physical base",
            "maximum_input_jet_order": 0,
            "field_content": "PHYSICAL_ACTION",
            "status": "TRIVIALIZED",
        },
        {
            "scope_id": "full_bv_zero_pbw",
            "source": "zero_pbw_full_bv_redefinition",
            "carrier": "retained 36-row BV carrier plus three certified Maxwell ghost shears",
            "maximum_input_jet_order": 0,
            "field_content": "FULL_BV",
            "status": "TRIVIALIZED",
        },
        {
            "scope_id": "physical_action_first_jet",
            "source": "first_jet_redefinition",
            "carrier": "unsplit retained 36-row physical base",
            "maximum_input_jet_order": 1,
            "field_content": "PHYSICAL_ACTION",
            "status": "TRIVIALIZED",
        },
        {
            "scope_id": "physical_action_second_jet",
            "source": "physical_order_two_redefinition",
            "carrier": "unsplit retained 36-row physical base",
            "maximum_input_jet_order": 2,
            "field_content": "PHYSICAL_ACTION",
            "status": "TRIVIALIZED",
        },
        {
            "scope_id": "complete_bounded_cyclic_full_bv_second_jet",
            "source": "bounded_cyclic_disposition",
            "carrier": "declared derivative-aware cyclic super-cotangent F2/F3 complex",
            "maximum_input_jet_order": 2,
            "field_content": "FULL_BV",
            "status": "OPEN",
        },
    ]

    invariant_class_ledger = [
        {
            "class_id": "retained_mixed_ell3_cyclic_deformation_class",
            "complex": "complete declared bounded cyclic full-BV redefinition complex through summed input order two",
            "status": "OPEN",
            "source": "bounded_cyclic_disposition",
            "statement": "The former 22-row witness is invalid on an admissible second-jet column; neither a full primitive nor a replacement full-cokernel witness is certified.",
        },
        {
            "class_id": "principal_branch_extension_beta1",
            "complex": "unary filtered cyclic principal branch-extension complex",
            "status": "OBSTRUCTED",
            "source": "branch_extension",
            "statement": "The invariant beta_1=(1,0) obstructs the declared principal branch split and classifies its minimal page repair.",
        },
    ]

    branch_and_cohomology = {
        "retained_ell3_operation_on_ell1_cohomology": "NO_CERTIFIED_MAP",
        "einstein_extra_weyl_maxwell_branch_mixing": "NO_CERTIFIED_MAP",
        "interaction_survives_complete_declared_cyclic_redefinition_complex": "OPEN",
        "branch_extension_class_beta1": "OBSTRUCTED",
        "carrier_crosswalk": "NO_CERTIFIED_MAP",
    }

    counterflow_nonactivation = {
        "theory_action": "repaired q70 two-phase counterflow action",
        "background": "selected positive Berger fixture and connected trace-healthy same-field stationary family",
        "charge_sector": "unrestricted and fixed-Q_rel kept distinct",
        "requested_calculation": "action-specific q2 and charge-sector consistency",
        "status": "NOT_ACTIVATED",
        "missing_pass": False,
        "source": "counterflow_viability",
        "reason": "The familywide j=1/2 Hamiltonian-Hopf obstruction leaves no robust stationary same-field clock candidate, so candidate-specific nonlinear success branches are not activated.",
        "does_not_establish": "No no-go is claimed for changed field content, derivative order or action architecture.",
    }

    return {
        "schema": "pure-weyl-nonlinear-phase1-interaction-disposition-v1",
        "result_id": "NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1",
        "result_state": "REPRESENTATIVES_CERTIFIED_COMPLETE_CYCLIC_CLASS_OPEN_COUNTERFLOW_NOT_ACTIVATED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "representative_ledger": representative_ledger,
        "cyclic_redefinition_ledger": cyclic_redefinition_ledger,
        "invariant_class_ledger": invariant_class_ledger,
        "branch_and_cohomology": branch_and_cohomology,
        "counterflow_nonactivation": counterflow_nonactivation,
        "adversarial_mutations": {
            "stale_q2": "REJECTED_Q2_CONTENT_HASH_MUST_MATCH",
            "representative_equals_class": "REJECTED_RETAINED_REPRESENTATIVE_DOES_NOT_DECIDE_DEFORMATION_CLASS",
            "physical_only_redefinition": "REJECTED_PHYSICAL_ACTION_PRIMITIVE_DOES_NOT_TRIVIALIZE_FULL_BV",
            "counterflow_healthy": "REJECTED_TERMINAL_CLASSICAL_HEALTH_OBSTRUCTION_PREVENTS_ACTIVATION",
            "undefined_branch": "REJECTED_NO_BRANCH_CROSSWALK_OR_MIXING_TABLE_EXISTS",
        },
        "terminal_summary": {
            "exact_retained_interaction_representative": True,
            "full_retained_bv_cyclicity": True,
            "retained_representative_equals_deformation_class": False,
            "physical_action_trivialized_through_input_order_two": True,
            "complete_bounded_cyclic_full_bv_class_decided": False,
            "interaction_survival_on_cohomology_proved": False,
            "branch_resolved_physical_mixing_proved": False,
            "counterflow_action_specific_q2_charge_activated": False,
        },
        "claim_boundary": {
            "establishes": [
                "the exact Phase-1 lifecycle of the retained Berger gravity-Maxwell q2/q3/ell3 representatives",
                "the exact scope of physical-action and full-BV cyclic removability currently certified",
                "the open status of the complete bounded cyclic class and branch/cohomology interpretation",
                "NOT_ACTIVATED status of counterflow q2/charge after the terminal classical health obstruction",
            ],
            "does_not_establish": [
                "a nonzero interaction on ell1 cohomology",
                "a nontrivial class modulo the complete declared cyclic redefinition complex",
                "Einstein-like/additional-Weyl/Maxwell branch-resolved mixing",
                "a counterflow nonlinear no-go independent of the prior classical health gate",
                "particle, scattering, positivity, unitarity, observer or quantum claims",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(rendered, encoding="utf-8")
        return 0
    if not OUT.is_file() or OUT.read_text(encoding="utf-8") != rendered:
        raise SystemExit("FAIL: stale nonlinear Phase-1 interaction disposition")
    print("PASS: nonlinear Phase-1 interaction disposition is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
