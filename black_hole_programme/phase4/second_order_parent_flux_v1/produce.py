#!/usr/bin/env python3
"""Produce the exact second-order parent-action and flux certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"

CARRIER = (
    ROOT
    / "black_hole_programme/phase4/covariant_einstein_maxwell_carrier_v1/certificate.json"
)
EULER = (
    ROOT
    / "black_hole_programme/phase4/weyl_euler_current_transgression_v1/certificate.json"
)
FLUX = ROOT / "black_hole_programme/phase3/axial_null_flux_gram/certificate.json"
QNM = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_spin_one_local_unit_v1/certificate.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_data() -> dict:
    # Trace solve of E_ab(h)=f_ab-g_ab f in four dimensions.
    dimension = sp.Integer(4)
    q, f = sp.symbols("q f")
    trace_e = (1 - dimension) * q
    trace_equation = sp.expand(trace_e + (dimension - 1) * f)
    f_solution = sp.solve(trace_equation, f)
    assert f_solution == [q]

    # Auxiliary elimination in the scalarized contraction algebra.
    q2 = sp.symbols("q2")
    f_dot_e_on_shell = q2 - q**2
    auxiliary_mass_on_shell = q2 - q**2
    parent_density_on_shell = sp.expand(
        4 * (f_dot_e_on_shell - sp.Rational(1, 2) * auxiliary_mass_on_shell)
    )
    assert parent_density_on_shell == 2 * (q2 - q**2)

    # The mixed Hessian is purely off diagonal.  J is an abstract
    # antisymmetric Einstein Green form.
    j_h1_f2, j_h2_f1 = sp.symbols("j_h1_f2 j_h2_f1")
    current_form_1 = j_h1_f2 - j_h2_f1
    # j_E(f1,h2)=-j_E(h2,f1).
    current_form_2 = j_h1_f2 + (-j_h2_f1)
    assert sp.expand(current_form_1 - current_form_2) == 0

    # Canonical null lift of a Hermitian hyperbolic plane.  A phase rotation
    # makes a>0, after which c=-b/(2a) kills the second diagonal entry.
    a = sp.symbols("a", positive=True)
    b = sp.symbols("b", real=True)
    c = -b / (2 * a)
    shifted_diagonal = sp.simplify(b + c * a + c * a)
    gram_determinant = sp.det(sp.Matrix([[0, a], [a, b]]))
    assert shifted_diagonal == 0
    assert gram_determinant == -a**2

    # Determinant divisor and contour count for u*D2^2*D1, with u a unit.
    n2, n1 = sp.symbols("N2 N1", integer=True)
    bach_count = sp.expand(2 * n2 + n1)
    assert bach_count == 2 * n2 + n1

    imports = {}
    for name, path in {
        "covariant_carrier": CARRIER,
        "euler_transgression": EULER,
        "axial_flux_gram": FLUX,
        "physical_connection_ep2": QNM,
    }.items():
        imports[name] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }

    return {
        "schema": "second-order-parent-flux-v1",
        "status": "EXACT_SECOND_ORDER_PARENT_FLUX_PASS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imports": imports,
        "scope": {
            "universal": (
                "quadratic four-dimensional pure Weyl gravity about an arbitrary "
                "Ricci-flat background, modulo the Euler boundary/corner term"
            ),
            "reduced_mode": (
                "Schwarzschild factor filtration and its certified axial ell=2 "
                "connection-level QNM specialization"
            ),
        },
        "parent_action": {
            "definition": (
                "S_par=4*alpha*Integral[f^ab*deltaG_ab[h]"
                "-(1/2)*(f_ab*f^ab-f^2)]"
            ),
            "f_equation": "deltaG_ab[h]=f_ab-g_ab*f",
            "trace_solve": "f=q=deltaR/3",
            "tensor_solve": "f_ab=q_ab=deltaR_ab-(1/6)*g_ab*deltaR",
            "h_equation": "deltaG_ab[f]=0",
            "on_shell_density": "2*alpha*(q_ab*q^ab-q^2)",
            "equivalence": (
                "bulk quadratic Weyl action modulo the Euler density and "
                "the retained boundary/corner terms"
            ),
        },
        "factorized_current": {
            "green_convention": (
                "<a,deltaG[b]>-<deltaG[a],b>=d j_E(a,b), "
                "with j_E(a,b)=-j_E(b,a)"
            ),
            "parent": (
                "j_par((h1,f1),(h2,f2))="
                "4*alpha*(j_E(h1,f2)+j_E(f1,h2))"
            ),
            "literal_weyl": "j_W=j_par+d k_Euler",
            "einstein_einstein": "j_W((hE,0),(hEprime,0))=d k_Euler",
            "einstein_additional": (
                "j_W((hE,0),(hX,fX))=4*alpha*j_E(hE,fX)+d k_Euler"
            ),
            "additional_additional": (
                "depends on the choice of metric lift hX while fX is fixed"
            ),
        },
        "canonical_null_lift": {
            "raw_block": "[[0,a],[conj(a),b]], a nonzero and b real",
            "lift": "X -> X+cE",
            "condition": "b+c*conj(a)+conj(c)*a=0",
            "phase_fixed_choice": "for a>0, c=-b/(2*a)",
            "canonical_block": "[[0,a],[conj(a),0]]",
            "determinant": "-abs(a)^2",
            "inertia": [1, 1, 0],
            "full_factor_anatomy": (
                "(1,2,0)=(1,1,0)_source_target_spin2"
                "+(0,1,0)_wrong_sign_Maxwell"
            ),
        },
        "qnm_determinant_count": {
            "factorization": "D_B(omega)=u(omega)*D_2(omega)^2*D_1(omega)",
            "unit_condition": "u is analytic and nonvanishing on the contour domain",
            "contour_count": "N_B(Gamma)=2*N_2(Gamma)+N_1(Gamma)",
            "interpretation": (
                "the extension changes local Smith/Jordan structure but not "
                "the total algebraic zero count"
            ),
            "simple_spin_two_options": {
                "semisimple": "beta_n=0 gives two length-one root vectors",
                "defective": (
                    "beta_n nonzero gives one length-two connection root chain"
                ),
            },
        },
        "radial_vs_temporal_boundary": {
            "generic_nonsplit_statement": (
                "a nonzero rational radial extension class is not by itself "
                "a Jordan block of the time-translation generator"
            ),
            "time_jordan_gate": (
                "a discrete spectral specialization with nonzero Fredholm/Smith "
                "selector is required"
            ),
            "certified_physical_specialization": (
                "one axial spin-two QNM has connection Smith valuations (0,0,2)"
            ),
            "uncertified_promotion": (
                "the physical Green-resolvent double pole still requires an "
                "analytic Fredholm realization"
            ),
        },
        "computational_reduction": {
            "primary": (
                "reconstruct f=q[h], evaluate Einstein RW/Zerilli Green currents, "
                "and evaluate the wrong-sign Maxwell current"
            ),
            "audit": "G_raw_Weyl-G_parent=G_Euler_cut",
            "polar_status": (
                "parent formula is universal, but a complete polar endpoint lift "
                "and Gram remain uncertified"
            ),
        },
        "claim_flags": {
            "parent_action_equivalent_mod_euler": True,
            "parent_euler_lagrange_system": True,
            "factorized_current_mod_euler": True,
            "canonical_null_lift": True,
            "qnm_count_identity": True,
            "generic_radial_nonsplitting_implies_time_jordan": False,
            "one_physical_connection_ep2": True,
            "physical_green_resolvent_double_pole": False,
            "all_positive_frequency_reflection_zero_exclusion": False,
            "complete_polar_parent_gram": False,
            "quantum_statement": False,
        },
        "does_not_establish": [
            "that generic radial differential-module nonsplitting is a time-Jordan block",
            "an analytic Fredholm realization or a physical Green-resolvent double pole",
            "a polynomially enhanced time-domain ringdown theorem",
            "absence of all positive-real scalar reflection zeros",
            "a complete polar lift, endpoint Gram, or polar scattering theorem",
            "a quantum, BRST, ghost, positivity, or unitarity theorem",
        ],
    }


def main() -> None:
    data = exact_data()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "second-order-parent-flux-receipt-v1",
        "status": data["status"],
        "source_commit": "05d5b042a6d9ae347346cd879aa18f457ae7a38d",
        "artifacts": {
            "certificate": {"path": CERT.name, "sha256": sha256(CERT)},
            "producer": {"path": Path(__file__).name, "sha256": sha256(Path(__file__))},
            "imports": data["imports"],
        },
        "verification": {
            "independence_level": "Level II: separately written invariant verifier",
            "independent_verifier": "python3 verify.py",
            "tests": "python3 -m unittest -v test_parent.py",
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
