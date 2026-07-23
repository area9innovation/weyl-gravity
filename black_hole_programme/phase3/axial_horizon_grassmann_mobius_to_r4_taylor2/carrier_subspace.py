#!/usr/bin/env python3
"""Produce the exact XH0a/XH0b carrier non-invariance witness."""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_complete_reconstruction_repair import (
    produce as reconstruction,
)

HERE = Path(__file__).resolve().parent
SOURCE = (
    HERE.parent / "axial_complete_reconstruction_repair" / "certificate.json"
)
OUTPUT = HERE / "carrier_subspace_witness.json"
OMEGA0 = sp.Rational(4097, 8192)
RADII = (sp.Rational(5, 2), sp.Rational(3), sp.Rational(4))


def parse_vector(label: str, omega: sp.Symbol) -> sp.Matrix:
    payload = json.loads(SOURCE.read_text())
    strings = payload["endpoint_bases"]["horizon"]["additional_lifts"][label][
        "carrier_leading_vector"
    ]
    return sp.Matrix([sp.sympify(value, locals={"omega": omega, "I": sp.I})
                      for value in strings])


def encode(value: sp.Expr) -> str:
    return sp.sstr(sp.cancel(value))


def produce() -> dict:
    exact = reconstruction.build_exact_system()
    r = exact["symbols"]["r"]
    omega = exact["symbols"]["omega"]
    carrier = exact["carrier"]
    basis_symbolic = sp.Matrix.hstack(
        parse_vector("XH0a", omega), parse_vector("XH0b", omega)
    )
    basis = basis_symbolic.subs(omega, OMEGA0)
    joined = sp.Matrix.hstack(basis, carrier.subs(omega, OMEGA0) * basis)
    determinants = {
        f"r={radius}": encode(sp.det(joined.subs(r, radius)))
        for radius in RADII
    }
    if basis.rank() != 2 or any(sp.sympify(value).equals(0)
                                for value in determinants.values()):
        raise RuntimeError("carrier subspace witness lost rank")
    document = {
        "schema": "phase3-axial-horizon-carrier-subspace-witness-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "frequency": str(OMEGA0),
        "basis": ["XH0a", "XH0b"],
        "leading_vector_matrix": [
            [encode(basis[i, j]) for j in range(2)] for i in range(4)
        ],
        "rank_B": 2,
        "rank_B_join_A_B": 4,
        "determinants": determinants,
        "source": {
            "carrier_matrix": (
                "black_hole_programme/phase3/"
                "axial_complete_reconstruction_repair/produce.py:72"
            ),
            "basis_heads": (
                "black_hole_programme/phase3/"
                "axial_complete_reconstruction_repair/certificate.json"
            ),
        },
        "conclusion": (
            "XH0a and XH0b span the two-dimensional future-regular "
            "zero-indicial solution subspace inside the four-dimensional "
            "Ricci carrier. Their fixed leading-vector coordinate span is "
            "not invariant under A(r)."
        ),
        "does_not_establish": [
            "the rank of any boundary projection",
            "invertibility of a selected endpoint-to-endpoint two-plane map",
            (
                "a scattering, flux-sign, stability, ghost, positivity, "
                "CPT or unitarity claim"
            ),
        ],
    }
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n")
    return document


if __name__ == "__main__":
    print(produce()["conclusion"])
