#!/usr/bin/env python3
"""Independent structural verifier for the reflection-cell certificate."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    data = json.loads(CERTIFICATE.read_text())
    require(
        data["schema"] == "phase3-axial-scalar-reflection-cell-half-v1",
        "schema drift",
    )
    require(
        data["scope"]["frequency_interval"] == ["0.49995", "0.50005"],
        "frequency cell drift",
    )
    for imported in data["imports"].values():
        require(
            sha256(ROOT / imported["path"]) == imported["sha256"],
            f"import drift: {imported['path']}",
        )
    require(
        len(data["method"]["rails"]) == 2,
        "independent geometry count drift",
    )
    for spin in (1, 2):
        exported = Decimal(
            data["certified_lower_bounds"][f"spin_{spin}"][
                "abs_A_out_lower"
            ]
        )
        require(exported > 0, f"spin-{spin} exported lower bound vanished")
        for rail in data["method"]["rails"].values():
            require(
                Decimal(
                    rail[f"spin_{spin}"]["bounds"]["abs_A_out_lower"]
                )
                > 0,
                f"spin-{spin} rail includes zero",
            )
    flags = data["claim_flags"]
    require(flags["full_declared_cell_certified"] is True, "cell gate lost")
    require(
        flags["spin_one_reflection_nonzero_on_cell"] is True,
        "spin-one gate lost",
    )
    require(
        flags["spin_two_reflection_nonzero_on_cell"] is True,
        "spin-two gate lost",
    )
    for key in (
        "whole_pilot_interval_certified",
        "explicit_full_Tplus_matrix_certified",
        "extension_offdiagonal_entries_certified",
        "time_domain_or_quantum_claim",
    ):
        require(flags[key] is False, f"overclaim: {key}")
    print("PASS scalar reflection cell-half certificate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
