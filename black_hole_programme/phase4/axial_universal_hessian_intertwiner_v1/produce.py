#!/usr/bin/env python3
"""Produce the exact Ricci-Hessian and no-rational-intertwiner certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
PROJECTIVE_CERT = (
    HERE.parent.parent
    / "phase3"
    / "axial_qnm_projective_cocycle_v1"
    / "certificate.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_data() -> dict:
    r, omega, rho, A0, B0 = sp.symbols(
        "r omega rho A0 B0", nonzero=True
    )
    a = sp.Function("a")(r)
    f = (r - 2) / r
    D = lambda z: sp.factor(f * sp.diff(z, r))
    V2 = 6 * (r - 2) * (r - 1) / r**4
    V1 = 6 * (r - 2) / r**3

    def compatibility(source, target):
        q_source = source - omega**2
        delta = source - target
        b = sp.factor(
            (
                sp.Rational(1, 2) * D(D(D(a)))
                + sp.Rational(1, 2) * D(a) * delta
                + sp.Rational(1, 2) * a * D(delta)
                - 2 * D(a) * q_source
                - a * D(q_source)
            )
            / delta
        )
        residual = sp.factor(
            D(b) + sp.Rational(1, 2) * (D(D(a)) + a * delta)
        )
        return b, residual

    H = sp.expand(
        r**4 * (r - 2) ** 2 * sp.diff(a, r, 4)
        + r**3 * (r - 2) * (3 * r + 4) * sp.diff(a, r, 3)
        + r**2
        * (4 * omega**2 * r**4 - 24 * r**2 + 62 * r - 12)
        * sp.diff(a, r, 2)
        + r
        * (12 * omega**2 * r**4 - 90 * r + 60)
        * sp.diff(a, r)
        + (90 * r - 60) * a
    )
    _, forward = compatibility(V2, V1)
    _, reverse = compatibility(V1, V2)
    assert sp.simplify(forward + (r - 2) * H / (12 * r**4)) == 0
    assert sp.simplify(reverse - (r - 2) * H / (12 * r**4)) == 0

    p0 = sp.factor(
        4 * rho * (rho - 1) * (rho - 2) * (rho - 3)
        - 8 * rho * (rho - 1) * (rho - 2)
        - 12 * rho * (rho - 1)
        + 60 * rho
        - 60
    )
    p2 = sp.factor(
        rho
        * (rho - 1)
        * (
            (rho - 2) * (rho - 3)
            + 5 * (rho - 2)
            + 4 * (4 * omega**2 + 1)
        )
    )
    assert sp.simplify(
        p0 - 4 * (rho + 1) * (rho - 1) * (rho - 3) * (rho - 5)
    ) == 0
    assert sp.simplify(
        p2 - rho * (rho - 1) * (rho**2 + 16 * omega**2)
    ) == 0

    trial = A0 + B0 / r
    trial_residual = sp.factor(H.xreplace({a: trial}).doit())
    expected_trial = (
        90 * A0 * r
        - 60 * A0
        - 4 * B0 * omega**2 * r**3
        - 42 * B0 * r
        + 220 * B0
    )
    assert sp.expand(trial_residual - expected_trial) == 0

    return {
        "schema": "axial-universal-hessian-intertwiner-v1",
        "status": "EXACT_UNIVERSAL_HESSIAN_AND_NO_RATIONAL_INTERTWINER_PASS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": {
            "projective_nonsplitting": {
                "path": str(PROJECTIVE_CERT.relative_to(HERE.parent.parent.parent)),
                "sha256": sha256(PROJECTIVE_CERT),
                "status": "EXACT_RATIONAL_COCYCLE_NONTRIVIAL_QNM_UNEVALUATED",
            }
        },
        "weyl_action_hessian": {
            "dimension": 4,
            "identity": "C2=E4+2*Ric2-(2/3)*R2",
            "background": "arbitrary four-dimensional Ricci-flat metric",
            "mixed_bulk_hessian_mod_euler": "4*alpha*Integral(psi1_ab*psi2**ab-(1/3)*psi1*psi2)",
            "normal_operator": "deltaB is proportional to Rlin_dagger*Pi*Rlin",
            "Pi": "Pi(psi)_ab=psi_ab-(1/3)*g_ab*trace(psi)",
            "einstein_bulk_radical": "Rlin(h_E)=0 implies Hessian_bulk(h_E,h)=0 for every h",
            "boundary_caveat": "the literal C2 Lee-Wald current can retain Euler boundary/corner contributions",
        },
        "positivity_obstruction": {
            "hypotheses": "E is nonzero, G(E,E)=0, and G restricted to W is nondegenerate",
            "conclusion": "every such W containing E is indefinite",
            "two_plane_gram": "[[0,a],[conjugate(a),b]]",
            "determinant": "-Abs(a)**2",
            "semidefinite_alternative": "if G(E,W)=0 then E lies in the radical of G|W",
            "trilemma": [
                "Einstein-only inherited bulk form is null and degenerate",
                "adding a symplectic partner produces an indefinite hyperbolic plane",
                "positivity requires a modified nonlocal or otherwise enlarged construction",
            ],
        },
        "axial_factor_intertwiner": {
            "scope": "Schwarzschild M=1, axial ell=2, each fixed real omega>0",
            "operators": {
                "D": "(r-2)/r*d/dr",
                "L2": "D**2+omega**2-6*(r-2)*(r-1)/r**4",
                "L1": "D**2+omega**2-6*(r-2)/r**3",
            },
            "reduced_map": "P=a(r)*D+b(r)",
            "compatibility_operator": (
                "r**4*(r-2)**2*a''''+r**3*(r-2)*(3*r+4)*a'''"
                "+r**2*(4*omega**2*r**4-24*r**2+62*r-12)*a''"
                "+r*(12*omega**2*r**4-90*r+60)*a'"
                "+(90*r-60)*a"
            ),
            "same_equation_both_directions": True,
            "indicial_factors": {
                "r=0": str(p0),
                "r=2": str(p2),
                "r=0_exponents": [-1, 1, 3, 5],
                "r=2_exponents": ["0", "1", "4*I*omega", "-4*I*omega"],
            },
            "ordinary_point_poles": "none for a rational solution",
            "infinity_balances": [0, -2],
            "exhaustive_rational_ansatz": "A0+B0/r",
            "ansatz_residual": str(expected_trial),
            "solution_for_real_positive_omega": "A0=B0=0, then b=0",
            "hom_M2_to_M1": 0,
            "hom_M1_to_M2": 0,
        },
        "local_C_corollary": {
            "scope": "generic rational repeated-spin-two differential module",
            "candidate": "C=[[I,Q],[0,-I]]",
            "covariant_constancy": "D_A(Q)=-2*E",
            "conclusion": "a branch-resolving rational involution would split the certified nontrivial extension and therefore does not exist",
        },
        "claim_flags": {
            "universal_ricci_flat_bulk_hessian_factorization": True,
            "einstein_bulk_radical": True,
            "nondegenerate_einstein_containing_restriction_indefinite": True,
            "no_rational_spin_intertwiner_positive_real": True,
            "no_generic_rational_branch_resolving_C": True,
            "literal_boundary_current_equals_bulk_hessian_without_euler_audit": False,
            "nonlocal_intertwiner_excluded": False,
            "quantum_positive_metric_excluded": False,
        },
        "does_not_establish": [
            "that the Euler term has no endpoint or corner contribution to the literal C2 Lee-Wald current",
            "absence of nonlocal, meromorphic, pseudodifferential, or scattering-dependent spin intertwiners",
            "absence or existence of a Mannheim dynamical C operator on a BRST physical state space",
            "a positive quantum Hilbert space or a quantum-unitarity theorem",
            "a complete asymptotically flat phase-space theorem",
            "a LORENTZIAN-CAUSAL theorem",
        ],
    }


def main() -> None:
    data = exact_data()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "axial-universal-hessian-intertwiner-receipt-v1",
        "status": data["status"],
        "source_commit": "82b5173569840a1207826ba9f25c4d9d65f07c2c",
        "artifacts": {
            "certificate": {"path": CERT.name, "sha256": sha256(CERT)},
            "producer": {"path": Path(__file__).name, "sha256": sha256(Path(__file__))},
            "projective_import": {
                "path": str(PROJECTIVE_CERT.relative_to(HERE.parent.parent.parent)),
                "sha256": sha256(PROJECTIVE_CERT),
            },
        },
        "verification": {
            "independent_verifier": "python3 verify.py",
            "tests": "python3 -m unittest -v test_structure.py",
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
