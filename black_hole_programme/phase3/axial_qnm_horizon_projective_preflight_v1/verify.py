#!/usr/bin/env python3
"""Verify the QNM-band horizon projective preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"
RUN = HERE / "horizon-run.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    run = json.loads(RUN.read_text())
    assert certificate["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "REDUCED-MODE"
    ]
    assert certificate["transport"]["run_artifact"]["sha256"] == sha256(RUN)
    assert run["dot_lambda_H"] == "0"
    assert all(
        row["coefficient_majorant_seed_gate"] for row in run["rows"]
    )
    assert not any(row["reached_r32"] for row in run["rows"])
    assert all(
        row["terminal"]["failure"] == "REFERENCE_Q_MAJORANT_DISCRIMINANT"
        for row in run["rows"]
    )
    flags = certificate["claim_flags"]
    assert flags["qnm_band_horizon_moving_phase_seed_certified"]
    assert not flags["horizon_projective_line_at_r32_certified"]
    assert not flags["projective_mismatch_at_r32_computed"]
    assert not flags["QNM_or_EP2_certified"]
    print("QNM-band horizon projective preflight: expected refusal verified")


if __name__ == "__main__":
    main()
