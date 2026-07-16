"""Fast exact Q(sqrt(10)) backend for the scientific Berger q2 replay.

This module changes only coefficient representation.  PBW words, Leibniz
expansion, Koszul signs, formal integration by parts, and the three replayed
identities are the same as in :mod:`berger_54_row_q2_replay`.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import time
from typing import Any, Callable, Iterable, Mapping

import sympy as sp

try:
    from . import berger_54_row_q2_arrival as arrival
    from . import berger_54_row_q2_replay as generic
    from . import berger_support_local_q2_import as scientific_import
except ImportError:
    import berger_54_row_q2_arrival as arrival
    import berger_54_row_q2_replay as generic
    import berger_support_local_q2_import as scientific_import


Q10 = tuple[Fraction, Fraction]
ZERO: Q10 = (Fraction(0), Fraction(0))
ONE: Q10 = (Fraction(1), Fraction(0))
Word = tuple[int, ...]
LinearKey = tuple[int, int, Word]
BilinearKey = tuple[int, int, int, Word, Word]
TrilinearKey = tuple[int, int, int, Word, Word]


def qadd(left: Q10, right: Q10) -> Q10:
    return left[0] + right[0], left[1] + right[1]


def qneg(value: Q10) -> Q10:
    return -value[0], -value[1]


def qmul(left: Q10, right: Q10) -> Q10:
    return (
        left[0] * right[0] + 10 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def qscale(value: Q10, scalar: int) -> Q10:
    return scalar * value[0], scalar * value[1]


def _add(target: dict[tuple[Any, ...], Q10], key: tuple[Any, ...], value: Q10) -> None:
    if value == ZERO:
        return
    total = qadd(target.get(key, ZERO), value)
    if total == ZERO:
        target.pop(key, None)
    else:
        target[key] = total


def _fraction_from_sympy(value: sp.Expr) -> Fraction:
    value = sp.cancel(value)
    if not value.is_Rational:
        raise ValueError(f"coefficient is outside Q(sqrt(10)): {value}")
    numerator, denominator = map(int, sp.fraction(value))
    return Fraction(numerator, denominator)


def qfrom_expr(value: sp.Expr) -> Q10:
    value = sp.expand(value)
    conjugate = sp.expand(value.xreplace({scientific_import.SQRT10: -scientific_import.SQRT10}))
    return (
        _fraction_from_sympy((value + conjugate) / 2),
        _fraction_from_sympy(
            (value - conjugate) / (2 * scientific_import.SQRT10)
        ),
    )


def _structure(first: int, second: int) -> dict[int, Q10]:
    u0: Q10 = (Fraction(0), Fraction(3, 20))
    v0: Q10 = (Fraction(0), Fraction(2, 3))
    return {
        (1, 2): {3: u0},
        (2, 1): {3: qneg(u0)},
        (2, 3): {1: v0},
        (3, 2): {1: qneg(v0)},
        (3, 1): {2: v0},
        (1, 3): {2: qneg(v0)},
    }.get((first, second), {})


@lru_cache(maxsize=None)
def pbw_word(word: Word) -> tuple[tuple[Word, Q10], ...]:
    inversion = next(
        (index for index in range(len(word) - 1) if word[index] > word[index + 1]),
        None,
    )
    if inversion is None:
        return ((word, ONE),)
    left, right = word[inversion], word[inversion + 1]
    swapped = word[:inversion] + (right, left) + word[inversion + 2 :]
    output: dict[tuple[Any, ...], Q10] = dict(pbw_word(swapped))
    for target, coefficient in _structure(left, right).items():
        shorter = word[:inversion] + (target,) + word[inversion + 2 :]
        for reduced, nested in pbw_word(shorter):
            _add(output, reduced, qmul(coefficient, nested))
    return tuple((key, value) for key, value in sorted(output.items()) if value != ZERO)


def _word(exponents: Iterable[int]) -> Word:
    values = tuple(exponents)
    if len(values) != 4 or any(type(value) is not int or value < 0 for value in values):
        raise ValueError("invalid PBW exponent vector")
    return tuple(axis for axis, count in enumerate(values) for _ in range(count))


def _exponents(word: Word) -> list[int]:
    return [word.count(axis) for axis in range(4)]


def _parse_linear(matrix: Mapping[str, Any], *, name: str) -> dict[LinearKey, Q10]:
    if matrix.get("shape") != [54, 54] or not isinstance(matrix.get("entries"), list):
        raise ValueError(f"{name} matrix shape drifted")
    output: dict[tuple[Any, ...], Q10] = {}
    for entry in matrix["entries"]:
        if not isinstance(entry, list) or len(entry) != 3:
            raise ValueError(f"{name} matrix entry drifted")
        target, source, terms = entry
        for exponents, raw_coefficient in terms:
            expression = arrival.parse_coefficient(raw_coefficient).subs(
                scientific_import.SPECIALIZATION
            )
            coefficient = qfrom_expr(expression)
            for reduced, pbw_coefficient in pbw_word(_word(exponents)):
                _add(
                    output,
                    (target, source, reduced),
                    qmul(coefficient, pbw_coefficient),
                )
    return output


def _parse_pairing(matrix: Mapping[str, Any]) -> dict[tuple[int, int], Q10]:
    parsed = _parse_linear(matrix, name="cyclic pairing")
    output: dict[tuple[Any, ...], Q10] = {}
    for (left, right, word), coefficient in parsed.items():
        if word:
            raise ValueError("scientific cyclic replay requires the order-zero pairing")
        _add(output, (left, right), coefficient)
    return output


def _parse_scientific_q2() -> dict[BilinearKey, Q10]:
    payload = scientific_import._git_json(scientific_import.PAYLOAD_RELATIVE)
    output: dict[tuple[Any, ...], Q10] = {}
    for row in payload["rows"]:
        target = row["output"]
        for left, left_exponents, right, right_exponents, raw_coefficient in row["terms"]:
            coefficient = scientific_import._quadratic_pair(raw_coefficient)
            for left_word, left_pbw in pbw_word(_word(left_exponents)):
                for right_word, right_pbw in pbw_word(_word(right_exponents)):
                    _add(
                        output,
                        (target, left, right, left_word, right_word),
                        qmul(coefficient, qmul(left_pbw, right_pbw)),
                    )
    return output


def _leibniz(word: Word, left_word: Word, right_word: Word) -> dict[tuple[Word, Word], Q10]:
    states: dict[tuple[Any, ...], Q10] = {(left_word, right_word): ONE}
    for axis in reversed(word):
        following: dict[tuple[Any, ...], Q10] = {}
        for (left, right), coefficient in states.items():
            _add(following, ((axis, *left), right), coefficient)
            _add(following, (left, (axis, *right)), coefficient)
        states = following
    return states  # type: ignore[return-value]


def _add_bilinear_normalized(
    output: dict[BilinearKey, Q10], key: BilinearKey, coefficient: Q10
) -> None:
    target, left, right, left_word, right_word = key
    for left_reduced, left_pbw in pbw_word(left_word):
        for right_reduced, right_pbw in pbw_word(right_word):
            _add(
                output,
                (target, left, right, left_reduced, right_reduced),
                qmul(coefficient, qmul(left_pbw, right_pbw)),
            )


def arity_two_defect(
    q1: Mapping[LinearKey, Q10],
    q2: Mapping[BilinearKey, Q10],
    degrees: tuple[int, ...],
) -> dict[BilinearKey, Q10]:
    output: dict[BilinearKey, Q10] = {}
    q1_by_source: dict[int, list[tuple[int, Word, Q10]]] = defaultdict(list)
    q1_by_target: dict[int, list[tuple[int, Word, Q10]]] = defaultdict(list)
    for (target, source, word), coefficient in q1.items():
        q1_by_source[source].append((target, word, coefficient))
        q1_by_target[target].append((source, word, coefficient))

    for (middle, left, right, left_word, right_word), q2_coefficient in q2.items():
        for target, outer_word, q1_coefficient in q1_by_source.get(middle, []):
            coefficient = qmul(q1_coefficient, q2_coefficient)
            for (new_left, new_right), leibniz_coefficient in _leibniz(
                outer_word, left_word, right_word
            ).items():
                _add_bilinear_normalized(
                    output,
                    (target, left, right, new_left, new_right),
                    qmul(coefficient, leibniz_coefficient),
                )
    for (target, middle, right, outer_left, right_word), q2_coefficient in q2.items():
        for source, inner_word, q1_coefficient in q1_by_target.get(middle, []):
            _add_bilinear_normalized(
                output,
                (target, source, right, outer_left + inner_word, right_word),
                qmul(q2_coefficient, q1_coefficient),
            )
    for (target, left, middle, left_word, outer_right), q2_coefficient in q2.items():
        sign = -1 if degrees[left] & 1 else 1
        for source, inner_word, q1_coefficient in q1_by_target.get(middle, []):
            _add_bilinear_normalized(
                output,
                (target, left, source, left_word, outer_right + inner_word),
                qscale(qmul(q2_coefficient, q1_coefficient), sign),
            )
    return output


def derivation_defect(
    d_action: Mapping[LinearKey, Q10], q2: Mapping[BilinearKey, Q10]
) -> dict[BilinearKey, Q10]:
    output: dict[BilinearKey, Q10] = {}
    d_by_source: dict[int, list[tuple[int, Word, Q10]]] = defaultdict(list)
    d_by_target: dict[int, list[tuple[int, Word, Q10]]] = defaultdict(list)
    for (target, source, word), coefficient in d_action.items():
        d_by_source[source].append((target, word, coefficient))
        d_by_target[target].append((source, word, coefficient))
    for (middle, left, right, left_word, right_word), q2_coefficient in q2.items():
        for target, outer_word, d_coefficient in d_by_source.get(middle, []):
            coefficient = qmul(d_coefficient, q2_coefficient)
            for (new_left, new_right), leibniz_coefficient in _leibniz(
                outer_word, left_word, right_word
            ).items():
                _add_bilinear_normalized(
                    output,
                    (target, left, right, new_left, new_right),
                    qmul(coefficient, leibniz_coefficient),
                )
    for (target, middle, right, outer_left, right_word), q2_coefficient in q2.items():
        for source, inner_word, d_coefficient in d_by_target.get(middle, []):
            _add_bilinear_normalized(
                output,
                (target, source, right, outer_left + inner_word, right_word),
                qneg(qmul(q2_coefficient, d_coefficient)),
            )
    for (target, left, middle, left_word, outer_right), q2_coefficient in q2.items():
        for source, inner_word, d_coefficient in d_by_target.get(middle, []):
            _add_bilinear_normalized(
                output,
                (target, left, source, left_word, outer_right + inner_word),
                qneg(qmul(q2_coefficient, d_coefficient)),
            )
    return output


def _integrate_third_slot(
    third_word: Word, first_word: Word, second_word: Word
) -> dict[tuple[Word, Word], Q10]:
    states: dict[tuple[Any, ...], Q10] = {(first_word, second_word): ONE}
    for axis in third_word:
        following: dict[tuple[Any, ...], Q10] = {}
        for (first, second), coefficient in states.items():
            _add(following, ((axis, *first), second), coefficient)
            _add(following, (first, (axis, *second)), coefficient)
        states = following
    if len(third_word) & 1:
        return {key: qneg(value) for key, value in states.items()}  # type: ignore[return-value]
    return states  # type: ignore[return-value]


def _add_trilinear_normalized(
    output: dict[TrilinearKey, Q10],
    first: int,
    second: int,
    third: int,
    first_word: Word,
    second_word: Word,
    third_word: Word,
    coefficient: Q10,
) -> None:
    for (new_first, new_second), ibp in _integrate_third_slot(
        third_word, first_word, second_word
    ).items():
        for first_reduced, first_pbw in pbw_word(new_first):
            for second_reduced, second_pbw in pbw_word(new_second):
                _add(
                    output,
                    (first, second, third, first_reduced, second_reduced),
                    qmul(coefficient, qmul(ibp, qmul(first_pbw, second_pbw))),
                )


def cyclicity_defect(
    q2: Mapping[BilinearKey, Q10],
    pairing: Mapping[tuple[int, int], Q10],
    degrees: tuple[int, ...],
) -> dict[TrilinearKey, Q10]:
    lhs: dict[TrilinearKey, Q10] = {}
    unsigned_rhs: dict[TrilinearKey, Q10] = {}
    pair_by_left: dict[int, list[tuple[int, Q10]]] = defaultdict(list)
    for (left, right), coefficient in pairing.items():
        pair_by_left[left].append((right, coefficient))
    if (
        len(pair_by_left) != 54
        or any(len(values) != 1 for values in pair_by_left.values())
        or any(
            coefficient not in {ONE, qneg(ONE)}
            or pairing.get((right, left)) != qneg(coefficient)
            for left, ((right, coefficient),) in pair_by_left.items()
        )
    ):
        raise ValueError("cyclic pairing is not the declared odd Darboux pairing")
    dual_slot = {
        index: values[0][1] == qneg(ONE)
        for index, values in pair_by_left.items()
    }
    for (output, first, second, first_word, second_word), q2_coefficient in q2.items():
        for third, pair_coefficient in pair_by_left.get(output, []):
            coefficient = qmul(q2_coefficient, pair_coefficient)
            _add_trilinear_normalized(
                lhs, first, second, third, first_word, second_word, (), coefficient
            )
            _add_trilinear_normalized(
                unsigned_rhs,
                third,
                first,
                second,
                (),
                first_word,
                second_word,
                coefficient,
            )
    defect: dict[TrilinearKey, Q10] = {}
    for key in set(lhs) | set(unsigned_rhs):
        first, second, _third, _first_word, _second_word = key
        coefficient = unsigned_rhs.get(key, ZERO)
        # Lowering an odd Hamiltonian vector field with the imported Darboux
        # matrix contributes the polarization sign of the second slot in
        # addition to the ordinary Koszul exchange sign.
        if dual_slot[second] ^ bool(
            (degrees[first] & 1) * (degrees[second] & 1)
        ):
            coefficient = qneg(coefficient)
        _add(defect, key, qadd(lhs.get(key, ZERO), qneg(coefficient)))
    return defect


def cyclicity_sign_diagnostic(
    q2: Mapping[BilinearKey, Q10],
    pairing: Mapping[tuple[int, int], Q10],
    degrees: tuple[int, ...],
) -> dict[str, Any]:
    """Determine the required cyclic sign independently in each parity sector."""

    lhs: dict[TrilinearKey, Q10] = {}
    unsigned_rhs: dict[TrilinearKey, Q10] = {}
    pair_by_left: dict[int, list[tuple[int, Q10]]] = defaultdict(list)
    for (left, right), coefficient in pairing.items():
        pair_by_left[left].append((right, coefficient))
    for (output, first, second, first_word, second_word), q2_coefficient in q2.items():
        for third, pair_coefficient in pair_by_left.get(output, []):
            coefficient = qmul(q2_coefficient, pair_coefficient)
            _add_trilinear_normalized(
                lhs, first, second, third, first_word, second_word, (), coefficient
            )
            _add_trilinear_normalized(
                unsigned_rhs,
                third,
                first,
                second,
                (),
                first_word,
                second_word,
                coefficient,
            )

    signatures = sorted(
        {
            (degrees[first] & 1, degrees[second] & 1, degrees[third] & 1)
            for first, second, third, _, _ in {*lhs, *unsigned_rhs}
        }
    )
    result: dict[str, Any] = {}
    for signature in signatures:
        left_sector = {
            key: value
            for key, value in lhs.items()
            if tuple(degrees[index] & 1 for index in key[:3]) == signature
        }
        right_sector = {
            key: value
            for key, value in unsigned_rhs.items()
            if tuple(degrees[index] & 1 for index in key[:3]) == signature
        }
        plus_defect = dict(left_sector)
        minus_defect = dict(left_sector)
        for key, value in right_sector.items():
            _add(plus_defect, key, qneg(value))
            _add(minus_defect, key, value)
        required = (
            "+1"
            if not plus_defect
            else "-1"
            if not minus_defect
            else "NO_SCALAR_SIGN"
        )
        result["".join(map(str, signature))] = {
            "required_sign": required,
            "lhs_coefficients": len(left_sector),
            "rhs_coefficients": len(right_sector),
            "plus_defect_count": len(plus_defect),
            "minus_defect_count": len(minus_defect),
        }
    return result


def _exact_rational(value: Fraction) -> int | dict[str, int]:
    if value.denominator == 1:
        return value.numerator
    return {"numerator": value.numerator, "denominator": value.denominator}


def _coefficient(value: Q10) -> dict[str, object]:
    return {
        "rational": _exact_rational(value[0]),
        "sqrt10": _exact_rational(value[1]),
    }


def _records(defect: Mapping[tuple[Any, ...], Q10], *, kind: str) -> list[dict[str, Any]]:
    output = []
    for key, coefficient in sorted(defect.items()):
        if kind in {"q1_q2", "D_q2"}:
            target, left, right, left_word, right_word = key
            output.append(
                {
                    "output": target,
                    "left": left,
                    "right": right,
                    "left_exponents": _exponents(left_word),
                    "right_exponents": _exponents(right_word),
                    "coefficient": _coefficient(coefficient),
                }
            )
        else:
            first, second, third, first_word, second_word = key
            output.append(
                {
                    "first": first,
                    "second": second,
                    "third": third,
                    "first_exponents": _exponents(first_word),
                    "second_exponents": _exponents(second_word),
                    "third_exponents": [0, 0, 0, 0],
                    "coefficient": _coefficient(coefficient),
                }
            )
    return output


def _summary(defect: Mapping[tuple[Any, ...], Q10], *, kind: str) -> dict[str, Any]:
    records = _records(defect, kind=kind)
    return {
        "status": "PASS" if not records else "FAIL",
        "nonzero_coefficient_count": len(records),
        "defect_sha256": arrival.canonical_hash(records),
        "localized_sample": records[:32],
        "sample_truncated": len(records) > 32,
    }


def replay_scientific_q2(
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    imported = scientific_import.import_support_local_q2()
    q1_raw, d_raw, pairing_raw = generic.load_committed_operators()
    timings: dict[str, float] = {}

    start = time.monotonic()
    q1 = _parse_linear(q1_raw, name="q1")
    d_action = _parse_linear(d_raw, name="D")
    pairing = _parse_pairing(pairing_raw)
    q2 = _parse_scientific_q2()
    timings["parse_inputs"] = time.monotonic() - start
    if progress:
        progress(f"parsed {len(q2)} exact q2 coefficients")

    start = time.monotonic()
    q1_q2 = arity_two_defect(q1, q2, imported.parsed.degrees)
    timings["q1_q2"] = time.monotonic() - start
    if progress:
        progress(f"q1/q2 defect coefficients: {len(q1_q2)}")

    start = time.monotonic()
    d_q2 = derivation_defect(d_action, q2)
    timings["D_q2"] = time.monotonic() - start
    if progress:
        progress(f"D/q2 defect coefficients: {len(d_q2)}")

    start = time.monotonic()
    cyclicity = cyclicity_defect(q2, pairing, imported.parsed.degrees)
    timings["BV_cyclicity"] = time.monotonic() - start
    if progress:
        progress(f"cyclicity defect coefficients: {len(cyclicity)}")

    results = {
        "q1_q2_arity_two_nilpotency": _summary(q1_q2, kind="q1_q2"),
        "D_q2_derivation": _summary(d_q2, kind="D_q2"),
        "BV_cyclicity_q2": _summary(cyclicity, kind="cyclicity"),
    }
    return {
        "backend": "two-rational-component-Q(sqrt(10))-v1",
        "arithmetic": "(a,b)*(c,d)=(ac+10bd,ad+bc), representing a+b*sqrt(10)",
        "cyclicity_convention": {
            "pairing": "imported odd Darboux matrix with primal/dual polarization",
            "identity": "T(a,b,c)=(-1)^(dual(b)+parity(a)*parity(b))*T(c,a,b)",
            "integration_by_parts": "all derivatives in the paired third slot are formally adjointed onto the first two slots",
        },
        "input": {
            "classical_commit": imported.parsed.classical_commit,
            "q2_sha256": imported.parsed.q2_sha256,
            "q2_term_count": imported.parsed.term_count,
            "maximum_total_jet_order": imported.parsed.maximum_total_jet_order,
            "specialization": {
                "alpha_B": "5",
                "u": "3*sqrt(10)/20",
                "v": "2*sqrt(10)/3",
            },
        },
        "operator_counts": {
            "q1_PBW_coefficients": len(q1),
            "D_PBW_coefficients": len(d_action),
            "q2_PBW_coefficients": len(q2),
            "pairing_PBW_coefficients": len(pairing),
        },
        "phase_seconds": {name: round(value, 6) for name, value in timings.items()},
        "results": results,
        "all_identities_pass": all(item["status"] == "PASS" for item in results.values()),
    }
