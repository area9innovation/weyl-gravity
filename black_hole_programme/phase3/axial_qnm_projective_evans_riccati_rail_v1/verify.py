#!/usr/bin/env python3
"""Independent verifier for the one-panel projective Riccati rail."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb

from .rail import RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERT.read_text())
    recorded = json.loads(RUN.read_text())
    reproduced = compute()
    assert reproduced == recorded
    assert recorded["passed"]
    assert recorded["chart_gate"]["pivot_excludes_zero"]
    assert arb(recorded["chart_gate"]["pivot_modulus_lower"]).lower() > 0
    assert recorded["chart_gate"]["analytic_chart_through_step"]
    assert recorded["transport"]["from_r"] == "45"
    assert recorded["transport"]["to_r"] == "899/20"
    assert recorded["transport"]["reference_gate"]["failure"] is None
    assert recorded["transport"]["remainder_gate"]["failure"] is None
    assert recorded["scope"]["radial_panel_count"] == 1
    assert not recorded["scope"]["two_sided"]
    assert certificate["run"]["sha256"] == sha(RUN)
    for imported in certificate["imports"].values():
        assert sha(ROOT / imported["path"]) == imported["sha256"]
    flags = certificate["claim_flags"]
    assert flags["typed_projective_chart_certified"]
    assert flags["joint_q_qtau_qomega_one_panel_transport_certified"]
    assert not flags["two_sided_projective_mismatch_certified_here"]
    assert not flags["QNM_root_count_certified"]
    assert not flags["QNM_or_EP2_certified"]
    print(
        "projective Evans/Riccati rail verifier: PASS "
        "(outgoing pivot and one correlated radial step certified)"
    )


if __name__ == "__main__":
    main()
