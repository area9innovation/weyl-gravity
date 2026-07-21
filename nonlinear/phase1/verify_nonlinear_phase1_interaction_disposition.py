#!/usr/bin/env python3
"""Independent hash, lifecycle, scope and mutation verifier."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "nonlinear/phase1/NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1.json"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(document: dict) -> None:
    assert document["schema"] == "pure-weyl-nonlinear-phase1-interaction-disposition-v1"
    assert document["result_id"] == "NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1"
    assert document["lifecycle_state"] == "CLASSIFIED"
    imports = document["imports"]
    for imported in imports.values():
        path = ROOT / imported["path"]
        assert path.is_file()
        assert _digest(path) == imported["sha256"]
        source = json.loads(path.read_text(encoding="utf-8"))
        assert source.get("result_id", source.get("artifact_id")) == imported["result_id"]

    q2 = json.loads((ROOT / imports["coupled_q2"]["path"]).read_text())
    q3 = json.loads((ROOT / imports["coupled_q3"]["path"]).read_text())
    ell3 = json.loads((ROOT / imports["retained_ell3"]["path"]).read_text())
    cyclic = json.loads((ROOT / imports["full_bv_cyclicity"]["path"]).read_text())
    disposition = json.loads((ROOT / imports["bounded_cyclic_disposition"]["path"]).read_text())
    branch = json.loads((ROOT / imports["branch_extension"]["path"]).read_text())
    viability = json.loads((ROOT / imports["counterflow_viability"]["path"]).read_text())
    paper11 = json.loads((ROOT / imports["paper11_current_status"]["path"]).read_text())

    assert q2["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"] is True
    assert q3["flags"]["BERGER_ACTION_DERIVED_MIXED_Q3"] is True
    assert ell3["flags"]["BERGER_RETAINED_MIXED_ELL3_TRANSFER"] is True
    assert cyclic["claim_flags"]["FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED"] is True
    assert disposition["claim_flags"]["ORDER_TWO_FILTERED_REMOVAL_OBSTRUCTED"] is False
    assert disposition["claim_flags"]["COMPLETE_ORDER_TWO_TRIVIALIZATION_EXISTS"] is False
    assert disposition["claim_flags"]["COMPLETE_ORDER_TWO_CLASS_NONZERO"] is False
    assert branch["claim_flags"]["FIRST_EXTENSION_OBSTRUCTION_CLASS_CERTIFIED"] is True
    assert branch["claim_flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"] is False
    assert viability["decision"]["robust_stationary_retuning_exists"] is False
    assert viability["downstream_activation"]["candidate_specific_nonlinear"] is False
    assert "BOUNDED_CYCLIC_CLASS_OPEN" in paper11["result_state"]

    representatives = {row["stage_id"]: row for row in document["representative_ledger"]}
    assert set(representatives) == {
        "action_derived_coupled_q2",
        "action_derived_coupled_q3",
        "retained_mixed_ell3",
        "full_retained_bv_cyclicity",
    }
    assert representatives["retained_mixed_ell3"]["interpretation"] == "EXACT_RETAINED_REPRESENTATIVE_NOT_A_DEFORMATION_CLASS"

    redefinitions = {row["scope_id"]: row for row in document["cyclic_redefinition_ledger"]}
    assert redefinitions["physical_action_second_jet"]["status"] == "TRIVIALIZED"
    assert redefinitions["physical_action_second_jet"]["field_content"] == "PHYSICAL_ACTION"
    assert redefinitions["complete_bounded_cyclic_full_bv_second_jet"]["status"] == "OPEN"
    assert redefinitions["complete_bounded_cyclic_full_bv_second_jet"]["field_content"] == "FULL_BV"

    branch_cohomology = document["branch_and_cohomology"]
    assert branch_cohomology["retained_ell3_operation_on_ell1_cohomology"] == "NO_CERTIFIED_MAP"
    assert branch_cohomology["einstein_extra_weyl_maxwell_branch_mixing"] == "NO_CERTIFIED_MAP"
    assert branch_cohomology["interaction_survives_complete_declared_cyclic_redefinition_complex"] == "OPEN"

    counterflow = document["counterflow_nonactivation"]
    assert counterflow["status"] == "NOT_ACTIVATED"
    assert counterflow["missing_pass"] is False
    summary = document["terminal_summary"]
    assert summary == {
        "branch_resolved_physical_mixing_proved": False,
        "complete_bounded_cyclic_full_bv_class_decided": False,
        "counterflow_action_specific_q2_charge_activated": False,
        "exact_retained_interaction_representative": True,
        "full_retained_bv_cyclicity": True,
        "interaction_survival_on_cohomology_proved": False,
        "physical_action_trivialized_through_input_order_two": True,
        "retained_representative_equals_deformation_class": False,
    }
    assert all(value.startswith("REJECTED_") for value in document["adversarial_mutations"].values())


def verify_mutations(document: dict) -> None:
    mutations = []

    stale_q2 = copy.deepcopy(document)
    stale_q2["imports"]["coupled_q2"]["sha256"] = "0" * 64
    mutations.append(stale_q2)

    representative_equals_class = copy.deepcopy(document)
    representative_equals_class["terminal_summary"]["retained_representative_equals_deformation_class"] = True
    mutations.append(representative_equals_class)

    physical_only_redefinition = copy.deepcopy(document)
    next(row for row in physical_only_redefinition["cyclic_redefinition_ledger"] if row["scope_id"] == "complete_bounded_cyclic_full_bv_second_jet")["status"] = "TRIVIALIZED"
    mutations.append(physical_only_redefinition)

    counterflow_healthy = copy.deepcopy(document)
    counterflow_healthy["counterflow_nonactivation"]["status"] = "ACTIVATED"
    mutations.append(counterflow_healthy)

    undefined_branch = copy.deepcopy(document)
    undefined_branch["branch_and_cohomology"]["einstein_extra_weyl_maxwell_branch_mixing"] = "CERTIFIED"
    mutations.append(undefined_branch)

    for mutant in mutations:
        try:
            audit(mutant)
        except AssertionError:
            continue
        raise AssertionError("an adversarial Phase-1 lifecycle mutation was accepted")


def main() -> int:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit(document)
    verify_mutations(document)
    print("PASS: independent nonlinear Phase-1 hash, lifecycle, scope and mutation audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
