#!/usr/bin/env python3
"""Generate the repaired-q70-health charged-time receiver nonactivation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
PAYLOAD = P / "certificates/COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1_PAYLOAD.json"
CERT = P / "certificates/COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1.json"
REPORT = P / "reports/counterflow-charged-time-physical-instantiation-after-repaired-q70-health-not-activated-v1.md"
HEALTH = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_V1.json"
HEALTH_PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_HEALTH_ASSEMBLY_MAXIMAL_DOMAIN_PAYLOAD_V1.json"
DEPS = {
    "receiver_admissibility": P / "certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json",
    "legacy_receiver_replay": P / "certificates/BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1.json",
    "legacy_ratio_nonactivation": P / "certificates/BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json",
    "phase1_disposition": P / "certificates/PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1.json",
    "standalone_local_receiver": P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1.json",
    "regraded_receiver_integration": P / "certificates/POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1.json",
    "terminal_receiver_nonactivation": P / "certificates/POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1.json",
    "health_assembly": HEALTH,
    "health_assembly_payload": HEALTH_PAYLOAD,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mode_scope(two_j: Any, carrier: str, charge_sector: str, omega: str) -> dict[str, Any]:
    if isinstance(two_j, int):
        j: Any = str(two_j // 2) if two_j % 2 == 0 else f"{two_j}/2"
        ell: Any = j
        m = f"all m=-{j},...,{j}"
        k = f"all k=-{j},...,{j}"
    else:
        ell, m, k = "j>=3/2", "all allowed m", "all allowed k"
    return {
        "theory": "pure_Weyl_two_phase_counterflow_repaired_q70",
        "background": "positive_Berger_a=1_c_squared=9/40_Omega=3/4",
        "boundaries": "R_times_compact_S3_support_local_causal_parent",
        "charge_sector": charge_sector,
        "carrier": carrier,
        "degree": "physical_H0_quotient_or_declared_NO_CERTIFIED_MAP",
        "parity": ["even", "odd"],
        "ell": ell,
        "m": m,
        "k": k,
        "omega": omega,
    }


def build_payload() -> dict[str, Any]:
    health = json.loads(HEALTH.read_text())
    hp = json.loads(HEALTH_PAYLOAD.read_text())
    blocks = hp["certified_block_ledger"]
    block_dispositions = []
    for block in blocks:
        block_dispositions.append({
            "two_j": block["two_j"],
            "j": block["j"],
            "all_m": block["all_m"],
            "all_k": block["all_k"],
            "physical_dimension": block["physical_total_dimension"],
            "pairing_radical_dimension": block["pairing_radical_dimension"],
            "instability_class": block["instability_class"],
            "unrestricted_status": block["unrestricted_status"],
            "fixed_Q_rel_status": block["fixed_Q_rel_status"],
            "receiver_disposition": "OBSTRUCTED_AS_HEALTHY_RECEIVER_PREPARATION",
            "scope": mode_scope(
                block["two_j"],
                f"repaired_q70_physical_quotient_j={block['j']}",
                "unrestricted_and_fixed_Q_rel_kept_distinct",
                "nonzero_frequency_unstable_sector",
            ),
        })
    interface_names = [
        "local_BV_class",
        "physical_receiver_quotient",
        "descended_pairing",
        "nonzero_period",
        "retarded_support_map",
        "monotone_clock_interval",
        "positive_denominator_margin",
        "D_action",
        "R_rel_action",
        "K_action",
        "charge_fibre_crosswalk",
        "emitter_preparation",
        "transported_signal_phase",
    ]
    interface = {
        name: {
            "status": "NO_CERTIFIED_MAP",
            "reason": "no common healthy physical clock-receiver carrier passes the repaired-q70 health gate",
        }
        for name in interface_names
    }
    interface["physical_receiver_quotient"]["reason"] = (
        "certified j=0,1/2,1 quotients are all physically unstable; j>=3/2 quotient is NO_CERTIFIED_MAP"
    )
    interface["R_rel_action"]["reason"] = (
        "fixed charge removes the clock; j=0,1 quotient action matrices are not exported; no eligible common carrier remains"
    )
    interface["K_action"]["reason"] = interface["R_rel_action"]["reason"]
    return {
        "schema": "counterflow-charged-time-physical-instantiation-after-repaired-q70-health-not-activated-payload-v1",
        "result_id": "COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1_PAYLOAD",
        "activation_rule": "instantiate only on one common action-derived, nonradical, linearly healthy physical receiver carrier",
        "ordered_gate": [
            {"gate": "repaired_q70_action_derived_causal_parent", "status": "CERTIFIED"},
            {"gate": "certified_physical_quotients_j_0_half_1", "status": "OBSTRUCTED", "reason": "every certified physical block is unstable"},
            {"gate": "remaining_physical_quotients_j_ge_3_over_2", "status": "NO_CERTIFIED_MAP"},
            {"gate": "common_healthy_clock_receiver_carrier", "status": "NO_CERTIFIED_MAP", "first_failed_receiver_gate": True},
            {"gate": "thirteen_field_receiver_interface", "status": "NOT_ACTIVATED"},
            {"gate": "operational_frequency_ratio", "status": "NOT_ACTIVATED"},
        ],
        "certified_block_dispositions": block_dispositions,
        "remaining_carrier": {
            **health["remaining_carrier"],
            "receiver_disposition": "NO_CERTIFIED_MAP",
            "scope": mode_scope(
                "two_j>=3",
                "repaired_q70_causal_parent_without_physical_quotient",
                "fixed_and_unrestricted_Q_rel_not_instantiated_on_unknown_quotient",
                "NO_CERTIFIED_MAP",
            ),
        },
        "branch_dispositions": {
            "fixed_Q_rel": {
                **health["branch_verdicts"]["fixed_Q_rel"],
                "receiver_effect": "relative clock removed; no charged-time observable",
            },
            "unrestricted": {
                **health["branch_verdicts"]["unrestricted"],
                "receiver_effect": "clock carrier remains charged but every certified receiver block is unstable and the remainder is undefined",
            },
        },
        "thirteen_field_interface": interface,
        "frequency_ratio_partial_function": {
            "domain": [],
            "domain_cardinality": 0,
            "value": "UNDEFINED",
            "redshift": "NO_CERTIFIED_MAP",
            "coordinate_ratio_promoted": False,
            "independent_methods_run": 0,
            "why_methods_not_run": "the common healthy receiver carrier and thirteen-field interface are not activated",
        },
        "health_transitive_imports": health["imports"],
        "paper_disposition": {
            "paper_09": "UPDATE_INPUT_SHORTFALL_TO_HEALTH_ASSEMBLY_NONACTIVATION; PRESERVE_CONDITIONAL_THEOREMS",
            "paper_98": "REPLACE_PENDING_RECEIVER_LANGUAGE_WITH_CERTIFIED_UNSTABLE_BLOCKS_PLUS_UNDEFINED_REMAINDER",
            "paper_99": "STATE_NO_OPERATIONAL_COUNTERFLOW_REDSHIFT_AFTER_HEALTH_ASSEMBLY",
        },
        "mutations": {
            "unstable_block_as_healthy_receiver": "REJECT",
            "unknown_higher_j_as_stable_receiver": "REJECT",
            "legacy_pre_quotient_probe_as_receiver": "REJECT",
            "standalone_local_cocycle_as_physical_observable": "REJECT",
            "advanced_adjoint_as_response": "REJECT",
            "coordinate_ratio_as_redshift": "REJECT",
            "K_equals_raw_D": "REJECT",
        },
        "exact_checks": {
            "health_result_obstructed": health["result_state"] == "OBSTRUCTED_LINEAR_PHYSICAL_HEALTH_WITH_TYPED_HIGHER_J_CENSUS_SHORTFALL",
            "every_certified_block_unstable": health["certified_domain_summary"]["every_certified_isotype_has_a_physical_instability"],
            "every_certified_pairing_nonradical": all(block["pairing_radical_dimension"] == 0 for block in blocks),
            "remaining_quotient_undefined": health["remaining_carrier"]["physical_quotient_status"] == "NO_CERTIFIED_MAP",
            "remaining_pairing_undefined": health["remaining_carrier"]["pairing_inertia_status"] == "NO_CERTIFIED_MAP",
            "fixed_charge_clock_removed": "removed" in health["branch_verdicts"]["fixed_Q_rel"]["global_relative_clock"],
            "all_isotype_census_incomplete": health["terminal_verdict"]["all_isotype_spectral_census_complete"] is False,
        },
        "claim_boundary": {
            "establishes": ["typed nonactivation of the charged-time receiver and operational ratio after the repaired-q70 health assembly"],
            "does_not_establish": [
                "nonexistence on a future retuned healthy action",
                "higher-j physical spectrum",
                "nonlinear instability or blow-up",
                "physical redshift, particle, phenomenology or quantum claim",
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
        "schema": "counterflow-charged-time-physical-instantiation-after-repaired-q70-health-not-activated-v1",
        "result_id": "COUNTERFLOW_CHARGED_TIME_PHYSICAL_INSTANTIATION_AFTER_REPAIRED_Q70_HEALTH_NOT_ACTIVATED_V1",
        "claim_status": "NOT_ACTIVATED_NO_COMMON_HEALTHY_PHYSICAL_CLOCK_RECEIVER_CARRIER",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(payload_bytes).hexdigest()},
        "first_failed_receiver_gate": payload["ordered_gate"][3],
        "thirteen_field_interface": payload["thirteen_field_interface"],
        "frequency_ratio_result": payload["frequency_ratio_partial_function"],
        "paper_disposition": payload["paper_disposition"],
        "next_gate": "REQUIRE_A_SEPARATELY_CERTIFIED_RETUNED_ACTION_WITH_ONE_LINEARLY_HEALTHY_NONRADICAL_PHYSICAL_RECEIVER_AND_A_COMPLETE_SAME_CARRIER_D_R_REL_K_INTERFACE",
        "claim_boundary": (
            "The repaired-q70 health assembly certifies nonradical physical quotients for j=0,1/2,1, but every certified block is physically unstable on both charge branches; the j>=3/2 physical quotient and pairing are NO_CERTIFIED_MAP, and fixed-Q_rel reduction removes the relative clock. Therefore no common healthy physical clock-receiver carrier exists in the certified domain, none of the thirteen receiver-interface fields is populated on one carrier, and the operational frequency-ratio domain is empty."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_counterflow_charged_time_physical_instantiation_after_repaired_q70_health_nonactivation --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_counterflow_charged_time_physical_instantiation_after_repaired_q70_health_nonactivation",
            "source_sha256": sha(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Counterflow charged-time physical instantiation not activated

The repaired-q70 health assembly supplies no eligible common clock-receiver
carrier.  Its complete certified domain, j=0,1/2,1 with all m,k, has
nonradical physical quotients but every block is unstable.  The remaining
j>=3/2 physical quotient and pairing are undefined.  Fixed charge removes the
relative clock.  The thirteen-field receiver interface and operational
frequency-ratio domain therefore remain unpopulated.
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
        REPORT.write_text(report_text())
    else:
        print(json.dumps(cert, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
