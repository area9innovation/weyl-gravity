#!/usr/bin/env python3
"""Independent verifier for the 16-panel outgoing S continuation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def verify(data: dict) -> None:
    jsonschema.validate(data, json.loads((HERE / "schema.json").read_text()))
    if data["status"] != "SPLUS_CORRELATED_16_PANEL_RESUME_PASS":
        raise RuntimeError("S continuation did not pass")
    for item in data["imports"].values():
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError("import hash drift")
    for name in ("source", "compile_log", "run_log"):
        item = data["artifacts"][name]
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError("artifact hash drift")
    checkpoint_path = ROOT / data["checkpoint"]["path"]
    checkpoint = json.loads(checkpoint_path.read_text())
    if sha256(checkpoint_path) != data["checkpoint"]["sha256"]:
        raise RuntimeError("checkpoint hash drift")
    if canonical_sha256(checkpoint["payload"]) != checkpoint["payload_sha256"]:
        raise RuntimeError("checkpoint payload hash drift")
    summary = data["transport"]["summary"]
    for key, value in {
        "status": "PASS",
        "generator": "7315",
        "panels": "16",
    }.items():
        if summary.get(key) != value:
            raise RuntimeError(f"summary drift: {key}")
    flags = data["claim_flags"]
    if not (
        flags["common_generator_preserved"]
        and flags["S_16_panel_resume_certified"]
        and flags["S_checkpoint_serialized"]
    ):
        raise RuntimeError("continuation claim missing")
    if any(
        flags[key]
        for key in (
            "joint_E_R_S_frame_certified",
            "K_plus_certified",
            "T_plus_certified",
            "scattering_or_flux_certified",
        )
    ):
        raise RuntimeError("downstream claim promoted")


def main() -> None:
    verify(json.loads((HERE / "certificate.json").read_text()))
    print("PASS independent outgoing S checkpoint-resume verification")


if __name__ == "__main__":
    main()
