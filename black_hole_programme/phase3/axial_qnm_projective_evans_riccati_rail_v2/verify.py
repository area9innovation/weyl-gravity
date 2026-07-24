#!/usr/bin/env python3
"""Independent verifier for the two-sided projective successor."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb

from .rail_v2 import RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERT.read_text())
    recorded = json.loads(RUN.read_text())
    assert compute() == recorded
    assert recorded["passed"]
    horizon = recorded["horizon"]
    assert horizon["passed"]
    assert horizon["chart_gate"]["pivot_excludes_zero"]
    assert arb(horizon["chart_gate"]["pivot_modulus_lower"]).lower() > 0
    assert horizon["initial_state"]["post_normalization_finite"]
    assert horizon["transport"]["post_normalization_finite"]
    assert horizon["transport"]["reference_gate"]["failure"] is None
    assert horizon["transport"]["remainder_gate"]["failure"] is None
    gates = recorded["interface_gates"]
    assert all(gates.values())
    match = recorded["common_match"]
    assert match["passed"]
    assert match["match_radius"] == 32
    assert match["mismatch"]["excludes_zero"]
    assert arb(match["mismatch"]["modulus_lower"]).lower() > 0
    assert match["omega_sensitivity"]["equals_affine_slope"]
    assert certificate["run"]["sha256"] == sha(RUN)
    for imported in certificate["imports"].values():
        assert sha(ROOT / imported["path"]) == imported["sha256"]
    flags = certificate["claim_flags"]
    assert flags["panel0_two_sided_projective_mismatch_certified"]
    assert not flags["full_contour_boundary_nonvanishing_certified"]
    assert not flags["QNM_root_count_certified"]
    assert not flags["QNM_or_EP2_certified"]
    print(
        "projective Evans/Riccati v2 verifier: PASS "
        "(horizon step and typed panel-0 mismatch certified)"
    )


if __name__ == "__main__":
    main()
