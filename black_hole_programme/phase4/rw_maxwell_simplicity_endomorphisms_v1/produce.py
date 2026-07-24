#!/usr/bin/env python3
"""Produce the exact RW/Maxwell simplicity and endomorphism certificate."""

from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"

COCYCLE = (
    ROOT
    / "black_hole_programme/phase3/axial_qnm_projective_cocycle_v1/certificate.json"
)
PARENT = (
    ROOT
    / "black_hole_programme/phase4/parent_resolvent_krein_obstructions_v1/certificate.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_data() -> dict:
    r, omega, lam = sp.symbols("r omega Lambda", nonzero=True)
    rho = sp.symbols("rho")
    sigma = sp.symbols("sigma")
    aa, bb = sp.symbols("A B")
    q0, q1, q2 = sp.symbols("q0 q1 q2")
    f = (r - 2) / r

    def d(expr: sp.Expr) -> sp.Expr:
        return sp.factor(f * sp.diff(expr, r))

    v2 = f * (lam / r**2 - 6 / r**3)
    v1 = f * lam / r**2
    u2 = omega**2 - v2
    u1 = omega**2 - v1

    # After y=exp(sigma*i*omega*rstar) F, sigma^2=1, the scalar
    # equation is D^2 F+2 sigma i omega D F-V F=0.
    prefactor = aa + bb / r
    residual2 = sp.factor(
        d(d(prefactor)) + 2 * sigma * sp.I * omega * d(prefactor) - v2 * prefactor
    )
    expected2 = -sp.I * (r - 2) / r**4 * (
        (-sp.I * lam * aa + 2 * sigma * omega * bb) * r
        + sp.I * (6 * aa + (2 - lam) * bb)
    )
    assert sp.simplify(residual2 - expected2) == 0

    b_as = 6 * aa / (lam - 2)
    omega_as = sigma * sp.I * lam * (lam - 2) / 12
    as_residual = sp.factor(
        residual2.subs(bb, b_as).subs(omega, omega_as).subs(sigma**2, 1)
    )
    assert as_residual == 0

    # Maxwell has no r=0 pole, hence its exhaustive rational prefactor is
    # constant after the common Jost phase is removed.
    residual1_constant = sp.factor(-v1 * aa)
    assert residual1_constant != 0

    # The selected-frame events are imaginary and are outside the
    # positive-real sign argument. Audit them separately for ell=2, allowing
    # the opposite-sign rational horizon power.
    frame_event_audit = {}
    for event in (sp.Rational(1, 4), sp.Rational(1, 2), sp.Integer(1)):
        event_rows = {}
        event_omega = sp.I * event
        for sign in (1, -1):
            horizon_order = sp.simplify(-4 * sign * sp.I * event_omega)
            if horizon_order > 0:
                event_coefficients = sp.symbols(f"e{event}_{sign}_0:2")
                event_prefactor = (
                    event_coefficients[0] + event_coefficients[1] / r
                )
            else:
                pole_order = int(-horizon_order)
                event_coefficients = sp.symbols(
                    f"e{event}_{sign}_0:{pole_order + 2}"
                )
                polynomial = sum(
                    value * r**power
                    for power, value in enumerate(event_coefficients)
                )
                event_prefactor = polynomial / (
                    r * (r - 2) ** pole_order
                )
            event_residual = sp.together(
                d(d(event_prefactor))
                + 2 * sign * sp.I * event_omega * d(event_prefactor)
                - v2.subs(lam, 6) * event_prefactor
            )
            event_equations = sp.Poly(
                event_residual.as_numer_denom()[0], r
            ).all_coeffs()
            event_solution = sp.linsolve(event_equations, event_coefficients)
            zero_tuple = tuple(sp.Integer(0) for _ in event_coefficients)
            assert event_solution == sp.FiniteSet(zero_tuple)
            event_rows[str(sign)] = {
                "horizon_order_after_jost_factor": str(horizon_order),
                "ansatz": str(event_prefactor),
                "solution": "ZERO_ONLY",
            }
        frame_event_audit[str(event_omega)] = event_rows

    # Indicial polynomials obtained from the leading operators at r=0 and
    # r=2.  The symmetric-square polynomials are for K_U below.
    indicial = {
        "spin2_r0": sp.factor(4 * rho * (rho - 2) - 12),
        "maxwell_r0": sp.factor(4 * rho * (rho - 2)),
        "common_horizon": sp.factor(rho**2 / 4 + omega**2),
        "spin2_symmetric_square_r0": sp.factor(
            -8 * (rho + 2) * (rho - 2) * (rho - 6)
        ),
        "maxwell_symmetric_square_r0": sp.factor(
            -8 * rho * (rho - 2) * (rho - 4)
        ),
        "common_symmetric_square_horizon": sp.factor(
            rho * (rho**2 + 16 * omega**2) / 8
        ),
    }

    def k_u(u: sp.Expr, q: sp.Expr) -> sp.Expr:
        return sp.factor(d(d(d(q))) + 4 * u * d(q) + 2 * d(u) * q)

    q_spin2 = q0 + q1 / r + q2 / r**2
    k2 = sp.factor(k_u(u2, q_spin2))
    numerator2 = sp.Poly(sp.together(k2).as_numer_denom()[0], r)
    coeff = {degree[0]: sp.factor(value) for degree, value in numerator2.terms()}
    assert coeff[5] == -4 * omega**2 * q1
    assert sp.simplify(
        coeff[4].subs(q1, 0) - 4 * (lam * q0 - 2 * omega**2 * q2)
    ) == 0
    eliminated = sp.factor(
        coeff[3].subs({q1: 0, q2: lam * q0 / (2 * omega**2)})
    )
    assert sp.simplify(eliminated + 12 * (lam + 3) * q0) == 0
    assert sp.solve(list(numerator2.all_coeffs()), [q0, q1, q2], dict=True) == [
        {q0: 0, q1: 0, q2: 0}
    ]

    k1_constant = sp.factor(k_u(u1, q0))
    assert k1_constant == 4 * lam * q0 * (r - 3) * (r - 2) / r**5

    # Strengthen the imported generic cocycle result on the physical real
    # axis.  Fixed monomial minors avoid the old left-null witness zero at
    # omega^2=3.
    matrix = sp.Matrix(
        [
            [0, -4 * omega**4, 0],
            [-8 * omega**4, 8 * omega**4, 24 * omega**2],
            [16 * omega**4, 42 * omega**2, -156 * omega**2],
            [48 * omega**2, -224 * omega**2, 312 * omega**2],
            [-208 * omega**2, 364 * omega**2, -192 * omega**2],
            [224 * omega**2, -168 * omega**2, 0],
        ]
    )
    rhs = sp.Matrix(
        [
            0,
            -2 * sp.I * (5 * omega - 6 * sp.I),
            sp.I * (35 * omega - 78 * sp.I),
            -6 * sp.I * (5 * omega - 26 * sp.I),
            96,
            0,
        ]
    )
    augmented = matrix.row_join(rhs)
    coefficient_minor = sp.factor(matrix.extract((0, 1, 2), (0, 1, 2)).det())
    augmented_minor = sp.factor(
        augmented.extract((0, 1, 2, 5), (0, 1, 2, 3)).det()
    )
    assert coefficient_minor == 3456 * omega**10
    assert augmented_minor == -645120 * sp.I * omega**9

    # Retain gcds as an independent global audit of the chosen fixed minors.
    coefficient_minors = [
        sp.factor(matrix.extract(rows, range(3)).det())
        for rows in combinations(range(6), 3)
    ]
    augmented_minors = [
        sp.factor(augmented.extract(rows, range(4)).det())
        for rows in combinations(range(6), 4)
    ]
    coefficient_gcd = sp.factor(
        sp.polys.polytools.terms_gcd(
            sp.gcd_list([x for x in coefficient_minors if x != 0])
        )
    )
    augmented_gcd = sp.factor(
        sp.polys.polytools.terms_gcd(
            sp.gcd_list([x for x in augmented_minors if x != 0])
        )
    )
    assert coefficient_gcd == 384 * omega**6
    assert augmented_gcd == 15360 * omega**7

    imports = {
        "generic_projective_cocycle": {
            "path": str(COCYCLE.relative_to(ROOT)),
            "sha256": digest(COCYCLE),
        },
        "parent_involution_lemma": {
            "path": str(PARENT.relative_to(ROOT)),
            "sha256": digest(PARENT),
        },
    }

    return {
        "schema": "rw-maxwell-simplicity-endomorphisms-v1",
        "status": "EXACT_RW_MAXWELL_SIMPLICITY_ENDOMORPHISMS_PASS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "background": "Schwarzschild M=1",
            "field": "C(r) with omega specialized to a positive real number",
            "angular_range": "integer ell>=2, Lambda=ell*(ell+1)",
            "derivative": "D=((r-2)/r)*d/dr",
        },
        "imports": imports,
        "local_exhaustion": {
            "ordinary_points": (
                "a hyperexponential solution or rational symmetric-square "
                "solution has no poles at ordinary points"
            ),
            "horizon_sign_rule": (
                "opposite horizon and infinity Jost signs require a rational "
                "factor with exponent 4*i*omega; impossible for real omega!=0"
            ),
            "spin2_prefactor": "F=A+B/r",
            "maxwell_prefactor": "F=A",
            "spin2_endomorphism_ansatz": "q=q0+q1/r+q2/r^2",
            "maxwell_endomorphism_ansatz": "q=q0",
            "indicial_polynomials": {k: str(v) for k, v in indicial.items()},
            "spin2_exponents": {
                "r0": [-1, 3],
                "horizon": ["-2*I*omega", "2*I*omega"],
            },
            "maxwell_exponents": {
                "r0": [0, 2],
                "horizon": ["-2*I*omega", "2*I*omega"],
            },
            "spin2_symmetric_square_exponents": {
                "r0": [-2, 2, 6],
                "horizon": ["-4*I*omega", 0, "4*I*omega"],
            },
            "maxwell_symmetric_square_exponents": {
                "r0": [0, 2, 4],
                "horizon": ["-4*I*omega", 0, "4*I*omega"],
            },
        },
        "spin2_simplicity": {
            "operator": (
                "L_2=D^2+omega^2-f*(Lambda/r^2-6/r^3)"
            ),
            "conjugated_residual": str(expected2),
            "terminal_equations": [
                "-I*Lambda*A+2*sigma*omega*B=0",
                "6*A+(2-Lambda)*B=0",
            ],
            "algebraically_special_frequency": (
                "omega=sigma*I*Lambda*(Lambda-2)/12"
            ),
            "algebraically_special_prefactor": "F=1+6/((Lambda-2)*r)",
            "ell2_control": (
                "omega=2*sigma*I, F=1+3/(2*r)"
            ),
            "positive_real_conclusion": (
                "M_2,ell is simple over C(r)[D] for every real omega>0"
            ),
            "frame_event_note": (
                "the separate exhaustive ell=2 audit excludes rational "
                "reducibility at omega=I/4,I/2,I"
            ),
        },
        "ell2_frame_event_audit": {
            "frequencies": ["I/4", "I/2", "I"],
            "opposite_sign_horizon_order": "-4*sigma*I*omega",
            "results": frame_event_audit,
            "conclusion": (
                "the selected-frame events I/4,I/2,I are not rational "
                "reducibility points of the ell=2 spin-two module"
            ),
        },
        "maxwell_simplicity": {
            "operator": "L_1=D^2+omega^2-f*Lambda/r^2",
            "constant_prefactor_residual": str(residual1_constant),
            "positive_real_conclusion": (
                "M_1,ell is simple over C(r)[D] for every real omega>0"
            ),
        },
        "endomorphism_rings": {
            "projective_operator": "K_U=D^3+4*U*D+2*D(U)",
            "horizontal_trace_free_entries": {
                "a": "-D(q)/2",
                "c": "-D(D(q))/2-U*q",
            },
            "spin2_terminal_chain": [
                "-4*omega^2*q1=0",
                "4*(Lambda*q0-2*omega^2*q2)=0 after q1=0",
                "-12*(Lambda+3)*q0=0 after eliminating q2",
            ],
            "maxwell_constant_result": str(k1_constant),
            "conclusions": [
                "End_C(r)[D](M_2,ell)=C for ell>=2 and real omega>0",
                "End_C(r)[D](M_1,ell)=C for ell>=2 and real omega>0",
            ],
        },
        "positive_real_nonsplitting_refinement": {
            "sector": "axial ell=2 repeated spin-two Bach extension",
            "imported_ansatz_scope": (
                "the exhaustive projective-cocycle ansatz is valid for real "
                "omega>0; its apparent pole does not collide with the horizon"
            ),
            "coefficient_minor_rows_0_1_2": str(coefficient_minor),
            "augmented_minor_rows_0_1_2_5": str(augmented_minor),
            "coefficient_maximal_minor_gcd": str(coefficient_gcd),
            "augmented_maximal_minor_gcd": str(augmented_gcd),
            "rank_conclusion": "rank(M)=3 and rank([M|rhs])=4 for omega!=0",
            "omega_squared_3": (
                "nonsplit; the old left-null witness vanishes there but the "
                "fixed augmented minor remains nonzero"
            ),
            "conclusion": (
                "the axial ell=2 projective self-extension is nonsplit for "
                "every real omega>0"
            ),
        },
        "local_c_consequence": {
            "premises": [
                "M_2,2 is simple and End(M_2,2)=C for real omega>0",
                "the axial ell=2 Bach self-extension is nonsplit there",
                "the base field has characteristic zero",
            ],
            "endomorphism_form": "C=a*I+N with N^2=0",
            "involution_equations": "a^2=1 and 2*a*N=0",
            "conclusion": (
                "the only rational differential-module involutions on the "
                "axial ell=2 Bach spin-two block are +I and -I"
            ),
            "positivity_conclusion": (
                "no rational local dynamically compatible involution makes "
                "the hyperbolic spin-two Weyl form positive on omega>0"
            ),
        },
        "claim_flags": {
            "spin2_simple_all_ell_positive_real": True,
            "maxwell_simple_all_ell_positive_real": True,
            "spin2_endomorphism_ring_scalar_positive_real": True,
            "maxwell_endomorphism_ring_scalar_positive_real": True,
            "spin2_algebraically_special_controls_exact": True,
            "spin2_simple_at_algebraically_special_points": False,
            "axial_ell2_nonsplit_all_positive_real": True,
            "only_plus_minus_identity_axial_ell2_positive_real": True,
            "local_rational_positive_c_axial_ell2_exists": False,
            "nonlocal_c_excluded": False,
            "all_ell_bach_nonsplitting_established": False,
            "physical_qnm_smith_case_selected": False,
            "green_resolvent_double_pole_established": False,
            "quantum_statement": False,
        },
        "does_not_establish": [
            "simplicity at the algebraically special imaginary frequencies",
            "a complete classification of the complex-frequency reducibility locus",
            "an all-ell Bach lift or all-ell nonsplit self-extension",
            "absence of nonlocal, spectral, scattering-dependent, or BRST C operators",
            "a Smith type or nonzero overlap at a physical QNM",
            "a Green-resolvent double pole or generalized ringdown term",
            "a quantum positivity or unitarity theorem",
        ],
    }


def main() -> None:
    data = exact_data()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "rw-maxwell-simplicity-endomorphisms-receipt-v1",
        "status": data["status"],
        "source_commit": "c010701670838e114af0e29a029020603ba327f1",
        "artifacts": {
            "certificate": {"path": CERT.name, "sha256": digest(CERT)},
            "producer": {"path": "produce.py", "sha256": digest(HERE / "produce.py")},
            "verifier": {"path": "verify.py", "sha256": digest(HERE / "verify.py")},
            "tests": {
                "path": "test_simplicity.py",
                "sha256": digest(HERE / "test_simplicity.py"),
            },
            "imports": data["imports"],
        },
        "verification": {
            "producer": "python3 produce.py",
            "independent_verifier": "python3 verify.py",
            "tests": "python3 -m unittest -v test_simplicity.py",
            "arithmetic": "SymPy exact rational/polynomial arithmetic",
            "independence": (
                "Level II: verifier rederives residuals, indicial polynomials, "
                "terminal equations, and rank minors from separately written formulas"
            ),
        },
        "claim_boundary": (
            "Exact LOCAL-ALGEBRAIC simplicity and scalar endomorphism rings on "
            "the positive real axis, plus the axial ell=2 local-C consequence. "
            "No nonlocal C, all-ell Bach, QNM Smith, resolvent-pole, or quantum claim."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
