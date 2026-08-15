#!/usr/bin/env python3
"""Fast independent receiver for the exhaustive universal Bach table."""
from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json"
sys.path.insert(0, str(HERE))
from cylinder_polarized_bach_evaluator import PAIRS, polarized_bach_euler_density, sparse_fixture  # noqa: E402


FALSE_FLAGS = {
    "PORTABLE_TENSOR_NATURAL_HSTAR_ROW",
    "DIFFERENTIATED_DIFF_NOETHER_REPLAYED",
    "HT1B_NONZERO_CHANNELS_REPLAYED_BY_TABLE",
    "STRICT_SUPPORT_LOCAL_Q2_COMPLETE",
    "CLASSICAL_IMPORT_GATE_PASSED",
    "LORENTZIAN_CAUSAL_CERTIFIED",
    "QME_RESTORED",
}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def words_through(order: int) -> tuple[tuple[int, int, int, int], ...]:
    return tuple(sorted((word for word in product(range(order + 1), repeat=4) if sum(word) <= order), key=lambda word: (sum(word), word)))


def expected_basis() -> list[dict[str, object]]:
    return [
        {"index": index, "component": component, "component_pair": list(PAIRS[component]), "word": list(word), "order": sum(word)}
        for index, (component, word) in enumerate((item for component in range(10) for item in ((component, word) for word in words_through(4))))
    ]


def decode(table: Mapping[str, Any]) -> tuple[list[dict[str, object]], list[Fraction], list[dict[int, Fraction]], list[dict[tuple[int, int], Fraction]]]:
    basis = table["input_basis"]
    coefficients = [Fraction(value) for value in table["coefficient_dictionary"]]
    linear_rows: list[dict[int, Fraction]] = []
    bilinear_rows: list[dict[tuple[int, int], Fraction]] = []
    for row in table["rows"]:
        linear_rows.append({basis_id: coefficients[coefficient_id] for basis_id, coefficient_id in row["linear_entries"]})
        bilinear_rows.append({(left, right): coefficients[coefficient_id] for left, right, coefficient_id in row["symmetric_bilinear_entries"]})
    return basis, coefficients, linear_rows, bilinear_rows


def compact_apply(table: Mapping[str, Any], left: Mapping, right: Mapping) -> dict[tuple[int, int], Fraction]:
    basis, coefficients, _, _ = decode(table)

    def input_value(values: Mapping, basis_id: int) -> Fraction:
        item = basis[basis_id]
        return Fraction(values.get(tuple(item["component_pair"]), {}).get(tuple(item["word"]), 0))

    output = {}
    for row in table["rows"]:
        total = Fraction(0)
        for left_id, right_id, coefficient_id in row["symmetric_bilinear_entries"]:
            coefficient = coefficients[coefficient_id]
            total += coefficient * input_value(left, left_id) * input_value(right, right_id)
            if left_id != right_id:
                total += coefficient * input_value(left, right_id) * input_value(right, left_id)
        output[tuple(row["output_pair"])] = total
    return output


def weyl_identity_defects(table: Mapping[str, Any]) -> dict[str, object]:
    basis, _, linear, bilinear = decode(table)
    diagonal_outputs = ((0, -1), (4, 1), (7, 1), (9, 1))
    linear_defects = []
    for input_id in range(len(basis)):
        value = sum(sign * linear[output].get(input_id, Fraction(0)) for output, sign in diagonal_outputs)
        if value:
            linear_defects.append((input_id, str(value)))

    quadratic_defects = []
    for left in range(len(basis)):
        for right in range(left, len(basis)):
            if basis[left]["order"] + basis[right]["order"] > 4:
                continue
            value = sum(sign * bilinear[output].get((left, right), Fraction(0)) for output, sign in diagonal_outputs)
            left_item, right_item = basis[left], basis[right]
            if left_item["word"] == [0, 0, 0, 0]:
                component = left_item["component"]
                pair = PAIRS[component]
                value += (1 if pair[0] == pair[1] else 2) * linear[component].get(right, Fraction(0))
            if right_item["word"] == [0, 0, 0, 0]:
                component = right_item["component"]
                pair = PAIRS[component]
                value += (1 if pair[0] == pair[1] else 2) * linear[component].get(left, Fraction(0))
            if value:
                quadratic_defects.append((left, right, str(value)))
    return {
        "linear_defect_count": len(linear_defects),
        "quadratic_defect_count": len(quadratic_defects),
        "first_linear_defects": linear_defects[:5],
        "first_quadratic_defects": quadratic_defects[:5],
    }


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("result_state") != "UNIVERSAL_CYLINDER_TABLE_FAST_RECEIVER_READY_GLOBAL_AST_AND_DIFF_IDENTITY_OPEN" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("result state/lifecycle drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("dependency tag promotion")
    scope = value.get("scope", {})
    if scope.get("maximum_total_input_derivative_order") != 4 or scope.get("coefficient_field") != "Q":
        errors.append("derivative/exactness scope drift")
    if scope.get("action_normalization") != "B_action=-2 B_standard" or "not yet supplied" not in scope.get("globalization_boundary", ""):
        errors.append("normalization or globalization boundary drift")

    table = value.get("universal_table", {})
    basis = table.get("input_basis", [])
    if basis != expected_basis():
        errors.append("700-entry normalized metric four-jet basis drift")
    raw_coefficients = table.get("coefficient_dictionary", [])
    try:
        coefficients = [Fraction(item) for item in raw_coefficients]
    except (ValueError, ZeroDivisionError):
        coefficients = []
        errors.append("coefficient dictionary contains a non-exact rational")
    if not coefficients or coefficients != sorted(set(coefficients)) or any(item == 0 for item in coefficients):
        errors.append("coefficient dictionary is not unique sorted nonzero Q data")
    rows = table.get("rows", [])
    if [row.get("output_pair") for row in rows] != [list(pair) for pair in PAIRS] or [row.get("output_component") for row in rows] != list(range(10)):
        errors.append("ten output row inventory/order drift")
    linear_count = ordered_count = symmetric_count = 0
    for row in rows:
        linear_entries = row.get("linear_entries", [])
        bilinear_entries = row.get("symmetric_bilinear_entries", [])
        if len({entry[0] for entry in linear_entries if len(entry) == 2}) != len(linear_entries):
            errors.append(f"duplicate unary basis entry in output {row.get('output_pair')}")
        if len({tuple(entry[:2]) for entry in bilinear_entries if len(entry) == 3}) != len(bilinear_entries):
            errors.append(f"duplicate bilinear basis pair in output {row.get('output_pair')}")
        for entry in linear_entries:
            if len(entry) != 2 or not (0 <= entry[0] < len(basis)) or not (0 <= entry[1] < len(coefficients)):
                errors.append(f"invalid unary entry in output {row.get('output_pair')}")
        for entry in bilinear_entries:
            if len(entry) != 3 or not (0 <= entry[0] <= entry[1] < len(basis)) or not (0 <= entry[2] < len(coefficients)):
                errors.append(f"invalid canonical bilinear entry in output {row.get('output_pair')}")
            elif basis[entry[0]]["order"] + basis[entry[1]]["order"] > 4:
                errors.append(f"bilinear derivative order exceeds four in output {row.get('output_pair')}")
        linear_count += len(linear_entries)
        ordered_count += row.get("ordered_term_count_before_symmetry", 0)
        symmetric_count += len(bilinear_entries)
    expected_counts = {
        "input_basis": len(basis), "coefficient_dictionary": len(coefficients),
        "linear_terms": linear_count, "ordered_bilinear_terms": ordered_count,
        "symmetric_bilinear_terms": symmetric_count,
    }
    if table.get("counts") != expected_counts:
        errors.append("table counts do not reproduce")

    hashes = value.get("canonical_hashes", {})
    expected_hashes = {
        "input_basis_sha256": digest(basis),
        "coefficient_dictionary_sha256": digest(raw_coefficients),
        "row_sha256": {str(tuple(row["output_pair"])): digest(row) for row in rows},
        "universal_table_sha256": digest(table),
        "point_crosschecks_sha256": digest(value.get("exact_checks", {}).get("three_independent_point_evaluator_crosschecks")),
    }
    if hashes != expected_hashes:
        errors.append("canonical table hashes do not reproduce")

    identity = weyl_identity_defects(table) if not errors else {}
    if identity.get("linear_defect_count") != 0 or identity.get("quadratic_defect_count") != 0:
        errors.append(f"independent differentiated Weyl identity failed: {identity}")
    checks = value.get("exact_checks", {})
    producer_trace = checks.get("universal_weyl_trace_defects", {})
    if producer_trace != {"background": "0", "linear_term_count": 0, "bilinear_term_count": 0}:
        errors.append("producer Weyl trace status promoted or failed")
    crosschecks = checks.get("three_independent_point_evaluator_crosschecks", [])
    if [(item.get("left_seed"), item.get("right_seed")) for item in crosschecks] != [(1, 2), (3, 4), (5, 6)]:
        errors.append("point-evaluator crosscheck inventory drift")
    else:
        for record in crosschecks:
            left, right = sparse_fixture(record["left_seed"]), sparse_fixture(record["right_seed"])
            compact = compact_apply(table, left, right)
            point = polarized_bach_euler_density(left, right)
            swapped = compact_apply(table, right, left)
            serialized = [str(point[pair]) for pair in PAIRS]
            if compact != point or swapped != point or record.get("output") != serialized or record.get("output_sha256") != digest(serialized):
                errors.append(f"point/compact/swap crosscheck failed for seeds {record['left_seed']},{record['right_seed']}")
    if checks.get("input_swap_symmetry_defect_count") != 0 or checks.get("compact_table_reproduces_unreduced_operator") is not True:
        errors.append("producer symmetry/compact disposition drift")

    for item in value.get("implementation", {}).values():
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"implementation drift: {item.get('path')}")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"provenance drift: {item.get('path')}")
    receiver = value.get("independent_receiver", {})
    if receiver.get("path") != "quantum-weyl/classical_import/check_strict_cylinder_bach_universal_export.py" or receiver.get("cost_class") != "TIER_1_FAST_REPLAY" or len(receiver.get("replays", [])) != 5:
        errors.append("fast independent receiver declaration drift")
    gates = {item.get("gate"): item.get("status") for item in value.get("next_gates", [])}
    if set(gates) != {"DIFFERENTIATED_DIFF_NOETHER", "HT1B_MODE_ADAPTERS", "TENSOR_NATURAL_GLOBALIZATION", "STRICT_HSTAR_ROW_INTEGRATION"} or any(status != "OPEN" for status in gates.values()):
        errors.append("next-gate inventory/status drift")
    flags = value.get("claim_flags", {})
    if flags.get("UNIVERSAL_BASEPOINT_METRIC_HESSIAN_TABLE_EXPORTED") is not True or flags.get("EXHAUSTIVE_INPUT_SWAP_AND_WEYL_TRACE_REPLAYED") is not True or flags.get("FAST_INDEPENDENT_TABLE_RECEIVER_IMPLEMENTED") is not True or any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim boundary flag promoted")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        counts = value["universal_table"]["counts"]
        print(f"  - {counts['input_basis']} inputs, {counts['symmetric_bilinear_terms']} exact symmetric coefficients, 10 outputs")
        print("  - fast hashes, full Weyl identity and 3 point-evaluator comparisons replayed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
