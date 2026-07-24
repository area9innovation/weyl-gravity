#!/usr/bin/env python3
"""Produce the exact all-ell Regge--Wheeler threshold certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
L2_THRESHOLD = (
    ROOT / "black_hole_programme/phase4/axial_threshold_exact_structure_v1/certificate.json"
)
CARRIER = (
    ROOT
    / "black_hole_programme/phase4/covariant_einstein_maxwell_carrier_v1/certificate.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def static_solution(ell: int, spin: int, r: sp.Symbol) -> sp.Expr:
    prefactor = sp.factorial(2 * ell) / (
        2 ** (ell + 1)
        * sp.factorial(ell - spin)
        * sp.factorial(ell + spin)
    )
    return sp.factor(
        sp.hyperexpand(
            prefactor
            * r ** (ell + 1)
            * sp.hyper(
                [spin - ell, -spin - ell],
                [-2 * ell],
                2 / r,
            )
        )
    )


def exact_data() -> dict:
    r = sp.symbols("r", positive=True)

    # Exact independent spot checks across several harmonics.  The all-ell
    # proof recorded below is the terminating hypergeometric recurrence.
    samples = {}
    for ell in range(2, 9):
        samples[str(ell)] = {}
        for spin in (1, 2):
            y = static_solution(ell, spin, r)
            blackening = 1 - 2 / r
            potential = blackening * (
                ell * (ell + 1) / r**2 + 2 * (1 - spin**2) / r**3
            )
            d_y = blackening * sp.diff(y, r)
            residual = sp.cancel(blackening * sp.diff(d_y, r) - potential * y)
            assert residual == 0
            assert sp.simplify(y.subs(r, 2)) == 1
            lead = sp.simplify(sp.limit(y / r ** (ell + 1), r, sp.oo))
            expected = sp.factorial(2 * ell) / (
                2 ** (ell + 1)
                * sp.factorial(ell - spin)
                * sp.factorial(ell + spin)
            )
            assert lead == expected
            samples[str(ell)][str(spin)] = {
                "horizon_value": "1",
                "infinity_leading_coefficient": str(lead),
            }

    # Explicit ell=2 controls.
    assert static_solution(2, 2, r) == r**3 / 8
    assert static_solution(2, 1, r) == r**2 * (2 * r - 3) / 4

    imports = {}
    for name, path in {
        "ell2_threshold": L2_THRESHOLD,
        "covariant_carrier": CARRIER,
    }.items():
        imports[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }

    return {
        "schema": "axial-all-ell-threshold-structure-v1",
        "status": "EXACT_ALL_ELL_THRESHOLD_NONRESONANCE_PASS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "mass": "M=1",
            "spins": [1, 2],
            "harmonics": "every integer ell>=2",
            "frequency": "omega=0 exact scalar diagonal factors",
        },
        "operator": {
            "D": "(1-2/r)*d/dr",
            "potential": (
                "V_s_ell=(1-2/r)*(ell*(ell+1)/r**2"
                "+2*(1-s**2)/r**3)"
            ),
            "equation": "(D**2-V_s_ell)*phi=0",
        },
        "regular_solution": {
            "formula": (
                "phi_s_ell=(2ell)!*r**(ell+1)"
                "/(2**(ell+1)*(ell-s)!*(ell+s)!)"
                "*2F1(s-ell,-s-ell;-2ell;2/r)"
            ),
            "termination": "s-ell is a nonpositive integer",
            "horizon_normalization": "phi_s_ell(2)=1 by Chu-Vandermonde",
            "infinity": (
                "phi_s_ell~C_s_ell*r**(ell+1), "
                "C_s_ell=(2ell)!/(2**(ell+1)*(ell-s)!*(ell+s)!)"
            ),
            "all_ell_proof": (
                "substitution z=2/r reduces the static equation to the "
                "Gauss hypergeometric equation with "
                "a=s-ell, b=-s-ell, c=-2ell"
            ),
            "ell2_controls": {
                "spin2": "r**3/8",
                "spin1": "r**2*(2*r-3)/4",
            },
        },
        "second_solution": {
            "formula": (
                "phi_tilde=phi*Integral[dr/((1-2/r)*phi**2)]"
            ),
            "horizon": "logarithmically singular because phi(2)=1",
            "infinity_normalization": "a decaying choice behaves as r**(-ell)",
            "conclusion": (
                "no nonzero solution is both horizon regular and bounded/"
                "decaying at infinity"
            ),
        },
        "formal_low_frequency_matching": {
            "status": "FORMAL_NOT_CERTIFIED_SCATTERING",
            "leading_coefficient": (
                "kappa_s_ell=(2ell)!*(2ell+1)!!"
                "/(2**(ell+2)*(ell-s)!*(ell+s)!)"
            ),
            "jost_prediction": (
                "|A_in|~|A_out|~kappa_s_ell*omega**(-(ell+1))"
            ),
            "absorption_prediction": (
                "Gamma_s_ell~kappa_s_ell**(-2)*omega**(2ell+2)"
            ),
            "required_gate": (
                "uniform two-region Volterra estimate controlling the "
                "difference from the far Riccati-Hankel problem"
            ),
        },
        "sample_checks": samples,
        "imports": imports,
        "claim_flags": {
            "all_ell_exact_static_solution": True,
            "all_ell_no_zero_energy_resonance": True,
            "ell2_controls_recovered": True,
            "uniform_low_frequency_jost_asymptotics": False,
            "punctured_threshold_outgoing_invertibility": False,
            "all_ell_bach_lift": False,
            "all_ell_endpoint_gram": False,
        },
        "does_not_establish": [
            "uniform low-frequency Jost asymptotics",
            "a punctured positive-real interval of outgoing invertibility",
            "the omega=0 scattering map itself",
            "the complete all-ell Bach lift or extension shear",
            "an all-ell endpoint Gram, connection, or scattering theorem",
        ],
    }


def main() -> None:
    data = exact_data()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "axial-all-ell-threshold-structure-receipt-v1",
        "status": data["status"],
        "source_commit": "d51f5185044f938e9e348de6829bd000b0057d4f",
        "artifacts": {
            "certificate": {"path": CERT.name, "sha256": sha256(CERT)},
            "producer": {"path": Path(__file__).name, "sha256": sha256(Path(__file__))},
            "imports": data["imports"],
        },
        "verification": {
            "independent_verifier": "python3 verify.py",
            "tests": "python3 -m unittest -v test_threshold.py",
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
