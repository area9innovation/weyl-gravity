#!/usr/bin/env python3
"""Produce the exact Schwarzschild parameter-deformation audit."""
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
        ROOT
        / "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
    "complete_reconstruction": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_complete_reconstruction_repair/certificate.json"
    ),
    "extension_preflight": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_spin_two_scattering_extension_preflight/certificate.json"
    ),
}

R, W, M = sp.symbols("r omega M", nonzero=True)
QW, QM = sp.symbols("q_omega q_M")
I = sp.I


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(
        value,
        locals={"r": R, "omega": W, "M": M, "I": I},
    )


def matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def cancel(value: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(value))


def encode(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(cancel(value)))


def encode_matrix(value: sp.Matrix) -> list[list[str]]:
    return [
        [encode(value[row, column]) for column in range(value.cols)]
        for row in range(value.rows)
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def residue_at_infinity(value: sp.Expr) -> sp.Expr:
    z = sp.Symbol("z")
    return sp.factor(
        -sp.residue(value.subs(R, 1 / z) / z**2, z, 0)
    )


def d_connection(connection: sp.Matrix, gauge: sp.Matrix) -> sp.Matrix:
    return (
        gauge.diff(R) + gauge * connection - connection * gauge
    ).applyfunc(cancel)


def produce() -> dict:
    triangular = json.loads(INPUTS["triangular_factorization"].read_text())
    complete = json.loads(INPUTS["complete_reconstruction"].read_text())
    extension_preflight = json.loads(INPUTS["extension_preflight"].read_text())

    # Re-derive the frozen extension from its authoritative exact maps.
    flow6 = matrix(complete["complete_reconstruction"]["flow6"])
    carrier_to_metric = flow6[4:, :4]
    embedding = matrix(
        triangular["carrier_exact_sequence"]["RW_embedding_J"]
    )
    metric_master = matrix(
        triangular["Einstein_kernel_RW_equivalence"][
            "U_H1F_to_PsiPsiPrime"
        ]
    )
    extension = (
        metric_master * carrier_to_metric * embedding
    ).applyfunc(cancel)
    recorded_extension = matrix(
        extension_preflight["exact_local_extension"]["matrix"]
    )
    if any(
        cancel(extension[row, column] - recorded_extension[row, column])
        for row in range(2)
        for column in range(2)
    ):
        raise RuntimeError("imported extension preflight drift")

    # The dimensionful ell=2 axial RW equation at fixed areal r and
    # physical omega follows from f=1-2M/r and
    # V=f*(6/r**2-6M/r**3).
    f = 1 - 2 * M / R
    potential = f * (6 / R**2 - 6 * M / R**3)
    scalar_a = cancel(sp.diff(f, R) / f + 2 * I * W / f)
    scalar_b = cancel(-potential / f**2)
    connection_m = sp.Matrix(
        [[0, 1], [-scalar_b, -scalar_a]]
    ).applyfunc(cancel)
    connection = connection_m.subs(M, 1).applyfunc(cancel)
    d_omega = connection_m.diff(W).subs(M, 1).applyfunc(cancel)
    d_mass = connection_m.diff(M).subs(M, 1).applyfunc(cancel)

    candidate = (
        extension - QW * d_omega - QM * d_mass
    ).applyfunc(cancel)
    trace_candidate = cancel(sp.trace(candidate))
    apparent = 2 * I / W
    residues = {
        "r=0": encode(sp.residue(trace_candidate, R, 0)),
        "r=2": encode(sp.residue(trace_candidate, R, 2)),
        "r=2*I/omega": encode(
            sp.residue(trace_candidate, R, apparent)
        ),
        "r=infinity": encode(residue_at_infinity(trace_candidate)),
    }
    expected_relation = QW + W * QM
    if cancel(sp.residue(trace_candidate, R, 2) - 4 * I * expected_relation):
        raise RuntimeError("horizon residue drift")
    if cancel(
        residue_at_infinity(trace_candidate)
        + 4 * I * expected_relation
    ):
        raise RuntimeError("infinity residue drift")

    scale_deformation = (d_mass - W * d_omega).applyfunc(cancel)
    scale_gauge = -R * connection - sp.diag(0, 1)
    scale_coboundary = d_connection(connection, scale_gauge)
    if any(
        cancel(scale_deformation[row, column] - scale_coboundary[row, column])
        for row in range(2)
        for column in range(2)
    ):
        raise RuntimeError("mass-scaling coboundary identity failed")

    # In x=r/M and Omega=M*omega, with state (y,d_x y), the scalar
    # equation has no remaining M dependence.
    X, OMEGA = sp.symbols("x Omega", nonzero=True)
    dimensionless_a = cancel(
        M * scalar_a.subs({R: M * X, W: OMEGA / M})
    )
    dimensionless_b = cancel(
        M**2 * scalar_b.subs({R: M * X, W: OMEGA / M})
    )
    if sp.diff(dimensionless_a, M) or sp.diff(dimensionless_b, M):
        raise RuntimeError("dimensionless mass cancellation failed")

    imports = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }
        for name, path in INPUTS.items()
    }
    document = {
        "schema": (
            "phase3-axial-qnm-parameter-deformation-cohomology-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_QNM_PARAMETER_DEFORMATION_COHOMOLOGY"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "PARAMETER_SHORTCUT_REFUSED",
        "declaration": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior",
            "sector": "axial ell=2 repeated spin-two filtration",
            "r_coordinate": "dimensionful areal radius held fixed for d_M",
            "omega_coordinate": "dimensionful physical frequency held fixed for d_M",
            "frozen_specialization": "M=1",
            "differential_field": "Q(I,omega,M,r) with d/dr",
            "genericity": (
                "omega is a nonzero indeterminate; finite residue points "
                "are interpreted over the rational function field"
            ),
        },
        "imports": imports,
        "mass_family_derivation": {
            "f": encode(f),
            "spin_two_potential": encode(potential),
            "scalar_a": encode(scalar_a),
            "scalar_b": encode(scalar_b),
            "companion_A_M": encode_matrix(connection_m),
            "companion_A_M1": encode_matrix(connection),
            "d_omega_A_M1": encode_matrix(d_omega),
            "d_M_A_M1": encode_matrix(d_mass),
        },
        "dimensionless_scaling_check": {
            "coordinates": "x=r/M, Omega=M*omega",
            "state": "(y,d_x y)",
            "scalar_a": sp.sstr(sp.factor(dimensionless_a)),
            "scalar_b": sp.sstr(sp.factor(dimensionless_b)),
            "d_M_scalar_a": "0",
            "d_M_scalar_b": "0",
            "interpretation": (
                "Schwarzschild mass is a scale in the dimensionless "
                "operator; its fixed-(r,omega) variation combines coordinate "
                "dilation, state rescaling and spectral rescaling."
            ),
        },
        "extension": {
            "definition": (
                "E_RW=U_metric*(carrier_to_metric_source)*J_carrier_RW"
            ),
            "matrix": encode_matrix(extension),
            "rank": int(extension.rank()),
            "source_hash_matches_preflight": True,
        },
        "trace_residue_audit": {
            "candidate": (
                "E_RW-q_omega*d_omega(A_RW)-q_M*d_M(A_RW)=D_A(B)"
            ),
            "D_A": "B_prime+B*A_RW-A_RW*B",
            "residues": residues,
            "necessary_relation": "q_omega+omega*q_M=0",
            "reason": (
                "the trace of D_A(B) is (tr B)' and every rational "
                "derivative has zero residue at every finite point and infinity"
            ),
        },
        "scale_coboundary": {
            "deformation": "d_M(A_RW)-omega*d_omega(A_RW)",
            "gauge_B_scale": encode_matrix(scale_gauge),
            "deformation_matrix": encode_matrix(scale_deformation),
            "identity": (
                "d_M(A_RW)-omega*d_omega(A_RW)=D_A(B_scale) at M=1"
            ),
            "verified": True,
        },
        "cohomology_conclusion": {
            "class_relation": "[d_M A_RW]=omega*[d_omega A_RW]",
            "parameter_span_dimension": 1,
            "admissible_candidate_combination_is_exact": True,
            "equivalence": (
                "E_RW lies in the rational span of d_omega A_RW and "
                "d_M A_RW modulo D_A iff E_RW itself is a rational "
                "D_A-coboundary"
            ),
            "pure_E_RW_coboundary_status": "NOT_DECIDED",
            "result": (
                "Mass variation adds no independent rational deformation "
                "class and cannot provide the proposed nontrivial "
                "parameter-derivative shortcut."
            ),
        },
        "scope_refusals": {
            "Lambda": (
                "UNDEFINED: the frozen input is Schwarzschild, not a "
                "certified Schwarzschild-(A)dS family. Varying cosmological "
                "Lambda changes the background, horizons and boundary problem."
            ),
            "ell": (
                "REFUSED_AS_PHYSICAL_PARAMETER: ell=2 is a discrete harmonic "
                "label. An auxiliary analytic continuation in ell*(ell+1) "
                "would be a different algebraic experiment, not a physical "
                "Schwarzschild parameter derivative."
            ),
        },
        "claim_flags": {
            "dimensionful_mass_family_derived": True,
            "trace_residue_constraint_certified": True,
            "mass_scaling_combination_rationally_exact": True,
            "mass_adds_independent_deformation_class": False,
            "pure_E_RW_coboundary_decided": False,
            "beta_n_computed": False,
            "QNM_Smith_type_selected": False,
        },
        "does_not_establish": [
            "that E_RW is or is not a pure rational D_A-coboundary",
            "a value or nonvanishing theorem for beta_n",
            "a local QNM Smith type or resolvent pole order",
            "a Schwarzschild-(A)dS parameter deformation",
            "a physical continuous deformation of the discrete ell label",
            "a Lorentzian quantum, CPT, particle or unitarity theorem",
        ],
    }
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n")
    return document


if __name__ == "__main__":
    result = produce()
    print(
        "status="
        f"{result['status']} "
        "mass_independent_class=false beta_n_computed=false"
    )
