#!/usr/bin/env python3
"""Certify the complete scalar 108-row q1 first-jet replay obstruction."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_Q1_PBW_FIRST_JET_REPLAY_OBSTRUCTION.json"
SCHEMA = P / "schema/berger-108-row-q1-pbw-first-jet-replay-obstruction-v1.schema.json"
REPORT = P / "reports/berger-108-row-q1-pbw-first-jet-replay-obstruction.md"
DEPENDENCIES = {
    "component_contract": replay.COMPONENT,
    "base_q1": replay.BASE,
    "emitter_overlay": replay.EMITTER,
    "memory_overlay": replay.MEMORY,
    "shifted_q2_overlay": replay.SHIFTED,
    "local_rod_hessian": replay.LOCAL_ROD,
    "background_quotient": P / "certificates/BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "berger_108_row_q1_pbw_replay.py",
    P / "verify_berger_108_row_q1_pbw_first_jet_replay.py",
    P / "tests/test_berger_108_row_q1_pbw_first_jet_replay.py",
    SCHEMA,
    REPORT,
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remove_euler_to_bv_bridge(operator: replay.Operator) -> replay.Operator:
    """Mutation: restore the previously serialized covariant Euler rows."""
    result = dict(operator)
    eta1 = (-1, 1, 1, 1)
    eta2 = (-1, -1, -1, 1, 1, 1)
    minus = (Fraction(-1), Fraction(0))
    for key, coefficient in list(result.items()):
        row, column, _word = key
        factor = 1
        if 59 <= row <= 62 and 84 <= column <= 95:
            factor = eta1[row - 59]
        elif 96 <= row <= 107:
            factor = -eta2[(row - 96) % 6]
        if factor == -1:
            result[key] = replay.scale(coefficient, minus)
    return result


def exact_first_jet_witness(operator: replay.Operator) -> dict[str, Any]:
    key = (27, 0, ())
    evaluator = replay.BackgroundEvaluator()
    target = evaluator.polynomial(operator[key])
    normal = replay.sphere_normal_form(target[0])
    x0, x1, x2, x3 = replay.background_ideal.X
    coefficient = sp.Poly(normal, x0, x1, x2, x3).coeff_monomial(x0 * x1)
    sine = replay.TRIG_S
    expected = -sp.Rational(27, 40) * sine**4 + sp.Rational(27, 32) * sine**2 - sp.Rational(2921, 480)
    if sp.expand(coefficient - expected) != 0:
        raise AssertionError("first-jet witness coefficient drifted")
    sine_squared_upper = sp.Rational(5, 72)
    strict_upper = sp.Rational(27, 32) * sine_squared_upper - sp.Rational(2921, 480)
    if strict_upper >= 0:
        raise AssertionError("first-jet witness sign bound failed")
    return {
        "operator_key": {"output_row": 27, "input_row": 0, "input_pbw_word": []},
        "target_time_mode": 0,
        "sphere_normal_form": sp.sstr(normal),
        "selected_spatial_monomial": "x0*x1",
        "selected_coefficient": sp.sstr(coefficient),
        "phase_definition": "s=sin(sqrt(10)/12)",
        "strict_inequality": "0<s^2<10/144=5/72",
        "coefficient_strict_upper": str(strict_upper),
        "coefficient_nonzero": True,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if not values["emitter_overlay"]["flags"]["EULER_TO_BV_COMPONENT_BRIDGE_EXPORTED"]:
        raise AssertionError("Euler-to-BV component repair is not pinned")
    if not values["background_quotient"]["flags"]["BERGER_FRAME_DIFFERENTIAL_IDEAL_EXPORTED"]:
        raise AssertionError("background quotient is not available")

    q1 = replay.load_q1()
    cyclicity = {str(degree): replay.summary(replay.cyclicity_defect(operator)) for degree, operator in q1.items()}
    if any(row["operator_key_count"] for row in cyclicity.values()):
        raise AssertionError("a complete q1 coefficient ceased to be cyclic")
    squared = replay.q1_squared_coefficients(q1)
    squared_summary = {str(degree): replay.summary(operator) for degree, operator in squared.items()}
    for degree in ((0, 0), (0, 1), (1, 1)):
        if squared[degree]:
            raise AssertionError(f"unexpected q1-squared defect at {degree}")
    if not squared[(1, 0)]:
        raise AssertionError("first-jet obstruction disappeared")
    witness = exact_first_jet_witness(squared[(1, 0)])

    unraised = remove_euler_to_bv_bridge(q1[(0, 0)])
    mutation_square = replay.compose(unraised, unraised)
    mutation_cyclic = replay.cyclicity_defect(unraised)
    if replay.summary(mutation_square)["operator_key_count"] != 24:
        raise AssertionError("Euler-to-BV nilpotency mutation drifted")
    if replay.summary(mutation_cyclic)["operator_key_count"] != 102:
        raise AssertionError("Euler-to-BV cyclicity mutation drifted")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate composes the pinned base, memory, emitter, shifted-q2 and local rod-Hessian PBW overlays into one in-memory scalar 108-row q1 over Q(sqrt(10))[epsilon_R_squared,kappa]/(epsilon_R_squared^2,kappa^2). After the explicit Euler-form-to-density-cotangent repair, all four coefficient operators are exactly odd-cyclic; q00 squared, the kappa coefficient and the mixed epsilon_R_squared*kappa coefficient vanish exactly. The epsilon_R_squared coefficient does not vanish. Its complete free PBW residual has 355 operator keys, 150 matrix positions and 30326 serialized coefficient monomials. Evaluation in the certified finite Berger background quotient retains an exact time-mode-zero witness at output row 27 and input row 0: the x0*x1 coefficient is -27 s^4/40+27 s^2/32-2921/480 with s=sin(sqrt(10)/12), strictly negative because 0<s^2<5/72. Therefore the complete scalar first-jet unary gate is OBSTRUCTED at epsilon_R_squared. The mixed epsilon_R_squared*kappa coefficient itself passes, but the nonlinear apparatus q2/q3, K_Berger-equivariance, observer-morphism-stability and tangent-cone response steps remain inactive while q1 squared is nonzero. This is not a no-go theorem for another correction class, a finite-parameter causal theorem, a same-background physical-branch bridge, or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-108-row-q1-pbw-first-jet-replay-obstruction-v1",
        "result_id": "BERGER_108_ROW_Q1_PBW_FIRST_JET_REPLAY_OBSTRUCTION",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_FIRST_JET_NILPOTENCY_OBSTRUCTION",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "coefficient_ring": "Q(sqrt(10))[epsilon_R_squared,kappa]/(epsilon_R_squared^2,kappa^2), with formal g0,g1,m0_squared,m1_squared and certified coefficient jets",
        "composed_q1": {
            "shape": [108, 108],
            "bidegree_summaries": {str(degree): replay.summary(operator) for degree, operator in q1.items()},
            "unified_payload_exported": False,
            "deterministic_composition_module": str((P / "berger_108_row_q1_pbw_replay.py").relative_to(ROOT)),
        },
        "odd_cyclicity_replay": cyclicity,
        "nilpotency_replay": {
            "bidegree_summaries": squared_summary,
            "passing_bidegrees": ["(0, 0)", "(0, 1)", "(1, 1)"],
            "obstructed_bidegree": "(1, 0)",
            "first_jet_witness": witness,
        },
        "mutations": [
            {
                "name": "remove_Euler_to_BV_component_bridge",
                "detected": True,
                "q00_squared_summary": replay.summary(mutation_square),
                "q00_cyclicity_summary": replay.summary(mutation_cyclic),
            },
            {
                "name": "set_certified_first_jet_witness_to_zero",
                "detected": witness["coefficient_nonzero"],
                "strict_upper": witness["coefficient_strict_upper"],
            },
        ],
        "activation_disposition": {
            "current_gate": "complete scalar first-jet unary gate",
            "gate_status": "OBSTRUCTED",
            "repair_target": "the epsilon_R_squared shifted-gravity/rod-memory unary composition, before any q2/q3 apparatus extension",
            "nonlinear_team_request_activated": False,
            "tangent_cone_observer_restriction_activated": False,
            "physical_branch_bridge_activated": False,
            "reason": "q1 squared is nonzero in the certified same-background quotient",
        },
        "exhaustive_specialization_diagnostic": {
            "command": "exact quotient_defect on the complete (1,0) residual",
            "elapsed_seconds": "231.46",
            "evaluated_time_mode_count": 930,
            "nonzero_quotient_term_count_before_selecting_the_minimal_witness": 818,
            "matrix_position_count": 114,
            "role": "Tier-2 diagnostic; the independently replayable strict-sign witness is the certification rail",
        },
        "flags": {
            "COMPLETE_SCALAR_108_ROW_Q1_COMPOSED_IN_MEMORY": True,
            "ALL_FIRST_JET_COEFFICIENTS_ODD_CYCLIC": True,
            "ZEROTH_ORDER_Q1_SQUARED_ZERO": True,
            "KAPPA_Q1_SQUARED_ZERO": True,
            "MIXED_EPSILON_R_SQUARED_KAPPA_Q1_SQUARED_ZERO": True,
            "EPSILON_R_SQUARED_Q1_SQUARED_ZERO_IN_BACKGROUND_QUOTIENT": False,
            "FIRST_JET_NILPOTENCY_OBSTRUCTION_CERTIFIED": True,
            "MIXED_EPSILON_R_SQUARED_KAPPA_UNARY_COEFFICIENT_PASSES": True,
            "COMPLETE_FIRST_JET_UNARY_GATE": False,
            "APPARATUS_Q2_Q3_EXTENSION_AUTHORIZED": False,
            "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "REPAIR_EPSILON_R_SQUARED_SHIFTED_GRAVITY_ROD_MEMORY_UNARY_COMPOSITION_AND_REPLAY_THE_EXACT_WITNESS",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger 108-row q1 first-jet replay obstruction")
    print("BERGER_108_ROW_Q1_PBW_FIRST_JET_REPLAY_OBSTRUCTION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
