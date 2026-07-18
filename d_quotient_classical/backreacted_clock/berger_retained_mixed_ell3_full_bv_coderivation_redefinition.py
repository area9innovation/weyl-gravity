#!/usr/bin/env python3
"""Exact zero-jet full-BV coderivation redefinition preflight for mixed ell3.

Unlike the physical-action screens, this consumer works directly with Taylor
maps in the suspended graded-symmetric convention.  Degree-zero base-field
and ghost redefinitions are extended with the certified super-cotangent rule,
then the arity-three coboundary ``[ell1,F3]+[ell2,F2]`` is assembled exactly.
The current CLI is exploratory and does not emit a scientific certificate.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import time
from typing import Iterable, Mapping

import sympy as sp
from jsonschema import Draft202012Validator
from sympy.polys.matrices import DomainMatrix

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_constant_field_redefinition as zero,
)


ROOT = zero.ROOT
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_ZERO_JET_FULL_BV_REDEFINITION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-zero-jet-full-bv-redefinition-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-mixed-ell3-zero-jet-full-bv-redefinition.md"
VERIFIER = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_zero_jet_full_bv_redefinition.py"
TESTS = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retained_mixed_ell3_zero_jet_full_bv_redefinition.py"
LEGACY = zero._load(zero.LEGACY_CARRIER)
DEGREES = tuple(row["degree"] for row in LEGACY["retained_complex"]["component_rows"])
PARITIES = tuple(degree & 1 for degree in DEGREES)
MATTER = tuple(int(row >= 26) for row in range(36))
BASE_ROWS = tuple(row for row in range(36) if DEGREES[row] in (-1, 0))

TYPED = zero._load(zero.TYPED_CARRIER)
PARTNER = {
    left: right
    for left, right, terms in TYPED["retained_complex"]["typed_cyclic_pairing"]["entries"]
    if len(terms) == 1 and not any(terms[0][0])
}
if set(PARTNER) != set(range(36)) or any(PARTNER[PARTNER[row]] != row for row in range(36)):
    raise ValueError("retained Darboux partner ledger drifted")
PAIRING_WEIGHT = {
    row: abs(
        zero._scalar(terms[0][1])
    )
    for row, partner, terms in TYPED["retained_complex"]["typed_cyclic_pairing"]["entries"]
}
if set(PAIRING_WEIGHT) != set(range(36)) or any(not value for value in PAIRING_WEIGHT.values()):
    raise ValueError("retained typed-pairing weight ledger drifted")

Key = tuple[int, tuple[int, ...]]
Taylor = dict[Key, sp.Expr]
WITNESS_KEY: Key = (23, (1, 30, 35))


def _canonical(inputs: Iterable[int]) -> tuple[tuple[int, ...] | None, int]:
    values = tuple(inputs)
    exponent = sum(
        PARITIES[values[left]] * PARITIES[values[right]]
        for left in range(len(values))
        for right in range(left + 1, len(values))
        if values[left] > values[right]
    )
    key = tuple(sorted(values))
    if any(
        key[index] == key[index + 1] and PARITIES[key[index]]
        for index in range(len(key) - 1)
    ):
        return None, 0
    return key, -1 if exponent & 1 else 1


def _add(value: Taylor, output: int, inputs: Iterable[int], coefficient: sp.Expr) -> None:
    canonical, sign = _canonical(inputs)
    if canonical is None:
        return
    key = (output, canonical)
    updated = sp.expand(value.get(key, 0) + sign * coefficient)
    if updated:
        value[key] = updated
    else:
        value.pop(key, None)


def _get(value: Mapping[Key, sp.Expr], output: int, inputs: Iterable[int]) -> sp.Expr:
    canonical, sign = _canonical(inputs)
    return sp.Integer(0) if canonical is None else sign * value.get((output, canonical), 0)


def _zero_word(word: Iterable[int]) -> bool:
    return not any(word)


def _orbit_size(inputs: Iterable[int]) -> int:
    """Number of distinct ordered slots represented by one symmetric key."""

    values = tuple(inputs)
    result = sp.factorial(len(values))
    for row in set(values):
        result //= sp.factorial(values.count(row))
    return int(result)


def retained_maps_zero() -> tuple[Taylor, Taylor, Taylor]:
    q1: Taylor = {}
    q2: Taylor = {}
    q3: Taylor = {}
    for output, source, terms in TYPED["retained_complex"]["classical_unary_q1"]["entries"]:
        for word, coefficient in terms:
            if _zero_word(word):
                _add(q1, output, (source,), zero._scalar(coefficient))
    for payload in (zero._load(zero.GRAVITY_ELL2), zero._load(zero.MIXED_ELL2)):
        for row in payload["rows"]:
            for left, left_word, right, right_word, coefficient in row["terms"]:
                if _zero_word(left_word) and _zero_word(right_word):
                    inputs = (left, right)
                    _add(
                        q2,
                        row["output"],
                        inputs,
                        zero._q10(coefficient) / _orbit_size(inputs),
                    )
    payload = zero._load(zero.MIXED_ELL3)
    for chunk in payload["chunks"]:
        path = ROOT / chunk["path"]
        if zero._sha256(path) != chunk["file_sha256"]:
            raise ValueError("retained ell3 row digest drifted")
        with gzip.open(path, "rt") as handle:
            row = json.load(handle)
        for first, first_word, second, second_word, third, third_word, coefficient in row["terms"]:
            if all(_zero_word(word) for word in (first_word, second_word, third_word)):
                inputs = (first, second, third)
                _add(
                    q3,
                    row["output"],
                    inputs,
                    zero._q10(coefficient) / _orbit_size(inputs),
                )
    return q1, q2, q3


def _base_labels(arity: int) -> tuple[tuple[int, tuple[int, ...]], ...]:
    labels = []
    for output in BASE_ROWS:
        for inputs in itertools.combinations_with_replacement(BASE_ROWS, arity):
            if any(PARITIES[row] and inputs.count(row) > 1 for row in set(inputs)):
                continue
            if sum(DEGREES[row] for row in inputs) != DEGREES[output]:
                continue
            if (MATTER[output] + sum(MATTER[row] for row in inputs)) & 1:
                continue
            labels.append((output, inputs))
    return tuple(labels)


LABELS2 = _base_labels(2)
LABELS3 = _base_labels(3)
PHYSICAL_LABELS2 = tuple(
    label
    for label in LABELS2
    if DEGREES[label[0]] == 0 and all(DEGREES[row] == 0 for row in label[1])
)
PHYSICAL_LABELS3 = tuple(
    label
    for label in LABELS3
    if DEGREES[label[0]] == 0 and all(DEGREES[row] == 0 for row in label[1])
)


def cotangent_column(output: int, inputs: tuple[int, ...]) -> Taylor:
    """Extend one base Taylor coefficient by the certified super-cotangent rule."""

    value: Taylor = {}
    _add(value, output, inputs, sp.Integer(1))
    for input_row in sorted(set(inputs)):
        remaining = list(inputs)
        remaining.remove(input_row)
        coefficient = (
            -(-1 if PARITIES[input_row] else 1)
            * PAIRING_WEIGHT[output]
            / PAIRING_WEIGHT[input_row]
        )
        _add(
            value,
            PARTNER[input_row],
            (PARTNER[output], *remaining),
            coefficient,
        )
    return value


UNSHUFFLES = (((0, 1), 2), ((0, 2), 1), ((1, 2), 0))


def _unshuffle_sign(inputs: tuple[int, int, int], pair: tuple[int, int]) -> int:
    selected = set(pair)
    exponent = sum(
        PARITIES[inputs[earlier]] * PARITIES[inputs[later]]
        for later in pair
        for earlier in range(later)
        if earlier not in selected
    )
    return -1 if exponent & 1 else 1


def _candidate_keys(q1: Taylor, q2: Taylor, f2: Taylor, f3: Taylor) -> set[Key]:
    candidates: set[Key] = set()
    q1_by_source: dict[int, list[int]] = defaultdict(list)
    q2_by_input: dict[int, list[tuple[int, tuple[int, int]]]] = defaultdict(list)
    q2_by_output: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for (output, (source,)), coefficient in q1.items():
        if coefficient:
            q1_by_source[source].append(output)
    for (output, inputs), coefficient in q2.items():
        if coefficient:
            q2_by_output[output].append(inputs)
            for row in set(inputs):
                q2_by_input[row].append((output, inputs))
    for (middle, inputs), coefficient in f3.items():
        if not coefficient:
            continue
        for output in q1_by_source[middle]:
            _candidate_add(candidates, output, inputs)
        for position, row in enumerate(inputs):
            for (new_row, (source,)), qcoefficient in q1.items():
                if new_row == row and qcoefficient:
                    replaced = list(inputs)
                    replaced[position] = source
                    _candidate_add(candidates, middle, replaced)
    for (middle, pair), coefficient in f2.items():
        if not coefficient:
            continue
        for output, qinputs in q2_by_input[middle]:
            remaining = list(qinputs)
            remaining.remove(middle)
            _candidate_add(candidates, output, (*pair, remaining[0]))
        for position, row in enumerate(pair):
            for qinputs in q2_by_output.get(row, ()):
                remaining = pair[1 - position]
                _candidate_add(candidates, middle, (*qinputs, remaining))
    return candidates


def _candidate_add(candidates: set[Key], output: int, inputs: Iterable[int]) -> None:
    canonical, _ = _canonical(inputs)
    if canonical is not None:
        candidates.add((output, canonical))


def coboundary(q1: Taylor, q2: Taylor, f2: Taylor, f3: Taylor) -> Taylor:
    result: Taylor = {}
    for output, inputs in _candidate_keys(q1, q2, f2, f3):
        post = sum(
            _get(q1, output, (middle,)) * _get(f3, middle, inputs)
            for middle in range(36)
        )
        pre = sp.Integer(0)
        for position in range(3):
            sign = -1 if sum(PARITIES[inputs[index]] for index in range(position)) & 1 else 1
            for middle in range(36):
                replaced = list(inputs)
                replaced[position] = middle
                pre += sign * _get(f3, output, replaced) * _get(q1, middle, (inputs[position],))
        binary_post = sp.Integer(0)
        binary_pre = sp.Integer(0)
        for pair, remainder in UNSHUFFLES:
            sign = _unshuffle_sign(inputs, pair)
            pair_inputs = (inputs[pair[0]], inputs[pair[1]])
            direct = inputs[remainder]
            for middle in range(36):
                binary_post += sign * _get(q2, output, (middle, direct)) * _get(f2, middle, pair_inputs)
                binary_pre += sign * _get(f2, output, (middle, direct)) * _get(q2, middle, pair_inputs)
        coefficient = sp.expand(post - pre + binary_post - binary_pre)
        if coefficient:
            result[(output, inputs)] = coefficient
    return result


def coboundary_at(
    q1: Taylor,
    q2: Taylor,
    f2: Taylor,
    f3: Taylor,
    key: Key,
) -> sp.Expr:
    """Evaluate one arity-three coefficient without assembling its column."""

    output, inputs = key
    post = sum(
        _get(q1, output, (middle,)) * _get(f3, middle, inputs)
        for middle in range(36)
    )
    pre = sp.Integer(0)
    for position in range(3):
        sign = -1 if sum(PARITIES[inputs[index]] for index in range(position)) & 1 else 1
        for middle in range(36):
            replaced = list(inputs)
            replaced[position] = middle
            pre += sign * _get(f3, output, replaced) * _get(
                q1, middle, (inputs[position],)
            )
    binary_post = sp.Integer(0)
    binary_pre = sp.Integer(0)
    for pair, remainder in UNSHUFFLES:
        sign = _unshuffle_sign(inputs, pair)
        pair_inputs = (inputs[pair[0]], inputs[pair[1]])
        direct = inputs[remainder]
        for middle in range(36):
            binary_post += sign * _get(q2, output, (middle, direct)) * _get(
                f2, middle, pair_inputs
            )
            binary_pre += sign * _get(f2, output, (middle, direct)) * _get(
                q2, middle, pair_inputs
            )
    return sp.expand(post - pre + binary_post - binary_pre)


def cyclicity_defects(value: Mapping[Key, sp.Expr]) -> Taylor:
    """Return the certified suspended-Darboux first-slot transpose defect."""

    defects: Taylor = {}
    for (output, inputs), coefficient in value.items():
        paired_output = PARTNER[output]
        first = inputs[0]
        transposed_output = PARTNER[first]
        exponent = (
            PARITIES[first] * PARITIES[paired_output]
            + int(DEGREES[first] == 2)
            + int(DEGREES[paired_output] == 2)
        ) & 1
        predicted = (
            (-1 if exponent else 1)
            * PAIRING_WEIGHT[output]
            / PAIRING_WEIGHT[first]
            * coefficient
        )
        actual = _get(
            value,
            transposed_output,
            (paired_output, *inputs[1:]),
        )
        difference = sp.expand(actual - predicted)
        if difference:
            defects[(output, inputs)] = difference
    return defects


def _lowered_maxwell_count(key: Key) -> int:
    output, inputs = key
    return MATTER[PARTNER[output]] + sum(MATTER[row] for row in inputs)


def exact_matrix() -> dict[str, object]:
    q1, q2, target = retained_maps_zero()
    if cyclicity_defects(target):
        raise ValueError("zero-jet retained ell3 target lost full-BV cyclicity")
    columns: list[Taylor] = []
    for output, inputs in PHYSICAL_LABELS2:
        column = coboundary(q1, q2, cotangent_column(output, inputs), {})
        if cyclicity_defects(column):
            raise ValueError(f"F2 cotangent column lost cyclicity: {(output, inputs)}")
        columns.append(column)
    for output, inputs in PHYSICAL_LABELS3:
        column = coboundary(q1, q2, {}, cotangent_column(output, inputs))
        if cyclicity_defects(column):
            raise ValueError(f"F3 cotangent column lost cyclicity: {(output, inputs)}")
        columns.append(column)
    if {_lowered_maxwell_count(key) for key in target} != {2}:
        raise ValueError("retained target left the two-Maxwell deformation sector")
    row_basis = tuple(
        sorted(
            key
            for key in set(target).union(*(set(column) for column in columns))
            if _lowered_maxwell_count(key) == 2
        )
    )
    row_index = {key: row for row, key in enumerate(row_basis)}
    entries = {
        (row_index[key], column): coefficient
        for column, value in enumerate(columns)
        for key, coefficient in value.items()
        if key in row_index
    }
    return {
        "matrix": sp.MutableSparseMatrix(len(row_basis), len(columns), entries),
        "target": sp.Matrix([target.get(key, 0) for key in row_basis]),
        "row_basis": row_basis,
        "labels": (
            *(("F2", *label) for label in PHYSICAL_LABELS2),
            *(("F3", *label) for label in PHYSICAL_LABELS3),
        ),
        "target_map": target,
    }


def target_component(data: Mapping[str, object]) -> dict[str, object]:
    matrix = data["matrix"]
    target = data["target"]
    row_to_columns: dict[int, set[int]] = defaultdict(set)
    column_to_rows: dict[int, set[int]] = defaultdict(set)
    for (row, column), coefficient in matrix.todok().items():
        if coefficient:
            row_to_columns[row].add(column)
            column_to_rows[column].add(row)
    rows = {row for row, coefficient in enumerate(target) if coefficient}
    columns: set[int] = set()
    queue = deque(("row", row) for row in rows)
    while queue:
        kind, index = queue.popleft()
        if kind == "row":
            for column in row_to_columns[index] - columns:
                columns.add(column)
                queue.append(("column", column))
        else:
            for row in column_to_rows[index] - rows:
                rows.add(row)
                queue.append(("row", row))
    selected_rows = tuple(sorted(rows))
    selected_columns = tuple(sorted(columns))
    return {
        "rows": selected_rows,
        "columns": selected_columns,
        "matrix": matrix[list(selected_rows), list(selected_columns)],
        "target": target[list(selected_rows), :],
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def witness_replay() -> dict[str, object]:
    q1, q2, target = retained_maps_zero()
    if cyclicity_defects(target):
        raise ValueError("zero-jet retained target lost full-BV cyclicity")
    target_coefficient = target.get(WITNESS_KEY, 0)
    expected = sp.Rational(3, 10) * sp.sqrt(10)
    if sp.expand(target_coefficient - expected):
        raise ValueError("normalized zero-jet BV target witness drifted")
    nonzero_columns = []
    for kind, labels in (("F2", PHYSICAL_LABELS2), ("F3", PHYSICAL_LABELS3)):
        for index, (output, inputs) in enumerate(labels):
            lift = cotangent_column(output, inputs)
            coefficient = coboundary_at(
                q1,
                q2,
                lift if kind == "F2" else {},
                lift if kind == "F3" else {},
                WITNESS_KEY,
            )
            if coefficient:
                nonzero_columns.append((kind, index, output, inputs, coefficient))
    if nonzero_columns:
        raise ValueError(f"dual witness does not annihilate the ansatz: {nonzero_columns[:1]}")
    dual_weight = sp.sqrt(10) / 3
    if sp.expand(dual_weight * target_coefficient - 1):
        raise ValueError("dual witness normalization failed")
    cross_lift = cotangent_column(3, (27, 27))
    if cross_lift.get((31, (13, 27))) != -sp.Rational(1, 2):
        raise ValueError("typed half-weight cotangent carrier drifted")
    return {
        "target_key": {
            "output": WITNESS_KEY[0],
            "inputs": list(WITNESS_KEY[1]),
            "output_degree": DEGREES[WITNESS_KEY[0]],
            "input_degrees": [DEGREES[row] for row in WITNESS_KEY[1]],
            "lowered_Maxwell_count": _lowered_maxwell_count(WITNESS_KEY),
        },
        "target_coefficient": str(target_coefficient),
        "normalized_dual_weight": str(dual_weight),
        "normalized_target_evaluation": "1",
        "annihilated_F2_columns": len(PHYSICAL_LABELS2),
        "annihilated_F3_columns": len(PHYSICAL_LABELS3),
        "typed_half_weight_control": {
            "base": "F2^3(27,27)=1",
            "dual": "F2^31(13,27)=-1/2",
        },
    }


def _dependency(path: Path, artifact_id: str) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def exhaustive_build() -> dict[str, object]:
    started = time.monotonic()
    data = exact_matrix()
    component = target_component(data)
    matrix = component["matrix"]
    target = component["target"]
    rank = DomainMatrix.from_Matrix(matrix).rank()
    augmented_rank = DomainMatrix.from_Matrix(matrix.row_join(target)).rank()
    physical_rows = tuple(
        local_row
        for local_row, global_row in enumerate(component["rows"])
        if DEGREES[data["row_basis"][global_row][0]] == 1
        and tuple(DEGREES[row] for row in data["row_basis"][global_row][1])
        == (0, 0, 0)
    )
    physical_matrix = matrix[list(physical_rows), :]
    physical_target = target[list(physical_rows), :]
    physical_rank = DomainMatrix.from_Matrix(physical_matrix).rank()
    physical_augmented_rank = DomainMatrix.from_Matrix(
        physical_matrix.row_join(physical_target)
    ).rank()
    replay = witness_replay()
    if (rank, augmented_rank, physical_rank, physical_augmented_rank) != (
        129,
        130,
        66,
        66,
    ):
        raise ValueError("zero-jet full-BV rank ledger drifted")
    dependencies = {
        "typed_carrier": (zero.TYPED_CARRIER, "BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR"),
        "legacy_layout": (zero.LEGACY_CARRIER, "BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR"),
        "gravity_ell2": (zero.GRAVITY_ELL2, "BERGER_RETAINED_26_Q2_PAYLOAD"),
        "mixed_ell2": (zero.MIXED_ELL2, "BERGER_RETAINED_TYPED_MIXED_ELL2_PAYLOAD"),
        "mixed_ell3": (zero.MIXED_ELL3, "BERGER_RETAINED_MIXED_ELL3_PAYLOAD"),
        "cotangent_convention": (
            ROOT / "d_quotient_classical/certificates/BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json",
            "BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1",
        ),
    }
    value = {
        "schema": "pure-weyl-berger-retained-mixed-ell3-zero-jet-full-bv-redefinition-v1",
        "result_id": "BERGER_RETAINED_MIXED_ELL3_ZERO_JET_FULL_BV_REDEFINITION_V1",
        "result_state": "ZERO_JET_FULL_BV_PHYSICAL_COTANGENT_SUBCOMPLEX_OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G0",
        "dependency_refs": {
            name: _dependency(path, artifact_id)
            for name, (path, artifact_id) in dependencies.items()
        },
        "ansatz": {
            "F2_physical_base_coefficients": len(PHYSICAL_LABELS2),
            "F3_physical_base_coefficients": len(PHYSICAL_LABELS3),
            "typed_super_cotangent_completion": True,
            "nonlinear_ghost_coordinate_redefinitions_included": False,
            "PBW_positive_jet_redefinitions_included": False,
        },
        "exact_matrix_audit": {
            "two_Maxwell_matrix_shape": list(data["matrix"].shape),
            "two_Maxwell_matrix_nonzero_entries": len(data["matrix"].todok()),
            "target_connected_shape": list(matrix.shape),
            "target_connected_nonzero_entries": len(matrix.todok()),
            "rank": rank,
            "augmented_rank": augmented_rank,
            "target_compatible": False,
            "physical_projection_shape": list(physical_matrix.shape),
            "physical_projection_rank": physical_rank,
            "physical_projection_augmented_rank": physical_augmented_rank,
            "physical_projection_target_compatible": True,
            "target_zero_jet_canonical_Taylor_coefficients": len(data["target_map"]),
            "elapsed_seconds": round(time.monotonic() - started, 6),
        },
        "normalized_dual_witness": replay,
        "claim_flags": {
            "ZERO_JET_FULL_BV_PHYSICAL_COTANGENT_SUBCOMPLEX_OBSTRUCTED": True,
            "FULL_JET_BOUNDED_CYCLIC_DEFORMATION_CLASS_DECIDED": False,
            "POSITIVE_JET_REDEFINITIONS_EXCLUDED": False,
            "NONLINEAR_GHOST_REDEFINITIONS_EXCLUDED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_MIXED_ELL3_PBW_ORDER_TWO_FULL_BV_REDEFINITION_V1",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha256(path)
            for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
        },
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_full_bv_coderivation_redefinition.py --check",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_zero_jet_full_bv_redefinition.py",
            "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_zero_jet_full_bv_redefinition -v",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_full_bv_coderivation_redefinition.py --write-exhaustive",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-mixed-ell3-zero-jet-full-bv-redefinition-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_ZERO_JET_FULL_BV_REDEFINITION_V1.json",
        ],
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC G0 result proves that the two-Maxwell zero-PBW "
            "Taylor component of the complete retained BV ell3 is not in the image "
            "of zero-jet degree-zero physical base-field F2/F3 redefinitions with "
            "their certified typed super-cotangent completion. The normalized witness "
            "is a single ghost/antifield coefficient and the separately projected "
            "degree-zero physical action remains compatible. This is not a nontrivial "
            "cyclic deformation class: positive-jet redefinitions can feed this PBW "
            "page, nonlinear ghost-coordinate redefinitions were not admitted, total "
            "PBW order two remains open, and no quantum claim is made."
        ),
    }
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    return value


def fast_validate(value: Mapping[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["normalized_dual_witness"] != witness_replay():
        raise ValueError("normalized dual witness replay drifted")
    for dependency in value["dependency_refs"].values():
        if _sha256(ROOT / dependency["path"]) != dependency["sha256"]:
            raise ValueError(f"dependency hash drifted: {dependency['path']}")
    for relative, expected in value["source_manifest"].items():
        if _sha256(ROOT / relative) != expected:
            raise ValueError(f"source hash drifted: {relative}")


def explore() -> dict[str, object]:
    data = exact_matrix()
    component = target_component(data)
    matrix = data["matrix"]
    return {
        "convention_dependency": "BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1",
        "ansatz_counts": {"F2": len(PHYSICAL_LABELS2), "F3": len(PHYSICAL_LABELS3)},
        "target_zero_jet_Taylor_coefficients": len(data["target_map"]),
        "full_matrix_shape": list(matrix.shape),
        "full_matrix_nonzero_entries": len(matrix.todok()),
        "target_component_shape": list(component["matrix"].shape),
        "target_component_nonzero_entries": len(component["matrix"].todok()),
        "claim_boundary": "Exploratory exact coderivation matrix only; no rank, primitive, obstruction or deformation-class claim.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--explore", action="store_true")
    parser.add_argument("--write-exhaustive", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write_exhaustive:
        value = exhaustive_build()
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        print("BERGER_RETAINED_MIXED_ELL3_ZERO_JET_FULL_BV_REDEFINITION_V1: PASS")
    elif args.check:
        fast_validate(json.loads(OUTPUT.read_text()))
        print("BERGER_RETAINED_MIXED_ELL3_ZERO_JET_FULL_BV_REDEFINITION_V1: PASS")
    elif args.explore:
        print(json.dumps(explore(), indent=2, sort_keys=True))
    else:
        parser.error("select --explore, --write-exhaustive, or --check")


if __name__ == "__main__":
    main()
