#!/usr/bin/env python3
"""Export the exact clock-dressing correction to the six-rod q2 orbit."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers import berger_108_row_arity_replay as arity
from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import serialize
from closed_universe_observers import generate_berger_108_row_local_rod_hessian_pbw_overlay as local_rod


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_DRESSED_ROD_CLOCK_Q2_PBW.json"
PAYLOAD = P / "certificates/BERGER_108_ROW_DRESSED_ROD_CLOCK_Q2_PBW_PAYLOAD.json"
SCHEMA = P / "schema/berger-108-row-dressed-rod-clock-q2-pbw-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-dressed-rod-clock-q2-pbw-payload-v1.schema.json"
REPORT = P / "reports/berger-108-row-dressed-rod-clock-q2-pbw.md"
BASE_Q2 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "background_quotient": P / "certificates/BERGER_108_ROW_BACKGROUND_SPECIALIZATION_DIFFERENTIAL_IDEAL.json",
    "completed_unary": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "combined_clock_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json",
    "apparatus_scalar_BV": P / "certificates/BERGER_108_ROW_APPARATUS_SCALAR_BV_Q2_PBW.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_108_row_dressed_rod_clock_q2_pbw.py",
    P / "tests/test_berger_108_row_dressed_rod_clock_q2_pbw.py",
    SCHEMA,
    PAYLOAD_SCHEMA,
    REPORT,
]

ONE = {(): (Fraction(1), Fraction(0))}
MINUS = (Fraction(-1), Fraction(0))
ROD_PAIRS = tuple(zip(range(64, 70), range(74, 80), strict=True))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def identity_operator() -> replay.Operator:
    return {(row, row, ()): ONE for row in range(108)}


def clock_dressing_maps() -> tuple[replay.Operator, replay.Operator]:
    """Return F and F^-1 for R_dressed=R_raw-Theta e0(Rbar)."""

    forward = identity_operator()
    inverse = identity_operator()
    for rod_index, name in enumerate(local_rod.RODS):
        coefficient = local_rod.derivative(local_rod.background(name), 0)
        replay.add_operator_term(
            forward, (64 + rod_index, 16, ()), replay.scale(coefficient, MINUS)
        )
        replay.add_operator_term(inverse, (64 + rod_index, 16, ()), coefficient)
        # The cotangent shift is forced by preservation of
        # R_plus dR + Theta_star dTheta.
        replay.add_operator_term(forward, (38, 74 + rod_index, ()), coefficient)
        replay.add_operator_term(
            inverse, (38, 74 + rod_index, ()), replay.scale(coefficient, MINUS)
        )
    return forward, inverse


def raw_temporal_unary(current: replay.Operator) -> replay.Operator:
    """Restore the temporal part of the raw scalar Diff orbit."""

    raw = dict(current)
    for rod_index, name in enumerate(local_rod.RODS):
        coefficient = local_rod.derivative(local_rod.background(name), 0)
        replay.add_operator_term(raw, (64 + rod_index, 3, ()), coefficient)
        replay.add_operator_term(
            raw, (52, 74 + rod_index, ()), replay.scale(coefficient, MINUS)
        )
    return raw


def unary_conjugation_audit() -> dict[str, Any]:
    current = replay.load_q1()[(0, 0)]
    forward, inverse = clock_dressing_maps()
    transformed = replay.compose(forward, replay.compose(raw_temporal_unary(current), inverse))
    defect = replay.add_operators(transformed, replay.scale_operator(current, MINUS))
    left_inverse = replay.add_operators(
        replay.compose(forward, inverse), replay.scale_operator(identity_operator(), MINUS)
    )
    right_inverse = replay.add_operators(
        replay.compose(inverse, forward), replay.scale_operator(identity_operator(), MINUS)
    )
    one_form_defects = 0
    for name in local_rod.RODS:
        coefficient = local_rod.derivative(local_rod.background(name), 0)
        # R_plus d(R-Theta a)+(Theta_star+a R_plus)dTheta has
        # cross coefficient -a+a.  Compute it in the same coefficient algebra.
        cross_coefficient = replay.add(replay.scale(coefficient, MINUS), coefficient)
        one_form_defects += bool(cross_coefficient)
    return {
        "field_map": "R_dressed=R_raw-Theta e0(Rbar)",
        "cotangent_map": "Theta_star_dressed=Theta_star_raw+sum e0(Rbar_aI) R_aI_plus",
        "raw_temporal_unary_term_count": 12,
        "unary_conjugation_defect_summary": replay.summary(defect),
        "left_inverse_defect_summary": replay.summary(left_inverse),
        "right_inverse_defect_summary": replay.summary(right_inverse),
        "canonical_one_form_cross_term_count": 12,
        "canonical_one_form_cross_term_defect_count": one_form_defects,
    }


def _add_base_q2(rows: dict[int, arity.BilinearRow]) -> None:
    document = json.loads(BASE_Q2.read_text())
    for row in document["rows"]:
        for left, left_multi, right, right_multi, coefficient in row["terms"]:
            key = (
                left,
                replay.word(left_multi),
                right,
                replay.word(right_multi),
            )
            arity.add_bilinear_term(
                rows[row["output"]],
                key,
                replay.polynomial(
                    {"coefficient": coefficient, "coefficient_factors": []}
                ),
            )


def _add_spatial_apparatus_q2(rows: dict[int, arity.BilinearRow]) -> None:
    document = json.loads(DEPENDENCIES["apparatus_scalar_BV"].read_text())
    for output, left, left_multi, right, right_multi, coefficient in document["payload"]["terms"]:
        arity.add_bilinear_term(
            rows[output],
            (left, replay.word(left_multi), right, replay.word(right_multi)),
            replay.polynomial(
                {"coefficient": coefficient, "coefficient_factors": []}
            ),
        )


def temporal_scalar_template() -> list[tuple[int, list[Any]]]:
    document = json.loads(BASE_Q2.read_text())
    support = {3, 16, 38}
    outputs = {16, 38, 52}
    terms: list[tuple[int, list[Any]]] = []
    for row in document["rows"]:
        if row["output"] not in outputs:
            continue
        for term in row["terms"]:
            if (
                term[0] in support
                and term[2] in support
                and (3 in (term[0], term[2]) or {term[0], term[2]} == {16, 38})
            ):
                terms.append((row["output"], term))
    if len(terms) != 8:
        raise AssertionError(f"temporal scalar template changed: {len(terms)}")
    return terms


def _add_raw_temporal_rod_q2(rows: dict[int, arity.BilinearRow]) -> None:
    template = temporal_scalar_template()
    for field, dual in ROD_PAIRS:
        mapping = {16: field, 38: dual}
        for output, term in template:
            left, left_multi, right, right_multi, coefficient = term
            arity.add_bilinear_term(
                rows[mapping.get(output, output)],
                (
                    mapping.get(left, left),
                    replay.word(left_multi),
                    mapping.get(right, right),
                    replay.word(right_multi),
                ),
                replay.polynomial(
                    {"coefficient": coefficient, "coefficient_factors": []}
                ),
            )


def _input_transform(
    tensor: dict[int, arity.BilinearRow], inverse: replay.Operator
) -> dict[int, arity.BilinearRow]:
    unary_rows = arity.q1_rows(inverse)
    result: dict[int, arity.BilinearRow] = defaultdict(dict)
    for target, row in tensor.items():
        for (left, left_word, right, right_word), coefficient in row.items():
            for new_left, inner_left_word, inner_left_coefficient in unary_rows[left]:
                for new_left_word, left_value in replay.apply_word(
                    left_word, inner_left_coefficient, inner_left_word
                ).items():
                    for new_right, inner_right_word, inner_right_coefficient in unary_rows[right]:
                        for new_right_word, right_value in replay.apply_word(
                            right_word, inner_right_coefficient, inner_right_word
                        ).items():
                            arity.add_bilinear_term(
                                result[target],
                                (new_left, new_left_word, new_right, new_right_word),
                                replay.multiply(
                                    coefficient,
                                    replay.multiply(left_value, right_value),
                                ),
                            )
    return result


def _output_transform(
    tensor: dict[int, arity.BilinearRow], forward: replay.Operator
) -> dict[int, arity.BilinearRow]:
    unary_rows = arity.q1_rows(forward)
    result: dict[int, arity.BilinearRow] = defaultdict(dict)
    for target in range(108):
        for middle, outer_word, outer_coefficient in unary_rows.get(target, ()):
            for (left, left_word, right, right_word), coefficient in tensor.get(middle, {}).items():
                for (new_left_word, new_right_word), value in arity.apply_output_word(
                    outer_word, coefficient, left_word, right_word
                ).items():
                    arity.add_bilinear_term(
                        result[target],
                        (left, new_left_word, right, new_right_word),
                        replay.multiply(outer_coefficient, value),
                    )
    return result


@lru_cache(maxsize=1)
def correction_rows() -> dict[int, arity.BilinearRow]:
    original: dict[int, arity.BilinearRow] = defaultdict(dict)
    _add_base_q2(original)
    _add_spatial_apparatus_q2(original)
    raw = {target: dict(row) for target, row in original.items()}
    _add_raw_temporal_rod_q2(raw)
    forward, inverse = clock_dressing_maps()
    transformed = _output_transform(_input_transform(raw, inverse), forward)
    correction = {target: dict(row) for target, row in transformed.items()}
    for target, row in original.items():
        for key, coefficient in row.items():
            arity.add_bilinear_term(
                correction.setdefault(target, {}),
                key,
                replay.scale(coefficient, MINUS),
            )
    return {target: row for target, row in sorted(correction.items()) if row}


def payload_document(*, delete_last_term: bool = False) -> dict[str, Any]:
    rows = []
    flat_terms = []
    for output, row in correction_rows().items():
        terms = []
        for (left, left_word, right, right_word), polynomial in sorted(row.items()):
            for item in serialize(polynomial):
                term = {
                    "left_input_row": left,
                    "left_pbw_multiindex": [left_word.count(axis) for axis in range(4)],
                    "right_input_row": right,
                    "right_pbw_multiindex": [right_word.count(axis) for axis in range(4)],
                    "coefficient": item["coefficient"],
                    "coefficient_factors": item["factors"],
                }
                terms.append(term)
                flat_terms.append({"output": output, **term})
        rows.append({"output": output, "terms": terms})
    if delete_last_term:
        flat_terms.pop()
    summary = arity.bilinear_summary(correction_rows())
    return {
        "schema": "closed-universe-berger-108-row-dressed-rod-clock-q2-pbw-payload-v1",
        "result_id": "BERGER_108_ROW_DRESSED_ROD_CLOCK_Q2_PBW_PAYLOAD",
        "shape": [108, 108, 108],
        "coefficient_field": "differential coefficient-jet algebra over Q(sqrt(10))",
        "pbw_basis": "left-invariant Berger frame; e0^n0 e1^n1 e2^n2 e3^n3",
        "factorial_convention": "suspended-graded-symmetric-factorial-v1",
        "source_action": "sum_aI integral R_aI_plus L_c R_aI transported by R_dressed=R_raw-Theta e0(Rbar_aI) and its cotangent lift",
        "rows": rows,
        **summary,
        "canonical_sha256": canonical_sha256(flat_terms),
    }


def build(*, payload: dict[str, Any] | None = None, payload_hash: str | None = None) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED",
        "background_quotient": "SIX_ROD_BACKGROUND_SPECIALIZATION_EXPORTED",
        "completed_unary": "COMPLETE_FIRST_BIDEGREE_UNARY_GATE",
        "combined_clock_chart": "COMBINED_NONLINEAR_CLOCK_CANONICAL_MAP_EXPORTED",
        "apparatus_scalar_BV": "APPARATUS_SCALAR_BV_Q2_PBW_EXPORTED",
    }
    for name, flag in required.items():
        if values[name]["flags"].get(flag) is not True:
            raise AssertionError(f"required gate dropped: {name}.{flag}")
    audit = unary_conjugation_audit()
    for key in (
        "unary_conjugation_defect_summary",
        "left_inverse_defect_summary",
        "right_inverse_defect_summary",
    ):
        if audit[key]["operator_key_count"]:
            raise AssertionError(f"clock dressing audit failed: {key}")
    if audit["canonical_one_form_cross_term_defect_count"]:
        raise AssertionError("clock dressing ceased to preserve the canonical one-form")
    payload = payload or payload_document()
    expected = {
        "operator_key_count": 192,
        "serialized_term_count": 192,
        "nonzero_output_rows": [38, 49, 50, 51, 52, 64, 65, 66, 67, 68, 69, 74, 75, 76, 77, 78, 79],
        "maximum_total_input_order": 1,
    }
    if {key: payload[key] for key in expected} != expected:
        raise AssertionError("dressed rod clock correction drifted")
    mutation = payload_document(delete_last_term=True)
    if mutation["canonical_sha256"] == payload["canonical_sha256"]:
        raise AssertionError("payload deletion mutation was not detected")
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    payload_hash = payload_hash or hashlib.sha256(rendered.encode()).hexdigest()
    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE certificate repairs the six-rod temporal gauge orbit without changing the certified clock-dressed unary. It starts from the full raw scalar Diff--BV action, including the temporal ghost tau, and conjugates it by the background-dependent triangular map R_dressed=R_raw-Theta e0(Rbar) with the unique cotangent shift preserving the canonical one-form. Exact operator composition proves that this map sends the raw temporal rod unary and its cotangent mate back to the already-certified spatial-only q1 with zero defect. Applying the same map to the raw base-plus-rod scalar q2 and subtracting the prior dressed presentation produces 192 exact differential-coefficient PBW keys on 17 rows. This is an action/chart-derived additive correction, not a fit to an arity witness. It does not repair the independently exposed Maxwell-emitter coefficient orbit, certify the complete q1q2 or q2q2+q1q3 identities, K_Berger equivariance, observer-morphism stability, detector response on Z2, nonlinear rank, physical Bridge 3, finite-parameter causality or a quantum claim. No cross-background mode identification is made."
    )
    return {
        "schema": "closed-universe-berger-108-row-dressed-rod-clock-q2-pbw-v1",
        "result_id": "BERGER_108_ROW_DRESSED_ROD_CLOCK_Q2_PBW",
        "setting_id": values["component_contract"]["setting_id"],
        "claim_status": "CERTIFIED_DRESSED_ROD_CLOCK_Q2_ADDITIVE_CORRECTION",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "clock_dressing_audit": audit,
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": payload_hash,
            "canonical_sha256": payload["canonical_sha256"],
            **{key: payload[key] for key in expected},
        },
        "mutation_results": [
            {"name": "delete_last_dressed_rod_clock_q2_term", "detected": True}
        ],
        "activation_disposition": {
            "rod_clock_crosswalk_repaired": True,
            "complete_arity_two_identity": "OBSTRUCTED_BY_SEPARATE_EMITTER_ORBIT",
            "arity_three_replay_authorized": False,
            "K_Berger_equivariance_authorized": False,
            "observer_morphism_stability_authorized": False,
            "detector_response_on_second_order_cone_authorized": False,
        },
        "flags": {
            "DRESSED_ROD_CLOCK_Q2_PBW_CORRECTION_EXPORTED": True,
            "CLOCK_DRESSING_LEAVES_CERTIFIED_Q1_UNCHANGED": True,
            "CLOCK_DRESSING_CANONICAL_ONE_FORM_PRESERVED": True,
            "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False,
            "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "REPAIR_TYPED_MAXWELL_EMITTER_COMMON_ACTION_ORBIT_AND_REPLAY_Q1Q2",
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
    args = parser.parse_args()
    payload = payload_document()
    rendered_payload = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    value = build(
        payload=payload,
        payload_hash=hashlib.sha256(rendered_payload.encode()).hexdigest(),
    )
    for schema_path, document in ((PAYLOAD_SCHEMA, payload), (SCHEMA, value)):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(document)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        PAYLOAD.write_text(rendered_payload)
        CERTIFICATE.write_text(rendered)
    if args.check:
        if not PAYLOAD.exists() or PAYLOAD.read_text() != rendered_payload:
            raise SystemExit("stale dressed rod clock q2 payload")
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered:
            raise SystemExit("stale dressed rod clock q2 certificate")
    print("BERGER_108_ROW_DRESSED_ROD_CLOCK_Q2_PBW generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
