#!/usr/bin/env python3
"""Fail-closed structural verifier for the point-reflection certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify(data: dict) -> None:
    require(
        data["schema"] == "phase3-axial-scalar-reflection-point-half-v1",
        "schema drift",
    )
    require(data["scope"]["frequency"] == "1/2", "frequency drift")
    for item in data["imports"].values():
        require(sha256(ROOT / item["path"]) == item["sha256"], "input drift")

    require(
        data["convention_crosswalk"]["horizon_initial_line"] == "(a,b)=(1,0)",
        "horizon line drift",
    )
    require(
        data["convention_crosswalk"]["asymptotic_reading"]
        == "A_in_s=lim a; A_out_s=lim b",
        "asymptotic coefficient drift",
    )
    rails = data["validated_method"]["rails"]
    require(len(rails) == 2, "two-geometry control was lost")
    for spin in (1, 2):
        local_bounds = []
        for rail in rails.values():
            channel = rail[f"spin_{spin}"]
            require(channel["spin"] == spin, "channel type drift")
            require(channel["bounds"]["zero_excluded"] is True, "zero admitted")
            lower = float(channel["bounds"]["abs_A_out_lower"])
            error = float(channel["errors"]["total_A_out_error_upper"])
            centre = float(
                channel["bounds"]["finite_A_out_centre_modulus_lower"]
            )
            require(lower > 0.0, "nonpositive reflection lower bound")
            require(centre - error >= lower, "lower-bound arithmetic drift")
            local_bounds.append(lower)
        exported = float(
            data["certified_lower_bounds"][f"spin_{spin}"][
                "abs_A_out_lower"
            ]
        )
        require(exported <= min(local_bounds), "exported bound is too strong")
        require(exported > 0.0, "exported scalar reflection bound vanished")

    flags = data["claim_flags"]
    require(flags["spin_one_reflection_nonzero_at_omega_half"] is True, "s1")
    require(flags["spin_two_reflection_nonzero_at_omega_half"] is True, "s2")
    require(flags["whole_frequency_cell_certified"] is False, "cell overclaim")
    require(flags["explicit_full_Tplus_matrix_certified"] is False, "Tplus")
    require(
        flags["extension_offdiagonal_entries_certified"] is False,
        "extension overclaim",
    )


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("PASS point-reflection certificate verified fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
