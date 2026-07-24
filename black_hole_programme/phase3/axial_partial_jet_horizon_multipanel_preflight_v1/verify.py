#!/usr/bin/env python3
"""Independent verifier for the regular partial-jet multipanel refusal."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    doc = json.loads(CERTIFICATE.read_text())
    if doc["status"] != "CERTIFIED_MULTIPANEL_REGULAR_PARTIAL_JET_SHORTFALL":
        raise RuntimeError("status drift")
    for item in doc["imports"].values():
        path = ROOT / item["path"]
        if sha256(path) != item["sha256"]:
            raise RuntimeError(f"import hash drift: {path}")

    attempt = doc["attempt"]
    for name in ("source", "compile_log", "run_log"):
        path = ROOT / attempt[f"{name}_path"]
        if sha256(path) != attempt[f"{name}_sha256"]:
            raise RuntimeError(f"{name} hash drift")
    if attempt["compile_exit"] != 0 or attempt["run_exit"] != 3:
        raise RuntimeError("unexpected process exits")
    if (ROOT / attempt["compile_log_path"]).read_text():
        raise RuntimeError("compiler emitted diagnostics")

    output = (ROOT / attempt["run_log_path"]).read_text()
    shell_pattern = re.compile(
        r"MULTIPANEL_SHELL shell=(\d+) rho=([-+0-9.eE]+) "
        r"width=([-+0-9.eE]+) direct_width=([-+0-9.eE]+)"
    )
    raw_shells = shell_pattern.findall(output)
    parsed_shells = attempt["parsed"]["shell_records"]
    if len(raw_shells) != 6 or len(parsed_shells) != 6:
        raise RuntimeError("unexpected completed-shell count")
    previous_width = 0.0
    for index, (shell, rho, width, direct_width) in enumerate(raw_shells):
        if int(shell) != index:
            raise RuntimeError("nonconsecutive shell record")
        expected_rho = 2.0 ** (index - 21)
        if float(rho) != expected_rho:
            raise RuntimeError("geometric shell endpoint drift")
        width_value = float(width)
        direct_value = float(direct_width)
        if not (
            math.isfinite(width_value)
            and math.isfinite(direct_value)
            and width_value > previous_width
            and abs(width_value - direct_value)
            <= 1e-12 * max(1.0, width_value, direct_value)
        ):
            raise RuntimeError("direct/jet shell-width control failed")
        previous_width = width_value

    refusal_pattern = re.compile(
        r"MULTIPANEL_REFUSAL gate=state_width shell=6 panel=3 "
        r"total_panels=27 width=([-+0-9.eE]+) overlap=true "
        r"scaled=([-+0-9.eE]+) tail=([-+0-9.eE]+)"
    )
    match = refusal_pattern.search(output)
    if match is None:
        raise RuntimeError("exact refusal record missing")
    width, scaled, tail = map(float, match.groups())
    if not (
        width > doc["scope"]["width_refusal_threshold"]
        and 0.9 < scaled < 0.91
        and 0.0 < tail < 1e-26
    ):
        raise RuntimeError("refusal diagnostics drift")
    refusal = attempt["parsed"]["refusal"]
    if (
        attempt["parsed"]["status"] != "REFUSED"
        or refusal["gate"] != "state_width"
        or refusal["shell"] != 6
        or refusal["panel"] != 3
    ):
        raise RuntimeError("parsed refusal drift")
    details = refusal["details"]
    if not (
        details["total_panels"] == 27
        and details["overlap"] is True
        and details["width"] == width
        and details["scaled"] == scaled
        and details["tail"] == tail
    ):
        raise RuntimeError("structured refusal details drift")

    flags = doc["claim_flags"]
    if any(flags.values()):
        raise RuntimeError("fail-closed claim flag promoted")
    if "K_H or a tau-analytic endpoint normalizer identification" not in (
        doc["does_not_establish"]
    ):
        raise RuntimeError("K_H boundary missing")
    print("PASS regular partial-jet multipanel shortfall")


if __name__ == "__main__":
    verify()
