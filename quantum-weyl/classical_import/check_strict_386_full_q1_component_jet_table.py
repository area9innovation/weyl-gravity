#!/usr/bin/env python3
"""Independently check the strict 386-row full-q1 component jet table."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

import sympy as sp

from strict_386_endpoint_q1_content_bridge import (
    bridge_maps,
    compare,
    covariantized_gate_bach,
    endpoint_data,
    gate_r_tables,
    translated_gate_n_tables,
)
from covariant_completion.curved_operator.weyl_cotton_hyperbolic import (
    ConstraintAdjustedWeylCottonEvolution,
)
from covariant_completion.curved_retract.curvature_mapping_cylinder_kernel import (
    BLOCK_NAMES,
    CurvatureMappingCylinderKernel,
    OperatorPolynomial,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
ENDPOINT_BRIDGE = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
ENDPOINT_WITNESS = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_WITNESS_V1.json"
Q1_AST = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
UNIVERSAL = HERE / "certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json"
AUX_WITNESS = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1.json"
AUX_REPAIR = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.json"
SUSPENSION = HERE / "certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json"
ENDPOINT_PAYLOAD = ROOT / "covariant_completion/certificates/curved_prolonged_metric_endpoint_coefficients.json"
CONE_BOUNDARY = ROOT / "covariant_completion/certificates/curved_rank14_equation_sdr_boundary.json"
CONE_KERNEL = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_kernel.json"
CONE_SUBSTITUTION = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json"

ZERO = (0, 0, 0, 0)
DERIVATIVES = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))
Sparse = dict[tuple[int, int], Fraction]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def q(value: object) -> str:
    rational = Fraction(str(value))
    return str(rational.numerator) if rational.denominator == 1 else f"{rational.numerator}/{rational.denominator}"


def fraction_matrix(matrix: Any) -> list[list[Fraction]]:
    return [[Fraction(str(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def scale(matrix: Sequence[Sequence[Fraction]], coefficient: int) -> list[list[Fraction]]:
    return [[Fraction(coefficient) * value for value in row] for row in matrix]


def identity(size: int, coefficient: int = 1) -> list[list[Fraction]]:
    return [[Fraction(coefficient if row == column else 0) for column in range(size)] for row in range(size)]


def block_indices(pairing: Mapping[str, Any]) -> dict[str, list[int]]:
    output: dict[str, list[int]] = {}
    for row in pairing["component_basis"]["rows"]:
        output.setdefault(row["block"], []).append(row["index"])
    return output


def encode_coefficients(
    coefficients: Mapping[tuple[int, int, int, int], Sequence[Sequence[Fraction]]],
    sources: Sequence[int],
    targets: Sequence[int],
) -> list[dict[str, Any]]:
    output = []
    for multiindex, matrix in sorted(coefficients.items()):
        entries = []
        for target_local, row in enumerate(matrix):
            for source_local, value in enumerate(row):
                if value:
                    entries.append([targets[target_local], sources[source_local], q(value)])
        output.append({"multiindex": list(multiindex), "entries": entries})
    return output


def endpoint_expected(pairing: Mapping[str, Any]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    q1 = load(Q1_AST)
    universal = load(UNIVERSAL)["universal_table"]
    witness = load(ENDPOINT_WITNESS)
    payload = load(ENDPOINT_PAYLOAD)
    bridge = load(ENDPOINT_BRIDGE)
    errors, comparison = compare(q1=q1, universal=universal, witness=witness, endpoint_payload=payload)
    if errors or comparison["common_q1_sha256"] != bridge["coefficientwise_identification"]["common_q1_sha256"]:
        raise ValueError("independent endpoint bridge reconstruction failed")
    k, _, _, field, ghost = endpoint_data(payload)
    maps = bridge_maps(field, ghost)
    gauge = gate_r_tables(q1, k)
    bach = covariantized_gate_bach(witness, universal)
    noether = translated_gate_n_tables(gauge, maps["W_M"])
    blocks = block_indices(pairing)
    return {
        ("ENDPOINT_G", "ENDPOINT_M"): encode_coefficients(gauge, blocks["ENDPOINT_G"], blocks["ENDPOINT_M"]),
        ("ENDPOINT_M", "ENDPOINT_E"): encode_coefficients(bach, blocks["ENDPOINT_M"], blocks["ENDPOINT_E"]),
        ("ENDPOINT_E", "ENDPOINT_I"): encode_coefficients(noether, blocks["ENDPOINT_E"], blocks["ENDPOINT_I"]),
    }


def curvature_primitives() -> dict[str, dict[tuple[int, int, int, int], list[list[Fraction]]]]:
    evolution = ConstraintAdjustedWeylCottonEvolution.build()
    evolution.verify()
    equation_derivative = (
        sp.eye(26).col_join(sp.zeros(14, 26)),
        *tuple(evolution.evolution_spatial_coefficients[axis].col_join(evolution.source_compatibility_spatial_coefficients[axis]) for axis in range(3)),
    )
    equation_zero = evolution.evolution_zeroth_coefficient.col_join(evolution.source_compatibility_zeroth_coefficient)
    identity_derivative = (
        sp.zeros(14, 26).row_join(sp.eye(14)),
        *tuple((-evolution.source_compatibility_spatial_coefficients[axis]).row_join(evolution.constraint_spatial_coefficients[axis]) for axis in range(3)),
    )
    identity_zero = (-evolution.source_compatibility_zeroth_coefficient).row_join(evolution.constraint_zeroth_coefficient)
    if evolution.commuting_symbol_defect + evolution.sphere_curvature_correction != sp.zeros(14, 26):
        raise ValueError("independent curved PBW identity failed")

    def maps(matrices: Sequence[Any]) -> dict[tuple[int, int, int, int], list[list[Fraction]]]:
        return {multiindex: fraction_matrix(matrix) for multiindex, matrix in zip((*DERIVATIVES, ZERO), matrices, strict=True)}

    return {
        "Ecurv": maps((*equation_derivative, equation_zero)),
        "Ncurv": maps((*identity_derivative, identity_zero)),
        "EcurvSharp": maps((*tuple(-matrix.T for matrix in equation_derivative), equation_zero.T)),
        "NcurvSharp": maps((*tuple(-matrix.T for matrix in identity_derivative), identity_zero.T)),
    }


def cone_expected(pairing: Mapping[str, Any]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    blocks = block_indices(pairing)
    primitives = curvature_primitives()
    kernel = CurvatureMappingCylinderKernel.build()
    kernel.verify()
    output: dict[tuple[str, str], list[dict[str, Any]]] = {}
    zero = OperatorPolynomial.zero()
    for target_index in range(4, 16):
        for source_index in range(4, 16):
            operator = kernel.split_differential[target_index][source_index]
            if operator == zero:
                continue
            if len(operator.terms) != 1:
                raise ValueError("non-atomic split cone arrow")
            word, coefficient = operator.terms[0]
            source = "CONE_" + BLOCK_NAMES[source_index].upper()
            target = "CONE_" + BLOCK_NAMES[target_index].upper()
            if not word:
                coefficients = {ZERO: identity(len(blocks[source]), int(coefficient))}
            else:
                if len(word) != 1 or word[0] not in primitives:
                    raise ValueError("unknown split cone primitive")
                coefficients = {multiindex: scale(matrix, int(coefficient)) for multiindex, matrix in primitives[word[0]].items()}
            output[(source, target)] = encode_coefficients(coefficients, blocks[source], blocks[target])
    if len(output) != 14:
        raise ValueError("split cone arrow coverage drift")
    return output


def sparse_multiply(left: Sparse, right: Sparse) -> Sparse:
    by_row: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), value in right.items():
        by_row.setdefault(row, []).append((column, value))
    output: Sparse = {}
    for (row, middle), left_value in left.items():
        for column, right_value in by_row.get(middle, ()):
            key = (row, column)
            value = output.get(key, Fraction()) + left_value * right_value
            if value:
                output[key] = value
            else:
                output.pop(key, None)
    return output


def scale_rows(matrix: Sparse, diagonal: Sequence[int]) -> Sparse:
    return {(row, column): value * diagonal[row] for (row, column), value in matrix.items() if value * diagonal[row]}


def scale_columns(matrix: Sparse, diagonal: Sequence[int]) -> Sparse:
    return {(row, column): value * diagonal[column] for (row, column), value in matrix.items() if value * diagonal[column]}


def combine(tables: Sequence[Mapping[str, Any]], errors: list[str]) -> dict[tuple[int, int, int, int], Sparse]:
    output: dict[tuple[int, int, int, int], Sparse] = {}
    for table in tables:
        for coefficient in table.get("coefficients", []):
            multiindex = tuple(coefficient.get("multiindex", ()))
            if len(multiindex) != 4 or any(not isinstance(axis, int) or axis < 0 for axis in multiindex):
                errors.append("invalid derivative multiindex")
                continue
            matrix = output.setdefault(multiindex, {})
            for entry in coefficient.get("entries", []):
                try:
                    target, source, raw = entry
                    value = Fraction(str(raw))
                except (TypeError, ValueError, ZeroDivisionError):
                    errors.append("non-rational or malformed q1 coefficient")
                    continue
                if not value or not all(isinstance(index, int) and 0 <= index < 386 for index in (target, source)):
                    errors.append("invalid q1 component entry")
                    continue
                if (target, source) in matrix:
                    errors.append("overlapping q1 component entry")
                matrix[target, source] = value
    return output


def check(value: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    pairing = load(PAIRING)
    if value.get("result_id") != "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("result identity or lifecycle drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags drift")
    serialization = value.get("q1_serialization", {})
    tables = serialization.get("tables", [])
    if serialization.get("carrier_dimension") != 386 or serialization.get("carrier_split") != "30+36+320" or serialization.get("maximum_order") != 4 or len(tables) != 18:
        errors.append("carrier or table inventory drift")

    actual: dict[tuple[str, str], Mapping[str, Any]] = {}
    rows = pairing["component_basis"]["rows"]
    for operator in tables:
        key = (operator.get("source_block"), operator.get("target_block"))
        if key in actual:
            errors.append("duplicate source/target operator table")
        actual[key] = operator
        coefficients = operator.get("coefficients", [])
        if operator.get("sha256") != digest(coefficients):
            errors.append(f"operator table digest drift: {operator.get('table_id')}")
        count = sum(len(item.get("entries", [])) for item in coefficients)
        if operator.get("nonzero_coefficients") != count or operator.get("coefficient_multiindices") != len(coefficients):
            errors.append(f"operator table count drift: {operator.get('table_id')}")
        for coefficient in coefficients:
            for target, source, _ in coefficient.get("entries", []):
                if rows[target]["degree"] != rows[source]["degree"] + 1:
                    errors.append("q1 degree-one condition failed")

    try:
        expected = endpoint_expected(pairing)
        expected.update(cone_expected(pairing))
    except (KeyError, TypeError, ValueError, AssertionError) as error:
        errors.append(str(error))
        expected = {}
    auxiliary_indices = list(range(30, 66))
    auxiliary_matrix = [[Fraction() for _ in auxiliary_indices] for _ in auxiliary_indices]
    witness = load(AUX_WITNESS)
    for target, source, raw in witness["entries"]:
        auxiliary_matrix[target][source] = Fraction(raw)
    expected[("AUXILIARY_36", "AUXILIARY_36")] = encode_coefficients({ZERO: auxiliary_matrix}, auxiliary_indices, auxiliary_indices)
    if set(actual) != set(expected):
        errors.append("source/target arrow coverage drift")
    for key, coefficients in expected.items():
        if actual.get(key, {}).get("coefficients") != coefficients:
            errors.append(f"independent coefficient reconstruction mismatch: {key}")

    combined = combine(tables, errors)
    omega: Sparse = {(entry["left_index"], entry["right_index"]): Fraction(entry["coefficient"]) for entry in pairing["pairing_serialization"]["entries"]}
    suspension = pairing["suspension_serialization"]["R_diagonal"]
    degree = [-1 if row["degree"] % 2 else 1 for row in rows]
    omega_r = scale_columns(omega, suspension)
    cyclic_defects = 0
    sector_defects = {"endpoint": 0, "auxiliary": 0, "mapping_cone": 0}
    for multiindex, matrix in combined.items():
        formal_transpose = {(column, row): value * (-1 if sum(multiindex) % 2 else 1) for (row, column), value in matrix.items()}
        left = sparse_multiply(formal_transpose, omega_r)
        right = sparse_multiply(omega_r, scale_rows(matrix, degree))
        defects = [key for key in set(left) | set(right) if left.get(key, Fraction()) != right.get(key, Fraction())]
        cyclic_defects += len(defects)
        for row, column in defects:
            sector_defects["endpoint" if max(row, column) < 30 else "auxiliary" if max(row, column) < 66 else "mapping_cone"] += 1
    cyclicity = value.get("suspended_cyclicity_replay", {})
    if cyclic_defects or cyclicity.get("exact_defects") != cyclic_defects or cyclicity.get("sector_defects") != sector_defects or cyclicity.get("coefficientwise_multiindices_checked") != len(combined):
        errors.append("independent suspended cyclicity replay failed")

    auxiliary = actual.get(("AUXILIARY_36", "AUXILIARY_36"), {})
    aux_sparse = {(target - 30, source - 30): Fraction(raw) for target, source, raw in auxiliary.get("coefficients", [{}])[0].get("entries", [])} if auxiliary.get("coefficients") else {}
    if sparse_multiply(aux_sparse, aux_sparse):
        errors.append("serialized auxiliary q square is nonzero")
    nilpotency = value.get("nilpotency_replay", {})
    sectors = nilpotency.get("sector_replays", {})
    if nilpotency.get("full_q1_squared_zero") is not True or nilpotency.get("cross_sector_arrows") != 0 or any(sectors.get(name, {}).get("defects") != 0 for name in ("endpoint_30", "auxiliary_36", "mapping_cone_320")):
        errors.append("nilpotency disposition drift")
    if load(Q1_AST)["square_zero_theorem"]["status"] != "CERTIFIED" or load(AUX_REPAIR)["claim_flags"]["STRICT_386_AUXILIARY_Q_SIGN_REPAIR_APPLIED"] is not True:
        errors.append("nilpotency dependency unavailable")

    counts = serialization.get("counts", {})
    expected_counts = {
        "operator_tables": len(tables),
        "coefficient_multiindex_tables": sum(len(item.get("coefficients", [])) for item in tables),
        "nonzero_rational_coefficients": sum(item.get("nonzero_coefficients", 0) for item in tables),
        "by_sector": {
            "endpoint_30": sum(item.get("nonzero_coefficients", 0) for item in tables if str(item.get("source_block", "")).startswith("ENDPOINT_")),
            "auxiliary_36": auxiliary.get("nonzero_coefficients", 0),
            "mapping_cone_320": sum(item.get("nonzero_coefficients", 0) for item in tables if str(item.get("source_block", "")).startswith("CONE_")),
        },
    }
    if counts != expected_counts or counts.get("by_sector") != {"endpoint_30": 619, "auxiliary_36": 30, "mapping_cone_320": 1544}:
        errors.append("serialization counts drift")

    snapshot = value.get("unary_snapshot", {})
    expected_snapshot = {
        "kind": "STRICT_386_UNARY_OPERATOR_SNAPSHOT",
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "suspension_sha256": pairing["canonical_hashes"]["suspension_serialization_sha256"],
        "q1_tables_sha256": digest(tables),
        "primitive_curvature_table_sha256": snapshot.get("primitive_curvature_table_sha256"),
    }
    expected_snapshot["snapshot_sha256"] = digest(expected_snapshot)
    if snapshot != expected_snapshot:
        errors.append("unary snapshot binding drift")

    gate = value.get("gate_disposition", {})
    expected_gate_true = (
        "full_386_component_basis_serialized", "full_386_component_pairing_serialized",
        "full_386_q1_component_jet_tables_serialized", "full_386_q1_squared_zero_replayed",
        "full_386_q1_suspended_cyclicity_replayed", "unary_snapshot_hash_established",
    )
    if any(gate.get(key) is not True for key in expected_gate_true) or gate.get("one_common_gate_a_snapshot_hash_accepted") is not False or gate.get("classical_import_gate_a_status") != "FAIL_CLOSED":
        errors.append("Gate-A boundary drift")
    flags = value.get("claim_flags", {})
    for key in ("STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_SERIALIZED", "STRICT_386_FULL_Q1_SQUARED_ZERO_REPLAYED", "STRICT_386_FULL_Q1_SUSPENDED_CYCLICITY_REPLAYED", "STRICT_386_UNARY_SNAPSHOT_HASH_ESTABLISHED"):
        if flags.get(key) is not True:
            errors.append(f"missing warranted flag {key}")
    for key in ("STRICT_386_FULL_SDR_OPERATOR_TABLES_SERIALIZED", "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED", "STRICT_386_LOCAL_D_CERTIFIED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append(f"overclaim flag {key}")

    hashes = value.get("canonical_hashes", {})
    expected_hashes = {
        "q1_serialization_sha256": digest(serialization),
        "nilpotency_replay_sha256": digest(nilpotency),
        "suspended_cyclicity_replay_sha256": digest(cyclicity),
        "unary_snapshot_sha256": digest(snapshot),
    }
    if hashes != expected_hashes:
        errors.append("canonical hashes drift")
    projection_keys = ("scope", "q1_serialization", "nilpotency_replay", "suspended_cyclicity_replay", "unary_snapshot", "foundational_strength", "gate_disposition", "claim_flags", "does_not_establish", "next_gate", "canonical_hashes")
    if value.get("independent_checker", {}).get("expected_digest") != digest({key: value[key] for key in projection_keys}):
        errors.append("independent projection digest drift")

    provenance = value.get("provenance", {})
    for item in provenance.get("inputs", []) + provenance.get("implementation", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or item.get("sha256") != sha(path):
            errors.append(f"provenance hash drift: {item.get('path')}")
    return errors


def main() -> int:
    errors = check(load(RESULT))
    print("STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print(" - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
