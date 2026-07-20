#!/usr/bin/env python3
"""Independent audit of the replacement-112 mixed rod Hessian export."""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE.json"
X = P / "certificates/BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement112-mixed-metric-rod-hessian-interface-v1.schema.json"
PAYLOAD_SCHEMA = P / "schema/berger-replacement112-mixed-metric-rod-hessian-interface-payload-v1.schema.json"
FIELDS = (64, 65, 66, 67, 68, 69, 108, 109)
COTANGENTS = (74, 75, 76, 77, 78, 79, 110, 111)
SA, CA, SU, CU = sp.symbols("sa ca su cu", nonzero=True, real=True)
SYMBOLS = {"sa": SA, "ca": CA, "su": SU, "cu": CU}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def ideal() -> sp.GroebnerBasis:
    return sp.groebner([CA**2 + SA**2 - 1, CU**2 + SU**2 - 1], CA, CU, SA, SU, order="lex", extension=sp.sqrt(10))


def expression(text: str) -> sp.Expr:
    return sp.sympify(text, locals=SYMBOLS)


def reduced(value: sp.Expr) -> sp.Expr:
    numerator, denominator = sp.cancel(value).as_numer_denom()
    return sp.factor(ideal().reduce(sp.expand(numerator))[1] / ideal().reduce(sp.expand(denominator))[1])


def factor_key(factors: list[dict[str, Any]]) -> str:
    ordered = sorted(factors, key=lambda x: (x["kind"], x["name"], tuple(x["vertical_multiindex"]), tuple(x["spacetime_multiindex"])))
    return json.dumps(ordered, sort_keys=True, separators=(",", ":"))


@lru_cache(maxsize=None)
def pbw(word: tuple[int, ...]) -> dict[tuple[int, int, int, int], sp.Expr]:
    inversion = next((index for index in range(len(word) - 1) if word[index] > word[index + 1]), None)
    if inversion is None:
        return {tuple(word.count(axis) for axis in range(4)): sp.S.One}
    left, right = word[inversion], word[inversion + 1]
    swapped = word[:inversion] + (right, left) + word[inversion + 2:]
    output = defaultdict(lambda: sp.S.Zero, pbw(swapped))
    structure = {
        (1, 2): (3, sp.Rational(3, 20) * sp.sqrt(10)),
        (2, 1): (3, -sp.Rational(3, 20) * sp.sqrt(10)),
        (2, 3): (1, sp.Rational(2, 3) * sp.sqrt(10)),
        (3, 2): (1, -sp.Rational(2, 3) * sp.sqrt(10)),
        (3, 1): (2, sp.Rational(2, 3) * sp.sqrt(10)),
        (1, 3): (2, -sp.Rational(2, 3) * sp.sqrt(10)),
    }
    if (left, right) in structure:
        target, bracket = structure[left, right]
        shorter = word[:inversion] + (target,) + word[inversion + 2:]
        for multiindex, coefficient in pbw(shorter).items():
            output[multiindex] += bracket * coefficient
    return {multiindex: sp.expand(coefficient) for multiindex, coefficient in output.items() if coefficient != 0}


def terms(block: dict[str, Any]) -> dict[tuple[int, int, tuple[int, ...], str], sp.Expr]:
    result: dict[tuple[int, int, tuple[int, ...], str], sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for entry in block["entries"]:
        for term in entry["terms"]:
            key = (entry["output_row"], entry["input_row"], tuple(term["input_pbw_multiindex"]), factor_key(term["coefficient_factors"]))
            result[key] += expression(term["coefficient"])
    return {key: reduced(value) for key, value in result.items() if reduced(value) != 0}


def transpose_expected(block: dict[str, Any]) -> dict[tuple[int, int, tuple[int, ...], str], sp.Expr]:
    result: dict[tuple[int, int, tuple[int, ...], str], sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for entry in block["entries"]:
        rod_slot = COTANGENTS.index(entry["output_row"])
        for term in entry["terms"]:
            word = tuple(term["input_pbw_multiindex"])
            coefficient = expression(term["coefficient"])
            factors = term["coefficient_factors"]
            target = 27 + entry["input_row"] - 5
            if sum(word) == 0:
                result[target, FIELDS[rod_slot], word, factor_key(factors)] += coefficient
                continue
            if sum(word) != 1:
                raise AssertionError("mixed operator is not first order")
            axis = word.index(1)
            result[target, FIELDS[rod_slot], word, factor_key(factors)] -= coefficient
            for index, item in enumerate(factors):
                if item["kind"] == "parameter":
                    continue
                existing_word = tuple(direction for direction, count in enumerate(item["spacetime_multiindex"]) for _ in range(count))
                for multiindex, pbw_coefficient in pbw((axis,) + existing_word).items():
                    differentiated = json.loads(json.dumps(factors))
                    differentiated[index]["spacetime_multiindex"] = list(multiindex)
                    result[target, FIELDS[rod_slot], (0, 0, 0, 0), factor_key(differentiated)] -= coefficient * pbw_coefficient
    return {key: reduced(value) for key, value in result.items() if reduced(value) != 0}


def assert_equal_maps(left: dict[Any, sp.Expr], right: dict[Any, sp.Expr]) -> None:
    keys = set(left) | set(right)
    defects = [key for key in keys if reduced(left.get(key, 0) - right.get(key, 0)) != 0]
    if defects:
        raise AssertionError(f"operator maps differ at {defects[0]!r}; total defects={len(defects)}")


def verify() -> None:
    certificate = json.loads(C.read_text())
    payload = json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if sha(X) != certificate["payload_ref"]["sha256"]:
        raise AssertionError("payload hash mismatch")
    for ref in certificate["dependency_refs"].values():
        if sha(ROOT / ref["path"]) != ref["sha256"]:
            raise AssertionError(f"dependency drift: {ref['path']}")

    action = json.loads((ROOT / certificate["dependency_refs"]["positive_action_payload"]["path"]).read_text())
    B = sp.Matrix([[expression(value) for value in row] for row in action["mixed_action"]["background_orbit_matrix_B"]])
    H = (B.inv().T * B.inv()).applyfunc(sp.factor)
    exported_H = sp.Matrix([[expression(value) for value in row] for row in payload["action_crosswalk"]["kinetic_matrix_H"]])
    if any(reduced(value) != 0 for value in H - exported_H):
        raise AssertionError("exported kinetic matrix is not B^-T B^-1")

    for part in ("eight_rod_addition", "six_rod_subtraction", "net_replacement_delta"):
        assert_equal_maps(transpose_expected(payload["operator_blocks"]["K_Rh"][part]), terms(payload["operator_blocks"]["K_hR"][part]))

    for part in ("eight_rod_addition", "six_rod_subtraction", "net_replacement_delta"):
        metric = terms(payload["operator_blocks"]["Delta_K_hh_rod"][part])
        swapped = {(27 + column - 5, 5 + row - 27, word, factors): value for (row, column, word, factors), value in metric.items()}
        assert_equal_maps(metric, swapped)

    gamma = terms(payload["operator_blocks"]["Gamma_R"]["eight_rod_addition"])
    gamma_sharp = terms(payload["operator_blocks"]["Gamma_R_sharp"]["eight_rod_addition"])
    expected_sharp = {}
    for (row, column, word, factors), value in gamma.items():
        slot = FIELDS.index(row)
        expected_sharp[48 + column + 1, COTANGENTS[slot], word, factors] = -value
    assert_equal_maps(expected_sharp, gamma_sharp)

    wave = terms(payload["operator_blocks"]["K_RR"]["eight_rod_addition"])
    for i, output in enumerate(COTANGENTS):
        for j, input_row in enumerate(FIELDS):
            for axis, signature in enumerate((-1, 1, 1, 1)):
                factors = factor_key([{"kind": "parameter", "name": "epsilon_R_squared", "spacetime_multiindex": [0, 0, 0, 0], "vertical_multiindex": []}])
                word = tuple(2 if k == axis else 0 for k in range(4))
                if reduced(wave.get((output, input_row, word, factors), 0) - signature * H[i, j]) != 0:
                    raise AssertionError("wave block does not reconstruct H Box")

    direct_h00_derivative_coefficient = -H[0, 0] / 2
    anchor = payload["independent_variation_anchor"]
    if reduced(expression(anchor["serialized_coefficient"]) - direct_h00_derivative_coefficient) != 0:
        raise AssertionError("direct density variation disagrees with mixed anchor")
    if reduced(-expression(anchor["serialized_coefficient"]) - direct_h00_derivative_coefficient) == 0:
        raise AssertionError("sign mutation was not detected")

    for family in payload["operator_blocks"].values():
        for block in family.values():
            if block["matrix_position_count"] != len(block["entries"]):
                raise AssertionError("matrix-position count drift")
            if block["term_count"] != sum(len(entry["terms"]) for entry in block["entries"]):
                raise AssertionError("term count drift")
    if set(payload["operator_blocks"]["K_Rh"]["eight_rod_addition"]["row_support"]) != set(COTANGENTS):
        raise AssertionError("mixed Hessian misses a rod cotangent row")
    if set(payload["operator_blocks"]["K_hR"]["eight_rod_addition"]["column_support"]) != set(FIELDS):
        raise AssertionError("mixed transpose misses a rod field column")


def main() -> int:
    verify()
    print("BERGER_REPLACEMENT112_MIXED_METRIC_ROD_HESSIAN_INTERFACE independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
