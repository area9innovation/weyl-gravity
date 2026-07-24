#!/usr/bin/env python3
"""Independent verifier for the reduced-phase infinity preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    certificate = json.loads((HERE / "certificate.json").read_text())
    assert certificate["status"] == (
        "FINITE_REDUCED_PHASE_SEED_PANEL_PASS_JOST_REMAINDER_OPEN"
    )
    assert certificate["phase_factor"]["kept_symbolic"] is True
    assert certificate["phase_factor"]["omega_phase_taylor_expanded"] is False
    assert certificate["exact_endpoint_factor_seed"][
        "spin_one_projection_zero"
    ] is True
    rail = certificate["mixed_rail"]
    assert rail["finite_seed_and_panel_passed"] is True
    assert rail["compile_exit"] == 0 and rail["run_exit"] == 0
    assert rail["parsed_result"]["status"] == "PASS"
    gate = certificate["correlation_gate"]
    assert gate["coefficient_equal"] is True
    assert gate["interval_difference_contains_zero"] is True
    flags = certificate["claim_flags"]
    assert flags["uniform_all_order_infinity_remainder_enclosed"] is False
    assert flags["outgoing_Jost_column_certified"] is False
    assert flags["T_plus_recovered"] is False
    assert flags["scattering_claim"] is False
    for item in certificate["imports"].values():
        path = ROOT / item["path"]
        assert path.exists()
        assert sha256(path) == item["sha256"]
    for key in ("source", "compile_log", "run_log"):
        path = ROOT / rail[f"{key}_path"]
        assert path.exists()
        assert sha256(path) == rail[f"{key}_sha256"]
    print("PASS reduced-phase infinity partial-jet preflight")


if __name__ == "__main__":
    main()
