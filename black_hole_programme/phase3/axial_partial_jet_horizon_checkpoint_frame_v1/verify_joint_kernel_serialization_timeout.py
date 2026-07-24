#!/usr/bin/env python3
"""Verify the fail-closed joint-kernel serialization shortfall."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "joint-kernel-serialization-timeout-certificate.json"
RECEIPT = HERE / "joint-kernel-serialization-timeout-receipt.json"
SUCCESSOR = HERE / "correlated-affine-seed-successor-run.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cert = json.loads(CERT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    successor = json.loads(SUCCESSOR.read_text())
    for item in cert["evidence"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert len(receipt["invocations"]) == 2
    assert all(
        row["exit_code"] == 124
        and row["wall_cap_seconds"] < 60
        and row["status"] == "TIMEOUT_NOT_PASS"
        for row in receipt["invocations"]
    )
    assert cert["resume"]["model_content_sha256"] == successor[
        "successor_model"
    ]["content_sha256"]
    assert cert["resume"]["rho"] == successor["successor_model"]["rho"]
    assert not any(cert["claim_flags"].values())
    assert "generator entry" in cert["required_split"]["unit"]
    print(
        "joint-kernel serialization shortfall verifier: PASS "
        "(two bounded timeouts; exact resume retained; all claims closed)"
    )


if __name__ == "__main__":
    main()
