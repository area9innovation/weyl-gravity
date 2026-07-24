#!/usr/bin/env python3
"""Independent verifier for the outgoing S+ r=31 continuation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from .produce import canonical_sha256


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(data: dict) -> None:
    jsonschema.validate(data, json.loads((HERE / "schema.json").read_text()))
    if data["status"] != "SPLUS_REACHES_R31":
        raise RuntimeError("S+ did not reach r=31")
    for item in data["imports"].values():
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError("import hash drift")
    progress = data["progress"]
    if sha256(ROOT / progress["path"]) != progress["sha256"]:
        raise RuntimeError("progress hash drift")
    checkpoint_path = ROOT / data["checkpoint"]["path"]
    checkpoint = json.loads(checkpoint_path.read_text())
    if sha256(checkpoint_path) != data["checkpoint"]["sha256"]:
        raise RuntimeError("checkpoint hash drift")
    if canonical_sha256(checkpoint["payload"]) != checkpoint["payload_sha256"]:
        raise RuntimeError("checkpoint payload hash drift")
    if checkpoint["payload"]["radius"] != "31":
        raise RuntimeError("checkpoint radius drift")
    chunks = data["transport"]["chunks"]
    if len(chunks) != 6 or data["transport"]["completed_panels"] != 104:
        raise RuntimeError("chunk cover drift")
    expected = (
        (0, "32", "8079/256"),
        (1, "16", "8047/256"),
        (2, "16", "8015/256"),
        (3, "16", "7983/256"),
        (4, "16", "7951/256"),
        (5, "8", "31"),
    )
    for chunk, (chunk_id, panels, final_r) in zip(chunks, expected):
        summary = chunk["summary"]
        if not chunk["passed"]:
            raise RuntimeError("chunk did not pass")
        for name in ("source", "compile_log", "run_log"):
            item = chunk[name]
            if sha256(ROOT / item["path"]) != item["sha256"]:
                raise RuntimeError(f"chunk {chunk_id} artifact drift: {name}")
        for key, value in {
            "status": "PASS",
            "generator": "7315",
            "panels": panels,
            "final_r": final_r,
        }.items():
            if summary.get(key) != value:
                raise RuntimeError(f"chunk {chunk_id} summary drift: {key}")
    flags = data["claim_flags"]
    if not (
        flags["common_generator_preserved"]
        and flags["S_reaches_r31"]
        and flags["S_checkpoint_serialized"]
    ):
        raise RuntimeError("positive claim missing")
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
    print("PASS independent outgoing S+ r31 verifier")


if __name__ == "__main__":
    main()
