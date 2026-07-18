#!/usr/bin/env python3
"""Exact PBW-order-two full-BV redefinition consumer for retained mixed ell3.

This module is the exact N-G4 filtration engine.  It parses the frozen retained unary,
binary and ternary Taylor payloads in their native suspended graded-symmetric
convention, lifts base-coordinate redefinitions with the certified
derivative-aware super-cotangent rule, and assembles

    [ell1,F3] + [ell2,F2]

    coefficientwise in the Berger PBW algebra.  Its positive-jet consumer found
a normalized exact obstruction on the first associated-graded page, so the
declared order-two filtered removal is terminally obstructed.

Dependency tag: LOCAL-ALGEBRAIC.  Generality: G0.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import gzip
import itertools
import json
from typing import Iterable, Mapping

import sympy as sp

from d_quotient_classical.backreacted_clock import (
    berger_positive_jet_super_cotangent_redefinition_convention as lift,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_exact_primitive as physical,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_redefinition as second,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_zero_jet_ghost_shear_completion as zero_completion,
)
from d_quotient_classical.backreacted_clock import berger_support_local_q2 as engine


ROOT = lift.ROOT
ZERO_PRIMITIVE = zero_completion.OUTPUT
PHYSICAL_PRIMITIVE = physical.OUTPUT

Word = tuple[int, ...]
Atom = tuple[int, Word]


def _word(multiindex: Iterable[int]) -> Word:
    values = tuple(int(count) for count in multiindex)
    if len(values) != 4 or any(count < 0 for count in values):
        raise ValueError(f"invalid retained PBW multiindex: {values}")
    return tuple(
        axis for axis, count in enumerate(values) for _ in range(count)
    )


def _total_order(terms: tuple) -> int:
    """Total input-word order of one bilinear or trilinear term."""

    if len(terms) == 5:
        return len(terms[1]) + len(terms[3])
    if len(terms) == 7:
        return len(terms[1]) + len(terms[3]) + len(terms[5])
    raise ValueError("unexpected Taylor term arity")


def _q10(value: Mapping[str, object]) -> sp.Expr:
    return lift.zero.zero._q10(value)


@lru_cache(maxsize=1)
def retained_operations() -> tuple[
    tuple[tuple[engine.LinearOperator, ...], ...],
    tuple[engine.BilinearOperator, ...],
    tuple[engine.TrilinearOperator, ...],
]:
    """Parse the pinned retained ell1, ell2 and mixed ell3 payloads."""

    carrier = lift.zero.zero._load(lift.zero.zero.TYPED_CARRIER)
    q1_rows: list[list[list[tuple[int, Word, sp.Expr]]]] = [
        [[] for _ in range(36)] for _ in range(36)
    ]
    for output, source, terms in carrier["retained_complex"]["classical_unary_q1"]["entries"]:
        for word, coefficient in terms:
            q1_rows[output][source].append(
                (0, _word(word), lift.zero.zero._scalar(coefficient))
            )
    q1 = tuple(
        tuple(engine.LinearOperator.from_terms(entry) for entry in row)
        for row in q1_rows
    )

    q2_terms: list[list[tuple]] = [[] for _ in range(36)]
    for path in (lift.zero.zero.GRAVITY_ELL2, lift.zero.zero.MIXED_ELL2):
        payload = lift.zero.zero._load(path)
        if payload.get("factorial_convention") != "suspended-graded-symmetric-factorial-v1":
            raise ValueError(f"retained ell2 factorial convention drifted: {path}")
        for row in payload["rows"]:
            q2_terms[row["output"]].extend(
                (
                    left,
                    _word(left_word),
                    right,
                    _word(right_word),
                    _q10(coefficient),
                )
                for left, left_word, right, right_word, coefficient in row["terms"]
            )
    q2 = tuple(engine.BilinearOperator.from_terms(terms) for terms in q2_terms)

    manifest = lift.zero.zero._load(lift.zero.zero.MIXED_ELL3)
    if manifest.get("factorial_convention") != "suspended-graded-symmetric-factorial-v1":
        raise ValueError("retained ell3 factorial convention drifted")
    q3_rows = [engine.TZERO for _ in range(36)]
    seen: set[int] = set()
    for chunk in manifest["chunks"]:
        path = ROOT / chunk["path"]
        if lift.zero.zero._sha256(path) != chunk["file_sha256"]:
            raise ValueError(f"retained ell3 row digest drifted: {chunk['output']}")
        with gzip.open(path, "rt") as handle:
            row = json.load(handle)
        output = int(row["output"])
        if output in seen:
            raise ValueError("duplicate retained ell3 output row")
        seen.add(output)
        q3_rows[output] = engine.TrilinearOperator.from_terms(
            (
                first,
                _word(first_word),
                second_field,
                _word(second_word),
                third,
                _word(third_word),
                _q10(coefficient),
            )
            for first, first_word, second_field, second_word, third, third_word, coefficient in row["terms"]
        )
    if seen != set(range(36)):
        raise ValueError("retained ell3 row ledger is incomplete")
    return q1, q2, tuple(q3_rows)


def _permutation_sign(permutation: tuple[Atom, ...]) -> int:
    canonical, sign = lift._canonical_atoms(permutation)
    if canonical is None:
        return 0
    return sign


def jet_taylor_vectors(
    f2_map: Mapping[lift.Key, sp.Expr],
    f3_map: Mapping[lift.Key, sp.Expr],
) -> tuple[tuple[engine.BilinearOperator, ...], tuple[engine.TrilinearOperator, ...]]:
    """Expand canonical symmetric jet keys into ordered Taylor operators."""

    f2_terms: list[list[tuple]] = [[] for _ in range(36)]
    f3_terms: list[list[tuple]] = [[] for _ in range(36)]
    for arity, source, destination in (
        (2, f2_map, f2_terms),
        (3, f3_map, f3_terms),
    ):
        for (output, atoms), coefficient in source.items():
            canonical, sign = lift._canonical_atoms(atoms)
            if canonical != atoms or sign != 1:
                raise ValueError("jet Taylor map contains a noncanonical input key")
            for permutation in sorted(set(itertools.permutations(atoms))):
                permutation_sign = _permutation_sign(permutation)
                if not permutation_sign:
                    continue
                flattened: list[object] = []
                for field, word in permutation:
                    flattened.extend((field, word))
                destination[output].append(
                    (*flattened, permutation_sign * coefficient)
                )
    return (
        tuple(engine.BilinearOperator.from_terms(terms) for terms in f2_terms),
        tuple(engine.TrilinearOperator.from_terms(terms) for terms in f3_terms),
    )


def coderivation_coboundary(
    f2: tuple[engine.BilinearOperator, ...],
    f3: tuple[engine.TrilinearOperator, ...],
    *,
    q1: tuple[tuple[engine.LinearOperator, ...], ...] | None = None,
    q2: tuple[engine.BilinearOperator, ...] | None = None,
) -> tuple[engine.TrilinearOperator, ...]:
    """Return ``[ell1,F3]+[ell2,F2]`` in exact PBW normal form."""

    retained_q1, retained_q2, _ = retained_operations()
    q1 = retained_q1 if q1 is None else q1
    q2 = retained_q2 if q2 is None else q2
    output = [
        _coboundary_row(target, f2, f3, q1, q2) for target in range(36)
    ]
    return tuple(output)


def _coboundary_row(
    target: int,
    f2: tuple[engine.BilinearOperator, ...],
    f3: tuple[engine.TrilinearOperator, ...],
    q1: tuple[tuple[engine.LinearOperator, ...], ...],
    q2: tuple[engine.BilinearOperator, ...],
) -> engine.TrilinearOperator:
    ternary = engine.TZERO
    for middle, outer in enumerate(q1[target]):
        if outer.terms and f3[middle].terms:
            ternary = ternary + engine._apply_output_linear_trilinear(
                outer, f3[middle]
            )
    if f3[target].terms:
        for slot in range(3):
            ternary = ternary - engine._precompose_trilinear_slot(
                f3[target],
                q1,
                slot=slot,
                parities=lift.zero.PARITIES,
            )
    if f2[target].terms or q2[target].terms:
        ternary = ternary + engine._q2_composed_with_q2_row(
            q2[target], f2, lift.zero.PARITIES
        )
        ternary = ternary - engine._q2_composed_with_q2_row(
            f2[target], q2, lift.zero.PARITIES
        )
    return engine._fixture_trilinear(ternary)


def coderivation_coboundary_page(
    f2: tuple[engine.BilinearOperator, ...],
    f3: tuple[engine.TrilinearOperator, ...],
    page: int,
    *,
    q1: tuple[tuple[engine.LinearOperator, ...], ...],
    q2: tuple[engine.BilinearOperator, ...],
) -> dict[tuple[int, tuple], sp.Expr]:
    """Assemble and immediately project one page, one output row at a time."""

    value: dict[tuple[int, tuple], sp.Expr] = {}
    for output in range(36):
        row = _coboundary_row(output, f2, f3, q1, q2)
        for term in row.terms:
            if _total_order(term) != page or not _mixed_term(output, term):
                continue
            key = (output, term[:-1])
            updated = sp.expand(value.get(key, 0) + term[-1])
            if updated:
                value[key] = updated
            else:
                value.pop(key, None)
    return value


def _add_streamed_term(
    value: dict[tuple[int, tuple], sp.Expr],
    output: int,
    fields: tuple[int, int, int],
    words: tuple[Word, Word, Word],
    coefficient: sp.Expr,
    page: int,
) -> None:
    """PBW-normalize one ordered term and retain only the requested page."""

    if (
        lift.zero.MATTER[lift.zero.PARTNER[output]]
        + sum(lift.zero.MATTER[field] for field in fields)
        != 2
    ):
        return
    reductions = [engine._pbw_word(word) for word in words]
    for first in reductions[0]:
        for second_field in reductions[1]:
            for third in reductions[2]:
                reduced_words = (first[0], second_field[0], third[0])
                if sum(map(len, reduced_words)) != page:
                    continue
                pbw_coefficient = sp.expand(
                    coefficient
                    * first[1]
                    * second_field[1]
                    * third[1]
                ).subs({engine.U: engine.U0, engine.V: engine.V0})
                pbw_coefficient = sp.expand(pbw_coefficient)
                if not pbw_coefficient:
                    continue
                flattened = (
                    fields[0],
                    reduced_words[0],
                    fields[1],
                    reduced_words[1],
                    fields[2],
                    reduced_words[2],
                )
                key = (output, flattened)
                updated = sp.expand(value.get(key, 0) + pbw_coefficient)
                if updated:
                    value[key] = updated
                else:
                    value.pop(key, None)


def coderivation_coboundary_page_streaming(
    f2: tuple[engine.BilinearOperator, ...],
    f3: tuple[engine.TrilinearOperator, ...],
    page: int,
    *,
    q1: tuple[tuple[engine.LinearOperator, ...], ...],
    q2: tuple[engine.BilinearOperator, ...],
) -> dict[tuple[int, tuple], sp.Expr]:
    """Stream the exact page without materializing higher-order PBW terms."""

    value: dict[tuple[int, tuple], sp.Expr] = {}
    q1_supports = {
        old: [
            (new, entry)
            for new, entry in enumerate(q1[old])
            if entry.terms
        ]
        for old in range(36)
    }
    for output in range(36):
        # ell1 after F3.
        for middle, outer in enumerate(q1[output]):
            if not outer.terms or not f3[middle].terms:
                continue
            for _, outer_word, outer_coefficient in outer.terms:
                for first, first_word, second_field, second_word, third, third_word, inner_coefficient in f3[middle].terms:
                    for new_first, new_second, new_third, multiplicity in engine._leibniz_output_terms3(
                        outer_word, first_word, second_word, third_word
                    ):
                        _add_streamed_term(
                            value,
                            output,
                            (first, second_field, third),
                            (new_first, new_second, new_third),
                            outer_coefficient * inner_coefficient * multiplicity,
                            page,
                        )

        # F3 after ell1, with the coderivation bracket minus sign.
        for first, first_word, second_field, second_word, third, third_word, coefficient in f3[output].terms:
            fields = (first, second_field, third)
            words = (first_word, second_word, third_word)
            for slot in range(3):
                sign = -1 if sum(
                    lift.zero.PARITIES[fields[index]] for index in range(slot)
                ) & 1 else 1
                for new_field, entry in q1_supports[fields[slot]]:
                    for _, inner_word, inner_coefficient in entry.terms:
                        new_fields = list(fields)
                        new_words = list(words)
                        new_fields[slot] = new_field
                        new_words[slot] = words[slot] + inner_word
                        _add_streamed_term(
                            value,
                            output,
                            tuple(new_fields),
                            tuple(new_words),
                            -sign * coefficient * inner_coefficient,
                            page,
                        )

        # q2 after F2 and F2 after q2.  The helper streams the three
        # (2,1)-unshuffles with the same signs as the certified engine.
        for bracket_sign, outer, inner_vector in (
            (1, q2[output], f2),
            (-1, f2[output], q2),
        ):
            for middle, outer_word, last, last_word, outer_coefficient in outer.terms:
                for first, first_word, second_field, second_word, inner_coefficient in inner_vector[middle].terms:
                    for new_first, new_second, multiplicity in engine._leibniz_output_terms(
                        outer_word, first_word, second_word
                    ):
                        coefficient = (
                            bracket_sign
                            * outer_coefficient
                            * inner_coefficient
                            * multiplicity
                        )
                        _add_streamed_term(
                            value,
                            output,
                            (first, second_field, last),
                            (new_first, new_second, last_word),
                            coefficient,
                            page,
                        )
                        swap_sign = -1 if (
                            lift.zero.PARITIES[second_field]
                            * lift.zero.PARITIES[last]
                        ) else 1
                        _add_streamed_term(
                            value,
                            output,
                            (first, last, second_field),
                            (new_first, last_word, new_second),
                            swap_sign * coefficient,
                            page,
                        )
                        rotate_sign = -1 if (
                            lift.zero.PARITIES[last]
                            * (
                                lift.zero.PARITIES[first]
                                + lift.zero.PARITIES[second_field]
                            )
                        ) & 1 else 1
                        _add_streamed_term(
                            value,
                            output,
                            (last, first, second_field),
                            (last_word, new_first, new_second),
                            rotate_sign * coefficient,
                            page,
                        )
    return value


def projected_lower_operations(
    maximum_input_order: int,
) -> tuple[
    tuple[tuple[engine.LinearOperator, ...], ...],
    tuple[engine.BilinearOperator, ...],
]:
    """Project ell1/ell2 before composition on a homogeneous low-order page."""

    q1, q2, _ = retained_operations()
    projected_q1 = tuple(
        tuple(
            engine.LinearOperator.from_terms(
                term for term in entry.terms if len(term[1]) <= maximum_input_order
            )
            for entry in row
        )
        for row in q1
    )
    projected_q2 = tuple(
        engine.BilinearOperator.from_terms(
            term for term in row.terms if _total_order(term) <= maximum_input_order
        )
        for row in q2
    )
    return projected_q1, projected_q2


def homogeneous_lower_operations(
    exact_input_order: int,
) -> tuple[
    tuple[tuple[engine.LinearOperator, ...], ...],
    tuple[engine.BilinearOperator, ...],
]:
    """Select one pre-composition homogeneous ell1/ell2 input order."""

    q1, q2, _ = retained_operations()
    return (
        tuple(
            tuple(
                engine.LinearOperator.from_terms(
                    term
                    for term in entry.terms
                    if len(term[1]) == exact_input_order
                )
                for entry in row
            )
            for row in q1
        ),
        tuple(
            engine.BilinearOperator.from_terms(
                term
                for term in row.terms
                if _total_order(term) == exact_input_order
            )
            for row in q2
        ),
    )


def _mixed_term(output: int, term: tuple) -> bool:
    fields = (term[0], term[2], term[4])
    return (
        lift.zero.MATTER[lift.zero.PARTNER[output]]
        + sum(lift.zero.MATTER[field] for field in fields)
        == 2
    )


def page_terms(
    operators: tuple[engine.TrilinearOperator, ...],
    page: int,
) -> dict[tuple[int, tuple], sp.Expr]:
    """Canonical ordered coefficient table at one exact PBW total order."""

    value: dict[tuple[int, tuple], sp.Expr] = {}
    for output, operator in enumerate(operators):
        for term in operator.terms:
            if _total_order(term) != page or not _mixed_term(output, term):
                continue
            key = (output, term[:-1])
            coefficient = sp.expand(term[-1])
            updated = sp.expand(value.get(key, 0) + coefficient)
            if updated:
                value[key] = updated
            else:
                value.pop(key, None)
    return value


def zero_primitive_vectors() -> tuple[
    tuple[engine.BilinearOperator, ...],
    tuple[engine.TrilinearOperator, ...],
]:
    """Load the frozen 67-coefficient full-BV zero-word primitive."""

    certificate = json.loads(ZERO_PRIMITIVE.read_text())
    f2_map: lift.JetTaylor = {}
    f3_map: lift.JetTaylor = {}
    for record in certificate["primitive"]:
        output = int(record["output"])
        inputs = tuple((int(row), ()) for row in record["inputs"])
        coefficient = lift.zero.zero._scalar(str(record["coefficient"]))
        lifted = lift.cotangent_column(output, inputs)
        destination = f2_map if record["kind"] == "F2" else f3_map
        for (dual_output, atoms), value in lifted.items():
            lift._add(destination, dual_output, atoms, coefficient * value)
    return jet_taylor_vectors(f2_map, f3_map)


def zero_page_replay() -> dict[str, int]:
    """Cross-check the native ordered engine against the zero-word theorem."""

    _, _, target = retained_operations()
    q1, q2 = projected_lower_operations(0)
    reconstructed = coderivation_coboundary(
        *zero_primitive_vectors(), q1=q1, q2=q2
    )
    expected = page_terms(target, 0)
    actual = page_terms(reconstructed, 0)
    missing = set(expected) - set(actual)
    extra = set(actual) - set(expected)
    changed = {
        key
        for key in set(expected).intersection(actual)
        if sp.expand(expected[key] - actual[key]) != 0
    }
    if missing or extra or changed:
        raise ValueError(
            f"native zero-page replay failed: missing={len(missing)} "
            f"extra={len(extra)} changed={len(changed)}"
        )
    return {
        "expected_ordered_coefficients": len(expected),
        "reconstructed_ordered_coefficients": len(actual),
        "missing": 0,
        "extra": 0,
        "changed": 0,
    }


@lru_cache(maxsize=None)
def first_jet_labels(axis: int = 0) -> tuple[tuple[str, int, tuple[Atom, ...]], ...]:
    """All degree-zero base F2/F3 Taylor keys with one derivative."""

    if axis not in range(4):
        raise ValueError("first-jet axis must be 0, 1, 2, or 3")
    labels: list[tuple[str, int, tuple[Atom, ...]]] = []
    for kind, base_labels in (("F2", lift.zero.LABELS2), ("F3", lift.zero.LABELS3)):
        for output, inputs in base_labels:
            atoms_for_label: set[tuple[Atom, ...]] = set()
            for slot in range(len(inputs)):
                atoms = [(field, ()) for field in inputs]
                atoms[slot] = (inputs[slot], (axis,))
                canonical, _ = lift._canonical_atoms(atoms)
                if canonical is not None:
                    atoms_for_label.add(canonical)
            labels.extend(
                (kind, output, atoms) for atoms in sorted(atoms_for_label)
            )
    return tuple(labels)


def first_jet_column(
    label: tuple[str, int, tuple[Atom, ...]],
) -> dict[tuple[int, tuple], sp.Expr]:
    """One associated-graded first-page full-BV coboundary column."""

    kind, output, atoms = label
    column = lift.cotangent_column(output, atoms)
    f2, f3 = jet_taylor_vectors(
        column if kind == "F2" else {},
        column if kind == "F3" else {},
    )
    q1, q2 = homogeneous_lower_operations(0)
    return coderivation_coboundary_page_streaming(
        f2, f3, 1, q1=q1, q2=q2
    )


def first_page_targets() -> tuple[dict[tuple[int, tuple], sp.Expr], ...]:
    """Target minus the frozen zero-map/order-one-lower-operation source."""

    _, _, target = retained_operations()
    q1, q2 = homogeneous_lower_operations(1)
    zero_source = coderivation_coboundary_page_streaming(
        *zero_primitive_vectors(), 1, q1=q1, q2=q2
    )
    full_target = page_terms(target, 1)
    residual = dict(full_target)
    for key, coefficient in zero_source.items():
        updated = sp.expand(residual.get(key, 0) - coefficient)
        if updated:
            residual[key] = updated
        else:
            residual.pop(key, None)
    by_axis = [dict() for _ in range(4)]
    for key, coefficient in residual.items():
        _, term = key
        words = (term[1], term[3], term[5])
        axes = [word[0] for word in words if len(word) == 1]
        if len(axes) != 1 or any(len(word) > 1 for word in words):
            raise ValueError("first-page residual left the one-derivative basis")
        by_axis[axes[0]][key] = coefficient
    return tuple(by_axis)


def diagnostics() -> dict[str, object]:
    q1, q2, q3 = retained_operations()
    return {
        "q1_term_count": sum(
            len(entry.terms) for row in q1 for entry in row
        ),
        "q2_term_count": sum(len(row.terms) for row in q2),
        "q3_term_count": sum(len(row.terms) for row in q3),
        "mixed_q3_order_histogram": dict(
            sorted(
                Counter(
                    _total_order(term)
                    for output, row in enumerate(q3)
                    for term in row.terms
                    if _mixed_term(output, term)
                ).items()
            )
        ),
        "zero_page_replay": zero_page_replay(),
        "status": "ORDER_TWO_FILTERED_REMOVAL_OBSTRUCTED_AT_FIRST_ASSOCIATED_GRADED_PAGE",
    }


if __name__ == "__main__":
    print(json.dumps(diagnostics(), indent=2, sort_keys=True))
