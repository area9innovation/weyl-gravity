#!/usr/bin/env python3
"""Export the exact signed formal-adjoint lift of the temporal clock chart."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import generator, normalize
from closed_universe_observers.generate_berger_nonlinear_clock_temporal_field_f2_f3 import (
    METRIC_ROW,
    PAIRS,
    THETA_ROW,
    TemporalJetChart,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_NONLINEAR_CLOCK_TEMPORAL_COTANGENT_F2_F3.json"
SCHEMA = P / "schema/berger-nonlinear-clock-temporal-cotangent-f2-f3-v1.schema.json"
REPORT = P / "reports/berger-nonlinear-clock-temporal-cotangent-f2-f3.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "completed_unary": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "radial_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_RADIAL_CANONICAL_MAP_F2_F3.json",
    "temporal_field_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_TEMPORAL_FIELD_F2_F3.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_nonlinear_clock_temporal_cotangent_f2_f3.py",
    P / "tests/test_berger_nonlinear_clock_temporal_cotangent_f2_f3.py",
    SCHEMA,
    REPORT,
]

FIELD_ROWS = tuple(range(5, 15)) + (THETA_ROW,)
DUAL_ROWS = tuple(range(27, 37)) + (38,)
MINUS = (Fraction(-1), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rational_scalar(value: sp.Expr) -> replay.Scalar:
    value = sp.Rational(value)
    return Fraction(int(sp.numer(value)), int(sp.denom(value))), Fraction(0)


def frechet_operator(chart: TemporalJetChart, degree: int) -> replay.Operator:
    """Frechet derivative of the homogeneous degree-`degree` field map."""
    symbol_atoms = {}
    for symbol in chart.symbols:
        atom = chart.atom(symbol)
        local_index = atom["row"] - 5 if atom["row"] <= 14 else 10
        symbol_atoms[symbol] = local_index, tuple(atom["pbw"])
    operator: replay.Operator = {}
    for pair in PAIRS:
        output = METRIC_ROW[pair] - 5
        expression = chart.homogeneous(chart.metric_correction(pair), degree)
        for monomial, coefficient in sp.Poly(expression, *chart.symbols).terms():
            occurrences = [symbol for symbol, power in zip(chart.symbols, monomial, strict=True) for _ in range(power)]
            for position, varied_symbol in enumerate(occurrences):
                input_index, input_pbw = symbol_atoms[varied_symbol]
                factors = []
                for index, other_symbol in enumerate(occurrences):
                    if index == position:
                        continue
                    field_index, field_pbw = symbol_atoms[other_symbol]
                    factors.append(generator("background", f"X_{field_index}", spacetime=field_pbw))
                replay.add_operator_term(
                    operator,
                    (output, input_index, replay.word(input_pbw)),
                    normalize([(rational_scalar(coefficient), factors)]),
                )
    return operator


def formal_adjoint_operator(operator: replay.Operator) -> replay.Operator:
    entries: dict[tuple[int, int], dict[tuple[int, ...], replay.Polynomial]] = defaultdict(dict)
    for (row, column, word), coefficient in operator.items():
        entries[(row, column)][word] = replay.add(entries[(row, column)].get(word, {}), coefficient)
    result: replay.Operator = {}
    for (row, column), entry in entries.items():
        for word, coefficient in replay.formal_adjoint_entry(entry).items():
            replay.add_operator_term(result, (column, row, word), coefficient)
    return result


def pointwise_transpose(operator: replay.Operator) -> replay.Operator:
    result: replay.Operator = {}
    for (row, column, word), coefficient in operator.items():
        replay.add_operator_term(result, (column, row, word), coefficient)
    return result


def drop_sqrt10(operator: replay.Operator) -> replay.Operator:
    result: replay.Operator = {}
    for key, polynomial in operator.items():
        rationalized = normalize(((coefficient[0], Fraction(0)), monomial) for monomial, coefficient in polynomial.items())
        if rationalized:
            replay.add_operator_term(result, key, rationalized)
    return result


def cotangent_operators() -> dict[str, replay.Operator]:
    chart = TemporalJetChart()
    a1 = frechet_operator(chart, 2)
    a2 = frechet_operator(chart, 3)
    b1 = formal_adjoint_operator(a1)
    b2 = formal_adjoint_operator(a2)
    p2 = replay.scale_operator(b1, MINUS)
    p3 = replay.add_operators(replay.compose(b1, b1), replay.scale_operator(b2, MINUS))
    return {"A1": a1, "A2": a2, "B1": b1, "B2": b2, "P2": p2, "P3": p3}


def inverse_and_adjoint_audit(*, pointwise: bool = False, omit_quadratic_inverse: bool = False, drop_structure: bool = False) -> dict[str, Any]:
    chart = TemporalJetChart()
    a1 = frechet_operator(chart, 2)
    a2 = frechet_operator(chart, 3)
    canonical_b1 = formal_adjoint_operator(a1)
    canonical_b2 = formal_adjoint_operator(a2)
    adjoint = pointwise_transpose if pointwise else formal_adjoint_operator
    b1 = adjoint(a1)
    b2 = adjoint(a2)
    p2 = replay.scale_operator(b1, MINUS)
    p3 = replay.scale_operator(b2, MINUS) if omit_quadratic_inverse else replay.add_operators(
        replay.compose(b1, b1), replay.scale_operator(b2, MINUS)
    )
    if drop_structure:
        p3 = drop_sqrt10(p3)
    degree2_defect = replay.add_operators(p2, canonical_b1)
    degree3_defect = replay.add_operators(p3, replay.compose(canonical_b1, p2), canonical_b2)
    a1_involution = replay.add_operators(formal_adjoint_operator(canonical_b1), replay.scale_operator(a1, MINUS))
    a2_involution = replay.add_operators(formal_adjoint_operator(canonical_b2), replay.scale_operator(a2, MINUS))
    sqrt10_terms = sum(coefficient[1] != 0 for polynomial in p3.values() for coefficient in polynomial.values())
    return {
        "field_jacobian_linear_summary": replay.summary(a1),
        "field_jacobian_quadratic_summary": replay.summary(a2),
        "formal_adjoint_linear_summary": replay.summary(b1),
        "formal_adjoint_quadratic_summary": replay.summary(b2),
        "cotangent_F2_operator_summary": replay.summary(p2),
        "cotangent_F3_operator_summary": replay.summary(p3),
        "formal_adjoint_involution_defect": {
            "linear": replay.summary(a1_involution),
            "quadratic": replay.summary(a2_involution),
        },
        "canonical_one_form_inverse_defect": {
            "degree_2": replay.summary(degree2_defect),
            "degree_3": replay.summary(degree3_defect),
        },
        "nonholonomic_sqrt10_term_count": sqrt10_terms,
        "identity": "p=(I+B1+B2)P, P=p-B1 p+(B1^2-B2)p+O(4), Bn=(D C_(n+1))^dagger",
    }


def multiindex(word: tuple[int, ...]) -> list[int]:
    return [word.count(axis) for axis in range(4)]


def serialize_cotangent_operator(operator: replay.Operator, degree: int) -> list[dict[str, Any]]:
    entries = []
    for (output, input_index, input_word), polynomial in sorted(operator.items()):
        for monomial, coefficient in polynomial.items():
            field_inputs = []
            keys = []
            for kind, name, vertical, spacetime in monomial:
                if kind != "background" or vertical or not name.startswith("X_"):
                    raise AssertionError("unexpected cotangent coefficient factor")
                local_index = int(name[2:])
                field_inputs.append({"row": FIELD_ROWS[local_index], "pbw": list(spacetime)})
                keys.append((local_index, spacetime))
            field_inputs.sort(key=lambda item: (item["row"], item["pbw"]))
            multiplicity = math.prod(math.factorial(value) for value in Counter(keys).values())
            scaled = replay.scalar_mul(coefficient, (Fraction(multiplicity), Fraction(0)))
            entries.append({
                "output_row": DUAL_ROWS[output],
                "field_inputs": field_inputs,
                "cotangent_input": {"row": DUAL_ROWS[input_index], "pbw": multiindex(input_word)},
                "coefficient": {
                    "rational": {"numerator": scaled[0].numerator, "denominator": scaled[0].denominator},
                    "sqrt10": {"numerator": scaled[1].numerator, "denominator": scaled[1].denominator},
                },
            })
    entries.sort(key=lambda item: (
        item["output_row"],
        tuple((atom["row"], tuple(atom["pbw"])) for atom in item["field_inputs"]),
        item["cotangent_input"]["row"],
        tuple(item["cotangent_input"]["pbw"]),
        json.dumps(item["coefficient"], sort_keys=True),
    ))
    if any(len(entry["field_inputs"]) != degree - 1 for entry in entries):
        raise AssertionError("cotangent Taylor degree drifted")
    return entries


def deserialize_cotangent_operator(entries: list[dict[str, Any]], degree: int, *, use_full_arity_factorial: bool = False) -> replay.Operator:
    result: replay.Operator = {}
    field_index = {row: index for index, row in enumerate(FIELD_ROWS)}
    dual_index = {row: index for index, row in enumerate(DUAL_ROWS)}
    for entry in entries:
        factors = [
            generator("background", f"X_{field_index[atom['row']]}", spacetime=atom["pbw"])
            for atom in entry["field_inputs"]
        ]
        keys = [(factor[1], factor[3]) for factor in factors]
        denominator = math.factorial(degree) if use_full_arity_factorial else math.prod(
            math.factorial(value) for value in Counter(keys).values()
        )
        coefficient = (
            Fraction(entry["coefficient"]["rational"]["numerator"], entry["coefficient"]["rational"]["denominator"]),
            Fraction(entry["coefficient"]["sqrt10"]["numerator"], entry["coefficient"]["sqrt10"]["denominator"]),
        )
        coefficient = (coefficient[0] / denominator, coefficient[1] / denominator)
        replay.add_operator_term(
            result,
            (
                dual_index[entry["output_row"]],
                dual_index[entry["cotangent_input"]["row"]],
                replay.word(entry["cotangent_input"]["pbw"]),
            ),
            normalize([(coefficient, factors)]),
        )
    return result


def build() -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONCOMMUTING_BERGER_FRAME_PBW_CERTIFIED",
        "completed_unary": "COMPLETE_FIRST_BIDEGREE_UNARY_GATE",
        "radial_chart": "RADIAL_NONLINEAR_CLOCK_COTANGENT_LIFT_CANONICAL",
        "temporal_field_chart": "TEMPORAL_NONLINEAR_CLOCK_FIELD_F2_F3_EXPORTED",
    }
    for name, flag in required.items():
        if dependencies[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency flag dropped: {name}.{flag}")

    operators = cotangent_operators()
    audit = inverse_and_adjoint_audit()
    pointwise = inverse_and_adjoint_audit(pointwise=True)
    omit_square = inverse_and_adjoint_audit(omit_quadratic_inverse=True)
    drop_commutator = inverse_and_adjoint_audit(drop_structure=True)
    f2 = serialize_cotangent_operator(operators["P2"], 2)
    f3 = serialize_cotangent_operator(operators["P3"], 3)
    reconstruction_defects = {
        "F2": replay.summary(replay.add_operators(deserialize_cotangent_operator(f2, 2), replay.scale_operator(operators["P2"], MINUS))),
        "F3": replay.summary(replay.add_operators(deserialize_cotangent_operator(f3, 3), replay.scale_operator(operators["P3"], MINUS))),
    }
    factorial_mutation = {
        "F2": replay.summary(replay.add_operators(deserialize_cotangent_operator(f2, 2, use_full_arity_factorial=True), replay.scale_operator(operators["P2"], MINUS))),
        "F3": replay.summary(replay.add_operators(deserialize_cotangent_operator(f3, 3, use_full_arity_factorial=True), replay.scale_operator(operators["P3"], MINUS))),
    }
    if audit["formal_adjoint_involution_defect"]["linear"]["operator_key_count"]:
        raise AssertionError("linear formal adjoint is not involutive")
    if audit["formal_adjoint_involution_defect"]["quadratic"]["operator_key_count"]:
        raise AssertionError("quadratic formal adjoint is not involutive")
    if audit["canonical_one_form_inverse_defect"]["degree_2"]["operator_key_count"]:
        raise AssertionError("cotangent inverse failed at degree two")
    if audit["canonical_one_form_inverse_defect"]["degree_3"]["operator_key_count"]:
        raise AssertionError("cotangent inverse failed at degree three")
    if len(f2) != 93 or len(f3) != 135 or audit["nonholonomic_sqrt10_term_count"] == 0:
        raise AssertionError("temporal cotangent support changed")
    if any(value["operator_key_count"] for value in reconstruction_defects.values()):
        raise AssertionError("serialized temporal cotangent payload does not reconstruct")
    if not all(value["operator_key_count"] for value in factorial_mutation.values()):
        raise AssertionError("full-arity factorial mutation was not detected")
    if pointwise["canonical_one_form_inverse_defect"]["degree_2"]["operator_key_count"] == 0:
        raise AssertionError("pointwise-transpose mutation was not detected")
    if omit_square["canonical_one_form_inverse_defect"]["degree_3"]["operator_key_count"] == 0:
        raise AssertionError("inverse-square mutation was not detected")
    if drop_commutator["canonical_one_form_inverse_defect"]["degree_3"]["operator_key_count"] == 0:
        raise AssertionError("Berger-structure mutation was not detected")

    payload = {"F2": f2, "F3": f3}
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate closes the signed-pairing BV cotangent half of the temporal "
        "nonlinear Berger clock chart through F3. It differentiates the certified temporal field map into its "
        "linear and quadratic Frechet operators A1 and A2 in the arbitrary-finite noncommuting Berger PBW jet "
        "algebra. Coefficientwise integration by parts gives B1=A1^dagger and B2=A2^dagger; both adjoints are "
        "exactly involutive. Solving the canonical one-form equation gives P=p-B1 p+(B1^2-B2)p through cubic "
        "total degree. The degree-two and degree-three inverse defects vanish as complete sparse PBW operators. "
        "The result serializes 93 F2 and 135 F3 cotangent component entries on rows 27--38 with exact metric/Theta "
        "field jets, differentiated cotangent inputs, multiplicity factorials and Q(sqrt(10)) coefficients. The "
        "nonzero sqrt(10) terms retain the Berger spatial commutators. Replacing the formal adjoint by a pointwise "
        "transpose, omitting B1 squared, or deleting the nonholonomic terms is detected. This certifies the temporal "
        "field-plus-cotangent submap, but it does not yet compose it with the radial chart: mixed radial-temporal "
        "F2/F3 terms and a combined canonical one-form replay remain missing. Therefore scalar apparatus q2/q3 "
        "transport, arity replay, K_Berger equivariance, observer-morphism stability, detector restriction to Z2, "
        "nonlinear rank, physical Bridge 3, finite-parameter causal and quantum claims remain fail-closed. No "
        "compact-product mode is identified with a Berger row."
    )
    return {
        "schema": "closed-universe-berger-nonlinear-clock-temporal-cotangent-f2-f3-v1",
        "result_id": "BERGER_NONLINEAR_CLOCK_TEMPORAL_COTANGENT_F2_F3",
        "setting_id": dependencies["completed_unary"]["setting_id"],
        "claim_status": "CERTIFIED_TEMPORAL_FIELD_AND_BV_COTANGENT_F2_F3_COMBINED_CLOCK_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": dependencies[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "formal_adjoint_and_inverse_audit": audit,
        "taylor_payload": {
            "factorial_convention": "F=F1+F2/2!+F3/3!+...; cotangent entries contain one distinguished dual input and field-input multiplicity factorials",
            "field_rows": list(FIELD_ROWS),
            "cotangent_rows": list(DUAL_ROWS),
            "F2": f2,
            "F3": f3,
            "F2_entry_count": len(f2),
            "F3_entry_count": len(f3),
            "canonical_sha256": canonical_sha256(payload),
            "reconstruction_defects": reconstruction_defects,
        },
        "mutation_results": [
            {"name": "replace_formal_adjoint_by_pointwise_transpose", "detected": pointwise["canonical_one_form_inverse_defect"]["degree_2"]["operator_key_count"] > 0, "defect": pointwise["canonical_one_form_inverse_defect"]["degree_2"]},
            {"name": "omit_B1_squared_from_cubic_inverse", "detected": omit_square["canonical_one_form_inverse_defect"]["degree_3"]["operator_key_count"] > 0, "defect": omit_square["canonical_one_form_inverse_defect"]["degree_3"]},
            {"name": "delete_nonholonomic_sqrt10_terms", "detected": drop_commutator["canonical_one_form_inverse_defect"]["degree_3"]["operator_key_count"] > 0, "defect": drop_commutator["canonical_one_form_inverse_defect"]["degree_3"]},
            {"name": "replace_input_multiplicity_factorials_by_full_arity_factorial", "detected": all(value["operator_key_count"] > 0 for value in factorial_mutation.values()), "defect": factorial_mutation},
        ],
        "activation_disposition": {
            "temporal_field_F2_F3_certified": True,
            "temporal_BV_cotangent_lift_certified": True,
            "combined_radial_temporal_clock_map_certified": False,
            "scalar_q2_q3_transport_authorized": False,
            "detector_response_on_second_order_cone_authorized": False,
            "physical_branch_bridge_activated": False,
        },
        "flags": {
            "TEMPORAL_NONLINEAR_CLOCK_FIELD_F2_F3_EXPORTED": True,
            "TEMPORAL_NONLINEAR_CLOCK_COTANGENT_LIFT_CANONICAL": True,
            "TEMPORAL_FORMAL_ADJOINT_INTEGRATION_BY_PARTS_CERTIFIED": True,
            "NONCOMMUTING_BERGER_PBW_TERMS_RETAINED": True,
            "COMBINED_NONLINEAR_CLOCK_CANONICAL_MAP_EXPORTED": False,
            "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED": False,
            "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "COMPOSE_RADIAL_AND_TEMPORAL_CANONICAL_CHARTS_AND_EXPORT_MIXED_F2_F3",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
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
        raise SystemExit("stale Berger temporal cotangent F2/F3 certificate")
    print("BERGER_NONLINEAR_CLOCK_TEMPORAL_COTANGENT_F2_F3 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
