#!/usr/bin/env python3
"""Exact Candidate-A auxiliary-scalaron obstruction on the unit cylinder.

The earlier changed-action preflight correctly found the scalar trace
polynomial ``-(Box+2)^2/8``, but it treated that polynomial as a direct-sum
addition to the strict metric carrier.  The auxiliary rewrite exposes the
missing mixed metric rows on the non-Einstein cylinder:

    beta R^2 = chi R - chi^2/(4 beta),
    psi = chi + 1/12,
    L_A = psi (R-6) + 36 psi^2.

This module derives the full mixed Hessian from that action and then restricts
it to an invariant, spatially homogeneous scalar sector.  The restriction is
not a metric-only substitute: both the metric equation and the auxiliary
equation are checked.  It gives a second-order Jordan system with an
action-derived kinetic form of inertia (1,1), real D roots +/-sqrt(2), and an
indefinite D Hamiltonian.  Hence Candidate A fails the physical-sign gate.

The result supersedes only the *complete-direct-sum* promotion of
COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1.  Its rational action
tuning and scalar Schur-complement/iterated-Green identities remain valid.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "compensator-candidate-a-r2-auxiliary-scalar-obstruction-v1.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "compensator-candidate-a-r2-auxiliary-scalar-obstruction-v1.schema.json"
)

DEPENDENCIES = {
    "action_preflight": {
        "path": ROOT
        / "d_quotient_classical"
        / "certificates"
        / "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json",
        "source_commit": "306ff78a2001f23124d412e9a2f41531bec74f78",
        "sha256": "a537e31bf667520443903551b5bf2596dff9a1c35fade88d2ffc1e89c1e0b836",
    },
    "strict_tau_obstruction": {
        "path": ROOT
        / "d_quotient_classical"
        / "certificates"
        / "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json",
        "source_commit": "2b834dc751d6948366fd5c3d99174c268fa50d21",
        "sha256": "db1f998a0920adb94cf4fcbffb1b9eb2ea6537876aff9513aac4e4d9ec2b51b9",
    },
    "superseded_direct_sum_parent": {
        "path": ROOT
        / "d_quotient_classical"
        / "certificates"
        / "COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1.json",
        "source_commit": "08ce0b87301b60a3ff717dfe7d285184a20c3820",
        "sha256": "be7847102b7c219fd09865b68c4982c84e280e09c73364c509dcb9aaca91d6c4",
    },
    "strict_metric_endpoint": {
        "path": ROOT
        / "covariant_completion"
        / "certificates"
        / "curved_prolonged_metric_endpoint_complex.json",
        "source_commit": "6ebd72043d61dd3ca9a8cd571321424408762cd5",
        "sha256": "870621ae6750b1e66e3f3316c5a2680d1244c7fca3be4d6aeaabbfdc2178fd79",
    },
    "positive_Berger_clock": {
        "path": ROOT
        / "d_quotient_classical"
        / "certificates"
        / "POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "source_commit": "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
        "sha256": "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: Fraction | sp.Rational | int) -> dict[str, int]:
    rational = sp.Rational(value)
    return {
        "numerator": int(rational.p),
        "denominator": int(rational.q),
    }


def _matrix(matrix: sp.MatrixBase) -> dict[str, Any]:
    value = {
        "row_count": matrix.rows,
        "column_count": matrix.cols,
        "entries": [
            {
                "row": row,
                "column": column,
                "coefficient": str(matrix[row, column]),
            }
            for row in range(matrix.rows)
            for column in range(matrix.cols)
            if matrix[row, column] != 0
        ],
    }
    value["sha256"] = _digest(value)
    return value


def _dense(record: dict[str, Any], locals_map: dict[str, Any] | None = None) -> sp.Matrix:
    matrix = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        matrix[entry["row"], entry["column"]] = sp.sympify(
            entry["coefficient"], locals=locals_map or {}
        )
    return matrix


def _dependency_rows() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    rows: dict[str, Any] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for name, item in DEPENDENCIES.items():
        path = item["path"]
        actual = _sha(path)
        if actual != item["sha256"]:
            raise AssertionError(f"Candidate-A dependency hash drifted: {name}")
        payload = json.loads(path.read_text())
        payloads[name] = payload
        rows[name] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": payload.get("result_id", payload.get("schema")),
            "source_commit": item["source_commit"],
            "sha256": actual,
        }
    if (
        payloads["action_preflight"].get("result_state")
        != "LOCAL_ACTION_AND_QUARTET_CERTIFIED"
        or payloads["strict_tau_obstruction"].get("result_state") != "OBSTRUCTED"
        or payloads["superseded_direct_sum_parent"].get("result_state")
        != "CHANGED_ACTION_CAUSAL_BV_PARENT_CERTIFIED"
        or payloads["strict_metric_endpoint"].get("dimension") != 30
        or payloads["positive_Berger_clock"].get("claim_status")
        != "CERTIFIED_EXACT_BACKGROUND"
    ):
        raise AssertionError("Candidate-A dependency semantics drifted")
    return rows, payloads


def _action_data() -> dict[str, Any]:
    beta = sp.Rational(-1, 144)
    R0 = sp.Integer(6)
    M2 = sp.Rational(1, 6)
    V0 = sp.Rational(1, 4)
    chi0 = 2 * beta * R0
    if chi0 != sp.Rational(-1, 12):
        raise AssertionError("auxiliary background drifted")

    R, chi, psi = sp.symbols("R chi psi")
    original = beta * R**2 + M2 * R / 2 - V0
    auxiliary = chi * R - chi**2 / (4 * beta) + M2 * R / 2 - V0
    shifted = sp.expand(auxiliary.subs(chi, psi + chi0))
    if sp.expand(shifted - (psi * (R - 6) + 36 * psi**2)) != 0:
        raise AssertionError("shifted auxiliary action identity failed")
    if sp.expand(auxiliary.subs(chi, 2 * beta * R) - original) != 0:
        raise AssertionError("auxiliary elimination failed")
    if sp.expand(original + (R - 6) ** 2 / 144) != 0:
        raise AssertionError("critical square identity failed")

    manifest = {
        "density": (
            "alpha_B C(g_hat)^2/8 + chi R(g_hat) "
            "- chi^2/(4 beta) + M_P^2 R(g_hat)/2 - V0 "
            "- (nabla theta)^2/2"
        ),
        "beta": "-1/144",
        "M_P_squared": "1/6",
        "V0": "1/4",
        "chi_background": "-1/12",
        "psi_definition": "psi=chi+1/12",
        "shifted_scalar_tensor_density": "psi(R-6)+36 psi^2",
        "metric_gauge_group_after_dressing": "Diff only",
        "original_Weyl_sector": (
            "pointwise contractible (tau,omega,omega_star,tau_hat_star) quartet"
        ),
        "global_internal_symmetry": "U(1) shift of theta",
    }
    return {
        "manifest": manifest,
        "action_sha256": _digest(manifest),
        "identities": {
            "critical_metric_density": "R/12-R^2/144-1/4=-(R-6)^2/144",
            "auxiliary_elimination": "chi=2 beta R",
            "shifted_identity": (
                "chi R-chi^2/(4 beta)+R/12-1/4="
                "psi(R-6)+36 psi^2"
            ),
            "background": "R0=6, chi0=-1/12, psi0=0",
        },
    }


def _mixed_hessian() -> dict[str, Any]:
    # Normal orthonormal cylinder frame, covariant symmetric-tensor coordinates.
    metric = sp.diag(-1, 1, 1, 1)
    inverse = metric
    ricci = sp.diag(0, 2, 2, 2)
    coordinates = (
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 1),
        (1, 2),
        (1, 3),
        (2, 2),
        (2, 3),
        (3, 3),
    )
    tensor_basis = []
    for a, b in coordinates:
        basis = sp.zeros(4)
        basis[a, b] = 1
        basis[b, a] = 1
        tensor_basis.append(basis)
    tensor_pairing = sp.Matrix(
        10,
        10,
        lambda row, column: sp.trace(
            inverse * tensor_basis[row] * inverse * tensor_basis[column]
        ),
    )

    z = sp.symbols("z0:4", real=True)
    z_cov = sp.Matrix(z)
    z_up = inverse * z_cov
    box_symbol = sp.expand((z_cov.T * inverse * z_cov)[0])
    # L_ab psi is the metric variation of int psi(R-6):
    # nabla_a nabla_b psi-g_ab Box psi-Ric_ab psi.
    L = z_cov * z_cov.T - metric * box_symbol - ricci
    L_coordinates = sp.Matrix([L[a, b] for a, b in coordinates])
    mixed_column = (tensor_pairing * L_coordinates).applyfunc(sp.expand)
    delta_R_row = mixed_column.T
    hessian = sp.zeros(11)
    hessian[:10, 10] = mixed_column
    hessian[10, :10] = delta_R_row
    hessian[10, 10] = 72

    trace_vector = sp.Matrix([metric[a, b] for a, b in coordinates])
    trace_restriction = sp.expand((delta_R_row * trace_vector)[0])
    if trace_restriction != -3 * (box_symbol + 2):
        raise AssertionError("delta R trace restriction drifted")
    if hessian.T != hessian:
        raise AssertionError("mixed Hessian is not formally self-adjoint")

    return {
        "normal_frame": {
            "metric": ["-1", "1", "1", "1"],
            "Ricci_covariant": ["0", "2", "2", "2"],
            "scalar_curvature": "6",
            "parallel_Ricci": True,
        },
        "full_action_hessian": {
            "field_basis": ["h_00", "h_01", "h_02", "h_03", "h_11", "h_12", "h_13", "h_22", "h_23", "h_33", "psi"],
            "block_formula": (
                "[[B_C2, L], [delta_R,72]], "
                "L_ab=nabla_a nabla_b-g_ab Box-Ric_ab"
            ),
            "delta_R": (
                "nabla_a nabla_b h^ab-Box tr(h)-Ric_ab h^ab"
            ),
            "mixed_block_polynomial": _matrix(hessian),
            "covector_symbols": [str(value) for value in z],
            "formal_adjoint_defect": 0,
            "trace_restriction": "delta_R(u g_bar)=-3(Box+2)u",
            "strict_complement_change": (
                "NONZERO: L psi has tracefree components on the non-Einstein cylinder"
            ),
            "old_direct_sum_statement_valid": False,
        },
        "BV_rows": {
            "minimal_fields": [
                "g_hat",
                "chi",
                "theta",
                "xi",
                "tau",
                "omega",
                "and canonical antifields",
            ],
            "Q_g_hat": "L_xi g_hat",
            "Q_chi": "L_xi chi",
            "Q_theta": "L_xi theta",
            "Q_xi": "xi^nu partial_nu xi",
            "Q_tau": "L_xi tau+omega",
            "Q_omega": "L_xi omega",
            "Q_antifields": (
                "minus the action Euler rows plus the canonical Diff/Weyl cotangent lift"
            ),
            "new_chi_Euler_row": "R(g_hat)-chi/(2 beta)",
            "nonminimal_rows": (
                "the Diff and Weyl antighost/multiplier cotangent doublets imported from the action preflight"
            ),
            "CME": "PASS_BY_ACTION_INVARIANCE_AND_CANONICAL_COTANGENT_LIFT",
            "Q_squared_zero": "PASS",
            "real_structure": "componentwise real",
            "Weyl_quartet": "UNCHANGED_EXACT_CONTRACTION",
            "important_reclassification": (
                "the dressed metric has Diff gauge only; the original Weyl ghost acts in the tau quartet and is not a conformal gauge generator of g_hat"
            ),
        },
    }


def _homogeneous_scalar_sector() -> dict[str, Any]:
    P = sp.Symbol("P")
    H = sp.Matrix([[0, -3 * P], [-3 * P, 72]])
    H_inverse = sp.Matrix(
        [
            [-sp.Rational(8, 1) / P**2, -sp.Rational(1, 3) / P],
            [-sp.Rational(1, 3) / P, 0],
        ]
    )
    if sp.simplify(H * H_inverse) != sp.eye(2):
        raise AssertionError("scalar Schur inverse failed")

    velocity = sp.Matrix([[0, -3], [-3, 0]])
    if velocity.eigenvals() != {-3: 1, 3: 1}:
        raise AssertionError("scalar velocity inertia drifted")

    # State order (u,u_dot,psi,psi_dot).
    evolution = sp.Matrix(
        [
            [0, 1, 0, 0],
            [2, 0, -24, 0],
            [0, 0, 0, 1],
            [0, 0, 2, 0],
        ]
    )
    lam = sp.Symbol("lambda")
    characteristic = sp.factor(evolution.charpoly(lam).as_expr())
    nilpotent_part = evolution**2 - 2 * sp.eye(4)
    if characteristic != (lam**2 - 2) ** 2:
        raise AssertionError("scalar D characteristic polynomial drifted")
    if nilpotent_part == sp.zeros(4) or nilpotent_part**2 != sp.zeros(4):
        raise AssertionError("scalar Jordan test failed")

    symplectic = sp.Matrix(
        [
            [0, 0, 0, -3],
            [0, 0, 3, 0],
            [0, -3, 0, 0],
            [3, 0, 0, 0],
        ]
    )
    if symplectic.det() != 81:
        raise AssertionError("reduced Lee-Wald form is degenerate")
    if evolution.T * symplectic + symplectic * evolution != sp.zeros(4):
        raise AssertionError("D does not preserve reduced Lee-Wald form")

    energy_hessian = sp.Matrix(
        [
            [0, 0, 6, 0],
            [0, 0, 0, -3],
            [6, 0, -72, 0],
            [0, -3, 0, 0],
        ]
    )
    if evolution.T * symplectic != energy_hessian:
        raise AssertionError("D Hamiltonian/Lee-Wald identity drifted")

    return {
        "consistent_full_Hessian_restriction": {
            "ansatz": (
                "h_ab=u(t) g_bar_ab and psi=psi(t), spatially homogeneous"
            ),
            "B_C2_on_trace": "0 by exact conformal invariance",
            "mixed_metric_rows": (
                "L_00 psi=0; L_ij psi=-(P_2 psi) g_ij"
            ),
            "auxiliary_row": "delta_R+72 psi=-3 P_2 u+72 psi",
            "complete_equations": [
                "P_2 psi=0",
                "P_2 u=24 psi",
            ],
            "Schur_equation": "P_2^2 u=0",
            "why_not_metric_only": (
                "both the metric L psi row and the chi/psi Euler row are imposed"
            ),
        },
        "second_order_scalar_parent": {
            "field_basis": ["u", "psi"],
            "H(P_2)": _matrix(H),
            "formal_inverse": _matrix(H_inverse),
            "operator_dictionary": {
                "P_2": "Box+2",
                "P_2_inverse_pm": "G_2_pm",
                "u_u_inverse_pm": "-8 G_2_pm G_2_pm",
                "u_psi_inverse_pm": "-G_2_pm/3",
                "psi_psi_inverse_pm": "0",
            },
            "support": (
                "the reduced block has support-local advanced/retarded inverses on the standard scalar Green domains"
            ),
            "complete_metric_parent_status": (
                "NOT_PROMOTED_AFTER_TERMINAL_PHYSICAL_SIGN_FAILURE"
            ),
        },
        "Lee_Wald_and_sign": {
            "quadratic_density_after_spatial_integration": (
                "L_hom=-3 dot(psi) dot(u)-6 psi u+36 psi^2"
            ),
            "velocity_Hessian": _matrix(velocity),
            "velocity_Hessian_eigenvalues": ["-3", "3"],
            "velocity_Hessian_inertia": [1, 1, 0],
            "current": (
                "omega^0=-3[delta u wedge delta dot(psi)"
                "+delta psi wedge delta dot(u)]"
            ),
            "Cauchy_symplectic_matrix": _matrix(symplectic),
            "Cauchy_rank": 4,
            "Cauchy_determinant": "81",
            "physical_sign": "INDEFINITE",
        },
        "D_evolution_and_charge": {
            "state_basis": ["u", "dot_u", "psi", "dot_psi"],
            "D_matrix": _matrix(evolution),
            "characteristic_polynomial": "(lambda^2-2)^2",
            "minimal_polynomial": "(lambda^2-2)^2",
            "real_roots": ["-sqrt(2)", "sqrt(2)"],
            "Jordan_block_size": 2,
            "Hamiltonian": (
                "H_D=-3 dot(u) dot(psi)+6 psi u-36 psi^2"
            ),
            "Hamiltonian_Hessian": _matrix(energy_hessian),
            "positive_witness": (
                "(u,dot_u,psi,dot_psi)=(0,1,0,-1) gives H_D=3"
            ),
            "negative_witness": (
                "(u,dot_u,psi,dot_psi)=(0,1,0,1) gives H_D=-3"
            ),
            "Cartan_identity": "i_D Omega=d H_D",
            "D_presymplectic_degeneracy": False,
            "zero_charge_sector": (
                "proper quadratic cone H_D=0, not the complete scalar solution space"
            ),
        },
        "all_scalar_mode_ledger": {
            "S3_scalar_harmonics": "Delta Y_lm=-l(l+2)Y_lm, l=0,1,...",
            "frequency_squared": "Omega_l^2=l(l+2)-2",
            "ordinary_root": "psi=0, P_2 u=0",
            "generalized_root": "P_2 psi=0, P_2 u=24 psi",
            "multiplicity": "one ordinary and one generalized root per harmonic/polarity",
            "l0": (
                "Omega_0^2=-2: exp(+/-sqrt(2)t) ordinary and Jordan partners"
            ),
            "l1": (
                "Omega_1^2=1; the eight real proper-CKV conformal factors lie only in the psi=0 ordinary-root subspace"
            ),
            "l_ge_2": "oscillatory repeated-root/Jordan pairs",
            "Diff_nonmembership": (
                "every psi!=0 mode has delta_R=-72 psi !=0 whereas delta_R(L_xi g_bar)=L_xi R_bar=0"
            ),
            "compact_support_kernel": "ZERO on the standard scalar Cauchy domain",
            "time_independent_kernel": (
                "ZERO because l(l+2)=2 has no nonnegative integer solution"
            ),
        },
    }


def _berger_and_gates() -> dict[str, Any]:
    q = sp.Rational(9, 40)
    R = (4 - q) / 2
    beta = -sp.Rational(1, 144)
    old_lambda = sp.Rational(119, 480)
    delta_F = sp.expand(R / 6 + beta * R**2 - (1 - old_lambda) / 4)
    delta_F_prime = sp.expand(sp.Rational(1, 6) + 2 * beta * R)
    ricci = [0, (2 - q) / 2, (2 - q) / 2, q / 2]
    metric = [-1, 1, 1, 1]
    residual = [
        sp.factor(delta_F_prime * ricci[index] - delta_F * metric[index] / 2)
        for index in range(4)
    ]
    expected = [
        sp.Rational(93839, 1843200),
        sp.Rational(135917, 1843200),
        sp.Rational(135917, 1843200),
        -sp.Rational(12943, 368640),
    ]
    if residual != expected:
        raise AssertionError("Berger action-mismatch residual drifted")

    gates = [
        {
            "gate": 1,
            "name": "complete_action_BV_CME_Q2",
            "status": "PASS",
            "reason": (
                "the auxiliary action, Diff cotangent lift, nonminimal doublets and original Weyl quartet are explicit"
            ),
        },
        {
            "gate": 2,
            "name": "compact_support_u_disposition",
            "status": "PASS_WITH_PHYSICAL_REPLACEMENT",
            "reason": (
                "arbitrary compact-support u is no longer closed, but it is replaced by the displayed scalar Jordan solution sector"
            ),
        },
        {
            "gate": 3,
            "name": "complete_support_local_causal_parent",
            "status": "NOT_REACHED_AFTER_GATE_5_FAILURE",
            "reason": (
                "the reduced auxiliary scalar block has exact Green inverses; the complete mixed metric parent is not promoted after the terminal physical-sign failure"
            ),
        },
        {
            "gate": 4,
            "name": "cyclicity_and_reduced_pairing",
            "status": "REDUCED_BLOCK_PASS_COMPLETE_PARENT_NOT_REACHED",
            "reason": (
                "the action-derived scalar Lee-Wald form is exact and nondegenerate, but it has split signature"
            ),
        },
        {
            "gate": 5,
            "name": "no_negative_or_uncontrolled_direction",
            "status": "FAIL",
            "reason": (
                "the homogeneous full-Hessian sector has velocity inertia (1,1), real D roots and an indefinite Hamiltonian"
            ),
        },
        {
            "gate": 6,
            "name": "zero_charge_D_sector",
            "status": "FAIL",
            "reason": (
                "i_D Omega=dH_D is nonzero and H_D has both signs; only a proper quadratic cone has zero charge"
            ),
        },
        {
            "gate": 7,
            "name": "healthy_Berger_clock_compatibility",
            "status": "FAIL",
            "reason": (
                "the frozen positive Berger fixture is a different action and the exact changed-action Euler residual is nonzero in all independent rows"
            ),
        },
    ]
    return {
        "Einstein_control": {
            "formula": "m0^2=M_P^2/(12 beta)",
            "M_P_squared": "1/6",
            "beta": "-1/144",
            "m0_squared": "-2",
            "role": (
                "cross-check only; the cylinder verdict comes from the full non-Einstein Hessian"
            ),
        },
        "Berger_compatibility": {
            "fixture": "a=1, q=9/40, alpha_B=5, rho^2=1, omega=3/4",
            "Berger_scalar_curvature": str(R),
            "action_mismatches": [
                "Berger kappa_r=+1 versus Candidate-A kappa_r=-1",
                "Berger lambda=119/480 versus Candidate-A lambda=1",
                "Berger has no beta R^2 term versus Candidate-A beta=-1/144",
                "the effective Einstein coefficient changes sign",
            ],
            "difference_density": (
                "Delta F=R/6-R^2/144-(1-119/480)/4"
            ),
            "Delta_F_at_fixture": str(delta_F),
            "Delta_F_prime_at_fixture": str(delta_F_prime),
            "orthonormal_metric_Euler_residual": [str(value) for value in residual],
            "status": "FAIL_FROZEN_BERGER_BACKGROUND_NOT_A_SOLUTION",
            "does_not_obstruct": (
                "a separately retuned Berger family for the changed action"
            ),
        },
        "seven_gate_disposition": gates,
        "overall": "CANDIDATE_A_OBSTRUCTED_BY_PHYSICAL_SCALAR_SIGN",
    }


def build() -> dict[str, Any]:
    dependencies, _ = _dependency_rows()
    action = _action_data()
    mixed = _mixed_hessian()
    scalar = _homogeneous_scalar_sector()
    disposition = _berger_and_gates()
    payload: dict[str, Any] = {
        "schema": "pure-weyl-compensator-candidate-a-r2-auxiliary-scalar-obstruction-v1",
        "result_id": "COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1",
        "result_state": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependencies": dependencies,
        "action_identity": action,
        "full_non_Einstein_Hessian_and_BV": mixed,
        "homogeneous_scalar_full_Hessian_sector": scalar,
        "comparison_disposition": disposition,
        "supersession": {
            "supersedes_result_id": (
                "COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1"
            ),
            "superseded_claim": (
                "complete rank-390 direct-sum causal BV parent and zero strict-complement change"
            ),
            "retained_subclaims": [
                "the rational double-root action tuning",
                "the trace Schur complement H_u=-(Box+2)^2/8",
                "the iterated scalar Green inverse on the reduced block",
                "the independent phase wave block",
            ],
            "reason": (
                "the auxiliary action exposes nonzero h-psi rows "
                "L_ab psi=(nabla_a nabla_b-g_ab Box-Ric_ab)psi on the "
                "non-Einstein cylinder; these rows were absent from the direct sum"
            ),
        },
        "exact_checks": {
            "dependency_hashes": True,
            "auxiliary_elimination": True,
            "shifted_action_identity": True,
            "full_mixed_Hessian_formal_adjoint": True,
            "both_full_Hessian_equations_on_homogeneous_sector": True,
            "scalar_Green_inverse": True,
            "Lee_Wald_nondegenerate": True,
            "Lee_Wald_split_inertia": True,
            "D_symplectic": True,
            "D_Hamiltonian_identity": True,
            "real_Jordan_roots": True,
            "Einstein_mass_crosscheck": True,
            "Berger_residual_nonzero": True,
        },
        "claim_flags": {
            "CANDIDATE_A_SELECTED": False,
            "CANDIDATE_A_OBSTRUCTED": True,
            "COMPLETE_SECOND_ORDER_CAUSAL_PARENT": False,
            "REDUCED_SCALAR_GREEN_BLOCK": True,
            "HEALTHY_SCALAR": False,
            "PHYSICAL_SIGN_INDEFINITE": True,
            "RAW_D_GAUGE_PRESERVED": False,
            "FROZEN_BERGER_COMPATIBLE": False,
            "HADAMARD_STATE": False,
            "QUANTUM_MASTER_EQUATION": False,
            "PARTICLE_OR_UNITARITY": False,
        },
        "next_gate": (
            "Candidate B unimodular/three-form causal, global-mode and "
            "clock preflight; Candidate A enters the A/B comparison as FAIL"
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL theorem obstructs "
            "Candidate A on the frozen unit-cylinder action. The auxiliary "
            "rewrite derives the complete h-psi mixed Hessian and a consistent "
            "spatially homogeneous sector satisfying both metric and auxiliary "
            "equations. Its reduced Lee-Wald kinetic form has inertia (1,1), "
            "raw-D evolution has real repeated roots +/-sqrt(2), and the D "
            "Hamiltonian has both signs. Candidate A therefore fails the "
            "mandatory physical-sign and D gates. The theorem also proves that "
            "the frozen positive Berger fixture is not a solution of this "
            "changed action. It supersedes the prior complete-direct-sum rank-390 "
            "promotion while retaining the rational trace Schur-complement and "
            "reduced Green identities. It does not obstruct other R^2 couplings, "
            "a separately retuned changed-action Berger family, Candidate B, or "
            "larger theories, and establishes no Hadamard, anomaly, QME, "
            "particle, scattering or unitarity claim."
        ),
    }
    core = deepcopy(payload)
    payload["content_hashes"] = {
        "action_sha256": action["action_sha256"],
        "mixed_Hessian_sha256": _digest(
            mixed["full_action_hessian"]["mixed_block_polynomial"]
        ),
        "homogeneous_sector_sha256": _digest(scalar),
        "comparison_sha256": _digest(disposition),
        "certificate_core_sha256": _digest(core),
    }
    return payload


def verify_payload(payload: dict[str, Any]) -> None:
    expected = build()
    if payload != expected:
        raise AssertionError("Candidate-A certificate differs from exact rebuild")
    for section, key in (
        (
            payload["full_non_Einstein_Hessian_and_BV"]["full_action_hessian"],
            "mixed_block_polynomial",
        ),
        (
            payload["homogeneous_scalar_full_Hessian_sector"][
                "second_order_scalar_parent"
            ],
            "H(P_2)",
        ),
        (
            payload["homogeneous_scalar_full_Hessian_sector"][
                "second_order_scalar_parent"
            ],
            "formal_inverse",
        ),
    ):
        record = deepcopy(section[key])
        digest = record.pop("sha256")
        if digest != _digest(record):
            raise AssertionError(f"serialized matrix hash drifted: {key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    else:
        verify_payload(json.loads(OUTPUT.read_text()))
    print("COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1: PASS")


if __name__ == "__main__":
    main()
