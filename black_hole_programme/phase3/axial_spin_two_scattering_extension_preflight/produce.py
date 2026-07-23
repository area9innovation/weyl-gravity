#!/usr/bin/env python3
"""Extract the local spin-two extension and audit its scattering class."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
INPUTS = {
    "triangular_factorization": (
        ROOT / "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
    "complete_reconstruction": (
        ROOT / "black_hole_programme/phase3/"
        "axial_complete_reconstruction_repair/certificate.json"
    ),
    "analytic_incoming_connection": (
        ROOT / "black_hole_programme/phase3/"
        "axial_incoming_connection_analytic/certificate.json"
    ),
}
COMMITS = {
    "triangular_factorization": "8e7de78c3835a35180294a8e2d6d3437f0a716a2",
    "complete_reconstruction": "d5d5d6de648795203604d62ce7bc4f4ce6fea510",
    "analytic_incoming_connection": "b3be2b0778d61ae6053ec39edb8542bc1e074044",
}
R = sp.Symbol("r", positive=True)
W = sp.Symbol("omega")
I = sp.I


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def cancel(value: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(value))


def encode(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(cancel(value)))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def companion(a: sp.Expr, b: sp.Expr) -> sp.Matrix:
    return sp.Matrix([[0, 1], [-b, -a]])


def produce() -> dict:
    triangular = json.loads(INPUTS["triangular_factorization"].read_text())
    complete = json.loads(INPUTS["complete_reconstruction"].read_text())
    incoming = json.loads(INPUTS["analytic_incoming_connection"].read_text())

    flow6 = matrix(complete["complete_reconstruction"]["flow6"])
    carrier_to_metric = flow6[4:, :4]
    embedding = matrix(triangular["carrier_exact_sequence"]["RW_embedding_J"])
    metric_master = matrix(
        triangular["Einstein_kernel_RW_equivalence"][
            "U_H1F_to_PsiPsiPrime"
        ]
    )
    extension = (
        metric_master * carrier_to_metric * embedding
    ).applyfunc(cancel)

    rw = triangular["operators"]["L_RW"]
    a_rw, b_rw = parse(rw["a"]), parse(rw["b"])
    connection = companion(a_rw, b_rw)
    spectral_derivative = connection.diff(W)

    # A pointwise scalar multiple is impossible because d_omega A has only
    # one nonzero entry, while the exact extension has other nonzero entries.
    direct_proportionality = all(
        extension[i, j] == 0
        for i in range(2) for j in range(2)
        if spectral_derivative[i, j] == 0
    )

    trace_extension = encode(sp.trace(extension))
    trace_spectral = encode(sp.trace(spectral_derivative))
    q = sp.Symbol("q")
    trace_difference = cancel(
        sp.trace(extension) - q * sp.trace(spectral_derivative)
    )
    residue_r2 = sp.factor(sp.residue(trace_difference, R, 2))
    trace_antiderivative = cancel(
        -sp.Rational(3, 4) * R
        - 1 / (W * (W * R - 2 * I))
    )
    if cancel(sp.diff(trace_antiderivative, R) - sp.trace(extension)) != 0:
        raise RuntimeError("trace antiderivative drift")
    # If E-q*d_omega A were a rational connection coboundary
    # B'+BA-AB, its trace would be (tr B)' and have zero residues.
    rational_q_forced = sp.solve(sp.Eq(residue_r2, 0), q)

    imports = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
            "commit": COMMITS[name],
        }
        for name, path in INPUTS.items()
    }
    document = {
        "schema": "phase3-axial-spin-two-scattering-extension-preflight-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "METHOD_SHORTFALL",
        "declaration": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2",
            "time_phase": "exp(+I*omega*t)",
            "ingoing_EF_phase": (
                "exp(+I*omega*v)=exp(+I*omega*t)"
                "*exp(+I*omega*rstar)"
            ),
            "damped_QNM_half_plane": "Im(omega)>0",
        },
        "exact_local_extension": {
            "definition": (
                "E_RW=U_metric*(carrier_to_metric_source)*J_carrier_RW"
            ),
            "system": (
                "d_r [x_metric;x_carrier]="
                "[[A_RW,E_RW],[0,A_RW]]*[x_metric;x_carrier]"
            ),
            "matrix": [
                [encode(extension[i, j]) for j in range(2)]
                for i in range(2)
            ],
            "rank": int(extension.rank()),
            "determinant": encode(extension.det()),
            "trace": trace_extension,
            "spectral_derivative_matrix": [
                [encode(spectral_derivative[i, j]) for j in range(2)]
                for i in range(2)
            ],
            "pointwise_scalar_multiple_of_domega_A_RW": direct_proportionality,
        },
        "rational_gauge_trace_test": {
            "candidate_identity": (
                "E_RW=q(omega)*d_omega(A_RW)+B_prime+B*A_RW-A_RW*B"
            ),
            "trace_E_minus_q_domega_A": encode(trace_difference),
            "rational_antiderivative_of_trace_E": encode(
                trace_antiderivative
            ),
            "residue_at_r=2": encode(residue_r2),
            "zero_residue_forces": [f"q={encode(value)}"
                                    for value in rational_q_forced],
            "conclusion": (
                "No nonzero q(omega) can occur in this identity with a "
                "globally rational B. This does not test endpoint-analytic "
                "gauges containing logarithmic spectral-phase derivatives."
            ),
            "pure_rational_coboundary_status": "NOT_DECIDED",
            "relation_to_scattering_q": (
                "This operator-level rational q is not the quotient class "
                "[q]=[c]/[A_in_2_prime]; the latter allows endpoint-analytic "
                "spectral-phase gauges and remains uncomputed."
            ),
        },
        "local_filtration_invariant": {
            "hypothesis": (
                "omega_star is a simple zero of "
                "a=A_in_2 in the analytic-germ DVR O"
            ),
            "reduced_matrix": "[[a,c],[0,a]]",
            "frame_law": "c -> u*c+a*d, u in O^times, d in O",
            "class": "[c] in O/(A_in_2), defined up to multiplication by a unit",
            "smith_valuations": (
                "(min(ord(a),ord(c)), "
                "2*ord(a)-min(ord(a),ord(c)))"
            ),
        },
        "spectral_derivative_congruence": {
            "statement": (
                "c == q*A_in_2_prime modulo A_in_2"
            ),
            "existence_at_a_simple_zero": "TAUTOLOGICALLY_TRUE",
            "reason": (
                "[A_in_2_prime] is a unit in O/(A_in_2), so every [c] "
                "has a unique [q]=[c]*[A_in_2_prime]^-1"
            ),
            "canonical_class": (
                "[q]=[c]*[A_in_2_prime]^-1 in O/(A_in_2)"
            ),
            "nonvanishing_equivalence": (
                "[q]!=0 iff [c]!=0 iff the Fredholm extension pairing "
                "is nonzero, after compatible normalizations"
            ),
            "physical_q_computed": False,
            "smith_case_selected": False,
        },
        "jost_data_audit": {
            "available": [
                "the exact short-range spin-two potential",
                "formal symbols A_in_2 and A_out_2",
                "the real-frequency Wronskian identity",
                "real-frequency nonvanishing of A_in_2",
                "exact rational endpoint factor frames",
            ],
            "missing": [
                "a certified damped QNM omega_star with A_in_2(omega_star)=0",
                "a regular analytic horizon-normalized QNM germ near omega_star",
                "a compatible adjoint QNM germ and normalization",
                "A_in_2_prime(omega_star) and a proof that the zero is simple",
                "a boundary-convergent or regularized Fredholm pairing",
                "the normalization identity relating that pairing to c",
            ],
            "incoming_certificate_domain": incoming["declaration"]["frequency"],
        },
        "minimal_successor_input": {
            "qnm": (
                "An exact or independently certified complex omega_star in "
                "Im(omega)>0 with A_in_2(omega_star)=0 and "
                "A_in_2_prime(omega_star)!=0."
            ),
            "analytic_patches": (
                "Horizon and infinity Jost/adjoint germs holomorphic in omega "
                "through omega_star, with all Frobenius frame events resolved."
            ),
            "pairing": (
                "A convergent contour, complex scaling, or explicitly "
                "renormalized Fredholm pairing Gamma_star="
                "<psi_star_adj,E_RW(omega_star)psi_star>."
            ),
            "normalization": (
                "A proved formula c(omega_star)=unit*Gamma_star and compatible "
                "normalizations for A_in_2_prime."
            ),
            "decision": (
                "Then [q]=[c]/[A_in_2_prime] can be evaluated; its zero or "
                "nonzero value selects the simple-zero Smith case."
            ),
        },
        "imports": imports,
        "claim_flags": {
            "exact_local_RW_to_RW_extension_extracted": True,
            "filtration_invariant_class_defined": True,
            "unquantified_simple_zero_congruence_is_tautological": True,
            "nonzero_rational_operator_derivative_coefficient_ruled_out": True,
            "scattering_extension_coefficient_c_computed": False,
            "Fredholm_pairing_computed": False,
            "spectral_derivative_q_nonzero_certified": False,
            "simple_QNM_Smith_case_selected": False,
        },
        "does_not_establish": [
            "the existence or location of a damped axial spin-two QNM",
            "a closed symbolic formula for A_in_2, c or q",
            "nonvanishing of the extension class [c]",
            "a Smith type for the repeated spin-two QNM block",
            "time-domain stability, CPT positivity, particles or unitarity",
            "a LORENTZIAN-CAUSAL quantum theorem",
        ],
    }
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n")
    return document


if __name__ == "__main__":
    result = produce()
    print(result["status"])
