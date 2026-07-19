#!/usr/bin/env python3
"""Verify the Berger generic direct-shell and tail-stop certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE.json"
SCHEMA = PACKAGE / "schema/berger-recoil-direct-shell-and-tail-stop-gate-v1.schema.json"


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in value["dependency_refs"].values():
        path = ROOT / ref["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
            raise SystemExit(f"dependency hash drift: {ref['path']}")
    for ref in value["provenance"]["source_manifest"]:
        path = ROOT / ref["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
            raise SystemExit(f"source hash drift: {ref['path']}")
    provider = value["direct_shell_provider"]
    if set(provider["contiguous_carrier_cutoffs"].values()) != {6}:
        raise SystemExit("direct carrier cutoff is not uniformly two_j=6")
    if provider["hashed_exact_T_two_j138_stream_identification_status"] != "NO_CERTIFIED_MAP":
        raise SystemExit("exact-T carrier boundary was lost")
    gate = value["four_stream_stop_gate"]
    if gate["certificate_derived_open_fixture"]["stop"]:
        raise SystemExit("certificate-derived validation fixture must remain open")
    if not gate["synthetic_rank_two_stop_fixture"]["stop"]:
        raise SystemExit("synthetic rank-two stop fixture failed")
    print("BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
