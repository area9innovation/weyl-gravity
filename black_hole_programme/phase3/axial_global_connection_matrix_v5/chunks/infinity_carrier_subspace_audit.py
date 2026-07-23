#!/usr/bin/env python3
"""Classify the status of the XI0/XI1 finite infinity carrier plane."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp

from .verify_handoff import canonical_sha256


HERE = Path(__file__).resolve().parent
PHASE3 = HERE.parents[1]
INTERFACE = PHASE3 / "axial_endpoint_bases/repair-interface.json"
OUTPUT = HERE / "artifacts/infinity_xi01_subspace_audit.json"
STATE = ("P", "P_prime", "Q", "Q_prime")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    raw = json.loads(INTERFACE.read_text())
    r, omega = sp.symbols("r omega", nonzero=True)
    matrix = sp.Matrix([
        [
            sp.sympify(value, locals={"r": r, "omega": omega, "i": sp.I})
            for value in row
        ]
        for row in raw["carrier_ode_matrix"]
    ])
    if tuple(raw["carrier_state"]) != STATE or matrix.shape != (4, 4):
        raise RuntimeError("carrier interface drift")

    coordinate_planes = []
    for selected in itertools.combinations(range(4), 2):
        outside = tuple(index for index in range(4) if index not in selected)
        defects = [
            {
                "row": STATE[row],
                "column": STATE[col],
                "coefficient": sp.sstr(sp.factor(matrix[row, col])),
            }
            for row in outside
            for col in selected
            if sp.cancel(matrix[row, col]) != 0
        ]
        coordinate_planes.append({
            "selected": [STATE[index] for index in selected],
            "invariant": not defects,
            "defects": defects,
        })
    if any(item["invariant"] for item in coordinate_planes):
        raise RuntimeError("unexpected two-coordinate carrier subsystem")

    payload = {
        "schema": "phase3-axial-infinity-xi01-subspace-audit-v1",
        "status": "CERTIFIED_STRUCTURAL_CLASSIFICATION",
        "source": {
            "path": INTERFACE.relative_to(HERE.parents[4]).as_posix(),
            "sha256": _sha256(INTERFACE),
        },
        "carrier_state": list(STATE),
        "carrier_dimension_complex": 4,
        "finite_rate_zero_boundary_basis": ["XI0", "XI1"],
        "finite_rate_zero_dimension_complex": 2,
        "coordinate_plane_audit": coordinate_planes,
        "classification": {
            "XI0_XI1": (
                "a two-dimensional asymptotically selected solution plane "
                "inside the four-dimensional Ricci-carrier solution space"
            ),
            "not": (
                "a closed two-coordinate Ricci subsystem in the declared "
                "(P,P_prime,Q,Q_prime) first-order variables"
            ),
            "radial_uniqueness_establishes": (
                "injective transport of this plane onto its propagated image"
            ),
            "radial_uniqueness_does_not_establish": (
                "surjectivity of the horizon-regular boundary plane onto the "
                "XI0/XI1 infinity plane, or nonzero intersection of the two"
            ),
        },
        "does_not_establish": [
            "horizon-to-infinity matching",
            "a globally populated finite-flux Ricci channel",
            "invertibility of a boundary-to-boundary restricted map",
            "flux, stability, ghost, CPT, or unitarity",
        ],
    }
    payload["payload_sha256"] = canonical_sha256(payload)
    return payload


def verify(data: dict) -> bool:
    expected = build()
    if data != expected:
        raise RuntimeError("XI0/XI1 subspace certificate drift")
    return True


def main() -> int:
    payload = build()
    verify(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("PASS XI0/XI1 is endpoint-selected, not a closed coordinate subsystem")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
