#!/usr/bin/env python3
"""Independent telescoping replay of the relative Hessian current cone."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
from itertools import combinations_with_replacement
import json

from d_quotient_classical.relative import einstein_weyl_relative_hessian_green_current_cone as producer


def _load_terms(path, field_start, equation_start, sign):
    content = json.loads(path.read_text())["content"]
    profiles = {
        item["index"]: {tuple(jet["word"]): Fraction(jet["coefficient"]) for jet in item["coefficient_jets"]}
        for item in content.get("coefficient_profiles", [])
    }
    output = []
    for term in content["terms"]:
        incoming = term["inputs"][0]
        if not equation_start <= term["output_row"] < equation_start + 14:
            continue
        if not field_start <= incoming["row"] < field_start + 14:
            continue
        profile = profiles.get(term.get("coefficient_profile"))
        if profile is None:
            profile = {tuple(jet["word"]): Fraction(jet["coefficient"]) for jet in term["coefficient_jets"]}
        output.append((term["output_row"] - equation_start, incoming["row"] - field_start, tuple(incoming["word"]), {word: sign * value for word, value in profile.items()}))
    return output


def _add(table, key, value):
    if value:
        table[key] += value


def _independent_defect(terms):
    left = defaultdict(Fraction)
    right = defaultdict(Fraction)
    for output, incoming, word, profile in terms:
        for position in range(len(word)):
            axis = word[position]
            prefix = word[:position]
            suffix = word[position + 1 :]
            for mask in range(1 << len(prefix)):
                coefficient_word = tuple(sorted(prefix[index] for index in range(len(prefix)) if mask & (1 << index)))
                field_word = tuple(sorted(prefix[index] for index in range(len(prefix)) if not mask & (1 << index)))
                sign = Fraction((-1) ** position)
                _add(left, (output, field_word, incoming, suffix), sign * profile.get(tuple(sorted((*coefficient_word, axis))), 0))
                _add(left, (output, tuple(sorted((*field_word, axis))), incoming, suffix), sign * profile.get(coefficient_word, 0))
                _add(left, (output, field_word, incoming, tuple(sorted((*suffix, axis)))), sign * profile.get(coefficient_word, 0))
        _add(right, (output, (), incoming, word), profile.get((), 0))
        for mask in range(1 << len(word)):
            coefficient_word = tuple(sorted(word[index] for index in range(len(word)) if mask & (1 << index)))
            field_word = tuple(sorted(word[index] for index in range(len(word)) if not mask & (1 << index)))
            _add(right, (output, field_word, incoming, ()), -((-1) ** len(word)) * profile.get(coefficient_word, 0))
    return {key: left[key] - right[key] for key in set(left) | set(right) if left[key] != right[key]}


def _independent_densitize(terms):
    volume = {(): Fraction(1), (2, 2): Fraction(-1), (2, 2, 2, 2): Fraction(1)}
    words = [()]
    for order in range(1, 5):
        words.extend(combinations_with_replacement(range(4), order))
    output = []
    for equation, incoming, word, profile in terms:
        product_profile = defaultdict(Fraction)
        for derivative_word in words:
            for mask in range(1 << len(derivative_word)):
                left_word = tuple(sorted(derivative_word[index] for index in range(len(derivative_word)) if mask & (1 << index)))
                right_word = tuple(sorted(derivative_word[index] for index in range(len(derivative_word)) if not mask & (1 << index)))
                product_profile[derivative_word] += profile.get(left_word, 0) * volume.get(right_word, 0)
        output.append((equation, incoming, word, {key: value for key, value in product_profile.items() if value}))
    return output


def verify() -> dict[str, object]:
    certificate = json.loads(producer.OUTPUT.read_text())
    producer.validate(certificate)
    for name, artifact in certificate["dependencies"].items():
        path = producer.ROOT / artifact["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {name}")
    for relative, expected in certificate["provenance"]["source_manifest"].items():
        if hashlib.sha256((producer.ROOT / relative).read_bytes()).hexdigest() != expected:
            raise AssertionError(f"source manifest mismatch: {relative}")
    terms = _independent_densitize(
        _load_terms(producer.TARGET_Q1, 6, 20, 1)
        + _load_terms(producer.SOURCE_Q1, 5, 19, -1)
    )
    defect = _independent_defect(terms)
    if defect:
        raise AssertionError(f"independent telescoping defect: {next(iter(defect.items()))}")
    generated = json.loads(producer.GENERATED.read_text())
    if generated["term_count"] != 3704:
        raise AssertionError("generated current term count drifted")
    swapped = {
        (term["component"], term["left"]["field"], tuple(term["left"]["word"]), term["right"]["field"], tuple(term["right"]["word"])): Fraction(term["coefficient"])
        for term in generated["terms"]
    }
    for (component, left, left_word, right, right_word), coefficient in swapped.items():
        if swapped.get((component, right, right_word, left, left_word), 0) != -coefficient:
            raise AssertionError("generated current is not antisymmetric")
    adjoint_defect = producer.formal_self_adjoint_defect(terms)
    if adjoint_defect:
        raise AssertionError(f"densitized formal-adjoint defect: {next(iter(adjoint_defect.items()))}")
    return {"status": "PASS", "operator_terms": len(terms), "current_terms": len(swapped), "divergence_defects": 0, "formal_adjoint_defects": 0}


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
