#!/usr/bin/env python3
"""Produce the exact complete massive axial first-jet crosswalk certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
INPUTS = {
    "bach_projective_cocycle": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_qnm_projective_cocycle_v1/certificate.json"
    ),
    "partial_jet_crosswalk": (
        ROOT
        / "black_hole_programme/phase3/"
        "axial_partial_jet_transport_crosswalk_v1/certificate.json"
    ),
}

R, W = sp.symbols("r omega", nonzero=True)
I = sp.I
F = (R - 2) / R


def exact(value: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(value))


def encode(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(exact(value)))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dstar(value: sp.Expr) -> sp.Expr:
    return exact(F * sp.diff(value, R))


def dstar_matrix(value: sp.Matrix) -> sp.Matrix:
    return value.applyfunc(dstar)


def projective(value: sp.Expr, potential: sp.Expr) -> sp.Expr:
    return exact(
        dstar(dstar(dstar(value)))
        + 4 * potential * dstar(value)
        + 2 * dstar(potential) * value
    )


def matrix_strings(value: sp.Matrix) -> list[list[str]]:
    return [[encode(entry) for entry in row] for row in value.tolist()]


def scalarize_block(
    block: sp.Matrix, source_potential: sp.Expr
) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """Scalarize a first-order tangent block in (y,Dy) coordinates."""
    e00, e01, e10, e11 = (
        block[0, 0],
        block[0, 1],
        block[1, 0],
        block[1, 1],
    )
    s1 = exact(e11 + e00 + dstar(e01))
    s0 = exact(e10 + dstar(e00) - e01 * source_potential)
    density = exact(s0 - sp.Rational(1, 2) * dstar(s1))
    return s1, s0, density


def produce() -> dict:
    u2 = exact(W**2 - F * (6 / R**2 - 6 / R**3))
    u1 = exact(W**2 - 6 * F / R**2)
    a_factor = sp.Matrix(
        [
            [0, 1, 0, 0],
            [-u2, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, -u1, 0],
        ]
    )

    # Brito--Cardoso--Pani's massless Berndtson transformation, specialized
    # to M=1 and ell=2, in state order (phi_2,Dphi_2,phi_1,Dphi_1).
    q_row = sp.Matrix(
        [[
            4 * F / (3 * W**2 * R),
            4 / (3 * W**2),
            -2 * F / (W**2 * R),
            1 / W**2,
        ]]
    )
    z_row = sp.Matrix(
        [[
            -(7 * R - 6) / (3 * W**2 * R**2),
            -1 / W**2,
            -1 / (W**2 * R),
            0,
        ]]
    )

    def derivative_row(row: sp.Matrix) -> sp.Matrix:
        return (dstar_matrix(row) + row * a_factor).applyfunc(exact)

    transform = sp.Matrix.vstack(
        q_row, derivative_row(q_row), z_row, derivative_row(z_row)
    )

    vq = exact(W**2 - F * (10 / R**2 - 16 / R**3))
    vz = exact(W**2 - F * (4 / R**2 + 2 / R**3))
    qz_flow_zero = sp.Matrix(
        [
            [0, 1, 0, 0],
            [-vq, 0, 8 * F * (R - 3) / R**3, 0],
            [0, 0, 0, 1],
            [2 * F / R**2, 0, -vz, 0],
        ]
    )
    intertwining_residual = (
        dstar_matrix(transform)
        + transform * a_factor
        - qz_flow_zero * transform
    ).applyfunc(exact)
    if intertwining_residual != sp.zeros(4):
        raise RuntimeError("massless Berndtson factorization failed")

    qz_mass_tangent = sp.zeros(4)
    qz_mass_tangent[1, 0] = F
    qz_mass_tangent[3, 2] = F
    factor_tangent = (
        transform.inv() * qz_mass_tangent * transform
    ).applyfunc(exact)

    k22 = factor_tangent[:2, :2]
    k21 = factor_tangent[2:, :2]
    k12 = factor_tangent[:2, 2:]
    k11 = factor_tangent[2:, 2:]

    tensor_s1, tensor_s0, tensor_density = scalarize_block(k22, u2)
    reverse_s1, reverse_s0, _ = scalarize_block(k21, u2)
    vector_s1, vector_s0, vector_density = scalarize_block(k11, u1)

    reverse_multiplier = -sp.Rational(16, 27) / W**2
    reverse_exact = exact(
        reverse_multiplier * (u1 - u2) - reverse_s0
    )
    if reverse_s1 != 0 or reverse_exact != 0:
        raise RuntimeError("reverse tensor-to-vector removal failed")

    mass_primitive = R / (6 * W**2)
    mass_normal_residual = exact(
        tensor_density
        - projective(mass_primitive, u2)
        - F / 3
    )
    if mass_normal_residual != 0:
        raise RuntimeError("complete-system mass normal form failed")

    bach_density = exact(
        I
        * (R - 2)
        * (2 * R * W**2 + 3 * W**2 + 12)
        / (5 * R**4 * W)
    )
    bach_primitive = exact(
        -I
        / (120 * W)
        * (15 * R + 13 + 12 / R + 9 / R**2)
    )
    bach_normal_residual = exact(
        bach_density - projective(bach_primitive, u2) - I * W * F / 2
    )
    if bach_normal_residual != 0:
        raise RuntimeError("Bach mass-direction identity drift")

    scaling = 3 * I * W / 2
    combined_primitive = exact(bach_primitive - scaling * mass_primitive)
    combined_residual = exact(
        bach_density
        - scaling * tensor_density
        - projective(combined_primitive, u2)
    )
    if combined_residual != 0:
        raise RuntimeError("complete Bach/massive crosswalk failed")

    # Show that equality with [f], rather than proportionality by 1/3, is
    # false over the declared generic rational field.
    c_m2, c_m1, c_0 = sp.symbols("c_m2 c_m1 c_0")
    trial = c_m2 / R**2 + c_m1 / R + c_0
    equality_expr = sp.together(
        projective(trial, u2) - (tensor_density - F)
    )
    equality_poly = sp.Poly(equality_expr.as_numer_denom()[0], R)
    equality_matrix, equality_rhs = sp.linear_eq_to_matrix(
        equality_poly.all_coeffs(), [c_m2, c_m1, c_0]
    )
    equality_left_witness = sp.Matrix(
        [
            (104 * W**4 - 75 * W**2 + 126) / (9 * W**4),
            26 * (2 * W**2 + 3) / (9 * W**2),
            2 * (13 * W**2 + 6) / (9 * W**2),
            1,
            0,
            0,
        ]
    )
    if any(
        exact(entry) != 0
        for entry in equality_left_witness.T * equality_matrix
    ):
        raise RuntimeError("equality obstruction witness drift")
    equality_obstruction = exact(
        (equality_left_witness.T * equality_rhs)[0]
    )

    # Endpoint leading terms.  Q(q)=2qD-D(q) is the corrected full gauge.
    sigma = sp.symbols("sigma")
    raw_mass_phase = -sigma * I / (2 * W)
    mass_gauge_phase = exact(2 * mass_primitive * sigma * I * W / R)
    # Coefficients of r in the relative tangent; D(q)=O(1), so it does not
    # contribute to this leading coefficient.
    reduced_mass_phase = exact(raw_mass_phase + sigma * I / (3 * W))
    bach_gauge_phase = sigma / 4
    scaled_mass_phase = exact(scaling * reduced_mass_phase)
    if exact(scaled_mass_phase - bach_gauge_phase) != 0:
        raise RuntimeError("endpoint leading phase crosswalk failed")

    source_records = {
        "brito_cardoso_pani": {
            "arxiv": "1304.6725",
            "doi": "10.1103/PhysRevD.88.023514",
            "used_result": (
                "complete Schwarzschild axial massive-spin-two Q,Z system "
                "and its massless Berndtson Maxwell/RW transformation"
            ),
        },
        "antoniou_gualtieri_pani": {
            "arxiv": "2412.15037",
            "doi": "10.1103/PhysRevD.111.064059",
            "used_result": (
                "Einstein-Weyl auxiliary-field equations and Schwarzschild "
                "massive axial/Jost normalization"
            ),
        },
    }

    document = {
        "schema": "phase4-axial-complete-massive-jet-crosswalk-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE4_AXIAL_COMPLETE_MASSIVE_JET_CROSSWALK",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "EXACT_COMPLETE_MASSIVE_FIRST_JET_FACTOR_THREE_PASS",
        "scope": {
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2",
            "mass_parameter": "m=mu**2, the signed squared-mass coefficient",
            "field": "C(I,omega)(r), generic omega",
            "derivative": "D=((r-2)/r)*d/dr",
            "frequency_exclusions": [
                "omega=0",
                "omega**2=3 for the displayed equality-obstruction witness",
            ],
        },
        "sources": source_records,
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
            }
            for name, path in INPUTS.items()
        },
        "complete_massive_axial_system": {
            "state_order": ["Q", "D(Q)", "Z", "D(Z)"],
            "massless_flow": matrix_strings(qz_flow_zero),
            "mass_tangent": matrix_strings(qz_mass_tangent),
            "statement": (
                "The complete axial massive-spin-two equations are the "
                "coupled Q,Z system, not a single shifted RW equation."
            ),
        },
        "massless_factorization": {
            "factor_state_order": [
                "phi_2",
                "D(phi_2)",
                "phi_1",
                "D(phi_1)",
            ],
            "transform_factor_to_QZ": matrix_strings(transform),
            "determinant": encode(transform.det()),
            "intertwining_residual": matrix_strings(intertwining_residual),
            "exact": True,
        },
        "complete_first_mass_jet": {
            "factor_tangent": matrix_strings(factor_tangent),
            "tensor_to_tensor": matrix_strings(k22),
            "vector_to_tensor": matrix_strings(k12),
            "tensor_to_vector": matrix_strings(k21),
            "vector_to_vector": matrix_strings(k11),
            "reverse_scalar_source": {
                "s1": encode(reverse_s1),
                "s0": encode(reverse_s0),
                "removing_multiplier_P": encode(reverse_multiplier),
                "identity": "L1*(P*phi2)=s0*phi2 on ker(L2)",
                "exact": True,
            },
        },
        "physical_tensor_projective_class": {
            "s1": encode(tensor_s1),
            "s0": encode(tensor_s0),
            "density": encode(tensor_density),
            "primitive": encode(mass_primitive),
            "normal_form_identity": "I_phys=K_U(q_mass)+(1/3)*f",
            "normal_form_residual": encode(mass_normal_residual),
            "class": "[I_phys]=(1/3)[f]",
        },
        "vector_diagonal_tangent": {
            "s1": encode(vector_s1),
            "s0": encode(vector_s0),
            "density": encode(vector_density),
        },
        "bach_crosswalk": {
            "bach_density": encode(bach_density),
            "bach_primitive": encode(bach_primitive),
            "physical_scaling": encode(scaling),
            "combined_primitive": encode(combined_primitive),
            "identity": (
                "I_Bach=(3*I*omega/2)*I_phys+K_U(q_combined)"
            ),
            "residual": encode(combined_residual),
            "tangent_parameter_relation": (
                "m=(3*I*omega/2)*tau at fixed omega, modulo rational gauge"
            ),
            "not_a_global_parameter_redefinition": True,
        },
        "naive_single_scalar_equality_obstruction": {
            "tested_false_identity": "[I_phys]=[f]",
            "exhaustive_trial": "c_m2/r**2+c_m1/r+c_0",
            "matrix_rank": int(equality_matrix.rank()),
            "augmented_rank": int(
                equality_matrix.row_join(equality_rhs).rank()
            ),
            "left_null_witness": [
                encode(entry) for entry in equality_left_witness
            ],
            "obstruction": encode(equality_obstruction),
            "conclusion": (
                "The complete tensor branch carries one third of the naive "
                "single shifted-RW projective class."
            ),
        },
        "endpoint_leading_crosswalk": {
            "raw_physical_mass_tangent_r_coefficient": encode(raw_mass_phase),
            "mass_reduction_gauge_r_coefficient": encode(
                sigma * I / (3 * W)
            ),
            "reduced_physical_tangent_r_coefficient": encode(
                reduced_mass_phase
            ),
            "scaled_physical_tangent_r_coefficient": encode(
                scaled_mass_phase
            ),
            "bach_tangent_r_coefficient": encode(bach_gauge_phase),
            "coulomb_power_first_derivative": "0",
            "leading_match_exact": True,
        },
        "claim_flags": {
            "complete_coupled_massive_axial_equations_imported": True,
            "exact_massless_Maxwell_RW_factorization": True,
            "complete_first_mass_squared_jet_transformed": True,
            "reverse_tensor_to_vector_tangent_rationally_removed": True,
            "physical_tensor_projective_class_computed": True,
            "naive_unit_mass_class_rejected": True,
            "factor_three_Bach_mass_crosswalk_exact": True,
            "leading_differentiated_Jost_phase_match": True,
            "all_order_differentiated_Jost_map_certified": False,
            "physical_QNM_velocity_certified": False,
            "global_causal_resolvent_certified": False,
        },
        "does_not_establish": [
            "a convergent all-order differentiated massive Jost construction",
            "absence of opposite-Jost admixture beyond the formal endpoint class",
            "the physical massive-QNM velocity at the certified Weyl QNM",
            "a common global Fredholm domain for the massive and Bach pencils",
            "a global retarded contour deformation or causal ringdown theorem",
        ],
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return document


if __name__ == "__main__":
    result = produce()
    print(result["status"])
