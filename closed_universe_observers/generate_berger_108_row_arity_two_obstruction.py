#!/usr/bin/env python3
"""Export the first exact obstruction to the complete Berger arity-two replay."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_form_clock_chart as form_clock
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import (
    _multiindex_from_word,
    serialize,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_ARITY_TWO_OBSTRUCTION.json"
SCHEMA = P / "schema/berger-108-row-arity-two-obstruction-v1.schema.json"
REPORT = P / "reports/berger-108-row-arity-two-obstruction.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "completed_q1": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "complete_typed_q2": P / "certificates/BERGER_108_ROW_COMPLETE_Q2_PBW.json",
    "complete_q3": P / "certificates/BERGER_108_ROW_COMPLETE_Q3_PBW.json",
    "emitter_switches": P / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "berger_108_row_arity_replay.py",
    P / "berger_108_row_form_clock_chart.py",
    P / "verify_berger_108_row_arity_two_obstruction.py",
    P / "tests/test_berger_108_row_arity_two_obstruction.py",
    SCHEMA,
    REPORT,
]


@lru_cache(maxsize=1)
def form_clock_chart_audit() -> dict[str, Any]:
    """Prove that the form pullback is a canonical q1-coboundary, not a repair."""

    f2 = form_clock.f2_rows()
    field = form_clock.field_f2_rows()
    cotangent = form_clock.cotangent_f2_rows()
    expected = {
        "field": {
            "operator_key_count": 76,
            "serialized_term_count": 76,
            "nonzero_output_rows": list(range(55, 59)) + list(range(84, 96)),
            "maximum_total_input_order": 1,
        },
        "cotangent": {
            "operator_key_count": 172,
            "serialized_term_count": 172,
            "nonzero_output_rows": [38] + list(range(59, 63)) + list(range(96, 108)),
            "maximum_total_input_order": 1,
        },
        "complete": {
            "operator_key_count": 248,
            "serialized_term_count": 248,
            "nonzero_output_rows": [38] + list(range(55, 63)) + list(range(84, 108)),
            "maximum_total_input_order": 1,
        },
    }
    summaries = {
        "field": arity.bilinear_summary(field),
        "cotangent": arity.bilinear_summary(cotangent),
        "complete": arity.bilinear_summary(f2),
    }
    if summaries != expected:
        raise AssertionError(f"form-clock F2 support drifted: {summaries}")

    # These two fixtures distinguish the Maxwell pairing sign -1 from the
    # emitter pairing sign +1 in the Theta-star cotangent component.
    theta_star = cotangent[38]
    maxwell_fixture = (55, (), 59, (0,))
    emitter_fixture = (84, (), 96, (0,))
    if theta_star[maxwell_fixture] != form_clock.constant(1):
        raise AssertionError("Maxwell form-clock cotangent sign drifted")
    if theta_star[emitter_fixture] != form_clock.constant(-1):
        raise AssertionError("emitter form-clock cotangent sign drifted")

    q1 = replay.load_q1()
    correction = form_clock.conjugation_correction(q1)
    correction_summaries = {
        f"{degree[0]},{degree[1]}": arity.bilinear_summary(correction[degree])
        for degree in arity.SUPPORTED_BIDEGREES
    }
    expected_counts = {
        "0,0": (3108, 3156),
        "1,0": (1968, 5292),
        "0,1": (212, 768),
        "1,1": (440, 7288),
    }
    for degree, (keys, terms) in expected_counts.items():
        if (
            correction_summaries[degree]["operator_key_count"],
            correction_summaries[degree]["serialized_term_count"],
        ) != (keys, terms):
            raise AssertionError(f"form-clock conjugation correction drifted at {degree}")

    residuals = {
        f"{degree[0]},{degree[1]}": arity.bilinear_summary(
            arity.arity_two_degree(degree, q1, correction)
        )
        for degree in arity.SUPPORTED_BIDEGREES
    }
    if any(summary["operator_key_count"] for summary in residuals.values()):
        raise AssertionError("form-clock coordinate correction ceased to be a q1 cocycle")
    return {
        "geometric_field_map": "A_dressed=A_raw-L_(Theta e0)A_raw+O(3); K_b_dressed=K_b_raw-L_(Theta e0)K_b_raw+O(3)",
        "cotangent_map": "signed formal-adjoint lift -S^{-1}(D C2)^dagger S on Theta_star, A_plus and K_b_plus",
        "quadratic_chart_summaries": summaries,
        "pairing_sign_fixtures": {
            "Theta_star_from_A0_A0_plus": "+1",
            "Theta_star_from_K0_01_K0_01_plus": "-1",
        },
        "conjugation_correction_summaries": correction_summaries,
        "correction_arity_two_residuals": residuals,
        "existing_obstruction_change_summary": residuals["0,0"],
        "disposition": "CERTIFIED_CANONICAL_CHART_CHANGE_DOES_NOT_REPAIR_RAW_WARD_DEFECT",
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _base_q1() -> replay.GradedOperator:
    value: replay.GradedOperator = {}
    replay.load_base(value)
    return value


def _q1_source_parts() -> dict[str, replay.GradedOperator]:
    parts: dict[str, replay.GradedOperator] = {}
    value: replay.GradedOperator = {}
    replay.load_base(value)
    parts["base_gravity_clock_maxwell"] = value
    for name, path, root_key in (
        ("emitter", replay.EMITTER, "emitter_overlay"),
        ("memory", replay.MEMORY, None),
        ("local_rod", replay.LOCAL_ROD, None),
    ):
        value = {}
        document = json.loads(path.read_text())
        blocks = document[root_key]["blocks"] if root_key else document["blocks"]
        replay.load_generic_blocks(value, blocks)
        parts[name] = value
    value = {}
    replay.load_shifted(value)
    parts["shifted_nonlinear_clock"] = value
    return parts


def _witness_record(
    target: int,
    key: arity.BilinearKey,
    coefficient: replay.Polynomial,
) -> dict[str, Any]:
    left, left_word, right, right_word = key
    rows = json.loads(replay.COMPONENT.read_text())["carrier_contract"]["rows"]
    evaluator = replay.BackgroundEvaluator()
    quotient_modes = []
    try:
        evaluated = evaluator.polynomial(coefficient)
        quotient_status = "EVALUATED_IN_CERTIFIED_BACKGROUND_QUOTIENT"
    except ValueError:
        evaluated = {}
        quotient_status = "NOT_APPLICABLE_FORMAL_PARAMETER_PROFILE_COEFFICIENT"
    for mode, expression in sorted(evaluated.items()):
        normal = replay.sphere_normal_form(expression)
        if normal != 0:
            quotient_modes.append({"time_mode": mode, "normal_form": sp.sstr(normal)})
    return {
        "output_row": target,
        "output_row_id": rows[target]["row_id"],
        "left_input_row": left,
        "left_input_row_id": rows[left]["row_id"],
        "left_pbw_multiindex": list(_multiindex_from_word(left_word)),
        "right_input_row": right,
        "right_input_row_id": rows[right]["row_id"],
        "right_pbw_multiindex": list(_multiindex_from_word(right_word)),
        "coefficient": serialize(coefficient),
        "background_quotient_evaluation_status": quotient_status,
        "background_quotient_nonzero_modes": quotient_modes,
    }


@lru_cache(maxsize=1)
def replay_audit() -> dict[str, Any]:
    q1 = replay.load_q1()
    q2 = arity.load_q2()
    defect = arity.arity_two_degree((0, 0), q1, q2)
    formal_summary = arity.bilinear_summary(defect)
    expected_formal = {
        "operator_key_count": 3432,
        "serialized_term_count": 3720,
        "nonzero_output_rows": [
            49, 50, 51, 52, 59, 60, 61, 62, 80, 81, 82, 83, 96, 97,
            98, 99, 100, 101, 102, 103, 104, 105, 106, 107,
        ],
        "maximum_total_input_order": 3,
    }
    if formal_summary != expected_formal:
        raise AssertionError(f"formal arity-two obstruction drifted: {formal_summary}")

    specialized_defect = arity.specialize_bilinear_rows(defect)
    summary = arity.bilinear_summary(specialized_defect)
    expected = {
        "operator_key_count": 2340,
        "serialized_term_count": 2388,
        "nonzero_output_rows": [
            52, 59, 60, 61, 62, 80, 81, 82, 83, 96, 97, 98, 99,
            100, 101, 102, 103, 104, 105, 106, 107,
        ],
        "maximum_total_input_order": 3,
    }
    if summary != expected:
        raise AssertionError(f"switch-specialized arity-two obstruction drifted: {summary}")

    first = min(
        (target, key, coefficient)
        for target, row in specialized_defect.items()
        for key, coefficient in row.items()
    )
    witness = _witness_record(*first)
    if (
        witness["background_quotient_evaluation_status"]
        == "EVALUATED_IN_CERTIFIED_BACKGROUND_QUOTIENT"
        and not witness["background_quotient_nonzero_modes"]
    ):
        raise AssertionError("first arity-two witness vanished in the background quotient")

    base_defect = arity.arity_two_degree(
        (0, 0), _base_q1(), arity.load_q2(sources={"base_gravity_clock", "base_maxwell_typed"})
    )
    if base_defect:
        raise AssertionError("typed 64-row base control ceased to satisfy arity two")

    source_values = {}
    parity = arity.parities()
    witness_key = (
        witness["left_input_row"],
        arity.replay.word(witness["left_pbw_multiindex"]),
        witness["right_input_row"],
        arity.replay.word(witness["right_pbw_multiindex"]),
    )
    for source in (
        "base_gravity_clock", "base_maxwell_typed", "apparatus_scalar_BV", "dressed_rod_clock", "rod_metric",
        "memory_transport", "normalized_readout", "emitter_physical",
        "emitter_Diff_BV",
    ):
        row = arity.arity_two_row(
            witness["output_row"], (0, 0), q1,
            arity.load_q2(sources={source}), parity,
        )
        row = arity.specialize_bilinear_rows({witness["output_row"]: row}).get(
            witness["output_row"], {}
        )
        if witness_key in row:
            source_values[source] = serialize(row[witness_key])
    if set(source_values) != {"emitter_Diff_BV"}:
        raise AssertionError(f"first-witness source isolation drifted: {source_values}")

    q1_source_values = {}
    complete_q2 = arity.load_q2()
    for source, source_q1 in _q1_source_parts().items():
        row = arity.arity_two_row(
            witness["output_row"], (0, 0), source_q1, complete_q2,
            parity,
        )
        row = arity.specialize_bilinear_rows({witness["output_row"]: row}).get(
            witness["output_row"], {}
        )
        if witness_key in row:
            q1_source_values[source] = serialize(row[witness_key])
    if set(q1_source_values) != {"emitter"}:
        raise AssertionError(f"first-witness q1 source isolation drifted: {q1_source_values}")

    return {
        "tested_bidegree": [0, 0],
        "formal_differential_coefficient_defect_summary": formal_summary,
        "emitter_switch_specialization": {
            "clock_rate_e0_Theta_bar": "3/4",
            "spatial_clock_jets": "e1(Theta_bar)=e2(Theta_bar)=e3(Theta_bar)=0",
            "chain_rule": "e0^p h_b^(n)(Theta_bar)=(3/4)^p h_b^(n+p)(Theta_bar); every spatial h_b jet vanishes",
        },
        "complete_defect_summary": summary,
        "first_lexicographic_defect": witness,
        "first_defect_q2_source_isolation": source_values,
        "first_defect_q1_source_isolation": q1_source_values,
        "typed_64_row_base_control_summary": arity.bilinear_summary(base_defect),
        "higher_bidegrees_not_run": [[1, 0], [0, 1], [1, 1]],
        "stop_reason": "the lowest bidegree already has a nonzero exact defect",
    }


def build(*, audit: dict[str, Any] | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED",
        "completed_q1": "COMPLETE_FIRST_BIDEGREE_UNARY_GATE",
        "complete_typed_q2": "COMPLETE_SCALAR_108_ROW_Q2_EXPORTED",
        "complete_q3": "COMPLETE_SCALAR_108_ROW_Q3_EXPORTED",
        "emitter_switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
    }
    for name, flag in required.items():
        if values[name]["flags"].get(flag) is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    audit = audit or replay_audit()
    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE obstruction replays the lowest "
        "(epsilon_R_squared,kappa)=(0,0) coefficient of q1 q2+q2(q1,-)+(-1)^|x|q2(-,q1) "
        "on the canonical 108-row Berger differential-coefficient PBW carrier. The "
        "typed 64-row gravity-clock-Maxwell base is an exact zero control. The "
        "action-derived dressed-rod clock correction removes the former +e0 e1 R0_1 "
        "witness and all six rod/rod-cotangent defect rows. The physical-emitter action "
        "exporter now also restores the multiplicity-two second derivative when its two "
        "remaining action slots coincide; this removes 244 further formal operator keys. "
        "The metric action derivatives are now also raised to the canonical stress rows "
        "with T=-2 delta S/dg, while the three frozen spatial Diff momentum-map rows carry "
        "the matching -2 Hamiltonian weight. This common-action bridge removes the former "
        "c_spatial_1_star witness and all same-background defects on rows 49--51 without "
        "altering the relational temporal row. The exact h_b(Theta_bar) chain-rule quotient then kills every spatial switch jet "
        "and replaces e0^p h_b^(n) by (3/4)^p h_b^(n+p). Before that quotient the residual "
        "has 3,432 keys and 3,720 monomials; after it the decisive same-background residual "
        "has 2,340 keys and 2,388 monomials on 21 output rows. Its first lexicographic "
        "witness has moved to the relational temporal orbit: tau_star on e0 e1 A_0 "
        "and undifferentiated K0_01 has coefficient +g0 h0. It source-isolates entirely "
        "to the emitter Diff--BV q2 source crossed with the emitter q1 source. Since "
        "this witness is at bidegree "
        "(0,0), neither the epsilon_R_squared nonlinear-clock unary correction nor "
        "any q3 term can cancel it inside the declared arity-two identity. The "
        "remaining first-bidegree coefficients are deliberately not evaluated once "
        "this lowest-cost falsifier fires; they are recorded as skipped, not passed. "
        "Therefore the complete arity-two identity is OBSTRUCTED. This "
        "canonical form-clock gate now removes one possible ambiguity without fitting the residual. "
        "The quadratic pullback A_dressed=A_raw-L_(Theta e0)A_raw and its two-form analog, "
        "together with the signed formal-adjoint BV cotangent lift, give 248 exact F2 keys. "
        "Their induced q2 coordinate correction is a q1 cocycle in all four retained "
        "bidegrees, so it changes the displayed obstruction by exactly zero. A consistent "
        "relational clock conjugation can relocate the residual but cannot repair it. The "
        "remaining gate is therefore a fresh component export of the raw temporal "
        "gravity-clock-Maxwell-emitter Ward orbit from one common action, including the later "
        "memory/clock rows; the earlier covariant row-coverage theorem did not certify this "
        "coefficientwise PBW identity. The two-sided "
        "source isolation is diagnostic only: it identifies the q2 and q1 sources "
        "of the first key, not a proof that no other apparatus or emitter orbit is "
        "missing. The existing q2 and q3 payloads "
        "remain valid as source-labelled tensors, but their coexistence with the "
        "completed unary does not define a certified L-infinity coderivation. "
        "Because arity two already fails, "
        "the q2q2+q1q3 replay, K_Berger equivariance, observer-morphism stability, "
        "detector restriction to Z2, nonlinear response rank, physical Bridge 3, "
        "finite-parameter causal propagation and all quantum claims remain fail-closed. "
        "No compact-product mode is identified with a Berger row."
    )
    return {
        "schema": "closed-universe-berger-108-row-arity-two-obstruction-v1",
        "result_id": "BERGER_108_ROW_ARITY_TWO_OBSTRUCTION",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "OBSTRUCTED_COMPLETE_108_ROW_ARITY_TWO_IDENTITY",
        "atlas_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "arity_two_replay": audit,
        "form_clock_chart_gate": form_clock_chart_audit(),
        "repair_gate": {
            "status": "OPEN",
            "required_object": "re-export the raw temporal gravity-clock-Maxwell-emitter Ward orbit coefficientwise from one common action, include the later memory/clock rows, then transport the complete zero identity through the certified form clock chart; do not flip or fit isolated coefficients",
            "acceptance": "the complete (0,0) defect and then every first-bidegree q1q2 coefficient vanish exactly, with the typed 64-row base retained as a zero control",
        },
        "activation_disposition": {
            "complete_arity_two_identity": "OBSTRUCTED",
            "arity_three_replay_authorized": False,
            "K_Berger_equivariance_authorized": False,
            "observer_morphism_stability_authorized": False,
            "detector_response_on_second_order_cone_authorized": False,
            "physical_branch_bridge_activated": False,
        },
        "flags": {
            "TYPED_64_ROW_BASE_ARITY_TWO_CONTROL_ZERO": True,
            "COMPLETE_108_ROW_ARITY_TWO_OBSTRUCTED": True,
            "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False,
            "K_BERGER_EQUIVARIANCE_ON_COMPLETE_INTERACTION_CERTIFIED": False,
            "OBSERVER_MORPHISM_STABILITY_CERTIFIED": False,
            "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "REEXPORT_RAW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_AND_REPLAY_Q1Q2",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--reuse-audit",
        action="store_true",
        help="reuse the emitted exact replay audit while refreshing validated metadata",
    )
    args = parser.parse_args()
    audit = None
    if args.reuse_audit:
        existing = json.loads(CERTIFICATE.read_text())
        audit = existing["arity_two_replay"]
        formal = audit["formal_differential_coefficient_defect_summary"]
        specialized = audit["complete_defect_summary"]
        witness = audit["first_lexicographic_defect"]
        if (formal["operator_key_count"], formal["serialized_term_count"]) != (3432, 3720):
            raise SystemExit("stale formal arity-two audit")
        if (specialized["operator_key_count"], specialized["serialized_term_count"]) != (2340, 2388):
            raise SystemExit("stale switch-specialized arity-two audit")
        if audit["typed_64_row_base_control_summary"]["operator_key_count"] != 0:
            raise SystemExit("stale typed-base arity-two control")
        if audit["emitter_switch_specialization"]["clock_rate_e0_Theta_bar"] != "3/4":
            raise SystemExit("stale emitter-switch specialization")
        if (
            witness["output_row"], witness["left_input_row"], witness["left_pbw_multiindex"],
            witness["right_input_row"], witness["right_pbw_multiindex"],
        ) != (52, 55, [1, 1, 0, 0], 84, [0, 0, 0, 0]):
            raise SystemExit("stale same-background arity-two witness")
        if set(audit["first_defect_q2_source_isolation"]) != {"emitter_Diff_BV"}:
            raise SystemExit("stale q2 source isolation")
        if set(audit["first_defect_q1_source_isolation"]) != {"emitter"}:
            raise SystemExit("stale q1 source isolation")
    value = build(audit=audit)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger 108-row arity-two obstruction")
    print("BERGER_108_ROW_ARITY_TWO_OBSTRUCTION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
