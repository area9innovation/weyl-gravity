#!/usr/bin/env python3
"""Produce the exact local-DVR axial QNM Smith-dichotomy certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(sp.cancel(value)))


def matrix_strings(value: sp.Matrix) -> list[list[str]]:
    return [
        [encode(value[i, j]) for j in range(value.cols)]
        for i in range(value.rows)
    ]


def produce() -> dict:
    z = sp.Symbol("z")
    unit_a, unit_f = sp.symbols("u_a u_f", nonzero=True)
    b0, b1, g0 = sp.symbols("b_0 b_1 g_0")
    c0, d0 = sp.symbols("c_0 d_0")

    a = unit_a * z
    f = unit_f
    b_unit = b0 + b1 * z
    b_divisible = a * g0
    generic = sp.Matrix([
        [a, b_unit, c0],
        [0, a, d0],
        [0, 0, f],
    ])
    eliminate_third = sp.Matrix([
        [1, 0, -c0 / f],
        [0, 1, -d0 / f],
        [0, 0, 1],
    ])
    reduced = sp.simplify(eliminate_third * generic)
    expected_reduced = sp.Matrix([
        [a, b_unit, 0],
        [0, a, 0],
        [0, 0, f],
    ])
    if reduced != expected_reduced:
        raise RuntimeError("unit spin-one elimination identity failed")

    spin_two_unit = sp.Matrix([[a, b_unit], [0, a]])
    spin_two_divisible = sp.Matrix([[a, b_divisible], [0, a]])
    inverse_unit = sp.simplify(spin_two_unit.inv())
    inverse_divisible = sp.simplify(spin_two_divisible.inv())

    # Local-DVR valuation data.  At a simple zero, a is a uniformizer.
    # In the first branch b0 is declared nonzero; in the second b=a*g.
    unit_min_entry_valuation = 0
    divisible_min_entry_valuation = 1
    determinant_valuation = 2
    unit_pair = [
        unit_min_entry_valuation,
        determinant_valuation - unit_min_entry_valuation,
    ]
    divisible_pair = [
        divisible_min_entry_valuation,
        determinant_valuation - divisible_min_entry_valuation,
    ]

    # Finite normal-form model of the Fredholm pairing.  L has one-dimensional
    # kernel/cokernel, with right and left germs e_1.  The commutator ambiguity
    # has identically zero (1,1) matrix element.
    lam = sp.Symbol("lambda_q", nonzero=True)
    q11, q12, q21, q22 = sp.symbols("q_11 q_12 q_21 q_22")
    e11, e12, e21, e22 = sp.symbols("e_11 e_12 e_21 e_22")
    L = sp.diag(0, lam)
    Q = sp.Matrix([[q11, q12], [q21, q22]])
    extension = sp.Matrix([[e11, e12], [e21, e22]])
    right = sp.Matrix([1, 0])
    left = sp.Matrix([[1, 0]])
    commutator = L * Q - Q * L
    beta = (left * extension * right)[0]
    beta_shift = sp.simplify(
        (left * (extension + commutator) * right)[0] - beta
    )
    if beta_shift != 0:
        raise RuntimeError("Fredholm commutator invariance failed")

    document = {
        "schema": "phase3-axial-qnm-local-smith-dichotomy-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "EXACT_DICHOTOMY_BETA_UNEVALUATED",
        "scope": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2",
            "time_phase": "exp(+I*omega*t)",
            "damped_QNM_half_plane": "Im(omega)>0",
            "local_ring": (
                "analytic germs O_{omega_n}, a DVR at a simple zero "
                "z=omega-omega_n"
            ),
        },
        "hypotheses": {
            "connection": "T=[[a,b,c],[0,a,d],[0,0,f]]",
            "simple_spin_two_zero": (
                "a(omega_n)=0 and a'(omega_n)!=0"
            ),
            "noncoincident_spin_one_factor": "f(omega_n)!=0",
            "equivalence": (
                "invertible analytic row and column transformations "
                "preserving the local connection problem"
            ),
        },
        "spin_one_elimination": {
            "left_matrix": matrix_strings(eliminate_third),
            "input_matrix": matrix_strings(generic),
            "output_matrix": matrix_strings(reduced),
            "identity_verified": True,
            "conclusion": (
                "Because f is a local unit, c and d are eliminated exactly; "
                "the Smith question reduces to [[a,b],[0,a]]."
            ),
        },
        "local_dvr_proof": {
            "uniformizer_model": "a=u_a*z with u_a a unit",
            "determinant_valuation": determinant_valuation,
            "valuation_rule": (
                "For a 2x2 full-rank matrix over a DVR, the first Smith "
                "valuation is the minimum valuation of its entries and the "
                "second is determinant valuation minus the first."
            ),
            "nonzero_class_case": {
                "condition": "[b]!=0 in O/(a), equivalently ord(b)=0",
                "spin_two_pair_valuations": unit_pair,
                "factor_ordered_full_valuations": [0, 2, 0],
                "sorted_full_smith_valuations": [0, 0, 2],
                "geometric_multiplicity": 1,
                "algebraic_multiplicity": 2,
                "resonance_structure": "one length-two root chain",
                "inverse_matrix": matrix_strings(inverse_unit),
                "double_pole_entry": "-b/a**2",
                "time_domain_term": "t*exp(+I*omega_n*t)",
            },
            "zero_class_case": {
                "condition": "[b]=0 in O/(a), equivalently b=a*g",
                "spin_two_pair_valuations": divisible_pair,
                "factor_ordered_full_valuations": [1, 1, 0],
                "sorted_full_smith_valuations": [0, 1, 1],
                "geometric_multiplicity": 2,
                "algebraic_multiplicity": 2,
                "resonance_structure": "two independent simple root vectors",
                "inverse_matrix": matrix_strings(inverse_divisible),
                "pole_order": 1,
            },
            "frame_law": "b -> u*b+a*h with u in O^times and h in O",
            "invariant_class": "[b] in O/(a), defined up to a unit",
        },
        "fredholm_invariant": {
            "definition": (
                "beta_n=<u_n^#, E(omega_n) u_n> for normalized right "
                "QNM germ u_n and adjoint cokernel germ u_n^#"
            ),
            "derivative_pairing": (
                "alpha_n=<u_n^#, d_omega L(omega_n) u_n> != 0 "
                "at a simple QNM"
            ),
            "normalized_coupling": "kappa_n=beta_n/alpha_n",
            "equivalence": (
                "[b]!=0 iff beta_n!=0, after compatible endpoint and "
                "left/right germ normalizations"
            ),
            "gauge_law": "E -> E+L*Q-Q*L",
            "gauge_invariance_identity": (
                "<u#,L*Q*u>-<u#,Q*L*u>=0"
            ),
            "finite_normal_form": {
                "L": matrix_strings(L),
                "Q": matrix_strings(Q),
                "E": matrix_strings(extension),
                "right_germ": ["1", "0"],
                "left_germ": ["1", "0"],
                "beta": encode(beta),
                "commutator": matrix_strings(commutator),
                "beta_shift": encode(beta_shift),
            },
        },
        "boundary": {
            "beta_n_evaluated": False,
            "smith_case_selected_for_any_QNM": False,
            "missing": [
                "a certified simple damped spin-two QNM germ",
                "a compatible normalized adjoint QNM cokernel germ",
                "a boundary-convergent or regularized Fredholm pairing",
                "an exact or validated evaluation of beta_n",
            ],
            "does_not_establish": [
                "that beta_n is nonzero at any QNM",
                "that any doubled determinant zero is a double resolvent pole",
                "an all-overtone generalized-resonance theorem",
                "time-domain stability or boundedness",
            ],
        },
        "claim_flags": {
            "spin_one_unit_elimination_exact": True,
            "local_smith_dichotomy_exact": True,
            "fredholm_commutator_invariance_exact": True,
            "beta_n_evaluated": False,
            "simple_QNM_smith_case_selected": False,
            "double_resolvent_pole_established": False,
        },
        "provenance": {
            "producer": "produce.py",
            "verifier": "verify.py",
            "schema": {
                "path": "schema.json",
                "sha256": sha256(SCHEMA),
            },
            "arithmetic": "exact SymPy rational/polynomial algebra",
            "external_scientific_inputs": [],
        },
    }
    return document


def main() -> None:
    OUTPUT.write_text(
        json.dumps(produce(), indent=2, sort_keys=True) + "\n"
    )
    print(f"wrote={OUTPUT}")


if __name__ == "__main__":
    main()
