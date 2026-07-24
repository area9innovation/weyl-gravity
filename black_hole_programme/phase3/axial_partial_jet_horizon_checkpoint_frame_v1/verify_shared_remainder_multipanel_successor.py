#!/usr/bin/env python3
"""Independent verifier for the content-addressed multipanel successor."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from . import shared_remainder_multipanel_successor as successor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cert = json.loads(
        (HERE / "shared-remainder-multipanel-successor-certificate.json").read_text()
    )
    schema = json.loads(
        (HERE / "shared-remainder-multipanel-successor-schema.json").read_text()
    )
    Draft202012Validator(schema).validate(cert)
    require(
        cert["status"] == "NINE_SUBSTEPS_CONTENT_ADDRESSED_PIVOT_SHORTFALL",
        "status",
    )
    progress = cert["progress"]
    require(progress["accepted_substeps"] == 9, "accepted substeps")
    require(len(progress["checkpoint_chain"]) == 9, "checkpoint count")
    require(len(progress["gate_ledger"]) == 9, "gate count")
    parent = cert["source"]["sha256"]
    generator = cert["controls"]["generator_sha256"]
    for index, checkpoint in enumerate(progress["checkpoint_chain"]):
        require(checkpoint["substep_index"] == index, "checkpoint index")
        require(checkpoint["parent_sha256"] == parent, "parent hash")
        require(checkpoint["generator_sha256"] == generator, "generator hash")
        payload = {
            key: value
            for key, value in checkpoint.items()
            if key != "content_sha256"
        }
        require(
            successor.canonical_hash(payload) == checkpoint["content_sha256"],
            "content hash",
        )
        require(
            checkpoint["normalization"]["exact_base_pivot"] == "1",
            "base pivot",
        )
        require(
            checkpoint["normalization"]["exact_tangent_pivot"] == "0",
            "tangent pivot",
        )
        parent = checkpoint["content_sha256"]
    require(
        all(row["post_normalization_finite"] for row in progress["gate_ledger"]),
        "post-normalization finiteness",
    )
    obstruction = cert["obstruction"]
    require(obstruction["gate"] == "FIXED_ATLAS_PIVOT_OBSTRUCTION", "gate")
    require(obstruction["selected"] is None, "selected chart")
    require(
        all(value == "0" for value in obstruction["atlas_modulus_lowers"].values()),
        "atlas lower bounds",
    )
    flags = cert["claim_flags"]
    require(flags["all_accepted_checkpoints_content_addressed"], "hash flag")
    require(flags["first_obstruction_fail_closed"], "refusal flag")
    require(not flags["next_base_panel_completed"], "base-panel overclaim")
    require(not flags["r4_reached"], "r4 overclaim")
    for item in cert["imports"].values():
        path = ROOT / item["path"]
        require(path.exists(), f"missing import {path}")
        require(sha256(path) == item["sha256"], f"hash drift {path}")
    run = ROOT / cert["run"]["path"]
    require(sha256(run) == cert["run"]["sha256"], "run hash")
    print("PASS independent shared-remainder multipanel verifier")


if __name__ == "__main__":
    main()
