#!/usr/bin/env python3
"""Independent verifier for the panel-77 self-map repair artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb

from .repair import RUN

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def by_label(run: dict, label: str) -> dict:
    return next(
        row for row in run["diagnostic_grid"] if row["label"] == label
    )


def main() -> None:
    certificate = json.loads(CERT.read_text())
    run = json.loads(RUN.read_text())
    assert run["panel"] == 77
    box = by_label(run, "box_baseline")
    baseline = by_label(run, "center_baseline")
    precision = by_label(run, "center_higher_precision")
    order = by_label(run, "center_higher_seed_and_taylor_order")
    stable = by_label(run, "center_stable_interval_root")
    assert box["self_map_passed"]
    assert not baseline["self_map_passed"]
    assert not precision["self_map_passed"]
    assert not order["self_map_passed"]
    assert baseline["failure"] == "HORIZON_Q_REMAINDER_SELF_MAP"
    assert stable["self_map_passed"]
    assert stable["failure"] is None
    assert arb(stable["strict_margin"]).lower() > 0
    assert arb(stable["candidate"]).lower() > arb(
        stable["self_map_rhs"]
    ).upper()
    assert all(
        pivot["pivot_excludes_zero"]
        and arb(pivot["q_modulus_lower"]).lower() > 0
        for pivot in run["reciprocal_chart"]
    )
    assert not run["repair"]["threshold_lowered"]
    assert run["repair"]["strict_self_map_rechecked"]
    panel = run["repaired_panel"]
    assert panel["panel"] == 77
    assert panel["boundary_nonvanishing"]["status"] == "PASS"
    assert arb(
        panel["physical_mismatch"]["modulus_lower"]
    ).lower() > 0
    assert certificate["run"]["sha256"] == sha(RUN)
    for imported in certificate["imports"].values():
        assert sha(ROOT / imported["path"]) == imported["sha256"]
    assert certificate["imports"]["common_affine_source"]["sha256"] == (
        "8ae5c434f7fe3757b79b6cafddd71057cf67d5fb31e1b7ac16754fcbcb20bc5b"
    )
    assert certificate["claim_flags"][
        "panel_77_horizon_center_self_map_repaired"
    ]
    assert not certificate["claim_flags"]["threshold_lowered"]
    assert not certificate["claim_flags"]["QNM_or_EP2_certified"]
    print(
        "panel-77 horizon center self-map verifier: PASS "
        "(stable interval root; strict unchanged self-map; Delta nonzero)"
    )


if __name__ == "__main__":
    main()
