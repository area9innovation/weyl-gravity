#!/usr/bin/env python3
"""Independent lifecycle and claim-map verifier for the Phase 1 synthesis."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1.json"
Q = P / "certificates/PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1_PAYLOAD.json"
S = P / "schema/phase1-relational-observable-disposition-synthesis-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(cert: dict[str, Any], payload: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(S.read_text())).validate(cert)
    assert [row["layer"] for row in payload["claim_crosswalk"]] == [
        "conditional_or_kinematic_frequency_ratio_fixtures",
        "local_BV_receiver_cocycle",
        "ambient_action_integration",
        "residual_nonradical_physical_descent",
        "operational_relational_observable",
    ]
    assert [row["status"] for row in payload["claim_crosswalk"]] == [
        "CERTIFIED", "CERTIFIED", "OBSTRUCTED", "NO_CERTIFIED_MAP", "NO_CERTIFIED_MAP"
    ]
    assert payload["claim_crosswalk"][4]["domain"] == []
    assert payload["claim_crosswalk"][4]["coordinate_ratio_promoted"] is False
    assert payload["claim_crosswalk"][4]["redshift"] == "NO_CERTIFIED_MAP"
    assert "observable" in payload["claim_crosswalk"][1]["does_not_establish"]
    instances = payload["claim_crosswalk"][0]["carrier_instances"]
    assert len(instances) == 6
    assert len({row["id"] for row in instances}) == len(instances)
    assert all(row["status"] == "CERTIFIED" for row in instances)
    assert all("no cross_carrier name matching" in row["scope"]["charge_sector"] for row in instances[1:5])
    assert payload["phase1_freeze"]["new_receiver_architecture_opened"] is False
    assert payload["phase1_freeze"]["suspension_bridge_constructed"] is False
    assert all(value == "REJECT" for value in payload["mutation_expectations"].values())
    assert payload["generator_and_charge_dispositions"]["D"] != payload["generator_and_charge_dispositions"]["K"]
    assert all(payload["exact_checks"].values())


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(Q.read_text())
    assert sha(Q) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    verify(cert, payload)
    print("PHASE1_RELATIONAL_OBSERVABLE_DISPOSITION_SYNTHESIS_V1 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
