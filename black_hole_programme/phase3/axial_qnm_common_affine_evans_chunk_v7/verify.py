#!/usr/bin/env python3
"""Independent verifier for stable-root panels 94--109."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb

from .chunk import PANEL_START, PANEL_STOP, RUN

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERT.read_text())
    run = json.loads(RUN.read_text())
    assert run["requested_panels"] == [PANEL_START, PANEL_STOP - 1]
    assert not run["threshold_lowered"]
    for offset, row in enumerate(run["rows"]):
        assert row["panel"] == PANEL_START + offset
        generator = row["omega_generator_id"]
        assert generator == row["horizon"]["omega_generator_id"]
        assert generator == row["outgoing"]["omega_generator_id"]
        if row["boundary_nonvanishing"]["status"] == "PASS":
            assert arb(
                row["physical_mismatch"]["modulus_lower"]
            ).lower() > 0
    if run["all_requested_panels_nonzero"]:
        assert len(run["rows"]) == PANEL_STOP - PANEL_START
        assert run["terminal"] is None
    else:
        assert run["terminal"] is not None
        assert run["rows"][-1]["panel"] == run["terminal"]["panel"]
        assert run["rows"][-1]["boundary_nonvanishing"]["status"] != "PASS"
    assert certificate["run"]["sha256"] == sha(RUN)
    for item in certificate["imports"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert certificate["claim_flags"]["stable_root_repair_applied"]
    assert not certificate["claim_flags"]["threshold_lowered"]
    assert not certificate["claim_flags"]["QNM_or_EP2_certified"]
    print(
        "stable-root common-affine Evans panels 94--109 verifier: PASS "
        f"({run['completed_panel_count']} materialized rows; "
        f"terminal={run['terminal']})"
    )


if __name__ == "__main__":
    main()
