#!/usr/bin/env python3
"""Independent materialized verifier for the bounded contour chunk."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb

from .chunk import RUN

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads(CERT.read_text())
    run = json.loads(RUN.read_text())
    assert run["requested_panels"] == [0, 15]
    assert run["completed_panel_count"] == 16
    assert run["all_requested_panels_nonzero"]
    assert run["terminal"] is None
    assert run["argument_principle"]["status"] == "NOT_RUN"
    generators = set()
    for expected, row in enumerate(run["rows"]):
        assert row["panel"] == expected
        assert row["boundary_nonvanishing"]["status"] == "PASS"
        assert row["horizon"]["passed"] and row["outgoing"]["passed"]
        generator = row["omega_generator_id"]
        assert generator == row["horizon"]["omega_generator_id"]
        assert generator == row["outgoing"]["omega_generator_id"]
        generators.add(generator)
        assert arb(row["physical_mismatch"]["modulus_lower"]).lower() > 0
    assert len(generators) == 16
    assert certificate["run"]["sha256"] == sha(RUN)
    for item in certificate["imports"].values():
        assert sha(ROOT / item["path"]) == item["sha256"]
    assert certificate["claim_flags"]["panels_0_through_15_nonzero_certified"]
    assert not certificate["claim_flags"]["full_contour_nonzero_certified"]
    assert not certificate["claim_flags"]["argument_principle_certified"]
    print("common-affine Evans panels 0--15 verifier: PASS")


if __name__ == "__main__":
    main()
