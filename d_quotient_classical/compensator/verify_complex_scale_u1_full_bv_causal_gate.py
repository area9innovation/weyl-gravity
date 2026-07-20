#!/usr/bin/env python3
"""Independent replay of the separated scale/U1 non-activation gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_COMPLEX_SCALE_U1_FULL_BV_CAUSAL_GATE_V1.json"
)


def verify() -> None:
    payload = json.loads(RESULT.read_text())
    predecessor = payload["predecessor"]
    actual = hashlib.sha256((ROOT / predecessor["path"]).read_bytes()).hexdigest()
    if (
        actual != predecessor["sha256"]
        or actual
        != "3b7b1f86392f0d5daeec4b1adac99a0e16e472ff37b44253908a20c53aad1404"
        or predecessor["healthy_locus"] != "EMPTY"
        or predecessor["selected_action"]
    ):
        raise AssertionError("predecessor replay failed")
    if (
        payload["activation_condition_satisfied"]
        or payload["terminal_verdict"]["full_gate_activated"]
        or payload["terminal_verdict"]["causal_parent_constructed"]
        or any(payload["claim_flags"].values())
    ):
        raise AssertionError("forbidden conditional activation detected")
    if set(item["status"] for item in payload["skipped_gates"].values()) != {
        "NOT_ACTIVATED"
    }:
        raise AssertionError("skip status promoted")
    print(
        "COMPENSATOR_COMPLEX_SCALE_U1_FULL_BV_CAUSAL_GATE_V1 "
        "independent activation replay: PASS"
    )


if __name__ == "__main__":
    verify()
