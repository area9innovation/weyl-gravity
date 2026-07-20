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
    P / "verify_berger_108_row_arity_two_obstruction.py",
    P / "tests/test_berger_108_row_arity_two_obstruction.py",
    SCHEMA,
    REPORT,
]


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
        "operator_key_count": 3984,
        "serialized_term_count": 4272,
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
        "operator_key_count": 2772,
        "serialized_term_count": 2820,
        "nonzero_output_rows": expected_formal["nonzero_output_rows"],
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
    if set(source_values) != {"base_maxwell_typed", "emitter_physical"}:
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
    if set(q1_source_values) != {"base_gravity_clock_maxwell", "emitter"}:
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
        "The exact h_b(Theta_bar) chain-rule quotient then kills every spatial switch jet "
        "and replaces e0^p h_b^(n) by (3/4)^p h_b^(n+p). Before that quotient the residual "
        "has 3,984 keys and 4,272 monomials; after it the decisive same-background residual "
        "has 2,772 keys and 2,820 monomials on 24 output rows. Its first lexicographic "
        "witness is the shared typed Maxwell--emitter orbit: c_spatial_1_star on e1 A_0 "
        "and e1 K0_01 has coefficient -3 g0 h0. It source-isolates to the typed Maxwell "
        "and physical-emitter q2 sources crossed with the base/emitter q1 sources. Since "
        "this witness is at bidegree "
        "(0,0), neither the epsilon_R_squared nonlinear-clock unary correction nor "
        "any q3 term can cancel it inside the declared arity-two identity. The "
        "remaining first-bidegree coefficients are deliberately not evaluated once "
        "this lowest-cost falsifier fires; they are recorded as skipped, not passed. "
        "Therefore the complete arity-two identity is OBSTRUCTED. This "
        "certificate does not guess the remaining repair: the typed Maxwell-emitter "
        "shared-field orbit must be rederived from the common action after the now-fixed "
        "identical-slot factorial convention, and the later memory/clock orbit must also "
        "be replayed. The two-sided "
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
        "repair_gate": {
            "status": "OPEN",
            "required_object": "rederive the typed Maxwell-emitter shared-field q2 orbit from the common BV action in the suspended graded-symmetric factorial convention; do not flip or fit isolated coefficients",
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
        "next_gate": "REDERIVE_TYPED_MAXWELL_EMITTER_COMMON_ACTION_ORBIT_AND_REPLAY_Q1Q2",
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
        if (formal["operator_key_count"], formal["serialized_term_count"]) != (3984, 4272):
            raise SystemExit("stale formal arity-two audit")
        if (specialized["operator_key_count"], specialized["serialized_term_count"]) != (2772, 2820):
            raise SystemExit("stale switch-specialized arity-two audit")
        if audit["typed_64_row_base_control_summary"]["operator_key_count"] != 0:
            raise SystemExit("stale typed-base arity-two control")
        if audit["emitter_switch_specialization"]["clock_rate_e0_Theta_bar"] != "3/4":
            raise SystemExit("stale emitter-switch specialization")
        if (
            witness["output_row"], witness["left_input_row"], witness["left_pbw_multiindex"],
            witness["right_input_row"], witness["right_pbw_multiindex"],
        ) != (49, 55, [0, 1, 0, 0], 84, [0, 1, 0, 0]):
            raise SystemExit("stale same-background arity-two witness")
        if set(audit["first_defect_q2_source_isolation"]) != {"base_maxwell_typed", "emitter_physical"}:
            raise SystemExit("stale q2 source isolation")
        if set(audit["first_defect_q1_source_isolation"]) != {"base_gravity_clock_maxwell", "emitter"}:
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
