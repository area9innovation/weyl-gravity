#!/usr/bin/env python3
"""Independent exact consumer for the compact-product Einstein--Maxwell export.

This module intentionally does not import either Taylor producer.  It treats
the JSON coefficient-jet tables as the sole operator input and replays the
graded identities and cyclicity over ``Q``.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import product
import json
from pathlib import Path

import sympy as sp

from d_quotient_classical.relative.relative_linfinity_through_arity_three_preflight import (
    validate_taylor,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _rat(value: str) -> sp.Rational:
    result = sp.Rational(value)
    if not result.is_Rational:
        raise ValueError(f"coefficient escaped Q: {value}")
    return result


def _terms(payload: dict) -> tuple[list[list[dict]], int]:
    content = payload["content"]
    profiles = {
        profile["index"]: profile["coefficient_jets"]
        for profile in content.get("coefficient_profiles", [])
    }
    rows: list[list[dict]] = [[] for _ in range(content["row_count"])]
    for raw in content["terms"]:
        coefficient_jets = (
            profiles[raw["coefficient_profile"]]
            if "coefficient_profile" in raw
            else raw["coefficient_jets"]
        )
        term = {
            "inputs": tuple((item["row"], tuple(item["word"])) for item in raw["inputs"]),
            "jets": {tuple(item["word"]): _rat(item["coefficient"]) for item in coefficient_jets},
        }
        rows[raw["output_row"]].append(term)
    return rows, content["arity"]


def _add(target: dict, key: tuple, value: sp.Rational) -> None:
    if value:
        target[key] += value
        if target[key] == 0:
            del target[key]


def _differentiate(term: dict, word: tuple[int, ...]) -> list[tuple[tuple, sp.Rational]]:
    """Differentiate coefficient times all inputs and evaluate at the base."""

    arity = len(term["inputs"])
    output = []
    for assignment in product(range(arity + 1), repeat=len(word)):
        coefficient_word = tuple(sorted(axis for axis, bucket in zip(word, assignment) if bucket == 0))
        coefficient = term["jets"].get(coefficient_word, sp.S.Zero)
        if coefficient == 0:
            continue
        inputs = []
        for slot, (row, old_word) in enumerate(term["inputs"], start=1):
            added = tuple(axis for axis, bucket in zip(word, assignment) if bucket == slot)
            inputs.append((row, tuple(sorted((*old_word, *added)))))
        output.append((tuple(inputs), coefficient))
    return output


_LOCAL = sp.symbols("y0:4")


def _coefficient_polynomial(jets: dict[tuple[int, ...], sp.Rational]) -> sp.Expr:
    value = sp.S.Zero
    for word, coefficient in jets.items():
        multiplicity = sp.S.One
        monomial = sp.S.One
        for axis in range(4):
            count = word.count(axis)
            multiplicity *= sp.factorial(count)
            monomial *= _LOCAL[axis] ** count
        value += coefficient * monomial / multiplicity
    return sp.expand(value)


def _formal_adjoint_product(
    term: dict,
    selected_word: tuple[int, ...],
    remaining: tuple[tuple[int, tuple[int, ...]], ...],
) -> list[tuple[tuple, sp.Rational]]:
    """Apply the fixed-product formal adjoint to coefficient times inputs."""

    states: dict[tuple[tuple[int, tuple[int, ...]], ...], sp.Expr] = {
        remaining: _coefficient_polynomial(term["jets"])
    }
    # d log(sin(theta))/d theta=cot(theta)=-y_theta+O(y_theta^3).
    # Order two is exhaustive because no exported input word is longer.
    divergence = (sp.S.Zero, sp.S.Zero, -_LOCAL[2], sp.S.Zero)
    for axis in reversed(selected_word):
        updated: dict[tuple[tuple[int, tuple[int, ...]], ...], sp.Expr] = defaultdict(lambda: sp.S.Zero)
        for inputs, coefficient in states.items():
            updated[inputs] += -sp.diff(coefficient, _LOCAL[axis]) - divergence[axis] * coefficient
            for slot, (row, word) in enumerate(inputs):
                changed = list(inputs)
                changed[slot] = (row, tuple(sorted((*word, axis))))
                updated[tuple(changed)] += -coefficient
        states = {key: sp.expand(value) for key, value in updated.items() if value != 0}
    substitution = {variable: 0 for variable in _LOCAL}
    return [
        (inputs, sp.Rational(sp.expand(value).subs(substitution)))
        for inputs, value in states.items()
        if sp.expand(value).subs(substitution) != 0
    ]


def _q1_qn(q1: list[list[dict]], qn: list[list[dict]]) -> list[dict]:
    output = [defaultdict(lambda: sp.S.Zero) for _ in q1]
    for target, outer_terms in enumerate(q1):
        for outer in outer_terms:
            middle, word = outer["inputs"][0]
            outer_coefficient = outer["jets"].get((), sp.S.Zero)
            if outer_coefficient == 0:
                continue
            for inner in qn[middle]:
                for inputs, value in _differentiate(inner, word):
                    _add(output[target], inputs, outer_coefficient * value)
    return output


def _qn_q1(qn: list[list[dict]], q1: list[list[dict]], parities: tuple[int, ...]) -> list[dict]:
    output = [defaultdict(lambda: sp.S.Zero) for _ in qn]
    for target, terms in enumerate(qn):
        for outer in terms:
            coefficient = outer["jets"].get((), sp.S.Zero)
            if coefficient == 0:
                continue
            for slot, (middle, word) in enumerate(outer["inputs"]):
                sign = -1 if sum(parities[outer["inputs"][index][0]] for index in range(slot)) % 2 else 1
                for inner in q1[middle]:
                    for replacement, value in _differentiate(inner, word):
                        if len(replacement) != 1:
                            raise AssertionError("unary replacement changed arity")
                        inputs = list(outer["inputs"])
                        inputs[slot] = replacement[0]
                        _add(output[target], tuple(inputs), sign * coefficient * value)
    return output


def _q2_q2(q2: list[list[dict]], parities: tuple[int, ...]) -> list[dict]:
    output = [defaultdict(lambda: sp.S.Zero) for _ in q2]
    for target, outer_terms in enumerate(q2):
        for outer in outer_terms:
            middle, word = outer["inputs"][0]
            last = outer["inputs"][1]
            outer_coefficient = outer["jets"].get((), sp.S.Zero)
            if outer_coefficient == 0:
                continue
            for inner in q2[middle]:
                for inputs, value in _differentiate(inner, word):
                    first, second = inputs
                    coefficient = outer_coefficient * value
                    _add(output[target], (first, second, last), coefficient)
                    sign = -1 if parities[second[0]] * parities[last[0]] else 1
                    _add(output[target], (first, last, second), sign * coefficient)
                    sign = -1 if parities[last[0]] * (parities[first[0]] + parities[second[0]]) % 2 else 1
                    _add(output[target], (last, first, second), sign * coefficient)
    return output


def _combine(*values: list[dict]) -> list[dict]:
    output = [defaultdict(lambda: sp.S.Zero) for _ in values[0]]
    for rows in values:
        for target, entries in enumerate(rows):
            for key, value in entries.items():
                _add(output[target], key, value)
    return output


def _input_symmetry(rows: list[list[dict]], arity: int, parities: tuple[int, ...]) -> None:
    actual = []
    for terms in rows:
        table = defaultdict(lambda: defaultdict(lambda: sp.S.Zero))
        for term in terms:
            for word, value in term["jets"].items():
                table[term["inputs"]][word] += value
        actual.append(table)
    generators = [(0, 1)] if arity == 2 else [(0, 1), (1, 2)]
    for target, table in enumerate(actual):
        for inputs, profile in table.items():
            for left, right in generators:
                swapped = list(inputs)
                swapped[left], swapped[right] = swapped[right], swapped[left]
                sign = -1 if parities[inputs[left][0]] * parities[inputs[right][0]] else 1
                expected = {word: sign * value for word, value in profile.items() if value}
                found = {word: value for word, value in table.get(tuple(swapped), {}).items() if value}
                if expected != found:
                    raise AssertionError(f"arity-{arity} Koszul symmetry failed on row {target}")


def _pairing_data(layout: dict, pairing: dict) -> tuple[tuple[int, ...], tuple[int, ...], dict[tuple[int, int], sp.Rational]]:
    rows = sorted(layout["content"]["rows"], key=lambda item: item["index"])
    parities = tuple(1 if row["parity"] == "odd" else 0 for row in rows)
    duals = tuple(row["dual_row"] for row in rows)
    omega = defaultdict(lambda: sp.S.Zero)
    for term in pairing["content"]["terms"]:
        omega[(term["left_row"], term["right_row"])] += _rat(term["coefficient"])
    return parities, duals, omega


def _cyclic_swap_test(
    rows: list[list[dict]],
    arity: int,
    parities: tuple[int, ...],
    duals: tuple[int, ...],
    omega: dict,
) -> None:
    """Replay infinitesimal symplecticity in the first input, including IBP.

    With the exported odd Darboux convention the local identity is
    ``Omega(q(x,...),y)+Omega(x,q(...,y))=0``.  Input Koszul symmetry is
    checked separately, so the first input generates all cyclic exchanges.
    """

    actual = defaultdict(lambda: sp.S.Zero)
    for output, terms in enumerate(rows):
        test = duals[output]
        pairing_coefficient = omega[(test, output)]
        if pairing_coefficient == 0:
            raise AssertionError(f"missing output pairing on row {output}")
        for term in terms:
            base = term["jets"].get((), sp.S.Zero)
            if base:
                key = ((test, ()), *term["inputs"])
                _add(actual, key, pairing_coefficient * base)

    transformed = defaultdict(lambda: sp.S.Zero)
    for output, terms in enumerate(rows):
        test = duals[output]
        pairing_coefficient = omega[(test, output)]
        for term in terms:
            selected_row, selected_word = term["inputs"][0]
            remaining = (*term["inputs"][1:], (test, ()))
            for differentiated, value in _formal_adjoint_product(
                term, selected_word, remaining
            ):
                key = ((selected_row, ()), *differentiated)
                _add(
                    transformed,
                    key,
                    (
                        -1
                        if (
                            1
                            + (arity - 1)
                            * parities[selected_row]
                            * (1 + parities[test])
                        )
                        % 2
                        else 1
                    )
                    * omega[(output, test)]
                    * value,
                )
    if dict(actual) != dict(transformed):
        difference = defaultdict(lambda: sp.S.Zero, actual)
        for key, value in transformed.items():
            _add(difference, key, -value)
        sample = next(iter(difference.items())) if difference else None
        raise AssertionError(f"arity-{arity} cyclic output/input swap failed: {sample}")


def verify() -> dict:
    certificate = _load(CERTIFICATE)
    validate_taylor(
        certificate,
        expected_result_id="EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1",
        expected_theory="Einstein-Maxwell",
    )
    payloads = {
        name: _load(ROOT / certificate["taylor_artifacts"][name]["path"])
        for name in ("row_layout", "q1", "q2", "q3", "pairing")
    }
    q1, _ = _terms(payloads["q1"])
    q2, _ = _terms(payloads["q2"])
    q3, _ = _terms(payloads["q3"])
    parities, duals, omega = _pairing_data(payloads["row_layout"], payloads["pairing"])
    _input_symmetry(q2, 2, parities)
    _input_symmetry(q3, 3, parities)
    _cyclic_swap_test(q1, 1, parities, duals, omega)
    # Higher cyclicity is tied to the action/cotangent-lift construction in
    # the producer.  This independent consumer checks the convention-free
    # content available from the serialized coderivation: full input Koszul
    # symmetry and every Q^2 identity.  It deliberately does not pretend to
    # rederive the master action from the coefficient table.

    q1_squared = _q1_qn(q1, q1)
    q1q2 = _combine(_q1_qn(q1, q2), _qn_q1(q2, q1, parities))
    arity_three = _combine(
        _q1_qn(q1, q3),
        _qn_q1(q3, q1, parities),
        _q2_q2(q2, parities),
    )
    defects = {
        "q1_squared": [len(row) for row in q1_squared],
        "arity_two": [len(row) for row in q1q2],
        "arity_three": [len(row) for row in arity_three],
    }
    if any(any(counts) for counts in defects.values()):
        raise AssertionError(f"independent Q^2 replay failed: {defects}")
    return {
        "result_id": certificate["result_id"],
        "status": "PASS",
        "row_count": len(q1),
        "term_counts": {
            "q1": sum(len(row) for row in q1),
            "q2": sum(len(row) for row in q2),
            "q3": sum(len(row) for row in q3),
        },
        "cyclicity": {
            "unary_pairing_adjoint": "PASS",
            "higher_input_koszul_symmetry": "PASS",
            "higher_output_input_cyclicity": "PRODUCER_ACTION_DERIVATION_NOT_INDEPENDENTLY_REDERIVED",
        },
        "defect_counts": defects,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
