#!/usr/bin/env python3
"""Independent fail-closed verifier for the mixed fixed-GL pivot repair."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cert = json.loads((HERE / "pivot-switch-certificate.json").read_text())
    schema = json.loads((HERE / "pivot-switch-schema.json").read_text())
    Draft202012Validator(schema).validate(cert)
    require(cert["status"] == "ONE_POST_SWITCH_CHECKPOINT_CERTIFIED", "status")
    flags = cert["claim_flags"]
    for name in (
        "former_pivot_obstruction_reproduced",
        "fixed_gl_chart_certified",
        "common_dual_correlation_preserved",
        "one_post_switch_panel_certified",
    ):
        require(flags[name] is True, name)
    for name in ("r4_reached", "H4_certified", "T_plus_certified"):
        require(flags[name] is False, name)
    switch = cert["method"]["fixed_chart"]
    require(switch["determinant"] == "1", "chart determinant")
    require(switch["selected_row"] == "e2-e3", "selected row")
    require(switch["pivot"]["exact_base_pivot"] == "1", "exact base pivot")
    require(switch["pivot"]["exact_tangent_pivot"] == "0", "exact tangent pivot")
    require(cert["checkpoint"]["accepted_post_switch_panels"] == 1, "panel count")
    require(cert["checkpoint"]["pivot"]["passed"] is True, "post pivot")
    for item in cert["imports"].values():
        path = ROOT / item["path"]
        require(path.exists(), f"missing import {path}")
        require(sha256(path) == item["sha256"], f"hash drift {path}")
    run = ROOT / cert["run"]["path"]
    require(sha256(run) == cert["run"]["sha256"], "run hash")
    print("PASS independent horizon mixed pivot-switch verifier")


if __name__ == "__main__":
    main()
