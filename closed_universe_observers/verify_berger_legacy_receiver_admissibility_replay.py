#!/usr/bin/env python3
"""Independent symbolic and structural replay of the legacy receiver census."""

import hashlib
import json
from pathlib import Path
import sys

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ci.standalone_provenance import read_attached_blob


CERT = ROOT / "closed_universe_observers/certificates/BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1.json"
SCHEMA = ROOT / "closed_universe_observers/schema/berger-legacy-receiver-admissibility-replay-v1.schema.json"
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
    _, payload = read_attached_blob(
        ref["source_commit"],
        ref["repository_path"],
        ref["sha256"],
    )
    document = json.loads(payload)
    dispositions = {
        row["atlas_id"]: row["admissibility_status"]
        for row in document["observer_carrier_census"]
    }
    assert dispositions == HISTORICAL_DISPOSITIONS
    assert document["census_completeness"]["discovered_count"] == 5
    return document


def verify() -> dict:
    result = json.loads(CERT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(result)
    imported = {}
    for name, ref in result["dependency_refs"].items():
        if name == "receiver_contract":
            imported[name] = resolve_historical_ref(ref)
        else:
            path = ROOT / ref["path"]
            assert sha256(path) == ref["sha256"]
            imported[name] = json.loads(path.read_text())
    current_crosswalk = ROOT / "closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json"
    assert sha256(current_crosswalk) != result["dependency_refs"]["receiver_contract"]["sha256"]

    k0, k1 = sp.symbols("k0 k1", nonzero=True)
    mu = sp.symbols("mu")
    assert sp.Matrix([[k0, 0], [mu, k1]]).rank() == 2
    dyn = imported["dynamical_emitter"]
    assert dyn["transfer_matrix"]["matrix"] == [["kappa_0", "0"], ["mu", "kappa_1"]]

    beta, s0, c1 = sp.symbols("beta s0 c1", positive=True)
    assert sp.Matrix([[-beta * s0, 0], [mu, beta * c1]]).rank() == 2
    loc = imported["localized_transfer"]
    assert loc["transfer_matrix"]["rank"] == 2
    assert "disjoint from J^-(supp Q_0)" in loc["causal_support"]["late_source_to_early_detector"]

    c00, c11 = sp.symbols("c00 c11", positive=True)
    assert sp.diag(c00, c11).rank() == 2
    smeared = imported["smeared_transfer"]
    assert smeared["retarded_maxwell_solution"]["advanced_solution_excluded"] is True
    assert smeared["flags"]["D_DESCENT_WITH_SOURCE_ROD_MEMORY_SECTOR_CERTIFIED"] is False

    records = imported["detector_records"]
    assert sp.Matrix(records["smearing_independence"]["evaluation_matrix"]).rank() == 2
    assert records["flags"]["SMEARED_RETARDED_TRANSFER_MATRIX_RANK_TWO"] is False
    assert records["gauge_and_quotient_tests"]["raw_D"].startswith("OPEN")
    assert records["gauge_and_quotient_tests"]["K_Berger"].startswith("OPEN")

    covectors = imported["detector_covectors"]
    assert covectors["advanced_detector_to_emitter_covector"]["green_images_evaluated"] is False
    assert "adv" in covectors["advanced_detector_to_emitter_covector"]["maxwell_advanced_field"]
    selected = imported["selected_preparations"]
    assert selected["flags"]["ADVANCED_GREEN_IMAGES_EVALUATED"] is False
    assert imported["quartic_redshift"]["calibration_map_disposition"]["rank"] == "NOT_APPLICABLE_EMPTY_DOMAIN"

    legacy_docs = [imported[row["legacy_key"]] for row in result["legacy_receiver_census"]]
    required_absent = {
        "local_BV_class", "cocycle_witness", "representative_quotient",
        "descended_pairing", "nonradical_witness", "nonzero_period",
        "sampled_denominator_margin", "D_action", "R_action", "K_action",
    }
    for doc in legacy_docs:
        assert required_absent.isdisjoint(set(all_keys(doc)))

    rows = result["legacy_receiver_census"]
    assert len(rows) == 7
    assert all(not row["physical_receiver_promoted"] for row in rows)
    assert all(row["admissibility_status"] == "NO_CERTIFIED_MAP" for row in rows)
    assert len({row["result_id"] for row in rows}) == 7
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
    print("BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1 independent verification: PASS")
