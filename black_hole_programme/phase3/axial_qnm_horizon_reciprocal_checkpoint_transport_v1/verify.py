#!/usr/bin/env python3
"""Fail-closed verifier for the reciprocal checkpoint artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cert = json.loads((HERE / "certificate.json").read_text())
    run = json.loads((HERE / "checkpoint-run.json").read_text())
    assert cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert cert["run"]["sha256"] == sha(HERE / "checkpoint-run.json")
    assert run["checkpoint_radii"] == [8, 16, 32]
    assert len(run["rows"]) == 16
    reached = 0
    recovered = 0
    for row in run["rows"]:
        assert [item["radius"] for item in row["checkpoints"]] in (
            [8], [8, 16], [8, 16, 32]
        )
        for checkpoint in row["checkpoints"]:
            recovered += int(
                checkpoint["q_recovery_denominator_excludes_zero"]
            )
            if checkpoint["q_recovery_denominator_excludes_zero"]:
                assert checkpoint["q_recovered"] is not None
        if row["reached_r32"]:
            reached += 1
            assert row["terminal"] is None
            assert len(row["checkpoints"]) == 3
        else:
            assert row["terminal"] is not None
    assert reached == cert["transport"]["reached_panel_count"]
    assert recovered == cert["transport"]["checkpoint_q_recovery_gate_count"]
    assert cert["claim_flags"]["all_panels_reached_r8_r16_r32"] == (reached == 16)
    assert (
        cert["claim_flags"]["base_horizon_projective_line_at_r32_certified"]
        == (reached == 16)
    )
    assert not cert["claim_flags"]["QNM_or_EP2_certified"]
    assert not cert["claim_flags"]["Evans_boundary_nonzero_certified"]
    assert not cert["claim_flags"]["outgoing_match_certified"]
    print("PASS")


if __name__ == "__main__":
    main()
