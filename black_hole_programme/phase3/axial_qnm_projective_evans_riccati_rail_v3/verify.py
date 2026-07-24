#!/usr/bin/env python3
"""Independent verifier for the bounded multi-panel successor."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb

from .rail_v3 import RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERT.read_text())
    recorded = json.loads(RUN.read_text())
    assert compute() == recorded
    assert recorded["status"] == (
        "BOUNDED_PROGRESS_FAIL_CLOSED_BEFORE_LOCAL_QNM_TEST"
    )
    assert len(recorded["rows"]) == 16
    assert recorded["summary"]["completed_panel_count"] == 16
    assert recorded["summary"]["full_contour_panel_count"] == 512
    assert recorded["summary"]["two_sided_co_location_passed"]
    assert recorded["summary"]["all_completed_deltas_exclude_zero"]
    assert recorded["summary"]["delta_tau_excludes_zero_panel_count"] == 0
    assert recorded["summary"]["delta_omega_excludes_zero_panel_count"] == 0
    for panel, row in enumerate(recorded["rows"]):
        assert row["panel"] == panel
        assert all(row["interface_gates"].values())
        assert row["delta"]["excludes_zero"]
        assert arb(row["delta"]["modulus_lower"]).lower() > 0
        assert not row["delta_tau"]["excludes_zero"]
        assert not row["delta_omega"]["excludes_zero"]
        assert row["delta_omega"]["equals_affine_slope"]
    obstruction = recorded["local_qnm_gate"]["first_obstruction"]
    assert obstruction["code"] == "INCOMPLETE_CLOSED_BOUNDARY_COVERAGE"
    assert obstruction["first_missing_panel"] == 16
    assert not recorded["local_qnm_gate"]["interval_newton_run"]
    assert not recorded["local_qnm_gate"]["argument_principle_run"]
    assert certificate["run"]["sha256"] == sha(RUN)
    for imported in certificate["imports"].values():
        assert sha(ROOT / imported["path"]) == imported["sha256"]
    flags = certificate["claim_flags"]
    assert flags["panels_0_through_15_typed_two_sided_at_r32"]
    assert flags["panels_0_through_15_delta_nonzero"]
    assert not flags["delta_tau_nonzero_certified"]
    assert not flags["delta_omega_nonzero_certified"]
    assert not flags["interval_newton_certified"]
    assert not flags["QNM_or_EP2_certified"]
    print(
        "projective Evans/Riccati v3 verifier: PASS "
        "(16 typed panels; local-QNM gate fails closed at panel 16)"
    )


if __name__ == "__main__":
    main()
