#!/usr/bin/env python3
"""Generate the fail-closed physical-descent/frequency-ratio nonactivation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
PAYLOAD = P / "certificates/POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1_PAYLOAD.json"
CERT = P / "certificates/POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1.json"
REPORT = P / "reports/positive-berger-receiver-physical-descent-frequency-ratio-not-activated-v1.md"
DEPS = {
    "terminal_integration": P / "certificates/POSITIVE_BERGER_RECEIVER_BV_COCYCLE_INTEGRATION_GRADING_OBSTRUCTION_V1.json",
    "standalone_receiver": P / "certificates/POSITIVE_BERGER_LOCAL_RECEIVER_ACTION_PREFLIGHT_V1.json",
    "charged_time_admissibility": P / "certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_payload() -> dict[str, Any]:
    integration = json.loads(DEPS["terminal_integration"].read_text())
    receiver = json.loads(DEPS["standalone_receiver"].read_text())
    return {
        "schema": "positive-berger-receiver-physical-descent-frequency-ratio-not-activated-payload-v1",
        "result_id": "POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1_PAYLOAD",
        "scope": {
            "theory": "positive_Berger_action_derived_receiver_physical_descent",
            "background": "positive_Berger_Omega=3/4_D0_worldtube_and_repaired_counterflow_q70",
            "boundaries": "compact_D0_worldtube_before_ambient_quotient",
            "charge_sector": "fixed_Q_rel_parent_leaf_with_unrestricted_local_apparatus_fibre",
            "carrier": "receiver20_to_q70_combined_carrier_not_defined",
            "degree": [-1, 0, 1, 2],
            "parity": ["even", "odd"],
            "ell": "NOT_APPLICABLE_NO_COMBINED_QUOTIENT",
            "m": "NOT_APPLICABLE_NO_COMBINED_QUOTIENT",
            "k": "NOT_APPLICABLE_NO_COMBINED_QUOTIENT",
            "omega": "NOT_APPLICABLE_NO_OPERATIONAL_RATIO_DOMAIN",
        },
        "exact_import_disposition": {
            "standalone_local_action": receiver["gate_results"]["declared_master_action"],
            "standalone_local_receiver_cocycle": receiver["gate_results"]["compact_local_receiver_descent"],
            "ambient_integration": integration["atlas_status"],
            "receiver_cocycle_inclusion": integration["downstream_disposition"]["receiver_cocycle_inclusion"],
            "residual_quotient_input_map": integration["downstream_disposition"]["residual_quotient_input_map"],
        },
        "first_failed_intertwiner": {
            "name": "degree_zero_pairing_preserving_receiver20_to_q70_inclusion",
            "status": "OBSTRUCTED",
            "receiver_pairing_degree": -1,
            "q70_pairing_degree": 1,
            "degree_minus_one_injection_deficiency": 4,
            "evidence_result_id": integration["result_id"],
        },
        "charged_time_gate_ladder": [
            {"gate": "action_derived_local_BV_receiver", "status": "CERTIFIED_STANDALONE_ONLY"},
            {"gate": "ambient_unary_chain_and_pairing_inclusion", "status": "OBSTRUCTED", "first_failure": True},
            {"gate": "receiver_residual_cohomology_class", "status": "NOT_REACHED"},
            {"gate": "descended_nonradical_pairing_and_period", "status": "NOT_REACHED"},
            {"gate": "same_carrier_retarded_support_map", "status": "NOT_REACHED"},
            {"gate": "monotone_clock_interval_and_positive_denominator_margin", "status": "NOT_REACHED"},
            {"gate": "separate_D_R_K_actions_on_physical_receiver", "status": "NOT_REACHED"},
            {"gate": "action_derived_emitter_and_transported_phase", "status": "NOT_REACHED"},
            {"gate": "operational_frequency_ratio", "status": "NOT_ACTIVATED"},
        ],
        "frequency_ratio_partial_function": {
            "domain": [],
            "domain_cardinality": 0,
            "value": "UNDEFINED",
            "coordinate_ratio_promoted": False,
            "redshift_claim": "NO_CERTIFIED_MAP",
        },
        "mutations": {
            "call_standalone_A_physical": {"failure": "no ambient inclusion or quotient representative", "rejected": True},
            "ignore_pairing_degree_obstruction": {"failure": "combined cyclic pairing is not homogeneous", "rejected": True},
            "reuse_coordinate_frequency_ratio_one": {"failure": "no action-derived receiver event map or denominator", "rejected": True},
            "use_advanced_covector_as_response": {"failure": "advanced covector is preparation data, not causally acquired response", "rejected": True},
            "add_emitter_before_receiver_descent": {"failure": "stop condition forbids widening after the first failed intertwiner", "rejected": True},
        },
        "downstream_disposition": {
            "physical_receiver": "NO_CERTIFIED_MAP",
            "descended_pairing_period": "NO_CERTIFIED_MAP",
            "positive_denominator_margin": "NO_CERTIFIED_MAP",
            "operational_frequency_ratio": "NOT_ACTIVATED",
            "relational_redshift": "NO_CERTIFIED_MAP",
        },
        "exact_checks": {
            "integration_terminal_is_obstructed": integration["atlas_status"] == "OBSTRUCTED",
            "local_class_not_called_physical": True,
            "frequency_ratio_domain_empty": True,
            "advanced_covector_not_response": True,
        },
        "claim_boundary": {
            "establishes": ["typed nonactivation at the first failed ambient receiver intertwiner"],
            "does_not_establish": ["nonexistence after a regraded receiver action", "physical receiver, frequency ratio or redshift", "nonlinear, particle or quantum result"],
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    refs = {}
    for name, path in DEPS.items():
        data = json.loads(path.read_text())
        refs[name] = {"path": str(path.relative_to(ROOT)), "result_id": data["result_id"], "sha256": sha(path)}
    payload_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    return {
        "schema": "positive-berger-receiver-physical-descent-frequency-ratio-not-activated-v1",
        "result_id": "POSITIVE_BERGER_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1",
        "setting_id": "positive_Berger_receiver20_q70_physical_descent",
        "claim_status": "NOT_ACTIVATED_AT_FIRST_FAILED_AMBIENT_RECEIVER_INTERTWINER",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(payload_bytes).hexdigest()},
        "first_failed_intertwiner": payload["first_failed_intertwiner"],
        "frequency_ratio_result": payload["frequency_ratio_partial_function"],
        "downstream_disposition": payload["downstream_disposition"],
        "next_gate": "REISSUE_AND_INTEGRATE_A_Q70_GRADED_RECEIVER_ACTION_BEFORE_RETRYING_PHYSICAL_DESCENT",
        "claim_boundary": (
            "The standalone D0 action and local receiver cocycle remain certified, but the terminal integration result obstructs the degree-zero pairing-preserving receiver20-to-q70 inclusion and exports no residual-quotient input map. Under the charged-time admissibility contract this is the first failed intertwiner, so the local cocycle is not called a physical receiver. Residual cohomology, descended nonradical pairing and period, same-carrier retarded map, denominator margin, physical D/R/K actions and emitter phase are not reached. The operational frequency-ratio partial function therefore has empty domain and no value; no coordinate ratio is promoted to redshift. This is a typed nonactivation, not a nonexistence theorem after regrading, and makes no nonlinear, particle, phenomenology or quantum claim."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_positive_berger_receiver_physical_descent_frequency_ratio_nonactivation --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_positive_berger_receiver_physical_descent_frequency_ratio_nonactivation",
            "source_sha256": sha(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Positive-Berger physical receiver and frequency ratio not activated

The standalone D0 cocycle does not reach the physical-receiver gate.  Its
terminal integration theorem obstructs the first required chain/pairing
intertwiner and supplies no residual-quotient input map.  The charged-time
gate ladder therefore stops before cohomology, nonradical pairing, period,
denominator, emitter phase or response.

The operational frequency-ratio partial function has empty domain and no
value.  No coordinate-frequency ratio is called redshift.  Retry requires a
regraded, action-derived receiver contract and a successful q70 pushout.
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
