#!/usr/bin/env python3
"""Exact order-two local-functional screen for the retained mixed ell3.

The module represents a quartic density by its variational Euler derivative.
This gives a canonical, exact realization of the quotient by total
derivatives while retaining the noncommuting Berger-frame PBW relations.  It
first replays the exported order-one primitive against the complete action
through total PBW order two.  A nonzero result is the source term for the
second-jet redefinition solve; it is not an obstruction verdict by itself.

Dependency tag: LOCAL-ALGEBRAIC.  Generality: G0.
"""

from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Mapping

import sympy as sp
from jsonschema import Draft202012Validator

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_constant_field_redefinition as zero,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_first_jet_redefinition as first,
)
from d_quotient_classical.backreacted_clock import berger_support_local_q2 as engine
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import _pbw_word


ROOT = zero.ROOT
FIRST_CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1.json"
)
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_SOURCE_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-second-jet-source-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-mixed-ell3-second-jet-source.md"

Word = tuple[int, ...]
Atom = tuple[int, Word]
Monomial = tuple[Atom, ...]
Density = dict[Monomial, sp.Expr]
EulerKey = tuple[int, tuple[Atom, Atom, Atom]]
EulerImage = dict[EulerKey, sp.Expr]
FLabel = tuple[str, int, tuple[Atom, ...]]


def _add(value: dict, key: object, coefficient: sp.Expr) -> None:
    updated = sp.expand(value.get(key, 0) + coefficient)
    if updated != 0:
        value[key] = updated
    else:
        value.pop(key, None)


def _word(word: Iterable[int]) -> Word:
    """Convert a four-entry multiindex to its ordered frame word."""

    values = tuple(int(count) for count in word)
    if len(values) != 4 or any(count < 0 for count in values):
        raise ValueError(f"invalid retained PBW multiindex: {values}")
    return tuple(axis for axis, count in enumerate(values) for _ in range(count))


@lru_cache(maxsize=None)
def _canonical_atom_terms(atom: Atom) -> tuple[tuple[Atom, sp.Expr], ...]:
    field, word = atom
    return tuple(((field, reduced), coefficient) for reduced, coefficient in _pbw_word(word))


def _canonical_monomial_terms(atoms: Iterable[Atom]) -> tuple[tuple[Monomial, sp.Expr], ...]:
    states: dict[tuple[Atom, ...], sp.Expr] = {(): sp.Integer(1)}
    for atom in atoms:
        updated: dict[tuple[Atom, ...], sp.Expr] = {}
        for prefix, prefix_coefficient in states.items():
            for reduced, coefficient in _canonical_atom_terms(atom):
                _add(updated, (*prefix, reduced), prefix_coefficient * coefficient)
        states = updated
    combined: dict[Monomial, sp.Expr] = {}
    for value, coefficient in states.items():
        _add(combined, tuple(sorted(value)), coefficient)
    return tuple(sorted(combined.items()))


def _add_density(value: Density, atoms: Iterable[Atom], coefficient: sp.Expr) -> None:
    for monomial, pbw_coefficient in _canonical_monomial_terms(tuple(atoms)):
        _add(value, monomial, coefficient * pbw_coefficient)


def _total_order(monomial: Monomial) -> int:
    return sum(len(word) for _, word in monomial)


def _project_density(density: Mapping[Monomial, sp.Expr], maximum_order: int) -> Density:
    return {
        monomial: coefficient
        for monomial, coefficient in density.items()
        if _total_order(monomial) <= maximum_order
    }


def _project_mixed_density(density: Mapping[Monomial, sp.Expr]) -> Density:
    """Retain precisely the declared two-gravity/two-Maxwell quartic sector."""

    return {
        monomial: coefficient
        for monomial, coefficient in density.items()
        if sum(field in zero.GRAVITY for field, _ in monomial) == 2
        and sum(field in zero.MAXWELL for field, _ in monomial) == 2
    }


def _density_terms(maximum_order: int = 2) -> tuple[Density, Density, Density]:
    """Load the lowered physical S2, S3 and mixed S4 densities."""

    typed = zero._load(zero.TYPED_CARRIER)
    gravity = zero._load(zero.GRAVITY_ELL2)
    mixed2 = zero._load(zero.MIXED_ELL2)
    mixed3 = zero._load(zero.MIXED_ELL3)
    s2: Density = {}
    s3: Density = {}
    s4: Density = {}

    for output, source, terms in typed["retained_complex"]["classical_unary_q1"]["entries"]:
        if output not in zero.PAIRING or source not in zero.FIELD_LOCAL:
            continue
        paired, weight = zero.PAIRING[output]
        for word, coefficient in terms:
            source_word = _word(word)
            if len(source_word) <= maximum_order:
                _add_density(
                    s2,
                    ((paired, ()), (zero.FIELD_LOCAL[source], source_word)),
                    weight * zero._scalar(coefficient),
                )

    for payload in (gravity, mixed2):
        for row in payload["rows"]:
            output = row["output"]
            if output not in zero.PAIRING:
                continue
            paired, weight = zero.PAIRING[output]
            for left, left_word, right, right_word, coefficient in row["terms"]:
                words = (_word(left_word), _word(right_word))
                if (
                    left in zero.FIELD_LOCAL
                    and right in zero.FIELD_LOCAL
                    and sum(map(len, words)) <= maximum_order
                ):
                    _add_density(
                        s3,
                        (
                            (paired, ()),
                            (zero.FIELD_LOCAL[left], words[0]),
                            (zero.FIELD_LOCAL[right], words[1]),
                        ),
                        weight * zero._q10(coefficient),
                    )

    seen: set[int] = set()
    for chunk in mixed3["chunks"]:
        path = ROOT / chunk["path"]
        if zero._sha256(path) != chunk["file_sha256"]:
            raise ValueError(f"retained ell3 row digest drifted: {chunk['output']}")
        with gzip.open(path, "rt") as handle:
            row = json.load(handle)
        output = row["output"]
        if output in seen:
            raise ValueError("duplicate retained ell3 output row")
        seen.add(output)
        if output not in zero.PAIRING:
            continue
        paired, weight = zero.PAIRING[output]
        for first_field, first_word, second_field, second_word, third_field, third_word, coefficient in row["terms"]:
            words = (_word(first_word), _word(second_word), _word(third_word))
            if (
                all(field in zero.FIELD_LOCAL for field in (first_field, second_field, third_field))
                and sum(map(len, words)) <= maximum_order
            ):
                _add_density(
                    s4,
                    (
                        (paired, ()),
                        (zero.FIELD_LOCAL[first_field], words[0]),
                        (zero.FIELD_LOCAL[second_field], words[1]),
                        (zero.FIELD_LOCAL[third_field], words[2]),
                    ),
                    weight * zero._q10(coefficient),
                )
    if seen != set(range(36)):
        raise ValueError("retained ell3 row ledger is incomplete")
    return s2, s3, s4


def euler_image(density: Mapping[Monomial, sp.Expr]) -> EulerImage:
    """Apply the exact variational Euler operator to a quartic density."""

    value: EulerImage = {}
    for atoms, coefficient in density.items():
        if len(atoms) != 4:
            raise ValueError("Euler screen expects quartic densities")
        for atom, multiplicity in Counter(atoms).items():
            field, word = atom
            remaining = list(atoms)
            remaining.remove(atom)
            for first_word, second_word, third_word, leibniz_coefficient in engine._leibniz_adjoint_terms3(
                word, remaining[0][1], remaining[1][1], remaining[2][1]
            ):
                shifted = (
                    (remaining[0][0], first_word),
                    (remaining[1][0], second_word),
                    (remaining[2][0], third_word),
                )
                for cubic, pbw_coefficient in _canonical_monomial_terms(shifted):
                    _add(
                        value,
                        (field, cubic),
                        coefficient * multiplicity * leibniz_coefficient * pbw_coefficient,
                    )
    return value


def _output_derivative_terms(word: Word, atoms: tuple[Atom, ...]) -> tuple[tuple[tuple[Word, ...], int], ...]:
    if len(atoms) == 2:
        return tuple(
            ((left, right), coefficient)
            for left, right, coefficient in engine._leibniz_output_terms(
                word, atoms[0][1], atoms[1][1]
            )
        )
    if len(atoms) == 3:
        return tuple(
            ((first_word, second_word, third_word), coefficient)
            for first_word, second_word, third_word, coefficient in engine._leibniz_output_terms3(
                word, atoms[0][1], atoms[1][1], atoms[2][1]
            )
        )
    raise ValueError("only F2 and F3 are admitted")


def variation(density: Mapping[Monomial, sp.Expr], maps: Mapping[FLabel, sp.Expr]) -> Density:
    """Vary a density by sparse F2/F3 base-field maps."""

    by_output: dict[int, list[tuple[str, tuple[Atom, ...], sp.Expr]]] = {}
    for (arity, output, inputs), map_coefficient in maps.items():
        if arity not in ("F2", "F3") or len(inputs) != int(arity[1]):
            raise ValueError("invalid redefinition label")
        if map_coefficient != 0:
            by_output.setdefault(output, []).append((arity, inputs, map_coefficient))

    value: Density = {}
    for atoms, density_coefficient in density.items():
        for outer, multiplicity in Counter(atoms).items():
            output, outer_word = outer
            if output not in by_output:
                continue
            remaining = list(atoms)
            remaining.remove(outer)
            for _, inputs, map_coefficient in by_output[output]:
                for words, leibniz_coefficient in _output_derivative_terms(outer_word, inputs):
                    inserted = tuple((inputs[index][0], word) for index, word in enumerate(words))
                    _add_density(
                        value,
                        (*remaining, *inserted),
                        density_coefficient * multiplicity * map_coefficient * leibniz_coefficient,
                    )
    return value


def _primitive_maps() -> dict[FLabel, sp.Expr]:
    certificate = zero._load(FIRST_CERTIFICATE)
    x0, y = first._solution_from_records(certificate)
    maps: dict[FLabel, sp.Expr] = {}
    for column, coefficient in enumerate(x0):
        if coefficient == 0:
            continue
        arity, output, inputs = zero._labels()[column]
        maps[(arity, output, tuple((field, ()) for field in inputs))] = coefficient
    for axis in range(4):
        for column, coefficient in enumerate(y[:, axis]):
            if coefficient == 0:
                continue
            arity, output, inputs, derivative_field = first._positive_labels()[column]
            used = False
            atoms: list[Atom] = []
            for field in inputs:
                differentiated = field == derivative_field and not used
                atoms.append((field, (axis,) if differentiated else ()))
                used = used or differentiated
            label = (arity, output, tuple(sorted(atoms)))
            _add(maps, label, coefficient)
    return maps


def _project_maps(maps: Mapping[FLabel, sp.Expr], maximum_order: int) -> dict[FLabel, sp.Expr]:
    return {
        label: coefficient
        for label, coefficient in maps.items()
        if sum(len(word) for _, word in label[2]) <= maximum_order
    }


def _jet_input_monomials(inputs: tuple[int, ...], order: int) -> tuple[tuple[Atom, ...], ...]:
    """Enumerate symmetric PBW input monomials of total order one or two."""

    if order not in (1, 2):
        raise ValueError("only first and second input jets are enumerated")
    values: set[tuple[Atom, ...]] = set()
    if order == 1:
        for slot in range(len(inputs)):
            for axis in range(4):
                atoms = [(field, ()) for field in inputs]
                atoms[slot] = (inputs[slot], (axis,))
                values.add(tuple(sorted(atoms)))
    else:
        for slot in range(len(inputs)):
            for first_axis in range(4):
                for second_axis in range(first_axis, 4):
                    atoms = [(field, ()) for field in inputs]
                    atoms[slot] = (inputs[slot], (first_axis, second_axis))
                    values.add(tuple(sorted(atoms)))
        for left_slot in range(len(inputs)):
            for right_slot in range(left_slot + 1, len(inputs)):
                for left_axis in range(4):
                    for right_axis in range(4):
                        atoms = [(field, ()) for field in inputs]
                        atoms[left_slot] = (inputs[left_slot], (left_axis,))
                        atoms[right_slot] = (inputs[right_slot], (right_axis,))
                        values.add(tuple(sorted(atoms)))
    return tuple(sorted(values))


@lru_cache(maxsize=1)
def second_jet_labels() -> tuple[FLabel, ...]:
    return tuple(
        (arity, output, atoms)
        for arity, output, inputs in zero._labels()
        for atoms in _jet_input_monomials(inputs, 2)
    )


def _subtract(left: Mapping, right: Mapping) -> dict:
    value = dict(left)
    for key, coefficient in right.items():
        _add(value, key, -coefficient)
    return value


def _variation_through_order(
    maximum_order: int,
    maps: Mapping[FLabel, sp.Expr],
) -> tuple[Density, Density, Density, Density]:
    """Vary using pairs whose pre-reduction differential orders sum to the page."""

    target_s2, target_s3, target_s4 = _density_terms(maximum_order)
    varied: Density = {}
    for map_order in range(maximum_order + 1):
        selected = {
            label: coefficient
            for label, coefficient in maps.items()
            if sum(len(word) for _, word in label[2]) == map_order
        }
        if not selected:
            continue
        source_s2, source_s3, _ = _density_terms(maximum_order - map_order)
        for source, arity in ((source_s2, "F3"), (source_s3, "F2")):
            contribution = variation(
                source,
                {label: coefficient for label, coefficient in selected.items() if label[0] == arity},
            )
            for monomial, coefficient in contribution.items():
                _add(varied, monomial, coefficient)
    return (
        target_s2,
        target_s3,
        _project_mixed_density(target_s4),
        _project_mixed_density(_project_density(varied, maximum_order)),
    )


def total_derivative(density: Mapping[Monomial, sp.Expr], axis: int) -> Density:
    """Differentiate a density, with exact PBW reduction on each factor."""

    value: Density = {}
    for atoms, coefficient in density.items():
        for slot in range(len(atoms)):
            shifted = list(atoms)
            shifted[slot] = (atoms[slot][0], (axis, *atoms[slot][1]))
            _add_density(value, shifted, coefficient)
    return value


def exact_data() -> dict[str, object]:
    maps = _primitive_maps()
    controls = {}
    for maximum_order in (0, 1):
        control_maps = _project_maps(maps, maximum_order)
        _, _, s4_control, varied_control = _variation_through_order(
            maximum_order, control_maps
        )
        controls[maximum_order] = euler_image(_subtract(s4_control, varied_control))

    s2, s3, s4, varied = _variation_through_order(2, maps)
    residual = _subtract(s4, varied)
    euler = euler_image(residual)
    residual_by_order = Counter(_total_order(monomial) for monomial in residual)
    euler_by_order = Counter(
        sum(len(word) for _, word in cubic)
        for _, cubic in euler
    )
    return {
        "s2": s2,
        "s3": s3,
        "s4": s4,
        "maps": maps,
        "variation": varied,
        "residual": residual,
        "euler": euler,
        "control_euler": controls,
        "residual_by_order": dict(sorted(residual_by_order.items())),
        "euler_by_order": dict(sorted(euler_by_order.items())),
    }


def _self_tests() -> dict[str, object]:
    base: Density = {
        tuple((field, ()) for field in range(4)): sp.Integer(1),
    }
    first_derivative_checks = 0
    second_derivative_checks = 0
    for axis in range(4):
        if euler_image(total_derivative(base, axis)):
            raise AssertionError("Euler operator did not kill a first total derivative")
        first_derivative_checks += 1
        for second_axis in range(4):
            if euler_image(total_derivative(total_derivative(base, axis), second_axis)):
                raise AssertionError("Euler operator did not kill a second total derivative")
            second_derivative_checks += 1
    return {
        "first_total_derivatives_killed": first_derivative_checks,
        "second_total_derivatives_killed": second_derivative_checks,
        "first_jet_label_count": sum(
            len(_jet_input_monomials(inputs, 1))
            for _, _, inputs in zero._labels()
        ),
        "second_jet_label_count": len(second_jet_labels()),
    }


def _euler_records(image: Mapping[EulerKey, sp.Expr]) -> list[dict[str, object]]:
    return [
        {
            "varied_field": field,
            "cubic": [[item, list(word)] for item, word in cubic],
            "coefficient": str(sp.factor(coefficient)),
        }
        for (field, cubic), coefficient in sorted(image.items())
    ]


def _records_sha256(records: object) -> str:
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def certificate() -> dict[str, object]:
    tests = _self_tests()
    data = exact_data()
    records = _euler_records(data["euler"])
    return {
        "artifact_id": "BERGER_RETAINED_MIXED_ELL3_SECOND_JET_SOURCE_V1",
        "schema_version": "berger-retained-mixed-ell3-second-jet-source-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality": "G0",
        "status": "SOURCE_COMPUTED_SOLVE_PENDING",
        "dependency_refs": {
            str(path.relative_to(ROOT)): zero._sha256(path)
            for path in (
                zero.TYPED_CARRIER,
                zero.GRAVITY_ELL2,
                zero.MIXED_ELL2,
                zero.MIXED_ELL3,
                FIRST_CERTIFICATE,
            )
        },
        "quotient": {
            "method": "variational Euler image after exact Berger PBW reduction",
            "summed_pre_reduction_order": 2,
            "mixed_sector": "two gravity and two Maxwell base fields",
            "first_total_derivative_mutations_killed": tests["first_total_derivatives_killed"],
            "second_total_derivative_mutations_killed": tests["second_total_derivatives_killed"],
        },
        "reproduction": {
            "zero_page_euler_terms": len(data["control_euler"][0]),
            "first_page_euler_terms": len(data["control_euler"][1]),
        },
        "order_two_source": {
            "S2_density_terms_through_order_two": len(data["s2"]),
            "S3_density_terms_through_order_two": len(data["s3"]),
            "S4_density_terms_through_order_two": len(data["s4"]),
            "exported_lower_primitive_map_terms": len(data["maps"]),
            "variation_terms_after_mixed_projection": len(data["variation"]),
            "residual_density_terms_by_PBW_order": {
                str(key): value for key, value in data["residual_by_order"].items()
            },
            "Euler_terms_by_PBW_order": {
                str(key): value for key, value in data["euler_by_order"].items()
            },
            "Euler_records_sha256": _records_sha256(records),
            "first_Euler_record": records[0],
        },
        "second_jet_ansatz": {
            "symmetric_PBW_label_count": tests["second_jet_label_count"],
            "first_jet_enumeration_control_count": tests["first_jet_label_count"],
        },
        "claim_flags": {
            "LOWER_PAGES_REPRODUCED": True,
            "ORDER_TWO_SOURCE_COMPUTED": True,
            "ORDER_TWO_PRIMITIVE_COMPUTED": False,
            "ORDER_TWO_OBSTRUCTION_PROVED": False,
            "FULL_BV_REDEFINITION_MATCHED": False,
            "CYCLIC_DEFORMATION_CLASS_DECIDED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "SOLVE_155640_COLUMN_SECOND_JET_AFFINE_SYSTEM_THEN_LIFT_TO_FULL_BV",
        "claim_boundary": "This LOCAL-ALGEBRAIC G0 certificate constructs the exact mixed physical-action order-two source in the variational Euler quotient, reproduces the frozen lower pages, and enumerates the complete symmetric second-input-jet ansatz. The nonzero source is not an obstruction: compatibility with the second-jet image has not yet been decided. It does not match the positive-jet ghost/antifield completion, decide a cyclic deformation class, descend to residual cohomology, or make a quantum claim.",
    }


def validate(value: Mapping[str, object], *, replay: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    if flags["LOWER_PAGES_REPRODUCED"] is not True or flags["ORDER_TWO_SOURCE_COMPUTED"] is not True:
        raise ValueError("source claim flags drifted")
    if any(
        flags[name] is not False
        for name in flags
        if name not in ("LOWER_PAGES_REPRODUCED", "ORDER_TWO_SOURCE_COMPUTED")
    ):
        raise ValueError("fail-closed claim flags drifted")
    if not replay:
        return
    expected = certificate()
    if value != expected:
        raise ValueError("second-jet source certificate replay drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    tests = _self_tests()
    data = exact_data()
    summary = {
        "density_terms": {
            "S2": len(data["s2"]),
            "S3": len(data["s3"]),
            "S4": len(data["s4"]),
        },
        "primitive_map_terms": len(data["maps"]),
        "variation_terms": len(data["variation"]),
        "residual_terms_by_order": data["residual_by_order"],
        "euler_terms_by_order": data["euler_by_order"],
        "existing_order_one_primitive_closes_order_two": not data["euler"],
        "lower_page_euler_terms": {
            str(order): len(image) for order, image in data["control_euler"].items()
        },
        "scope": "all action/redefinition pairs of summed pre-reduction differential order at most two, followed by exact Berger PBW reduction and Euler quotient",
        "self_tests": tests,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.check and any(data["control_euler"].values()):
        raise SystemExit("exported primitive failed a frozen lower-page replay")
    if args.write:
        OUTPUT.write_text(json.dumps(certificate(), indent=2, sort_keys=True) + "\n")
    if args.check and OUTPUT.exists():
        validate(json.loads(OUTPUT.read_text()))


if __name__ == "__main__":
    main()
