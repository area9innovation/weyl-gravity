#!/usr/bin/env python3
"""Independent replay of the two-field full-BV non-activation gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_TWO_FIELD_FULL_BV_CAUSAL_GATE_V1.json"
)
EXPECTED_PREDECESSOR_SHA = (
    "e597c687ae064ac6809b674c056aa08d0167a9184b6addb95b5b7330c33dcc62"
)


def verify() -> None:
    payload = json.loads(RESULT.read_text())
    predecessor = payload["predecessor"]
    source_path = ROOT / predecessor["path"]
    actual = hashlib.sha256(source_path.read_bytes()).hexdigest()
    source = json.loads(source_path.read_text())
    terminal = source["terminal_verdict"]
    if (
        actual != predecessor["sha256"]
        or actual != EXPECTED_PREDECESSOR_SHA
        or terminal["healthy_locus"] != "EMPTY"
        or terminal["selected_action"]
        or terminal["full_BV_or_causal_completion_activated"]
    ):
        raise AssertionError("predecessor replay failed")
    if (
        payload["activation_condition_satisfied"]
        or payload["terminal_verdict"]["full_gate_activated"]
        or payload["terminal_verdict"]["causal_parent_constructed"]
        or payload["terminal_verdict"]["relative_clock_constructed"]
        or any(payload["claim_flags"].values())
    ):
        raise AssertionError("forbidden conditional activation detected")
    if set(item["status"] for item in payload["skipped_gates"].values()) != {
        "NOT_ACTIVATED"
    }:
        raise AssertionError("skip status promoted")
    if "primitive rank one leaves one legitimate relative phase" not in (
        predecessor["compact_charge_lattice_result"]
    ):
        raise AssertionError("positive compact-lattice result was lost")
    print(
        "COMPENSATOR_TWO_FIELD_FULL_BV_CAUSAL_GATE_V1 "
        "independent activation replay: PASS"
    )


if __name__ == "__main__":
    verify()
