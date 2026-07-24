#!/usr/bin/env python3
"""Fail-closed verifier for the reciprocal horizon chart artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cert = json.loads((HERE / "certificate.json").read_text())
    run = json.loads((HERE / "reciprocal-run.json").read_text())
    assert cert["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    assert cert["run"]["sha256"] == sha(HERE / "reciprocal-run.json")
    assert len(run["rows"]) == 16
    denominator_count = 0
    reached_count = 0
    for row in run["rows"]:
        assert row["first_obstruction"]["failure"] == "REFERENCE_Q_MAJORANT_DISCRIMINANT"
        assert row["switch"]["denominator_excludes_zero"]
        denominator_count += int(row["switch"]["denominator_excludes_zero"])
        assert float(row["switch"]["q_modulus_lower"].split()[0].lstrip("[")) > 0
        if row["reached_r4"]:
            reached_count += 1
            assert row["terminal"] is None
            assert row["checkpoint_r4"] is not None
        else:
            assert row["terminal"] is not None
    assert denominator_count == cert["chart_switch"]["certified_panel_count"]
    assert reached_count == cert["transport"]["reached_panel_count"]
    assert (
        cert["claim_flags"]["full_panel_reciprocal_denominator_certified"]
        == (denominator_count == 16)
    )
    assert cert["claim_flags"]["all_panels_reached_r4"] == (reached_count == 16)
    assert not cert["claim_flags"]["QNM_or_EP2_certified"]
    assert not cert["claim_flags"]["Evans_boundary_nonzero_certified"]
    print("PASS")


if __name__ == "__main__":
    main()
