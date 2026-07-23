#!/usr/bin/env python3
"""Regenerate the practical infinity initializer at one exact frequency."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from black_hole_programme.phase3.axial_infinity_practical_transfer import (
    produce as practical,
)

from .verify_handoff import canonical_sha256


OMEGA0 = Fraction(4097, 8192)
SCHEMA = "phase3-axial-exact-point-infinity-endpoint-v1"


def build_point_source() -> tuple[str, dict]:
    """Return a fresh point-frequency endpoint adapter and its typed receipt."""
    old_cells = practical.OMEGA_CELLS
    try:
        practical.OMEGA_CELLS = ((OMEGA0, OMEGA0),)
        exact = practical.scaled_exact_expressions()
        cells = [
            practical.bound_cell(
                exact, (OMEGA0, OMEGA0), z_cell
            )
            for z_cell in practical.Z_CELLS
        ]
        certificate = practical.build_data_from(exact, cells)
        source = practical.render_adapter(certificate, exact)
    finally:
        practical.OMEGA_CELLS = old_cells
    receipt = {
        "schema": SCHEMA,
        "status": "REGENERATED_EXACT_POINT_ENDPOINT",
        "frequency": {
            "parameter": "Momega",
            "value": f"{OMEGA0.numerator}/{OMEGA0.denominator}",
            "radius": "0/1",
        },
        "z_cell_count": len(practical.Z_CELLS),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "construction": (
            "formal basis, rational Neumann bounds, and Volterra correction "
            "regenerated with the omega interval collapsed exactly to omega0"
        ),
        "not_constructed_from": (
            "evaluation at e=0 of the inherited whole-frequency-cell endpoint "
            "Taylor remainder"
        ),
        "does_not_establish": [
            "horizon-to-infinity matching",
            "a scattering channel",
            "flux, stability, ghost, CPT, or unitarity",
        ],
    }
    receipt["payload_sha256"] = canonical_sha256(receipt)
    return source, receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    source, receipt = build_point_source()
    args.source.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.source.write_text(source)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("PASS regenerated exact-point infinity endpoint")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
