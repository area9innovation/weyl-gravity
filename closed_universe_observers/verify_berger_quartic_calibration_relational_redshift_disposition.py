#!/usr/bin/env python3
"""Independently verify the quartic calibration/redshift disposition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = (
    P
    / "certificates/BERGER_QUARTIC_CALIBRATION_RELATIONAL_REDSHIFT_DISPOSITION.json"
)
SCHEMA = (
    P
    / "schema/berger-quartic-calibration-relational-redshift-disposition-v1.schema.json"
)
EXPECTED = {
    "quartic_family": P
    / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE.json",
    "quartic_family_payload": P
    / "certificates/BERGER_QUARTIC_COMMON_ACTION_COMPLETION_MODULE_PAYLOAD.json",
    "quartic_moduli_gate": P
    / "certificates/BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE.json",
    "quartic_moduli_payload": P
    / "certificates/BERGER_QUARTIC_COMPLETION_MODULI_OBSERVER_INVARIANCE_PAYLOAD.json",
    "observable_disposition": P
    / "certificates/BERGER_COMMON_ACTION_OBSERVABLE_REPLAY_DISPOSITION.json",
    "latest_action_gate": P
    / "certificates/BERGER_DIRECT_TEMPORAL_AK_DIFF_COVARIANCE_REPAIR.json",
}


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    dependencies = {}
    for name, reference in value["dependency_refs"].items():
        path = ROOT / reference["path"]
        assert path == EXPECTED[name]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]
        dependency = json.loads(path.read_text())
        assert dependency["result_id"] == reference["result_id"]
        dependencies[name] = dependency

    family = dependencies["quartic_family"]
    payload = dependencies["quartic_family_payload"]
    assert len(payload["modules"]) == 12
    assert [row["Maxwell_and_U1_invariant_dimension"] for row in family[
        "module_classification"
    ]] == [6, 6]
    moduli = dependencies["quartic_moduli_gate"]
    assert len(moduli["completion_space"]["basis"]) == 12
    assert moduli["completion_space"]["q3_parameter_map_rank"] == 12
    assert moduli["full_arity_three_gate"]["admissible_subvariety"] == "EMPTY"
    assert moduli["full_arity_three_gate"]["witness_polynomial"] == (
        "-4*g0*h0 + sum_i lambda_i*0"
    )

    latest = dependencies["latest_action_gate"]
    assert latest["arity_two_gate"]["status"] == "OBSTRUCTED"
    assert latest["arity_two_gate"]["full_covariance_projection"] == (
        "EMPTY_ADMISSIBLE_LOCUS"
    )
    assert {
        (
            audit["complete_covariance_projection"]["action_image_rank"],
            audit["complete_covariance_projection"]["source_augmented_rank"],
        )
        for audit in latest["arity_two_gate"]["per_emitter_audits"].values()
    } == {(934, 935)}
    assert latest["arity_two_gate"]["decisive_witness"]["coefficient"] == [
        [-3, 1],
        [0, 1],
    ]

    calibration = value["calibration_map_disposition"]
    assert calibration["not_the_zero_map"] is True
    assert {
        calibration[name]
        for name in (
            "moduli_to_detector_tensor_polynomial",
            "rank",
            "kernel",
            "stabilizer_orbits",
            "blind_directions",
            "minimal_calibration_observables",
        )
    } == {"NOT_APPLICABLE_EMPTY_DOMAIN"}
    redshift = value["relational_redshift_disposition"]
    assert redshift["two_event_dynamical_clock_construction_performed"] is False
    assert redshift["transported_phase_rod_detector_construction_performed"] is False
    assert {
        redshift[name]
        for name in (
            "completion_independent_nonlinear_redshift",
            "gauge_invariance",
            "causal_support",
            "K_Berger_covariance",
            "backreacted_rank",
            "tangent_cone_admissibility",
            "Einstein_extra_Weyl_Maxwell_sensitivity",
        )
    } == {"NO_CERTIFIED_MAP"}
    survival = value["standalone_observable_survival_ledger"]
    imported = dependencies["observable_disposition"][
        "standalone_observable_survival_ledger"
    ]
    assert survival == imported
    assert not value["nonpromotion_theorem"][
        "linear_or_source_free_results_promoted"
    ]
    assert value["smallest_additional_action_representation"] == latest[
        "first_missing_action_representation"
    ]
    print(
        "BERGER_QUARTIC_CALIBRATION_RELATIONAL_REDSHIFT_DISPOSITION "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
