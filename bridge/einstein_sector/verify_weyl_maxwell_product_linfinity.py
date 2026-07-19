#!/usr/bin/env python3
"""Independent exact consumer for the compact-product Weyl--Maxwell export."""

from __future__ import annotations

from collections import defaultdict
import gc
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.verify_einstein_maxwell_product_linfinity import (
    _add,
    _combine,
    _differentiate,
    _input_symmetry,
    _load,
    _pairing_data,
    _q1_qn,
    _q2_q2,
    _qn_q1,
    _terms,
)
from d_quotient_classical.relative.relative_linfinity_through_arity_three_preflight import (
    validate_taylor,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json"
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
    """Transpose one PBW input against the exact product density through order four."""

    states: dict[tuple[tuple[int, tuple[int, ...]], ...], sp.Expr] = {
        remaining: _coefficient_polynomial(term["jets"])
    }
    # cot(pi/2+y)=-tan(y)=-y-y^3/3+O(y^5).  Fourth-order Bach inputs cannot
    # sample the omitted fifth-order term after evaluation at y=0.
    divergence = (
        sp.S.Zero,
        sp.S.Zero,
        -_LOCAL[2] - _LOCAL[2] ** 3 / 3,
        sp.S.Zero,
    )
    for axis in reversed(selected_word):
        updated: dict[tuple[tuple[int, tuple[int, ...]], ...], sp.Expr] = defaultdict(
            lambda: sp.S.Zero
        )
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


def _cyclic_swap_test(
    rows: list[list[dict]],
    arity: int,
    parities: tuple[int, ...],
    duals: tuple[int, ...],
    omega: dict,
) -> int:
    for row, partner in enumerate(duals):
        if abs(omega[(row, partner)]) != 1 or abs(omega[(partner, row)]) != 1:
            raise AssertionError(f"non-Darboux pairing on rows {row}, {partner}")
    checked = 0
    for target, target_terms in enumerate(rows):
        actual = defaultdict(lambda: sp.S.Zero)
        for term in target_terms:
            base = term["jets"].get((), sp.S.Zero)
            if base:
                _add(actual, term["inputs"], base)
        expected = defaultdict(lambda: sp.S.Zero)
        selected = duals[target]
        for source_output, source_terms in enumerate(rows):
            partner_output = duals[source_output]
            sign = -1 if parities[selected] * parities[partner_output] else 1
            for term in source_terms:
                selected_row, selected_word = term["inputs"][0]
                if selected_row != selected:
                    continue
                remaining = ((partner_output, ()), *term["inputs"][1:])
                for differentiated, value in _formal_adjoint_product(
                    term, selected_word, remaining
                ):
                    _add(expected, differentiated, sign * value)
        if dict(actual) != dict(expected):
            difference = defaultdict(lambda: sp.S.Zero, actual)
            for key, value in expected.items():
                _add(difference, key, -value)
            sample = next(iter(difference.items())) if difference else None
            raise AssertionError(
                f"arity-{arity} ordered cyclic transpose failed on output row "
                f"{target}: {sample}"
            )
        checked += len(actual)
    return checked


def _q1_qn_row(
    target: int,
    q1: list[list[dict]],
    qn: list[list[dict]],
) -> dict:
    """Replay the outer-unary composition on one output row."""

    output = defaultdict(lambda: sp.S.Zero)
    for outer in q1[target]:
        middle, word = outer["inputs"][0]
        outer_coefficient = outer["jets"].get((), sp.S.Zero)
        if outer_coefficient == 0:
            continue
        for inner in qn[middle]:
            for inputs, value in _differentiate(inner, word):
                _add(output, inputs, outer_coefficient * value)
    return output


def _qn_q1_row(
    target: int,
    qn: list[list[dict]],
    q1: list[list[dict]],
    parities: tuple[int, ...],
) -> dict:
    """Replay unary insertion into an n-ary bracket on one output row."""

    output = defaultdict(lambda: sp.S.Zero)
    for outer in qn[target]:
        coefficient = outer["jets"].get((), sp.S.Zero)
        if coefficient == 0:
            continue
        for slot, (middle, word) in enumerate(outer["inputs"]):
            sign = (
                -1
                if sum(
                    parities[outer["inputs"][index][0]]
                    for index in range(slot)
                )
                % 2
                else 1
            )
            for inner in q1[middle]:
                for replacement, value in _differentiate(inner, word):
                    if len(replacement) != 1:
                        raise AssertionError("unary replacement changed arity")
                    inputs = list(outer["inputs"])
                    inputs[slot] = replacement[0]
                    _add(output, tuple(inputs), sign * coefficient * value)
    return output


def _q2_q2_row(
    target: int,
    q2: list[list[dict]],
    parities: tuple[int, ...],
) -> dict:
    """Replay the quadratic Jacobi insertion on one output row."""

    output = defaultdict(lambda: sp.S.Zero)
    for outer in q2[target]:
        middle, word = outer["inputs"][0]
        last = outer["inputs"][1]
        outer_coefficient = outer["jets"].get((), sp.S.Zero)
        if outer_coefficient == 0:
            continue
        for inner in q2[middle]:
            for inputs, value in _differentiate(inner, word):
                first, second = inputs
                coefficient = outer_coefficient * value
                _add(output, (first, second, last), coefficient)
                sign = -1 if parities[second[0]] * parities[last[0]] else 1
                _add(output, (first, last, second), sign * coefficient)
                sign = (
                    -1
                    if parities[last[0]]
                    * (parities[first[0]] + parities[second[0]])
                    % 2
                    else 1
                )
                _add(output, (last, first, second), sign * coefficient)
    return output


def _combine_row(*values: dict) -> dict:
    output = defaultdict(lambda: sp.S.Zero)
    for entries in values:
        for key, value in entries.items():
            _add(output, key, value)
    return output


def verify() -> dict:
    certificate = _load(CERTIFICATE)
    validate_taylor(
        certificate,
        expected_result_id="WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1",
        expected_theory="Weyl-Maxwell",
    )
    row_layout = _load(ROOT / certificate["taylor_artifacts"]["row_layout"]["path"])
    pairing = _load(ROOT / certificate["taylor_artifacts"]["pairing"]["path"])
    q1_payload = _load(ROOT / certificate["taylor_artifacts"]["q1"]["path"])
    q1, _ = _terms(q1_payload)
    del q1_payload
    q2_payload = _load(ROOT / certificate["taylor_artifacts"]["q2"]["path"])
    q2, _ = _terms(q2_payload)
    del q2_payload
    q3_payload = _load(ROOT / certificate["taylor_artifacts"]["q3"]["path"])
    q3, _ = _terms(q3_payload)
    del q3_payload
    gc.collect()
    parities, duals, omega = _pairing_data(row_layout, pairing)
    _input_symmetry(q2, 2, parities)
    _input_symmetry(q3, 3, parities)
    cyclic_counts = {
        "q1": _cyclic_swap_test(q1, 1, parities, duals, omega),
        "q2": _cyclic_swap_test(q2, 2, parities, duals, omega),
        "q3": _cyclic_swap_test(q3, 3, parities, duals, omega),
    }
    defects = {
        "q1_squared": [len(row) for row in _q1_qn(q1, q1)],
        "arity_two": [
            len(row)
            for row in _combine(_q1_qn(q1, q2), _qn_q1(q2, q1, parities))
        ],
        "arity_three": [],
    }
    for target in range(len(q1)):
        defect = _combine_row(
            _q1_qn_row(target, q1, q3),
            _qn_q1_row(target, q3, q1, parities),
            _q2_q2_row(target, q2, parities),
        )
        defects["arity_three"].append(len(defect))
        del defect
        gc.collect()
    if any(any(counts) for counts in defects.values()):
        raise AssertionError(f"independent Weyl--Maxwell Q^2 replay failed: {defects}")
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
            "higher_output_input_cyclicity": "PASS",
            "ordered_first_slot_transpose_counts": cyclic_counts,
        },
        "defect_counts": defects,
        "action_derivation_boundary": "serialized coderivation verified; action-to-coefficient derivation not independently repeated",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
