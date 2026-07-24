#!/usr/bin/env python3
"""Independent materialized verifier for panels 16--31."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb

from .chunk import PANEL_START, PANEL_STOP, RUN

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERT.read_text())
    run = json.loads(RUN.read_text())
    assert run["requested_panels"] == [PANEL_START, PANEL_STOP - 1]
    assert run["argument_principle"]["status"] == "NOT_RUN"
    expected = PANEL_START
    generators = set()
    for row in run["rows"]:
        assert row["panel"] == expected
        expected += 1
        generator = row["omega_generator_id"]
        assert generator == row["horizon"]["omega_generator_id"]
        assert generator == row["outgoing"]["omega_generator_id"]
        generators.add(generator)
        if row["boundary_nonvanishing"]["status"] == "PASS":
            assert row["horizon"]["passed"] and row["outgoing"]["passed"]
            assert arb(
                row["physical_mismatch"]["modulus_lower"]
            ).lower() > 0
    assert len(generators) == len(run["rows"])
    if run["all_requested_panels_nonzero"]:
        assert len(run["rows"]) == PANEL_STOP - PANEL_START
        assert run["terminal"] is None
        assert all(
            row["boundary_nonvanishing"]["status"] == "PASS"
            for row in run["rows"]
        )
    else:
        assert run["terminal"] is not None
        assert run["rows"][-1]["panel"] == run["terminal"]["panel"]
    assert certificate["run"]["sha256"] == sha(RUN)
    for item in certificate["imports"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert not certificate["claim_flags"]["full_contour_nonzero_certified"]
    assert not certificate["claim_flags"]["argument_principle_certified"]
    assert not certificate["claim_flags"]["QNM_or_EP2_certified"]
    print(
        "common-affine Evans panels 16--31 verifier: PASS "
        f"({run['completed_panel_count']} materialized rows)"
    )


if __name__ == "__main__":
    main()
