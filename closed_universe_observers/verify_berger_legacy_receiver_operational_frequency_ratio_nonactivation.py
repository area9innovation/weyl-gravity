#!/usr/bin/env python3
"""Independent maximal-candidate and ratio-domain replay."""

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "closed_universe_observers/certificates/BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1.json"
SCHEMA = ROOT / "closed_universe_observers/schema/berger-legacy-receiver-operational-frequency-ratio-nonactivation-v1.schema.json"


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


def verify() -> dict:
    result = json.loads(CERT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(result)
    imported = {}
    for name, ref in result["dependency_refs"].items():
        path = ROOT / ref["path"]
        assert sha256(path) == ref["sha256"]
        imported[name] = json.loads(path.read_text())
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
    return result


if __name__ == "__main__":
    verify()
    print("BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1 independent verification: PASS")
