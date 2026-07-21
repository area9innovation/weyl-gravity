#!/usr/bin/env python3
"""Exact higher-jet scan of the retained mixed-ell3 22-row functional.

This is an exploratory consumer for the bounded cyclic-deformation gate.  It
does not promote a claim.  The scan evaluates the stored first-page functional
on derivative-aware cyclic super-cotangent ``F2/F3`` columns without
materialising their complete ternary images.  The implementation transposes
the twelve supported page-one rows directly through

    [ell1, F3] + [ell2, F2]

and therefore stays exact over ``QQ(sqrt(10))``.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import itertools
import json
import time
from typing import Iterable, Mapping

import sympy as sp

from d_quotient_classical.backreacted_clock import (
    berger_positive_jet_super_cotangent_redefinition_convention as lift,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_order_two_full_bv_redefinition as core,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_positive_jet_full_bv_obstruction as obstruction,
)
from d_quotient_classical.backreacted_clock import berger_support_local_q2 as engine


Atom = tuple[int, tuple[int, ...]]
BaseLabel = tuple[str, int, tuple[int, ...]]


def _weights() -> tuple[dict[tuple[int, tuple], sp.Expr], dict[int, set[tuple[int, ...]]]]:
    value = json.loads(obstruction.OUTPUT.read_text())
    weights: dict[tuple[int, tuple], sp.Expr] = {}
    field_support: dict[int, set[tuple[int, ...]]] = {}
    for record in value["obstruction_witness"]["weights"]:
        if int(record["page"]) != 1:
            continue
        key = obstruction._actual_first_key(record)
        weights[key] = obstruction._coefficient(str(record["coefficient"]))
        output, term = key
        field_support.setdefault(output, set()).add(
            (term[0], term[2], term[4])
        )
    return weights, field_support


WEIGHTS, FIELD_SUPPORT = _weights()
Q1, Q2, _ = core.retained_operations()
WITNESS_OUTPUTS = tuple(sorted(FIELD_SUPPORT))


def _pair_reduced(
    output: int,
    fields: tuple[int, int, int],
    words: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
    coefficient: sp.Expr,
) -> sp.Expr:
    if fields not in FIELD_SUPPORT.get(output, ()):
        return sp.S.Zero
    value = sp.S.Zero
    reductions = tuple(engine._pbw_word(word) for word in words)
    for first in reductions[0]:
        for second in reductions[1]:
            for third in reductions[2]:
                if len(first[0]) + len(second[0]) + len(third[0]) != 1:
                    continue
                key = (
                    output,
                    (
                        fields[0],
                        first[0],
                        fields[1],
                        second[0],
                        fields[2],
                        third[0],
                    ),
                )
                value += (
                    WEIGHTS.get(key, 0)
                    * coefficient
                    * sp.expand(
                        (first[1] * second[1] * third[1]).subs(
                            {engine.U: engine.U0, engine.V: engine.V0}
                        )
                    )
                )
    return sp.expand(value)


@lru_cache(maxsize=None)
def _unit_f3_pairing(
    f_output: int,
    first: int,
    first_word: tuple[int, ...],
    second: int,
    second_word: tuple[int, ...],
    third: int,
    third_word: tuple[int, ...],
) -> sp.Expr:
    value = sp.S.Zero
    fields = (first, second, third)
    words = (first_word, second_word, third_word)

    for output in WITNESS_OUTPUTS:
        if fields not in FIELD_SUPPORT[output]:
            continue
        for _, outer_word, outer_coefficient in Q1[output][f_output].terms:
            for new_first, new_second, new_third, multiplicity in engine._leibniz_output_terms3(
                outer_word, first_word, second_word, third_word
            ):
                value += _pair_reduced(
                    output,
                    fields,
                    (new_first, new_second, new_third),
                    outer_coefficient * multiplicity,
                )

    if f_output in FIELD_SUPPORT:
        for slot in range(3):
            sign = -1 if sum(
                lift.zero.PARITIES[fields[index]] for index in range(slot)
            ) & 1 else 1
            old_field = fields[slot]
            for new_field, entry in enumerate(Q1[old_field]):
                if not entry.terms:
                    continue
                new_fields = list(fields)
                new_fields[slot] = new_field
                if tuple(new_fields) not in FIELD_SUPPORT[f_output]:
                    continue
                for _, inner_word, inner_coefficient in entry.terms:
                    new_words = list(words)
                    new_words[slot] = words[slot] + inner_word
                    value += _pair_reduced(
                        f_output,
                        tuple(new_fields),
                        tuple(new_words),
                        -sign * inner_coefficient,
                    )
    return sp.factor(value)


def _three_unshuffles(
    first: int,
    first_word: tuple[int, ...],
    second: int,
    second_word: tuple[int, ...],
    last: int,
    last_word: tuple[int, ...],
    coefficient: sp.Expr,
) -> tuple[tuple[tuple[int, int, int], tuple[tuple[int, ...], ...], sp.Expr], ...]:
    swap_sign = -1 if lift.zero.PARITIES[second] * lift.zero.PARITIES[last] else 1
    rotate_sign = -1 if (
        lift.zero.PARITIES[last]
        * (lift.zero.PARITIES[first] + lift.zero.PARITIES[second])
    ) & 1 else 1
    return (
        (
            (first, second, last),
            (first_word, second_word, last_word),
            coefficient,
        ),
        (
            (first, last, second),
            (first_word, last_word, second_word),
            swap_sign * coefficient,
        ),
        (
            (last, first, second),
            (last_word, first_word, second_word),
            rotate_sign * coefficient,
        ),
    )


@lru_cache(maxsize=None)
def _unit_f2_pairing(
    f_output: int,
    first: int,
    first_word: tuple[int, ...],
    second: int,
    second_word: tuple[int, ...],
) -> sp.Expr:
    value = sp.S.Zero

    for output in WITNESS_OUTPUTS:
        for middle, outer_word, last, last_word, outer_coefficient in Q2[output].terms:
            if middle != f_output:
                continue
            for new_first, new_second, multiplicity in engine._leibniz_output_terms(
                outer_word, first_word, second_word
            ):
                for fields, words, coefficient in _three_unshuffles(
                    first,
                    new_first,
                    second,
                    new_second,
                    last,
                    last_word,
                    outer_coefficient * multiplicity,
                ):
                    value += _pair_reduced(output, fields, words, coefficient)

    if f_output in FIELD_SUPPORT:
        for q_first, q_first_word, q_second, q_second_word, q_coefficient in Q2[first].terms:
            for new_first, new_second, multiplicity in engine._leibniz_output_terms(
                first_word, q_first_word, q_second_word
            ):
                for fields, words, coefficient in _three_unshuffles(
                    q_first,
                    new_first,
                    q_second,
                    new_second,
                    second,
                    second_word,
                    -q_coefficient * multiplicity,
                ):
                    value += _pair_reduced(f_output, fields, words, coefficient)
    return sp.factor(value)


def _expanded_column_pairing(
    kind: str,
    column: Mapping[tuple[int, tuple[Atom, ...]], sp.Expr],
) -> sp.Expr:
    value = sp.S.Zero
    for (output, atoms), coefficient in column.items():
        for permutation in sorted(set(itertools.permutations(atoms))):
            sign = core._permutation_sign(permutation)
            if not sign:
                continue
            if kind == "F2":
                value += coefficient * sign * _unit_f2_pairing(
                    output,
                    permutation[0][0],
                    permutation[0][1],
                    permutation[1][0],
                    permutation[1][1],
                )
            else:
                value += coefficient * sign * _unit_f3_pairing(
                    output,
                    permutation[0][0],
                    permutation[0][1],
                    permutation[1][0],
                    permutation[1][1],
                    permutation[2][0],
                    permutation[2][1],
                )
    return sp.factor(value)


def _field_connected(
    kind: str,
    output: int,
    inputs: tuple[int, ...],
) -> bool:
    column = lift.cotangent_column(output, tuple((field, ()) for field in inputs))
    for (f_output, atoms), _ in column.items():
        for permutation in set(itertools.permutations(atoms)):
            fields = tuple(atom[0] for atom in permutation)
            if kind == "F3":
                for witness_output in WITNESS_OUTPUTS:
                    if Q1[witness_output][f_output].terms and fields in FIELD_SUPPORT[witness_output]:
                        return True
                if f_output in FIELD_SUPPORT:
                    for slot in range(3):
                        for new_field, entry in enumerate(Q1[fields[slot]]):
                            changed = list(fields)
                            changed[slot] = new_field
                            if entry.terms and tuple(changed) in FIELD_SUPPORT[f_output]:
                                return True
            else:
                first, second = fields
                for witness_output in WITNESS_OUTPUTS:
                    for middle, _, last, _, _ in Q2[witness_output].terms:
                        if middle != f_output:
                            continue
                        if any(
                            candidate in FIELD_SUPPORT[witness_output]
                            for candidate, _, _ in _three_unshuffles(
                                first, (), second, (), last, (), sp.S.One
                            )
                        ):
                            return True
                if f_output in FIELD_SUPPORT:
                    for q_first, _, q_second, _, _ in Q2[first].terms:
                        if any(
                            candidate in FIELD_SUPPORT[f_output]
                            for candidate, _, _ in _three_unshuffles(
                                q_first, (), q_second, (), second, (), sp.S.One
                            )
                        ):
                            return True
    return False


@lru_cache(maxsize=1)
def connected_base_labels() -> tuple[BaseLabel, ...]:
    labels: list[BaseLabel] = []
    for kind, base_labels in (
        ("F2", lift.zero.LABELS2),
        ("F3", lift.zero.LABELS3),
    ):
        for output, inputs in base_labels:
            if _field_connected(kind, output, inputs):
                labels.append((kind, output, inputs))
    return tuple(labels)


def _second_order_atoms(inputs: tuple[int, ...]) -> tuple[tuple[Atom, ...], ...]:
    candidates: set[tuple[Atom, ...]] = set()
    for slot in range(len(inputs)):
        for first in range(4):
            for second in range(first, 4):
                atoms = [(field, ()) for field in inputs]
                atoms[slot] = (inputs[slot], (first, second))
                canonical, _ = lift._canonical_atoms(atoms)
                if canonical is not None:
                    candidates.add(canonical)
    for left in range(len(inputs)):
        for right in range(left + 1, len(inputs)):
            for first in range(4):
                for second in range(4):
                    atoms = [(field, ()) for field in inputs]
                    atoms[left] = (inputs[left], (first,))
                    atoms[right] = (inputs[right], (second,))
                    canonical, _ = lift._canonical_atoms(atoms)
                    if canonical is not None:
                        candidates.add(canonical)
    return tuple(sorted(candidates))


def scan_second_order(*, stop_at_first: bool = True, progress: int = 250) -> dict[str, object]:
    started = time.monotonic()
    columns = 0
    nonzero: list[dict[str, object]] = []
    labels = connected_base_labels()
    for label_index, (kind, output, inputs) in enumerate(labels):
        for atoms in _second_order_atoms(inputs):
            columns += 1
            pairing = _expanded_column_pairing(
                kind, lift.cotangent_column(output, atoms)
            )
            if pairing:
                nonzero.append(
                    {
                        "kind": kind,
                        "output": output,
                        "atoms": [[field, list(word)] for field, word in atoms],
                        "pairing": str(pairing),
                    }
                )
                if stop_at_first:
                    return {
                        "connected_base_labels": len(labels),
                        "columns_checked": columns,
                        "nonzero_columns": nonzero,
                        "elapsed_seconds": round(time.monotonic() - started, 6),
                    }
        if progress and (label_index + 1) % progress == 0:
            print(
                json.dumps(
                    {
                        "labels_completed": label_index + 1,
                        "columns_checked": columns,
                        "elapsed_seconds": round(time.monotonic() - started, 3),
                        "F2_cache": _unit_f2_pairing.cache_info()._asdict(),
                        "F3_cache": _unit_f3_pairing.cache_info()._asdict(),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    return {
        "connected_base_labels": len(labels),
        "columns_checked": columns,
        "nonzero_columns": nonzero,
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }


def physical_second_correction_pairing(*, progress: int = 100) -> dict[str, object]:
    """Evaluate the exact physical second-jet correction on the full-BV dual."""

    from d_quotient_classical.backreacted_clock import (
        berger_retained_mixed_ell3_second_jet_exact_primitive as physical,
    )

    certificate = json.loads(physical.OUTPUT.read_text())
    records = physical._load_records(certificate)
    connected = set(connected_base_labels())
    selected = []
    for record in records:
        if int(record["jet_order"]) != 2:
            continue
        kind = str(record["arity"])
        output = physical.second.zero.FIELD_ROWS[int(record["output_local"])]
        atoms = tuple(
            (
                physical.second.zero.FIELD_ROWS[int(atom["field_local"])],
                tuple(int(axis) for axis in atom["PBW_word"]),
            )
            for atom in record["input_atoms"]
        )
        if (kind, output, tuple(field for field, _ in atoms)) not in connected:
            continue
        selected.append((record, kind, output, atoms))

    started = time.monotonic()
    total = sp.S.Zero
    nonzero = []
    for index, (record, kind, output, atoms) in enumerate(selected):
        pairing = _expanded_column_pairing(
            kind, lift.cotangent_column(output, atoms)
        )
        if pairing:
            coefficient = physical._scalar(str(record["coefficient"]))
            contribution = sp.factor(coefficient * pairing)
            total += contribution
            nonzero.append(
                {
                    "full_column": int(record["full_column"]),
                    "kind": kind,
                    "output": output,
                    "atoms": [[field, list(word)] for field, word in atoms],
                    "coefficient": str(coefficient),
                    "dual_pairing": str(pairing),
                    "contribution": str(contribution),
                }
            )
        if progress and (index + 1) % progress == 0:
            print(
                json.dumps(
                    {
                        "selected_completed": index + 1,
                        "selected_total": len(selected),
                        "nonzero_contributions": len(nonzero),
                        "elapsed_seconds": round(time.monotonic() - started, 3),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    return {
        "physical_second_records": sum(
            int(record["jet_order"]) == 2 for record in records
        ),
        "field_connected_records": len(selected),
        "nonzero_contributions": nonzero,
        "total_pairing": str(sp.factor(total)),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }


def _add_lifted_base(
    destination: lift.JetTaylor,
    output: int,
    atoms: tuple[Atom, ...],
    coefficient: sp.Expr,
) -> None:
    column = lift.cotangent_column(output, atoms)
    for (new_output, new_atoms), value in column.items():
        lift._add(
            destination,
            new_output,
            new_atoms,
            coefficient * value,
        )


def physical_candidate_maps(*, add_ghost_shears: bool = True) -> tuple[lift.JetTaylor, lift.JetTaylor]:
    """Lift the complete exact physical order-two primitive to the full BV carrier."""

    from d_quotient_classical.backreacted_clock import (
        berger_retained_mixed_ell3_first_jet_redefinition as first,
    )
    from d_quotient_classical.backreacted_clock import (
        berger_retained_mixed_ell3_second_jet_coupled_solver as coupled,
    )
    from d_quotient_classical.backreacted_clock import (
        berger_retained_mixed_ell3_second_jet_exact_primitive as physical,
    )

    first_certificate = json.loads(first.OUTPUT.read_text())
    x0, y0 = first._solution_from_records(first_certificate)
    physical_certificate = json.loads(physical.OUTPUT.read_text())
    records = physical._load_records(physical_certificate)
    dx, dy, sparse = physical._correction(records)
    final_x = x0 + dx
    final_y = [y0[:, axis] + dy[axis] for axis in range(4)]
    f2_map: lift.JetTaylor = {}
    f3_map: lift.JetTaylor = {}

    for column, coefficient in enumerate(final_x):
        if coefficient == 0:
            continue
        kind, output_local, inputs_local = physical.second.zero._labels()[column]
        output = physical.second.zero.FIELD_ROWS[output_local]
        atoms = tuple(
            (physical.second.zero.FIELD_ROWS[field], ())
            for field in inputs_local
        )
        _add_lifted_base(f2_map if kind == "F2" else f3_map, output, atoms, coefficient)

    for axis in range(4):
        for local, coefficient in enumerate(final_y[axis]):
            if coefficient == 0:
                continue
            kind, output_local, atoms_local = coupled._first_label(
                axis, first._positive_labels()[local]
            )
            output = physical.second.zero.FIELD_ROWS[output_local]
            atoms = tuple(
                (physical.second.zero.FIELD_ROWS[field], word)
                for field, word in atoms_local
            )
            _add_lifted_base(f2_map if kind == "F2" else f3_map, output, atoms, coefficient)

    for full_column, coefficient in sparse.items():
        jet_order, (kind, output_local, atoms_local) = physical._label(full_column)
        if jet_order != 2:
            continue
        output = physical.second.zero.FIELD_ROWS[output_local]
        atoms = tuple(
            (physical.second.zero.FIELD_ROWS[field], word)
            for field, word in atoms_local
        )
        _add_lifted_base(f2_map if kind == "F2" else f3_map, output, atoms, coefficient)

    if add_ghost_shears:
        for ghost, potential in ((0, 28), (1, 29), (2, 30)):
            _add_lifted_base(
                f2_map,
                26,
                ((ghost, ()), (potential, ())),
                -sp.S.One,
            )
    return f2_map, f3_map


def physical_candidate_residual(
    *, add_ghost_shears: bool = True, max_page: int = 2
) -> dict[str, object]:
    """Replay the lifted physical primitive against every mixed full-BV page."""

    if max_page not in range(3):
        raise ValueError("max_page must be 0, 1, or 2")

    started = time.monotonic()
    f2_map, f3_map = physical_candidate_maps(add_ghost_shears=add_ghost_shears)
    f2, f3 = core.jet_taylor_vectors(f2_map, f3_map)
    q1, q2, target = core.retained_operations()
    pages = {}
    for page in range(max_page + 1):
        expected = core.page_terms(target, page)
        actual = core.coderivation_coboundary_page_streaming(
            f2, f3, page, q1=q1, q2=q2
        )
        residual = dict(expected)
        for key, coefficient in actual.items():
            value = sp.expand(residual.get(key, 0) - coefficient)
            if value:
                residual[key] = value
            else:
                residual.pop(key, None)
        pages[str(page)] = {
            "target": len(expected),
            "reconstruction": len(actual),
            "residual": len(residual),
            "residual_sample": [
                {
                    "output": key[0],
                    "term": [list(value) if isinstance(value, tuple) else value for value in key[1]],
                    "coefficient": str(sp.factor(coefficient)),
                }
                for key, coefficient in sorted(residual.items())[:10]
            ],
        }
        print(
            json.dumps(
                {
                    "page": page,
                    "target": len(expected),
                    "reconstruction": len(actual),
                    "residual": len(residual),
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    return {
        "ghost_shears_added": add_ghost_shears,
        "max_page_checked": max_page,
        "F2_canonical_components": len(f2_map),
        "F3_canonical_components": len(f3_map),
        "F2_ordered_terms": sum(len(row.terms) for row in f2),
        "F3_ordered_terms": sum(len(row.terms) for row in f3),
        "pages": pages,
        "complete": all(not page["residual"] for page in pages.values()),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--progress", type=int, default=25)
    parser.add_argument("--physical-correction", action="store_true")
    parser.add_argument("--candidate-residual", action="store_true")
    parser.add_argument("--without-ghost-shears", action="store_true")
    parser.add_argument("--max-page", type=int, default=2)
    args = parser.parse_args()
    if args.candidate_residual:
        print(
            json.dumps(
                physical_candidate_residual(
                    add_ghost_shears=not args.without_ghost_shears,
                    max_page=args.max_page,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.physical_correction:
        print(
            json.dumps(
                physical_second_correction_pairing(progress=args.progress),
                indent=2,
                sort_keys=True,
            )
        )
        return
    print(
        json.dumps(
            scan_second_order(
                stop_at_first=not args.all,
                progress=args.progress,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
