#!/usr/bin/env python3
"""Generate the Phase 1 relational-observable disposition crosswalk."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
PAYLOAD = P / "certificates/PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1_PAYLOAD.json"
CERT = P / "certificates/PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1.json"
REPORT = P / "reports/phase1-relational-observable-disposition-synthesis-v1.md"
PAPER_DISPOSITION = ROOT / "planning/paper-coverage/observer-phase1-relational-observable-dispositions-2026-07-21.json"
DEPS = {
    "charged_time_admissibility": P / "certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json",
    "legacy_receiver_replay": P / "certificates/BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1.json",
    "legacy_ratio_nonactivation": P / "certificates/BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json",
    "legacy_g0_probe_observable": ROOT / "d_quotient_classical/certificates/BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE.json",
    "standalone_receiver_preflight": P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1.json",
    "original_grading_obstruction": P / "certificates/POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1.json",
    "regraded_integration_obstruction": P / "certificates/POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1.json",
    "terminal_physical_nonactivation": P / "certificates/POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scope(carrier: str, charge_sector: str, degree: Any, omega: str) -> dict[str, Any]:
    return {
        "theory": "pure_Weyl_plus_two_conformal_scalars_plus_Maxwell_and_declared_receiver_sector",
        "background": "positive_Berger_a=1_c_squared=9/40_Omega=3/4",
        "boundaries": "R_times_compact_S3_with_compact_receiver_worldtube_support",
        "charge_sector": charge_sector,
        "carrier": carrier,
        "degree": degree,
        "parity": ["even", "odd"],
        "ell": "NOT_APPLICABLE_OR_NOT_EXPORTED_ON_RECEIVER_CARRIER",
        "m": "NOT_APPLICABLE_OR_NOT_EXPORTED_ON_RECEIVER_CARRIER",
        "k": "NOT_APPLICABLE_OR_NOT_EXPORTED_ON_RECEIVER_CARRIER",
        "omega": omega,
    }


def build_payload() -> dict[str, Any]:
    deps = {name: json.loads(path.read_text()) for name, path in DEPS.items()}
    terminal = deps["terminal_physical_nonactivation"]
    regraded = deps["regraded_integration_obstruction"]
    standalone = deps["standalone_receiver_preflight"]
    legacy = deps["legacy_receiver_replay"]
    legacy_by_key = {row["legacy_key"]: row for row in legacy["legacy_receiver_census"]}
    legacy_scope = lambda key, carrier, omega: scope(  # noqa: E731
        carrier,
        legacy_by_key[key]["carrier_gate"]["declared_setting_id"] + "; no cross_carrier name matching",
        "pre_quotient_probe_degree_zero",
        omega,
    )
    return {
        "schema": "phase1-relational-observable-disposition-synthesis-payload-v1",
        "result_id": "PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1_PAYLOAD",
        "phase": "PHASE_1",
        "claim_crosswalk": [
            {
                "layer": "conditional_or_kinematic_frequency_ratio_fixtures",
                "status": "CERTIFIED",
                "scope": scope(
                    "declared_pre_quotient_source_to_probe_carriers_and_conditional_charged_time_interface",
                    "fixed_coupling_legacy_Berger_and_explicit_charged_time_fibres_kept_distinct",
                    "carrier_specific",
                    "legacy homogeneous control frequency 2*sqrt(10)/3 at each endpoint; ratio 1",
                ),
                "establishes": [
                    "three legacy rank_two retarded source_to_probe matrices on their original pre_quotient carriers",
                    "the conditional charged_time receiver and charge_fibre admissibility contract",
                    "the G0 spatially_global retarded probe_mode observable with one_plus_z=2 on its declared fixed_coupling carrier",
                    "the homogeneous coordinate_frequency ratio one as a kinematic control",
                ],
                "does_not_establish": ["localized action_derived physical receiver", "operational apparatus frequency ratio", "promotion beyond the G0 probe_mode carrier"],
                "carrier_instances": [
                    {
                        "id": "legacy_G0_one_plus_z_two_probe",
                        "status": "CERTIFIED",
                        "scope": scope(
                            "spatially_global_G0_reduced_probe_mode",
                            "compact_positive_berger_clock_fixed_coupling",
                            0,
                            "emit=2*sqrt(10)/3; receive=sqrt(10)/3; one_plus_z=2",
                        ),
                    },
                    {
                        "id": "legacy_dynamical_emitter_rank_two",
                        "status": "CERTIFIED",
                        "scope": legacy_scope("dynamical_emitter", "massive_two_form_source_to_probe_pre_quotient_carrier", "carrier_specific"),
                    },
                    {
                        "id": "legacy_localized_current_rank_two",
                        "status": "CERTIFIED",
                        "scope": legacy_scope("localized_transfer", "localized_external_Maxwell_current_to_probe_pre_quotient_carrier", "carrier_specific"),
                    },
                    {
                        "id": "legacy_homogeneous_Maxwell_rank_two",
                        "status": "CERTIFIED",
                        "scope": legacy_scope("smeared_transfer", "homogeneous_Maxwell_source_to_probe_pre_quotient_carrier", "2*sqrt(10)/3"),
                    },
                    {
                        "id": "legacy_homogeneous_coordinate_ratio_one_control",
                        "status": "CERTIFIED",
                        "scope": legacy_scope("smeared_transfer", "homogeneous_Maxwell_coordinate_frequency_control", "both endpoints 2*sqrt(10)/3; ratio 1"),
                    },
                    {
                        "id": "conditional_charged_time_admissibility_interface",
                        "status": "CERTIFIED",
                        "scope": scope(
                            "typed_receiver_and_charge_fibre_interface_only",
                            "each source_and_target_charge_fibre_must_be_explicitly_crosswalked",
                            "NOT_APPLICABLE_INTERFACE",
                            "NOT_APPLICABLE_NO_INSTANTIATED_RATIO",
                        ),
                    },
                ],
            },
            {
                "layer": "local_BV_receiver_cocycle",
                "status": "CERTIFIED",
                "scope": scope(
                    "standalone_action_derived_D0_receiver_local_polynomial_cochain",
                    "positive_Berger_fixed_coupling_local_receiver; no residual charge fibre exported",
                    [-1, 0],
                    "NOT_APPLICABLE_LOCAL_DESCENT",
                ),
                "establishes": [standalone["receiver_result"]["identity"]],
                "does_not_establish": ["ambient q70 inclusion", "receiver quotient", "observable"],
            },
            {
                "layer": "ambient_action_integration",
                "status": "OBSTRUCTED",
                "scope": scope(
                    "regraded_receiver_local_cochain_to_repaired_q70_chain_candidate",
                    "fixed_and_unrestricted_Q_rel_branches_not_identified",
                    {"source": -1, "target": 1, "map": 0},
                    "NOT_REACHED",
                ),
                "first_obstruction": regraded["first_obstruction"],
                "phase1_disposition": "EXACT_OBSTRUCTION_ALTERNATIVE_ACCEPTED",
                "does_not_establish": ["nonexistence after a new degree_reversing bridge"],
            },
            {
                "layer": "residual_nonradical_physical_descent",
                "status": "NO_CERTIFIED_MAP",
                "scope": scope(
                    "no_combined_receiver_q70_residual_carrier",
                    "fixed_Q_rel_clock_removed; unrestricted_Q_rel_secular; branches kept distinct",
                    [0, 1],
                    "NOT_APPLICABLE_NO_QUOTIENT_INPUT",
                ),
                "first_failed_map": terminal["first_failed_map"],
                "does_not_establish": ["receiver residual cohomology", "nonradical period", "gauge_reduced record"],
            },
            {
                "layer": "operational_relational_observable",
                "status": "NO_CERTIFIED_MAP",
                "scope": scope(
                    "empty_operational_frequency_ratio_domain",
                    "fixed_and_unrestricted_Q_rel_branches_kept_distinct",
                    "NOT_APPLICABLE_EMPTY_DOMAIN",
                    "UNDEFINED",
                ),
                "domain": [],
                "coordinate_ratio_promoted": False,
                "redshift": "NO_CERTIFIED_MAP",
                "does_not_establish": ["physical frequency ratio", "relational redshift", "backreacted observable"],
            },
        ],
        "carrier_preservation": {
            "legacy_rank_two_response": "CERTIFIED_ONLY_ON_THREE_HASHED_PRE_QUOTIENT_CARRIERS",
            "legacy_G0_one_plus_z_two": "CERTIFIED_ONLY_AS_SPATIALLY_GLOBAL_RETARDED_PROBE_MODE_OBSERVABLE_ON_ITS_HASHED_FIXED_COUPLING_CARRIER",
            "local_receiver_descent": "CERTIFIED_ONLY_ON_STANDALONE_D0_LOCAL_COCHAIN_CARRIER",
            "cross_background_or_name_matching": "FORBIDDEN",
            "physical_promotion": "NOT_ACTIVATED",
        },
        "generator_and_charge_dispositions": {
            "D": "raw time translation; never identified with K",
            "R_rel": "relative phase rotation; retained as a separately typed action",
            "K": "D-H_prime(Q_rel)*R_rel; separately typed helical stabilizer",
            "fixed_Q_rel": terminal["classical_dispositions"]["fixed_Q_rel"],
            "unrestricted_Q_rel": terminal["classical_dispositions"]["unrestricted_Q_rel"],
            "unstable_preparation_boundary": terminal["classical_dispositions"]["first_generic_physical_block"],
        },
        "phase1_freeze": {
            "status": "OBSTRUCTED",
            "first_exact_obstruction": regraded["first_obstruction"]["first_failed_gate"],
            "new_receiver_architecture_opened": False,
            "suspension_bridge_constructed": False,
            "operational_observable_activated": False,
        },
        "mutation_expectations": {
            "stale_redshift_promotion": "REJECT",
            "local_cocycle_equals_observable": "REJECT",
            "fixed_charge_clock_revival": "REJECT",
            "raw_D_equals_K": "REJECT",
            "unstable_counterflow_preparation": "REJECT",
        },
        "result_to_paper_dispositions": {
            "paper_09": "CORRECT_LEGACY_NEXT_GATE_AND_ADD_PHASE1_EXACT_OBSTRUCTION_DISPOSITION; MAIN_THEOREMS_UNCHANGED",
            "paper_00": "QUALIFY_G0_ONE_PLUS_Z_TWO_AS_SPATIALLY_GLOBAL_PROBE_MODE; RECORD_LOCALIZED_RECEIVER_NONACTIVATION",
            "paper_98": "QUALIFY_ORIGINAL_G0_RESULT; RETRACT_OPERATIONAL_APPARATUS_PROMOTION; PRESERVE_CLOCK_AND_PRE_QUOTIENT_RESPONSES",
            "paper_99": "QUALIFY_ONE_PLUS_Z_TWO_AS_G0_PROBE_MODE_WITH_NO_LOCALIZED_ACTION_DERIVED_RECEIVER_PROMOTION",
        },
        "exact_checks": {
            "admissibility_has_no_current_fully_populated_receiver": "No current row supplies a fully admissible action-derived nonzero receiver" in deps["charged_time_admissibility"]["claim_boundary"],
            "legacy_physical_redshift_false": legacy["flags"]["PHYSICAL_REDSHIFT_CERTIFIED"] is False,
            "legacy_G0_probe_ratio_two_exact": deps["legacy_g0_probe_observable"]["relational_redshift"]["one_plus_z"] == "2",
            "standalone_local_cocycle_certified": standalone["atlas_status"] == "CERTIFIED",
            "original_grading_obstructed": deps["original_grading_obstruction"]["atlas_status"] == "OBSTRUCTED",
            "regraded_intertwiner_obstructed": regraded["atlas_status"] == "OBSTRUCTED",
            "terminal_ratio_domain_empty": terminal["frequency_ratio_result"]["domain"] == [],
        },
        "claim_boundary": {
            "establishes": [
                "a Phase 1 exact obstruction disposition",
                "a carrier_explicit separation of kinematic, local, ambient, residual and operational layers",
            ],
            "does_not_establish": [
                "a new receiver architecture or suspension bridge",
                "a physical redshift",
                "nonlinear, particle, phenomenology or quantum promotion",
            ],
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    refs = {}
    for name, path in DEPS.items():
        data = json.loads(path.read_text())
        refs[name] = {"path": str(path.relative_to(ROOT)), "result_id": data["result_id"], "sha256": sha(path)}
    payload_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    return {
        "schema": "phase1-relational-observable-disposition-synthesis-v1",
        "result_id": "PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1",
        "claim_status": "PHASE1_EXACT_OBSTRUCTION_DISPOSITION_CERTIFIED",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(payload_bytes).hexdigest()},
        "claim_crosswalk": [{"layer": row["layer"], "status": row["status"]} for row in payload["claim_crosswalk"]],
        "phase1_freeze": payload["phase1_freeze"],
        "result_to_paper_dispositions": payload["result_to_paper_dispositions"],
        "next_gate": "PHASE_2_MUST_EXPLICITLY_AUTHORIZE_ANY_NEW_CHAIN_COCHAIN_BRIDGE_OR_RECEIVER_ARCHITECTURE",
        "claim_boundary": (
            "Phase 1 ends at the exact degree-zero local-cochain-to-q70-chain intertwiner obstruction. "
            "Legacy rank-two responses and the coordinate-frequency control remain certified only on their declared pre-quotient carriers; the G0 one-plus-z-equals-two result remains certified only as a spatially global retarded probe-mode observable; and the standalone local receiver descent remains certified only as a local BV cochain. "
            "No residual nonradical receiver or operational frequency ratio exists on the certified carrier map; no coordinate ratio is promoted to relational redshift."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_phase1_relational_observable_disposition_synthesis --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_phase1_relational_observable_disposition_synthesis",
            "source_sha256": sha(Path(__file__)),
        },
    }


def paper_disposition(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "observer-result-to-paper-disposition-v1",
        "result_id": "PHASE1_RELATIONAL_OBSERVABLE_RESULT_TO_PAPER_DISPOSITIONS_2026_07_21",
        "source_result_id": "PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1",
        "dispositions": payload["result_to_paper_dispositions"],
        "human_materiality_review": "PENDING",
        "does_not_establish": ["publication release", "materiality approval", "a new scientific claim"],
    }


def report_text() -> str:
    return """# Phase 1 relational-observable disposition synthesis

Phase 1 closes on an exact obstruction, not on an operational observable.
Three legacy rank-two retarded matrices and one coordinate-frequency control
remain certified only on their original pre-quotient carriers.  The exact
G0 one-plus-z-equals-two result remains certified on its spatially global
retarded probe-mode carrier, not as a localized action-derived receiver.  The standalone
receiver action supplies an exact local BV descent, but the regraded audit
proves that no degree-zero map can intertwine that degree-minus-one cochain
with the degree-plus-one repaired q70 chain.  Residual descent, a nonradical
period and the operational frequency-ratio domain therefore remain absent.

The public correction preserves the positive Berger clock, every scoped
pre-quotient response and every conditional charged-time theorem.  It removes
only the unsupported promotion from the G0 probe carrier to a localized
operational apparatus observable.  Fixed and unrestricted charge branches, raw D,
R_rel and K, and the unstable j=1/2 preparation boundary remain separate.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    cert = build_certificate(payload)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERT.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
        PAPER_DISPOSITION.write_text(json.dumps(paper_disposition(payload), indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report_text())
    else:
        print(json.dumps(cert, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
