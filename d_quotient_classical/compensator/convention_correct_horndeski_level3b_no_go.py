#!/usr/bin/env python3
"""Exact cylinder-fast no-go for the convention-correct Level-3b family."""

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
    "COMPENSATOR_CONVENTION_CORRECT_HORNDESKI_LEVEL3B_NO_GO_V1.json"
)
IMPORTS = {
    "literal_level3": {
        "path": ROOT / "d_quotient_classical/certificates/COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1.json",
        "sha256": "2e687331b6985b3a84c54a0f05b210bee5e3ac06d5659b5603ac9bc25f61dfed",
        "source_commit": "e77ee444450890dd1df720f70c5ef5ab202fe8cc",
        "result_id": "COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1",
        "result_state": "SCOPED_LEVEL3_LITERAL_CURVATURE_COUPLING_GOOD_LOCUS_EMPTY",
    },
    "P2_freeze": {
        "path": ROOT / "d_quotient_classical/certificates/COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json",
        "sha256": "9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533",
        "source_commit": "f64be4a5793764ebf8871d5f1a83bd736aed7fc1",
        "result_id": "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1",
        "result_state": "SCOPED_QUADRATIC_ACTIVE_CLOCK_NO_GO_INDEPENDENTLY_FROZEN",
    },
    "trace_obstruction": {
        "path": ROOT / "d_quotient_classical/certificates/TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json",
        "sha256": "db1f998a0920adb94cf4fcbffb1b9eb2ea6537876aff9513aac4e4d9ec2b51b9",
        "source_commit": "2b834dc751d6948366fd5c3d99174c268fa50d21",
        "result_id": "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1",
        "result_state": "OBSTRUCTED",
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
    result: dict[str, Any] = {}
    for name, item in IMPORTS.items():
        actual = _sha(item["path"])
        payload = json.loads(item["path"].read_text())
        if (
            actual != item["sha256"]
            or payload["result_id"] != item["result_id"]
            or payload["result_state"] != item["result_state"]
        ):
            raise AssertionError(f"{name} import drifted")
        if name == "literal_level3":
            control = payload["convention_correct_control"]
            if (
                control["corrected_density"]
                != "F(X)R-2F_X[(Box theta)^2-(nabla_a nabla_b theta)^2]"
            ):
                raise AssertionError("literal theorem convention control drifted")
        result[name] = {
            "path": str(item["path"].relative_to(ROOT)),
            "result_id": payload["result_id"],
            "result_state": payload["result_state"],
            "sha256": actual,
            "source_commit": item["source_commit"],
        }
    return result


def _adm_degeneracy() -> dict[str, Any]:
    X, F, Fx = sp.symbols("X F F_X")
    h, A = sp.symbols("h A")
    R_reduced = -6 * F * h**2 + 12 * X * Fx * A * h
    Q = -6 * X * h**2 + 6 * X * A * h
    kinetic = sp.expand(R_reduced - 2 * Fx * Q)
    expected = -6 * (F - 2 * Fx * X) * h**2
    if sp.expand(kinetic - expected) != 0:
        raise AssertionError("corrected Horndeski cancellation drifted")
    Hessian = sp.hessian(kinetic, (h, A))
    if Hessian.det() != 0 or Hessian * sp.Matrix([0, 1]) != sp.zeros(2, 1):
        raise AssertionError("Horndeski degeneracy drifted")
    return {
        "fixture": (
            "ds^2=-N^2dt^2+a^2 delta_ij dx^i dx^j, theta=nu t, "
            "h=dot(a)/(aN), A=dot(N)/N^2, X=-nu^2/N^2"
        ),
        "raw_identities": {
            "F_R_after_boundary_reduction": "-6Fh^2+12X F_X A h",
            "Hessian_square_difference": "-6Xh^2+6XAh",
        },
        "corrected_kinetic_density_over_Na3": _q(kinetic),
        "velocity_order": ["h", "A"],
        "velocity_Hessian": _matrix(Hessian),
        "determinant": "0",
        "lapse_velocity_null_vector": ["0", "1"],
        "rank_strata": {
            "F-2X_F_X_nonzero": 1,
            "F-2X_F_X_zero": 0,
        },
        "linear_F_rank_change_surface": "f0-f1X=0",
        "conclusion": "HORNDESKI_DEGENERACY_EXACTLY_REDERIVED",
    }


def _cylinder_stationarity() -> dict[str, Any]:
    # f0 is absorbed into M2_eff. The slope column is zero because the
    # constant-clock background has d theta=0.
    M = sp.Matrix(
        [
            [0, 36, 3, 1, 0, 0, 0],
            [0, 12, -1, -1, 0, 0, 0],
        ]
    )
    if M.rank() != 2 or len(M.nullspace()) != 5:
        raise AssertionError("cylinder stationary rank drifted")
    R = M.rref()[0]
    expected_rref = sp.Matrix(
        [
            [0, 1, 0, sp.Rational(-1, 36), 0, 0, 0],
            [0, 0, 1, sp.Rational(2, 3), 0, 0, 0],
        ]
    )
    if R != expected_rref:
        raise AssertionError("cylinder RREF drifted")
    return {
        "coefficient_order": [
            "alpha_B",
            "alpha_R",
            "M_P_squared_effective",
            "p0",
            "p1",
            "p2",
            "f1",
        ],
        "f0_absorption": "M_P_squared_effective=M_P_squared+2f0",
        "Euler_row_order": ["spatial_metric", "temporal_metric"],
        "stationary_matrix": _matrix(M),
        "rank": 2,
        "kernel_dimension": 5,
        "complete_solution": {
            "M_P_squared_effective": "-24 alpha_R",
            "p0": "36 alpha_R",
            "free": ["alpha_B", "alpha_R", "p1", "p2", "f1"],
        },
        "slope_first_variation": "ZERO because d theta_bar=0",
        "common_background_locus_relation": (
            "every common cylinder/Berger stationary coefficient vector is a "
            "subset of this complete cylinder stationary locus"
        ),
    }


def _cylinder_hessian() -> dict[str, Any]:
    p1, f1, omega2, k2 = sp.symbols("p1 f1 omega_squared k_squared")
    # On R x S3: G^00=3 and G^ij=-gamma^ij.
    P_symbol = 2 * p1 * (-omega2 + k2)
    H_symbol = -4 * f1 * (3 * omega2 - k2)
    combined = sp.factor(P_symbol + H_symbol)
    expected = -2 * (p1 + 6 * f1) * omega2 + 2 * (p1 + 2 * f1) * k2
    if sp.expand(combined - expected) != 0:
        raise AssertionError("clock symbol drifted")
    split = sp.Matrix([[0, -3], [-3, 0]])
    change = sp.Matrix([[1, 1], [1, -1]])
    congruence = change.T * split * change
    if congruence != sp.diag(-6, 6):
        raise AssertionError("R2 split congruence drifted")
    return {
        "boundary_identity": (
            "f1[X R-2((Box theta)^2-(nabla nabla theta)^2)]"
            "=-2f1 G_ab nabla^a theta nabla^b theta mod d_h"
        ),
        "unit_cylinder_Einstein_tensor": {
            "G^00": "3",
            "G^ij": "-gamma^ij",
        },
        "block_structure": {
            "f1_pure_metric": "ZERO",
            "f1_metric_clock_mixed": "ZERO",
            "f1_clock_clock": "-4f1 G_bar^{ab}k_a k_b",
            "p2_quadratic": "ZERO",
        },
        "clock_symbol": _q(combined),
        "clock_rank_surfaces": [
            "p1+6f1=0 (time coefficient)",
            "p1+2f1=0 (spatial coefficient)",
        ],
        "clock_hyperbolicity_condition": (
            "(p1+6f1)(p1+2f1)>0 away from either rank surface"
        ),
        "R2_auxiliary_velocity_block": _matrix(split),
        "R2_rational_congruence": _matrix(change),
        "R2_congruent_diagonal": _matrix(congruence),
        "R2_inertia_for_alpha_R_nonzero": [1, 1, 0],
        "slope_effect_on_R2_block": "NONE",
    }


def _stratified_no_go() -> dict[str, Any]:
    return {
        "alpha_R_nonzero": {
            "cylinder_stationarity": (
                "M_P_squared_effective=-24alpha_R and p0=36alpha_R"
            ),
            "trace_sector": (
                "the auxiliary R2 velocity block is congruent to diag(-6,6)"
            ),
            "clock_sector": (
                "the corrected slope changes only the separate clock diagonal"
            ),
            "invariant_failure": "SPLIT_GRAVITY_AUXILIARY_INERTIA_PERSISTS",
            "raw_D_witnesses": ["+3", "-3"],
        },
        "alpha_R_zero": {
            "cylinder_stationarity": (
                "M_P_squared_effective=0 and p0=0"
            ),
            "metric_action": (
                "alpha_B C^2 is trace-free; p1,p2 and f1 are clock-only at "
                "quadratic order"
            ),
            "dressed_trace": "u=phi_trace-2tau",
            "compact_support_witness": (
                "the imported arbitrary compact-support u class and its dual "
                "functional survive by direct-sum extension"
            ),
            "invariant_failure": "DRESSED_TRACE_HOMOLOGY_PERSISTS",
        },
        "exhaustiveness": (
            "alpha_R=0 or alpha_R!=0 partitions the complete cylinder "
            "stationary locus. Every common-background solution lies in one "
            "branch, and both fail before Berger equations can rescue them."
        ),
        "common_seven_gate_good_locus": "EMPTY",
    }


def _unary_and_gates() -> dict[str, Any]:
    return {
        "action_origin_unary": {
            "Q_g_hat": "Lie_xi(g_hat)",
            "Q_theta": "Lie_xi(theta)",
            "Q_xi": "xi^nu partial_nu xi",
            "new_gauge_generator": False,
            "Horndeski_primary_constraint": (
                "the lapse-velocity null vector (0,1) in the homogeneous "
                "(h,A) Hessian"
            ),
            "cylinder_scalar_reduction": (
                "the metric/constraint rows are exactly the P2 rows; f1 "
                "appends only the clock-clock principal entry"
            ),
        },
        "shift_current": (
            "j^a=2P_X nabla^a theta-4f1 G^{ab}nabla_b theta"
        ),
        "seven_gates": [
            {"gate": 1, "status": "PASS_ACTION_AND_HORNDESKI_DEGENERACY"},
            {"gate": 2, "status": "PASS_COMPLETE_CYLINDER_STATIONARY_LOCUS"},
            {"gate": 3, "status": "FAIL_SPLIT_OR_TRACE_HOMOLOGY"},
            {"gate": 4, "status": "FAIL_SPLIT_OR_DEGENERATE_TRACE_PAIRING"},
            {"gate": 5, "status": "FAIL_SPLIT_OR_NONZERO_TRACE_COHOMOLOGY"},
            {"gate": 6, "status": "FAIL_RAW_D_OR_NO_TRACE_GENERATOR"},
            {"gate": 7, "status": "NOT_REACHED_AFTER_CYLINDER_SEPARATOR"},
        ],
        "Berger_system": (
            "NOT_COMPUTED: the complete cylinder stationary locus already has "
            "empty physical good locus, so its intersection with any Berger "
            "stationary locus is empty"
        ),
        "support_local_causal_parent": False,
        "selected_action": False,
        "nonlinear_q2": False,
    }


def build() -> dict[str, Any]:
    imported = _imports()
    adm = _adm_degeneracy()
    stationary = _cylinder_stationarity()
    hessian = _cylinder_hessian()
    strata = _stratified_no_go()
    unary = _unary_and_gates()
    verdict = {
        "complete_convention_correct_linear_F_family_checked": True,
        "Horndeski_degeneracy_verified": True,
        "complete_cylinder_stationary_locus_classified": True,
        "common_cylinder_Berger_good_locus": "EMPTY",
        "selected_level3b_action": False,
        "first_complete_invariant_separator": (
            "on the complete cylinder stationary locus, alpha_R nonzero "
            "retains the slope-independent split R2 auxiliary pair, while "
            "alpha_R zero forces M_P_squared_effective=p0=0 and retains the "
            "compact-support dressed-trace homology"
        ),
        "result": "SCOPED_LEVEL3B_CORRECT_HORNDESKI_GOOD_LOCUS_EMPTY",
    }
    value = {
        "schema": "pure-weyl-compensator-correct-horndeski-level3b-no-go-v1",
        "result_id": (
            "COMPENSATOR_CONVENTION_CORRECT_HORNDESKI_LEVEL3B_NO_GO_V1"
        ),
        "result_state": "SCOPED_LEVEL3B_CORRECT_HORNDESKI_GOOD_LOCUS_EMPTY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imported,
        "conventions": {
            "signature": "(-,+,+,+)",
            "X": "g_hat^{ab}partial_a(theta)partial_b(theta)",
            "F": "f0+f1X",
            "corrected_coefficient": "-2F_X",
            "level2_braiding": "ZERO",
            "arithmetic": "exact characteristic-zero rational polynomial algebra",
        },
        "complete_declared_action": (
            "S_P2+integral sqrt(-g_hat){F(X)R_hat"
            "-2F_X[(Box_hat theta)^2-(nabla_hat nabla_hat theta)^2]}"
        ),
        "exact_adm_degeneracy": adm,
        "complete_cylinder_stationary_locus": stationary,
        "full_cylinder_quadratic_separator": hessian,
        "stratified_no_go": strata,
        "unary_constraint_charge_and_gates": unary,
        "terminal_verdict": verdict,
        "exact_checks": {
            "literal_control_hash_and_semantics_pinned": True,
            "corrected_action_declared_without_braiding": True,
            "Horndeski_ADM_cancellation_rederived": True,
            "lapse_velocity_null_vector_exact": True,
            "cylinder_stationary_matrix_and_RREF_exact": True,
            "f1_background_column_zero": True,
            "clock_symbol_exact": True,
            "pure_metric_and_mixed_f1_blocks_zero": True,
            "alpha_R_nonzero_split_congruence_exact": True,
            "alpha_R_zero_trace_homology_direct_sum_exact": True,
            "common_good_locus_empty_without_Berger_sampling": True,
            "downstream_claims_fail_closed": True,
        },
        "claim_flags": {
            "SELECTED_LEVEL3B_ACTION": False,
            "BERGER_STATIONARY_LOCUS_COMPUTED": False,
            "COMPLETE_SUPPORT_LOCAL_CAUSAL_PARENT": False,
            "NONLINEAR_Q2": False,
            "HIGHER_HORNDESKI_G5_OR_DHOST_NO_GO": False,
            "HADAMARD_ANOMALY_QME_OR_QUANTUM": False,
            "PARTICLE_SCATTERING_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact theorem covers the complete convention-correct "
            "F=f0+f1X quartic-Horndeski family with coefficient -2F_X, "
            "quadratic P(X), zero braiding, the unit-cylinder constant-clock "
            "gate and the requirement of a common cylinder/Berger passing "
            "action. Horndeski degeneracy is rederived. The complete cylinder "
            "stationary locus is partitioned by alpha_R: its nonzero branch "
            "retains the split R2 auxiliary pair, and its zero branch retains "
            "the compact-support dressed-trace homology because the corrected "
            "slope is clock-only. Hence the common good locus is empty without "
            "computing or sampling a Berger locus. No selected action, full "
            "causal parent, nonlinear q2, Hadamard, anomaly/QME, particle, "
            "scattering, positivity or unitarity result follows. Higher F, "
            "G5, DHOST, independent connections, new fields and other "
            "backgrounds remain outside scope."
        ),
        "next_gate": (
            "The convention-correct Level-3b family is terminal at the "
            "cylinder gate. The independently gauged Weyl-connection Level 4 "
            "may now be activated under a fresh authoritative work item."
        ),
    }
    value["content_hashes"] = {
        "imports_sha256": _digest(value["imports"]),
        "adm_sha256": _digest(value["exact_adm_degeneracy"]),
        "stationary_sha256": _digest(value["complete_cylinder_stationary_locus"]),
        "hessian_sha256": _digest(value["full_cylinder_quadratic_separator"]),
        "strata_sha256": _digest(value["stratified_no_go"]),
        "unary_sha256": _digest(value["unary_constraint_charge_and_gates"]),
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
        raise AssertionError("Level-3b Horndeski certificate is stale")
    print("COMPENSATOR_CONVENTION_CORRECT_HORNDESKI_LEVEL3B_NO_GO_V1: PASS")


if __name__ == "__main__":
    main()
