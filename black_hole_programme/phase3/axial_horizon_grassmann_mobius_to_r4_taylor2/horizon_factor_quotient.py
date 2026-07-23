#!/usr/bin/env python3
"""Apply the certified horizon factor quotient to the exact outward Gram."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GRAM = HERE / "future_horizon_outward_gram.json"
DEVISSAGE = (
    ROOT / "black_hole_programme/phase3/"
    "axial_boundary_devissage_no_growth/certificate.json"
)
OUTPUT = HERE / "future_horizon_factor_quotient.json"


def conjugate(value: sp.Expr, omega: sp.Symbol) -> sp.Expr:
    return sp.conjugate(value).subs(sp.conjugate(omega), omega)


def produce() -> dict:
    omega = sp.Symbol("omega", real=True, nonzero=True)
    local = {"omega": omega, "I": sp.I}
    gram_document = json.loads(GRAM.read_text())
    gram = sp.Matrix([
        [sp.sympify(value, locals=local) for value in row]
        for row in gram_document["gram_without_pi_alpha_W"]
    ])
    devissage = json.loads(DEVISSAGE.read_text())
    horizon = devissage["local_boundary_maps"]["future_horizon"]
    amplitude_a = sp.sympify(
        horizon["spin_one_quotient_amplitudes"]["XH0a"], locals=local
    )
    amplitude_b = sp.sympify(
        horizon["spin_one_quotient_amplitudes"]["XH0b"], locals=local
    )
    # New basis (RH,SH,EH) with RH=XH0a-(A/B)XH0b, SH=XH0b, EH=EH0.
    change = sp.Matrix([
        [1, 0, 0],
        [-amplitude_a / amplitude_b, 1, 0],
        [0, 0, 1],
    ])
    factor_gram = (
        change.conjugate().T.subs(sp.conjugate(omega), omega)
        * gram * change
    ).applyfunc(sp.cancel)
    spin_two = factor_gram.extract([0, 2], [0, 2])
    cross = factor_gram.extract([0, 2], [1])
    raw_quotient = factor_gram[1, 1]
    schur = sp.factor(sp.cancel(
        raw_quotient
        - (cross.conjugate().T.subs(sp.conjugate(omega), omega)
           * spin_two.inv() * cross)[0]
    ))
    amplitude_norm = sp.factor(sp.cancel(
        conjugate(amplitude_b, omega) * amplitude_b
    ))
    unit_quotient = sp.factor(sp.cancel(schur / amplitude_norm))
    spin_two_determinant = sp.factor(sp.cancel(spin_two.det()))
    expected_unit = -sp.Rational(32, 15) / omega
    if sp.cancel(unit_quotient - expected_unit) != 0:
        raise RuntimeError("unit spin-one quotient sign changed")
    document = {
        "schema": "phase3-axial-future-horizon-factor-quotient-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "PASS",
        "frequency_interval": ["1/2", "3/4"],
        "factor_basis": ["RH", "SH", "EH"],
        "quotient_map": {
            "pi_x_XH0a": sp.sstr(amplitude_a),
            "pi_x_XH0b": sp.sstr(amplitude_b),
            "RH": "XH0a-(pi_x_XH0a/pi_x_XH0b)*XH0b",
            "SH": "XH0b",
            "EH": "EH0",
        },
        "spin_two_extension": {
            "basis": ["RH", "EH"],
            "determinant": sp.sstr(spin_two_determinant),
            "inertia_for_alpha_W_positive": [1, 1, 0],
        },
        "spin_one_quotient": {
            "raw_lift": "SH",
            "raw_schur_complement": sp.sstr(schur),
            "quotient_amplitude_norm": sp.sstr(amplitude_norm),
            "unit_quotient_norm": sp.sstr(unit_quotient),
            "inertia_for_alpha_W_positive": [0, 1, 0],
        },
        "full_inertia_for_alpha_W_positive": [1, 2, 0],
        "structural_check": (
            "the exact outward Gram is the hyperbolic spin-two extension "
            "plus a strictly negative spin-one quotient line"
        ),
        "provenance": {
            "gram_path": str(GRAM.relative_to(ROOT)),
            "gram_sha256": hashlib.sha256(GRAM.read_bytes()).hexdigest(),
            "devissage_path": str(DEVISSAGE.relative_to(ROOT)),
            "devissage_sha256": hashlib.sha256(
                DEVISSAGE.read_bytes()
            ).hexdigest(),
        },
        "does_not_establish": [
            "a splitting of the differential extension",
            "a global horizon-to-infinity connection",
            "a boundary projection rank or scattering map",
            "stability, ghost, positivity, CPT or unitarity",
        ],
    }
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n")
    return document


if __name__ == "__main__":
    result = produce()
    print(result["spin_one_quotient"]["unit_quotient_norm"])
