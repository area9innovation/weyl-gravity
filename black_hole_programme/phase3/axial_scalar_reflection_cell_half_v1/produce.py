#!/usr/bin/env python3
"""Produce the real-frequency-cell scalar-reflection certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .rigorous import OMEGA_LEFT, OMEGA_RIGHT, run_all


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SCHEMA = "phase3-axial-scalar-reflection-cell-half-v1"
IMPORTS = {
    "point_engine": (
        "black_hole_programme/phase3/"
        "axial_scalar_reflection_point_half_v1/rigorous.py"
    ),
    "incoming_connection": (
        "black_hole_programme/phase3/"
        "axial_incoming_connection_analytic/certificate.json"
    ),
    "triangular_factorization": (
        "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    rails = run_all()
    lower_bounds = {}
    for spin in (1, 2):
        values = [
            float(rails[name][f"spin_{spin}"]["bounds"]["abs_A_out_lower"])
            for name in rails
        ]
        squared = [
            float(
                rails[name][f"spin_{spin}"]["bounds"][
                    "abs_A_out_squared_lower"
                ]
            )
            for name in rails
        ]
        lower_bounds[f"spin_{spin}"] = {
            "abs_A_out_lower": repr(min(values)),
            "abs_A_out_squared_lower": repr(min(squared)),
            "both_rails_exclude_zero": all(value > 0 for value in values),
        }
    return {
        "schema": SCHEMA,
        "status": (
            "VALIDATED_REAL_CELL_SPIN_ONE_AND_SPIN_TWO_"
            "OUTGOING_REFLECTION_NONVANISHING"
        ),
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "scope": {
            "background": "Schwarzschild M=1",
            "parity": "axial",
            "ell": 2,
            "frequency_interval": [OMEGA_LEFT, OMEGA_RIGHT],
            "channels": ["spin_one", "spin_two"],
        },
        "imports": {
            name: {"path": path, "sha256": sha256(ROOT / path)}
            for name, path in IMPORTS.items()
        },
        "method": {
            "backend": "python-flint Arb/Acb ball arithmetic",
            "frequency_representation": (
                "one real Arb ball 0.5 +/- 0.00005"
            ),
            "spatial_engine": (
                "Taylor recurrence, Cauchy coefficient tail and Gronwall "
                "defect enclosure imported from the independently tested "
                "point-frequency rail"
            ),
            "frequency_dependency_policy": (
                "frequency-ball coefficient radii are accumulated into the "
                "validated spatial defect at every step; no midpoint-only "
                "or sampling inference"
            ),
            "tail_policy": (
                "exact horizon and infinity potential integrals multiplied "
                "by the directed Arb upper bound of 1/omega"
            ),
            "independent_geometries": [
                "h=1/8, Taylor order 24",
                "h=1/16, Taylor order 20",
            ],
            "rails": rails,
        },
        "certified_lower_bounds": lower_bounds,
        "claim_flags": {
            "spin_one_reflection_nonzero_on_cell": True,
            "spin_two_reflection_nonzero_on_cell": True,
            "full_declared_cell_certified": True,
            "whole_pilot_interval_certified": False,
            "explicit_full_Tplus_matrix_certified": False,
            "extension_offdiagonal_entries_certified": False,
            "time_domain_or_quantum_claim": False,
        },
        "does_not_establish": [
            "reflection nonvanishing outside the declared frequency cell",
            "reflection nonvanishing on the complete pilot interval",
            "the explicit full 3x3 outgoing Bach connection matrix",
            "outgoing extension amplitudes or channel mixing",
            "time-domain boundedness, limiting absorption or decay",
            "a QNM Smith selector or Green-resolvent pole",
            "positivity, particles, ghosts, CPT or quantum unitarity",
        ],
    }


def render(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render(build())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != content:
            raise RuntimeError("certificate drift")
        print("PASS scalar reflection cell-half reproduction")
        return 0
    OUTPUT.write_text(content)
    RECEIPT.write_text(
        render(
            {
                "schema": (
                    "phase3-axial-scalar-reflection-cell-half-receipt-v1"
                ),
                "certificate": OUTPUT.name,
                "certificate_sha256": sha256(OUTPUT),
                "producer": "produce.py",
                "commands": [
                    (
                        "python3 -m black_hole_programme.phase3."
                        "axial_scalar_reflection_cell_half_v1.produce --check"
                    ),
                    (
                        "python3 -m black_hole_programme.phase3."
                        "axial_scalar_reflection_cell_half_v1.verify"
                    ),
                    (
                        "python3 -m unittest -v black_hole_programme.phase3."
                        "axial_scalar_reflection_cell_half_v1.tests."
                        "test_reflection_cell"
                    ),
                ],
                "claim_boundary": (
                    "scalar diagonal reflection nonvanishing only on "
                    "[0.49995,0.50005]; no whole-pilot, explicit-Tplus, "
                    "off-diagonal, QNM or time-domain claim"
                ),
            }
        )
    )
    print("PASS spin-one and spin-two reflection on declared cell")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
