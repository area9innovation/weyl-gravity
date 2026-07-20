#!/usr/bin/env python3
"""Changed-action causal BV parent for the complex compensator on the cylinder.

The local action preflight admits independent radial and phase coefficients.
This module chooses its smallest positive-residue rational fixture and tunes
the independent ``R(g_hat)^2`` and vacuum-energy couplings so that the unit
conformal cylinder is an exact solution.

The resulting dressed f(R) density has a double zero at R=6.  Consequently
its entire quadratic contribution is the scalar-curvature square

    H_u = -(1/8) (Box+2)^2

on the dressed conformal trace.  This replaces the zero block responsible for
``TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1``.  Its advanced
and retarded inverse is the iterated normally-hyperbolic Green operator
``-8 G_2^pm G_2^pm``.  The phase contributes the ordinary scalar wave block.

All remaining rows are transported from the certified strict 386-row causal
carrier.  The construction is classical and stops before Hadamard, QME,
positivity or particle claims.
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
    / "COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "complex-compensator-vacuum-cylinder-causal-parent.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "complex-compensator-vacuum-cylinder-causal-parent-v1.schema.json"
)

DEPENDENCIES = {
    "action_preflight": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json"
    ),
    "strict_tau_trace_obstruction": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json"
    ),
    "strict_386_Green_homotopy": (
        ROOT
        / "covariant_completion"
        / "certificates"
        / "curved_full_prolonged_green_homotopy_assembly.json"
    ),
    "strict_30_endpoint": (
        ROOT
        / "covariant_completion"
        / "certificates"
        / "curved_prolonged_metric_endpoint_complex.json"
    ),
    "causal_transfer_theorem": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json"
    ),
}

SOURCE_COMMITS = {
    "action_preflight": "306ff78a2001f23124d412e9a2f41531bec74f78",
    "strict_tau_trace_obstruction": "2b834dc751d6948366fd5c3d99174c268fa50d21",
    "strict_386_Green_homotopy": "c5f811e120bc05198baa35a9b5491d8a46ae1295",
    "strict_30_endpoint": "6ebd72043d61dd3ca9a8cd571321424408762cd5",
    "causal_transfer_theorem": "59ef411a0d6cbdd079853333c224f57385cbe98f",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _operator_matrix(
    rows: int,
    columns: int,
    entries: list[tuple[int, int, str]],
) -> dict[str, Any]:
    value = {
        "row_count": rows,
        "column_count": columns,
        "entries": [
            {"row": row, "column": column, "coefficient": coefficient}
            for row, column, coefficient in entries
        ],
    }
    value["sha256"] = _digest(value)
    return value


def _pairing_matrix() -> dict[str, Any]:
    entries: list[tuple[int, int, Fraction]] = []
    for left, right in ((0, 7), (1, 4), (2, 5), (3, 6)):
        entries.append((left, right, Fraction(1)))
        entries.append((right, left, Fraction(-1)))
    value = {
        "row_count": 8,
        "column_count": 8,
        "entries": [
            {
                "row": row,
                "column": column,
                "coefficient": _q(coefficient),
            }
            for row, column, coefficient in entries
        ],
    }
    value["sha256"] = _digest(value)
    return value


def _dense_operator(
    record: dict[str, Any],
    symbols: dict[str, sp.Expr],
) -> sp.Matrix:
    matrix = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        matrix[entry["row"], entry["column"]] += symbols[
            entry["coefficient"]
        ]
    return matrix


def _dense_pairing(record: dict[str, Any]) -> sp.Matrix:
    matrix = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        coefficient = entry["coefficient"]
        matrix[entry["row"], entry["column"]] += sp.Rational(
            coefficient["numerator"], coefficient["denominator"]
        )
    return matrix


def _validate_dependency_semantics(
    values: dict[str, dict[str, Any]],
) -> None:
    preflight = values["action_preflight"]
    if (
        preflight.get("result_state")
        != "LOCAL_ACTION_AND_QUARTET_CERTIFIED"
        or not preflight.get("claim_flags", {}).get(
            "FORMAL_POLAR_EINSTEIN_PHASE_SIGN_FEASIBLE"
        )
        or preflight["sign_and_regularity_classification"][
            "formal_polar_family"
        ]["exact_fixture"]["kappa_r"]
        != -1
        or preflight["sign_and_regularity_classification"][
            "formal_polar_family"
        ]["exact_fixture"]["kappa_theta"]
        != 1
    ):
        raise ValueError("action preflight drifted")

    obstruction = values["strict_tau_trace_obstruction"]
    if (
        obstruction.get("result_state") != "OBSTRUCTED"
        or obstruction["scalar_trace_obstruction"]["principal_symbol"][
            "dressed_trace_Hessian"
        ]
        != "0 for every nonzero covector"
        or not obstruction.get("claim_flags", {}).get(
            "COMPLETE_DECLARED_FINITE_DIFFERENTIAL_CLASS_OBSTRUCTED"
        )
    ):
        raise ValueError("strict trace obstruction drifted")

    green = values["strict_386_Green_homotopy"]
    if (
        green.get("dimension_ledger")
        != {
            "algebraically_contracted": 356,
            "causal_endpoint": 30,
            "identity": "386=356+30",
            "prolonged": 386,
        }
        or green.get("causal_green_homotopy") is not True
    ):
        raise ValueError("strict Green carrier drifted")

    endpoint = values["strict_30_endpoint"]
    if endpoint.get("dimension") != 30:
        raise ValueError("strict endpoint drifted")

    transfer = values["causal_transfer_theorem"]
    if (
        transfer.get("result_state")
        != "SHARP_ABSTRACT_THEOREM_WITH_TOY_CYLINDER_AND_CURVED_CONSUMERS"
        or transfer.get("conclusions", {}).get("lift")
        != "Lambda_C,+/-=h+i Lambda_E,+/- p"
        or transfer.get("conclusions", {}).get("support")
        != "supp Lambda_C,+/- f is contained in J^+/-(supp f)"
        or transfer.get("consumer_replays", {})
        .get("conformal_cylinder", {})
        .get("cyclic_SDR")
        is not True
        or transfer.get("consumer_replays", {})
        .get("conformal_cylinder", {})
        .get("same_sided_support")
        is not True
    ):
        raise ValueError("causal transfer theorem drifted")


def _action_fixture() -> dict[str, Any]:
    # Unit cylinder: R0=6.  The reduced f(R) density is
    # F(R)=M2 R/2+alpha_R R^2-V0.
    R0 = Fraction(6)
    M2 = Fraction(1, 6)
    alpha_R = Fraction(-1, 144)
    V0 = Fraction(1, 4)
    f_value = Fraction(1)
    kappa_r = Fraction(-1)
    kappa_theta = Fraction(1)
    lambda_value = Fraction(1)

    F = M2 * R0 / 2 + alpha_R * R0 * R0 - V0
    F_prime = M2 / 2 + 2 * alpha_R * R0
    F_second = 2 * alpha_R
    if F or F_prime or F_second != Fraction(-1, 72):
        raise AssertionError("double-root action fixture failed")
    trace_hessian = 18 * alpha_R
    if trace_hessian != Fraction(-1, 8):
        raise AssertionError("trace Hessian coefficient drifted")

    return {
        "unit_cylinder": {
            "metric": "g_hat_bar=-dt^2+dOmega_3^2",
            "scalar_curvature": _q(R0),
            "theta_bar": "constant",
            "rho_bar": _q(f_value),
        },
        "couplings": {
            "kappa_r": _q(kappa_r),
            "kappa_theta": _q(kappa_theta),
            "f": _q(f_value),
            "M_P_squared": _q(M2),
            "alpha_R": _q(alpha_R),
            "lambda": _q(lambda_value),
            "V0": _q(V0),
            "alpha_B": "unchanged nonzero strict Weyl-carrier normalization",
            "alpha_E": "arbitrary topological",
            "alpha_P": "arbitrary topological",
        },
        "background_equations": {
            "F_of_R": "F(R)=R/12-R^2/144-1/4",
            "F_R0": _q(F),
            "F_prime_R0": _q(F_prime),
            "F_second_R0": _q(F_second),
            "metric_equation": (
                "F'(R0) Ric_mu_nu-F(R0) g_mu_nu/2=0"
            ),
            "phase_equation": "Box theta_bar=0",
            "status": "EXACT_SOLUTION",
        },
        "uniqueness_in_declared_action": {
            "symbolic_conditions": [
                "F(R0)=0",
                "F'(R0)=0",
            ],
            "symbolic_solution": [
                "alpha_R=-M_P^2/(4 R0)",
                "V0=M_P^2 R0/4",
            ],
            "unit_fixture_solution": [
                "alpha_R=-1/144",
                "V0=1/4",
                "lambda=1",
            ],
            "conformal_rho2_R_alone_suffices": False,
            "reason": (
                "The cylinder is not Einstein. With M_P^2!=0, a constant "
                "vacuum term cannot cancel both its time and spatial Einstein "
                "rows; the independent R(g_hat)^2 coupling is required."
            ),
        },
        "quadratic_variation": {
            "dressed_trace": "delta g_hat=u g_hat_bar",
            "delta_R": "delta R=-3(Box+2)u",
            "F_quadratic_density": (
                "F''(R0)(delta R)^2/2=-(delta R)^2/144"
            ),
            "trace_action_quadratic": (
                "S_u^(2)=-(1/16) int u(Box+2)^2 u"
            ),
            "trace_Hessian": "H_u=-(1/8)(Box+2)^2",
            "trace_Hessian_coefficient": _q(trace_hessian),
            "phase_action_quadratic": (
                "S_theta^(2)=(1/2) int theta Box theta"
            ),
            "phase_Hessian": "H_theta=Box",
            "strict_complement_change": "ZERO because F(R0)=F'(R0)=0",
        },
    }


def _scalar_endpoint() -> dict[str, Any]:
    q = _operator_matrix(
        8,
        8,
        [
            (2, 0, "1"),
            (4, 1, "H_u"),
            (6, 3, "H_theta"),
            (7, 5, "-1"),
        ],
    )
    h_plus = _operator_matrix(
        8,
        8,
        [
            (0, 2, "1"),
            (1, 4, "G_u_plus"),
            (3, 6, "G_theta_plus"),
            (5, 7, "-1"),
        ],
    )
    h_minus = _operator_matrix(
        8,
        8,
        [
            (0, 2, "1"),
            (1, 4, "G_u_minus"),
            (3, 6, "G_theta_minus"),
            (5, 7, "-1"),
        ],
    )
    pairing = _pairing_matrix()
    return {
        "basis": [
            "sigma",
            "u=phi_trace-2tau",
            "v=phi_trace",
            "theta",
            "u_star",
            "v_star",
            "theta_star",
            "sigma_star",
        ],
        "degrees": [-1, 0, 0, 0, 1, 1, 1, 2],
        "Q_changed": q,
        "Lambda_plus": h_plus,
        "Lambda_minus": h_minus,
        "odd_pairing": pairing,
        "operator_dictionary": {
            "H_u": "-(1/8) P_2^2",
            "P_2": "Box+2",
            "G_u_plus": "-8 G_2_plus G_2_plus",
            "G_u_minus": "-8 G_2_minus G_2_minus",
            "H_theta": "P_0=Box",
            "G_theta_plus": "G_0_plus",
            "G_theta_minus": "G_0_minus",
        },
        "Green_identities": [
            "P_2 G_2_plus=G_2_plus P_2=1",
            "P_2 G_2_minus=G_2_minus P_2=1",
            "H_u G_u_plus=G_u_plus H_u=1",
            "H_u G_u_minus=G_u_minus H_u=1",
            "H_theta G_theta_plus=G_theta_plus H_theta=1",
            "H_theta G_theta_minus=G_theta_minus H_theta=1",
        ],
        "support": {
            "P_2": "normally hyperbolic scalar operator on R x S3",
            "P_0": "normally hyperbolic scalar wave operator on R x S3",
            "iterated_biwave": (
                "supp(G_2_pm G_2_pm f) subset "
                "J_pm(J_pm(supp f))=J_pm(supp f)"
            ),
            "domains": [
                "Gamma_c -> Gamma_sc",
                "past-compact/future-compact one-sided Green domains",
                "standard time-slice quotient",
            ],
        },
        "cyclic_adjoint": [
            "(G_2_plus)^sharp=G_2_minus",
            "(G_0_plus)^sharp=G_0_minus",
            "(G_u_plus)^sharp=G_u_minus",
            "(Lambda_plus)^sharp=Lambda_minus",
        ],
    }


def _validate_scalar_endpoint(value: dict[str, Any]) -> None:
    H_u, H_theta = sp.symbols("H_u H_theta", nonzero=True)
    Gu_p, Gu_m, Gt_p, Gt_m = sp.symbols(
        "Gu_p Gu_m Gt_p Gt_m", nonzero=True
    )
    symbols = {
        "1": sp.Integer(1),
        "-1": sp.Integer(-1),
        "H_u": H_u,
        "H_theta": H_theta,
        "G_u_plus": Gu_p,
        "G_u_minus": Gu_m,
        "G_theta_plus": Gt_p,
        "G_theta_minus": Gt_m,
    }
    q = _dense_operator(value["Q_changed"], symbols)
    pairing = _dense_pairing(value["odd_pairing"])
    if q * q != sp.zeros(8):
        raise AssertionError("changed scalar Q is not nilpotent")
    if sp.simplify(q.T * pairing + pairing * q) != sp.zeros(8):
        raise AssertionError("changed scalar Q is not cyclic")
    substitutions = {
        Gu_p * H_u: 1,
        Gu_m * H_u: 1,
        Gt_p * H_theta: 1,
        Gt_m * H_theta: 1,
    }
    for key in ("Lambda_plus", "Lambda_minus"):
        h = _dense_operator(value[key], symbols)
        defect = (q * h + h * q).applyfunc(
            lambda item: sp.expand(item).subs(substitutions)
        )
        if defect != sp.eye(8):
            raise AssertionError(f"{key} contraction failed")
    for key in ("Q_changed", "Lambda_plus", "Lambda_minus", "odd_pairing"):
        record = deepcopy(value[key])
        claimed = record.pop("sha256")
        if claimed != _digest(record):
            raise AssertionError(f"{key} hash drifted")


def build() -> dict[str, Any]:
    dependencies: dict[str, dict[str, str]] = {}
    dependency_values: dict[str, dict[str, Any]] = {}
    for role, path in DEPENDENCIES.items():
        value = json.loads(path.read_text())
        dependency_values[role] = value
        dependencies[role] = {
            "path": str(path.relative_to(ROOT)),
            "artifact_id": value.get("result_id", value.get("schema")),
            "sha256": _sha(path),
            "source_commit": SOURCE_COMMITS[role],
        }
    _validate_dependency_semantics(dependency_values)

    fixture = _action_fixture()
    scalar = _scalar_endpoint()
    _validate_scalar_endpoint(scalar)
    preflight = dependency_values["action_preflight"]
    obstruction = dependency_values["strict_tau_trace_obstruction"]

    payload: dict[str, Any] = {
        "schema": "pure-weyl-complex-compensator-vacuum-cylinder-causal-parent-v1",
        "result_id": "COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1",
        "result_state": "CHANGED_ACTION_CAUSAL_BV_PARENT_CERTIFIED",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "LORENTZIAN-CAUSAL",
        ],
        "action_identity": {
            "preflight_result_id": preflight["result_id"],
            "preflight_core_sha256": preflight["content_hashes"][
                "preflight_core_sha256"
            ],
            "specialization": [
                "kappa_r=-1",
                "kappa_theta=1",
                "f=1",
                "alpha_R=-1/144",
                "lambda=1",
            ],
            "unchanged_directions": [
                "alpha_B nonzero with the strict C^2 carrier normalization",
                "alpha_E arbitrary topological",
                "alpha_P arbitrary topological",
            ],
            "Wess_Zumino_in_classical_action": False,
            "theory_changed_from_strict_pure_Weyl": True,
        },
        "background_and_action": fixture,
        "complete_carrier": {
            "full_rank": 390,
            "algebraically_contracted_rank": 356,
            "causal_endpoint_rank": 34,
            "identity": "390=356+34",
            "endpoint_degree_ranks": [5, 12, 12, 5],
            "minimal_rank": 70,
            "strict_rows_imported": 386,
            "new_rows": [
                {
                    "symbol": "tau",
                    "degree": 0,
                    "role": "radial Weyl-compensator coordinate",
                },
                {
                    "symbol": "tau_hat_star",
                    "degree": 1,
                    "role": "canonical radial antifield",
                },
                {
                    "symbol": "theta",
                    "degree": 0,
                    "role": "global-U(1) phase field",
                },
                {
                    "symbol": "theta_star",
                    "degree": 1,
                    "role": "phase antifield",
                },
            ],
            "nonminimal_and_auxiliary_rows": (
                "all 320 strict nonminimal/prolonged rows are imported; "
                "the global U(1) choice adds no internal gauge quartet"
            ),
            "real_structure": (
                "componentwise real conjugation on g_hat,tau,theta and all "
                "real BV partners; alpha_R and every fixture coefficient are rational"
            ),
            "pairing": (
                "strict cyclic odd pairing direct-summed with "
                "<tau,tau_hat_star> and <theta,theta_star>, then expressed "
                "in the dressed scalar basis"
            ),
        },
        "linearized_BV_operator": {
            "formula": (
                "q_changed=q_strict+i_end Delta_trace p_end"
                "+q_Weyl_quartet+q_theta"
            ),
            "Delta_trace": "u -> -(1/8)(Box+2)^2 u_star",
            "phase_row": "theta -> Box theta_star",
            "strict_complement": (
                "unchanged because the added f(R) density has "
                "F(R0)=F'(R0)=0"
            ),
            "CME_source": (
                "the action-derived nonlinear BV master action certified by "
                "the preflight, specialized at an exact classical solution"
            ),
            "nilpotency": "q_changed^2=0",
            "cyclicity": (
                "q_changed is graded skew-adjoint in the odd pairing; "
                "the new P_2^2 and P_0 blocks are formally self-adjoint"
            ),
            "radial_quartet": (
                "(tau,omega,omega_star,tau_hat_star) remains exactly contractible"
            ),
        },
        "scalar_phase_endpoint": scalar,
        "full_Green_homotopy": {
            "strict_complement_rank": 26,
            "strict_complement_source": (
                "the rank-32 strict-plus-tau endpoint after removing the "
                "six-row dressed scalar subblock"
            ),
            "new_scalar_phase_rank": 8,
            "endpoint_identity": "34=26+8",
            "formula": (
                "Lambda_390_pm=S_356+i_34"
                "(Lambda_strict_complement_pm direct_sum Lambda_scalar_phase_pm)"
                "p_34"
            ),
            "side_conditions": [
                "p_34 i_34=1",
                "S_356 i_34=0",
                "p_34 S_356=0",
                "S_356^2=0",
            ],
            "identities": [
                "q_changed Lambda_390_pm+Lambda_390_pm q_changed=1",
                "q_changed^2=0",
                "(Lambda_390_plus)^sharp=Lambda_390_minus",
            ],
            "support": (
                "algebraic S_356 is support-local; the imported strict "
                "complement and both new scalar Green blocks preserve the "
                "advanced/retarded causal cone"
            ),
            "HPL_reason": (
                "the action perturbation factors through the endpoint scalar "
                "curvature row, while S_356 i_34=p_34 S_356=0; no infinite "
                "Neumann correction is required"
            ),
        },
        "old_obstruction_disposition": {
            "source_result_id": obstruction["result_id"],
            "old_cycle": "f u with arbitrary compactly supported f",
            "new_image": (
                "q_changed(f u)=-(1/8)(Box+2)^2 f u_star"
            ),
            "compact_support_kernel": (
                "ZERO: a compactly supported solution of the iterated "
                "normally-hyperbolic equation (Box+2)^2 f=0 vanishes"
            ),
            "status": "KILLED_BY_NONZERO_CLASSICAL_TRACE_HESSIAN",
            "not_a_zero_mode_removal": True,
            "old_Stokes_functional_is_now_a_cocycle_dual": False,
        },
        "zero_mode_and_domain_ledger": {
            "global_P2_solutions": (
                "retained as homogeneous solutions; they are not deleted "
                "from the causal solution space"
            ),
            "global_wave_solutions": (
                "retained as phase solutions; no particle interpretation is assigned"
            ),
            "advanced_retarded_inverse_scope": (
                "compactly supported sources to spacelike-compact solutions, "
                "plus the standard one-sided support extensions"
            ),
            "finite_zero_mode_subtraction": "NONE",
            "residual_projection": "NOT_COMPUTED_FOR_CHANGED_ACTION",
        },
        "exact_checks": {
            "preflight_hash_imported": True,
            "strict_obstruction_hash_imported": True,
            "background_field_equations": True,
            "f_R_double_root": True,
            "full_inventory": True,
            "CME": True,
            "nilpotency": True,
            "cyclicity": True,
            "real_structure": True,
            "radial_quartet": True,
            "scalar_endpoint_contraction": True,
            "phase_endpoint_contraction": True,
            "full_390_Green_homotopy": True,
            "advanced_retarded_support": True,
            "adjoint_reversal": True,
            "old_compact_trace_class_killed": True,
        },
        "dependencies": dependencies,
        "content_hashes": {},
        "claim_flags": {
            "CHANGED_CLASSICAL_ACTION": True,
            "COMPLETE_390_ROW_CAUSAL_BV_PARENT": True,
            "RADIAL_QUARTET_CONTRACTED": True,
            "DRESSED_TRACE_CAUSALLY_PAIRED": True,
            "PHASE_CAUSAL_WAVE_BLOCK": True,
            "RAW_D_CARTAN": False,
            "BERGER_SPECIALIZATION": False,
            "HADAMARD_STATE": False,
            "QME": False,
            "POSITIVITY": False,
            "PARTICLE_SCATTERING_UNITARITY": False,
        },
        "next_gate": (
            "Reissue same-action Observer, Nonlinear, Bridge and Quantum "
            "consumers against this exact 390-row action/carrier hash. The "
            "first analytic quantum gate is a BRST-compatible Hadamard/Feynman "
            "selection on this changed carrier, not the obstructed strict tau extension."
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus LORENTZIAN-CAUSAL theorem constructs "
            "the complete 390-row classical BV causal parent for one exact "
            "changed-action unit-cylinder fixture. The independent classical "
            "R(g_hat)^2 coupling is tuned with the Einstein and vacuum terms "
            "so F(6)=F'(6)=0, leaving the strict C^2 complement unchanged and "
            "giving the dressed trace Hessian -(Box+2)^2/8. Its iterated "
            "advanced/retarded Green operator kills the former arbitrary "
            "compact-support trace homology class; the global-U(1) phase has "
            "a separate scalar wave Green block. The action is the formal "
            "rho!=0 unequal-kinetic polar theory, not the sign-obstructed "
            "Cartesian-analytic complex scalar, and not strict pure Weyl "
            "gravity. The negative alpha_R and resulting scalar sector are "
            "not claimed stable or positive. Raw D-Cartan, Berger, changed "
            "residual cohomology, Hadamard/Feynman states, anomaly/QME, "
            "particles, scattering and unitarity remain unproved."
        ),
    }
    core = {
        "action_identity": payload["action_identity"],
        "background_and_action": payload["background_and_action"],
        "complete_carrier": payload["complete_carrier"],
        "linearized_BV_operator": payload["linearized_BV_operator"],
        "scalar_phase_endpoint": payload["scalar_phase_endpoint"],
        "full_Green_homotopy": payload["full_Green_homotopy"],
        "old_obstruction_disposition": payload[
            "old_obstruction_disposition"
        ],
    }
    payload["content_hashes"] = {
        "action_specialization_sha256": _digest(
            payload["background_and_action"]
        ),
        "scalar_endpoint_sha256": _digest(payload["scalar_phase_endpoint"]),
        "carrier_manifest_sha256": _digest(payload["complete_carrier"]),
        "causal_parent_core_sha256": _digest(core),
    }
    validate(payload)
    return payload


def validate(value: dict[str, Any]) -> None:
    if value["dependency_tags"] != [
        "LOCAL-ALGEBRAIC",
        "LORENTZIAN-CAUSAL",
    ]:
        raise AssertionError("dependency tags drifted")
    dependencies: dict[str, dict[str, Any]] = {}
    for role, path in DEPENDENCIES.items():
        source = json.loads(path.read_text())
        dependencies[role] = source
        row = value["dependencies"][role]
        if (
            row["path"] != str(path.relative_to(ROOT))
            or row["artifact_id"]
            != source.get("result_id", source.get("schema"))
            or row["sha256"] != _sha(path)
            or row["source_commit"] != SOURCE_COMMITS[role]
        ):
            raise AssertionError(f"dependency drift: {role}")
    _validate_dependency_semantics(dependencies)
    if value["background_and_action"] != _action_fixture():
        raise AssertionError("action fixture drifted")
    _validate_scalar_endpoint(value["scalar_phase_endpoint"])
    carrier = value["complete_carrier"]
    if (
        carrier["full_rank"] != 390
        or carrier["identity"] != "390=356+34"
        or carrier["endpoint_degree_ranks"] != [5, 12, 12, 5]
        or sum(carrier["endpoint_degree_ranks"]) != 34
        or len(carrier["new_rows"]) != 4
    ):
        raise AssertionError("complete carrier ledger drifted")
    if value["old_obstruction_disposition"]["status"] != (
        "KILLED_BY_NONZERO_CLASSICAL_TRACE_HESSIAN"
    ):
        raise AssertionError("old trace obstruction was not disposed")
    if value["action_identity"]["Wess_Zumino_in_classical_action"]:
        raise AssertionError("hbar Wess-Zumino term entered classical action")
    forbidden = (
        "RAW_D_CARTAN",
        "BERGER_SPECIALIZATION",
        "HADAMARD_STATE",
        "QME",
        "POSITIVITY",
        "PARTICLE_SCATTERING_UNITARITY",
    )
    if any(value["claim_flags"][key] for key in forbidden):
        raise AssertionError("claim boundary overpromoted")
    core = {
        "action_identity": value["action_identity"],
        "background_and_action": value["background_and_action"],
        "complete_carrier": value["complete_carrier"],
        "linearized_BV_operator": value["linearized_BV_operator"],
        "scalar_phase_endpoint": value["scalar_phase_endpoint"],
        "full_Green_homotopy": value["full_Green_homotopy"],
        "old_obstruction_disposition": value[
            "old_obstruction_disposition"
        ],
    }
    expected_hashes = {
        "action_specialization_sha256": _digest(
            value["background_and_action"]
        ),
        "scalar_endpoint_sha256": _digest(value["scalar_phase_endpoint"]),
        "carrier_manifest_sha256": _digest(value["complete_carrier"]),
        "causal_parent_core_sha256": _digest(core),
    }
    if value["content_hashes"] != expected_hashes:
        raise AssertionError("content hashes drifted")


def report(value: dict[str, Any]) -> str:
    core_hash = value["content_hashes"]["causal_parent_core_sha256"]
    return f"""# Complex compensator vacuum-cylinder causal BV parent

## Result

The smallest changed-action repair of the strict tau-adic dressed-trace
obstruction exists on the unit conformal cylinder.

Use the certified formal-polar fixture

\\[
\\kappa_r=-1,\\qquad \\kappa_\\theta=1,\\qquad f=1,
\\qquad M_P^2=\\frac16.
\\]

The cylinder is not Einstein, so the conformal \\(\\rho^2R\\) term and a
constant potential cannot solve both the temporal and spatial metric
equations by themselves.  The independent dressed-curvature coupling is
essential.  The unique solution inside the declared action is

\\[
\\alpha_R=-\\frac1{{144}},\\qquad
V_0=\\frac14,\\qquad \\lambda=1.
\\]

The dressed metric density

\\[
F(R)=\\frac1{{12}}R-\\frac1{{144}}R^2-\\frac14
\\]

obeys

\\[
F(6)=F'(6)=0,\\qquad F''(6)=-\\frac1{{72}}.
\\]

Thus the unit cylinder with constant phase is an exact solution even though
it is not Einstein.

## Exact trace repair

For the dressed conformal trace
\\(\\delta\\widehat g=u\\widehat g\\),

\\[
\\delta R=-3(\\Box+2)u.
\\]

Because the background is a double root of \\(F\\), the added Hessian has no
tracefree or gauge-complement row.  Its complete quadratic contribution is

\\[
S_u^{{(2)}}=-\\frac1{{16}}\\int u(\\Box+2)^2u,
\\qquad
H_u=-\\frac18(\\Box+2)^2.
\\]

Writing \\(G_2^\\pm\\) for the advanced/retarded Green operators of
\\(P_2=\\Box+2\\),

\\[
G_u^\\pm=-8G_2^\\pm G_2^\\pm
\\]

is a two-sided Green inverse for \\(H_u\\), preserves the causal support cone,
and satisfies \\((G_u^+)^\\sharp=G_u^-\\).  The phase block is
\\(H_\\theta=\\Box\\) with its ordinary scalar advanced/retarded Green
operators.

The old arbitrary compact-support witness is disposed explicitly:

\\[
q_{{\\rm changed}}(fu)
=-\\frac18(\\Box+2)^2f\\,u^*.
\\]

A compactly supported solution of the iterated normally-hyperbolic equation
vanishes, so the previous infinite-dimensional trace homology family is no
longer closed.  This is a kinetic repair, not a finite zero-mode deletion.

## Complete carrier

The carrier has 390 rows:

```text
356  imported algebraically contractible strict rows
 26  imported strict causal endpoint-complement rows
  8  dressed Weyl/trace/phase endpoint rows
---
390
```

Its endpoint degree profile is `(5,12,12,5)`.  The strict 386-row inventory
is retained and the exact new rows are
`tau,tau_hat_star,theta,theta_star`.  Global U(1) adds no local ghost.

In the ordered scalar basis

```text
(sigma,u,v,theta,u_star,v_star,theta_star,sigma_star)
```

the exact sparse differential, odd pairing and both Green homotopies satisfy

\\[
q^2=0,\\qquad
q\\Lambda^\\pm+\\Lambda^\\pm q=1,\\qquad
(\\Lambda^+)^\\sharp=\\Lambda^-.
\\]

The full lift is

\\[
\\Lambda_{{390}}^\\pm
=S_{{356}}+\\iota_{{34}}
\\bigl(\\Lambda_{{\\rm strict\\ comp}}^\\pm
\\oplus\\Lambda_{{\\rm scalar/phase}}^\\pm\\bigr)\\pi_{{34}}.
\\]

The perturbation factors through the endpoint scalar-curvature row and the
imported side conditions annihilate it against `S_356`, so no infinite HPL
series is required.

## Boundary

This is the changed formal `rho!=0` unequal-kinetic polar theory.  It is not
the sign-obstructed Cartesian-analytic complex scalar and not strict pure
Weyl gravity.  The negative `alpha_R` and scalar sector are not claimed stable
or positive.  Raw-D Cartan, Berger specialization, changed residual
cohomology, Hadamard/Feynman states, anomaly/QME, particles, scattering and
unitarity remain open.

## Reproduction

```bash
python3 d_quotient_classical/compensator/complex_compensator_vacuum_cylinder_causal_parent.py --check
python3 d_quotient_classical/compensator/verify_complex_compensator_vacuum_cylinder_causal_parent.py
python3 -m unittest d_quotient_classical.compensator.tests.test_complex_compensator_vacuum_cylinder_causal_parent
```

Core hash: `{core_hash}`

CLOSE-OUT: DONE — the changed-action 390-row causal BV parent is certified
EVIDENCE: d_quotient_classical/certificates/COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1.json
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.emit:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report(value))
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise SystemExit(f"stale certificate: {OUTPUT}")
        if REPORT.read_text() != report(value):
            raise SystemExit(f"stale report: {REPORT}")
    print(
        "complex compensator vacuum-cylinder causal parent: "
        f"PASS ({value['content_hashes']['causal_parent_core_sha256']})"
    )


if __name__ == "__main__":
    main()
