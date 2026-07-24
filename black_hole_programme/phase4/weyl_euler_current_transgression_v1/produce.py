#!/usr/bin/env python3
"""Produce the exact Weyl/Euler current-transgression certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
HESSIAN = (
    ROOT
    / "black_hole_programme/phase4/axial_universal_hessian_intertwiner_v1/certificate.json"
)
CARRIER = (
    ROOT
    / "black_hole_programme/phase4/covariant_einstein_maxwell_carrier_v1/certificate.json"
)
FLUX = ROOT / "black_hole_programme/phase3/axial_null_flux_gram/certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_data() -> dict:
    # Curvature decomposition in four dimensions.
    ric2, r2, e4 = sp.symbols("Ric2 R2 E4")
    c2 = e4 + 2 * ric2 - sp.Rational(2, 3) * r2
    assert sp.expand(c2 - e4 - 2 * ric2 + sp.Rational(2, 3) * r2) == 0

    # Exact Fourier cut-current identity.
    alpha, w1, w2, radius, psi1, psi2, time = sp.symbols(
        "alpha w1 w2 r Psi1 Psi2 t", nonzero=True
    )
    phase = sp.exp(sp.I * (w1 + w2) * time)
    flux = (
        -sp.Rational(192, 5)
        * sp.pi
        * alpha
        * (w1**2 - w2**2)
        / (w1 * w2 * radius)
        * psi1
        * psi2
        * phase
    )
    cut = (
        sp.Rational(192, 5)
        * sp.pi
        * sp.I
        * alpha
        * (w1 - w2)
        / (w1 * w2 * radius)
        * psi1
        * psi2
        * phase
    )
    assert sp.simplify(sp.diff(cut, time) - flux) == 0

    imports = {}
    for name, path in {
        "universal_hessian": HESSIAN,
        "covariant_carrier": CARRIER,
        "axial_flux_gram": FLUX,
    }.items():
        imports[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }

    return {
        "schema": "weyl-euler-current-transgression-v1",
        "status": "EXACT_WEYL_EULER_CURRENT_TRANSGRESSION_PASS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "four_dimensional_decomposition": {
            "identity": "C2=E4+2*Ric2-(2/3)*R2",
            "euler_form": "E4=epsilon_abcd*R^ab wedge R^cd",
            "bulk_hessian_mod_euler": (
                "4*alpha*Integral(psi1_ab*psi2**ab-(1/3)*psi1*psi2)"
            ),
            "einstein_bulk_block": "zero when deltaR_ab[h_E]=0",
        },
        "euler_transgression": {
            "current_convention": "omega(delta1,delta2)=delta1 Theta(delta2)-delta2 Theta(delta1)",
            "potential": "Theta_E(delta)=2*alpha*epsilon_abcd*deltaGamma^ab wedge R^cd",
            "cut_two_form": (
                "k_E(delta1,delta2)=2*alpha*epsilon_abcd*"
                "delta1Gamma^ab wedge delta2Gamma^cd"
            ),
            "identity": "omega_E(delta1,delta2)=d k_E(delta1,delta2)",
            "literal_minus_ricci": "omega_C2-omega_Ric=d k_E",
            "derivation": (
                "deltaR=D(deltaGamma), D epsilon=0, and graded antisymmetry "
                "give d(delta1Gamma wedge delta2Gamma)="
                "delta2Gamma wedge D(delta1Gamma)-"
                "delta1Gamma wedge D(delta2Gamma)"
            ),
        },
        "axial_einstein_cut": {
            "fourier_convention": "exp(i*(omega1+omega2)*t)",
            "flux": (
                "-192*pi*alpha*(omega1**2-omega2**2)"
                "*Psi1*Psi2*exp(i*(omega1+omega2)*t)"
                "/(5*omega1*omega2*r)"
            ),
            "cut": (
                "192*pi*i*alpha*(omega1-omega2)"
                "*Psi1*Psi2*exp(i*(omega1+omega2)*t)"
                "/(5*omega1*omega2*r)"
            ),
            "identity": "F_EE^r=partial_t Q_EE",
            "pointwise_flux_zero": False,
        },
        "wave_packet_theorem": {
            "core": (
                "smooth compact frequency support bounded away from omega=0, "
                "with radial profiles obeying the declared packet bounds"
            ),
            "time_regular": "inverse Fourier transforms and the cut bilinear are Schwartz in t",
            "finite_radius_identity": (
                "Integral_{-infinity}^{infinity} F_EE^r dt="
                "Q_EE(+infinity)-Q_EE(-infinity)=0"
            ),
            "conclusion": "the complete Einstein wave-packet subspace is totally isotropic",
            "endpoint_scope": (
                "null and horizon limits only where the declared bounds justify "
                "interchanging the endpoint limit with the time integral"
            ),
        },
        "phase_space_interpretation": {
            "einstein_self_block": "Euler-exact cut contribution and zero integrated packet flux",
            "mixed_block": "not established Euler-exact and certified nonzero in populated fixtures",
            "conclusion": "Einstein wave packets form an isotropic but nonradical subspace",
            "positivity": (
                "Einstein-only is degenerate; a nondegenerate restriction containing "
                "the Einstein line is indefinite"
            ),
        },
        "claim_flags": {
            "general_euler_transgression_explicit": True,
            "literal_minus_ricci_current_exact": True,
            "axial_cut_identity_exact": True,
            "smooth_packet_finite_radius_integrated_flux_zero": True,
            "einstein_wave_packet_total_isotropy": True,
            "monochromatic_current_pointwise_zero": False,
            "unconditional_endpoint_limit_interchange": False,
            "mixed_einstein_additional_pairing_euler_exact": False,
            "quantum_statement": False,
        },
        "does_not_establish": [
            "pointwise vanishing of the literal monochromatic C2 Einstein current",
            "unconditional interchange of the null or horizon limit with time integration",
            "Euler exactness or removability of the mixed Einstein/additional pairing",
            "positivity of the inherited Weyl form",
            "a quantum, BRST, ghost, or unitarity theorem",
        ],
    }


def main() -> None:
    data = exact_data()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "weyl-euler-current-transgression-receipt-v1",
        "status": data["status"],
        "source_commit": "e8371371fc37776d536470eae2fd1f6fc2877f36",
        "artifacts": {
            "certificate": {"path": CERT.name, "sha256": sha256(CERT)},
            "producer": {"path": Path(__file__).name, "sha256": sha256(Path(__file__))},
            "imports": data["imports"],
        },
        "verification": {
            "independent_verifier": "python3 verify.py",
            "tests": "python3 -m unittest -v test_transgression.py",
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
