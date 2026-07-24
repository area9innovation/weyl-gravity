#!/usr/bin/env python3
"""Independent verifier for the panels 0--97 aggregate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb

from .aggregate import RUN, compute

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERT.read_text())
    recorded = json.loads(RUN.read_text())
    assert compute() == recorded
    summary = recorded["summary"]
    assert summary["contiguous_prefix"]
    assert summary["completed_panel_count"] == 98
    assert summary["last_panel"] == 97
    assert summary["two_sided_interface_gates_pass"]
    assert summary["all_completed_deltas_exclude_zero"]
    assert len(recorded["rows"]) == 98
    for expected, row in enumerate(recorded["rows"]):
        assert row["panel"] == expected
        assert all(row["interface_gates"].values())
        assert row["delta"]["excludes_zero"]
        assert arb(row["delta"]["modulus_lower"]).lower() > 0
    gate = recorded["local_qnm_gate"]
    obstruction = gate["first_obstruction"]
    assert obstruction["first_missing_panel"] == 98
    assert obstruction["code"] == "COMMON_AFFINE_DELTA_ENCLOSURE_CONTAINS_ZERO"
    assert obstruction["terminal_observation"]["panel"] == 98
    assert not gate["interval_newton_run"]
    assert not gate["argument_principle_run"]
    assert certificate["run"]["sha256"] == sha(RUN)
    for imported in certificate["imports"].values():
        assert sha(ROOT / imported["path"]) == imported["sha256"]
    assert certificate["claim_flags"][
        "panels_0_through_97_typed_two_sided_at_r32"
    ]
    assert not certificate["claim_flags"][
        "panel_98_endpoint_export_certified"
    ]
    assert not certificate["claim_flags"]["QNM_or_EP2_certified"]
    print(
        "projective Evans/Riccati v10 verifier: PASS "
        "(contiguous typed prefix 0--97; terminal panel 98 "
        "COMMON_AFFINE_DELTA_ENCLOSURE_CONTAINS_ZERO)"
    )


if __name__ == "__main__":
    main()
