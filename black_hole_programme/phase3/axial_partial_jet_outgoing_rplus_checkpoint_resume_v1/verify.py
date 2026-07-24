#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    document = json.loads((HERE / "certificate.json").read_text())
    checkpoint = json.loads((HERE / "checkpoint.json").read_text())
    assert checkpoint["payload_sha256"] == canonical_sha256(checkpoint["payload"])
    assert document["checkpoint"]["sha256"] == sha256(HERE / "checkpoint.json")
    assert document["checkpoint"]["schema_sha256"] == sha256(
        HERE / "checkpoint.schema.json"
    )
    assert document["checkpoint"]["payload_sha256"] == checkpoint["payload_sha256"]
    payload = checkpoint["payload"]
    assert payload["radial_state"]["radius"] == "63/2"
    assert payload["radial_state"]["next_panel_center"] == "2015/64"
    assert payload["omega_model"]["generator"] == 7315
    assert payload["base"]["generator"] == payload["tangent"]["generator"] == 7315
    assert payload["base"]["rows"] == payload["tangent"]["rows"] == 4
    for item in document["imports"].values():
        assert sha256(ROOT / item["path"]) == item["sha256"]
    transport = document["transport"]
    for prefix in (
        "export_source",
        "export_compile_log",
        "export_run_log",
        "restart_source",
        "roundtrip_source",
        "roundtrip_compile_log",
        "roundtrip_run_log",
        "restart_compile_log",
        "restart_run_log",
    ):
        assert sha256(ROOT / transport[f"{prefix}_path"]) == transport[
            f"{prefix}_sha256"
        ]
    restart_source = (HERE / "restart_chunk.forge").read_text()
    assert "build_seed(" not in restart_source
    assert 'big("2015/64")' in restart_source
    if document["status"] == "RPLUS_CHECKPOINT_RESTART_SECOND_CHUNK_PASS":
        flags = document["claim_flags"]
        assert flags["restart_does_not_replay_from_r32"] is True
        assert flags["restart_matches_independent_reference_exactly"] is True
        assert flags["Rplus_reaches_r31"] is True
        assert flags["Rplus_reaches_r4"] is False
        assert transport["exact_serialized_checkpoint_roundtrip"] is True
        assert transport["exact_serialized_final_state_match"] is True
    else:
        assert document["status"] == "RPLUS_CHECKPOINT_RESUME_SHORTFALL"
        assert document["shortfall"] is not None
        assert document["claim_flags"]["checkpoint_roundtrip_is_bit_exact"] is True
        assert document["claim_flags"]["Rplus_reaches_r31"] is False
    assert document["claim_flags"]["T_plus_recovered"] is False
    print("PASS outgoing Rplus checkpoint/restart certificate")


if __name__ == "__main__":
    main()
