"""Independent exact replay of the Berger 54-row arity-two identities.

The arrival adapter validates a portable support-local ``q2`` record.  This
module performs the logically separate consumer-side calculation: it composes
that record with the committed unary differential, helical ``D`` action, and
cyclic pairing in the noncommutative Berger PBW algebra.  The implementation
does not import the classical q2 producer.

All three identities are evaluated coefficientwise:

``q1 q2 + q2(q1,-) + (-1)^|x| q2(-,q1) = 0``,
``D q2 - q2(D,-) - q2(-,D) = 0``, and cyclicity of
``<q2(-,-),->`` modulo exact integration by parts.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping

import sympy as sp

TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))

try:
    from . import berger_54_row_q2_arrival as arrival
    from . import berger_54_row_local_d_import as d_import
except ImportError:
    import berger_54_row_q2_arrival as arrival
    import berger_54_row_local_d_import as d_import


U, V = arrival.U, arrival.V
Word = tuple[int, ...]
LinearKey = tuple[int, int, Word]
BilinearKey = tuple[int, int, int, Word, Word]
TrilinearKey = tuple[int, int, int, Word, Word]

def _simp(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(sp.expand(value)))


def _structure(first: int, second: int) -> dict[int, sp.Expr]:
    """Berger invariant-frame commutators, independently encoded."""

    return {
        (1, 2): {3: U},
        (2, 1): {3: -U},
        (2, 3): {1: V},
        (3, 2): {1: -V},
        (3, 1): {2: V},
        (1, 3): {2: -V},
    }.get((first, second), {})


@lru_cache(maxsize=None)
def pbw_word(word: Word) -> tuple[tuple[Word, sp.Expr], ...]:
    """Reduce a frame word to ``e0^n0 e1^n1 e2^n2 e3^n3`` order."""

    inversion = next(
        (index for index in range(len(word) - 1) if word[index] > word[index + 1]),
        None,
    )
    if inversion is None:
        return ((word, sp.S.One),)
    left, right = word[inversion], word[inversion + 1]
    swapped = word[:inversion] + (right, left) + word[inversion + 2 :]
    output: dict[Word, sp.Expr] = dict(pbw_word(swapped))
    for target, coefficient in _structure(left, right).items():
        shorter = word[:inversion] + (target,) + word[inversion + 2 :]
        for reduced, nested in pbw_word(shorter):
            output[reduced] = output.get(reduced, sp.S.Zero) + coefficient * nested
    return tuple(
        (reduced, _simp(coefficient))
        for reduced, coefficient in sorted(output.items())
        if _simp(coefficient) != 0
    )


def _word(exponents: Iterable[int]) -> Word:
    values = tuple(exponents)
    if len(values) != 4 or any(type(value) is not int or value < 0 for value in values):
        raise ValueError("operator term has an invalid PBW exponent vector")
    return tuple(axis for axis, count in enumerate(values) for _ in range(count))


def _exponents(word: Word) -> list[int]:
    if any(axis not in range(4) for axis in word):
        raise ValueError("operator word uses an undeclared Berger frame axis")
    return [word.count(axis) for axis in range(4)]


def _add(
    target: dict[tuple[Any, ...], sp.Expr], key: tuple[Any, ...], value: sp.Expr
) -> None:
    normalized = _simp(value)
    if normalized == 0:
        return
    total = _simp(target.get(key, sp.S.Zero) + normalized)
    if total == 0:
        target.pop(key, None)
    else:
        target[key] = total


def _parse_matrix(
    matrix: Mapping[str, Any],
    *,
    name: str,
    coefficient_substitution: Mapping[sp.Symbol, sp.Expr] | None = None,
) -> dict[LinearKey, sp.Expr]:
    if matrix.get("shape") != [54, 54] or not isinstance(matrix.get("entries"), list):
        raise ValueError(f"{name} matrix shape drifted")
    output: dict[LinearKey, sp.Expr] = {}
    for entry in matrix["entries"]:
        if not isinstance(entry, list) or len(entry) != 3:
            raise ValueError(f"{name} matrix entry drifted")
        target, source, terms = entry
        if (
            type(target) is not int
            or type(source) is not int
            or not 0 <= target < 54
            or not 0 <= source < 54
            or not isinstance(terms, list)
        ):
            raise ValueError(f"{name} matrix index drifted")
        for term in terms:
            if not isinstance(term, list) or len(term) != 2:
                raise ValueError(f"{name} matrix term drifted")
            raw_exponents, raw_coefficient = term
            word = _word(raw_exponents)
            coefficient = arrival.parse_coefficient(raw_coefficient)
            if coefficient_substitution:
                coefficient = _simp(coefficient.subs(coefficient_substitution))
            for reduced, pbw_coefficient in pbw_word(word):
                _add(output, (target, source, reduced), coefficient * pbw_coefficient)
    return output


def _specialize_map(
    values: Mapping[tuple[Any, ...], sp.Expr],
    substitution: Mapping[sp.Symbol, sp.Expr] | None,
) -> dict[tuple[Any, ...], sp.Expr]:
    if not substitution:
        return dict(values)
    output: dict[tuple[Any, ...], sp.Expr] = {}
    for key, coefficient in values.items():
        _add(output, key, coefficient.subs(substitution))
    return output


def _parse_q2(parsed: arrival.ParsedBergerQ2) -> dict[BilinearKey, sp.Expr]:
    output: dict[BilinearKey, sp.Expr] = {}
    for entry in parsed.entries:
        for term in entry.terms:
            left_word = _word(term.left_exponents)
            right_word = _word(term.right_exponents)
            for left_reduced, left_coefficient in pbw_word(left_word):
                for right_reduced, right_coefficient in pbw_word(right_word):
                    _add(
                        output,
                        (
                            entry.output,
                            entry.left,
                            entry.right,
                            left_reduced,
                            right_reduced,
                        ),
                        term.coefficient * left_coefficient * right_coefficient,
                    )
    return output


@lru_cache(maxsize=1)
def load_committed_operators() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load q1, D, and pairing from committed, content-addressed artifacts."""

    _, _, unary = arrival.load_prerequisites()
    d_payload = d_import._git_json(d_import.CERTIFICATE_RELATIVE)
    q1 = unary["classical_unary_q1"]["matrix"]
    d_action = d_payload["D_action"]["matrix"]
    pairing = unary["contraction"]["cyclic_pairing"]
    return q1, d_action, pairing


def _leibniz(
    word: Word, left_word: Word, right_word: Word
) -> dict[tuple[Word, Word], sp.Expr]:
    """Expand an outer differential operator on a bilinear product."""

    states: dict[tuple[Word, Word], sp.Expr] = {(left_word, right_word): sp.S.One}
    for axis in reversed(word):
        following: dict[tuple[Word, Word], sp.Expr] = {}
        for (left, right), coefficient in states.items():
            _add(following, ((axis, *left), right), coefficient)
            _add(following, (left, (axis, *right)), coefficient)
        states = following
    return states


def _normalize_bilinear(
    raw: Mapping[BilinearKey, sp.Expr],
    coefficient_substitution: Mapping[sp.Symbol, sp.Expr] | None = None,
) -> dict[BilinearKey, sp.Expr]:
    output: dict[BilinearKey, sp.Expr] = {}
    for (target, left, right, left_word, right_word), coefficient in raw.items():
        for left_reduced, left_pbw in pbw_word(left_word):
            for right_reduced, right_pbw in pbw_word(right_word):
                value = coefficient * left_pbw * right_pbw
                if coefficient_substitution:
                    value = value.subs(coefficient_substitution)
                _add(
                    output,
                    (target, left, right, left_reduced, right_reduced),
                    value,
                )
    return output


def arity_two_defect(
    q1: Mapping[LinearKey, sp.Expr],
    q2: Mapping[BilinearKey, sp.Expr],
    degrees: tuple[int, ...],
    coefficient_substitution: Mapping[sp.Symbol, sp.Expr] | None = None,
) -> dict[BilinearKey, sp.Expr]:
    """Compute the exact arity-two coefficient of ``Q^2``."""

    raw: dict[BilinearKey, sp.Expr] = {}
    q1_by_source: dict[int, list[tuple[int, Word, sp.Expr]]] = defaultdict(list)
    q1_by_target: dict[int, list[tuple[int, Word, sp.Expr]]] = defaultdict(list)
    for (target, source, word), coefficient in q1.items():
        q1_by_source[source].append((target, word, coefficient))
        q1_by_target[target].append((source, word, coefficient))

    # q1(q2(x,y)); the outer derivative acts by Leibniz on both inputs.
    for (middle, left, right, left_word, right_word), q2_coefficient in q2.items():
        for target, outer_word, q1_coefficient in q1_by_source.get(middle, []):
            for (new_left, new_right), leibniz_coefficient in _leibniz(
                outer_word, left_word, right_word
            ).items():
                _add(
                    raw,
                    (target, left, right, new_left, new_right),
                    q1_coefficient * q2_coefficient * leibniz_coefficient,
                )

    # q2(q1(x),y).
    for (target, middle, right, outer_left, right_word), q2_coefficient in q2.items():
        for source, inner_word, q1_coefficient in q1_by_target.get(middle, []):
            _add(
                raw,
                (target, source, right, outer_left + inner_word, right_word),
                q2_coefficient * q1_coefficient,
            )

    # (-1)^|x| q2(x,q1(y)).
    for (target, left, middle, left_word, outer_right), q2_coefficient in q2.items():
        sign = -1 if degrees[left] & 1 else 1
        for source, inner_word, q1_coefficient in q1_by_target.get(middle, []):
            _add(
                raw,
                (target, left, source, left_word, outer_right + inner_word),
                sign * q2_coefficient * q1_coefficient,
            )
    return _normalize_bilinear(raw, coefficient_substitution)


def derivation_defect(
    d_action: Mapping[LinearKey, sp.Expr],
    q2: Mapping[BilinearKey, sp.Expr],
    coefficient_substitution: Mapping[sp.Symbol, sp.Expr] | None = None,
) -> dict[BilinearKey, sp.Expr]:
    """Compute ``D q2 - q2(D,-) - q2(-,D)`` exactly."""

    raw: dict[BilinearKey, sp.Expr] = {}
    d_by_source: dict[int, list[tuple[int, Word, sp.Expr]]] = defaultdict(list)
    d_by_target: dict[int, list[tuple[int, Word, sp.Expr]]] = defaultdict(list)
    for (target, source, word), coefficient in d_action.items():
        d_by_source[source].append((target, word, coefficient))
        d_by_target[target].append((source, word, coefficient))

    for (middle, left, right, left_word, right_word), q2_coefficient in q2.items():
        for target, outer_word, d_coefficient in d_by_source.get(middle, []):
            for (new_left, new_right), leibniz_coefficient in _leibniz(
                outer_word, left_word, right_word
            ).items():
                _add(
                    raw,
                    (target, left, right, new_left, new_right),
                    d_coefficient * q2_coefficient * leibniz_coefficient,
                )

    for (target, middle, right, outer_left, right_word), q2_coefficient in q2.items():
        for source, inner_word, d_coefficient in d_by_target.get(middle, []):
            _add(
                raw,
                (target, source, right, outer_left + inner_word, right_word),
                -q2_coefficient * d_coefficient,
            )
    for (target, left, middle, left_word, outer_right), q2_coefficient in q2.items():
        for source, inner_word, d_coefficient in d_by_target.get(middle, []):
            _add(
                raw,
                (target, left, source, left_word, outer_right + inner_word),
                -q2_coefficient * d_coefficient,
            )
    return _normalize_bilinear(raw, coefficient_substitution)


def _pairing_terms(pairing: Mapping[str, Any]) -> dict[tuple[int, int], sp.Expr]:
    parsed = _parse_matrix(pairing, name="cyclic pairing")
    output: dict[tuple[int, int], sp.Expr] = {}
    for (left, right, word), coefficient in parsed.items():
        if word:
            raise ValueError("cyclic replay currently requires an order-zero pairing")
        _add(output, (left, right), coefficient)
    return output


def _integrate_third_slot(
    third_word: Word, first_word: Word, second_word: Word
) -> dict[tuple[Word, Word], sp.Expr]:
    """Move all derivatives from the third slot by exact formal adjunction."""

    states: dict[tuple[Word, Word], sp.Expr] = {(first_word, second_word): sp.S.One}
    for axis in third_word:
        following: dict[tuple[Word, Word], sp.Expr] = {}
        for (first, second), coefficient in states.items():
            _add(following, ((axis, *first), second), coefficient)
            _add(following, (first, (axis, *second)), coefficient)
        states = following
    sign = -1 if len(third_word) & 1 else 1
    return {key: sign * coefficient for key, coefficient in states.items()}


def _normalize_trilinear(
    raw: Iterable[tuple[int, int, int, Word, Word, Word, sp.Expr]],
    coefficient_substitution: Mapping[sp.Symbol, sp.Expr] | None = None,
) -> dict[TrilinearKey, sp.Expr]:
    output: dict[TrilinearKey, sp.Expr] = {}
    for first, second, third, first_word, second_word, third_word, coefficient in raw:
        for (new_first, new_second), ibp_coefficient in _integrate_third_slot(
            third_word, first_word, second_word
        ).items():
            for first_reduced, first_pbw in pbw_word(new_first):
                for second_reduced, second_pbw in pbw_word(new_second):
                    value = coefficient * ibp_coefficient * first_pbw * second_pbw
                    if coefficient_substitution:
                        value = value.subs(coefficient_substitution)
                    _add(
                        output,
                        (first, second, third, first_reduced, second_reduced),
                        value,
                    )
    return output


def cyclicity_defect(
    q2: Mapping[BilinearKey, sp.Expr],
    pairing: Mapping[str, Any],
    degrees: tuple[int, ...],
    coefficient_substitution: Mapping[sp.Symbol, sp.Expr] | None = None,
) -> dict[TrilinearKey, sp.Expr]:
    """Check graded cyclicity of ``<q2(x,y),z>`` modulo total derivatives."""

    pair = _pairing_terms(pairing)
    pair_by_left: dict[int, list[tuple[int, sp.Expr]]] = defaultdict(list)
    for (left, right), coefficient in pair.items():
        pair_by_left[left].append((right, coefficient))
    if (
        len(pair_by_left) != 54
        or any(len(values) != 1 for values in pair_by_left.values())
        or any(
            coefficient not in {sp.S.One, -sp.S.One}
            or pair.get((right, left)) != -coefficient
            for left, ((right, coefficient),) in pair_by_left.items()
        )
    ):
        raise ValueError("cyclic pairing is not the declared odd Darboux pairing")
    dual_slot = {
        index: values[0][1] == -sp.S.One
        for index, values in pair_by_left.items()
    }
    raw: list[tuple[int, int, int, Word, Word, Word, sp.Expr]] = []
    rotated: list[tuple[int, int, int, Word, Word, Word, sp.Expr]] = []
    for (output, first, second, first_word, second_word), q2_coefficient in q2.items():
        for third, pair_coefficient in pair_by_left.get(output, []):
            coefficient = q2_coefficient * pair_coefficient
            raw.append((first, second, third, first_word, second_word, (), coefficient))
            rotated.append(
                (third, first, second, (), first_word, second_word, coefficient)
            )
    lhs = _normalize_trilinear(raw, coefficient_substitution)
    unsigned_rhs = _normalize_trilinear(rotated, coefficient_substitution)
    defect: dict[TrilinearKey, sp.Expr] = {}
    for key in set(lhs) | set(unsigned_rhs):
        first, second, _third, _first_word, _second_word = key
        coefficient = unsigned_rhs.get(key, sp.S.Zero)
        if dual_slot[second] ^ bool(
            (degrees[first] & 1) * (degrees[second] & 1)
        ):
            coefficient = -coefficient
        _add(defect, key, lhs.get(key, sp.S.Zero) - coefficient)
    return defect


def _coefficient_text(value: sp.Expr) -> str:
    return sp.sstr(_simp(value))


def _defect_records(
    defect: Mapping[tuple[Any, ...], sp.Expr], *, kind: str
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key, coefficient in sorted(defect.items()):
        if kind in {"q1_q2", "D_q2"}:
            target, left, right, left_word, right_word = key
            records.append(
                {
                    "output": target,
                    "left": left,
                    "right": right,
                    "left_exponents": _exponents(left_word),
                    "right_exponents": _exponents(right_word),
                    "coefficient": _coefficient_text(coefficient),
                }
            )
        elif kind == "cyclicity":
            first, second, third, first_word, second_word = key
            records.append(
                {
                    "first": first,
                    "second": second,
                    "third": third,
                    "first_exponents": _exponents(first_word),
                    "second_exponents": _exponents(second_word),
                    "third_exponents": [0, 0, 0, 0],
                    "coefficient": _coefficient_text(coefficient),
                }
            )
        else:
            raise ValueError(f"unknown defect kind: {kind}")
    return records


def _defect_summary(defect: Mapping[tuple[Any, ...], sp.Expr], *, kind: str) -> dict[str, Any]:
    records = _defect_records(defect, kind=kind)
    return {
        "status": "PASS" if not records else "FAIL",
        "nonzero_coefficient_count": len(records),
        "defect_sha256": arrival.canonical_hash(records),
        "localized_sample": records[:32],
        "sample_truncated": len(records) > 32,
    }


def replay_parsed_q2(
    parsed: arrival.ParsedBergerQ2,
    *,
    q1_matrix: Mapping[str, Any] | None = None,
    d_matrix: Mapping[str, Any] | None = None,
    pairing_matrix: Mapping[str, Any] | None = None,
    coefficient_substitution: Mapping[sp.Symbol, sp.Expr] | None = None,
) -> dict[str, Any]:
    """Replay all exact identities and return localized defect certificates."""

    committed_q1, committed_d, committed_pairing = load_committed_operators()
    q1_raw = q1_matrix or committed_q1
    d_raw = d_matrix or committed_d
    pairing_raw = pairing_matrix or committed_pairing
    q1 = _parse_matrix(
        q1_raw, name="q1", coefficient_substitution=coefficient_substitution
    )
    d_action = _parse_matrix(
        d_raw, name="D", coefficient_substitution=coefficient_substitution
    )
    q2 = _parse_q2(parsed)
    q1_q2 = _specialize_map(
        arity_two_defect(q1, q2, parsed.degrees, coefficient_substitution),
        coefficient_substitution,
    )
    d_q2 = _specialize_map(
        derivation_defect(d_action, q2, coefficient_substitution),
        coefficient_substitution,
    )
    cyclic = _specialize_map(
        cyclicity_defect(
            q2, pairing_raw, parsed.degrees, coefficient_substitution
        ),
        coefficient_substitution,
    )
    results = {
        "q1_q2_arity_two_nilpotency": _defect_summary(q1_q2, kind="q1_q2"),
        "D_q2_derivation": _defect_summary(d_q2, kind="D_q2"),
        "BV_cyclicity_q2": _defect_summary(cyclic, kind="cyclicity"),
    }
    return {
        "coefficient_ring": arrival.COEFFICIENT_RING,
        "ordered_pbw_basis": arrival.ORDERED_PBW_BASIS,
        "identity_conventions": {
            "arity_two": "q1*q2 + q2(q1,-) + (-1)^degree(left)*q2(-,q1)",
            "D_derivation": "D*q2 - q2(D,-) - q2(-,D)",
            "cyclicity": "T(a,b,c)=(-1)^(dual(b)+parity(a)*parity(b))*T(c,a,b) for the imported odd Darboux polarization",
            "integration_by_parts": "all derivatives on the third pairing slot are formally adjointed onto the first two slots",
        },
        "input": {
            "q2_sha256": parsed.q2_sha256,
            "q2_term_count": parsed.term_count,
            "maximum_total_jet_order": parsed.maximum_total_jet_order,
            "coefficient_specialization": (
                {
                    str(symbol): _coefficient_text(value)
                    for symbol, value in sorted(
                        (coefficient_substitution or {}).items(), key=lambda item: str(item[0])
                    )
                }
                if coefficient_substitution
                else None
            ),
        },
        "operator_counts": {
            "q1_PBW_coefficients": len(q1),
            "D_PBW_coefficients": len(d_action),
            "q2_PBW_coefficients": len(q2),
            "pairing_PBW_coefficients": len(_pairing_terms(pairing_raw)),
        },
        "results": results,
        "all_identities_pass": all(result["status"] == "PASS" for result in results.values()),
    }


@lru_cache(maxsize=1)
def implementation_fixture() -> arrival.ParsedBergerQ2:
    """Non-scientific nonzero fixture used only to certify the replay engine."""

    _, _, unary = arrival.load_prerequisites()
    rows = unary["row_layout"]["component_rows"]
    q2_body = {
        "fixture": "field_field_to_equation",
        "entry": [27, 5, 5, [0, 0, 0, 0], [0, 0, 0, 0], "alpha_B*u/2"],
    }
    return arrival.ParsedBergerQ2(
        classical_commit="0" * 40,
        row_ids=tuple(row["row_id"] for row in rows),
        degrees=tuple(row["degree"] for row in rows),
        maximum_total_jet_order=0,
        entries=(
            arrival.PBWBilinearEntry(
                output=27,
                left=5,
                right=5,
                terms=(
                    arrival.PBWBilinearTerm(
                        (0, 0, 0, 0),
                        (0, 0, 0, 0),
                        arrival.parse_coefficient("alpha_B*u/2"),
                    ),
                ),
            ),
        ),
        q2_sha256=arrival.canonical_hash(q2_body),
        term_count=1,
    )


def output_row_mutation(parsed: arrival.ParsedBergerQ2) -> arrival.ParsedBergerQ2:
    """Valid-degree mutation that must be detected by q1q2 and cyclic replay."""

    entry = replace(parsed.entries[0], output=28)
    return replace(
        parsed,
        entries=(entry,),
        q2_sha256=arrival.canonical_hash({"mutation": "output_27_to_28"}),
    )


def d_axis_mutation(d_matrix: Mapping[str, Any]) -> dict[str, Any]:
    """Replace D=e0 by e1 on row 5 for a derivation-sensitivity fixture."""

    mutated = json.loads(json.dumps(d_matrix))
    changed = False
    for entry in mutated["entries"]:
        if entry[0] == 5 and entry[1] == 5:
            entry[2] = [[[0, 1, 0, 0], "1"]]
            changed = True
            break
    if not changed:
        raise ValueError("D mutation target row is absent")
    mutated["sha256"] = arrival.canonical_hash(
        {"shape": mutated["shape"], "entries": mutated["entries"]}
    )
    return mutated


@lru_cache(maxsize=1)
def build_replay_engine_payload() -> dict[str, Any]:
    """Build the fixture-and-mutation readiness certificate payload."""

    fixture = implementation_fixture()
    unary_import, d_import_payload, _ = arrival.load_prerequisites()
    q1, d_action, pairing = load_committed_operators()
    positive = replay_parsed_q2(
        fixture, q1_matrix=q1, d_matrix=d_action, pairing_matrix=pairing
    )
    output_mutation = replay_parsed_q2(
        output_row_mutation(fixture),
        q1_matrix=q1,
        d_matrix=d_action,
        pairing_matrix=pairing,
    )
    d_mutation = replay_parsed_q2(
        fixture,
        q1_matrix=q1,
        d_matrix=d_axis_mutation(d_action),
        pairing_matrix=pairing,
    )
    sensitivity = {
        "output_row_mutation": {
            "mutation": "q2 output row 27 -> 28",
            "q1_q2_detected": output_mutation["results"]["q1_q2_arity_two_nilpotency"]["status"] == "FAIL",
            "cyclicity_detected": output_mutation["results"]["BV_cyclicity_q2"]["status"] == "FAIL",
            "localized_results": output_mutation["results"],
        },
        "D_axis_mutation": {
            "mutation": "D row 5 derivative e0 -> e1",
            "D_derivation_detected": d_mutation["results"]["D_q2_derivation"]["status"] == "FAIL",
            "localized_result": d_mutation["results"]["D_q2_derivation"],
        },
    }
    fixture_sensitive = (
        positive["all_identities_pass"]
        and sensitivity["output_row_mutation"]["q1_q2_detected"]
        and sensitivity["output_row_mutation"]["cyclicity_detected"]
        and sensitivity["D_axis_mutation"]["D_derivation_detected"]
    )
    return {
        "schema": "quantum-weyl-berger-54-row-q2-replay-engine-v1",
        "result_id": "BERGER_54_ROW_Q2_REPLAY_ENGINE",
        "result_state": "EXACT_PBW_REPLAY_ENGINE_READY_SCIENTIFIC_Q2_INPUT_BLOCKED",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_id": arrival.SETTING_ID,
        "prerequisite_binding": arrival.expected_dependency_refs(
            unary_import, d_import_payload
        ),
        "implementation_fixture": positive,
        "mutation_sensitivity": sensitivity,
        "engine_capabilities": {
            "independent_q1_q2_identity_execution": True,
            "independent_D_q2_derivation_execution": True,
            "independent_BV_cyclicity_execution": True,
            "noncommutative_PBW_reduction": True,
            "exact_integration_by_parts": True,
            "localized_defect_records": True,
            "fixture_and_mutation_suite_pass": fixture_sensitive,
        },
        "input_gate": {
            "classical_q2_export_available": False,
            "scientific_fixture_substitution_allowed": False,
            "status": "INPUT_BLOCKED",
            "arrival_action": "parse the committed portable q2 with berger_54_row_q2_arrival.parse_portable_q2, then pass the parsed tensor to replay_parsed_q2",
        },
        "claim_flags": {
            "REPLAY_ENGINE_READY": fixture_sensitive,
            "CLASSICAL_SUPPORT_LOCAL_Q2_IMPORTED": False,
            "SCIENTIFIC_ARITY_TWO_IDENTITIES_REPLAYED": False,
            "TRANSFERRED_ELL2_COMPUTED": False,
            "INTERACTING_CARTAN_VERDICT": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC certificate validates the independent exact PBW replay implementation on a nonzero implementation fixture and three mutation-sensitive identity branches. It does not import the in-progress classical q2, does not certify the scientific 54-row arity-two identities, and makes no transfer, Cartan, causal, anomaly, QME, or quantum claim.",
    }
