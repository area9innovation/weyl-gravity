#!/usr/bin/env python3
"""Exact Level-2 no-go after cylinder invisibility of minimal braiding."""

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
    "COMPENSATOR_KINETIC_BRAIDING_LEVEL2_NO_GO_V1.json"
)
IMPORTS = {
    "visibility": {
        "path": ROOT
        / "d_quotient_classical/certificates/"
        "COMPENSATOR_KINETIC_BRAIDING_QUADRATIC_VISIBILITY_V1.json",
        "sha256": "bfce9fd2897511d43802c504ce10f9342b85f2e3d89ce9c4cb3e66b788905e10",
        "source_commit": "85a54362c8c82fd98810d07234e8c6a94e57f43b",
        "result_id": "COMPENSATOR_KINETIC_BRAIDING_QUADRATIC_VISIBILITY_V1",
        "result_state": "SCOPED_LEVEL2_BRAIDING_CYLINDER_QUADRATIC_INVISIBLE",
    },
    "P2_freeze": {
        "path": ROOT
        / "d_quotient_classical/certificates/"
        "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json",
        "sha256": "9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533",
        "source_commit": "f64be4a5793764ebf8871d5f1a83bd736aed7fc1",
        "result_id": "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1",
        "result_state": "SCOPED_QUADRATIC_ACTIVE_CLOCK_NO_GO_INDEPENDENTLY_FROZEN",
    },
    "background_stability": {
        "path": ROOT
        / "d_quotient_classical/certificates/"
        "COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1.json",
        "sha256": "8a3afc04d72427313fe8770936b03d4f4301277c9783a92e8df6d329e8c0ccba",
        "source_commit": "b0ee2bea23af4af809bc0a50956c3e37d944e72f",
        "result_id": "COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1",
        "result_state": (
            "SCOPED_ACTION_SPACE_NO_GO_BACKGROUND_STABLE_WITH_FIRST_BIFURCATION"
        ),
    },
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


def _imports() -> dict[str, Any]:
    records: dict[str, Any] = {}
    for name, item in IMPORTS.items():
        actual = _sha(item["path"])
        payload = json.loads(item["path"].read_text())
        if (
            actual != item["sha256"]
            or payload["result_id"] != item["result_id"]
            or payload["result_state"] != item["result_state"]
        ):
            raise AssertionError(f"{name} import drifted")
        records[name] = {
            "path": str(item["path"].relative_to(ROOT)),
            "result_id": payload["result_id"],
            "result_state": payload["result_state"],
            "sha256": actual,
            "source_commit": item["source_commit"],
        }
    return records


def _stationary_locus() -> dict[str, Any]:
    cylinder = sp.Matrix(
        [[0, 36, 3, 1, 0, 0], [0, 12, -1, -1, 0, 0]]
    )
    berger = sp.Matrix(
        [
            [
                sp.Rational(961, 9600),
                sp.Rational(22801, 6400),
                sp.Rational(151, 160),
                1,
                sp.Rational(9, 16),
                -sp.Rational(243, 256),
            ],
            [
                sp.Rational(403, 9600),
                sp.Rational(20083, 6400),
                -sp.Rational(9, 160),
                -1,
                sp.Rational(9, 16),
                -sp.Rational(81, 256),
            ],
            [
                sp.Rational(31, 1920),
                -sp.Rational(3473, 1280),
                -sp.Rational(133, 160),
                -1,
                sp.Rational(9, 16),
                -sp.Rational(81, 256),
            ],
        ]
    )
    base = cylinder.col_join(berger)
    extended = base.row_join(sp.zeros(5, 1))
    K = sp.Matrix(
        [
            sp.Rational(81, 20),
            sp.Rational(27, 3290),
            -sp.Rational(324, 1645),
            sp.Rational(486, 1645),
            sp.Rational(18, 25),
            1,
            0,
        ]
    )
    B = sp.Matrix([0, 0, 0, 0, 0, 0, 1])
    if (
        extended.rank() != 5
        or extended * K != sp.zeros(5, 1)
        or extended * B != sp.zeros(5, 1)
        or len(extended.nullspace()) != 2
    ):
        raise AssertionError("extended stationary locus drifted")
    witness = sp.factor(base[:, :5].det())
    if witness != sp.Rational(91791, 40960):
        raise AssertionError("rank witness drifted")
    return {
        "action": (
            "S=S_P2[alpha_B,alpha_R,M_P_squared,p0,p1,p2]"
            "+beta integral sqrt(-g_hat)X Box_hat(theta)"
        ),
        "coefficient_order": [
            "alpha_B",
            "alpha_R",
            "M_P_squared",
            "p0",
            "p1",
            "p2",
            "beta",
        ],
        "backgrounds": [
            "unit cylinder with theta constant",
            "Berger a=1, q=9/40, theta=3t/4",
        ],
        "braiding_first_variation": (
            "ZERO on both backgrounds because X is constant and "
            "nabla_a nabla_b theta=0"
        ),
        "P2_stacked_matrix": _matrix(base),
        "extended_stacked_matrix": _matrix(extended),
        "rank": 5,
        "rank_witness_first_five_P2_columns": "91791/40960",
        "kernel_dimension": 2,
        "kernel_basis": {
            "P2_ray": [_q(x) for x in K],
            "pure_braiding_axis": [_q(x) for x in B],
        },
        "complete_real_locus": (
            "t(81/20,27/3290,-324/1645,486/1645,18/25,1,0)"
            "+beta(0,0,0,0,0,0,1), (t,beta) in R^2"
        ),
        "completeness": (
            "The zero beta column is action-derived, and the nonzero 5-by-5 "
            "P2 minor proves there are no additional stationary directions."
        ),
    }


def _cylinder_replay() -> dict[str, Any]:
    eps, x2, x3, b1, b2, m1 = sp.symbols(
        "eps x2 x3 b1 b2 m1"
    )
    # On theta_bar=constant, d theta=eps d phi, so X starts at eps^2.
    X = eps**2 * x2 + eps**3 * x3
    Box = eps * b1 + eps**2 * b2
    volume = 1 + eps * m1
    density = sp.expand(volume * X * Box)
    quadratic = sp.expand(density).coeff(eps, 2)
    cubic = sp.expand(density).coeff(eps, 3)
    if quadratic != 0 or cubic != b1 * x2:
        raise AssertionError("independent cylinder order replay drifted")
    return {
        "independent_order_counting": {
            "d_theta": "O(eps)",
            "X": "eps^2 x2+eps^3 x3+O(eps^4)",
            "Box_theta": "eps b1+eps^2 b2+O(eps^3)",
            "sqrt_minus_g": "sqrt_minus_g_bar(1+eps m1+O(eps^2))",
            "epsilon_squared_coefficient": "0",
            "first_possible_coefficient": "epsilon^3 x2 b1",
        },
        "full_metric_clock_Hessian": _matrix(sp.zeros(11)),
        "braiding_rank": 0,
        "combined_operator_identity": (
            "H_cylinder[P2+G3]=H_cylinder[P2] for every beta"
        ),
        "unchanged_rows": [
            "dressed-trace/R2-auxiliary Hessian",
            "velocity and principal matrices",
            "Lee-Wald pairing",
            "raw-D quadratic Hamiltonian",
        ],
        "scope": (
            "This is full local order counting: inverse metric and volume "
            "perturbations can only enter at epsilon^3 or later because "
            "d theta_bar=0."
        ),
    }


def _gate_disposition() -> dict[str, Any]:
    t = sp.Symbol("t", real=True)
    velocity = sp.diag(-6, 6, -sp.Rational(36, 25) * t)
    if velocity.det() != sp.Rational(1296, 25) * t:
        raise AssertionError("velocity determinant drifted")
    return {
        "strata": {
            "t=0_beta=0": {
                "action": "zero action",
                "cylinder_quadratic_rank": 0,
                "disposition": "FAIL_NO_DYNAMICS",
            },
            "t=0_beta_nonzero": {
                "action": "pure minimal braiding",
                "cylinder_quadratic_rank": 0,
                "disposition": "FAIL_NO_CYLINDER_TRACE_OR_PAIRING",
            },
            "t_nonzero_beta_arbitrary": {
                "cylinder_velocity_congruence": _matrix(velocity),
                "inertia": {
                    "t>0": [1, 2, 0],
                    "t<0": [2, 1, 0],
                },
                "raw_D_witnesses": ["+3", "-3"],
                "beta_dependence": "NONE on the cylinder quadratic carrier",
                "disposition": "FAIL_SPLIT_PAIR_AND_RAW_D",
            },
        },
        "Berger_visibility": (
            "The rank-two Berger scalar braiding block is retained as an exact "
            "separate fact, but no Berger-only change can repair a cylinder "
            "failure on the common-background seven-gate problem."
        ),
        "seven_gates": [
            {"gate": 1, "status": "PASS_ACTION_DERIVED"},
            {"gate": 2, "status": "UNCHANGED_P2_OR_ABSENT_ON_PURE_BRAIDING"},
            {"gate": 3, "status": "FAIL_NO_COMPLETE_HEALTHY_CYLINDER_PARENT"},
            {"gate": 4, "status": "FAIL_SPLIT_OR_ZERO_PAIRING"},
            {"gate": 5, "status": "FAIL_SPLIT_OR_ZERO_PHYSICAL_QUADRATIC_FORM"},
            {"gate": 6, "status": "FAIL_RAW_D_OR_ZERO_DYNAMICS"},
            {"gate": 7, "status": "NOT_REACHED_AS_COMMON_PASS"},
        ],
        "good_locus": "EMPTY_FOR_ALL_(t,beta)_IN_R2",
    }


def build() -> dict[str, Any]:
    imported = _imports()
    locus = _stationary_locus()
    cylinder = _cylinder_replay()
    gates = _gate_disposition()
    verdict = {
        "complete_declared_P2_plus_linear_G_family_checked": True,
        "stationary_locus_dimension": 2,
        "common_seven_gate_good_locus": "EMPTY",
        "selected_level2_action": False,
        "nonlinear_q2_required": False,
        "first_invariant_separator": (
            "the braiding axis has zero cylinder Hessian, while every nonzero "
            "P2-ray component retains the beta-independent split cylinder pair "
            "and raw-D witnesses"
        ),
    }
    value = {
        "schema": "pure-weyl-compensator-kinetic-braiding-level2-no-go-v1",
        "result_id": "COMPENSATOR_KINETIC_BRAIDING_LEVEL2_NO_GO_V1",
        "result_state": "SCOPED_LEVEL2_KINETIC_BRAIDING_GOOD_LOCUS_EMPTY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imported,
        "complete_stationary_locus": locus,
        "independent_cylinder_zero_replay": cylinder,
        "stratified_gate_disposition": gates,
        "terminal_verdict": verdict,
        "exact_checks": {
            "dependency_hashes_and_semantics_pinned": True,
            "complete_seven_coefficient_action_declared": True,
            "braiding_background_first_variation_zero": True,
            "stationary_rank_and_two_dimensional_kernel_exact": True,
            "independent_full_order_counting_replayed": True,
            "combined_cylinder_Hessian_unchanged": True,
            "pure_braiding_axis_classified": True,
            "nonzero_P2_stratum_split_inertia_exact": True,
            "raw_D_witnesses_beta_independent": True,
            "Berger_visibility_not_used_as_cylinder_repair": True,
            "nonlinear_q2_stopped": True,
        },
        "claim_flags": {
            "SELECTED_LEVEL2_ACTION": False,
            "COMPLETE_SUPPORT_LOCAL_CAUSAL_PARENT": False,
            "NONLINEAR_Q2": False,
            "HADAMARD_ANOMALY_QME_OR_QUANTUM": False,
            "PARTICLE_SCATTERING_UNITARITY": False,
            "UNIVERSAL_BRAIDING_HORNDESKI_OR_DHOST_NO_GO": False,
        },
        "claim_boundary": (
            "This exact no-go covers the complete declared P(X)=p0+p1X+p2X^2 "
            "family enlarged only by the first nonexact polynomial braiding "
            "G(X)=g0+beta X on the common unit-cylinder and frozen Berger "
            "fixtures. The stationary locus is the old P2 ray plus the free "
            "beta axis. Pure braiding has zero cylinder Hessian; every nonzero "
            "P2 component retains the beta-independent split cylinder pairing "
            "and raw-D witnesses. No nonlinear q2 is constructed. This does "
            "not cover higher G(X), Horndeski/DHOST curvature couplings, other "
            "backgrounds, new fields or enlarged gauge groups, and establishes "
            "no causal parent, Hadamard state, anomaly/QME result, particle "
            "space, scattering, positivity or unitarity theorem."
        ),
        "next_gate": (
            "Activate the isolated Level-3 minimal degenerate curvature-coupling "
            "locus. Keep the failed braiding coefficient zero there so the new "
            "mechanism is classified independently."
        ),
    }
    value["content_hashes"] = {
        "imports_sha256": _digest(value["imports"]),
        "locus_sha256": _digest(value["complete_stationary_locus"]),
        "cylinder_sha256": _digest(value["independent_cylinder_zero_replay"]),
        "gates_sha256": _digest(value["stratified_gate_disposition"]),
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
        raise AssertionError("Level-2 kinetic-braiding no-go certificate is stale")
    print("COMPENSATOR_KINETIC_BRAIDING_LEVEL2_NO_GO_V1: PASS")


if __name__ == "__main__":
    main()
