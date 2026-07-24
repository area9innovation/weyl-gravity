#!/usr/bin/env python3
"""Fail-closed verifier for the two-sided mismatch preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cert = json.loads((HERE / "certificate.json").read_text())
    run = json.loads((HERE / "mismatch-run.json").read_text())
    assert cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert cert["run"]["sha256"] == sha(HERE / "mismatch-run.json")
    assert len(run["rows"]) == 16
    passed = sum(row["delta"]["excludes_zero"] for row in run["rows"])
    assert passed == run["gates"]["boundary_nonvanishing"]["passed_panel_count"]
    assert passed == 0
    assert all(
        row["dependency_scope"][
            "serialized_cross_endpoint_affine_generator_available"
        ] is False
        for row in run["rows"]
    )
    assert run["gates"]["boundary_nonvanishing"]["status"] == "FAIL_CLOSED"
    assert run["gates"]["argument_principle_root_count"]["status"] == "NOT_RUN"
    assert run["gates"]["K0_or_interval_newton_defect"]["status"] == "NOT_RUN"
    assert not cert["claim_flags"]["boundary_nonvanishing_certified"]
    assert not cert["claim_flags"]["QNM_or_EP2_certified"]
    print("PASS")


if __name__ == "__main__":
    main()
