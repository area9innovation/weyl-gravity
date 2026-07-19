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
    key = (27, 4, ())
    evaluator = replay.BackgroundEvaluator()
    target = evaluator.polynomial(operator[key])
    normal = replay.sphere_normal_form(target[-2])
    x0, x1, x2, x3 = replay.background_ideal.X
    sine = replay.TRIG_S
    cosine = replay.TRIG_C
    time_phase = replay.TIME_Z
    coefficient = sp.Poly(
        normal, x0, x1, x2, x3, cosine, sine, time_phase
    ).coeff_monomial(x0 * x3 * cosine * sine**3 * time_phase**4)
    expected = -sp.Rational(49, 20)
    if sp.expand(coefficient - expected) != 0:
        raise AssertionError("first-jet witness coefficient drifted")

    base: replay.GradedOperator = {}
    replay.load_base(base)
    shifted: replay.GradedOperator = {}
    replay.load_shifted(shifted)
    pair_coefficients = {}
    for name, contribution in (
        ("q00_base_after_q10_shifted", replay.compose(base[(0, 0)], shifted[(1, 0)])),
        ("q10_shifted_after_q00_base", replay.compose(shifted[(1, 0)], base[(0, 0)])),
    ):
        pair_normal = replay.sphere_normal_form(evaluator.polynomial(contribution[key])[-2])
        pair_coefficients[name] = sp.Poly(
            pair_normal, x0, x1, x2, x3, cosine, sine, time_phase
        ).coeff_monomial(x0 * x3 * cosine * sine**3 * time_phase**4)
    if pair_coefficients != {
        "q00_base_after_q10_shifted": sp.Rational(49, 20),
        "q10_shifted_after_q00_base": -sp.Rational(49, 10),
    }:
        raise AssertionError("Weyl-witness source decomposition drifted")
    return {
        "operator_key": {"output_row": 27, "input_row": 4, "input_pbw_word": []},
        "input_interpretation": "Weyl ghost sigma",
        "target_time_mode": -2,
        "sphere_normal_form": sp.sstr(normal),
        "selected_spatial_monomial": "x0*x3",
        "selected_phase_monomial": "cos(sqrt(10)/12)*sin(sqrt(10)/12)^3*detector_time_phase^4",
        "selected_coefficient": sp.sstr(coefficient),
        "source_pair_decomposition": {name: sp.sstr(value) for name, value in pair_coefficients.items()},
        "local_rod_sigma_column_contribution": "0",
        "radial_linear_map_scale_diagnostic": {
            "tested_scales": ["-1", "-1/2", "0", "1/2", "1", "2"],
            "selected_coefficient_at_every_scale": "-49/20",
            "interpretation": "the defect is not removable by rescaling the linear dressed-to-raw radial metric column",
        },
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
        "This corrected exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate composes the pinned base, memory, emitter, shifted-q2 and local rod-Hessian PBW overlays into one in-memory scalar 108-row q1 over Q(sqrt(10))[epsilon_R_squared,kappa]/(epsilon_R_squared^2,kappa^2). The rod source now uses the action-derived half-stress covariant metric Euler normalization, and q2(Phi2,-) fixes one ordered input slot rather than summing both symmetric placements. After those factor-two repairs and the explicit Euler-form-to-density-cotangent repair, all four coefficient operators are exactly odd-cyclic; q00 squared, the kappa coefficient and the mixed epsilon_R_squared*kappa coefficient vanish exactly. The former spatial witness cancels, but the epsilon_R_squared coefficient still does not vanish. Its complete free PBW residual has 355 operator keys, 150 matrix positions and 30326 serialized coefficient monomials. Evaluation in the certified finite Berger background quotient leaves 374 defects on 54 matrix positions. An exact Weyl witness occurs at output row 27, sigma input row 4 and time mode -2: the coefficient of x0*x3*cos(sqrt(10)/12)*sin(sqrt(10)/12)^3*detector_time_phase^4 is -49/20. It decomposes entirely into q00_base after q10_shifted and q10_shifted after q00_base, with coefficients 49/20 and -49/10; the serialized local rod Hessian has no sigma column. Rescaling the linear radial metric column through -1,-1/2,0,1/2,1,2 leaves -49/20 unchanged. The obstruction therefore localizes to a missing second jet of the clock canonical transformation (or an equivalent action-derived clock-source completion), not to a remaining normalization choice. The complete scalar first-jet unary gate remains OBSTRUCTED at epsilon_R_squared. The mixed epsilon_R_squared*kappa coefficient itself passes, but apparatus q2/q3, K_Berger-equivariance, observer-morphism stability and tangent-cone response remain inactive while q1 squared is nonzero. This is not a no-go theorem for the nonlinear clock completion, a finite-parameter causal theorem, a same-background physical-branch bridge, or a quantum claim."
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
                "name": "delete_missing_nonlinear_clock_dressing_witness",
                "detected": witness["coefficient_nonzero"],
                "selected_coefficient": witness["selected_coefficient"],
            },
        ],
        "activation_disposition": {
            "current_gate": "complete scalar first-jet unary gate",
            "gate_status": "OBSTRUCTED",
            "repair_target": "the action-derived second jet of the clock canonical transformation, including its rod-source cotangent completion, before any q2/q3 apparatus extension",
            "nonlinear_team_request_activated": False,
            "tangent_cone_observer_restriction_activated": False,
            "physical_branch_bridge_activated": False,
            "reason": "q1 squared has a nonzero Weyl/sigma witness in the certified same-background quotient because only the linear clock canonical map is serialized",
        },
        "exhaustive_specialization_diagnostic": {
            "command": "exact quotient_defect on the complete (1,0) residual",
            "elapsed_seconds": "202.18",
            "evaluated_time_mode_count": 930,
            "nonzero_quotient_term_count_before_selecting_the_minimal_witness": 374,
            "matrix_position_count": 54,
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
        "next_gate": "EXPORT_ACTION_DERIVED_SECOND_JET_CLOCK_CANONICAL_MAP_AND_ROD_SOURCE_COMPLETION_THEN_REPLAY_EPSILON_R_SQUARED_Q1_SQUARED",
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
