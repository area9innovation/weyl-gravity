#!/usr/bin/env python3
"""Freeze the Phase-1 counterflow viability classification."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json"

IMPORTS = {
    "retuning_locus": "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1.json",
    "retuning_payload": "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1.json",
    "causal_parent": "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json",
    "causal_parent_payload": "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V2.json",
    "q70_health_assembly": "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1.json",
    "q70_health_payload": "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_PAYLOAD_V1.json",
    "low_j_stabilizer": "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1.json",
    "low_j_stabilizer_payload": "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_PAYLOAD_V1.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict:
    imports = {}
    loaded = {}
    for role, rel in IMPORTS.items():
        path = ROOT / rel
        data = json.loads(path.read_text())
        loaded[role] = data
        imports[role] = {
            "path": rel,
            "result_id": data["result_id"],
            "sha256": sha256(path),
            "oracle_fields_consumed": [],
        }

    retuning = loaded["retuning_locus"]
    assembly = loaded["q70_health_assembly"]
    causal = loaded["causal_parent"]
    low_j = loaded["low_j_stabilizer"]
    assert retuning["terminal_verdict"]["entire_component_Hamiltonian_Hopf"] is True
    assert retuning["terminal_verdict"]["retuned_all_isotype_programme_activated"] is False
    assert assembly["terminal_verdict"]["health_obstruction_complete"] is True
    assert assembly["terminal_verdict"]["all_isotype_spectral_census_complete"] is False
    assert causal["result_id"] == "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2"
    assert low_j["result_id"] == "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1"

    decision = {
        "branch": "PHASE1_CLASSIFICATION_ENDING",
        "robust_stationary_retuning_exists": False,
        "first_exact_obstruction": "j=1/2 Hamiltonian-Hopf quartet throughout the connected trace-healthy stationary family",
        "structural_identity": "disc_w(F2)=256*q^5*(9*q-8)<0 for (13-3*sqrt(17))/4<q<1/4",
        "selected_fixture_causal_parent": "CERTIFIED_IMPORTED",
        "familywide_green_homotopy": "NO_CERTIFIED_MAP",
        "selected_fixture_health": assembly["result_state"],
        "all_isotype_retuning_branch": "NOT_ACTIVATED",
        "new_action_architecture_opened": False,
    }
    return {
        "schema": "pure-weyl-two-phase-counterflow-phase1-viability-classification-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "lifecycle_state": "CLASSIFIED",
        "result_state": "OBSTRUCTED_NO_ROBUST_STATIONARY_SAME_FIELD_CLOCK",
        "imports": imports,
        "decision": decision,
        "paper_disposition": {
            "phase1_counterflow_successor": "TERMINAL_NEGATIVE_RESULT",
            "headline": "The repaired counterflow theory has a support-local causal parent but no robust linearly healthy stationary same-field clock on the declared family.",
            "higher_j_census_required_for_decision": False,
            "reason": "The stop condition branches first on the familywide j=1/2 obstruction.",
        },
        "downstream_activation": {
            "phase1_classification_ending": True,
            "candidate_specific_nonlinear": False,
            "candidate_specific_observer": False,
            "candidate_specific_quantum": False,
        },
        "adversarial_mutations": {
            "isolated_cross_factor_collision_called_stable": "REJECTED_F2_DISCRIMINANT_REMAINS_NEGATIVE",
            "finite_harmonic_cutoff_called_uniform_health": "REJECTED_DECISION_IS_FAMILYWIDE_IN_Q_BUT_ONLY_J_HALF",
            "unstable_sector_deleted_as_gauge": "REJECTED_RESIDUE_PAIRING_NONDEGENERATE_AND_INERTIA_4_4_0",
            "fixed_charge_called_clock_cure": "REJECTED_NONZERO_FREQUENCY_INSTABILITY_SURVIVES_FIXED_Q_REL",
        },
        "claim_boundary": {
            "establishes": [
                "terminal Phase-1 viability disposition for the declared two-phase same-field stationary family",
                "absence of an open or structurally protected linearly healthy retuning candidate",
                "nonactivation of candidate-specific nonlinear, observer and quantum success branches",
            ],
            "does_not_establish": [
                "a no-go for changed field content, derivative order or action architecture",
                "a familywide Green homotopy away from the selected causal fixture",
                "a complete higher-isotype spectrum, nonlinear instability or finite-time blow-up",
                "Hadamard, anomaly, QME, particle, positivity, unitarity or observer claims",
            ],
        },
        "decision_sha256": canonical_hash(decision),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--emit", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUT.write_text(rendered)
        return 0
    if not OUT.exists() or OUT.read_text() != rendered:
        raise SystemExit("FAIL: generated Phase-1 classification artifact is stale")
    print("PASS: Phase-1 counterflow viability classification is exact and current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
