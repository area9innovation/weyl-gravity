#!/usr/bin/env python3
"""Produce the exact axial threshold-structure certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_data() -> dict:
    r, omega = sp.symbols("r omega", positive=True, nonzero=True)
    D = lambda value: sp.factor((r - 2) * sp.diff(value, r) / r)
    v2 = 6 * (r - 2) * (r - 1) / r**4
    v1 = 6 * (r - 2) / r**3
    phi2 = r**3 / 8
    phi1 = r**2 * (2 * r - 3) / 4
    companion2 = (
        r**3 * sp.log((r - 2) / r) / 32
        + r**2 / 16
        + r / 16
        + sp.Rational(1, 12)
        + 1 / (8 * r)
    )
    companion1 = (
        3 * r**2 * (2 * r - 3) * sp.log((r - 2) / r)
        + 12 * r**2
        - 6 * r
        - 2
    ) / 24
    cocycle = (
        sp.I
        * (r - 2)
        * (2 * r * omega**2 + 3 * omega**2 + 12)
        / (5 * r**4 * omega)
    )
    decomposition = (
        2 * sp.I * (v1 - v2) / (5 * omega)
        + sp.I * omega * (r - 2) * (2 * r + 3) / (5 * r**4)
    )
    primitive = -r**2 / 4 - r / 4 - sp.Rational(1, 3) - 1 / (2 * r)
    primitive_h = primitive + sp.Rational(25, 12) * phi2

    checks = {
        "spin_two_zero_mode": sp.factor(D(D(phi2)) - v2 * phi2),
        "spin_one_zero_mode": sp.factor(D(D(phi1)) - v1 * phi1),
        "spin_two_companion": sp.simplify(D(D(companion2)) - v2 * companion2),
        "spin_one_companion": sp.simplify(D(D(companion1)) - v1 * companion1),
        "cocycle_decomposition": sp.factor(cocycle - decomposition),
        "primitive": sp.factor(D(D(primitive)) - v2 * primitive - (r - 2) / r),
        "horizon_fixed_primitive": sp.factor(primitive_h.subs(r, 2)),
    }
    if any(sp.simplify(value) != 0 for value in checks.values()):
        raise RuntimeError(f"exact threshold identity failed: {checks}")

    return {
        "schema": "axial-threshold-exact-structure-v1",
        "status": "EXACT_THRESHOLD_IDENTITIES_PASS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "operator": {
            "D": "(r-2)/r*d/dr",
            "V2": sp.sstr(v2),
            "V1": sp.sstr(v1),
        },
        "zero_modes": {
            "spin_two": sp.sstr(phi2),
            "spin_one": sp.sstr(phi1),
            "horizon_values": ["1", "1"],
        },
        "reduction_of_order": {
            "spin_two": sp.sstr(companion2),
            "spin_one": sp.sstr(companion1),
            "horizon_behavior": "logarithmically_singular",
            "infinity_leading": {
                "spin_two": "-1/(5*r**2)",
                "spin_one": "-1/(10*r**2)",
            },
        },
        "zero_energy_resonance": {
            "spin_two": False,
            "spin_one": False,
            "reason": "the unique horizon-regular solutions grow as nonzero multiples of r^3",
        },
        "projective_cocycle": {
            "I_reduced": sp.sstr(cocycle),
            "threshold_decomposition": sp.sstr(decomposition),
            "leading_term": "2*I*(V1-V2)/(5*omega)",
            "leading_source_on_phi02": "3*I*(r-2)/(10*r*omega)",
        },
        "primitive": {
            "p": sp.sstr(primitive),
            "identity": "(D**2-V2)*p=(r-2)/r",
            "p_horizon_fixed": sp.sstr(primitive_h),
            "p_horizon_fixed_at_2": "0",
        },
        "formal_targets_not_certified": {
            "spin_two_jost_magnitude": "15/(16*omega**3)",
            "spin_one_jost_magnitude": "15/(4*omega**3)",
            "det_Tplus_magnitude": "3375/(1024*omega**9)",
            "extension_ratio": "b/a**2=O(omega**2)",
        },
        "does_not_establish": [
            "a two-region Volterra remainder estimate",
            "a punctured positive-real interval on which T_plus is invertible",
            "the stated low-frequency Jost or absorption asymptotics as rigorous estimates",
            "the normalization-sensitive b/a^2 threshold bound",
            "time-domain boundedness, decay, or a quantum statement",
        ],
    }


def main() -> None:
    data = exact_data()
    CERTIFICATE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "axial-threshold-exact-structure-receipt-v1",
        "status": "PASS",
        "certificate": str(CERTIFICATE.relative_to(HERE.parents[2])),
        "certificate_sha256": sha256(CERTIFICATE),
        "producer_sha256": sha256(Path(__file__)),
        "verification": [
            "all seven exact SymPy residuals vanish",
            "formal scattering targets remain outside certified theorem fields",
        ],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
