#!/usr/bin/env python3
"""Independent exact checker for the portable natural Bach-Hessian AST."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from bach_natural_operator_ast import (
    NaturalOperatorAstError,
    evaluate_ast,
    transform_background,
    transform_metric_jets,
    transform_output_density,
    validate_ast,
)
import cylinder_polarized_bach_evaluator as point


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_BACH_NATURAL_OPERATOR_AST_V1.json"
UNIVERSAL = HERE / "certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json"
HSTAR = HERE / "certificates/STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.json"
NORMALIZATION = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/action_normalization.json"
NARIAI = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json"
TRUE_FLAGS = {
    "BACH_EULER_NATURAL_MAP_PORTABLE",
    "POLARIZED_BACH_KERNEL_PORTABLE",
    "GENERAL_DIFF_NATURALITY_COMPOSITIONALLY_CERTIFIED",
    "SIGNED_COORDINATE_COVARIANCE_REPLAYED",
}
FALSE_FLAGS = {
    "PORTABLE_TENSOR_NATURAL_HSTAR_ROW",
    "SUSPENDED_GRADED_POLARIZATION_REPLAYED",
    "STRICT_SUPPORT_LOCAL_Q2_COMPLETE",
    "CLASSICAL_IMPORT_GATE_PASSED",
    "LORENTZIAN_CAUSAL_CERTIFIED",
    "QME_RESTORED",
}
OPERATIONS = (
    "metric_two_parameter_family",
    "inverse_metric",
    "levi_civita_geometry",
    "schouten_and_weyl_4d",
    "cotton_4d",
    "bach_4d",
    "raise_symmetric_two_tensor",
    "absolute_metric_volume_density",
    "densitize_and_scale",
    "mixed_frechet_coefficient",
)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def serialize(values: Mapping[tuple[int, int], Fraction]) -> list[str]:
    return [str(values[pair]) for pair in point.PAIRS]


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    universal = json.loads(UNIVERSAL.read_text())
    hstar = json.loads(HSTAR.read_text())
    normalization = json.loads(NORMALIZATION.read_text())
    nariai = json.loads(NARIAI.read_text())

    if value.get("result_state") != "PORTABLE_NATURAL_BACH_HESSIAN_CERTIFIED_HSTAR_INTEGRATION_AND_SUSPENSION_OPEN" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("result state or lifecycle drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("dependency-tag promotion")
    scope = value.get("scope", {})
    if scope.get("maximum_metric_jet_order") != 4 or scope.get("coefficient_field") != "Q" or "a*b" not in scope.get("taylor_convention", ""):
        errors.append("exact scope, order, or Taylor convention drift")
    if scope.get("action_normalization") != normalization.get("Euler_coordinate") or "intersect" not in scope.get("support_rule", ""):
        errors.append("action normalization or support-locality drift")

    ast = value.get("natural_operator_ast")
    try:
        validate_ast(ast)
    except NaturalOperatorAstError as exc:
        errors.append(f"natural AST rejected: {exc}")
    nodes = ast.get("nodes", []) if isinstance(ast, dict) else []
    if tuple(node.get("operation") for node in nodes) != OPERATIONS:
        errors.append("natural AST operation order/coverage drift")
    if not nodes or nodes[-1].get("declared_output_type") != "symmetric_bilinear_metric_jet_operator_to_symmetric_contravariant_density_weight_plus_1":
        errors.append("root operator target type drift")

    contracts = value.get("primitive_contracts", [])
    if tuple(item.get("operation") for item in contracts) != OPERATIONS or any(item.get("preserves_locality") is not True for item in contracts):
        errors.append("primitive naturality/locality contract incomplete")
    proof = value.get("compositional_naturality", {})
    if proof.get("status") != "CERTIFIED" or proof.get("proof_kind") != "COMPOSITIONAL_NATURAL_OPERATOR_THEOREM_WITH_EXECUTABLE_SEMANTICS":
        errors.append("compositional naturality proof status drift")
    if len(proof.get("derivation", [])) != 4 or "twice" not in proof.get("derivation", ["", "", "", ""])[-1] or "implementation regression" not in proof.get("finite_coordinate_test_role", ""):
        errors.append("naturality derivation or finite-test boundary drift")

    checks = value.get("exact_evaluator_checks", {})
    background_records = checks.get("background_crosschecks", [])
    expected_backgrounds = (
        ("conformal_cylinder", point.cylinder_background(4), 1, 2),
        ("minkowski", point.flat_background(4), 2, 3),
        ("flat_brinkmann", point.brinkmann_background(4), 3, 4),
    )
    if [(item.get("background"), item.get("left_seed"), item.get("right_seed")) for item in background_records] != [(name, left, right) for name, _, left, right in expected_backgrounds]:
        errors.append("background crosscheck inventory drift")
    elif not errors:
        for record, (name, background, left_seed, right_seed) in zip(background_records, expected_backgrounds):
            left, right = point.sparse_fixture(left_seed), point.sparse_fixture(right_seed)
            natural = evaluate_ast(ast, left, right, background=background)
            reference = point.polarized_bach_euler_density(left, right, background=background)
            swapped = evaluate_ast(ast, right, left, background=background)
            output = serialize(natural)
            if natural != reference or natural != swapped:
                errors.append(f"{name}: evaluator equality or input symmetry failed")
            if record.get("output_sha256") != digest(output) or record.get("nonzero_output_count") != sum(item != 0 for item in natural.values()) or record.get("natural_ast_equals_independent_point_evaluator") is not True:
                errors.append(f"{name}: stored exact output drift")

    ppwave_records = checks.get("ppwave_restriction_crosschecks", [])
    if [(item.get("left_seed"), item.get("right_seed")) for item in ppwave_records] != [(1, 2), (2, 4), (3, 5)]:
        errors.append("pp-wave crosscheck inventory drift")
    elif not errors:
        background = point.brinkmann_background(4)
        for record in ppwave_records:
            natural = evaluate_ast(ast, point.ppwave_profile_fixture(record["left_seed"]), point.ppwave_profile_fixture(record["right_seed"]), background=background)
            if any(natural.values()) or record.get("all_ten_outputs_zero") is not True or record.get("output_sha256") != digest(serialize(natural)):
                errors.append("pp-wave restriction drift")

    coordinate = checks.get("signed_coordinate_permutation", {})
    permutation, signs = tuple(coordinate.get("permutation", [])), tuple(coordinate.get("signs", []))
    if (permutation, signs, coordinate.get("left_seed"), coordinate.get("right_seed")) != ((0, 2, 3, 1), (-1, 1, -1, 1), 5, 6):
        errors.append("signed-coordinate witness inventory drift")
    elif not errors:
        background = point.cylinder_background(4)
        left, right = point.sparse_fixture(5), point.sparse_fixture(6)
        original = evaluate_ast(ast, left, right, background=background)
        transformed = evaluate_ast(ast, transform_metric_jets(left, permutation, signs), transform_metric_jets(right, permutation, signs), background=transform_background(background, permutation, signs))
        expected = transform_output_density(original, permutation, signs)
        if transformed != expected or coordinate.get("exact_covariance") is not True:
            errors.append("signed-coordinate covariance failed")
        if coordinate.get("transformed_output_sha256") != digest(serialize(transformed)) or coordinate.get("expected_tensor_density_output_sha256") != digest(serialize(expected)):
            errors.append("signed-coordinate output hash drift")

    evidence = value.get("cross_background_evidence", {})
    cylinder = evidence.get("cylinder_universal_table", {})
    nariai_record = evidence.get("Nariai_action_Hessian", {})
    if cylinder.get("result_id") != universal.get("result_id") or cylinder.get("table_sha256") != universal.get("canonical_hashes", {}).get("universal_table_sha256"):
        errors.append("cylinder table crosswalk drift")
    if nariai_record.get("result_id") != nariai.get("result_id") or nariai_record.get("sha256") != file_sha(NARIAI) or "no component adapter" not in nariai_record.get("relationship", ""):
        errors.append("Nariai evidence or adapter boundary drift")
    if hstar.get("claim_flags", {}).get("PORTABLE_TENSOR_NATURAL_HSTAR_ROW") is not False:
        errors.append("upstream h-star boundary drift")

    gates = {item.get("gate"): item.get("status") for item in value.get("gate_advancement", [])}
    if gates != {
        "P4_PORTABLE_AST_EXPORT": "PASS",
        "HSTAR_PORTABLE_INTEGRATION": "OPEN",
        "SUSPENDED_GRADED_POLARIZATION": "OPEN",
        "SIX_ROW_INTERACTION_IDENTITIES": "OPEN",
    }:
        errors.append("gate advancement drift or premature promotion")
    flags = value.get("claim_flags", {})
    if any(flags.get(flag) is not True for flag in TRUE_FLAGS) or any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim flags drift or premature promotion")
    if len(value.get("does_not_establish", [])) < 6:
        errors.append("does-not-establish ledger shortened")

    expected_hashes = {
        "natural_operator_ast_sha256": digest(ast),
        "primitive_contracts_sha256": digest(contracts),
        "compositional_naturality_sha256": digest(proof),
        "exact_evaluator_checks_sha256": digest(checks),
        "cross_background_evidence_sha256": digest(evidence),
        "gate_advancement_sha256": digest(value.get("gate_advancement")),
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    for group in value.get("provenance", {}).values():
        if not isinstance(group, list):
            errors.append("provenance group is not a list")
            continue
        for item in group:
            path = ROOT / item.get("path", "")
            if not path.is_file() or file_sha(path) != item.get("sha256"):
                errors.append(f"provenance drift: {item.get('path')}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_BACH_NATURAL_OPERATOR_AST_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - portable fourth-order natural Bach-Hessian DAG and exact semantics replayed")
        print("  - h-star integration, suspension and interaction identities remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
