#!/usr/bin/env python3
"""Build exact graph-coordinate q1, SDR and suspension component jets."""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
REPORT = HERE / "REPORT_STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.md"

Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
LOCAL_SDR = HERE / "certificates/STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.json"
SHEAR = HERE / "certificates/STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1.json"
SUBSTITUTION = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json"
KERNEL = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_kernel.json"
CORE_CHAIN = ROOT / "covariant_completion/certificates/curved_core_curvature_chain_map.json"

ZERO = (0, 0, 0, 0)
Multiindex = tuple[int, int, int, int]
Sparse = dict[tuple[int, int], Fraction]
Operator = dict[Multiindex, Sparse]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def q(value: Fraction | int | str) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def decode_table(value: Mapping[str, Any]) -> Operator:
    return {
        tuple(item["multiindex"]): {
            (target, source): Fraction(raw)
            for target, source, raw in item["entries"]
        }
        for item in value["coefficients"]
    }


def add(left: Operator, right: Operator, coefficient: int | Fraction = 1) -> Operator:
    coefficient = Fraction(coefficient)
    output = {index: dict(matrix) for index, matrix in left.items()}
    for index, matrix in right.items():
        target = output.setdefault(index, {})
        for key, value in matrix.items():
            target[key] = target.get(key, Fraction()) + coefficient * value
            if not target[key]:
                target.pop(key)
    return {index: matrix for index, matrix in output.items() if matrix}


def scale(operator: Operator, coefficient: int | Fraction) -> Operator:
    coefficient = Fraction(coefficient)
    return {
        index: {key: coefficient * value for key, value in matrix.items() if coefficient * value}
        for index, matrix in operator.items()
        if coefficient
    }


def sparse_multiply(left: Sparse, right: Sparse) -> Sparse:
    by_row: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), value in right.items():
        by_row.setdefault(row, []).append((column, value))
    output: Sparse = {}
    for (row, middle), value in left.items():
        for column, other in by_row.get(middle, ()):
            key = (row, column)
            output[key] = output.get(key, Fraction()) + value * other
    return {key: value for key, value in output.items() if value}


def compose(left: Operator, right: Operator) -> tuple[Operator, int]:
    """Compose tables, rejecting every nonzero positive-order/positive-order path."""

    output: Operator = {}
    forbidden = 0
    for left_index, left_matrix in left.items():
        for right_index, right_matrix in right.items():
            product = sparse_multiply(left_matrix, right_matrix)
            if not product:
                continue
            if sum(left_index) and sum(right_index):
                forbidden += len(product)
                continue
            index = tuple(a + b for a, b in zip(left_index, right_index, strict=True))
            output = add(output, {index: product})
    return output, forbidden


def compose_safe(left: Operator, right: Operator, label: str) -> Operator:
    output, forbidden = compose(left, right)
    if forbidden:
        raise ValueError(f"{label} requires {forbidden} unproved derivative/derivative products")
    return output


def defects(left: Operator, right: Operator) -> int:
    return sum(
        len(set(left.get(index, {})) | set(right.get(index, {})))
        for index in set(left) | set(right)
        if left.get(index, {}) != right.get(index, {})
    )


def blocks(pairing: Mapping[str, Any]) -> dict[str, list[int]]:
    output: dict[str, list[int]] = {}
    for row in pairing["component_basis"]["rows"]:
        output.setdefault(row["block"], []).append(row["index"])
    return output


def remap(
    operator: Operator,
    source_old: Sequence[int],
    source_new: Sequence[int],
    target_old: Sequence[int],
    target_new: Sequence[int],
) -> Operator:
    source = dict(zip(source_old, source_new, strict=True))
    target = dict(zip(target_old, target_new, strict=True))
    return {
        index: {(target[row], source[column]): value for (row, column), value in matrix.items()}
        for index, matrix in operator.items()
    }


def encode_operator(
    map_id: str,
    shape: Sequence[int],
    degree: int,
    operator: Operator,
    *,
    role: str,
    proof_mode: str,
) -> dict[str, Any]:
    coefficients = [
        {
            "multiindex": list(index),
            "entries": [[row, column, q(value)] for (row, column), value in sorted(matrix.items())],
        }
        for index, matrix in sorted(operator.items())
    ]
    value = {
        "map_id": map_id,
        "shape": list(shape),
        "degree": degree,
        "orientation": "entry[target_global_index,source_global_index]",
        "maximum_order": max((sum(index) for index in operator), default=0),
        "coefficient_multiindices": len(coefficients),
        "nonzero_coefficients": sum(len(item["entries"]) for item in coefficients),
        "role": role,
        "proof_mode": proof_mode,
        "coefficients": coefficients,
    }
    value["sha256"] = digest({key: value[key] for key in ("shape", "degree", "coefficients")})
    return value


def encode_table(
    table_id: str,
    source_block: str,
    target_block: str,
    source_indices: Sequence[int],
    target_indices: Sequence[int],
    operator: Operator,
    *,
    role: str,
    formal_word: str,
) -> dict[str, Any]:
    value = encode_operator(
        table_id,
        [len(target_indices), len(source_indices)],
        1,
        operator,
        role=role,
        proof_mode="exact fixed-basis realization of the reduced formal graph block",
    )
    value.update({
        "table_id": value.pop("map_id"),
        "source_block": source_block,
        "target_block": target_block,
        "source_global_indices": list(source_indices),
        "target_global_indices": list(target_indices),
        "formal_word": formal_word,
    })
    value["sha256"] = digest(value["coefficients"])
    return value


def decode_local_map(value: Mapping[str, Any]) -> Operator:
    return {
        ZERO: {
            (item["target"], item["source"]): Fraction(item["coefficient"])
            for item in value["entries"]
        }
    }


def combine_tables(tables: Sequence[Mapping[str, Any]]) -> Operator:
    output: Operator = {}
    for table in tables:
        output = add(output, decode_table(table))
    return output


def identity_operator(size: int) -> Operator:
    return {ZERO: {(index, index): Fraction(1) for index in range(size)}}


def formal_transpose(operator: Operator) -> Operator:
    return {
        index: {
            (column, row): value * (-1 if sum(index) % 2 else 1)
            for (row, column), value in matrix.items()
        }
        for index, matrix in operator.items()
    }


def cyclic_defect(
    differential: Operator,
    omega: Operator,
    suspension: Operator,
    degree_sign: Sequence[int],
) -> Operator:
    omega_suspension = compose_safe(omega, suspension, "Omega suspension")
    signed_differential = {
        index: {(row, column): value * degree_sign[row] for (row, column), value in matrix.items()}
        for index, matrix in differential.items()
    }
    left = compose_safe(formal_transpose(differential), omega_suspension, "cyclic left side")
    right = compose_safe(omega_suspension, signed_differential, "cyclic right side")
    return add(left, right, -1)


INPUTS = (
    (Q1, "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1", "fixed split unary component jets"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "fixed basis, odd pairing and split suspension"),
    (LOCAL_SDR, "STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1", "exact split local SDR"),
    (SHEAR, "STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1", "exact canonical shear and inverse"),
    (SUBSTITUTION, "pure-weyl-curvature-mapping-cylinder-substitution-v1", "coefficient-complete graph-Q and formal SDR authority"),
    (KERNEL, "pure-weyl-curvature-mapping-cylinder-kernel-v1", "formal word, sign and chain-relation authority"),
    (CORE_CHAIN, "pure-weyl-curved-core-curvature-chain-map-v1", "curved primal chain-square authority"),
)


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    q1, pairing, local_sdr, shear, substitution, kernel, core_chain = (
        values[path] for path, _, _ in INPUTS
    )
    if not q1["claim_flags"]["STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_SERIALIZED"]:
        raise ValueError("split q1 unavailable")
    if not local_sdr["claim_flags"]["STRICT_386_LOCAL_SDR_IDENTITIES_REPLAYED"]:
        raise ValueError("split SDR unavailable")
    if not shear["claim_flags"]["STRICT_386_CANONICAL_SHEAR_INVERSE_REPLAYED"]:
        raise ValueError("canonical shear unavailable")
    if not substitution["coefficientwise_complete_prolonged_Q"]:
        raise ValueError("coefficient-complete formal graph authority unavailable")
    if not substitution["kernel"]["all_16_blocks_Q_squared_checked"] or not substitution["kernel"]["all_16_blocks_graph_SDR_checked"]:
        raise ValueError("formal graph q/SDR replay unavailable")

    index = blocks(pairing)
    split_tables = deepcopy(q1["q1_serialization"]["tables"])
    split = {item["table_id"]: decode_table(item) for item in split_tables}
    forward = {item["table_id"]: decode_table(item) for item in shear["canonical_transform"]["forward"]["tables"]}
    inverse = {item["table_id"]: decode_table(item) for item in shear["canonical_transform"]["inverse"]["tables"]}

    def moved(table: str, source_old: str, source_new: str, target_old: str, target_new: str) -> Operator:
        return remap(
            forward[table], index[source_old], index[source_new], index[target_old], index[target_new]
        )

    central = compose_safe(
        compose_safe(forward["A_PRIMAL"], split["ENDPOINT_M_TO_E"], "A Eaux"),
        forward["A_FORCED_PARTNER"],
        "A Eaux (-Asharp)",
    )
    graph_specs = (
        ("GRAPH_Y_ID_SHARP_TO_ENDPOINT_G", "CONE_Y_ID_SHARP", "ENDPOINT_G", moved("B_FORCED_PARTNER", "CONE_X_ID_SHARP", "CONE_Y_ID_SHARP", "ENDPOINT_G", "ENDPOINT_G"), "-Bsharp"),
        ("GRAPH_Y_EQ_SHARP_TO_ENDPOINT_M", "CONE_Y_EQ_SHARP", "ENDPOINT_M", moved("A_FORCED_PARTNER", "CONE_X_EQ_SHARP", "CONE_Y_EQ_SHARP", "ENDPOINT_M", "ENDPOINT_M"), "-Asharp"),
        ("GRAPH_Y_U_SHARP_TO_ENDPOINT_E", "CONE_Y_U_SHARP", "ENDPOINT_E", moved("T_FORCED_PARTNER", "CONE_X_U_SHARP", "CONE_Y_U_SHARP", "ENDPOINT_E", "ENDPOINT_E"), "-Tsharp"),
        ("GRAPH_ENDPOINT_M_TO_Y_U", "ENDPOINT_M", "CONE_Y_U", scale(moved("T_PRIMAL", "ENDPOINT_M", "ENDPOINT_M", "CONE_X_U", "CONE_Y_U"), -1), "-T"),
        ("GRAPH_ENDPOINT_E_TO_Y_EQ", "ENDPOINT_E", "CONE_Y_EQ", scale(moved("A_PRIMAL", "ENDPOINT_E", "ENDPOINT_E", "CONE_X_EQ", "CONE_Y_EQ"), -1), "-A"),
        ("GRAPH_ENDPOINT_I_TO_Y_ID", "ENDPOINT_I", "CONE_Y_ID", scale(moved("B_PRIMAL", "ENDPOINT_I", "ENDPOINT_I", "CONE_X_ID", "CONE_Y_ID"), -1), "-B"),
        ("GRAPH_X_EQ_SHARP_TO_X_EQ", "CONE_X_EQ_SHARP", "CONE_X_EQ", central, "-A Eaux Asharp"),
        ("GRAPH_Y_U_SHARP_TO_X_EQ", "CONE_Y_U_SHARP", "CONE_X_EQ", moved("FORWARD_CROSS_A_TSHARP", "CONE_X_U_SHARP", "CONE_Y_U_SHARP", "CONE_X_EQ", "CONE_X_EQ"), "-A Tsharp"),
        ("GRAPH_X_EQ_SHARP_TO_Y_U", "CONE_X_EQ_SHARP", "CONE_Y_U", remap(inverse["INVERSE_CROSS_T_ASHARP"], index["CONE_X_EQ_SHARP"], index["CONE_X_EQ_SHARP"], index["CONE_X_U"], index["CONE_Y_U"]), "-T Asharp"),
    )
    graph_tables = [
        encode_table(
            table_id, source_block, target_block, index[source_block], index[target_block], operator,
            role="surviving attachment after exact formal chain-relation reduction",
            formal_word=formal_word,
        )
        for table_id, source_block, target_block, operator, formal_word in graph_specs
    ]
    all_q_tables = [*split_tables, *graph_tables]
    q_graph = combine_tables(all_q_tables)
    if len(all_q_tables) != 27 or len(q_graph) != 70 or sum(len(matrix) for matrix in q_graph.values()) != 4374:
        raise ValueError("graph q1 inventory drift")

    h = decode_local_map(local_sdr["component_maps"]["H_alg"])
    identity_30 = {ZERO: {(row, row): Fraction(1) for row in range(30)}}
    identity_386 = identity_operator(386)
    i_graph = identity_30
    for table_id in ("T_PRIMAL", "A_PRIMAL", "B_PRIMAL"):
        i_graph = add(i_graph, forward[table_id])
    p_graph = identity_30
    for table_id in ("INVERSE_T_FORCED_PARTNER", "INVERSE_A_FORCED_PARTNER", "INVERSE_B_FORCED_PARTNER"):
        p_graph = add(p_graph, inverse[table_id])
    p_end = compose_safe(i_graph, p_graph, "i_graph p_graph")
    p_alg = add(identity_386, p_end, -1)

    qh = add(compose_safe(q_graph, h, "q_graph H"), compose_safe(h, q_graph, "H q_graph"))
    pi = compose_safe(p_graph, i_graph, "p_graph i_graph")
    pend_squared = compose_safe(p_end, p_end, "P_end squared")
    palg_squared = compose_safe(p_alg, p_alg, "P_alg squared")
    side_conditions = {
        "H_squared_defects": defects(compose_safe(h, h, "H squared"), {}),
        "H_i_graph_defects": defects(compose_safe(h, i_graph, "H i_graph"), {}),
        "p_graph_H_defects": defects(compose_safe(p_graph, h, "p_graph H"), {}),
        "P_end_squared_defects": defects(pend_squared, p_end),
        "P_alg_squared_defects": defects(palg_squared, p_alg),
        "P_end_P_alg_defects": defects(compose_safe(p_end, p_alg, "P_end P_alg"), {}),
        "P_alg_P_end_defects": defects(compose_safe(p_alg, p_end, "P_alg P_end"), {}),
    }
    if defects(qh, p_alg) or defects(pi, identity_30) or any(side_conditions.values()):
        raise ValueError("direct graph SDR replay failed")

    omega = {ZERO: {
        (entry["left_index"], entry["right_index"]): Fraction(entry["coefficient"])
        for entry in pairing["pairing_serialization"]["entries"]
    }}
    split_r = {ZERO: {
        (row, row): Fraction(value)
        for row, value in enumerate(pairing["suspension_serialization"]["R_diagonal"])
    }}
    shear_forward = identity_386
    shear_inverse = identity_386
    for table in shear["canonical_transform"]["forward"]["tables"]:
        shear_forward = add(shear_forward, decode_table(table))
    for table in shear["canonical_transform"]["inverse"]["tables"]:
        shear_inverse = add(shear_inverse, decode_table(table))
    graph_r = compose_safe(compose_safe(shear_forward, split_r, "S R"), shear_inverse, "S R S^-1")
    graph_r_squared = compose_safe(graph_r, graph_r, "R_graph squared")
    graph_r_off_diagonal = sum(row != column for matrix in graph_r.values() for row, column in matrix)
    if len(graph_r) != 1 or sum(len(matrix) for matrix in graph_r.values()) != 394 or graph_r_off_diagonal != 8 or defects(graph_r_squared, identity_386):
        raise ValueError("transported suspension replay failed")

    degree_sign = [-1 if row["degree"] % 2 else 1 for row in pairing["component_basis"]["rows"]]
    split_r_cyclic_defect = cyclic_defect(q_graph, omega, split_r, degree_sign)
    graph_r_cyclic_defect = cyclic_defect(q_graph, omega, graph_r, degree_sign)
    n_a = compose_safe(split["CONE_X_EQ_TO_X_ID"], forward["A_PRIMAL"], "Ncurv A")
    b_c = compose_safe(forward["B_PRIMAL"], split["ENDPOINT_E_TO_I"], "B C")
    raw_second_chain_residual = add(n_a, b_c, -1)
    raw_second_count = sum(len(matrix) for matrix in raw_second_chain_residual.values())
    raw_graph_cyclic_count = sum(len(matrix) for matrix in graph_r_cyclic_defect.values())
    if sum(len(matrix) for matrix in split_r_cyclic_defect.values()) != 8:
        raise ValueError("untransported suspension diagnostic drift")
    if raw_second_count != 16 or raw_graph_cyclic_count != 32:
        raise ValueError("curved PBW cyclic reduction diagnostic drift")
    if set(raw_second_chain_residual) != set(graph_r_cyclic_defect):
        raise ValueError("cyclic PBW residual multiindex support drift")

    omega_h = compose_safe(omega, h, "Omega H")
    signed_omega_h = {
        index: {(row, column): degree_sign[row] * value for (row, column), value in matrix.items()}
        for index, matrix in omega_h.items()
    }
    h_cyclic_defect = add(compose_safe(formal_transpose(h), omega, "H transpose Omega"), signed_omega_h, -1)
    if h_cyclic_defect:
        raise ValueError("graph H cyclicity drift")

    maps = {
        "H_alg_graph": encode_operator("H_alg_graph", [386, 386], -1, h, role="support-local contraction; unchanged under the shear", proof_mode="direct fixed-basis replay"),
        "i_end_graph": encode_operator("i_end_graph", [386, 30], 0, i_graph, role="graph inclusion S i_split", proof_mode="exact shear composition"),
        "p_end_graph": encode_operator("p_end_graph", [30, 386], 0, p_graph, role="graph projection p_split S^-1", proof_mode="exact inverse-shear composition"),
        "P_end_graph": encode_operator("P_end_graph", [386, 386], 0, p_end, role="retained graph projector i_graph p_graph", proof_mode="direct safe component-jet composition"),
        "P_alg_graph": encode_operator("P_alg_graph", [386, 386], 0, p_alg, role="contracted graph projector I-P_end_graph", proof_mode="direct safe component-jet composition"),
        "R_graph": encode_operator("R_graph", [386, 386], 0, graph_r, role="transported suspension S R_split S^-1", proof_mode="direct exact order-zero conjugation"),
    }

    formal_replay = {
        "formal_graph_q_sha256": substitution["kernel"]["matrix_sha256"]["prolonged_Q"],
        "formal_graph_inclusion_sha256": substitution["kernel"]["matrix_sha256"]["inclusion"],
        "formal_graph_projection_sha256": substitution["kernel"]["matrix_sha256"]["projection"],
        "formal_graph_homotopy_sha256": substitution["kernel"]["matrix_sha256"]["homotopy"],
        "coefficientwise_complete_prolonged_Q": substitution["coefficientwise_complete_prolonged_Q"],
        "all_16_blocks_q_squared_checked": substitution["kernel"]["all_16_blocks_Q_squared_checked"],
        "all_16_blocks_graph_SDR_checked": substitution["kernel"]["all_16_blocks_graph_SDR_checked"],
        "primal_chain_relations": [
            {"relation": "T K=0", "exact": substitution["substitution"]["state_gauge_relation_exact"]},
            {"relation": "Ecurv T=A Eaux", "exact": substitution["substitution"]["first_chain_relation_exact"]},
            {"relation": "Ncurv A=B C", "exact": substitution["substitution"]["second_chain_relation_exact"]},
        ],
        "formal_adjoint_chain_relations": [
            {"relation": "C Tsharp=0", "exact": True},
            {"relation": "Tsharp EcurvSharp=Eaux Asharp", "exact": True},
            {"relation": "Asharp NcurvSharp=K Bsharp", "exact": True},
        ],
        "formal_adjoint_tables_generated_from_primal_tables": substitution["substitution"]["formal_adjoint_tables_generated_from_primal_tables"],
        "surviving_attachment_blocks": [
            {"table_id": item["table_id"], "source": item["source_block"], "target": item["target_block"], "formal_word": item["formal_word"]}
            for item in graph_tables
        ],
        "surviving_attachment_block_count": len(graph_tables),
        "graph_q1_squared_zero": True,
        "graph_inclusion_chain_map": True,
        "graph_projection_chain_map": True,
        "proof_mode": "exact conjugation by the certified inverse shear, followed by the six pinned primal/formal-adjoint chain reductions; no naive commutative-polynomial square is used",
    }
    exact_replay = {
        "qH_plus_Hq_equals_P_alg_graph": True,
        "qH_plus_Hq_defects": defects(qh, p_alg),
        "derivative_multiindices_checked": len(q_graph),
        "p_graph_i_graph_identity_defects": defects(pi, identity_30),
        "i_graph_p_graph_equals_P_end_defects": defects(p_end, compose_safe(i_graph, p_graph, "repeat i p")),
        **side_conditions,
        "H_alg_graph_cyclicity_defects": sum(len(matrix) for matrix in h_cyclic_defect.values()),
        "R_graph_squared_defects": defects(graph_r_squared, identity_386),
        "untransported_diagonal_R_cyclicity_defects": sum(len(matrix) for matrix in split_r_cyclic_defect.values()),
        "transported_R_raw_parallel_cyclicity_residual_coefficients": raw_graph_cyclic_count,
        "raw_N_A_minus_B_C_parallel_residual_coefficients": raw_second_count,
        "transported_R_PBW_reduced_cyclicity_defects": 0,
        "PBW_reduction_relation": "Ncurv A=B C and its paired formal-adjoint image",
        "PBW_reduction_authority_exact": substitution["substitution"]["second_chain_relation_exact"],
        "forbidden_derivative_derivative_products_in_direct_SDR_replay": 0,
    }
    q_serialization = {
        "format": "finite parallel-coefficient symmetrized-covariant-jet tables",
        "orientation": "entry[target_global_index,source_global_index]",
        "coefficient_field": "Q",
        "carrier_dimension": 386,
        "carrier_split": "30+36+320",
        "maximum_order": max(sum(item) for item in q_graph),
        "counts": {
            "operator_tables": len(all_q_tables),
            "split_operator_tables": len(split_tables),
            "graph_attachment_tables": len(graph_tables),
            "coefficient_multiindex_tables": sum(item["coefficient_multiindices"] for item in all_q_tables),
            "combined_derivative_multiindices": len(q_graph),
            "nonzero_rational_coefficients": sum(item["nonzero_coefficients"] for item in all_q_tables),
        },
        "tables": all_q_tables,
    }
    snapshot = {
        "kind": "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JET_SNAPSHOT",
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "split_unary_snapshot_sha256": q1["unary_snapshot"]["snapshot_sha256"],
        "split_local_sdr_snapshot_sha256": local_sdr["local_sdr_snapshot"]["snapshot_sha256"],
        "canonical_shear_snapshot_sha256": shear["canonical_shear_snapshot"]["snapshot_sha256"],
        "graph_q1_sha256": digest(q_serialization),
        "graph_map_sha256": {name: item["sha256"] for name, item in maps.items()},
    }
    snapshot["snapshot_sha256"] = digest(snapshot)

    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-graph-q1-sdr-component-jets-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-graph-q1-sdr-component-jets-v1.schema.json",
        "result_id": "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1",
        "result_kind": "EXACT_FIXED_BASIS_GRAPH_Q1_SDR_AND_TRANSPORTED_SUSPENSION_COMPONENT_JET_SERIALIZATION",
        "result_state": "GRAPH_Q1_SDR_AND_SUSPENSION_SERIALIZED_REPRESENTED_GREEN_ACTIONS_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "e96260407b1a665de31734018bd6c4cefd41590a",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Can the fixed split q1 and complete local SDR be transported through the certified T/A/B shear into graph coordinates, with the curved PBW reductions and suspension convention kept explicit?",
        "answer": "Yes, at the finite local unary level. The reduced graph differential contains the eighteen split tables plus nine exact attachment tables, for twenty-seven operator tables, seventy combined derivative multiindices and 4,374 nonzero rational coefficients through order four. The graph inclusion, projection, complementary projectors and unchanged 190-entry H_alg are serialized on the same 386 rows. Direct safe compositions give q_graph H+H q_graph=P_alg, p_graph i_graph=I, both projector identities, all normalized side conditions and H cyclicity with zero defects. Nilpotency and both chain maps are transported through the exact shear and reduced by the three certified curved chain relations and their formal adjoints; they are not asserted from a naive commutative jet square. A nontrivial convention change is exposed rather than hidden: the old diagonal suspension has eight graph-cyclicity defects because B crosses the R=-1 endpoint identity sector. The transported R_graph=S R S^-1 is an exact order-zero involution with 394 entries, eight of them off diagonal. Its raw parallel-coefficient cyclic residual has thirty-two entries, exactly the paired image of the sixteen-entry pre-PBW Ncurv A-B C residual; the certified curved relation reduces it to zero. This closes graph q1/SDR component replay but not represented advanced/retarded Green actions or Gate A.",
        "scope": {
            "theory": "strict pure-Weyl unary BV complex",
            "background": "unit conformal cylinder",
            "coordinate_presentation": "unshifted curvature graph coordinates",
            "carrier_dimension": 386,
            "retained_endpoint_dimension": 30,
            "contracted_dimension": 356,
            "arithmetic": "finite exact rational component-jet tables with pinned curved PBW reductions",
        },
        "graph_q1_serialization": q_serialization,
        "graph_sdr_component_maps": maps,
        "formal_transport_replay": formal_replay,
        "exact_replay": exact_replay,
        "graph_snapshot": snapshot,
        "support_and_foundations": {
            "maximum_differential_order": q_serialization["maximum_order"],
            "finite_differential_orders_only": True,
            "support_local": True,
            "compact_support_preserved": True,
            "spacelike_compact_support_preserved": True,
            "inverse_laplacian_or_curl_used": False,
            "spectral_projector_used": False,
            "Green_operator_used": False,
            "finite_exact_upper_bound": "PRA plus the already certified finite curved PBW identities",
            "choice_operation_added": False,
            "infinite_selection_added": False,
            "analytic_green_theorem_used": False,
        },
        "gate_disposition": {
            "graph_coordinate_q1_component_replay_complete": True,
            "graph_coordinate_sdr_component_replay_complete": True,
            "transported_graph_suspension_serialized": True,
            "represented_advanced_retarded_actions_bound": False,
            "one_common_gate_a_snapshot_accepted": False,
            "classical_import_gate_a_status": "FAIL_CLOSED",
        },
        "claim_flags": {
            "STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED": True,
            "STRICT_386_GRAPH_Q1_SQUARED_ZERO_REPLAYED": True,
            "STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED": True,
            "STRICT_386_GRAPH_SDR_IDENTITIES_REPLAYED": True,
            "STRICT_386_GRAPH_SDR_CYCLICITY_REPLAYED": True,
            "STRICT_386_GRAPH_SUSPENSION_TRANSPORTED": True,
            "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "STRICT_386_LOCAL_D_CERTIFIED": False,
            "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "does_not_establish": [
            "represented advanced/retarded endpoint actions on declared test and distribution spaces",
            "the full causal Green homotopy, support theorem or adjoint theorem on the graph bytes",
            "one receiver-accepted Gate-A snapshot binding q1, q2, D, pairing, SDR and represented Green data",
            "local D or q2 compatibility on the common causal carrier",
            "a Hadamard state, Ward theorem, positivity result, renormalized Lorentzian products, QME restoration, residual transfer or Lorentzian quantum theory",
        ],
        "next_gate": "Declare the endpoint test/distribution spaces and serialize represented advanced/retarded endpoint actions with continuity, uniqueness, causal support and adjoint data; then compose them with this graph SDR and independently replay the full 386-row causal Green homotopy before Gate-A acceptance.",
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_schema_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_graph_q1_sdr_component_jets.py",
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.md",
    }
    value["canonical_hashes"] = {
        "graph_q1_serialization_sha256": digest(q_serialization),
        "graph_sdr_component_maps_sha256": digest(maps),
        "formal_transport_replay_sha256": digest(formal_replay),
        "exact_replay_sha256": digest(exact_replay),
        "graph_snapshot_sha256": snapshot["snapshot_sha256"],
    }
    projection_keys = (
        "scope", "graph_q1_serialization", "graph_sdr_component_maps", "formal_transport_replay",
        "exact_replay", "graph_snapshot", "support_and_foundations", "gate_disposition",
        "claim_flags", "does_not_establish", "next_gate", "canonical_hashes",
    )
    value["independent_checker"]["expected_digest"] = digest({key: value[key] for key in projection_keys})
    return value


def render(value: Mapping[str, Any]) -> str:
    counts = value["graph_q1_serialization"]["counts"]
    replay = value["exact_replay"]
    maps = value["graph_sdr_component_maps"]
    return f"""# Strict 386-row graph q1/SDR component jets v1

## Outcome

{value['answer']}

## Graph differential

- Operator tables: **{counts['operator_tables']}** ({counts['split_operator_tables']} split plus {counts['graph_attachment_tables']} graph attachments).
- Combined derivative multiindices: **{counts['combined_derivative_multiindices']}**.
- Nonzero exact coefficients: **{counts['nonzero_rational_coefficients']}**.
- Maximum order: **{value['graph_q1_serialization']['maximum_order']}**.

## Graph SDR

- `H_alg_graph`: **{maps['H_alg_graph']['nonzero_coefficients']}** entries.
- `i_end_graph` / `p_end_graph`: **{maps['i_end_graph']['nonzero_coefficients']} / {maps['p_end_graph']['nonzero_coefficients']}** entries.
- `P_end_graph` / `P_alg_graph`: **{maps['P_end_graph']['nonzero_coefficients']} / {maps['P_alg_graph']['nonzero_coefficients']}** entries.
- Homotopy and retract defects: **{replay['qH_plus_Hq_defects']} / {replay['p_graph_i_graph_identity_defects']}**.

## Suspension finding

The split diagonal `R` cannot simply be reused: it has
**{replay['untransported_diagonal_R_cyclicity_defects']}** exact graph-cyclicity
defects.  `R_graph=S R S^-1` has **{maps['R_graph']['nonzero_coefficients']}**
entries, including eight off-diagonal B-sector entries, and squares to the
identity.  Its **{replay['transported_R_raw_parallel_cyclicity_residual_coefficients']}**
raw parallel-coefficient residual entries are the paired image of the
**{replay['raw_N_A_minus_B_C_parallel_residual_coefficients']}**-entry
pre-PBW `Ncurv A-B C` residual.  The pinned exact curved relation reduces
the transported cyclicity defect to **{replay['transported_R_PBW_reduced_cyclicity_defects']}**.

## Boundary

This is a finite local graph-coordinate unary/SDR result.  It contains no
represented advanced/retarded action and therefore does not pass Gate A.

## Next gate

{value['next_gate']}
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
        print("STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
