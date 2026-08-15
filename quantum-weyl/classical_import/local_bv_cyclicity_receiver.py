#!/usr/bin/env python3
"""Exact local cyclicity receiver for the strict minimal pure-Weyl q2 rows.

The receiver expands the eleven kinematic/cotangent primary kernels into the
thirty independent component coordinates of the minimal BV carrier.  It then
lowers the output with the canonical odd cotangent pairing and normalizes the
resulting trilinear differential polynomial modulo total derivatives.

The polarized Bach Hessian is deliberately excluded from this module.  A
nonzero defect in any of the other five disjoint field-content sectors is
already an obstruction to cyclicity of the complete q2, independently of the
metric cubic vertex.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import gcd
from typing import Iterable, Mapping, Sequence


DIMENSION = 4
SYMMETRIC_PAIRS = tuple(
    (left, right)
    for left in range(DIMENSION)
    for right in range(left, DIMENSION)
)
DEGREES = {
    "h": 0,
    "c": -1,
    "omega": -1,
    "h_star": 1,
    "c_star": 2,
    "omega_star": 2,
}
PARTNERS = {
    "h": "h_star",
    "h_star": "h",
    "c": "c_star",
    "c_star": "c",
    "omega": "omega_star",
    "omega_star": "omega",
}
PRIMARY_IDS = (
    "q2_c_cc",
    "q2_omega_comega",
    "q2_h_ch",
    "q2_h_omegah",
    "q2_hstar_chstar",
    "q2_hstar_omegahstar",
    "q2_cstar_hhstar",
    "q2_cstar_ccstar",
    "q2_cstar_omegaomegastar",
    "q2_omegastar_hhstar",
    "q2_omegastar_comegastar",
)
EXCLUDED_PRIMARY_ID = "q2_hstar_hh"
SIGN_TRANSLATION = {
    "h": 1,
    "c": 1,
    "omega": 1,
    "h_star": 1,
    "c_star": -1,
    "omega_star": -1,
}

Word = tuple[int, ...]
BilinearKey = tuple[int, int, int, Word, Word]
TrilinearKey = tuple[int, int, int, Word, Word]


@dataclass(frozen=True)
class BasisEntry:
    index: int
    symbol: str
    component: tuple[int, int] | int | None
    degree: int

    @property
    def parity(self) -> int:
        return self.degree & 1


def component_label(symbol: str, component: tuple[int, int] | int | None) -> str:
    if component is None:
        return symbol
    if isinstance(component, tuple):
        return f"{symbol}_{component[0]}{component[1]}"
    return f"{symbol}_{component}"


def canonical_basis() -> tuple[BasisEntry, ...]:
    records: list[tuple[str, tuple[int, int] | int | None]] = []
    records.extend(("h", pair) for pair in SYMMETRIC_PAIRS)
    records.extend(("c", index) for index in range(DIMENSION))
    records.append(("omega", None))
    records.extend(("h_star", pair) for pair in SYMMETRIC_PAIRS)
    records.extend(("c_star", index) for index in range(DIMENSION))
    records.append(("omega_star", None))
    return tuple(
        BasisEntry(index, symbol, component, DEGREES[symbol])
        for index, (symbol, component) in enumerate(records)
    )


BASIS = canonical_basis()
INDEX = {(entry.symbol, entry.component): entry.index for entry in BASIS}


def _sym(left: int, right: int) -> tuple[int, int]:
    return tuple(sorted((left, right)))  # type: ignore[return-value]


def _index(symbol: str, component: tuple[int, int] | int | None) -> int:
    return INDEX[(symbol, component)]


def _add(
    output: dict[tuple[object, ...], Fraction],
    key: tuple[object, ...],
    coefficient: Fraction | int,
) -> None:
    coefficient = Fraction(coefficient)
    if not coefficient:
        return
    value = output.get(key, Fraction(0)) + coefficient
    if value:
        output[key] = value
    else:
        output.pop(key, None)


def _term(
    output: dict[BilinearKey, Fraction],
    out_symbol: str,
    out_component: tuple[int, int] | int | None,
    left_symbol: str,
    left_component: tuple[int, int] | int | None,
    right_symbol: str,
    right_component: tuple[int, int] | int | None,
    coefficient: Fraction | int,
    left_word: Word = (),
    right_word: Word = (),
) -> None:
    _add(
        output,
        (
            _index(out_symbol, out_component),
            _index(left_symbol, left_component),
            _index(right_symbol, right_component),
            tuple(sorted(left_word)),
            tuple(sorted(right_word)),
        ),
        coefficient,
    )


def primary_component_terms() -> dict[str, dict[BilinearKey, Fraction]]:
    """Expand every non-Bach primary formula in the portable q2 ledger."""

    result = {primary_id: {} for primary_id in PRIMARY_IDS}

    # [c_left,c_right]^mu.
    terms = result["q2_c_cc"]
    for mu, rho in product(range(DIMENSION), repeat=2):
        _term(terms, "c", mu, "c", rho, "c", mu, 1, (), (rho,))
        _term(terms, "c", mu, "c", mu, "c", rho, -1, (rho,), ())

    # c^rho partial_rho omega.
    terms = result["q2_omega_comega"]
    for rho in range(DIMENSION):
        _term(terms, "omega", None, "c", rho, "omega", None, 1, (), (rho,))

    # Lie transport of a symmetric covariant tensor.
    terms = result["q2_h_ch"]
    for a, b in SYMMETRIC_PAIRS:
        for rho in range(DIMENSION):
            _term(terms, "h", (a, b), "c", rho, "h", (a, b), 1, (), (rho,))
            _term(terms, "h", (a, b), "c", rho, "h", _sym(rho, b), 1, (a,), ())
            _term(terms, "h", (a, b), "c", rho, "h", _sym(a, rho), 1, (b,), ())

    # 2 omega h.
    terms = result["q2_h_omegah"]
    for pair in SYMMETRIC_PAIRS:
        _term(terms, "h", pair, "omega", None, "h", pair, 2)

    # Lie transport of a symmetric contravariant density.
    terms = result["q2_hstar_chstar"]
    for mu, nu in SYMMETRIC_PAIRS:
        for rho in range(DIMENSION):
            _term(terms, "h_star", (mu, nu), "c", rho, "h_star", (mu, nu), 1, (), (rho,))
            _term(terms, "h_star", (mu, nu), "c", mu, "h_star", _sym(rho, nu), -1, (rho,), ())
            _term(terms, "h_star", (mu, nu), "c", nu, "h_star", _sym(mu, rho), -1, (rho,), ())
            _term(terms, "h_star", (mu, nu), "c", rho, "h_star", (mu, nu), 1, (rho,), ())

    # -2 omega h_star.
    terms = result["q2_hstar_omegahstar"]
    for pair in SYMMETRIC_PAIRS:
        _term(terms, "h_star", pair, "omega", None, "h_star", pair, -2)

    # h_star^{mu nu} partial_lambda h_{mu nu}
    #   -2 partial_mu(h_star^{mu nu} h_{lambda nu}).
    terms = result["q2_cstar_hhstar"]
    for lam in range(DIMENSION):
        for mu, nu in product(range(DIMENSION), repeat=2):
            _term(terms, "c_star", lam, "h", _sym(mu, nu), "h_star", _sym(mu, nu), 1, (lam,), ())
            _term(terms, "c_star", lam, "h", _sym(lam, nu), "h_star", _sym(mu, nu), -2, (), (mu,))
            _term(terms, "c_star", lam, "h", _sym(lam, nu), "h_star", _sym(mu, nu), -2, (mu,), ())

    # Lie transport of a covector density.
    terms = result["q2_cstar_ccstar"]
    for lam, rho in product(range(DIMENSION), repeat=2):
        _term(terms, "c_star", lam, "c", rho, "c_star", lam, 1, (), (rho,))
        _term(terms, "c_star", lam, "c", rho, "c_star", rho, 1, (lam,), ())
        _term(terms, "c_star", lam, "c", rho, "c_star", lam, 1, (rho,), ())

    # omega_star partial_lambda omega.
    terms = result["q2_cstar_omegaomegastar"]
    for lam in range(DIMENSION):
        _term(terms, "c_star", lam, "omega", None, "omega_star", None, 1, (lam,), ())

    # 2 h_{mu nu} h_star^{mu nu}; the full-index sum supplies the
    # independent off-diagonal multiplicity.
    terms = result["q2_omegastar_hhstar"]
    for mu, nu in product(range(DIMENSION), repeat=2):
        _term(terms, "omega_star", None, "h", _sym(mu, nu), "h_star", _sym(mu, nu), 2)

    # partial_rho(c^rho omega_star).
    terms = result["q2_omegastar_comegastar"]
    for rho in range(DIMENSION):
        _term(terms, "omega_star", None, "c", rho, "omega_star", None, 1, (rho,), ())
        _term(terms, "omega_star", None, "c", rho, "omega_star", None, 1, (), (rho,))

    return result


def ordered_component_terms(
    ordered_ledger: Sequence[Mapping[str, object]],
) -> tuple[dict[BilinearKey, Fraction], dict[str, dict[BilinearKey, Fraction]]]:
    """Apply the portable ledger's ordered orientations and coefficients."""

    primary = primary_component_terms()
    combined: dict[BilinearKey, Fraction] = {}
    by_primary = {primary_id: {} for primary_id in PRIMARY_IDS}
    seen: list[str] = []
    for row in ordered_ledger:
        primary_id = str(row["primary_id"])
        if primary_id == EXCLUDED_PRIMARY_ID:
            continue
        if primary_id not in primary:
            raise ValueError(f"unknown non-Bach primary id: {primary_id}")
        coefficient = Fraction(int(row["coefficient_relative_to_primary"]))
        orientation = row["orientation"]
        if orientation not in {"PRIMARY", "INTRINSIC_SELF_PAIR", "KOSZUL_SWAP"}:
            raise ValueError(f"unknown ordered orientation: {orientation}")
        seen.append(str(row["component_id"]))
        for (output, left, right, left_word, right_word), value in primary[primary_id].items():
            if orientation == "KOSZUL_SWAP":
                key = (output, right, left, right_word, left_word)
            else:
                key = (output, left, right, left_word, right_word)
            _add(combined, key, coefficient * value)
            _add(by_primary[primary_id], key, coefficient * value)
    if len(seen) != 21 or len(set(seen)) != 21:
        raise ValueError("expected exactly twenty-one non-Bach ordered q2 components")
    return combined, by_primary


def conjugation_multiplier(output: str, inputs: Sequence[str]) -> int:
    """Return the diagonal sign-translation multiplier for one Taylor row."""

    value = SIGN_TRANSLATION[output]
    for symbol in inputs:
        value *= SIGN_TRANSLATION[symbol]
    # Every entry is +/-1, so division by an input sign equals multiplication.
    return value


def translated_ordered_ledger(
    ordered_ledger: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Translate q2 by T q2(T^-1 -, T^-1 -) for diagonal T."""

    translated = []
    for source in ordered_ledger:
        row = dict(source)
        row["coefficient_relative_to_primary"] = int(
            row["coefficient_relative_to_primary"]
        ) * conjugation_multiplier(str(row["output"]), tuple(map(str, row["inputs"])))
        translated.append(row)
    return translated


def canonical_pairing() -> dict[tuple[int, int], Fraction]:
    """Canonical local odd cotangent pairing in independent components."""

    output: dict[tuple[int, int], Fraction] = {}
    for pair in SYMMETRIC_PAIRS:
        weight = 1 if pair[0] == pair[1] else 2
        h, h_star = _index("h", pair), _index("h_star", pair)
        output[(h, h_star)] = Fraction(weight)
        output[(h_star, h)] = Fraction(-weight)
    for index in range(DIMENSION):
        c, c_star = _index("c", index), _index("c_star", index)
        output[(c, c_star)] = Fraction(1)
        output[(c_star, c)] = Fraction(-1)
    omega, omega_star = _index("omega", None), _index("omega_star", None)
    output[(omega, omega_star)] = Fraction(1)
    output[(omega_star, omega)] = Fraction(-1)
    return output


def _integrate_third_slot(
    third_word: Word, first_word: Word, second_word: Word
) -> dict[tuple[Word, Word], Fraction]:
    states = {(tuple(first_word), tuple(second_word)): Fraction(1)}
    for axis in third_word:
        following: dict[tuple[Word, Word], Fraction] = {}
        for (first, second), coefficient in states.items():
            _add(following, (tuple(sorted((*first, axis))), second), -coefficient)
            _add(following, (first, tuple(sorted((*second, axis)))), -coefficient)
        states = following
    return states


def _normalize_trilinear(
    rows: Iterable[tuple[int, int, int, Word, Word, Word, Fraction]],
) -> dict[TrilinearKey, Fraction]:
    output: dict[TrilinearKey, Fraction] = {}
    for first, second, third, first_word, second_word, third_word, coefficient in rows:
        for (new_first, new_second), ibp in _integrate_third_slot(
            third_word, first_word, second_word
        ).items():
            _add(
                output,
                (first, second, third, new_first, new_second),
                coefficient * ibp,
            )
    return output


def cyclicity_defect(
    q2: Mapping[BilinearKey, Fraction],
    pairing: Mapping[tuple[int, int], Fraction] | None = None,
) -> dict[TrilinearKey, Fraction]:
    """Return the exact suspended odd-Darboux cyclicity defect modulo IBP."""

    pairing = dict(pairing or canonical_pairing())
    pair_by_left: dict[int, list[tuple[int, Fraction]]] = defaultdict(list)
    for (left, right), coefficient in pairing.items():
        pair_by_left[left].append((right, coefficient))
    if (
        len(pair_by_left) != len(BASIS)
        or any(len(entries) != 1 for entries in pair_by_left.values())
        or any(
            pairing.get((right, left)) != -coefficient
            for left, ((right, coefficient),) in pair_by_left.items()
        )
    ):
        raise ValueError("pairing is not a nondegenerate odd cotangent pairing")
    dual_slot = {
        index: pair_by_left[index][0][1] < 0
        for index in range(len(BASIS))
    }
    raw = []
    rotated = []
    for (output, first, second, first_word, second_word), value in q2.items():
        for third, pair_value in pair_by_left[output]:
            coefficient = value * pair_value
            raw.append((first, second, third, first_word, second_word, (), coefficient))
            rotated.append((third, first, second, (), first_word, second_word, coefficient))
    lhs = _normalize_trilinear(raw)
    rhs = _normalize_trilinear(rotated)
    defect: dict[TrilinearKey, Fraction] = {}
    for key in set(lhs) | set(rhs):
        first, second = key[:2]
        sign = -1 if (
            dual_slot[second]
            ^ bool(BASIS[first].parity * BASIS[second].parity)
        ) else 1
        _add(defect, key, lhs.get(key, Fraction(0)) - sign * rhs.get(key, Fraction(0)))
    return defect


def defect_sector(key: TrilinearKey) -> tuple[str, str, str]:
    return tuple(BASIS[index].symbol for index in key[:3])  # type: ignore[return-value]


def defect_summary(defect: Mapping[TrilinearKey, Fraction]) -> dict[str, object]:
    sectors: dict[tuple[str, str, str], int] = defaultdict(int)
    for key in defect:
        sectors[defect_sector(key)] += 1
    first_key = min(defect) if defect else None
    return {
        "coefficient_count": len(defect),
        "sector_count": len(sectors),
        "sectors": [
            {"symbols": list(symbols), "coefficient_count": count}
            for symbols, count in sorted(sectors.items())
        ],
        "first_witness": None if first_key is None else {
            "basis": [component_label(BASIS[index].symbol, BASIS[index].component) for index in first_key[:3]],
            "first_word": list(first_key[3]),
            "second_word": list(first_key[4]),
            "coefficient": str(defect[first_key]),
        },
    }


def _rref_nullspace(rows: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    if not rows:
        return [[Fraction(int(i == j)) for i in range(len(PRIMARY_IDS))] for j in range(len(PRIMARY_IDS))]
    matrix = [list(map(Fraction, row)) for row in rows if any(row)]
    columns = len(matrix[0])
    pivots: list[int] = []
    cursor = 0
    for column in range(columns):
        pivot = next((row for row in range(cursor, len(matrix)) if matrix[row][column]), None)
        if pivot is None:
            continue
        matrix[cursor], matrix[pivot] = matrix[pivot], matrix[cursor]
        scale = matrix[cursor][column]
        matrix[cursor] = [value / scale for value in matrix[cursor]]
        for row in range(len(matrix)):
            if row == cursor or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [left - factor * right for left, right in zip(matrix[row], matrix[cursor])]
        pivots.append(column)
        cursor += 1
        if cursor == len(matrix):
            break
    free = [column for column in range(columns) if column not in pivots]
    output = []
    for free_column in free:
        vector = [Fraction(0) for _ in range(columns)]
        vector[free_column] = Fraction(1)
        for row, pivot in reversed(list(enumerate(pivots))):
            vector[pivot] = -sum(
                matrix[row][column] * vector[column]
                for column in free
            )
        output.append(vector)
    return output


def _primitive_integer_vector(vector: Sequence[Fraction]) -> list[int]:
    denominator = 1
    for value in vector:
        denominator = denominator * value.denominator // gcd(denominator, value.denominator)
    integers = [int(value * denominator) for value in vector]
    common = 0
    for value in integers:
        common = gcd(common, abs(value))
    if common:
        integers = [value // common for value in integers]
    first = next((value for value in integers if value), 1)
    if first < 0:
        integers = [-value for value in integers]
    return integers


def cyclic_multiplier_nullspace(
    by_primary: Mapping[str, Mapping[BilinearKey, Fraction]],
) -> dict[str, object]:
    """Solve all exact cyclicity equations for one scalar per primary kernel."""

    columns = [cyclicity_defect(by_primary[primary_id]) for primary_id in PRIMARY_IDS]
    keys = sorted(set().union(*(set(column) for column in columns)))
    equations = [
        [column.get(key, Fraction(0)) for column in columns]
        for key in keys
    ]
    basis = [_primitive_integer_vector(vector) for vector in _rref_nullspace(equations)]
    baseline = [1] * len(PRIMARY_IDS)
    baseline_satisfies = all(
        sum(coefficient * multiplier for coefficient, multiplier in zip(row, baseline)) == 0
        for row in equations
    )
    return {
        "primary_order": list(PRIMARY_IDS),
        "equation_count": len([row for row in equations if any(row)]),
        "rank": len(PRIMARY_IDS) - len(basis),
        "nullity": len(basis),
        "integer_nullspace_basis": basis,
        "landed_all_one_multiplier_satisfies": baseline_satisfies,
    }


def receiver_result(ordered_ledger: Sequence[Mapping[str, object]]) -> dict[str, object]:
    combined, by_primary = ordered_component_terms(ordered_ledger)
    defect = cyclicity_defect(combined)
    translated_ledger = translated_ordered_ledger(ordered_ledger)
    translated, translated_by_primary = ordered_component_terms(translated_ledger)
    translated_defect = cyclicity_defect(translated)
    reverted_diff = {
        key: value
        for key, value in translated.items()
    }
    for key, value in translated_by_primary["q2_cstar_hhstar"].items():
        _add(reverted_diff, key, -2 * value)
    reverted_weyl = {
        key: value
        for key, value in translated.items()
    }
    for key, value in translated_by_primary["q2_omegastar_hhstar"].items():
        _add(reverted_weyl, key, -2 * value)
    return {
        "basis_dimension": len(BASIS),
        "pairing_entry_count": len(canonical_pairing()),
        "primary_kernel_count": len(PRIMARY_IDS),
        "ordered_component_count": 21,
        "expanded_q2_coefficient_count": len(combined),
        "excluded_primary_id": EXCLUDED_PRIMARY_ID,
        "source_convention_defect": defect_summary(defect),
        "translated_convention_defect": defect_summary(translated_defect),
        "translation": {
            "generator_signs": dict(SIGN_TRANSLATION),
            "changed_primary_ids": [
                primary_id
                for primary_id in PRIMARY_IDS
                if conjugation_multiplier(
                    BASIS[next(iter(by_primary[primary_id]))[0]].symbol,
                    tuple(
                        BASIS[index].symbol
                        for index in next(iter(by_primary[primary_id]))[1:3]
                    ),
                )
                == -1
            ],
            "revert_diff_Noether_defect": defect_summary(cyclicity_defect(reverted_diff)),
            "revert_Weyl_Noether_defect": defect_summary(cyclicity_defect(reverted_weyl)),
        },
        "multiplier_classification": cyclic_multiplier_nullspace(by_primary),
    }
