#!/usr/bin/env python3
"""Independent audit of the missing same-background Berger Z2 receiver."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_APPARATUS_Z2_MEMORY_RESPONSE_CROSSWALK.json"
X = P / "certificates/BERGER_APPARATUS_SAME_BACKGROUND_Z2_RECEIVER_CONTRACT.json"
SCHEMA = (
    P
    / "schema/berger-apparatus-z2-memory-response-crosswalk-v1.schema.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, contract = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(X) == cert["contract_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]
    assert sha(ROOT / cert["request_ref"]["path"]) == cert["request_ref"]["sha256"]

    payload = json.loads(
        (P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json").read_text()
    )
    keys = {
        "preparation_carrier_crosswalk": "preparation_carrier_crosswalk",
        "quadratic_source_map_on_preparation_span": (
            "quadratic_source_map_on_preparation_span"
        ),
        "stabilizer_basis": "stabilizer_basis",
        "moment_map_or_Taub_projections": "moment_map_or_Taub_projections",
        "nonzero_shell_output_blocks": "nonzero_shell_output_blocks",
        "reduced_adjoint_cokernel_bases": "reduced_adjoint_cokernel_bases",
        "resonant_adjoint_pairings": "resonant_adjoint_pairings",
        "correction_class_receivers": "correction_class_receivers",
        "Berger_Z2_ideal": "Berger_Z2_ideal",
        "memory_transport_on_Z2": "memory_transport_on_Z2",
    }
    independent_absence = {name: key not in payload for name, key in keys.items()}
    assert independent_absence == contract["current_absence_audit"]
    assert all(independent_absence.values())

    assert contract["input_span"]["required_quadratic_pairs"] == [
        "(u_0,u_0)",
        "(u_0,u_1)",
        "(u_1,u_1)",
    ]
    assert set(contract["correction_classes"]) == {
        "bounded_or_quasiperiodic",
        "smooth_secular",
        "causal_or_retarded",
    }
    assert all(
        row["current_status"] == "NO_CERTIFIED_MAP"
        for row in contract["correction_classes"].values()
    )
    assert all(
        value == "NO_CERTIFIED_MAP"
        for key, value in cert["observer_disposition"].items()
        if key != "leading_linear_response_rank"
    )
    assert cert["observer_disposition"]["leading_linear_response_rank"] == (
        "CERTIFIED_RANK_TWO_IN_PARENT_SCOPE_ONLY"
    )
    assert cert["capability_audit"]["verdict"] == (
        "TYPED_SAME_BACKGROUND_RECEIVER_REQUIRED"
    )
    assert "not promoted to a nonlinear response" in cert["claim_boundary"]
    print(
        "BERGER_APPARATUS_Z2_MEMORY_RESPONSE_CROSSWALK "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
