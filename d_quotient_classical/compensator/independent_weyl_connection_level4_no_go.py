#!/usr/bin/env python3
"""Exact Level-4 rank/charge no-go for one real independent Weyl connection."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_INDEPENDENT_WEYL_CONNECTION_LEVEL4_NO_GO_V1.json"
)
LEVEL3 = {
    "path": (
        ROOT
        / "d_quotient_classical/certificates/"
        "COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1.json"
    ),
    "sha256": "2e687331b6985b3a84c54a0f05b210bee5e3ac06d5659b5603ac9bc25f61dfed",
    "source_commit": "e77ee444450890dd1df720f70c5ef5ab202fe8cc",
    "result_id": (
        "COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1"
    ),
    "result_state": (
        "SCOPED_LEVEL3_LITERAL_CURVATURE_COUPLING_GOOD_LOCUS_EMPTY"
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: sp.Expr) -> str:
    return str(sp.factor(value))


def _matrix(value: sp.Matrix) -> dict[str, Any]:
    core = {
        "row_count": value.rows,
        "column_count": value.cols,
        "entries": [
            {"row": i, "column": j, "coefficient": _q(value[i, j])}
            for i in range(value.rows)
            for j in range(value.cols)
            if value[i, j] != 0
        ],
    }
    return {**core, "sha256": _digest(core)}


def _import_level3() -> dict[str, Any]:
    actual = _sha(LEVEL3["path"])
    payload = json.loads(LEVEL3["path"].read_text())
    if (
        actual != LEVEL3["sha256"]
        or payload["result_id"] != LEVEL3["result_id"]
        or payload["result_state"] != LEVEL3["result_state"]
        or payload["terminal_verdict"]["selected_level3_action"]
    ):
        raise AssertionError("terminal Level-3 import drifted")
    return {
        "path": str(LEVEL3["path"].relative_to(ROOT)),
        "result_id": payload["result_id"],
        "result_state": payload["result_state"],
        "sha256": actual,
        "source_commit": LEVEL3["source_commit"],
        "selected_action": False,
    }


def _action_basis() -> dict[str, Any]:
    return {
        "fields": [
            "g_ab",
            "Phi=rho exp(i theta), rho nonzero on the formal polar chart",
            "one real Weyl connection W_a",
        ],
        "symmetries": [
            "Diff",
            "original Weyl with ghost omega",
            "candidate independent real Weyl with ghost eta",
            "global phase shift theta -> theta+constant",
            "complex conjugation theta -> -theta",
        ],
        "geometric_curvatures": {
            "F_ab": "2 partial_[a W_b]",
            "R_W": (
                "scalar curvature of the torsion-free Weyl connection whose "
                "nonmetricity is fixed by W"
            ),
            "Ricci_W_TF": "symmetric trace-free Weyl-Ricci tensor",
        },
        "density": (
            "sqrt(-g){alpha_C C^2/8+alpha_0 R_W^2"
            "+alpha_2 Ricci_W_TF^2-zeta F^2/4"
            "-kappa_r(D_W rho)^2/2-kappa_R rho^2 R_W/12"
            "-kappa_theta rho^2(nabla theta)^2/2-lambda rho^4/4}"
        ),
        "coefficient_order": [
            "alpha_C",
            "alpha_0",
            "alpha_2",
            "zeta",
            "kappa_r",
            "kappa_R",
            "kappa_theta",
            "lambda",
        ],
        "topological_and_exact_terms": (
            "Euler-Weyl density and total divergences are retained only as "
            "boundary/topological terms and do not alter the separator"
        ),
        "completeness": (
            "At the lowest declared derivative order, the parity-even pure "
            "geometric sector is spanned by the conformal tensor square, the "
            "Weyl scalar and symmetric trace-free Ricci squares, and F^2, "
            "modulo Euler and total derivatives. On the complex-conjugation "
            "invariant polar chart, the scalar sector is spanned by radial "
            "kinetic, rho^2 R_W, phase kinetic and rho^4. The cross term "
            "rho D rho dot d theta is odd under complex conjugation. "
            "An additive theta gauge action is an internal U(1) or "
            "complexified connection and is outside this real-Weyl ansatz."
        ),
    }


def _gauge_rank() -> dict[str, Any]:
    a, b = sp.symbols("a b", real=True)
    Delta = sp.factor(a - b)
    # Rows: logarithmic metric scale, logarithmic radial scale, normalized
    # longitudinal connection symbol. Columns: omega, eta.
    gauge = sp.Matrix([[1, a], [-1, -b], [-1, -a]])
    scalar_minor = sp.factor(gauge[:2, :].det())
    if scalar_minor != Delta:
        raise AssertionError("charge-rank minor drifted")
    dependent = sp.simplify(gauge.subs(b, a))
    reducibility = sp.Matrix([-a, 1])
    if dependent * reducibility != sp.zeros(3, 1):
        raise AssertionError("dependent-stratum reducibility drifted")
    if dependent.rank() != 1:
        raise AssertionError("dependent-stratum rank drifted")

    return {
        "weight_parameters": {
            "original": {
                "metric_scale": "1",
                "rho_weight": "-1",
            },
            "candidate": {
                "metric_scale": "a",
                "rho_weight": "-b",
            },
            "Delta": "a-b",
        },
        "finite_infinitesimal_rows": {
            "delta_g": "2(omega+a eta)g",
            "delta_rho": "-(omega+b eta)rho",
            "delta_theta": "0",
            "delta_W": "-d(omega+a eta)",
            "delta_g_hat": "2(a-b)eta g_hat",
            "g_hat": "(rho/f)^2 g",
        },
        "symbol_row_order": [
            "logarithmic metric scale",
            "logarithmic radial scale",
            "normalized longitudinal W symbol",
        ],
        "ghost_column_order": ["omega", "eta"],
        "gauge_symbol": _matrix(gauge),
        "independence_minor": _q(scalar_minor),
        "strata": {
            "Delta_zero": {
                "rank": 1,
                "reducibility_vector_in_(omega,eta)": ["-a", "1"],
                "irreducible_quotient": "one effective Weyl ghost",
                "dressed_trace_action": "ZERO",
            },
            "Delta_nonzero": {
                "rank": 2,
                "reducibility": "NONE",
                "dressed_trace_action": "NONZERO",
            },
        },
        "rank_change_surface": "a-b=0",
    }


def _ward_locus() -> dict[str, Any]:
    Delta, kr, kR, kt, lam = sp.symbols(
        "Delta kappa_r kappa_R kappa_theta lambda"
    )
    weights = {
        "radial_kinetic": 2 * Delta,
        "rho_squared_R_W": 2 * Delta,
        "phase_kinetic": 2 * Delta,
        "quartic_potential": 4 * Delta,
    }
    ward = [
        Delta * kr,
        Delta * kR,
        Delta * kt,
        Delta * lam,
    ]
    independent_branch = [sp.factor(item / Delta) for item in ward]
    if independent_branch != [kr, kR, kt, lam]:
        raise AssertionError("independent Ward branch drifted")
    return {
        "constant_candidate_Weyl_weights": {
            name: _q(value) for name, value in weights.items()
        },
        "exact_Ward_ideal_generators": [_q(value) for value in ward],
        "complete_strata": {
            "Delta_zero": {
                "compensator_coefficients": "unconstrained by constant weight",
                "gauge_disposition": (
                    "DEPENDENT_REDUCIBLE_NO_NEW_DRESSED_TRACE_DIRECTION"
                ),
            },
            "Delta_nonzero": {
                "forced_zero_coefficients": [
                    "kappa_r",
                    "kappa_R",
                    "kappa_theta",
                    "lambda",
                ],
                "geometric_spectator_coefficients": [
                    "alpha_C",
                    "alpha_0",
                    "alpha_2",
                    "zeta",
                ],
                "gauge_disposition": "INDEPENDENT_BUT_COMPENSATOR_ACTION_ZERO",
            },
        },
        "exhaustiveness": (
            "Constant gauge parameters already impose these weights, so no "
            "derivative improvement or integration by parts can cancel a "
            "nonzero Delta weight. Local derivative Ward terms can only add "
            "constraints and cannot reopen the independent branch."
        ),
    }


def _bv_data() -> dict[str, Any]:
    return {
        "minimal_generators": [
            "g_ab",
            "rho",
            "theta",
            "W_a",
            "xi^a",
            "omega",
            "eta",
            "and canonical antifields",
        ],
        "BRST_fields": {
            "Q g": "L_xi g+2(omega+a eta)g",
            "Q rho": "L_xi rho-(omega+b eta)rho",
            "Q theta": "L_xi theta",
            "Q W": "L_xi W-d(omega+a eta)",
            "Q xi": "xi^nu partial_nu xi",
            "Q omega": "L_xi omega",
            "Q eta": "L_xi eta",
        },
        "cotangent_lift": (
            "S_BV=S0+integral[g_star Qg+rho_star Qrho+theta_star Qtheta"
            "+W_star QW+xi_star Qxi+omega_star Qomega+eta_star Qeta], "
            "with graded integrations by parts defining the antifield rows"
        ),
        "odd_pairing": (
            "integral(delta g_star delta g+delta rho_star delta rho"
            "+delta theta_star delta theta+delta W_star delta W"
            "+delta xi_star delta xi+delta omega_star delta omega"
            "+delta eta_star delta eta)"
        ),
        "real_structure": (
            "g,rho,theta,W and the two real Weyl ghosts are real; complex "
            "conjugation of Phi sends theta to -theta and lifts contragrediently"
        ),
        "Delta_zero_reducible_completion": {
            "option_1": (
                "quotient the dependent columns to one irreducible Weyl ghost"
            ),
            "option_2": (
                "retain both ghosts and add an even ghost-for-ghost z with "
                "Q omega containing -a z and Q eta containing z"
            ),
            "effect": "the reducible completion is contractible and adds no trace gauge direction",
        },
        "nilpotency": (
            "the two Weyl factors are abelian and transform as Diff scalars; "
            "the displayed semidirect-product Chevalley-Eilenberg rows square "
            "to zero, with the reducibility row on Delta=0"
        ),
    }


def _charge_and_cohomology() -> dict[str, Any]:
    return {
        "phase_current": (
            "J_theta^a=-kappa_theta rho^2 nabla^a theta"
        ),
        "Berger_clock_charge_condition": (
            "rho=f nonzero, theta=nu t with nu nonzero requires "
            "kappa_theta nonzero for a nonzero phase pairing and charge"
        ),
        "strata": {
            "Delta_zero": {
                "new_trace_gauge_direction": False,
                "old_dressed_trace_disposition": (
                    "NOT_CONTRACTED_BY_THE_NEW_GAUGE_ROW"
                ),
                "reason": (
                    "eta column equals a times the omega column after the "
                    "explicit reducibility quotient"
                ),
            },
            "Delta_nonzero": {
                "new_trace_gauge_direction": True,
                "kappa_theta": "0 by the Ward ideal",
                "phase_Hessian": "ZERO",
                "phase_current": "ZERO",
                "phase_compact_support_cohomology": (
                    "arbitrary compact-support theta variations survive "
                    "because shift symmetry and the declared minimal action "
                    "contain no theta row"
                ),
                "support_local_Green_parent": "OBSTRUCTED",
            },
        },
        "common_gate": (
            "A nonzero Berger phase charge forces kappa_theta nonzero, hence "
            "Delta=0, but a new dressed-trace gauge direction requires "
            "Delta nonzero. Their exact intersection is empty."
        ),
    }


def _gate_disposition() -> dict[str, Any]:
    return {
        "seven_gates": [
            {
                "gate": 1,
                "name": "complete minimal action and coefficient locus",
                "status": "PASS_WITH_EMPTY_INDEPENDENCE_AND_CLOCK_INTERSECTION",
            },
            {
                "gate": 2,
                "name": "action-origin BV rows and reducibility",
                "status": "PASS_KINEMATIC_AND_WARD_LEVEL",
            },
            {
                "gate": 3,
                "name": "both background Euler systems",
                "status": "NOT_REACHED_AFTER_RANK_CHARGE_SEPARATOR",
            },
            {
                "gate": 4,
                "name": "full scalar/longitudinal principal complex",
                "status": "FAIL_ZERO_PHASE_ROW_ON_INDEPENDENT_STRATUM",
            },
            {
                "gate": 5,
                "name": "cohomology and velocity inertia",
                "status": "FAIL_DEPENDENT_TRACE_OR_ZERO_PHASE_HESSIAN",
            },
            {
                "gate": 6,
                "name": "charge generators",
                "status": "FAIL_DEPENDENT_TRACE_OR_ZERO_PHASE_CHARGE",
            },
            {
                "gate": 7,
                "name": "support-local Green parent",
                "status": "FAIL_NONZERO_COMPACT_SUPPORT_HOMOLOGY",
            },
        ],
        "background_boundary": (
            "No prior unit-cylinder or Berger solution is inherited. On the "
            "independent stratum the phase stress and current vanish, so the "
            "frozen active-clock Berger equations are not the equations of "
            "this theory. Since the common rank/charge gate is already empty, "
            "no replacement background is promoted."
        ),
        "selected_action": False,
        "support_local_Green_parent": False,
        "nonlinear_q2": False,
    }


def build() -> dict[str, Any]:
    imported = {"level3_no_go": _import_level3()}
    action = _action_basis()
    rank = _gauge_rank()
    ward = _ward_locus()
    bv = _bv_data()
    charge = _charge_and_cohomology()
    gates = _gate_disposition()
    verdict = {
        "complete_minimal_real_Weyl_connection_family_checked": True,
        "independent_trace_gauge_and_nonzero_clock_charge_intersection": "EMPTY",
        "selected_level4_action": False,
        "first_invariant_separator": (
            "Delta=a-b must be nonzero to add a dressed-trace gauge direction, "
            "while the exact phase-kinetic Ward identity "
            "Delta*kappa_theta=0 and the nonzero Berger clock charge require "
            "Delta=0"
        ),
        "result": "SCOPED_LEVEL4_INDEPENDENT_WEYL_CONNECTION_GOOD_LOCUS_EMPTY",
    }
    value = {
        "schema": (
            "pure-weyl-compensator-independent-weyl-connection-level4-no-go-v1"
        ),
        "result_id": (
            "COMPENSATOR_INDEPENDENT_WEYL_CONNECTION_LEVEL4_NO_GO_V1"
        ),
        "result_state": (
            "SCOPED_LEVEL4_INDEPENDENT_WEYL_CONNECTION_GOOD_LOCUS_EMPTY"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imported,
        "domain": {
            "dimension": 4,
            "signature": "(-,+,+,+)",
            "connection": "one real torsion-free Weyl connection",
            "complex_compensator_chart": "Phi=rho exp(i theta), rho nonzero",
            "phase_symmetry": "global shift with complex-conjugation real structure",
            "arithmetic": "exact characteristic-zero polynomial algebra",
        },
        "complete_minimal_action": action,
        "gauge_rank_and_reducibility": rank,
        "exact_Ward_locus": ward,
        "minimal_BV_data": bv,
        "charge_and_cohomology_separator": charge,
        "gate_disposition": gates,
        "terminal_verdict": verdict,
        "exact_checks": {
            "level3_hash_and_semantics_pinned": True,
            "minimal_action_basis_declared": True,
            "two_generator_charge_matrix_exact": True,
            "rank_change_minor_exact": True,
            "dependent_reducibility_vector_exact": True,
            "dressed_trace_weight_exact": True,
            "constant_parameter_Ward_weights_exact": True,
            "independent_branch_coefficient_elimination_exact": True,
            "phase_current_and_Hessian_zero_on_independent_branch": True,
            "clock_charge_trace_independence_intersection_empty": True,
            "downstream_background_and_causal_claims_fail_closed": True,
        },
        "claim_flags": {
            "SELECTED_LEVEL4_ACTION": False,
            "BOTH_BACKGROUND_EULER_SYSTEMS": False,
            "COMPLETE_SCALAR_LONGITUDINAL_GREEN_PARENT": False,
            "NONLINEAR_Q2": False,
            "INTERNAL_U1_OR_COMPLEXIFIED_CONNECTION": False,
            "GENERAL_METRIC_AFFINE_OR_WEYL_GEOMETRY_NO_GO": False,
            "HADAMARD_ANOMALY_QME_OR_QUANTUM": False,
            "PARTICLE_SCATTERING_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact theorem covers the complete declared lowest-order "
            "parity-even family with one real torsion-free Weyl connection, "
            "one formal-polar complex compensator whose phase is neutral under "
            "real scale transformations, two candidate Weyl generators, and "
            "global phase shift plus complex-conjugation symmetry. If their "
            "weight difference Delta vanishes, the new gauge column is "
            "reducible and adds no dressed-trace direction. If Delta is "
            "nonzero, exact Ward invariance forces every minimal compensator "
            "coefficient, including kappa_theta, to zero, leaving a zero phase "
            "Hessian, zero Berger clock charge and arbitrary compact-support "
            "phase homology. No selected action or Green parent follows. An "
            "internal U(1), a complexified connection, extra compensators, "
            "higher phase derivatives, other backgrounds and general "
            "metric-affine theories are outside scope. No nonlinear q2, "
            "Hadamard, anomaly/QME, particle, scattering, positivity or "
            "unitarity result follows."
        ),
        "next_gate": (
            "The four-level compensator repair ladder is empty in its declared "
            "minimal classes. The next theory choice must be explicit: add an "
            "internal U(1)/complexified connection with its own BV sector, add "
            "another compensator, or abandon the common Berger clock gate."
        ),
    }
    value["content_hashes"] = {
        "imports_sha256": _digest(value["imports"]),
        "action_sha256": _digest(value["complete_minimal_action"]),
        "rank_sha256": _digest(value["gauge_rank_and_reducibility"]),
        "ward_sha256": _digest(value["exact_Ward_locus"]),
        "bv_sha256": _digest(value["minimal_BV_data"]),
        "separator_sha256": _digest(value["charge_and_cohomology_separator"]),
        "gates_sha256": _digest(value["gate_disposition"]),
        "verdict_sha256": _digest(value["terminal_verdict"]),
    }
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("Level-4 Weyl-connection certificate is stale")
    print("COMPENSATOR_INDEPENDENT_WEYL_CONNECTION_LEVEL4_NO_GO_V1: PASS")


if __name__ == "__main__":
    main()
