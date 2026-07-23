"""Boundary verifier for the unvalidated one-frequency diagnostic."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PHASE3 = HERE.parent
DATA = HERE / "pilot-diagnostic.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def main() -> None:
    data = json.loads(DATA.read_text())
    require(data["lifecycle"] == "UNVALIDATED-NUMERIC", "lifecycle promoted")
    flags = data["claim_flags"]
    require(flags["diagnostic_preview_computed"], "diagnostic absent")
    for key in (
        "declared_flux_conservation_passed",
        "validated_global_connection",
        "physical_scattering_channels_classified",
        "physical_ghost_established",
        "stability_or_pole_exclusion_established",
    ):
        require(not flags[key], key + " was promoted")
    require(data["scope"]["frequency"] == "M*omega=1/2",
            "pilot frequency changed")
    require(data["basis"]["horizon_future_regular"] == ["XH0a", "XH0b", "EH0"],
            "horizon basis changed")
    require(data["basis"]["Iminus"] == ["XI0", "XI1", "EI0"],
            "Iminus basis changed")
    require(data["basis"]["Iplus"] == ["XI2", "XI3", "EI2"],
            "Iplus basis changed")
    require(all(value == 3 for value in data["connection"]["numeric_rank"].values()),
            "point rank diagnostic changed")
    inertia = data["flux_diagnostic"]["numeric_inertia"]
    require(inertia["Cminus_dagger_Gminus_Cminus"] == [1, 2, 0],
            "Iminus point inertia changed")
    require(inertia["Cplus_dagger_Gplus_Cplus"] == [1, 2, 0],
            "Iplus point inertia changed")
    require(inertia["Hplus_outward_candidate"] == [1, 2, 0],
            "future-horizon point inertia changed")
    tests = data["flux_diagnostic"]["orientation_tests"]
    declared = float(
        tests["declared_Hplus_plus_Iplus_minus_Iminus"]["relative_max_residual"])
    reversed_control = float(
        tests["incorrect_double_reversal_minus_Hplus_plus_Iplus_minus_Iminus"]
        ["relative_max_residual"])
    require(1e-4 < declared < 1e-2,
            "correctly oriented residual left its recorded scale")
    require(reversed_control > 0.9,
            "incorrect horizon-sign control unexpectedly became small")
    require(
        data["flux_diagnostic"]["orientation_crosswalk"].startswith(
            "The imported radial matrix represents F^r/"
        ),
        "orientation crosswalk is absent",
    )
    require(not data["missing_Hminus"]["available"], "Hminus was invented")
    require(len(data["does_not_establish"]) >= 6, "boundaries were weakened")

    for relative, expected in data["imports"].items():
        path = PHASE3 / relative
        require(path.exists(), "missing import " + relative)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == expected, "import hash drift " + relative)
    print("PASS unvalidated axial connection pilot boundaries")


if __name__ == "__main__":
    main()
