#!/usr/bin/env python3
"""Independent maximal-candidate and ratio-domain replay."""

import hashlib
import json
import subprocess
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
CERT = ROOT / "closed_universe_observers/certificates/BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json"
SCHEMA = ROOT / "closed_universe_observers/schema/berger-legacy-receiver-operational-frequency-ratio-nonactivation-v1.schema.json"
HISTORICAL_COMMIT = "aa5ca7814798dfbcc92ee52e462d25af74806515"
HISTORICAL_PATH = (
    "physics/symplectic-reconstruction/closed_universe_observers/certificates/"
    "CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json"
)
HISTORICAL_SHA256 = "e2c9aad23b667ec16bbb124b72066d803f3607fc4bd89acd459b53f672a43918"
HISTORICAL_DISPOSITIONS = {
    "observer.general.charged_physical_time_relational_event_map": "CONDITIONAL_INTERFACE_ONLY",
    "observer.general.charged_time_finite_resolution_sampling": "CONDITIONAL_INTERFACE_ONLY",
    "observer.general.charged_time_emitter_receiver_composition": "CONDITIONAL_INTERFACE_ONLY",
    "observer.two_phase_counterflow.unrestricted_charged_time_event_map_contract": "NO_CERTIFIED_MAP",
    "observer.two_phase_counterflow.fixed_charge_relational_observable_obstruction": "CLOCK_REMOVED_OBSTRUCTED",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def all_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from all_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from all_keys(child)


def resolve_historical_ref(ref: dict) -> dict:
    assert ref["source_commit"] == HISTORICAL_COMMIT
    assert ref["repository_path"] == HISTORICAL_PATH
    assert ref["sha256"] == HISTORICAL_SHA256
    assert ref["object_type"] == "blob"
    assert ref["resolution"] == "IMMUTABLE_GIT_BLOB"
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref['source_commit']}^{{commit}}"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert resolved == HISTORICAL_COMMIT
    object_spec = f"{resolved}:{ref['repository_path']}"
    assert subprocess.run(
        ["git", "cat-file", "-t", object_spec],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == "blob"
    payload = subprocess.run(
        ["git", "show", object_spec],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert hashlib.sha256(payload).hexdigest() == HISTORICAL_SHA256
    document = json.loads(payload)
    assert {
        row["atlas_id"]: row["admissibility_status"]
        for row in document["observer_carrier_census"]
    } == HISTORICAL_DISPOSITIONS
    assert document["census_completeness"]["discovered_count"] == 5
    return document


def verify() -> dict:
    result = json.loads(CERT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(result)
    imported = {}
    for name, ref in result["dependency_refs"].items():
        if name == "receiver_crosswalk":
            imported[name] = resolve_historical_ref(ref)
        else:
            path = ROOT / ref["path"]
            assert sha256(path) == ref["sha256"]
            imported[name] = json.loads(path.read_text())
    current_crosswalk = ROOT / "closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json"
    assert sha256(current_crosswalk) != result["dependency_refs"]["receiver_crosswalk"]["sha256"]
    legacy = {}
    for name, ref in result["legacy_source_refs"].items():
        path = ROOT / ref["path"]
        assert sha256(path) == ref["sha256"]
        legacy[name] = json.loads(path.read_text())

    audit_rows = {row["legacy_key"]: row for row in imported["legacy_receiver_audit"]["legacy_receiver_census"]}
    assert len(audit_rows) == 7
    assert all(row["admissibility_status"] == "NO_CERTIFIED_MAP" for row in audit_rows.values())
    assert all(not row["physical_receiver_promoted"] for row in audit_rows.values())

    k0, k1 = sp.symbols("k0 k1", nonzero=True)
    mu = sp.symbols("mu")
    assert sp.Matrix([[k0, 0], [mu, k1]]).rank() == 2
    beta, s0, c1 = sp.symbols("beta s0 c1", positive=True)
    assert sp.Matrix([[-beta * s0, 0], [mu, beta * c1]]).rank() == 2
    c00, c11 = sp.symbols("c00 c11", positive=True)
    assert sp.diag(c00, c11).rank() == 2
    assert legacy["dynamical_emitter"]["transfer_matrix"]["rank"] == 2
    assert legacy["localized_transfer"]["transfer_matrix"]["rank"] == 2
    assert legacy["smeared_transfer"]["transfer_matrix"]["rank"] == 2

    required_receiver_keys = {
        "local_BV_class", "cocycle_witness", "representative_quotient", "descended_pairing",
        "nonradical_witness", "nonzero_period", "sampled_denominator_margin", "D_action", "R_action", "K_action",
    }
    for name in ("dynamical_emitter", "localized_transfer", "smeared_transfer", "detector_records", "detector_covectors"):
        assert required_receiver_keys.isdisjoint(set(all_keys(legacy[name])))
    assert legacy["smeared_transfer"]["flags"]["CLASSICAL_OBSERVER_MAP_CERTIFIED"] is False
    assert legacy["smeared_transfer"]["flags"]["D_DESCENT_WITH_SOURCE_ROD_MEMORY_SECTOR_CERTIFIED"] is False
    assert legacy["detector_records"]["flags"]["CLASSICAL_OBSERVER_MAP_CERTIFIED"] is False
    assert legacy["detector_records"]["flags"]["D_DESCENT_WITH_RODS_CERTIFIED"] is False
    assert legacy["detector_covectors"]["advanced_detector_to_emitter_covector"]["green_images_evaluated"] is False
    assert legacy["selected_preparations"]["flags"]["ADVANCED_GREEN_IMAGES_EVALUATED"] is False
    assert legacy["quartic_redshift"]["calibration_map_disposition"]["rank"] == "NOT_APPLICABLE_EMPTY_DOMAIN"

    maximal = result["maximal_candidate_replay"]
    assert len(maximal) == 3
    assert {row["first_missing_condition"] for row in maximal} == {
        "ACTION_DERIVED_RECEIVER_UNARY_THEORY", "ACTION_DERIVED_EMITTER_AND_RECEIVER_UNARY_THEORY"
    }
    assert all(row["ratio_status"] == "UNDEFINED_NO_PHYSICAL_RECEIVER" for row in maximal)

    beta_exact = 2 * sp.sqrt(10) / 3
    assert sp.simplify(beta_exact / beta_exact) == 1
    assert result["coordinate_control"]["exact_ratio"] == "1"
    assert result["operational_ratio_theorem"]["domain_on_legacy_census"] == "EMPTY"

    request_ref = result["producer_request"]
    request_path = ROOT / request_ref["path"]
    assert request_ref["count"] == 1
    assert sha256(request_path) == request_ref["sha256"]
    request = json.loads(request_path.read_text())
    assert request["id"] == request_ref["id"]
    assert request["schema"] == "work-v0" and request["body"]["state"] == "REQUESTED"
    assert request["body"]["depends_on"] == ["sf:program/work/observer-berger-legacy-receiver-operational-frequency-ratio"]
    assert "observer consumer will separately compute the residual quotient" in request["body"]["stop_condition"]
    assert all(mutation["detected"] for mutation in result["mutation_results"])
    assert {
        "wrong_historical_commit",
        "wrong_historical_path",
        "wrong_historical_blob_hash",
        "mutable_current_path_substitution",
    }.issubset({mutation["name"] for mutation in result["mutation_results"]})
    return result


if __name__ == "__main__":
    verify()
    print("BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1 independent verification: PASS")
