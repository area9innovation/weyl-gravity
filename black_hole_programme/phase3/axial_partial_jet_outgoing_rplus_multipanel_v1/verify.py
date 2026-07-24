#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    d = json.loads((HERE / "certificate.json").read_text())
    assert d["claim_flags"]["T_plus_recovered"] is False
    assert d["claim_flags"]["complementary_outgoing_columns_constructed"] is False
    assert d["claim_flags"]["K_plus_computed"] is False
    for item in d["imports"].values():
        p = ROOT / item["path"]
        assert sha256(p) == item["sha256"]
    t = d["transport"]
    for key in ("source", "compile_log", "run_log"):
        p = ROOT / t[f"{key}_path"]
        assert sha256(p) == t[f"{key}_sha256"]
    if d["status"] == "RPLUS_CORRELATED_FIRST_CHUNK_PASS":
        assert t["parsed_result"]["status"] == "PASS"
        assert d["claim_flags"]["Rplus_reaches_63_over_2"] is True
        assert d["claim_flags"]["Rplus_reaches_r4"] is False
        assert d["shortfall"]["code"] == "FULL_896_PANEL_MONOLITH_EXCEEDS_SCOPED_RUNTIME_BUDGET"
    else:
        assert d["status"] == "RPLUS_CORRELATED_MULTIPANEL_SHORTFALL"
        assert t["parsed_result"]["status"] == "REFUSED"
        assert d["shortfall"]["first_failed_panel"] is not None
    print("PASS outgoing Rplus multipanel certificate")

if __name__ == "__main__":
    main()
