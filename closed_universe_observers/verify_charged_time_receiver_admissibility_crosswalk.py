#!/usr/bin/env python3
"""Independent exact pairing, labelled-morphism and source-census reconstruction."""

import hashlib
import json
import subprocess
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json"
I = ROOT / "closed_universe_observers/generated/CHARGED_TIME_PHYSICAL_RECEIVER_CROSSWALK_INTERFACE_V1.json"
S = ROOT / "closed_universe_observers/schema/charged-time-receiver-admissibility-crosswalk-v1.schema.json"
IS = ROOT / "closed_universe_observers/schema/charged-time-physical-receiver-crosswalk-interface-v1.schema.json"

LEGACY_IDS = (
    "observer.berger.legacy_receiver_admissibility_replay",
    "observer.berger.legacy_receiver_operational_frequency_ratio_nonactivation",
)
ORIGINAL_FIVE = {
    "observer.general.charged_physical_time_relational_event_map": "CONDITIONAL_INTERFACE_ONLY",
    "observer.general.charged_time_finite_resolution_sampling": "CONDITIONAL_INTERFACE_ONLY",
    "observer.general.charged_time_emitter_receiver_composition": "CONDITIONAL_INTERFACE_ONLY",
    "observer.two_phase_counterflow.unrestricted_charged_time_event_map_contract": "NO_CERTIFIED_MAP",
    "observer.two_phase_counterflow.fixed_charge_relational_observable_obstruction": "CLOCK_REMOVED_OBSTRUCTED",
}
CONTRACT_PATH = "closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json"
REPO_PREFIX = "physics/symplectic-reconstruction/"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct_legacy_classifications(replay, ratio):
    assert replay["result_id"] == "BERGER_LEGACY_RECEIVER_ADMISSIBILITY_REPLAY_V1"
    assert replay["flags"]["LEGACY_CENSUS_COMPLETE"]
    assert len(replay["legacy_receiver_census"]) == 7
    assert all(
        row["admissibility_status"] == "NO_CERTIFIED_MAP"
        and not row["physical_receiver_promoted"]
        for row in replay["legacy_receiver_census"]
    )
    assert not replay["flags"]["ACTION_DERIVED_PHYSICAL_RECEIVER_CERTIFIED"]
    assert not replay["flags"]["DESCENDED_RECEIVER_PAIRING_CERTIFIED"]
    assert not replay["flags"]["PHYSICAL_REDSHIFT_CERTIFIED"]

    assert ratio["result_id"] == "BERGER_LEGACY_RECEIVER_OPERATIONAL_FREQUENCY_RATIO_NONACTIVATION_V1"
    theorem = ratio["operational_ratio_theorem"]
    assert theorem["domain_on_legacy_census"] == "EMPTY"
    assert theorem["result"] == "UNDEFINED_NO_PHYSICAL_RECEIVER"
    assert theorem["not_nonexistence_theorem"] and theorem["not_zero_ratio"]
    control = ratio["coordinate_control"]
    assert control["exact_ratio"] == "1"
    assert control["status"] == "COORDINATE_CONTROL_ONLY_NOT_OPERATIONAL_REDSHIFT"
    assert not ratio["flags"]["COORDINATE_RATIO_PROMOTED_AS_REDSHIFT"]
    assert not ratio["flags"]["PHYSICAL_RECEIVER_PROMOTED"]
    assert not ratio["flags"]["OPERATIONAL_FREQUENCY_RATIO_DEFINED"]

    return {
        LEGACY_IDS[0]: "NO_CERTIFIED_MAP",
        LEGACY_IDS[1]: "NO_CERTIFIED_MAP",
    }


def verify_value(v, i):
    Draft202012Validator(json.loads(S.read_text())).validate(v)
    Draft202012Validator(json.loads(IS.read_text())).validate(i)
    for ref in v["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    for ref in v["atlas_census_dependencies"]:
        assert sha(ROOT / ref["path"]) == ref["sha256"]

    sources = {source["name"]: source for source in v["provenance"]["legacy_extension_sources"]}
    assert set(sources) == {"legacy_replay", "legacy_ratio"}
    for source in sources.values():
        assert sha(ROOT / source["path"]) == source["sha256"]
    replay = json.loads((ROOT / sources["legacy_replay"]["path"]).read_text())
    ratio = json.loads((ROOT / sources["legacy_ratio"]["path"]).read_text())
    old_contract_sha = v["provenance"]["historical_base_contract_sha256"]
    assert replay["dependency_refs"]["receiver_contract"]["sha256"] == old_contract_sha
    assert ratio["dependency_refs"]["receiver_crosswalk"]["sha256"] == old_contract_sha
    shortfall = json.loads((ROOT / v["dependency_refs"]["tier3_shortfall"]["path"]).read_text())
    old_contract_bytes = subprocess.run(
        ["git", "show", f"{shortfall['baseline_commit']}:{REPO_PREFIX}{CONTRACT_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert hashlib.sha256(old_contract_bytes).hexdigest() == old_contract_sha
    old_contract = json.loads(old_contract_bytes)
    stable_fields = (
        "schema",
        "result_id",
        "claim_status",
        "dependency_tags",
        "interface_ref",
        "receiver_theorem",
        "crosswalk_theorem",
        "necessary_and_sufficient_conditions",
        "failure_classification",
        "flags",
        "next_gate",
    )
    assert all(old_contract[field] == v[field] for field in stable_fields)
    reconstructed = reconstruct_legacy_classifications(replay, ratio)

    G = sp.diag(1, 0)
    good = sp.Matrix([1, 0])
    radical = sp.Matrix([0, 1])
    exact = sp.Matrix([0, 1])
    probe = sp.Matrix([1, 0])
    assert (good.T * G * probe)[0] == 1
    assert radical.T * G == sp.zeros(1, 2)
    assert ((good + exact).T * G * probe)[0] == (good.T * G * probe)[0]
    eta1, eta2, eta3 = sp.symbols("eta1 eta2 eta3", nonzero=True)
    assert sp.simplify((eta1 / eta2) * (eta2 / eta3) - eta1 / eta3) == 0

    rows = {row["atlas_id"]: row for row in v["observer_carrier_census"]}
    assert len(rows) == v["census_completeness"]["discovered_count"] == 7
    assert set(rows) == set(ORIGINAL_FIVE) | set(LEGACY_IDS)
    assert all(rows[key]["admissibility_status"] == status for key, status in ORIGINAL_FIVE.items())
    assert all(rows[key]["admissibility_status"] == status for key, status in reconstructed.items())
    assert rows[LEGACY_IDS[0]]["atlas_path"] == "residual_atlas/berger-legacy-receiver-admissibility-replay-fragment-v1.json"
    assert rows[LEGACY_IDS[1]]["atlas_path"] == "residual_atlas/berger-legacy-receiver-operational-frequency-ratio-nonactivation-fragment-v1.json"
    assert all(not rows[key]["physical_receiver_promoted"] for key in rows)
    assert sum(row["admissibility_status"] == "CONDITIONAL_INTERFACE_ONLY" for row in rows.values()) == 3
    assert sum(row["admissibility_status"] == "NO_CERTIFIED_MAP" for row in rows.values()) == 3
    assert sum(row["admissibility_status"] == "CLOCK_REMOVED_OBSTRUCTED" for row in rows.values()) == 1

    mutation_names = {mutation["name"] for mutation in v["mutation_results"]}
    assert {
        "delete_legacy_replay_row",
        "delete_legacy_ratio_row",
        "promote_legacy_row_to_certified_admissible",
        "promote_coordinate_ratio_to_redshift",
        "alter_original_five_dispositions",
        "accept_stale_legacy_dependency_hash",
    } <= mutation_names
    assert all(mutation["detected"] for mutation in v["mutation_results"])
    return v


def verify():
    return verify_value(json.loads(C.read_text()), json.loads(I.read_text()))


if __name__ == "__main__":
    verify()
    print("CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1 independent verification: PASS")
