#!/usr/bin/env python3
"""Produce the exact covariant Einstein--Maxwell carrier certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
FILTRATION = ROOT / "black_hole_programme/phase3/axial_rw_lx_triangular_preflight/certificate.json"
FLUX = ROOT / "black_hole_programme/phase3/axial_null_flux_gram/certificate.json"
HESSIAN = ROOT / "black_hole_programme/phase4/axial_universal_hessian_intertwiner_v1/certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_data() -> dict:
    d = sp.Integer(4)
    c = sp.Rational(1, 6)
    q_trace_factor = sp.simplify(1 - d * c)
    q_divergence_factor = sp.simplify(sp.Rational(1, 2) - c)
    assert q_trace_factor == sp.Rational(1, 3)
    assert q_divergence_factor == q_trace_factor

    # -delta G[q] under div(q)=d trace(q):
    # 1/2 Box q_ab + Riemann*q - 1/2 Hessian(trace q).
    bach_coefficients = {
        "Box_psi_ab": sp.Rational(1, 2),
        "Riemann_psi": sp.Integer(1),
        "Hessian_psi": -sp.Rational(1, 2) * q_trace_factor,
        "g_ab_Box_psi": -sp.Rational(1, 2) * c,
    }
    assert bach_coefficients == {
        "Box_psi_ab": sp.Rational(1, 2),
        "Riemann_psi": sp.Integer(1),
        "Hessian_psi": -sp.Rational(1, 6),
        "g_ab_Box_psi": -sp.Rational(1, 12),
    }

    # Source Weyl perturbation h_ab=Phi g_ab.
    weyl_hessian_coefficient = -sp.Integer(1)
    weyl_gbox_coefficient = -sp.Rational(1, 2) - c * (-sp.Integer(3))
    assert weyl_gbox_coefficient == 0

    # Invert q_ab=psi_ab-g_ab psi/6 using tau=tr(q)=psi/3.
    tau = sp.symbols("tau")
    qnorm = sp.symbols("qnorm")
    psi_norm = qnorm + 2 * tau**2
    psi_trace = 3 * tau
    carrier_quadratic = sp.expand(psi_norm - psi_trace**2 / 3)
    assert carrier_quadratic == qnorm - tau**2

    # Exact first-jet contraction in Lorentz signature.
    eta = sp.diag(-1, 1, 1, 1)
    A = sp.Matrix(4, 4, lambda i, j: sp.symbols(f"A{i}{j}"))
    q = A + A.T
    F = A - A.T

    def norm2(tensor: sp.Matrix) -> sp.Expr:
        raised = eta * tensor * eta
        return sp.expand(
            sum(tensor[i, j] * raised[i, j] for i in range(4) for j in range(4))
        )

    divergence_eta = sp.expand(sum(eta[i, i] * A[i, i] for i in range(4)))
    cross = sp.expand(
        sum(
            A[i, j] * (eta[j, j] * eta[i, i] * A[j, i])
            for i in range(4)
            for j in range(4)
        )
    )
    lhs_minus_f2 = sp.expand(norm2(q) - (2 * divergence_eta) ** 2 - norm2(F))
    divergence_reduced = sp.expand(4 * (cross - divergence_eta**2))
    assert sp.simplify(lhs_minus_f2 - divergence_reduced) == 0

    imports = {}
    for name, path in {
        "axial_filtration": FILTRATION,
        "axial_flux": FLUX,
        "universal_hessian": HESSIAN,
    }.items():
        imports[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }

    return {
        "schema": "covariant-einstein-maxwell-carrier-v1",
        "status": "EXACT_SCHOUTEN_EINSTEIN_MAXWELL_CARRIER_PASS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "scope": {
            "universal": "linearized four-dimensional pure Weyl gravity about an arbitrary Ricci-flat background",
            "axial_realization": "certified Schwarzschild M=1 axial ell=2 factor filtration",
        },
        "schouten_carrier": {
            "definition": "q_ab=deltaR_ab-(1/6)*g_ab*deltaR",
            "trace": "q=deltaR/3",
            "divergence": "nabla^a q_ab=nabla_b q",
            "kernel_equivalence": "q[h]=0 iff deltaR_ab[h]=0",
            "factorization": "deltaB_ab[h]=-deltaG_ab[q[h]]",
            "expanded_coefficient_basis": {
                key: str(value) for key, value in bach_coefficients.items()
            },
            "exact_sequence": "0 -> H_E -> H_B -> K -> 0",
            "target": "K={q: deltaG[q]=0, div(q)=d trace(q)} intersect image(Q)",
        },
        "target_gauge_maxwell": {
            "target_gauge": "q_ab=L_eta g_ab=nabla_a eta_b+nabla_b eta_a",
            "constraint": "Box eta_b-nabla_b div(eta)=0",
            "field_strength": "F_ab=2*nabla_[a eta_b]",
            "equation": "nabla^a F_ab=0",
            "interpretation": "pure gauge for target Einstein equation, not pure gauge for source Weyl perturbation h",
        },
        "source_weyl_to_maxwell_gauge": {
            "source_shift": "h_ab -> h_ab+Phi*g_ab",
            "deltaRic": "-Hessian(Phi)-(1/2)*g*Box(Phi)",
            "deltaR": "-3*Box(Phi)",
            "q_shift": "-Hessian(Phi)=L_{-(1/2)dPhi}g",
            "eta_shift": "eta -> eta-(1/2)dPhi",
            "F_invariant": True,
        },
        "quadratic_action": {
            "bulk_mod_euler": "2*alpha*Integral(deltaRic_ab*deltaRic**ab-(1/3)*deltaR**2)",
            "q_form": "2*alpha*Integral(q_ab*q**ab-trace(q)**2)",
            "pure_target_gauge_identity": (
                "q_ab*q**ab-trace(q)**2=F_ab*F**ab"
                "+4*nabla_a(eta_b*nabla^b eta^a-eta^a*div(eta))"
            ),
            "spin_one_bulk_action": "2*alpha*Integral(F_ab*F**ab)",
            "maxwell_convention": "S_Maxwell=-(1/4)*Integral(F_ab*F**ab)",
            "relative_sign": "S_spin1=-8*alpha*S_Maxwell modulo boundary terms",
        },
        "axial_associated_graded": {
            "factors": [
                "source Einstein kernel: spin-two Regge-Wheeler",
                "target physical Einstein carrier: spin-two Regge-Wheeler",
                "target Einstein gauge vector: spin-one Maxwell Regge-Wheeler",
            ],
            "signature_anatomy": "(1,2,0)=(1,1,0)_spin2_hyperbolic plus (0,1,0)_wrong_sign_Maxwell",
            "spin_one_potential_l2": "6*(r-2)/r**3",
        },
        "general_ell_prediction": {
            "status": "PREDICTED_NOT_CERTIFIED",
            "spin_two_potential": "B*(ell*(ell+1)/r**2-6*M/r**3)",
            "spin_one_potential": "B*ell*(ell+1)/r**2",
            "open_gate": "all-row image/lift and extension theorem for each ell",
        },
        "claim_flags": {
            "schouten_einstein_factorization": True,
            "carrier_constraint": True,
            "target_gauge_maxwell_equation": True,
            "source_weyl_becomes_maxwell_gauge": True,
            "wrong_sign_maxwell_bulk_action_mod_boundary": True,
            "axial_l2_spin_one_geometric_identification": True,
            "all_ell_lift_certified": False,
            "complete_polar_phase_space_certified": False,
            "quantum_ghost_or_unitarity_statement": False,
        },
        "does_not_establish": [
            "that target Einstein gauge is gauge-trivial in the original Weyl perturbation",
            "the all-ell image/lift theorem or all-ell non-split extension",
            "a complete polar phase-space or polar scattering theorem",
            "that Euler and divergence boundary terms vanish for every endpoint phase space",
            "a particle, BRST physical-state, quantum ghost, positivity, or unitarity theorem",
            "a global Mannheim C operator",
        ],
    }


def main() -> None:
    data = exact_data()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "covariant-einstein-maxwell-carrier-receipt-v1",
        "status": data["status"],
        "source_commit": "d1a17090f9730ec30fe3dd813dd39ac3bc1338aa",
        "artifacts": {
            "certificate": {"path": CERT.name, "sha256": sha256(CERT)},
            "producer": {"path": Path(__file__).name, "sha256": sha256(Path(__file__))},
            "imports": data["imports"],
        },
        "verification": {
            "independent_verifier": "python3 verify.py",
            "tests": "python3 -m unittest -v test_carrier.py",
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
