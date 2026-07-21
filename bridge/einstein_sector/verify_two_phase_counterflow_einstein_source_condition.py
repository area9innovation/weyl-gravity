#!/usr/bin/env python3
"""Independent consumer for the counterflow Einstein-source obstruction.

This verifier does not import the producer.  It replays input hashes, exact
Berger tensors, charge-sector logic, and fail-closed atlas statuses directly.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/TWO_PHASE_COUNTERFLOW_EINSTEIN_SOURCE_CONDITION_OBSTRUCTION_V1.json"
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-einstein-source-condition-obstruction-fragment-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    data = json.loads(CERT.read_text(encoding="utf-8"))
    assert data["result_id"] == "TWO_PHASE_COUNTERFLOW_EINSTEIN_SOURCE_CONDITION_OBSTRUCTION_V1"
    assert data["result_state"] == "OBSTRUCTED_BEFORE_LINEAR_MAP_BY_EXACT_BACKGROUND_NONINCIDENCE"
    assert data["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert sha(ROOT / data["schema_path"]) == data["schema_sha256"]
    for record in data["imports"].values():
        path = ROOT / record["path"]
        imported = json.loads(path.read_text(encoding="utf-8"))
        assert sha(path) == record["sha256"]
        assert imported["result_id"] == record["result_id"]

    q = sp.Rational(9, 40)
    eta = sp.diag(-1, 1, 1, 1)
    ricci = sp.diag(0, (2 - q) / 2, (2 - q) / 2, q / 2)
    scalar = sp.trace(eta * ricci)
    bach = sp.diag(
        (1 - q) ** 2 / 6,
        (1 - q) * (1 - 3 * q) / 6,
        (1 - q) * (1 - 3 * q) / 6,
        (1 - q) * (5 * q - 1) / 6,
    )
    stress = 5 * bach
    tracefree = ricci - scalar * eta / 4
    minor = sp.factor(tracefree[0, 0] * stress[1, 1] - tracefree[1, 1] * stress[0, 0])
    assert scalar == sp.Rational(151, 80)
    assert sp.trace(eta * stress) == 0
    assert stress[0, 0] == sp.Rational(961, 1920) > 0
    assert minor == -sp.Rational(279, 2560) != 0
    assert sp.factor(tracefree[0, 0] / stress[0, 0]) == sp.Rational(906, 961)
    assert sp.factor(tracefree[1, 1] / stress[1, 1]) == sp.Rational(798, 403)
    test = data["exact_background_test"]
    assert test["stress_proportionality_minor_00_11"] == str(minor)
    assert test["first_failed_map"] == "background incidence Sol_Einstein-matter -> Sol_Weyl-matter"

    source = data["source_condition_disposition"]
    assert source["Q_T_status"] == "NOT_APPLICABLE"
    assert "Q_diag=0" in source["diagonal_gauge_charge"]
    assert "961/1920" in source["positive_stress_witness"]
    flags = data["claim_flags"]
    assert flags["counterflow_action_transport_certified"] is True
    assert flags["same_background_einstein_incidence"] is False
    assert flags["same_background_linear_inclusion"] is False
    assert flags["fixed_and_unrestricted_charge_sectors_separated"] is True
    assert flags["diagonal_neutrality_used_as_stress_vanishing"] is False
    assert flags["flat_Q_operator_transplanted_to_Berger"] is False

    assert data["charge_sector_split"]["unrestricted_Q_rel"]["D"].startswith("charged global")
    assert "size-two zero Jordan block" in data["charge_sector_split"]["unrestricted_Q_rel"]["linear_health"]
    assert data["charge_sector_split"]["unrestricted_Q_rel"]["background_Q_rel"] == "9*pi^2*sqrt(10)/5"
    assert data["charge_sector_split"]["fixed_Q_rel"]["clock"].startswith("OBSTRUCTED")
    assert data["relative_triangle"]["inclusion_i"] == "NO_CERTIFIED_MAP"
    assert data["relative_triangle"]["additional_Weyl_quotient"] == "NO_CERTIFIED_MAP"
    assert data["second_order_disposition"]["Einstein_clock_Taub_source_test"].startswith("NOT_APPLICABLE")

    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    assert atlas["status_vocabulary"] == ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
    assert len(atlas["entries"]) == 2
    assert {entry["scope"]["charge_sector"] for entry in atlas["entries"]} == {
        "unrestricted Q_rel",
        "derived fixed-Q_rel leaf followed by R_rel quotient",
    }
    for entry in atlas["entries"]:
        assert entry["evidence"][0]["sha256"] == sha(CERT)
        assert entry["descriptions"]["nonlinear"] == "NOT_APPLICABLE"
        assert entry["mode_data"]["taub_maps"]["status"] == "NOT_APPLICABLE"


if __name__ == "__main__":
    verify()
    print("TWO_PHASE_COUNTERFLOW_EINSTEIN_SOURCE_CONDITION_INDEPENDENT: PASS")
    print("input hashes, Berger incidence separator, charge split, and fail-closed atlas: PASS")
