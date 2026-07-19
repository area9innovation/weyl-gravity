#!/usr/bin/env python3
"""Export the combined radial-temporal Berger clock canonical map through F3."""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.berger_108_row_component_jet_contract import generator, normalize
from closed_universe_observers.generate_berger_nonlinear_clock_temporal_cotangent_f2_f3 import (
    drop_sqrt10,
    formal_adjoint_operator,
    pointwise_transpose,
)
from closed_universe_observers.generate_berger_nonlinear_clock_temporal_field_f2_f3 import (
    ETA,
    METRIC_ROW,
    PAIRS,
    TemporalJetChart,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3.json"
SCHEMA = P / "schema/berger-nonlinear-clock-combined-canonical-map-f2-f3-v1.schema.json"
REPORT = P / "reports/berger-nonlinear-clock-combined-canonical-map-f2-f3.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "completed_unary": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "scalarization_obstruction": P / "certificates/BERGER_108_ROW_APPARATUS_Q2_Q3_SCALARIZATION_OBSTRUCTION.json",
    "radial_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_RADIAL_CANONICAL_MAP_F2_F3.json",
    "temporal_field_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_TEMPORAL_FIELD_F2_F3.json",
    "temporal_cotangent_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_TEMPORAL_COTANGENT_F2_F3.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_nonlinear_clock_combined_canonical_map_f2_f3.py",
    P / "tests/test_berger_nonlinear_clock_combined_canonical_map_f2_f3.py",
    SCHEMA,
    REPORT,
]

FIELD_ROWS = tuple(range(5, 17))
DUAL_ROWS = tuple(range(27, 39))
R_LOCAL = 10
THETA_LOCAL = 11
MINUS = (Fraction(-1), Fraction(0))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class CombinedJetChart:
    """Exact cubic jet of conformal dressing followed by relational time."""

    def __init__(self):
        self.theta_symbols: dict[tuple[int | None, int], sp.Symbol] = {}
        self.radial_symbols: dict[int, sp.Symbol] = {}
        self.metric_symbols: dict[tuple[tuple[int, int], int], sp.Symbol] = {}
        for spatial in (None, 1, 2, 3):
            for n0 in range(4):
                self.theta(spatial, n0)
        for n0 in range(4):
            self.radial(n0)
        for pair in PAIRS:
            for n0 in range(3):
                self.metric(pair, n0)
        self.symbols = tuple(self.theta_symbols.values()) + tuple(self.radial_symbols.values()) + tuple(self.metric_symbols.values())
        theta = self.theta(None, 0)
        theta_0 = self.theta(None, 1)
        theta_00 = self.theta(None, 2)
        self.shift = self.truncate(-theta + theta * theta_0 - theta * theta_0**2 - sp.Rational(1, 2) * theta**2 * theta_00)
        self.u = self.evaluate(tuple(self.theta(None, n0) for n0 in range(1, 4)))
        self.v = {spatial: self.evaluate(tuple(self.theta(spatial, n0) for n0 in range(3))) for spatial in (1, 2, 3)}
        self.r_at_inverse = self.evaluate(tuple(self.radial(n0) for n0 in range(3)))
        self.q = self.truncate(1 - self.u + self.u**2 - self.u**3)
        self.a = {spatial: self.truncate(-self.q * self.v[spatial]) for spatial in (1, 2, 3)}

    def theta(self, spatial: int | None, n0: int) -> sp.Symbol:
        key = spatial, n0
        if key not in self.theta_symbols:
            prefix = "Theta" if spatial is None else f"Theta_{spatial}"
            self.theta_symbols[key] = sp.Symbol(prefix + "_0" * n0)
        return self.theta_symbols[key]

    def radial(self, n0: int) -> sp.Symbol:
        if n0 not in self.radial_symbols:
            self.radial_symbols[n0] = sp.Symbol("R" + "_0" * n0)
        return self.radial_symbols[n0]

    def metric(self, pair: tuple[int, int], n0: int) -> sp.Symbol:
        pair = tuple(sorted(pair))
        key = pair, n0
        if key not in self.metric_symbols:
            self.metric_symbols[key] = sp.Symbol(f"H_{pair[0]}{pair[1]}" + "_0" * n0)
        return self.metric_symbols[key]

    def truncate(self, expression: sp.Expr, maximum_degree: int = 3) -> sp.Expr:
        polynomial = sp.Poly(sp.expand(expression), *self.symbols)
        return sp.Add(*(
            coefficient * sp.prod(symbol**power for symbol, power in zip(self.symbols, monomial, strict=True))
            for monomial, coefficient in polynomial.terms()
            if sum(monomial) <= maximum_degree
        ))

    def homogeneous(self, expression: sp.Expr, degree: int) -> sp.Expr:
        polynomial = sp.Poly(self.truncate(expression), *self.symbols)
        return sp.Add(*(
            coefficient * sp.prod(symbol**power for symbol, power in zip(self.symbols, monomial, strict=True))
            for monomial, coefficient in polynomial.terms()
            if sum(monomial) == degree
        ))

    def evaluate(self, time_jets: tuple[sp.Symbol, sp.Symbol, sp.Symbol]) -> sp.Expr:
        value, first, second = time_jets
        return self.truncate(value + self.shift * first + sp.Rational(1, 2) * self.shift**2 * second)

    def conformal_metric_at_inverse(self, i: int, j: int) -> sp.Expr:
        pair = tuple(sorted((i, j)))
        raw = ETA.get(pair, 0) + self.evaluate(tuple(self.metric(pair, n0) for n0 in range(3))) - 2 * self.r_at_inverse * ETA.get(pair, 0)
        if pair == (0, 0):
            raw -= 2 * self.u
        elif pair[0] == 0:
            raw -= self.v[pair[1]]
        return self.truncate((1 + self.r_at_inverse) ** 2 * raw)

    def pulled_metric(self, i: int, j: int) -> sp.Expr:
        if (i, j) == (0, 0):
            return self.truncate(self.q**2 * self.conformal_metric_at_inverse(0, 0))
        if i == 0:
            return self.truncate(self.q * (self.conformal_metric_at_inverse(0, j) + self.a[j] * self.conformal_metric_at_inverse(0, 0)))
        return self.truncate(
            self.conformal_metric_at_inverse(i, j)
            + self.a[i] * self.conformal_metric_at_inverse(0, j)
            + self.a[j] * self.conformal_metric_at_inverse(i, 0)
            + self.a[i] * self.a[j] * self.conformal_metric_at_inverse(0, 0)
        )

    def corrections(self) -> dict[int, sp.Expr]:
        result = {
            METRIC_ROW[pair] - 5: self.truncate(self.pulled_metric(*pair) - ETA.get(pair, 0) - self.metric(pair, 0))
            for pair in PAIRS
        }
        result[R_LOCAL] = self.truncate(self.r_at_inverse - self.radial(0))
        result[THETA_LOCAL] = sp.Integer(0)
        return result

    def atom(self, symbol: sp.Symbol) -> tuple[int, tuple[int, int, int, int]]:
        for (spatial, n0), candidate in self.theta_symbols.items():
            if symbol == candidate:
                pbw = [n0, 0, 0, 0]
                if spatial is not None:
                    pbw[spatial] = 1
                return THETA_LOCAL, tuple(pbw)
        for n0, candidate in self.radial_symbols.items():
            if symbol == candidate:
                return R_LOCAL, (n0, 0, 0, 0)
        for (pair, n0), candidate in self.metric_symbols.items():
            if symbol == candidate:
                return METRIC_ROW[pair] - 5, (n0, 0, 0, 0)
        raise AssertionError(f"unregistered symbol: {symbol}")


def rational_scalar(value: sp.Expr) -> replay.Scalar:
    value = sp.Rational(value)
    return Fraction(int(sp.numer(value)), int(sp.denom(value))), Fraction(0)


def field_payload(chart: CombinedJetChart) -> dict[str, list[dict[str, Any]]]:
    result = {"F2": [], "F3": []}
    for output, correction in chart.corrections().items():
        for monomial, coefficient in sp.Poly(correction, *chart.symbols).terms():
            degree = sum(monomial)
            if degree not in (2, 3):
                continue
            atoms = []
            keys = []
            for symbol, power in zip(chart.symbols, monomial, strict=True):
                local, pbw = chart.atom(symbol)
                atoms.extend({"row": FIELD_ROWS[local], "pbw": list(pbw)} for _ in range(power))
                keys.extend((local, pbw) for _ in range(power))
            atoms.sort(key=lambda item: (item["row"], item["pbw"]))
            multiplier = math.prod(math.factorial(value) for value in Counter(keys).values())
            result[f"F{degree}"].append({
                "output_row": FIELD_ROWS[output],
                "inputs": atoms,
                "coefficient": str(sp.Rational(coefficient) * multiplier),
            })
    for entries in result.values():
        entries.sort(key=lambda item: (item["output_row"], tuple((atom["row"], tuple(atom["pbw"])) for atom in item["inputs"]), item["coefficient"]))
    return result


def deserialize_field(chart: CombinedJetChart, entries: list[dict[str, Any]], degree: int, *, full_factorial: bool = False) -> dict[int, sp.Expr]:
    reverse = {chart.atom(symbol): symbol for symbol in chart.symbols}
    row_index = {row: index for index, row in enumerate(FIELD_ROWS)}
    result = {index: sp.Integer(0) for index in range(len(FIELD_ROWS))}
    for entry in entries:
        symbols = [reverse[(row_index[atom["row"]], tuple(atom["pbw"]))] for atom in entry["inputs"]]
        keys = [chart.atom(symbol) for symbol in symbols]
        denominator = math.factorial(degree) if full_factorial else math.prod(math.factorial(value) for value in Counter(keys).values())
        result[row_index[entry["output_row"]]] += sp.Rational(entry["coefficient"]) * sp.prod(symbols) / denominator
    return {index: sp.expand(value) for index, value in result.items()}


def frechet_operator(chart: CombinedJetChart, degree: int) -> replay.Operator:
    atoms = {symbol: chart.atom(symbol) for symbol in chart.symbols}
    operator: replay.Operator = {}
    for output, correction in chart.corrections().items():
        expression = chart.homogeneous(correction, degree)
        for monomial, coefficient in sp.Poly(expression, *chart.symbols).terms():
            occurrences = [symbol for symbol, power in zip(chart.symbols, monomial, strict=True) for _ in range(power)]
            for position, varied in enumerate(occurrences):
                input_index, input_pbw = atoms[varied]
                factors = [
                    generator("background", f"X_{atoms[other][0]}", spacetime=atoms[other][1])
                    for index, other in enumerate(occurrences) if index != position
                ]
                replay.add_operator_term(operator, (output, input_index, replay.word(input_pbw)), normalize([(rational_scalar(coefficient), factors)]))
    return operator


def canonical_operators(chart: CombinedJetChart | None = None) -> dict[str, replay.Operator]:
    chart = chart or CombinedJetChart()
    a1 = frechet_operator(chart, 2)
    a2 = frechet_operator(chart, 3)
    b1 = formal_adjoint_operator(a1)
    b2 = formal_adjoint_operator(a2)
    p2 = replay.scale_operator(b1, MINUS)
    p3 = replay.add_operators(replay.compose(b1, b1), replay.scale_operator(b2, MINUS))
    return {"A1": a1, "A2": a2, "B1": b1, "B2": b2, "P2": p2, "P3": p3}


def serialize_cotangent(operator: replay.Operator, degree: int) -> list[dict[str, Any]]:
    entries = []
    for (output, input_index, input_word), polynomial in sorted(operator.items()):
        for monomial, coefficient in polynomial.items():
            fields = []
            keys = []
            for kind, name, vertical, spacetime in monomial:
                if kind != "background" or vertical or not name.startswith("X_"):
                    raise AssertionError("unexpected combined cotangent factor")
                local = int(name[2:])
                fields.append({"row": FIELD_ROWS[local], "pbw": list(spacetime)})
                keys.append((local, spacetime))
            fields.sort(key=lambda item: (item["row"], item["pbw"]))
            multiplier = math.prod(math.factorial(value) for value in Counter(keys).values())
            scaled = replay.scalar_mul(coefficient, (Fraction(multiplier), Fraction(0)))
            entries.append({
                "output_row": DUAL_ROWS[output],
                "field_inputs": fields,
                "cotangent_input": {"row": DUAL_ROWS[input_index], "pbw": [input_word.count(axis) for axis in range(4)]},
                "coefficient": {
                    "rational": {"numerator": scaled[0].numerator, "denominator": scaled[0].denominator},
                    "sqrt10": {"numerator": scaled[1].numerator, "denominator": scaled[1].denominator},
                },
            })
    entries.sort(key=lambda item: (item["output_row"], tuple((atom["row"], tuple(atom["pbw"])) for atom in item["field_inputs"]), item["cotangent_input"]["row"], tuple(item["cotangent_input"]["pbw"]), json.dumps(item["coefficient"], sort_keys=True)))
    if any(len(entry["field_inputs"]) != degree - 1 for entry in entries):
        raise AssertionError("combined cotangent degree drifted")
    return entries


def deserialize_cotangent(entries: list[dict[str, Any]], degree: int, *, full_factorial: bool = False) -> replay.Operator:
    field_index = {row: index for index, row in enumerate(FIELD_ROWS)}
    dual_index = {row: index for index, row in enumerate(DUAL_ROWS)}
    result: replay.Operator = {}
    for entry in entries:
        factors = [generator("background", f"X_{field_index[atom['row']]}", spacetime=atom["pbw"]) for atom in entry["field_inputs"]]
        keys = [(factor[1], factor[3]) for factor in factors]
        denominator = math.factorial(degree) if full_factorial else math.prod(math.factorial(value) for value in Counter(keys).values())
        coefficient = (
            Fraction(entry["coefficient"]["rational"]["numerator"], entry["coefficient"]["rational"]["denominator"]) / denominator,
            Fraction(entry["coefficient"]["sqrt10"]["numerator"], entry["coefficient"]["sqrt10"]["denominator"]) / denominator,
        )
        replay.add_operator_term(result, (dual_index[entry["output_row"]], dual_index[entry["cotangent_input"]["row"]], replay.word(entry["cotangent_input"]["pbw"])), normalize([(coefficient, factors)]))
    return result


def restriction_audit(chart: CombinedJetChart) -> dict[str, Any]:
    corrections = chart.corrections()
    theta_zero = {symbol: 0 for symbol in chart.theta_symbols.values()}
    radial_zero = {symbol: 0 for symbol in chart.radial_symbols.values()}
    radial_defects = {}
    for pair in PAIRS:
        h = chart.metric(pair, 0)
        r = chart.radial(0)
        eta = ETA.get(pair, 0)
        expected = 2 * r * h - 3 * r**2 * eta + r**2 * h - 2 * r**3 * eta
        radial_defects[f"{pair[0]}{pair[1]}"] = sp.expand(corrections[METRIC_ROW[pair] - 5].subs(theta_zero) - expected)
    radial_defects["R"] = sp.expand(corrections[R_LOCAL].subs(theta_zero))

    temporal = TemporalJetChart()
    temporal_defects = {}
    for pair in PAIRS:
        expected = temporal.metric_correction(pair)
        temporal_defects[f"{pair[0]}{pair[1]}"] = sp.expand(corrections[METRIC_ROW[pair] - 5].subs(radial_zero) - expected)
    temporal_defects["R"] = sp.expand(corrections[R_LOCAL].subs(radial_zero))

    mixed_counts = {2: 0, 3: 0}
    radial_set = set(chart.radial_symbols.values())
    theta_set = set(chart.theta_symbols.values())
    for correction in corrections.values():
        for monomial, _coefficient in sp.Poly(correction, *chart.symbols).terms():
            degree = sum(monomial)
            active = {symbol for symbol, power in zip(chart.symbols, monomial, strict=True) if power}
            if degree in mixed_counts and active & radial_set and active & theta_set:
                mixed_counts[degree] += 1
    return {
        "radial_restriction_defect_count": sum(value != 0 for value in radial_defects.values()),
        "temporal_restriction_defect_count": sum(value != 0 for value in temporal_defects.values()),
        "mixed_radial_temporal_monomial_counts": {"degree_2": mixed_counts[2], "degree_3": mixed_counts[3]},
        "deleted_mixed_term_count": mixed_counts[2] + mixed_counts[3],
    }


def canonical_audit(*, pointwise: bool = False, omit_square: bool = False, drop_structure: bool = False) -> dict[str, Any]:
    chart = CombinedJetChart()
    a1 = frechet_operator(chart, 2)
    a2 = frechet_operator(chart, 3)
    canonical_b1 = formal_adjoint_operator(a1)
    canonical_b2 = formal_adjoint_operator(a2)
    adjoint = pointwise_transpose if pointwise else formal_adjoint_operator
    b1 = adjoint(a1)
    b2 = adjoint(a2)
    p2 = replay.scale_operator(b1, MINUS)
    p3 = replay.scale_operator(b2, MINUS) if omit_square else replay.add_operators(replay.compose(b1, b1), replay.scale_operator(b2, MINUS))
    if drop_structure:
        p3 = drop_sqrt10(p3)
    degree2 = replay.add_operators(p2, canonical_b1)
    degree3 = replay.add_operators(p3, replay.compose(canonical_b1, p2), canonical_b2)
    involution1 = replay.add_operators(formal_adjoint_operator(canonical_b1), replay.scale_operator(a1, MINUS))
    involution2 = replay.add_operators(formal_adjoint_operator(canonical_b2), replay.scale_operator(a2, MINUS))
    return {
        "A1": replay.summary(a1), "A2": replay.summary(a2), "B1": replay.summary(canonical_b1), "B2": replay.summary(canonical_b2),
        "P2": replay.summary(p2), "P3": replay.summary(p3),
        "adjoint_involution_defects": {"linear": replay.summary(involution1), "quadratic": replay.summary(involution2)},
        "canonical_inverse_defects": {"degree_2": replay.summary(degree2), "degree_3": replay.summary(degree3)},
        "sqrt10_term_count": sum(coefficient[1] != 0 for polynomial in p3.values() for coefficient in polynomial.values()),
    }


@lru_cache(maxsize=1)
def build() -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "NONCOMMUTING_BERGER_FRAME_PBW_CERTIFIED",
        "completed_unary": "COMPLETE_FIRST_BIDEGREE_UNARY_GATE",
        "scalarization_obstruction": "NONLINEAR_CLOCK_COORDINATE_JET_NONUNIQUENESS_CERTIFIED",
        "radial_chart": "RADIAL_NONLINEAR_CLOCK_COTANGENT_LIFT_CANONICAL",
        "temporal_field_chart": "TEMPORAL_NONLINEAR_CLOCK_FIELD_F2_F3_EXPORTED",
        "temporal_cotangent_chart": "TEMPORAL_NONLINEAR_CLOCK_COTANGENT_LIFT_CANONICAL",
    }
    for name, flag in required.items():
        if dependencies[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency flag dropped: {name}.{flag}")

    chart = CombinedJetChart()
    fields = field_payload(chart)
    reconstructed_fields = {
        degree: deserialize_field(chart, fields[f"F{degree}"], degree)
        for degree in (2, 3)
    }
    factorial_field_mutation = {
        degree: deserialize_field(chart, fields[f"F{degree}"], degree, full_factorial=True)
        for degree in (2, 3)
    }
    operators = canonical_operators(chart)
    cotangent_f2 = serialize_cotangent(operators["P2"], 2)
    cotangent_f3 = serialize_cotangent(operators["P3"], 3)
    restriction = restriction_audit(chart)
    audit = canonical_audit()
    pointwise = canonical_audit(pointwise=True)
    omit_square = canonical_audit(omit_square=True)
    drop_structure = canonical_audit(drop_structure=True)
    recon2 = replay.add_operators(deserialize_cotangent(cotangent_f2, 2), replay.scale_operator(operators["P2"], MINUS))
    recon3 = replay.add_operators(deserialize_cotangent(cotangent_f3, 3), replay.scale_operator(operators["P3"], MINUS))
    factorial2 = replay.add_operators(deserialize_cotangent(cotangent_f2, 2, full_factorial=True), replay.scale_operator(operators["P2"], MINUS))
    factorial3 = replay.add_operators(deserialize_cotangent(cotangent_f3, 3, full_factorial=True), replay.scale_operator(operators["P3"], MINUS))

    field_counts = {"F2": len(fields["F2"]), "F3": len(fields["F3"])}
    cotangent_counts = {"F2": len(cotangent_f2), "F3": len(cotangent_f3)}
    if field_counts != {"F2": 55, "F3": 174}:
        raise AssertionError(f"combined field support changed: {field_counts}")
    field_reconstruction_defects = {
        f"F{degree}": sum(
            sp.expand(reconstructed_fields[degree][output] - chart.homogeneous(correction, degree)) != 0
            for output, correction in chart.corrections().items()
        )
        for degree in (2, 3)
    }
    factorial_field_defects = {
        f"F{degree}": sum(
            sp.expand(factorial_field_mutation[degree][output] - chart.homogeneous(correction, degree)) != 0
            for output, correction in chart.corrections().items()
        )
        for degree in (2, 3)
    }
    if any(field_reconstruction_defects.values()):
        raise AssertionError(f"combined field serialization failed: {field_reconstruction_defects}")
    if not all(factorial_field_defects.values()):
        raise AssertionError("combined field factorial mutation was not detected")
    if restriction != {"radial_restriction_defect_count": 0, "temporal_restriction_defect_count": 0, "mixed_radial_temporal_monomial_counts": {"degree_2": 5, "degree_3": 64}, "deleted_mixed_term_count": 69}:
        raise AssertionError(f"combined restriction audit changed: {restriction}")
    if any(audit["adjoint_involution_defects"][name]["operator_key_count"] for name in ("linear", "quadratic")):
        raise AssertionError("combined formal adjoint is not involutive")
    if any(audit["canonical_inverse_defects"][name]["operator_key_count"] for name in ("degree_2", "degree_3")):
        raise AssertionError("combined canonical inverse failed")
    if replay.summary(recon2)["operator_key_count"] or replay.summary(recon3)["operator_key_count"]:
        raise AssertionError("combined cotangent serialization failed")
    if not replay.summary(factorial2)["operator_key_count"] or not replay.summary(factorial3)["operator_key_count"]:
        raise AssertionError("combined factorial mutation was not detected")
    if not pointwise["canonical_inverse_defects"]["degree_2"]["operator_key_count"] or not omit_square["canonical_inverse_defects"]["degree_3"]["operator_key_count"] or not drop_structure["canonical_inverse_defects"]["degree_3"]["operator_key_count"]:
        raise AssertionError("combined canonical mutation was not detected")

    payload = {"field_F2": fields["F2"], "field_F3": fields["F3"], "cotangent_F2": cotangent_f2, "cotangent_F3": cotangent_f3}
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate closes the action-normalized same-background nonlinear Berger "
        "clock canonical map through F3. The single geometric definition first forms (1+R(x))^2 times the linearly "
        "dressed raw metric eta+H-2R eta-B(Theta), then pulls it to y0=x0+Theta(x), yi=xi by the exact inverse "
        "Jacobian; R is pulled back as a scalar. The complete field chart has zero linear defect, 55 F2 and 174 F3 "
        "component monomials. Its Theta=0 restriction reproduces the certified radial chart exactly and its R=0 "
        "restriction reproduces the certified temporal chart exactly. Five quadratic and 64 cubic mixed radial-"
        "temporal monomials show why juxtaposing the two submaps is insufficient. The signed BV cotangent lift is "
        "derived from the formal adjoints of the complete Frechet operators in the noncommuting Berger PBW algebra. "
        "Both adjoints are involutive and P=p-B1 p+(B1^2-B2)p has zero degree-two and degree-three canonical one-form "
        "inverse defects. Every field and cotangent Taylor component is serialized with exact multiplicity factorials, "
        "differentiated inputs and Q(sqrt(10)) coefficients. Pointwise transposition, omission of B1 squared, deletion "
        "of nonholonomic terms, wrong factorials and deletion of all 69 mixed terms are detected. This removes the "
        "coordinate-map nonuniqueness diagnosed by the scalarization obstruction and authorizes regeneration of the "
        "scalar 108-row apparatus/emitter q2 and q3 payloads. It does not itself export those interactions, replay the "
        "q1q2 or q2q2+q1q3 identities, prove K_Berger equivariance or observer-morphism stability, restrict detector "
        "response to Z2, promote nonlinear rank, activate physical Bridge 3, establish finite-parameter causality, or "
        "make a quantum claim. No compact-product mode is identified with a Berger row."
    )
    return {
        "schema": "closed-universe-berger-nonlinear-clock-combined-canonical-map-f2-f3-v1",
        "result_id": "BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3",
        "setting_id": dependencies["completed_unary"]["setting_id"],
        "claim_status": "CERTIFIED_COMBINED_RADIAL_TEMPORAL_CANONICAL_MAP_F2_F3",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": dependencies[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "geometric_definition": {"clock_map": "y0=x0+Theta(x), yi=xi", "metric_map": "gHat(y)=K^T (1+R(x(y)))^2 [eta+H-2R eta-B(Theta)](x(y)) K", "radial_map": "R_true(y)=R(x(y))", "restriction_audit": restriction},
        "field_payload": {"F2": fields["F2"], "F3": fields["F3"], "F2_entry_count": field_counts["F2"], "F3_entry_count": field_counts["F3"], "reconstruction_defect_counts": field_reconstruction_defects},
        "canonical_audit": audit,
        "cotangent_payload": {"F2": cotangent_f2, "F3": cotangent_f3, "F2_entry_count": cotangent_counts["F2"], "F3_entry_count": cotangent_counts["F3"], "reconstruction_defects": {"F2": replay.summary(recon2), "F3": replay.summary(recon3)}},
        "payload_canonical_sha256": canonical_sha256(payload),
        "mutation_results": [
            {"name": "delete_all_mixed_radial_temporal_terms", "detected": restriction["deleted_mixed_term_count"] > 0, "deleted_term_count": restriction["deleted_mixed_term_count"]},
            {"name": "replace_formal_adjoint_by_pointwise_transpose", "detected": pointwise["canonical_inverse_defects"]["degree_2"]["operator_key_count"] > 0, "defect": pointwise["canonical_inverse_defects"]["degree_2"]},
            {"name": "omit_B1_squared_from_cubic_inverse", "detected": omit_square["canonical_inverse_defects"]["degree_3"]["operator_key_count"] > 0, "defect": omit_square["canonical_inverse_defects"]["degree_3"]},
            {"name": "delete_nonholonomic_sqrt10_terms", "detected": drop_structure["canonical_inverse_defects"]["degree_3"]["operator_key_count"] > 0, "defect": drop_structure["canonical_inverse_defects"]["degree_3"]},
            {"name": "replace_input_multiplicity_factorials_by_full_arity_factorial", "detected": replay.summary(factorial2)["operator_key_count"] > 0 and replay.summary(factorial3)["operator_key_count"] > 0 and all(factorial_field_defects.values()), "field_defect_counts": factorial_field_defects},
        ],
        "activation_disposition": {"combined_clock_canonical_map_certified": True, "scalar_q2_q3_transport_authorized": True, "scalar_q2_q3_payload_exported": False, "arity_replay_certified": False, "K_Berger_equivariance_certified": False, "observer_morphism_stability_certified": False, "detector_response_on_second_order_cone_authorized": False, "physical_branch_bridge_activated": False},
        "flags": {"COMBINED_NONLINEAR_CLOCK_CANONICAL_MAP_EXPORTED": True, "MIXED_RADIAL_TEMPORAL_F2_F3_EXPORTED": True, "COMBINED_CANONICAL_ONE_FORM_CERTIFIED": True, "RADIAL_AND_TEMPORAL_RESTRICTIONS_REPRODUCED": True, "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED": True, "SCALAR_APPARATUS_Q2_Q3_PAYLOAD_EXPORTED": False, "COMPONENT_ARITY_IDENTITIES_CERTIFIED": False, "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False, "QUANTUM_CLAIM": False},
        "next_gate": "REGENERATE_SCALAR_108_ROW_APPARATUS_AND_EMITTER_Q2_Q3_AND_REPLAY_ARITY_IDENTITIES",
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
        raise SystemExit("stale combined nonlinear clock canonical map certificate")
    print("BERGER_NONLINEAR_CLOCK_COMBINED_CANONICAL_MAP_F2_F3 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
