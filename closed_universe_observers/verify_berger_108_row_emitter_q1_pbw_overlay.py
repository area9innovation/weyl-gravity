#!/usr/bin/env python3
"""Independently verify the scalar massive-emitter q1 PBW overlay."""

import hashlib
import json
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_EMITTER_Q1_PBW_OVERLAY.json"
SCHEMA = P / "schema/berger-108-row-emitter-q1-pbw-overlay-v1.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


SQRT10 = sp.sqrt(10)
ETA = (-1, 1, 1, 1)


def form_basis(degree):
    return tuple(combinations(range(4), degree))


def oriented_component(indices, basis):
    if len(set(indices)) != len(indices):
        return None
    inversions = sum(
        indices[left] > indices[right]
        for left in range(len(indices))
        for right in range(left + 1, len(indices))
    )
    return basis.index(tuple(sorted(indices))), (-1 if inversions % 2 else 1)


def bracket(first, second):
    table = {
        (1, 2): {3: 3 * SQRT10 / 20}, (2, 1): {3: -3 * SQRT10 / 20},
        (2, 3): {1: 2 * SQRT10 / 3}, (3, 2): {1: -2 * SQRT10 / 3},
        (3, 1): {2: 2 * SQRT10 / 3}, (1, 3): {2: -2 * SQRT10 / 3},
    }
    return table.get((first, second), {})


@lru_cache(maxsize=None)
def pbw(word):
    inversion = next((index for index in range(len(word) - 1) if word[index] > word[index + 1]), None)
    if inversion is None:
        return ((word, sp.Integer(1)),)
    left, right = word[inversion], word[inversion + 1]
    output = defaultdict(lambda: sp.Integer(0))
    swapped = word[:inversion] + (right, left) + word[inversion + 2 :]
    for reduced, coefficient in pbw(swapped):
        output[reduced] += coefficient
    for target, structure_coefficient in bracket(left, right).items():
        shorter = word[:inversion] + (target,) + word[inversion + 2 :]
        for reduced, coefficient in pbw(shorter):
            output[reduced] += structure_coefficient * coefficient
    return tuple((key, sp.simplify(value)) for key, value in sorted(output.items()) if sp.simplify(value) != 0)


def normalize(raw_terms):
    output = defaultdict(lambda: sp.Integer(0))
    for row, column, word, coefficient in raw_terms:
        for reduced, pbw_coefficient in pbw(tuple(word)):
            output[row, column, reduced] += coefficient * pbw_coefficient
    return {
        key: sp.simplify(value)
        for key, value in output.items()
        if sp.simplify(value) != 0
    }


def exterior(degree):
    source, target = form_basis(degree), form_basis(degree + 1)
    raw = []
    for row, output_indices in enumerate(target):
        for position, axis in enumerate(output_indices):
            component = oriented_component(output_indices[:position] + output_indices[position + 1 :], source)
            if component is not None:
                column, orientation = component
                raw.append((row, column, (axis,), (-1) ** position * orientation))
        for left in range(len(output_indices)):
            for right in range(left + 1, len(output_indices)):
                first, second = output_indices[left], output_indices[right]
                remainder = tuple(
                    output_indices[index]
                    for index in range(len(output_indices))
                    if index not in (left, right)
                )
                for target_axis, coefficient in bracket(first, second).items():
                    component = oriented_component((target_axis, *remainder), source)
                    if component is not None:
                        column, orientation = component
                        raw.append((row, column, (), (-1) ** (left + right) * orientation * coefficient))
    return normalize(raw)


def adjoint(operator, source_degree, target_degree):
    source, target = form_basis(source_degree), form_basis(target_degree)
    raw = []
    for (row, column, word), coefficient in operator.items():
        source_weight = sp.prod(ETA[index] for index in source[column])
        target_weight = sp.prod(ETA[index] for index in target[row])
        raw.append((column, row, tuple(reversed(word)), (-1) ** len(word) * source_weight * target_weight * coefficient))
    return normalize(raw)


def compose(outer, inner):
    return normalize(
        (outer_row, inner_column, outer_word + inner_word, outer_coefficient * inner_coefficient)
        for (outer_row, middle, outer_word), outer_coefficient in outer.items()
        for (inner_middle, inner_column, inner_word), inner_coefficient in inner.items()
        if middle == inner_middle
    )


def coefficient(value):
    rational, sqrt10 = value["rational"], value["sqrt10"]
    return sp.Rational(rational["numerator"], rational["denominator"]) + sp.Rational(
        sqrt10["numerator"], sqrt10["denominator"]
    ) * SQRT10


def factor_signature(factors):
    return tuple(sorted((factor["kind"], factor["name"], tuple(factor["spacetime_multiindex"])) for factor in factors))


def term_signature(row, column, value, factors, word):
    return row, column, sp.srepr(sp.expand(value)), factor_signature(factors), tuple(word.count(axis) for axis in range(4))


def actual_terms(block):
    return Counter(
        term_signature(
            entry["output_row"], entry["input_row"], coefficient(term["coefficient"]),
            term["coefficient_factors"], tuple(axis for axis, count in enumerate(term["input_pbw_multiindex"]) for _ in range(count)),
        )
        for entry in block["entries"]
        for term in entry["terms"]
    )


def parameter(name):
    return {"kind": "parameter", "name": name, "spacetime_multiindex": [0, 0, 0, 0]}


def profile(name, axis=None):
    return {
        "kind": "profile", "name": name,
        "spacetime_multiindex": [int(axis == index) for index in range(4)] if axis is not None else [0, 0, 0, 0],
    }


def expected_constant(operator, row_offset, column_offset, factors, scale=1):
    return Counter(
        term_signature(row_offset + row, column_offset + column, scale * value, factors, word)
        for (row, column, word), value in operator.items()
    )


def expected_profile_coderivative(operator, switch, coupling, row_offset, column_offset):
    terms = Counter()
    for (row, column, word), value in operator.items():
        terms[term_signature(row_offset + row, column_offset + column, -value, [parameter(coupling), profile(switch)], word)] += 1
        if len(word) == 1:
            terms[term_signature(row_offset + row, column_offset + column, -value, [parameter(coupling), profile(switch, word[0])], ())] += 1
    return terms


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in value["dependency_refs"].values():
        assert sha256(ROOT / ref["path"]) == ref["sha256"]

    # Independent Lie-algebra audit: Jacobi makes the Cartan exterior
    # differential square to zero; delta^2 is its exact formal adjoint.
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    structure = {}
    for first, second, target, coefficient in (
        (1, 2, 3, u), (2, 3, 1, v), (3, 1, 2, v)
    ):
        structure[first, second, target] = coefficient
        structure[second, first, target] = -coefficient
    jacobi_defects = 0
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for target in range(4):
                    residual = 0
                    for middle in range(4):
                        residual += (
                            structure.get((b, c, middle), 0) * structure.get((a, middle, target), 0)
                            + structure.get((c, a, middle), 0) * structure.get((b, middle, target), 0)
                            + structure.get((a, b, middle), 0) * structure.get((c, middle, target), 0)
                        )
                    jacobi_defects += int(sp.simplify(residual) != 0)
    assert jacobi_defects == 0
    assert value["support_local_de_rham"]["d_squared_defect_counts"] == [0, 0, 0]
    assert value["support_local_de_rham"]["delta_squared_defect_counts"] == [0, 0, 0]

    overlay = value["emitter_overlay"]
    blocks = overlay["blocks"]
    assert canonical_sha256(blocks) == overlay["entries_canonical_sha256"]
    assert [block["shape"] for block in blocks] == [[6, 4], [4, 6], [6, 6]] * 2
    assert all(
        len({(entry["output_row"], entry["input_row"]) for entry in block["entries"]})
        == len(block["entries"])
        for block in blocks
    )
    positions = {
        (entry["output_row"], entry["input_row"])
        for block in blocks
        for entry in block["entries"]
    }
    term_count = sum(len(entry["terms"]) for block in blocks for entry in block["entries"])
    assert len(positions) == overlay["nonzero_matrix_position_count"]
    assert term_count == overlay["serialized_term_count"]

    by_id = {block["id"]: block for block in blocks}
    d1, d2 = exterior(1), exterior(2)
    delta2 = adjoint(exterior(1), 1, 2)
    delta3 = adjoint(exterior(2), 2, 3)
    massive = compose(delta3, d2)
    mass_terms = []
    for emitter in (0, 1):
        coupling, switch = f"g{emitter}", f"h{emitter}"
        k_offset, kp_offset = ((84, 96), (90, 102))[emitter]
        assert actual_terms(by_id[f"A_to_K{emitter}_plus"]) == expected_constant(
            d1, kp_offset, 55, [parameter(coupling), profile(switch)], scale=-1
        )
        assert actual_terms(by_id[f"K{emitter}_to_A_plus"]) == expected_profile_coderivative(
            delta2, switch, coupling, 59, k_offset
        )
        expected_massive = expected_constant(massive, kp_offset, k_offset, [])
        for index in range(6):
            expected_massive[term_signature(kp_offset + index, k_offset + index, 1, [parameter(f"m{emitter}_squared")], ())] += 1
        assert actual_terms(by_id[f"K{emitter}_massive_equation"]) == expected_massive
        cross = by_id[f"K{emitter}_to_A_plus"]
        profile_jets = []
        for entry in cross["entries"]:
            for term in entry["terms"]:
                parameters = {factor["name"] for factor in term["coefficient_factors"] if factor["kind"] == "parameter"}
                profiles = [factor for factor in term["coefficient_factors"] if factor["kind"] == "profile"]
                assert parameters == {coupling}
                assert profiles and {factor["name"] for factor in profiles} == {switch}
                profile_jets.extend(sum(factor["spacetime_multiindex"]) for factor in profiles)
        assert 0 in profile_jets and 1 in profile_jets
        for entry in by_id[f"K{emitter}_massive_equation"]["entries"]:
            for term in entry["terms"]:
                names = [factor["name"] for factor in term["coefficient_factors"]]
                if f"m{emitter}_squared" in names:
                    mass_terms.append((emitter, entry["output_row"], entry["input_row"]))
    assert len(mass_terms) == 12
    assert all(row == column + 12 for _, row, column in mass_terms)
    assert value["base_composition_contract"]["base_entry_count"] == 333
    assert not value["flags"]["SCALAR_APPARATUS_Q1_PBW_OVERLAY_EXPORTED"]
    assert not value["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
    print("BERGER_108_ROW_EMITTER_Q1_PBW_OVERLAY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
