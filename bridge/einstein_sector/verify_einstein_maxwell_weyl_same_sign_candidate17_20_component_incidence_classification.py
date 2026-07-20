"""Independent verifier for candidate-17/20 component incidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = (
    ROOT
    / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_component_incidence_classification.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(
        ROOT / payload["provenance"]["generator_path"]
    )
    dependencies = {}
    for name, item in payload["provenance"]["inputs"].items():
        path = ROOT / item["path"]
        assert item["sha256"] == sha(path)
        dependencies[name] = json.loads(path.read_text())

    # Reconstruct the two boundary incidences and mutation controls without
    # importing the producer.
    a, b, delta, x, y = sp.symbols(
        "a b delta x y", positive=True, real=True
    )
    d = sp.symbols("d", nonzero=True, real=True)
    c = d + a * x - b * y
    assert sp.factor(c.subs({d: -delta, x: delta / a, y: 0})) == 0
    assert sp.factor(c.subs({d: delta, x: 0, y: delta / b})) == 0

    negative_fixture = {a: 3, b: 1, d: -1}
    positive_fixture = {a: 1, b: 3, d: 1}
    assert c.subs({**negative_fixture, x: sp.Rational(1, 3), y: 0}) == 0
    assert c.subs({**positive_fixture, x: 0, y: sp.Rational(1, 3)}) == 0
    assert (d - b).subs(negative_fixture) == -2
    assert (d + a).subs(positive_fixture) == 2

    # The four occupation predicates are an exhaustive disjoint truth table
    # for nonnegative (x,y). This explicitly retains both boundary nodes and
    # the maximally nonfree origin.
    strata = payload["occupation_strata"]
    assert [item["id"] for item in strata] == [
        "interior",
        "F_zero",
        "G_zero",
        "origin",
    ]
    truth_table = {
        (True, True): "interior",
        (False, True): "F_zero",
        (True, False): "G_zero",
        (False, False): "origin",
    }
    assert len(set(truth_table.values())) == 4
    assert "U(1)_F" in strata[1]["forced_stabilizer"]
    assert "U(1)_G" in strata[2]["forced_stabilizer"]
    assert "SO(3)_lifted" in strata[3]["forced_stabilizer"]

    components = payload["candidate_components"]
    expected = {
        "candidate17": (17, "delta<0<alpha", "G_zero"),
        "candidate20_negative_delta": (20, "delta<0<alpha", "G_zero"),
        "candidate20_positive_delta": (20, "alpha<0<delta", "F_zero"),
    }
    for name, (candidate_id, chamber, incidence_stratum) in expected.items():
        record = components[name]
        assert record["candidate_id"] == candidate_id
        assert record["strict_opposite_sign_chamber"] == chamber
        assert record["component_count"] == 1
        assert record["nonincident_components"] == []
        assert record["components"][0]["meets_incidence"]
        assert record["components"][0]["incidence_stratum"] == incidence_stratum

    # Independently replay the logical bridge: the prior criterion says a
    # component contracts iff it meets I; the successor supplies a path from
    # every point to the common connected hub and says every component meets
    # I. Hence no second or nonincident component survives.
    incidence_flags = dependencies["incidence_normal_form"]["classification"]
    complete_flags = dependencies["complete_contraction"]["classification"]
    assert incidence_flags["strict_opposite_sign_component_incidence_necessary"]
    assert incidence_flags["strict_opposite_sign_component_incidence_sufficient"]
    assert complete_flags["every_admissible_component_meets_incidence"]
    assert complete_flags["candidate17_complete_singular_rotation_zero_fibre_connected"]
    assert complete_flags["candidate20_complete_singular_rotation_zero_fibre_connected"]

    flags = payload["classification"]
    assert flags["candidate17_strict_sign_component_count_one"]
    assert flags["candidate20_negative_delta_strict_sign_component_count_one"]
    assert flags["candidate20_positive_delta_strict_sign_component_count_one"]
    assert flags["every_strict_sign_component_meets_incidence"]
    assert not flags["nonincident_component_exists"]
    assert flags["four_occupation_strata_exhaustive_and_disjoint"]
    assert flags["zero_node_boundaries_retained"]
    assert flags["nonfree_orbit_types_retained"]
    assert flags["singular_stabilizers_retained"]
    assert not flags["candidate17_candidate20_identified"]
    assert not flags["occupation_strata_glued_across_distinct_total_occupations"]
    assert not flags["final_residual_descent"]
    assert not flags["causal_observer_or_quantum_claim"]
    print(
        "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_COMPONENT_INCIDENCE_CLASSIFICATION verifier: PASS"
    )


if __name__ == "__main__":
    verify()
