#!/usr/bin/env python3
"""Independent exact replay of the five-current de Rham q2 interface."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json

from d_quotient_classical.relative import einstein_weyl_relative_five_current_de_rham_q2 as producer
from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    polarized_euler_source,
    stabilizer_action,
    stabilizer_vectors,
)
from d_quotient_classical.relative.einstein_weyl_relative_hessian_green_current_cone import (
    relative_operator_terms,
)


def _add(table: dict, key: tuple, value: Fraction) -> None:
    if value:
        table[key] += value


def _dual_action(action: list[tuple]) -> list[tuple]:
    """Separate implementation of minus the first-order density adjoint."""

    table = defaultdict(lambda: defaultdict(Fraction))
    for output, incoming, word, profile in action:
        if not word:
            for jet, value in profile.items():
                _add(table[(incoming, output, ())], jet, -value)
            continue
        axis, = word
        for jet, value in profile.items():
            _add(table[(incoming, output, word)], jet, value)
            if axis in jet:
                reduced = list(jet)
                reduced.remove(axis)
                _add(table[(incoming, output, ())], tuple(reduced), value)
    return [
        (output, incoming, word, {jet: value for jet, value in profile.items() if value})
        for (output, incoming, word), profile in sorted(table.items())
        if any(profile.values())
    ]


def _moment(action: list[tuple]) -> dict:
    table = defaultdict(lambda: defaultdict(Fraction))
    for output, incoming, word, profile in _dual_action(action):
        for jet, value in profile.items():
            _add(table[(incoming, word, output, ())], jet, value / 2)
    for output, incoming, word, profile in action:
        for jet, value in profile.items():
            _add(table[(output, (), incoming, word)], jet, -value / 2)
    return {
        key: {jet: value for jet, value in profile.items() if value}
        for key, profile in table.items()
        if any(profile.values())
    }


def _pull(moment: dict) -> dict:
    by_equation = defaultdict(list)
    for term in relative_operator_terms():
        by_equation[term[0]].append(term)
    one_sided = defaultdict(Fraction)
    for (equation, equation_word, right, right_word), profile in moment.items():
        coefficient = profile.get((), 0)
        for _, field, hessian_word, hessian_profile in by_equation[equation]:
            for mask in range(1 << len(equation_word)):
                coefficient_word = tuple(sorted(
                    equation_word[index] for index in range(len(equation_word)) if mask & (1 << index)
                ))
                extra = tuple(
                    equation_word[index] for index in range(len(equation_word)) if not mask & (1 << index)
                )
                _add(
                    one_sided,
                    (field, tuple(sorted((*hessian_word, *extra))), right, right_word),
                    coefficient * hessian_profile.get(coefficient_word, 0),
                )
    output = defaultdict(Fraction)
    for (left, left_word, right, right_word), value in one_sided.items():
        _add(output, (left, left_word, right, right_word), value)
        _add(output, (right, right_word, left, left_word), value)
    return {key: value for key, value in output.items() if value}


def verify() -> dict[str, object]:
    value = json.loads(producer.OUTPUT.read_text())
    producer.validate(value)
    for name, artifact in value["dependencies"].items():
        path = producer.ROOT / artifact["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {name}")
    for relative, expected in value["provenance"]["source_manifest"].items():
        if hashlib.sha256((producer.ROOT / relative).read_bytes()).hexdigest() != expected:
            raise AssertionError(f"source manifest mismatch: {relative}")
    for name, vector in stabilizer_vectors().items():
        action = stabilizer_action(vector)
        independent_dual = _dual_action(action)
        if independent_dual != producer.density_dual_action(action):
            raise AssertionError(f"density-dual action mismatch: {name}")
        moment = _moment(action)
        if moment != producer.equation_field_moment_map(action):
            raise AssertionError(f"moment-map operation mismatch: {name}")
        pullback = _pull(moment)
        source = polarized_euler_source(action)
        if pullback != source:
            keys = set(pullback) | set(source)
            first = next(key for key in keys if pullback.get(key, 0) != source.get(key, 0))
            raise AssertionError(f"Hessian pullback mismatch {name}: {first}")
        if value["operations"]["generator_records"][name]["hessian_pullback_defect_terms"] != 0:
            raise AssertionError(f"nonzero recorded defect: {name}")
    generated = json.loads(producer.GENERATED.read_text())
    digest = hashlib.sha256((json.dumps(generated, indent=2, sort_keys=True) + "\n").encode()).hexdigest()
    if digest != value["generated_operations"]["sha256"]:
        raise AssertionError("generated operation hash mismatch")
    if set(generated["equation_field_moment_operations"]) != set(stabilizer_vectors()):
        raise AssertionError("generated stabilizer table is incomplete")
    carrier = json.loads((producer.ROOT / value["dependencies"]["de_rham_carrier"]["path"]).read_text())
    layout = json.loads((producer.ROOT / carrier["generated_layout"]["path"]).read_text())
    roles = defaultdict(int)
    for row in layout["rows"]:
        role = {
            ("primal", 3): "field_field_current_output",
            ("primal", 4): "equation_field_moment_output",
            ("cotangent", 1): "field_field_current_cyclic_input",
            ("cotangent", 0): "equation_field_moment_cyclic_input",
        }.get((row["chain"], row["form_degree"]), "zero_q2_row")
        roles[role] += 1
    audit = value["operations"]["carrier_row_audit"]
    if len(layout["rows"]) != audit["row_count"] or dict(roles) != audit["role_counts"]:
        raise AssertionError("independent carrier row-role census mismatch")
    if len({record["row"] for record in audit["records"]}) != 160:
        raise AssertionError("carrier row audit is not exhaustive")
    return {"status": "PASS", "generators": 5, "carrier_rows_audited": 160, "pullback_defects": 0}


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
