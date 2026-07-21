#!/usr/bin/env python3
"""Generate the Classical Phase-1 counterflow claim chain."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "d_quotient_classical/phase1/CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1.json"

SOURCES = {
    "passive_trace_obstruction": (
        "d_quotient_classical/certificates/TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json",
        "OBSTRUCTED",
    ),
    "minimal_repair_ladder": (
        "d_quotient_classical/compensator/COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1.json",
        "SCOPED_MINIMAL_COMPENSATOR_LADDER_EXHAUSTED_WITHOUT_SELECTED_ACTION",
    ),
    "selected_causal_parent": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json",
        "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT",
    ),
    "selected_health_assembly": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1.json",
        "OBSTRUCTED_LINEAR_PHYSICAL_HEALTH_WITH_TYPED_HIGHER_J_CENSUS_SHORTFALL",
    ),
    "retuning_locus": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1.json",
        "OBSTRUCTED_NO_STABLE_JHALF_RETUNING_ON_CONNECTED_TRACE_HEALTHY_FAMILY",
    ),
    "phase1_viability": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json",
        "OBSTRUCTED_NO_ROBUST_STATIONARY_SAME_FIELD_CLOCK",
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(row_id: str, sequence: int, source: str, **fields: object) -> dict:
    return {"row_id": row_id, "sequence": sequence, "source": source, **fields}


def build() -> dict:
    imports = {}
    documents = {}
    for role, (rel, state) in SOURCES.items():
        path = ROOT / rel
        data = json.loads(path.read_text())
        assert data["result_state"] == state
        imports[role] = {
            "path": rel,
            "result_id": data["result_id"],
            "result_state": state,
            "sha256": digest(path),
            "oracle_fields_consumed": [],
        }
        documents[role] = data

    rows = [
        row("passive_tau_trace", 0, "passive_trace_obstruction",
            theory_action="formal tau-adic compensator extension of strict C^2 with no classical dressed-trace kinetic term",
            background="vacuum unit cylinder", charge_fibre="NOT_APPLICABLE",
            causal_scope="OBSTRUCTED_BY_COMPACT_SUPPORT_DRESSED_TRACE_HOMOLOGY",
            dressed_trace="SURVIVES_AS_NONZERO_UNARY_HOMOLOGY",
            physical_quotient="NO_CERTIFIED_MAP", spectral_scope="NO_CERTIFIED_MAP", lifecycle="OBSTRUCTED"),
        row("minimal_repair_ladder", 1, "minimal_repair_ladder",
            theory_action="declared nine-family minimal compensator/active-clock repair union",
            background="row-specific unit-cylinder and Berger fixtures", charge_fibre="ROW_SCOPED",
            causal_scope="NO_SELECTED_COMPLETE_CAUSAL_PARENT",
            dressed_trace="EACH_ROW_FAILS_ITS_PRINTED_TRACE_OR_HEALTH_GATE",
            physical_quotient="NO_SELECTED_ACTION", spectral_scope="NO_UNIONWIDE_SPECTRUM", lifecycle="OBSTRUCTED_SCOPED_UNION"),
        row("two_phase_selected_causal_parent", 2, "selected_causal_parent",
            theory_action="two-phase counterflow action with repaired diagonal-U1 contractible sector",
            background="selected positive biaxial Berger fixture", charge_fibre="fixed-Q_rel leaf for the causal activation",
            causal_scope="CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_PARENT_ON_SELECTED_FIXTURE",
            dressed_trace="CONTRACTED_ON_SELECTED_FIXTURE", physical_quotient="NOT_ESTABLISHED_BY_CAUSAL_CERTIFICATE",
            spectral_scope="NOT_COMPUTED_BY_CAUSAL_CERTIFICATE", lifecycle="CERTIFIED_CAUSAL_ONLY"),
        row("repaired_q70_selected_health", 3, "selected_health_assembly",
            theory_action="repaired q70 two-phase counterflow fixture", background="same selected Berger fixture",
            charge_fibre="unrestricted and derived fixed-Q_rel quotient kept distinct",
            causal_scope="CERTIFIED_IMPORTED_ON_SELECTED_FIXTURE", dressed_trace="REMOVED",
            physical_quotient="CERTIFIED_FOR_J_0_J_HALF_J_1_ALL_M_K; HIGHER_J_NO_CERTIFIED_MAP",
            spectral_scope="NONRADICAL_INSTABILITY_IN_EVERY_CERTIFIED_ISOTYPE; FIXED_Q_REL_REMOVES_GLOBAL_CLOCK_BUT_NOT_INSTABILITY",
            lifecycle="OBSTRUCTED_LINEAR_PHYSICAL_HEALTH"),
        row("same_field_retuning_family", 4, "retuning_locus",
            theory_action="same-field same-derivative-order stationary retuning family",
            background="connected trace-healthy Berger component (13-3*sqrt(17))/4<q<1/4",
            charge_fibre="j=1/2 nonhomogeneous delta-Q_rel=0 sector without charged-orbit deletion",
            causal_scope="SELECTED_FIXTURE_IMPORTED; FAMILYWIDE_GREEN_NO_CERTIFIED_MAP", dressed_trace="TRACE_HEALTHY_COMPONENT",
            physical_quotient="COMPLETE_14_DIMENSIONAL_BOTH_K_J_HALF_QUOTIENT",
            spectral_scope="FAMILYWIDE_HAMILTONIAN_HOPF_FROM_DISC_F2_256_Q5_9Q_MINUS_8_LT_0",
            lifecycle="OBSTRUCTED_SAME_FIELD_FAMILY"),
        row("phase1_terminal_disposition", 5, "phase1_viability",
            theory_action="Classical Phase-1 two-phase counterflow candidate selection",
            background="selected fixture plus declared connected same-field stationary family",
            charge_fibre="unrestricted/fixed-Q_rel distinction preserved",
            causal_scope="SELECTED_FIXTURE_CAUSAL_ONLY; FAMILYWIDE_NO_CERTIFIED_MAP", dressed_trace="REPAIRED_BUT_NOT_SUFFICIENT",
            physical_quotient="NO_ROBUST_LINEARLY_HEALTHY_CANDIDATE",
            spectral_scope="J_HALF_FAMILY_OBSTRUCTION_TERMINATES_BRANCH_WITHOUT_ALL_ISOTYPE_EXTRAPOLATION",
            lifecycle="TERMINAL_OBSTRUCTED_NO_PHASE2_CANDIDATE"),
    ]
    edges = [
        {"from": "passive_tau_trace", "to": "minimal_repair_ladder", "relation": "MOTIVATES_DECLARED_ACTION_REPAIR_LADDER"},
        {"from": "minimal_repair_ladder", "to": "two_phase_selected_causal_parent", "relation": "NEW_TWO_PHASE_ARCHITECTURE_SELECTED_OUTSIDE_TESTED_MINIMAL_UNION"},
        {"from": "two_phase_selected_causal_parent", "to": "repaired_q70_selected_health", "relation": "CAUSAL_PARENT_DOES_NOT_IMPLY_PHYSICAL_HEALTH"},
        {"from": "repaired_q70_selected_health", "to": "same_field_retuning_family", "relation": "SELECTED_FIXTURE_INSTABILITY_MOTIVATES_SAME_FIELD_RETUNING_TEST"},
        {"from": "same_field_retuning_family", "to": "phase1_terminal_disposition", "relation": "FAMILYWIDE_J_HALF_OBSTRUCTION_TERMINATES_CANDIDATE_SELECTION"},
    ]
    mutations = {
        "causal_equals_healthy": "REJECTED_SELECTED_CAUSAL_PARENT_HAS_SEPARATE_NONRADICAL_INSTABILITY",
        "fixed_charge_retains_clock": "REJECTED_FIXED_Q_REL_QUOTIENT_REMOVES_GLOBAL_RELATIVE_CLOCK",
        "selected_point_only": "REJECTED_RETUNING_DISCRIMINANT_IS_NEGATIVE_ON_ENTIRE_CONNECTED_COMPONENT",
        "familywide_green": "REJECTED_ONLY_SELECTED_FIXTURE_HAS_CERTIFIED_CAUSAL_PARENT",
        "universal_all_architecture": "REJECTED_OBSTRUCTION_IS_SAME_FIELD_SAME_DERIVATIVE_ORDER_ONLY",
    }
    return {
        "schema": "pure-weyl-classical-phase1-counterflow-claim-map-v1",
        "result_id": "CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "lifecycle_state": "CLASSIFIED",
        "result_state": "PHASE1_CLASSICAL_COUNTERFLOW_CHAIN_FROZEN_TERMINAL_OBSTRUCTED",
        "imports": imports,
        "rows": rows,
        "edges": edges,
        "adversarial_mutations": mutations,
        "terminal_summary": {
            "selected_fixture_causal_parent": True,
            "selected_fixture_dressed_trace_removed": True,
            "selected_fixture_physically_healthy": False,
            "fixed_Q_rel_retains_physical_clock": False,
            "familywide_same_field_stable_candidate": False,
            "phase2_candidate_selected": False,
        },
        "claim_boundary": {
            "establishes": ["the exact typed Classical Phase-1 counterflow claim progression", "the terminal nonselection of the declared same-field counterflow candidate"],
            "does_not_establish": ["a universal no-go over changed action architectures", "a familywide causal Green homotopy", "an all-isotype spectrum on the retuning family", "nonlinear, observer, quantum, particle, scattering, positivity or unitarity claims"],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit", action="store_true"); g.add_argument("--check", action="store_true"); args = ap.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit: OUT.write_text(rendered); return 0
    if not OUT.exists() or OUT.read_text() != rendered: raise SystemExit("FAIL: stale Classical Phase-1 claim map")
    print("PASS: Classical Phase-1 counterflow claim map is current")
    return 0


if __name__ == "__main__": raise SystemExit(main())
