#!/usr/bin/env python3
"""Independent exact checker for the authoritative minimal-BV q3 import."""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import permutations
import json
from pathlib import Path
from typing import Any, Mapping

import bach_natural_operator_ast as quadratic
import cylinder_cubic_bach_evaluator as diagonal
import cylinder_polarized_bach_evaluator as point
from local_q1_q2_receiver import apply_q1, field_fixture
import pure_weyl_cubic_natural_operator as cubic


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
WITNESS = HERE / "certificates/STRICT_386_PURE_WEYL_Q3_WITNESS_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def serialize(values: Mapping[tuple[int, int], Mapping[tuple[int, int, int, int], Fraction]]) -> list[dict[str, object]]:
    return [
        {
            "component": list(pair),
            "terms": [
                {"multiindex": list(alpha), "coefficient": str(coefficient)}
                for alpha, coefficient in sorted(values[pair].items())
                if coefficient
            ],
        }
        for pair in point.PAIRS
    ]


def metric_payload(value: Mapping[tuple[int, int], point.Jet]) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    return {
        pair: {alpha: coefficient for a, b, alpha, coefficient in value[pair].terms if a == b == 0}
        for pair in point.PAIRS
    }


def add_fields(*fields: point.MetricJets) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    output = {}
    for pair in point.PAIRS:
        row: dict[tuple[int, int, int, int], Fraction] = {}
        for field in fields:
            for alpha, coefficient in field.get(pair, {}).items():
                row[alpha] = row.get(alpha, Fraction(0)) + Fraction(coefficient)
        output[pair] = {alpha: coefficient for alpha, coefficient in row.items() if coefficient}
    return output


def diagonal_point(field: point.MetricJets, background: Mapping[tuple[int, int], point.Jet]) -> dict[tuple[int, int], Fraction]:
    data = diagonal.diagonal_cubic_bach_data(field, background=background, output_coordinate_order=1)
    return {
        pair: next((Fraction(term["coefficient"]) for term in data["q3_metric_euler_density"][pair] if term["multiindex"] == [0, 0, 0, 0]), Fraction(0))
        for pair in point.PAIRS
    }


def polarization_reference(fields: tuple[point.MetricJets, point.MetricJets, point.MetricJets], background: Mapping[tuple[int, int], point.Jet]) -> dict[tuple[int, int], Fraction]:
    x, y, z = fields
    samples = {
        "xyz": diagonal_point(add_fields(x, y, z), background),
        "xy": diagonal_point(add_fields(x, y), background),
        "xz": diagonal_point(add_fields(x, z), background),
        "yz": diagonal_point(add_fields(y, z), background),
        "x": diagonal_point(x, background),
        "y": diagonal_point(y, background),
        "z": diagonal_point(z, background),
    }
    return {
        pair: (samples["xyz"][pair] - samples["xy"][pair] - samples["xz"][pair] - samples["yz"][pair] + samples["x"][pair] + samples["y"][pair] + samples["z"][pair]) / 6
        for pair in point.PAIRS
    }


def check(value: dict[str, Any], *, replay_exact: bool = True) -> list[str]:
    errors: list[str] = []
    classical = json.loads(CLASSICAL.read_text())
    witness = json.loads(WITNESS.read_text())
    ast = classical.get("natural_operator_ast", {})
    try:
        cubic.validate_imported_ast(ast)
    except cubic.CubicNaturalOperatorError as exc:
        errors.append(f"classical AST rejected: {exc}")

    if value.get("result_id") != "STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1" or value.get("result_kind") != "INDEPENDENT_EXACT_IMPORT_AND_EXECUTION_OF_AUTHORITATIVE_MINIMAL_BV_Q3":
        errors.append("result identity or kind drift")
    if value.get("result_state") != "ARBITRARY_INPUT_MINIMAL_BV_Q3_IMPORTED_ARITY_THREE_AND_386_STABILIZATION_OPEN" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("result state or lifecycle drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("dependency tag promotion")
    scope = value.get("scope", {})
    if scope.get("coefficient_field") != "Q" or scope.get("maximum_metric_jet_order") != 4 or "[a*b*c]" not in scope.get("taylor_convention", ""):
        errors.append("exact scope, differential order or Taylor convention drift")
    if "intersect" not in scope.get("support_rule", ""):
        errors.append("support-locality boundary drift")

    bridge = value.get("import_bridge", {})
    if bridge.get("classical_export") != classical.get("result_id") or bridge.get("carrier_or_convention_change") is not False:
        errors.append("classical import bridge drift")
    if bridge.get("source_carrier") != ["g", "xi", "omega", "g_star", "xi_star", "omega_star"] or bridge.get("imported_zero_output_rows") != ["g", "xi", "omega", "xi_star", "omega_star"]:
        errors.append("six-row support import drift")
    if bridge.get("sha256") != digest({key: item for key, item in bridge.items() if key != "sha256"}):
        errors.append("import bridge digest drift")

    contracts = value.get("primitive_contracts", [])
    operations = [item.get("operation") for item in ast.get("nodes", [])]
    if [item.get("operation") for item in contracts] != operations or any(item.get("preserves_locality") is not True for item in contracts):
        errors.append("primitive naturality/locality contract incomplete")
    proof = value.get("compositional_naturality", {})
    if proof.get("status") != "CERTIFIED" or len(proof.get("derivation", [])) != 4 or "three" not in proof.get("derivation", ["", "", "", ""])[-1]:
        errors.append("compositional naturality theorem drift")
    if "implementation regressions" not in proof.get("finite_coordinate_test_role", ""):
        errors.append("finite-test/general-proof boundary drift")

    checks = value.get("exact_receiver_checks", {})
    records = checks.get("background_crosschecks", [])
    expected_backgrounds = (
        ("conformal_cylinder", point.cylinder_background(4), (1, 2, 3)),
        ("minkowski", point.flat_background(4), (2, 3, 4)),
        ("flat_brinkmann", point.brinkmann_background(4), (3, 4, 5)),
    )
    if [(item.get("background"), tuple(item.get("input_seeds", []))) for item in records] != [(name, seeds) for name, _, seeds in expected_backgrounds]:
        errors.append("background receiver inventory drift")
    elif replay_exact:
        for record, (name, background, seeds) in zip(records, expected_backgrounds):
            result = cubic.evaluate_ast(ast, *(point.sparse_fixture(seed) for seed in seeds), background=background)
            if record.get("output_sha256") != digest(serialize(result)) or record.get("nonzero_output_count") != sum(bool(row) for row in result.values()):
                errors.append(f"{name}: stored exact output drift")

    symmetry_defect = False
    if replay_exact:
        symmetry_fields = tuple(point.sparse_fixture(seed) for seed in (1, 2, 3))
        symmetry_outputs = [cubic.evaluate_ast(ast, *(symmetry_fields[index] for index in order), background=point.flat_background(4)) for order in permutations(range(3))]
        symmetry_defect = any(item != symmetry_outputs[0] for item in symmetry_outputs[1:])
    if symmetry_defect or checks.get("S3_input_permutations_replayed") != 6 or checks.get("S3_exact_symmetry") is not True:
        errors.append("S3 symmetry replay drift")

    polarization = checks.get("seven_diagonal_polarization", {})
    polarization_defect = False
    if replay_exact:
        polarization_fields = tuple(point.sparse_fixture(seed) for seed in (4, 5, 6))
        polarization_background = point.flat_background(5)
        direct = cubic.evaluate_point(ast, *polarization_fields, background=polarization_background)
        reference = polarization_reference(polarization_fields, polarization_background)
        direct_digest = digest([str(direct[pair]) for pair in point.PAIRS])
        reference_digest = digest([str(reference[pair]) for pair in point.PAIRS])
        polarization_defect = direct != reference or polarization.get("direct_output_sha256") != direct_digest or polarization.get("polarized_output_sha256") != reference_digest
    if polarization_defect or polarization.get("exact_equality") is not True:
        errors.append("seven-diagonal polarization replay drift")

    diagonal_record = checks.get("pinned_diagonal_witness", {})
    diagonal_defect = False
    if replay_exact:
        diagonal_background = point.flat_background(7)
        gauge_field = metric_payload(apply_q1("q1_h_c", field_fixture("c", 1, 7), diagonal_background, 6))
        diagonal_result = cubic.evaluate_ast(ast, gauge_field, gauge_field, gauge_field, background=diagonal_background, output_coordinate_order=1)
        stored = {
            tuple(row["component"]): {tuple(term["multiindex"]): Fraction(term["coefficient"]) for term in row["terms"]}
            for row in witness["exact_cubic_fixture"]["metric_output_rows"]
        }
        diagonal_defect = diagonal_result != stored
    if diagonal_defect or diagonal_record.get("exact_row_equality") is not True or diagonal_record.get("required_value") != "-75760/9" or diagonal_record.get("metric_output_term_count") != 41:
        errors.append("pinned diagonal witness replay drift")

    ppwave_defect = replay_exact and any(cubic.evaluate_ast(ast, *(point.ppwave_profile_fixture(seed) for seed in (1, 2, 3)), background=point.brinkmann_background(4)).values())
    if ppwave_defect or checks.get("ppwave_restriction", {}).get("all_ten_outputs_zero") is not True:
        errors.append("pp-wave restriction drift")

    coordinate = checks.get("signed_coordinate_permutation", {})
    coordinate_defect = False
    if replay_exact:
        permutation, signs = tuple(coordinate.get("permutation", [])), tuple(coordinate.get("signs", []))
        fields = tuple(point.sparse_fixture(seed) for seed in (5, 6, 7))
        background = point.cylinder_background(4)
        original = cubic.evaluate_ast(ast, *fields, background=background)
        transformed = cubic.evaluate_ast(ast, *(quadratic.transform_metric_jets(field, permutation, signs) for field in fields), background=quadratic.transform_background(background, permutation, signs))
        expected = cubic.transform_output_density_jets(original, permutation, signs)
        coordinate_defect = transformed != expected or coordinate.get("output_sha256") != digest(serialize(transformed))
    if coordinate_defect or coordinate.get("exact_covariance") is not True:
        errors.append("signed-coordinate covariance drift")

    gates = {item.get("gate"): item.get("status") for item in value.get("gate_advancement", [])}
    if gates != {
        "AUTHORITATIVE_MINIMAL_Q3_IMPORT": "PASS",
        "ARBITRARY_INPUT_COMPONENT_EXECUTION": "PASS",
        "MINIMAL_ARITY_THREE_Q_SQUARED": "OPEN",
        "MINIMAL_Q3_CYCLICITY": "OPEN",
        "STRICT_386_CYCLIC_STABILIZATION": "OPEN",
    }:
        errors.append("gate advancement drift or premature promotion")
    flags = value.get("claim_flags", {})
    true_flags = ("AUTHORITATIVE_MINIMAL_BV_Q3_IMPORTED", "ARBITRARY_THREE_INPUT_METRIC_Q3_EXECUTED", "ALL_SIX_MINIMAL_Q3_OUTPUT_ROWS_IMPORTED", "GENERAL_DIFF_NATURALITY_COMPOSITIONALLY_CERTIFIED", "S3_SYMMETRY_REPLAYED", "DIAGONAL_Q3_WITNESS_REPRODUCED")
    false_flags = ("MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED", "MINIMAL_BV_Q3_CYCLICITY_CERTIFIED", "STRICT_386_Q3_STABILIZED", "CLASSICAL_IMPORT_GATE_PASSED", "LORENTZIAN_CAUSAL_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED")
    if any(flags.get(name) is not True for name in true_flags) or any(flags.get(name) is not False for name in false_flags):
        errors.append("claim flags drift or premature promotion")

    foundations = value.get("foundational_strength", {})
    if foundations.get("dependency_boundary") != "LOCAL-ALGEBRAIC" or foundations.get("choice_operation_added") is not False or foundations.get("completion_or_infinite_sum_used") is not False:
        errors.append("foundational-strength boundary drift")
    expected_hashes = {
        "import_bridge_sha256": digest(bridge),
        "primitive_contracts_sha256": digest(contracts),
        "compositional_naturality_sha256": digest(proof),
        "exact_receiver_checks_sha256": digest(checks),
        "gate_advancement_sha256": digest(value.get("gate_advancement")),
        "foundational_strength_sha256": digest(foundations),
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    for group in value.get("provenance", {}).values():
        if not isinstance(group, list):
            errors.append("provenance group is not a list")
            continue
        for item in group:
            path = ROOT / item.get("path", "")
            if not path.is_file() or item.get("sha256") != sha(path):
                errors.append(f"provenance drift: {item.get('path')}")
    if len(value.get("does_not_establish", [])) < 6:
        errors.append("does-not-establish ledger shortened")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1_CHECK: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - authoritative arbitrary-input six-row minimal q3 imported and exactly replayed")
        print("  - arity-three identity, cyclicity and 386 stabilization remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
