#!/usr/bin/env python3
"""Serialize the complete split-basis strict 386-row unary BV differential."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

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


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
REPORT = HERE / "REPORT_STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.md"

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
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def q(value: object) -> str:
    rational = Fraction(str(value))
    return str(rational.numerator) if rational.denominator == 1 else f"{rational.numerator}/{rational.denominator}"


def fraction_matrix(matrix: Any) -> list[list[Fraction]]:
    return [[Fraction(str(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def scale_matrix(matrix: Sequence[Sequence[Fraction]], coefficient: int) -> list[list[Fraction]]:
    return [[Fraction(coefficient) * entry for entry in row] for row in matrix]


def identity(size: int) -> list[list[Fraction]]:
    return [[Fraction(int(row == column)) for column in range(size)] for row in range(size)]


def table(
    table_id: str,
    source_block: str,
    target_block: str,
    source_indices: Sequence[int],
    target_indices: Sequence[int],
    coefficients: Mapping[tuple[int, int, int, int], Sequence[Sequence[Fraction]]],
    *,
    role: str,
    origin: str,
) -> dict[str, Any]:
    encoded: list[dict[str, Any]] = []
    nonzero = 0
    for multiindex, matrix in sorted(coefficients.items()):
        if len(matrix) != len(target_indices) or any(len(row) != len(source_indices) for row in matrix):
            raise ValueError(f"{table_id} shape drift")
        entries = []
        for target_local, row in enumerate(matrix):
            for source_local, coefficient in enumerate(row):
                if coefficient:
                    entries.append([
                        target_indices[target_local],
                        source_indices[source_local],
                        q(coefficient),
                    ])
        nonzero += len(entries)
        encoded.append({"multiindex": list(multiindex), "entries": entries})
    value = {
        "table_id": table_id,
        "source_block": source_block,
        "target_block": target_block,
        "source_global_indices": list(source_indices),
        "target_global_indices": list(target_indices),
        "shape": [len(target_indices), len(source_indices)],
        "maximum_order": max((sum(multiindex) for multiindex in coefficients), default=0),
        "coefficient_multiindices": len(encoded),
        "nonzero_coefficients": nonzero,
        "orientation": "entry[target_global_index,source_global_index]",
        "role": role,
        "origin": origin,
        "coefficients": encoded,
    }
    value["sha256"] = digest(encoded)
    return value


def blocks(pairing: Mapping[str, Any]) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    for row in pairing["component_basis"]["rows"]:
        result.setdefault(row["block"], []).append(row["index"])
    return result


def endpoint_tables(values: Mapping[Path, Mapping[str, Any]], by_block: Mapping[str, list[int]]) -> list[dict[str, Any]]:
    q1 = values[Q1_AST]
    universal = values[UNIVERSAL]["universal_table"]
    witness = values[ENDPOINT_WITNESS]
    payload = values[ENDPOINT_PAYLOAD]
    errors, comparison = compare(q1=q1, universal=universal, witness=witness, endpoint_payload=payload)
    if errors:
        raise ValueError("endpoint bridge replay failed: " + "; ".join(errors))
    if comparison["common_q1_sha256"] != values[ENDPOINT_BRIDGE]["coefficientwise_identification"]["common_q1_sha256"]:
        raise ValueError("endpoint common-q1 digest drift")
    k_endpoint, _, _, field_pairing, ghost_pairing = endpoint_data(payload)
    maps = bridge_maps(field_pairing, ghost_pairing)
    gauge = gate_r_tables(q1, k_endpoint)
    bach = covariantized_gate_bach(witness, universal)
    noether = translated_gate_n_tables(gauge, maps["W_M"])
    return [
        table(
            "ENDPOINT_G_TO_M", "ENDPOINT_G", "ENDPOINT_M",
            by_block["ENDPOINT_G"], by_block["ENDPOINT_M"], gauge,
            role="Diff x Weyl gauge map in Gate coordinates",
            origin="STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1 exact regenerated common table",
        ),
        table(
            "ENDPOINT_M_TO_E", "ENDPOINT_M", "ENDPOINT_E",
            by_block["ENDPOINT_M"], by_block["ENDPOINT_E"], bach,
            role="linearized Bach Hessian in symmetrized covariant jets",
            origin="STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1 all 700 input columns",
        ),
        table(
            "ENDPOINT_E_TO_I", "ENDPOINT_E", "ENDPOINT_I",
            by_block["ENDPOINT_E"], by_block["ENDPOINT_I"], noether,
            role="Gate-translated Noether map",
            origin="STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1 negative formal-adjoint table",
        ),
    ]


def auxiliary_table(values: Mapping[Path, Mapping[str, Any]], by_block: Mapping[str, list[int]]) -> dict[str, Any]:
    witness = values[AUX_WITNESS]
    if values[AUX_REPAIR]["claim_flags"]["STRICT_386_AUXILIARY_Q_SIGN_REPAIR_APPLIED"] is not True:
        raise ValueError("auxiliary q sign repair unavailable")
    indices = [index for name in (
        "AUX_ETA", "AUX_F_HAT", "AUX_V", "AUX_F_HAT_STAR", "AUX_V_STAR", "AUX_ETA_STAR"
    ) for index in by_block[name]]
    matrix = [[Fraction() for _ in indices] for _ in indices]
    for target, source, coefficient in witness["entries"]:
        matrix[target][source] = Fraction(coefficient)
    return table(
        "AUXILIARY_SPLIT_Q", "AUXILIARY_36", "AUXILIARY_36", indices, indices, {ZERO: matrix},
        role="repaired generalized-auxiliary contractible differential",
        origin="STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1 with certified +I4 cotangent sign repair",
    )


def cone_tables(by_block: Mapping[str, list[int]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    evolution = ConstraintAdjustedWeylCottonEvolution.build()
    evolution.verify()
    equation_derivative = (
        sp.eye(26).col_join(sp.zeros(14, 26)),
        *tuple(
            evolution.evolution_spatial_coefficients[axis].col_join(
                evolution.source_compatibility_spatial_coefficients[axis]
            )
            for axis in range(3)
        ),
    )
    equation_zero = evolution.evolution_zeroth_coefficient.col_join(
        evolution.source_compatibility_zeroth_coefficient
    )
    identity_derivative = (
        sp.zeros(14, 26).row_join(sp.eye(14)),
        *tuple(
            (-evolution.source_compatibility_spatial_coefficients[axis]).row_join(
                evolution.constraint_spatial_coefficients[axis]
            )
            for axis in range(3)
        ),
    )
    identity_zero = (-evolution.source_compatibility_zeroth_coefficient).row_join(
        evolution.constraint_zeroth_coefficient
    )
    equation_adjoint = tuple(-matrix.T for matrix in equation_derivative) + (equation_zero.T,)
    identity_adjoint = tuple(-matrix.T for matrix in identity_derivative) + (identity_zero.T,)
    e = {multiindex: fraction_matrix(matrix) for multiindex, matrix in zip(
        (*DERIVATIVES, ZERO),
        (*equation_derivative, equation_zero),
        strict=True,
    )}
    n = {multiindex: fraction_matrix(matrix) for multiindex, matrix in zip(
        (*DERIVATIVES, ZERO),
        (*identity_derivative, identity_zero),
        strict=True,
    )}
    e_sharp = {multiindex: fraction_matrix(matrix) for multiindex, matrix in zip(
        (*DERIVATIVES, ZERO), equation_adjoint, strict=True,
    )}
    n_sharp = {multiindex: fraction_matrix(matrix) for multiindex, matrix in zip(
        (*DERIVATIVES, ZERO), identity_adjoint, strict=True,
    )}

    def signed(coefficients: Mapping[tuple[int, int, int, int], Sequence[Sequence[Fraction]]], sign: int) -> dict[tuple[int, int, int, int], list[list[Fraction]]]:
        return {multiindex: scale_matrix(matrix, sign) for multiindex, matrix in coefficients.items()}

    def one(source: str, target: str, sign: int = 1) -> dict[tuple[int, int, int, int], list[list[Fraction]]]:
        if len(by_block[source]) != len(by_block[target]):
            raise ValueError("incidence identity dimension drift")
        return {ZERO: scale_matrix(identity(len(by_block[source])), sign)}

    specifications = (
        ("CONE_X_U_TO_X_EQ", "CONE_X_U", "CONE_X_EQ", e, "Ecurv"),
        ("CONE_X_EQ_TO_X_ID", "CONE_X_EQ", "CONE_X_ID", n, "Ncurv"),
        ("CONE_X_U_TO_Y_U", "CONE_X_U", "CONE_Y_U", one("CONE_X_U", "CONE_Y_U"), "+I"),
        ("CONE_X_EQ_TO_Y_EQ", "CONE_X_EQ", "CONE_Y_EQ", one("CONE_X_EQ", "CONE_Y_EQ"), "+I"),
        ("CONE_Y_U_TO_Y_EQ", "CONE_Y_U", "CONE_Y_EQ", signed(e, -1), "-Ecurv"),
        ("CONE_X_ID_TO_Y_ID", "CONE_X_ID", "CONE_Y_ID", one("CONE_X_ID", "CONE_Y_ID"), "+I"),
        ("CONE_Y_EQ_TO_Y_ID", "CONE_Y_EQ", "CONE_Y_ID", signed(n, -1), "-Ncurv"),
        ("CONE_Y_ID_SHARP_TO_X_ID_SHARP", "CONE_Y_ID_SHARP", "CONE_X_ID_SHARP", one("CONE_Y_ID_SHARP", "CONE_X_ID_SHARP"), "+I"),
        ("CONE_X_ID_SHARP_TO_X_EQ_SHARP", "CONE_X_ID_SHARP", "CONE_X_EQ_SHARP", n_sharp, "NcurvSharp"),
        ("CONE_Y_EQ_SHARP_TO_X_EQ_SHARP", "CONE_Y_EQ_SHARP", "CONE_X_EQ_SHARP", one("CONE_Y_EQ_SHARP", "CONE_X_EQ_SHARP"), "+I"),
        ("CONE_X_EQ_SHARP_TO_X_U_SHARP", "CONE_X_EQ_SHARP", "CONE_X_U_SHARP", e_sharp, "EcurvSharp"),
        ("CONE_Y_U_SHARP_TO_X_U_SHARP", "CONE_Y_U_SHARP", "CONE_X_U_SHARP", one("CONE_Y_U_SHARP", "CONE_X_U_SHARP"), "+I"),
        ("CONE_Y_ID_SHARP_TO_Y_EQ_SHARP", "CONE_Y_ID_SHARP", "CONE_Y_EQ_SHARP", signed(n_sharp, -1), "-NcurvSharp"),
        ("CONE_Y_EQ_SHARP_TO_Y_U_SHARP", "CONE_Y_EQ_SHARP", "CONE_Y_U_SHARP", signed(e_sharp, -1), "-EcurvSharp"),
    )
    output = [
        table(
            table_id, source, target, by_block[source], by_block[target], coefficients,
            role=f"split mapping-cylinder arrow {operator}",
            origin="Rank14EquationSDRBoundary exact lower-order tables plus curvature_mapping_cylinder_kernel incidence signs",
        )
        for table_id, source, target, coefficients, operator in specifications
    ]
    return output, {
        "Ecurv_sha256": digest({str(key): [[q(entry) for entry in row] for row in matrix] for key, matrix in sorted(e.items())}),
        "Ncurv_sha256": digest({str(key): [[q(entry) for entry in row] for row in matrix] for key, matrix in sorted(n.items())}),
        "EcurvSharp_sha256": digest({str(key): [[q(entry) for entry in row] for row in matrix] for key, matrix in sorted(e_sharp.items())}),
        "NcurvSharp_sha256": digest({str(key): [[q(entry) for entry in row] for row in matrix] for key, matrix in sorted(n_sharp.items())}),
    }


def sparse_multiply(left: Sparse, right: Sparse) -> Sparse:
    by_row: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), coefficient in right.items():
        by_row.setdefault(row, []).append((column, coefficient))
    output: Sparse = {}
    for (row, middle), left_coefficient in left.items():
        for column, right_coefficient in by_row.get(middle, ()):
            key = (row, column)
            value = output.get(key, Fraction()) + left_coefficient * right_coefficient
            if value:
                output[key] = value
            else:
                output.pop(key, None)
    return output


def sparse_scale_rows(matrix: Sparse, diagonal: Sequence[int]) -> Sparse:
    return {(row, column): coefficient * diagonal[row] for (row, column), coefficient in matrix.items() if coefficient * diagonal[row]}


def sparse_scale_columns(matrix: Sparse, diagonal: Sequence[int]) -> Sparse:
    return {(row, column): coefficient * diagonal[column] for (row, column), coefficient in matrix.items() if coefficient * diagonal[column]}


def combined_coefficients(tables: Sequence[Mapping[str, Any]]) -> dict[tuple[int, int, int, int], Sparse]:
    output: dict[tuple[int, int, int, int], Sparse] = {}
    for operator in tables:
        for coefficient in operator["coefficients"]:
            multiindex = tuple(coefficient["multiindex"])
            matrix = output.setdefault(multiindex, {})
            for target, source, raw in coefficient["entries"]:
                key = (target, source)
                if key in matrix:
                    raise ValueError(f"overlapping q1 entry at {multiindex} {key}")
                matrix[key] = Fraction(raw)
    return output


def suspended_cyclicity_defects(
    tables: Sequence[Mapping[str, Any]], pairing: Mapping[str, Any]
) -> tuple[int, dict[str, int]]:
    omega = {
        (entry["left_index"], entry["right_index"]): Fraction(entry["coefficient"])
        for entry in pairing["pairing_serialization"]["entries"]
    }
    rows = pairing["component_basis"]["rows"]
    degree = [-1 if row["degree"] % 2 else 1 for row in rows]
    suspension = pairing["suspension_serialization"]["R_diagonal"]
    omega_r = sparse_scale_columns(omega, suspension)
    by_sector = {"endpoint": 0, "auxiliary": 0, "mapping_cone": 0}
    total = 0
    for multiindex, matrix in combined_coefficients(tables).items():
        formal_transpose = {
            (column, row): coefficient * (-1 if sum(multiindex) % 2 else 1)
            for (row, column), coefficient in matrix.items()
        }
        left = sparse_multiply(formal_transpose, omega_r)
        right = sparse_multiply(omega_r, sparse_scale_rows(matrix, degree))
        defects = {key for key in set(left) | set(right) if left.get(key, Fraction()) != right.get(key, Fraction())}
        total += len(defects)
        for row, column in defects:
            sector = "endpoint" if max(row, column) < 30 else "auxiliary" if max(row, column) < 66 else "mapping_cone"
            by_sector[sector] += 1
    return total, by_sector


def auxiliary_square_defects(operator: Mapping[str, Any]) -> int:
    entries = operator["coefficients"][0]["entries"]
    matrix = {(target - 30, source - 30): Fraction(raw) for target, source, raw in entries}
    return len(sparse_multiply(matrix, matrix))


INPUTS = (
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "published 386-row basis, pairing and suspension diagonals"),
    (ENDPOINT_BRIDGE, "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1", "coefficientwise Gate endpoint q1 identification"),
    (ENDPOINT_WITNESS, "strict-cylinder-coordinate-to-covariant-symmetric-four-jet-v1", "exact 700-column coordinate/covariant bridge witness"),
    (Q1_AST, "STRICT_PORTABLE_LOCAL_Q1_AST_V1", "portable minimal q1 and exact natural square-zero theorem"),
    (UNIVERSAL, "STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1", "all 700 coordinate-jet Bach input columns"),
    (AUX_WITNESS, "strict-386-auxiliary-q-sign-witness-v1", "executable repaired 36-row auxiliary q entries"),
    (AUX_REPAIR, "STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1", "certified source/ledger/pairing sign repair"),
    (SUSPENSION, "STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1", "Gate suspended-adjoint theorem"),
    (ENDPOINT_PAYLOAD, "pure-weyl-prolonged-metric-endpoint-coefficients-v1", "causal endpoint coefficient payload"),
    (CONE_BOUNDARY, "pure-weyl-rank14-equation-sdr-boundary-v1", "full lower-order Ecurv/Ncurv tables and PBW identity hashes"),
    (CONE_KERNEL, "pure-weyl-curvature-mapping-cylinder-kernel-v1", "split cone incidence and cotangent signs"),
    (CONE_SUBSTITUTION, "pure-weyl-curvature-mapping-cylinder-substitution-v1", "coefficientwise-complete prolonged-Q substitution authority"),
)


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    pairing = values[PAIRING]
    if pairing["component_basis"]["dimension"] != 386 or pairing["pairing_serialization"]["rank"] != 386:
        raise ValueError("published carrier unavailable")
    if values[CONE_SUBSTITUTION]["coefficientwise_complete_prolonged_Q"] is not True:
        raise ValueError("mapping-cylinder coefficient substitution unavailable")
    if values[CONE_KERNEL]["mapping_cylinder"]["split_cone_contractible"] is not True:
        raise ValueError("mapping-cylinder contraction unavailable")

    by_block = blocks(pairing)
    endpoint = endpoint_tables(values, by_block)
    auxiliary = auxiliary_table(values, by_block)
    cone, primitive_hashes = cone_tables(by_block)
    tables = endpoint + [auxiliary] + cone
    defect_count, sector_defects = suspended_cyclicity_defects(tables, pairing)
    if defect_count:
        raise ValueError(f"full q1 suspended cyclicity has {defect_count} coefficient defects")
    aux_square = auxiliary_square_defects(auxiliary)
    if aux_square:
        raise ValueError("auxiliary q1 is not nilpotent")
    if values[Q1_AST]["square_zero_theorem"]["status"] != "CERTIFIED":
        raise ValueError("endpoint natural square-zero theorem unavailable")
    evolution = ConstraintAdjustedWeylCottonEvolution.build()
    evolution.verify()
    if evolution.commuting_symbol_defect + evolution.sphere_curvature_correction != sp.zeros(14, 26):
        raise ValueError("curved Ecurv/Ncurv PBW identity drift")

    counts = {
        "operator_tables": len(tables),
        "coefficient_multiindex_tables": sum(item["coefficient_multiindices"] for item in tables),
        "nonzero_rational_coefficients": sum(item["nonzero_coefficients"] for item in tables),
        "by_sector": {
            "endpoint_30": sum(item["nonzero_coefficients"] for item in endpoint),
            "auxiliary_36": auxiliary["nonzero_coefficients"],
            "mapping_cone_320": sum(item["nonzero_coefficients"] for item in cone),
        },
    }
    q1_serialization = {
        "format": "finite parallel-coefficient symmetrized-covariant-jet tables",
        "orientation": "entry[target_global_index,source_global_index]",
        "coefficient_field": "Q",
        "carrier_dimension": 386,
        "carrier_split": "30+36+320",
        "maximum_order": max(item["maximum_order"] for item in tables),
        "counts": counts,
        "tables": tables,
    }
    nilpotency = {
        "full_q1_squared_zero": True,
        "cross_sector_arrows": 0,
        "sector_replays": {
            "endpoint_30": {
                "defects": 0,
                "proof_mode": "exact Bach-flat natural q1 square-zero theorem transported through the independently replayed 80-table endpoint content bridge",
                "serialized_common_q1_sha256": values[ENDPOINT_BRIDGE]["coefficientwise_identification"]["common_q1_sha256"],
            },
            "auxiliary_36": {
                "defects": aux_square,
                "proof_mode": "direct exact sparse multiplication of the serialized rational matrix",
            },
            "mapping_cone_320": {
                "defects": 0,
                "proof_mode": "exact first-order Ecurv/Ncurv coefficient reconstruction with the unit-S3 PBW commutator correction, cotangent formal adjoints and cone incidence",
                "Ncurv_Ecurv_identity": "zero including the noncommuting unit-S3 correction",
            },
        },
        "warning": "The endpoint and cone rows are covariant differential operators; nilpotency is not a naive commutative-polynomial matrix square. Their exact natural/PBW identities are replayed in their authoritative calculi.",
    }
    cyclicity = {
        "identity": "q1^(T,formal) Omega R = Omega R D q1",
        "equivalent_suspended_adjoint_identity": "R q1^sharp_G R = D q1",
        "D_diagonal": "(-1)^component_degree",
        "R_diagonal_source": "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1 suspension_serialization.R_diagonal",
        "coefficientwise_multiindices_checked": len(combined_coefficients(tables)),
        "exact_defects": defect_count,
        "sector_defects": sector_defects,
        "ordinary_adjoint_used_on_endpoint": False,
        "reason": "The Gate endpoint uses the already certified suspension character R; the 356-row complement has R=+I and therefore reduces to ordinary odd cyclicity.",
    }
    snapshot = {
        "kind": "STRICT_386_UNARY_OPERATOR_SNAPSHOT",
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "suspension_sha256": pairing["canonical_hashes"]["suspension_serialization_sha256"],
        "q1_tables_sha256": digest(tables),
        "primitive_curvature_table_sha256": primitive_hashes,
    }
    snapshot["snapshot_sha256"] = digest(snapshot)

    projection = {
        "scope": {
            "theory": "strict pure-Weyl unary BV complex",
            "background": "unit conformal cylinder",
            "basis": pairing["component_basis"]["ordering"],
            "carrier_dimension": 386,
            "arithmetic": "exact rational finite jet tables",
            "coordinate_presentation": "split differential; T/A/B canonical shear remains a separate degree-zero operator",
        },
        "q1_serialization": q1_serialization,
        "nilpotency_replay": nilpotency,
        "suspended_cyclicity_replay": cyclicity,
        "unary_snapshot": snapshot,
        "foundational_strength": {
            "finite_serialization_and_replay_base": "PRA",
            "choice_operation_added": False,
            "infinite_selection_added": False,
            "analytic_semantics_imported": "smooth compact-support covariant differential-operator semantics on the unit cylinder",
            "weakest_base_for_full_analytic_causal_theorem": "NOT_ESTABLISHED",
        },
        "gate_disposition": {
            "full_386_component_basis_serialized": True,
            "full_386_component_pairing_serialized": True,
            "full_386_q1_component_jet_tables_serialized": True,
            "full_386_q1_squared_zero_replayed": True,
            "full_386_q1_suspended_cyclicity_replayed": True,
            "unary_snapshot_hash_established": True,
            "one_common_gate_a_snapshot_hash_accepted": False,
            "classical_import_gate_a_status": "FAIL_CLOSED",
        },
        "claim_flags": {
            "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_SERIALIZED": True,
            "STRICT_386_FULL_Q1_SQUARED_ZERO_REPLAYED": True,
            "STRICT_386_FULL_Q1_SUSPENDED_CYCLICITY_REPLAYED": True,
            "STRICT_386_UNARY_SNAPSHOT_HASH_ESTABLISHED": True,
            "STRICT_386_FULL_SDR_OPERATOR_TABLES_SERIALIZED": False,
            "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
            "STRICT_386_LOCAL_D_CERTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "does_not_establish": [
            "component tables for H_alg, endpoint inclusion/projection, the canonical T/A/B shear, or advanced/retarded Green actions",
            "one accepted common Gate-A snapshot binding q1, q2, D, pairing, SDR and causal Green data",
            "q2 or local D on the same 386-row causal carrier",
            "a weakest-foundation calibration of the imported analytic Green theorem",
            "a Hadamard state, BRST Ward theorem, positivity result, renormalized Lorentzian products, QME restoration, residual transfer or Lorentzian quantum theory",
        ],
        "next_gate": "Serialize H_alg, endpoint inclusion/projection, the degree-zero T/A/B shear and advanced/retarded Green actions against this unary snapshot, independently replay the SDR and suspended Green-adjoint identities componentwise, and only then accept a common Gate-A snapshot hash before binding q2 and local D.",
        "canonical_hashes": {
            "q1_serialization_sha256": digest(q1_serialization),
            "nilpotency_replay_sha256": digest(nilpotency),
            "suspended_cyclicity_replay_sha256": digest(cyclicity),
            "unary_snapshot_sha256": digest(snapshot),
        },
    }
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-full-q1-component-jet-table-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-full-q1-component-jet-table-v1.schema.json",
        "result_id": "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1",
        "result_kind": "SAME_THEORY_FULL_UNARY_COMPONENT_JET_SERIALIZATION",
        "result_state": "FULL_386_Q1_SERIALIZED_NILPOTENT_SUSPENDED_CYCLIC_SDR_AND_COMMON_GATE_SNAPSHOT_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "cfc609324416133a1a0c712e2f706d3bc3fddd88",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Can the complete strict 386-row split-basis unary BV differential be emitted as exact receiver-readable component jet tables and replayed for nilpotency and the certified Gate suspended cyclicity convention?",
        "answer": "Yes. The artifact binds the already published 386-row basis and rank-386 odd pairing to all three Gate endpoint arrows, the repaired 36-row generalized-auxiliary differential, and all fourteen primal/cotangent mapping-cylinder arrows. Every coefficient is rational and indexed by a symmetrized covariant derivative multiindex. The endpoint contributes its independently matched 80 multiindex tables, the auxiliary block contributes its exact sparse matrix, and the 320-row cone contributes the full lower-order Ecurv, Ncurv and formal-adjoint tables plus incidence identities. Nilpotency replays sector by sector in the appropriate exact calculus, and every serialized coefficient satisfies q1^(T,formal) Omega R=Omega R D q1 with zero defects. This establishes a content-addressed unary snapshot, but it does not yet serialize the SDR, shear or Green actions and therefore does not pass classical import Gate A or promote any Hadamard/QME claim.",
        **projection,
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_schema_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ],
            "implementation": [
                {"path": "quantum-weyl/classical_import/strict_386_endpoint_q1_content_bridge.py", "sha256": sha(HERE / "strict_386_endpoint_q1_content_bridge.py"), "role": "independent endpoint table reconstruction"},
                {"path": "covariant_completion/curved_operator/rank14_equation_sdr_boundary.py", "sha256": sha(ROOT / "covariant_completion/curved_operator/rank14_equation_sdr_boundary.py"), "role": "complete lower-order curvature and formal-adjoint table reconstruction"},
            ],
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_full_q1_component_jet_table.py",
            "expected_digest": digest(projection),
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.md",
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    counts = value["q1_serialization"]["counts"]
    snapshot = value["unary_snapshot"]
    nilpotency = value["nilpotency_replay"]
    cyclicity = value["suspended_cyclicity_replay"]
    return f"""# Strict 386-row full q1 component jet table v1

## Outcome

{value['answer']}

## Complete unary carrier

- Carrier: **386 rows**, split `30+36+320`.
- Operator tables: **{counts['operator_tables']}**.
- Symmetrized-covariant coefficient tables: **{counts['coefficient_multiindex_tables']}**.
- Nonzero exact rational coefficients: **{counts['nonzero_rational_coefficients']}**.
- Endpoint / auxiliary / cone coefficients: `{counts['by_sector']}`.
- Maximum differential order: **{value['q1_serialization']['maximum_order']}**.

The primitive differential is written in split coordinates.  The `T/A/B`
attachment is a separate degree-zero canonical shear and has not been
silently inserted as extra q1 arrows.

## Exact replays

- Full q1 squared: **{nilpotency['full_q1_squared_zero']}**.
- Cross-sector primitive arrows: **{nilpotency['cross_sector_arrows']}**.
- Suspended cyclicity defects: **{cyclicity['exact_defects']}** over
  **{cyclicity['coefficientwise_multiindices_checked']}** distinct derivative
  multiindices.
- Identity: `{cyclicity['identity']}`.

The endpoint uses the certified Gate suspension character.  On the 356-row
complement `R=+I`, so the same identity reduces to ordinary odd cyclicity.

## Unary snapshot

The basis, pairing, suspension and q1 bytes are bound by:

`{snapshot['snapshot_sha256']}`

This is a unary snapshot, not yet the accepted common Gate-A snapshot.

## Does not establish

""" + "\n".join(f"- {item}" for item in value["does_not_establish"]) + f"""

## Next gate

{value['next_gate']}

## Reproduction

```text
PYTHONPATH=<repository-root>:<sympy-site> python3 quantum-weyl/classical_import/build_strict_386_full_q1_component_jet_table.py --check
PYTHONPATH=<repository-root>:<sympy-site> python3 quantum-weyl/classical_import/check_strict_386_full_q1_component_jet_table.py
PYTHONPATH=<repository-root>:<sympy-site> python3 quantum-weyl/classical_import/verify_strict_386_full_q1_component_jet_table.py
PYTHONPATH=<repository-root>:<sympy-site> python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_full_q1_component_jet_table.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [
        str(path.relative_to(ROOT))
        for path, content in ((RESULT, result), (REPORT, report))
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
