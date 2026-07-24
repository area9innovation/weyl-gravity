#!/usr/bin/env python3
"""Verifier for the common-affine export shortfall."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cert = json.loads((HERE / "certificate.json").read_text())
    run = json.loads((HERE / "audit-run.json").read_text())
    assert cert["run"]["sha256"] == sha(HERE / "audit-run.json")
    assert cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert not run["current_artifacts"]["common_generator_available"]
    assert not run["current_artifacts"][
        "independent_residuals_after_polynomial_subtraction_available"
    ]
    witness = run["bounded_joint_rerun_attempt"]
    assert witness["omega_is_singleton"]
    assert witness["reference_step_passed"]
    assert not witness["remainder_step_passed"]
    assert witness["failure"] == "HORIZON_Q_REMAINDER_SELF_MAP"
    assert run["gates"]["boundary_nonvanishing"]["status"] == "NOT_RUN"
    assert not cert["claim_flags"]["QNM_or_EP2_certified"]
    print("PASS")


if __name__ == "__main__":
    main()
