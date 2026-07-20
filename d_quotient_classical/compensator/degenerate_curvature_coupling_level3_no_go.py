#!/usr/bin/env python3
"""Exact Level-3 degeneracy test for the declared minimal curvature coupling."""

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
    "COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1.json"
)
LEVEL2 = {
    "path": (
        ROOT
        / "d_quotient_classical/certificates/"
        "COMPENSATOR_KINETIC_BRAIDING_LEVEL2_NO_GO_V1.json"
    ),
    "sha256": "833d7e0266fc81df2d73e9b822db29e451d8df7f0ae9e0cbe06aa391d8dcf584",
    "source_commit": "db36f419b03ea467f7829c1464c17c800b8aa218",
    "result_id": "COMPENSATOR_KINETIC_BRAIDING_LEVEL2_NO_GO_V1",
    "result_state": "SCOPED_LEVEL2_KINETIC_BRAIDING_GOOD_LOCUS_EMPTY",
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


def _import_level2() -> dict[str, Any]:
    actual = _sha(LEVEL2["path"])
    payload = json.loads(LEVEL2["path"].read_text())
    if (
        actual != LEVEL2["sha256"]
        or payload["result_id"] != LEVEL2["result_id"]
        or payload["result_state"] != LEVEL2["result_state"]
        or payload["terminal_verdict"]["selected_level2_action"]
    ):
        raise AssertionError("terminal Level-2 import drifted")
    return {
        "path": str(LEVEL2["path"].relative_to(ROOT)),
        "result_id": payload["result_id"],
        "result_state": payload["result_state"],
        "sha256": actual,
        "source_commit": LEVEL2["source_commit"],
        "selected_action": False,
    }


def _adm_degeneracy() -> dict[str, Any]:
    X, F, F_X, B = sp.symbols("X F F_X B")
    h, A = sp.symbols("h A")

    # Flat homogeneous ADM fixture:
    # ds^2=-N^2 dt^2+a^2 dx^i dx^i, theta=nu t,
    # h=dot(a)/(aN), A=dot(N)/N^2 and X=-nu^2/N^2.
    curvature_after_ibp = -6 * F * h**2 + 12 * X * F_X * A * h
    hessian_square = -6 * X * h**2 + 6 * X * A * h
    kinetic = sp.expand(curvature_after_ibp + B * hessian_square)
    expected = -6 * (F + B * X) * h**2 + 6 * X * (2 * F_X + B) * A * h
    if sp.expand(kinetic - expected) != 0:
        raise AssertionError("ADM integration-by-parts identity drifted")

    velocities = sp.Matrix([h, A])
    Hessian = sp.hessian(kinetic, velocities)
    determinant = sp.factor(Hessian.det())
    expected_det = -36 * X**2 * (2 * F_X + B) ** 2
    if sp.factor(determinant - expected_det) != 0:
        raise AssertionError("degeneracy determinant drifted")

    literal = sp.simplify(Hessian.subs(B, F_X))
    literal_det = sp.factor(literal.det())
    if literal_det != -324 * X**2 * F_X**2:
        raise AssertionError("literal coefficient determinant drifted")

    corrected = sp.simplify(Hessian.subs(B, -2 * F_X))
    if corrected.det() != 0 or corrected[0, 1] != 0:
        raise AssertionError("convention-correct degeneracy surface drifted")

    return {
        "fixture": {
            "metric": "ds^2=-N^2 dt^2+a^2 delta_ij dx^i dx^j",
            "clock": "theta=nu t",
            "variables": {
                "h": "dot(a)/(aN)",
                "A": "dot(N)/N^2",
                "X": "-nu^2/N^2",
            },
            "active_clock_condition": "X<0",
        },
        "raw_identities": {
            "Ricci_scalar": "R=6(Dh+2h^2)",
            "clock_Hessian_square_difference": (
                "(Box theta)^2-(nabla_a nabla_b theta)^2"
                "=-6X h^2+6X A h"
            ),
            "X_time_derivative": "dot(X)=-2NAX",
            "curvature_term_after_boundary_reduction": (
                "sqrt(-g)F(X)R -> Na^3[-6F h^2+12X F_X A h]"
            ),
        },
        "generalized_minimal_pair": {
            "density": (
                "F(X)R+B[(Box theta)^2-(nabla_a nabla_b theta)^2]"
            ),
            "kinetic_density_over_Na3": _q(kinetic),
            "velocity_order": ["h", "A"],
            "velocity_Hessian": _matrix(Hessian),
            "determinant": _q(determinant),
            "active_clock_degeneracy_ideal": ["B+2F_X"],
            "active_clock_degeneracy_surface": "B=-2F_X",
        },
        "literal_work_item_pair": {
            "coefficient_identification": "B=F_X",
            "velocity_Hessian": _matrix(literal),
            "determinant": _q(literal_det),
            "active_clock_rank": {
                "F_X_nonzero": 2,
                "F_X_zero_F_nonzero": 1,
                "F_X_zero_F_zero": 0,
            },
            "degenerate_intersection_ideal": ["B-F_X", "B+2F_X"],
            "reduced_intersection": "F_X=0 and B=0 over characteristic zero",
        },
        "rank_change_surfaces": [
            {
                "surface": "X=0",
                "scope": "inactive-clock boundary; excluded by the active-clock gate",
            },
            {
                "surface": "B=-2F_X",
                "scope": "general minimal pair; convention-correct Horndeski surface",
            },
            {
                "surface": "F_X=0",
                "scope": (
                    "only literal active-clock degeneracy surface; the coupling "
                    "collapses to a constant F R term"
                ),
            },
        ],
    }


def _literal_locus() -> dict[str, Any]:
    f0, f1, B = sp.symbols("f0 f1 B")
    equations = [B - f1, B + 2 * f1]
    groebner = sp.groebner(equations, B, f1, order="lex")
    if list(groebner.polys) != [
        sp.Poly(B, B, f1),
        sp.Poly(f1, B, f1),
    ]:
        raise AssertionError("literal/degenerate intersection basis drifted")
    if groebner.reduce(B)[1] != 0 or groebner.reduce(f1)[1] != 0:
        raise AssertionError("literal intersection does not reduce to zero slope")
    return {
        "declared_function": "F(X)=f0+f1 X",
        "literal_second_derivative_coefficient": "B=F_X=f1",
        "exact_elimination_order": ["B", "f1"],
        "input_ideal_generators": ["B-f1", "B+2f1"],
        "groebner_basis": ["B", "f1"],
        "complete_active_clock_strata": {
            "f1_nonzero": {
                "rank": 2,
                "status": "FAIL_NONDEGENERATE_LAPSE_ACCELERATION",
                "novel_curvature_coupling": True,
            },
            "f1_zero": {
                "rank": "1 if f0 is nonzero, otherwise 0",
                "status": "COLLAPSES_TO_IMPORTED_P2_FAMILY",
                "novel_curvature_coupling": False,
                "parameter_absorption": (
                    "M_P_squared_effective=M_P_squared+2f0"
                ),
            },
        },
        "good_locus": "EMPTY",
        "completeness": (
            "For X nonzero, the exact determinant vanishes iff "
            "F_X=0. The resulting constant f0 R term is already the "
            "Einstein-Hilbert coefficient in the complete imported P2 family, "
            "whose selected-action locus is empty."
        ),
    }


def _convention_control() -> dict[str, Any]:
    # Q=(Box theta)^2-H_ab H^ab differs from Ric(v,v) by a divergence.
    # Therefore X R-2Q=-2G_ab v^a v^b modulo a divergence.
    return {
        "status": "CONTROL_NOT_PART_OF_LITERAL_WORK_ITEM_FAMILY",
        "project_convention": "X=g_hat^{ab} partial_a(theta) partial_b(theta)",
        "standard_Horndeski_conversion": (
            "X_standard=-X/2, so G4_Xstandard=-2F_Xproject"
        ),
        "corrected_density": (
            "F(X)R-2F_X[(Box theta)^2-(nabla_a nabla_b theta)^2]"
        ),
        "boundary_identity_for_linear_F": (
            "F_X[X R-2((Box theta)^2-H_ab H^ab)]"
            "=-2F_X G_ab nabla^a(theta)nabla^b(theta) mod d_h"
        ),
        "constant_clock_cylinder": {
            "background_clock_gradient": "0",
            "pure_metric_Hessian_from_slope": "ZERO",
            "metric_clock_mixed_Hessian_from_slope": "ZERO",
            "clock_clock_Hessian": (
                "-4F_X G_bar^{ab} k_a k_b in the symmetric bilinear convention"
            ),
            "trace_lapse_repair": "NONE",
        },
        "does_not_establish": [
            "a full coefficient-locus theorem for the corrected family",
            "a Berger background solution for the corrected family",
            "a general Horndeski or DHOST no-go",
        ],
    }


def _gate_disposition() -> dict[str, Any]:
    return {
        "seven_gates": [
            {
                "gate": 1,
                "name": "complete action and degeneracy",
                "status": "FAIL_ON_EVERY_NOVEL_LITERAL_STRATUM",
            },
            {
                "gate": 2,
                "name": "full action-origin BV unary data",
                "status": "NOT_REACHED_AFTER_INVARIANT_SEPARATOR",
            },
            {
                "gate": 3,
                "name": "both background Euler systems",
                "status": "NOT_REACHED_AFTER_INVARIANT_SEPARATOR",
            },
            {
                "gate": 4,
                "name": "scalar and tensor principal symbols",
                "status": "NOT_REACHED_AFTER_INVARIANT_SEPARATOR",
            },
            {
                "gate": 5,
                "name": "constraints and reduced pairing",
                "status": "NOT_REACHED_AFTER_INVARIANT_SEPARATOR",
            },
            {
                "gate": 6,
                "name": "characteristic roots and charges",
                "status": "NOT_REACHED_AFTER_INVARIANT_SEPARATOR",
            },
            {
                "gate": 7,
                "name": "relational-clock inequalities",
                "status": "NOT_REACHED_AFTER_INVARIANT_SEPARATOR",
            },
        ],
        "action_origin_symmetry_rows": {
            "status": "KINEMATIC_ROWS_ONLY",
            "Q_g_hat": "Lie_xi(g_hat)",
            "Q_theta": "Lie_xi(theta)",
            "Weyl_action_on_g_hat_and_theta": "ZERO",
            "gauge_algebra": "unchanged Diff semidirect Weyl algebra",
            "new_gauge_generator": False,
            "Euler_antifield_rows": (
                "NOT_CONSTRUCTED because every novel literal coefficient "
                "fails the prior action-degeneracy gate"
            ),
        },
        "selected_action": False,
        "full_BV_unary_export": False,
        "nonlinear_q2": False,
    }


def build() -> dict[str, Any]:
    imported = {"level2_no_go": _import_level2()}
    degeneracy = _adm_degeneracy()
    locus = _literal_locus()
    control = _convention_control()
    gates = _gate_disposition()
    verdict = {
        "complete_literal_minimal_family_checked": True,
        "novel_active_clock_degenerate_stratum_exists": False,
        "collapsed_stratum_imported_P2_good_locus": "EMPTY",
        "selected_level3_action": False,
        "first_invariant_separator": (
            "with X=(nabla theta)^2, the literal +F_X Hessian-square "
            "coefficient gives det(H_vel)=-324 X^2 F_X^2, so every nonzero "
            "slope carries a nondegenerate lapse-acceleration velocity block"
        ),
        "result": "SCOPED_LEVEL3_LITERAL_CURVATURE_COUPLING_GOOD_LOCUS_EMPTY",
    }
    value = {
        "schema": "pure-weyl-compensator-degenerate-curvature-level3-no-go-v1",
        "result_id": (
            "COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1"
        ),
        "result_state": (
            "SCOPED_LEVEL3_LITERAL_CURVATURE_COUPLING_GOOD_LOCUS_EMPTY"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imported,
        "conventions": {
            "signature": "(-,+,+,+)",
            "X": "g_hat^{ab} partial_a(theta) partial_b(theta)",
            "active_clock": "X<0",
            "level2_braiding_coefficient": "0",
            "arithmetic": "exact characteristic-zero rational polynomial algebra",
        },
        "complete_declared_action": {
            "density": (
                "alpha_B C^2/8+alpha_R R^2+M_P_squared R/2"
                "+p0+p1X+p2X^2+F(X)R"
                "+F_X[(Box theta)^2-(nabla_a nabla_b theta)^2]"
            ),
            "F": "f0+f1X",
            "independent_coefficients": [
                "alpha_B",
                "alpha_R",
                "M_P_squared",
                "p0",
                "p1",
                "p2",
                "f0",
                "f1",
            ],
            "redundancy": "f0 is absorbed by M_P_squared -> M_P_squared+2f0",
            "braiding": "ZERO",
        },
        "exact_adm_degeneracy": degeneracy,
        "complete_literal_locus": locus,
        "convention_correct_control": control,
        "gate_disposition": gates,
        "terminal_verdict": verdict,
        "exact_checks": {
            "level2_hash_and_semantics_pinned": True,
            "project_X_convention_explicit": True,
            "raw_FLRW_curvature_and_clock_Hessian_identities_exact": True,
            "boundary_reduction_exact": True,
            "velocity_Hessian_exact": True,
            "general_degeneracy_surface_exact": True,
            "literal_intersection_Groebner_elimination_exact": True,
            "all_active_clock_literal_strata_classified": True,
            "collapsed_stratum_reduced_to_imported_P2_theorem": True,
            "standard_convention_control_separated": True,
            "downstream_gates_fail_closed": True,
        },
        "claim_flags": {
            "SELECTED_LEVEL3_ACTION": False,
            "FULL_ACTION_ORIGIN_BV_UNARY": False,
            "BOTH_BACKGROUND_EULER_SYSTEMS": False,
            "SUPPORT_LOCAL_CAUSAL_PARENT": False,
            "NONLINEAR_Q2": False,
            "GENERAL_HORNDESKI_DHOST_NO_GO": False,
            "HADAMARD_ANOMALY_QME_OR_QUANTUM": False,
            "PARTICLE_SCATTERING_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact theorem covers only the literal Level-3 action written "
            "in the work item, with X=g_hat^{ab}partial_a(theta)partial_b(theta), "
            "F(X)=f0+f1X, coefficient +F_X on the Hessian-square difference, "
            "quadratic P(X), and zero Level-2 braiding. Every novel f1-nonzero "
            "active-clock stratum fails the exact ADM degeneracy gate; f1=0 "
            "collapses to the imported P2 family with empty good locus. The "
            "convention-correct -2F_X expression is recorded only as a control "
            "and is not given a full coefficient-locus disposition. No full BV "
            "unary, background, principal, charge, causal, nonlinear q2, "
            "Hadamard, anomaly/QME, particle, scattering, positivity or "
            "unitarity result follows, and this is not a general Horndeski or "
            "DHOST no-go."
        ),
        "next_gate": (
            "Activate the independently gauged geometric-variable level. If "
            "the convention-correct -2F_X family is desired as a separate "
            "physics question, create a new work item rather than silently "
            "changing this certificate's declared action."
        ),
    }
    value["content_hashes"] = {
        "imports_sha256": _digest(value["imports"]),
        "degeneracy_sha256": _digest(value["exact_adm_degeneracy"]),
        "locus_sha256": _digest(value["complete_literal_locus"]),
        "control_sha256": _digest(value["convention_correct_control"]),
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
        raise AssertionError("Level-3 curvature-coupling certificate is stale")
    print("COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1: PASS")


if __name__ == "__main__":
    main()
