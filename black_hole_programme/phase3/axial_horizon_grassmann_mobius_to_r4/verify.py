#!/usr/bin/env python3
"""Independent fail-closed verifier for the frozen first-order shortfall."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify(root: Path = HERE) -> dict:
    cert = json.loads((root / "certificate.json").read_text())
    metadata = json.loads((root / "source_metadata.json").read_text())
    log = (root / "sentinel_q00.log").read_text()
    source = (root / "transport_c00.forge").read_text()

    require(cert["status"] == "METHOD_SHORTFALL", "wrong disposition")
    require(cert["claim_certified"] is False, "shortfall promoted to claim")
    require((root / "sentinel_q00.exit").read_text().strip() == "3",
            "sentinel did not return the declared refusal code")
    for relative, expected in cert["sha256"].items():
        require(digest(root / relative) == expected, f"hash drift: {relative}")

    require(metadata["attempted_indices"] == [0], "non-sentinel cells advertised")
    require(metadata["panels_per_shell"] == 256, "radial policy drift")
    require(len(metadata["charts"]) == 20, "chart atlas incomplete")
    require(metadata["source_sha256"] == {
        "transport_c00.forge": digest(root / "transport_c00.forge")
    }, "source metadata mismatch")

    required_log = [
        "SHELL q=0 shell=0 chart=11 rank=6",
        "SHELL q=0 shell=1 chart=11 rank=6",
        "HEARTBEAT q=0 shell=2 panel=256 chart=11",
        "REFUSE amplitude-rank q=0 shell=2",
        "AMPLITUDE_CENTER_RANK 6",
    ]
    for marker in required_log:
        require(marker in log, f"missing terminal evidence: {marker}")
    require("PASS q=0" not in log, "shortfall log contains PASS")
    require(len(re.findall(r"^AC [0-5] [0-5] ", log, re.MULTILINE)) == 36,
            "incomplete exact amplitude centre")

    required_source = [
        "while(shell<23)",
        "while(panel<256)",
        "while(c<20)",
        "ivam_full_column_rank_cells(state.amplitude,64)",
        "ivam_mul_checked(s.amplitude,hr_gauge())",
        "if(hr_norm(state.z)>=1.5)",
        "REFUSE amplitude-rank",
    ]
    for marker in required_source:
        require(marker in source, f"missing source invariant: {marker}")
    forbidden_source = [
        "while(panel<512)",
        "while(panel<1024)",
        "ivam_mul_checked(hr_gauge(),s.amplitude)",
    ]
    for marker in forbidden_source:
        require(marker not in source, f"forbidden mutation present: {marker}")

    stale = sorted(
        p.name for p in root.glob("transport_c*.forge")
        if p.name != "transport_c00.forge"
    )
    require(not stale, f"unevaluated child artifacts present: {stale}")
    return {
        "verified": True,
        "status": "METHOD_SHORTFALL",
        "terminal_shell": 2,
        "terminal_gate": "amplitude full-column rank over frequency cell",
        "claim_certified": False,
    }


if __name__ == "__main__":
    try:
        print(json.dumps(verify(), sort_keys=True))
    except Exception as exc:
        print(f"REFUSE {exc}", file=sys.stderr)
        raise SystemExit(1)
