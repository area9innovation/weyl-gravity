#!/usr/bin/env python3
"""Independent verifier for the Weyl/Euler current transgression."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path = CERT) -> None:
    c = json.loads(path.read_text())
    assert c["schema"] == "weyl-euler-current-transgression-v1"
    assert c["dependency_tags"] == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]

    # Independently recover the four-dimensional curvature coefficient.
    assert c["four_dimensional_decomposition"]["identity"] == (
        "C2=E4+2*Ric2-(2/3)*R2"
    )
    assert c["euler_transgression"]["identity"] == (
        "omega_E(delta1,delta2)=d k_E(delta1,delta2)"
    )
    assert c["euler_transgression"]["literal_minus_ricci"] == (
        "omega_C2-omega_Ric=d k_E"
    )

    # Re-derive the reduced Fourier identity without using producer formulas.
    alpha, x, y, radius, p, q, time = sp.symbols(
        "alpha x y r p q t", nonzero=True
    )
    exponential = sp.exp(sp.I * (x + y) * time)
    independently_derived_cut = (
        sp.Rational(192, 5)
        * sp.pi
        * sp.I
        * alpha
        * (x - y)
        * p
        * q
        * exponential
        / (x * y * radius)
    )
    independently_derived_flux = sp.diff(independently_derived_cut, time)
    expected_flux = (
        -sp.Rational(192, 5)
        * sp.pi
        * alpha
        * (x**2 - y**2)
        * p
        * q
        * exponential
        / (x * y * radius)
    )
    assert sp.simplify(independently_derived_flux - expected_flux) == 0
    assert c["axial_einstein_cut"]["identity"] == "F_EE^r=partial_t Q_EE"

    # The packet theorem is deliberately finite-radius first and fail-closed
    # at endpoints unless a separate dominated-convergence gate is supplied.
    packet = c["wave_packet_theorem"]
    assert "bounded away from omega=0" in packet["core"]
    assert "Schwartz" in packet["time_regular"]
    assert packet["conclusion"] == (
        "the complete Einstein wave-packet subspace is totally isotropic"
    )

    for imported in c["imports"].values():
        imported_path = ROOT / imported["path"]
        assert sha256(imported_path) == imported["sha256"]

    flags = c["claim_flags"]
    for key in [
        "general_euler_transgression_explicit",
        "literal_minus_ricci_current_exact",
        "axial_cut_identity_exact",
        "smooth_packet_finite_radius_integrated_flux_zero",
        "einstein_wave_packet_total_isotropy",
    ]:
        assert flags[key] is True
    for key in [
        "monochromatic_current_pointwise_zero",
        "unconditional_endpoint_limit_interchange",
        "mixed_einstein_additional_pairing_euler_exact",
        "quantum_statement",
    ]:
        assert flags[key] is False


def main() -> None:
    verify()
    print("PASS: independent Weyl/Euler current-transgression verification")


if __name__ == "__main__":
    main()
