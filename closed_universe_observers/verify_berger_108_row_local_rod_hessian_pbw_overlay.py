#!/usr/bin/env python3
"""Independently verify the scalar local Berger rod Hessian overlay."""

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.berger_108_row_component_jet_contract import (
    add,
    derivative,
    generator,
    normalize,
    scale,
    serialize,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY.json"
SCHEMA = P / "schema/berger-108-row-local-rod-hessian-pbw-overlay-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-108-row-local-rod-hessian-pbw-overlay-payload-v1.schema.json"
ETA = (-1, 1, 1, 1)
METRIC_COMPONENTS = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))
RODS = ("R0_1", "R0_2", "R0_3", "R1_1", "R1_2", "R1_3")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def scalar(value):
    def q(item):
        return Fraction(item["numerator"], item["denominator"])
    return q(value["rational"]), q(value["sqrt10"])


def polynomial(term):
    factors = tuple(
        generator(factor["kind"], factor["name"], factor["vertical_multiindex"], factor["spacetime_multiindex"])
        for factor in term["coefficient_factors"]
    )
    return normalize([(scalar(term["coefficient"]), factors)])


def operator(block):
    value = {}
    for entry in block["entries"]:
        for term in entry["terms"]:
            word = tuple(axis for axis, power in enumerate(term["input_pbw_multiindex"]) for _ in range(power))
            key = entry["output_row"], entry["input_row"], word
            value[key] = add(value.get(key, {}), polynomial(term))
    return value


def signature(value):
    rows = []
    for key, coefficient in sorted(value.items()):
        for term in serialize(coefficient):
            rows.append((key, json.dumps(term, sort_keys=True, separators=(",", ":"))))
    return Counter(rows)


def transpose_mixed(value):
    output = {}
    for (row, column, word), coefficient in value.items():
        key_base = 27 + column - 5, 64 + row - 74
        pieces = [((), coefficient)] if not word else [
            (word, scale(coefficient, (Fraction(-1), Fraction(0)))),
            ((), scale(derivative(coefficient, word[0]), (Fraction(-1), Fraction(0)))),
        ]
        for target_word, target_coefficient in pieces:
            key = key_base + (target_word,)
            output[key] = add(output.get(key, {}), target_coefficient)
    return output


def component_matrix(component):
    first, second = METRIC_COMPONENTS[component]
    value = sp.zeros(4)
    value[first, second] = value[second, first] = 1
    return value


def evaluate_polynomial(value, gradients):
    total = sp.S.Zero
    for monomial, coefficient in value.items():
        number = sp.Rational(coefficient[0].numerator, coefficient[0].denominator)
        number += sp.sqrt(10) * sp.Rational(coefficient[1].numerator, coefficient[1].denominator)
        for kind, name, _vertical, spacetime in monomial:
            if kind == "parameter":
                factor = 1
            else:
                assert sum(spacetime) == 1
                factor = gradients[name][spacetime.index(1)]
            number *= factor
        total += number
    return sp.simplify(total)


def evaluate_jet_polynomial(value, jets):
    total = sp.S.Zero
    for monomial, coefficient in value.items():
        number = sp.Rational(coefficient[0].numerator, coefficient[0].denominator)
        number += sp.sqrt(10) * sp.Rational(coefficient[1].numerator, coefficient[1].denominator)
        for kind, name, _vertical, spacetime in monomial:
            if kind == "parameter":
                factor = 1
            else:
                assert name == RODS[0]
                factor = jets[spacetime]
            number *= factor
        total += number
    return sp.expand(total)


def direct_mixed_wave_fixture(component, component_value, component_derivatives, first_jets, pbw_jets):
    """Differentiate the scalar wave operator from the general Koszul formula."""
    t = sp.symbols("t")
    eta = sp.diag(-1, 1, 1, 1)
    basis = component_matrix(component)
    h = component_value * basis
    dh = [component_derivatives[axis] * basis for axis in range(4)]
    g = eta + t * h
    inverse = g.inv()
    s10 = sp.sqrt(10)
    structure = {
        (1, 2, 3): 3 * s10 / 20,
        (2, 1, 3): -3 * s10 / 20,
        (2, 3, 1): 2 * s10 / 3,
        (3, 2, 1): -2 * s10 / 3,
        (3, 1, 2): 2 * s10 / 3,
        (1, 3, 2): -2 * s10 / 3,
    }
    connection = {}
    for first in range(4):
        for second in range(4):
            lowered = []
            for target in range(4):
                item = t * (dh[first][second, target] + dh[second][first, target] - dh[target][first, second])
                for output in range(4):
                    item -= g[first, output] * structure.get((second, target, output), 0)
                    item += g[second, output] * structure.get((target, first, output), 0)
                    item += g[target, output] * structure.get((first, second, output), 0)
                lowered.append(item / 2)
            for output in range(4):
                connection[output, first, second] = sum(inverse[output, target] * lowered[target] for target in range(4))
    box = sp.S.Zero
    for first in range(4):
        for second in range(4):
            multiindex = tuple(int(axis == first) + int(axis == second) for axis in range(4))
            raw_second = sp.Integer(pbw_jets[multiindex])
            if first > second:
                raw_second += sum(structure.get((first, second, target), 0) * first_jets[target] for target in range(4))
            covariant_second = raw_second - sum(connection[target, first, second] * first_jets[target] for target in range(4))
            box += inverse[first, second] * covariant_second
    return sp.simplify(sp.diff(box, t).subs(t, 0))


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in value["dependency_refs"].values():
        assert sha256(ROOT / ref["path"]) == ref["sha256"]
    ref = value["payload_ref"]
    payload_path = ROOT / ref["path"]
    assert sha256(payload_path) == ref["sha256"]
    payload = json.loads(payload_path.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)
    assert canonical_sha256(payload["blocks"]) == payload["blocks_canonical_sha256"] == ref["blocks_canonical_sha256"]
    blocks = {block["id"]: block for block in payload["blocks"]}

    expected_connection = {
        (3, 1, 2): (Fraction(0), Fraction(3, 40)),
        (2, 1, 3): (Fraction(0), Fraction(-3, 40)),
        (3, 2, 1): (Fraction(0), Fraction(-3, 40)),
        (1, 2, 3): (Fraction(0), Fraction(3, 40)),
        (2, 3, 1): (Fraction(0), Fraction(71, 120)),
        (1, 3, 2): (Fraction(0), Fraction(-71, 120)),
    }
    actual_connection = {
        (entry["target"], entry["first"], entry["second"]): scalar(entry["coefficient"])
        for entry in value["connection_audit"]["entries"]
    }
    assert actual_connection == expected_connection
    assert value["connection_audit"]["torsion_defect_count"] == 0
    assert value["connection_audit"]["metric_compatibility_defect_count"] == 0

    gamma = operator(blocks["Gamma_R"])
    gamma_sharp = operator(blocks["Gamma_R_sharp"])
    expected_sharp = {
        (49 + column, 74 + row - 64, ()): scale(coefficient, (Fraction(-1), Fraction(0)))
        for (row, column, word), coefficient in gamma.items()
        if not word
    }
    assert signature(gamma_sharp) == signature(expected_sharp)
    mixed = operator(blocks["K_Rh"])
    assert signature(operator(blocks["K_hR"])) == signature(transpose_mixed(mixed))

    # Reconstruct the mixed block from the general nonholonomic Koszul formula,
    # including nonzero metric first jets and PBW-reduced scalar second jets.
    first_jets = (2, -1, 3, 4)
    pbw_jets = {
        (2, 0, 0, 0): 5,
        (1, 1, 0, 0): -2,
        (1, 0, 1, 0): 7,
        (1, 0, 0, 1): 1,
        (0, 2, 0, 0): -4,
        (0, 1, 1, 0): 6,
        (0, 1, 0, 1): -3,
        (0, 0, 2, 0): 8,
        (0, 0, 1, 1): 2,
        (0, 0, 0, 2): -5,
    }
    jets = {(0, 0, 0, 0): 11}
    jets.update({tuple(int(axis == target) for axis in range(4)): first_jets[target] for target in range(4)})
    jets.update(pbw_jets)
    for component in range(10):
        component_value = component + 2
        component_derivatives = tuple((component + 1) * (axis + 2) - 5 for axis in range(4))
        actual = sp.S.Zero
        for (row, column, word), coefficient in mixed.items():
            if row == 74 and column == 5 + component:
                input_value = component_value if not word else component_derivatives[word[0]]
                actual += evaluate_jet_polynomial(coefficient, jets) * input_value
        direct = direct_mixed_wave_fixture(component, component_value, component_derivatives, first_jets, pbw_jets)
        assert sp.simplify(actual - direct) == 0

    wave = operator(blocks["K_RR"])
    for rod in range(6):
        words = {word: coefficient for (row, column, word), coefficient in wave.items() if row == 74 + rod and column == 64 + rod}
        assert set(words) == {(0, 0), (1, 1), (2, 2), (3, 3)}
        assert next(iter(words[(0, 0)].values())) == (Fraction(-1), Fraction(0))

    metric = operator(blocks["Delta_K_hh_rod"])
    for left in range(10):
        for right in range(10):
            assert metric.get((27 + left, 5 + right, ()), {}) == metric.get((27 + right, 5 + left, ()), {})

    # Evaluate all 100 payload coefficients and compare with direct second
    # variations of the scalar density for six independent exact gradients.
    gradients = {name: tuple(Fraction((rod + 1) * (axis + 1) - 3) for axis in range(4)) for rod, name in enumerate(RODS)}
    a, b = sp.symbols("a b")
    eta = sp.diag(-1, 1, 1, 1)
    for output_component in range(10):
        k = component_matrix(output_component)
        for input_component in range(10):
            h = component_matrix(input_component)
            direct = sp.S.Zero
            for name in RODS:
                vector = sp.Matrix(gradients[name])
                g = eta + a * h + b * k
                density = -sp.sqrt(-g.det()) * (vector.T * g.inv() * vector)[0] / 2
                direct += sp.diff(density, a, b).subs({a: 0, b: 0})
            actual = evaluate_polynomial(
                metric.get((27 + output_component, 5 + input_component, ()), {}),
                gradients,
            )
            assert sp.simplify(actual - direct) == 0

    assert not value["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
    print("BERGER_108_ROW_LOCAL_ROD_HESSIAN_PBW_OVERLAY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
