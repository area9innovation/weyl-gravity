#!/usr/bin/env python3
"""Generate the final regraded-receiver physical-descent nonactivation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
PAYLOAD = P / "certificates/POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1_PAYLOAD.json"
CERT = P / "certificates/POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1.json"
REPORT = P / "reports/positive-berger-regraded-receiver-physical-descent-frequency-ratio-not-activated-v1.md"
DEPS = {
    "regraded_integration": P / "certificates/POSITIVE_BERGER_RECEIVER_REGRADED_ACTION_COCHAIN_INTERTWINER_OBSTRUCTION_V1.json",
    "charged_time_admissibility": P / "certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json",
    "generic_health": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_V1.json",
    "charge_clock": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json",
    "fixed_charge_health": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_payload() -> dict[str, Any]:
    integration = json.loads(DEPS["regraded_integration"].read_text())
    generic = json.loads(DEPS["generic_health"].read_text())
    charge = json.loads(DEPS["charge_clock"].read_text())
    fixed = json.loads(DEPS["fixed_charge_health"].read_text())
    return {
        "schema": "positive-berger-regraded-receiver-physical-descent-frequency-ratio-not-activated-payload-v1",
        "result_id": "POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1_PAYLOAD",
        "scope": {
            "theory": "regraded_positive_Berger_receiver_physical_descent",
            "background": "counterflow_positive_Berger_a=1_c_squared=9/40_Omega=3/4",
            "boundaries": "compact_D0_worldtube_before_combined_quotient",
            "charge_sector": "fixed_and_unrestricted_Q_rel_branches_kept_distinct",
            "carrier": "no_combined_receiver_q70_carrier",
            "degree": [0, 1],
            "parity": ["even", "odd"],
            "ell": "NOT_APPLICABLE_NO_QUOTIENT_INPUT",
            "m": "NOT_APPLICABLE_NO_QUOTIENT_INPUT",
            "k": "NOT_APPLICABLE_NO_QUOTIENT_INPUT",
            "omega": "NOT_APPLICABLE_EMPTY_RATIO_DOMAIN",
        },
        "first_failed_map": {
            "name": integration["first_obstruction"]["first_failed_gate"],
            "status": "OBSTRUCTED",
            "source_degree": integration["first_obstruction"]["source_degree"],
            "target_degree": integration["first_obstruction"]["target_degree"],
            "homogeneous_degree_separation": integration["first_obstruction"]["homogeneous_degree_separation"],
            "quotient_input": integration["downstream_disposition"]["physical_descent_input_contract"],
        },
        "ordered_admissibility_ladder": [
            {"gate": "fresh_regraded_action_chain", "status": "CERTIFIED"},
            {"gate": "fresh_local_BV_receiver_cochain", "status": "CERTIFIED"},
            {"gate": "degree_zero_cochain_to_q70_chain_inclusion", "status": "OBSTRUCTED", "first_failure": True},
            {"gate": "combined_residual_cohomology_and_radical_quotient", "status": "NOT_REACHED"},
            {"gate": "nonzero_descended_period", "status": "NOT_REACHED"},
            {"gate": "retarded_event_map_and_clock_interval", "status": "NOT_REACHED"},
            {"gate": "positive_denominator_and_operational_frequency_ratio", "status": "NOT_ACTIVATED"},
        ],
        "independent_classical_dispositions": {
            "fixed_Q_rel": {"result_id": fixed["result_id"], "status": fixed["result_state"], "receiver_effect": "relative clock cohomology and phase pairing vanish"},
            "unrestricted_Q_rel": {"result_id": charge["result_id"], "status": charge["result_state"], "receiver_effect": "charged raw-D clock has a size-two secular zero Jordan block"},
            "first_generic_physical_block": {"result_id": generic["result_id"], "status": generic["result_state"], "receiver_effect": "j=1/2 complex-frequency modes cannot be used as a healthy preparation"},
            "ordering": "secondary; none supersedes the earlier receiver inclusion obstruction",
        },
        "frequency_ratio_partial_function": {
            "domain": [],
            "domain_cardinality": 0,
            "value": "UNDEFINED",
            "compact_phase_alternative": "NOT_REACHED",
            "frequency_modulated_alternative": "NOT_REACHED",
            "coordinate_ratio_promoted": False,
            "redshift": "NO_CERTIFIED_MAP",
        },
        "mutations": {
            "treat_cochain_as_q70_chain": {"failure": "compact differential degrees -1 and +1 conflated", "rejected": True},
            "skip_quotient_input": {"failure": "local cocycle called physical without an ambient representative", "rejected": True},
            "resurrect_fixed_charge_clock": {"failure": "contradicts zero relative-clock cohomology and phase pairing", "rejected": True},
            "use_unstable_j_half_mode": {"failure": "contradicts current generic physical-health obstruction", "rejected": True},
            "coordinate_ratio_as_redshift": {"failure": "empty operational domain and no denominator", "rejected": True},
        },
        "downstream_disposition": {
            "physical_receiver": "NO_CERTIFIED_MAP",
            "nonradical_pairing_period": "NO_CERTIFIED_MAP",
            "causal_emitter_receiver_map": "NO_CERTIFIED_MAP",
            "operational_frequency_ratio": "NOT_ACTIVATED",
            "relational_redshift": "NO_CERTIFIED_MAP",
        },
        "exact_checks": {
            "integration_obstructed": integration["atlas_status"] == "OBSTRUCTED",
            "quotient_input_absent": integration["downstream_disposition"]["physical_descent_input_contract"] == "NO_CERTIFIED_MAP",
            "fixed_and_unrestricted_charge_branches_separate": True,
            "ratio_domain_empty": True,
        },
        "claim_boundary": {
            "establishes": ["final typed nonactivation for the current regraded receiver architecture"],
            "does_not_establish": ["nonexistence after a certified chain/cochain suspension bridge", "physical ratio or redshift", "nonlinear, particle, phenomenology or quantum result"],
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    refs = {}
    for name, path in DEPS.items():
        data = json.loads(path.read_text())
        refs[name] = {"path": str(path.relative_to(ROOT)), "result_id": data["result_id"], "sha256": sha(path)}
    payload_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    return {
        "schema": "positive-berger-regraded-receiver-physical-descent-frequency-ratio-not-activated-v1",
        "result_id": "POSITIVE_BERGER_REGRADED_RECEIVER_PHYSICAL_DESCENT_FREQUENCY_RATIO_NOT_ACTIVATED_V1",
        "setting_id": "positive_Berger_regraded_receiver_current_architecture",
        "claim_status": "NOT_ACTIVATED_AT_REGRADED_RECEIVER_CHAIN_COCHAIN_INCLUSION",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": refs,
        "payload_ref": {"path": str(PAYLOAD.relative_to(ROOT)), "result_id": payload["result_id"], "sha256": hashlib.sha256(payload_bytes).hexdigest()},
        "first_failed_map": payload["first_failed_map"],
        "frequency_ratio_result": payload["frequency_ratio_partial_function"],
        "classical_dispositions": payload["independent_classical_dispositions"],
        "downstream_disposition": payload["downstream_disposition"],
        "next_gate": "ADD_A_CERTIFIED_ACTION_DERIVED_CHAIN_COCHAIN_SUSPENSION_BRIDGE_THEN_REPLAY_INTEGRATION_BEFORE_PHYSICAL_DESCENT",
        "claim_boundary": (
            "The fresh regraded receiver action chain and local BV cochain are individually certified, but their terminal integration result obstructs the first degree-zero cochain-to-q70-chain inclusion and exports no physical-descent quotient input. The charged-time admissibility ladder therefore stops before residual cohomology, radical quotient, nonzero period, retarded event map, clock interval, denominator or emitter phase. Independently, the current Classical fixed-Q_rel branch removes the relative clock, the unrestricted branch has a secular zero Jordan obstruction, and the first generic j=1/2 physical block has complex-frequency modes; these are secondary dispositions and are not used to bypass the earlier inclusion failure. The operational frequency-ratio partial function has empty domain and no value, and no coordinate ratio is promoted to redshift."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_positive_berger_regraded_physical_descent_frequency_ratio_nonactivation --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_positive_berger_regraded_physical_descent_frequency_ratio_nonactivation",
            "source_sha256": sha(Path(__file__)),
        },
    }


def report_text() -> str:
    return """# Regraded receiver physical descent and ratio not activated

The current regraded architecture ends at its first ambient inclusion map.
No quotient input exists, so the local cochain is not a physical receiver and
the operational frequency-ratio domain is empty.  The fixed-charge clock
contraction, unrestricted secular clock obstruction and generic j=1/2 health
obstruction are recorded as independent secondary failures, not substitutes
for the earlier receiver inclusion gate.
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
