#!/usr/bin/env python3
"""Independent audit of the temporal-curl all-jet SHORTFALL boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = (
    P / "certificates/BERGER_TEMPORAL_CURL_ALL_JET_DISPOSITION_SHORTFALL.json"
)
SCHEMA = (
    P
    / "schema/berger-temporal-curl-all-jet-disposition-shortfall-v1.schema.json"
)
REQUEST = (
    ROOT
    / "planning/forge-requests/observer-differential-pbw-module-membership.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)

    for ref in value["dependency_refs"].values():
        path = ROOT / ref["path"]
        assert path.exists()
        assert sha256(path) == ref["sha256"]

    predecessor = json.loads(
        (
            P
            / "certificates/BERGER_TEMPORAL_MAXWELL_COTANGENT_MAPPING_CONE_CONSTRUCTION.json"
        ).read_text()
    )
    for audit in predecessor["filtered_second_jet_theorem"][
        "per_emitter_audits"
    ].values():
        assert audit["full_action_image_rank"] == 2641
        assert audit["source_augmented_rank"] == 2642
        assert audit["source_outside_image"] is True

    request = json.loads(REQUEST.read_text())
    assert request["schema"] == "work-v0"
    assert request["id"] == (
        "sf:forge-request/observer-differential-pbw-module-membership"
    )
    assert request["body"]["state"] in {"REQUESTED", "ACCEPTED"}
    for term in (
        "Q(sqrt(10))",
        "syzygies",
        "filtered lift",
        "independent verifier",
    ):
        assert term in request["body"]["stop_condition"]

    audit = value["capability_audit"]
    assert audit["audit_verdict"] == "MISSING_REQUIRED_EXACT_MODULE_MACHINERY"
    assert "syzygies" in " ".join(audit["missing_required_layers"])
    assert value["all_jet_disposition"]["status"] == "SHORTFALL"
    assert all(
        field == "NO_CERTIFIED_MAP"
        for key, field in value["all_jet_disposition"].items()
        if key not in {"declared_module", "status"}
    )
    assert all(
        field == "NO_CERTIFIED_MAP"
        for field in value["downstream_disposition"].values()
    )
    assert value["controls"]["blind_third_jet"] == (
        "NOT_RUN_FORBIDDEN_BY_WORK_ITEM"
    )
    assert "not an all-jet obstruction theorem" in value[
        "claim_boundary"
    ]
    print(
        "BERGER_TEMPORAL_CURL_ALL_JET_DISPOSITION_SHORTFALL "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
