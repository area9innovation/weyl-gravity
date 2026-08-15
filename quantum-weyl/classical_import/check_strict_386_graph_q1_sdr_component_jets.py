#!/usr/bin/env python3
"""Independently replay the strict 386-row graph q1/SDR certificate."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
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


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def decode(value: Mapping[str, Any]) -> Operator:
    output: Operator = {}
    for item in value.get("coefficients", []):
        index = tuple(item.get("multiindex", ()))
        if len(index) != 4 or index in output:
            raise ValueError("duplicate or malformed multiindex")
        matrix: Sparse = {}
        for row, column, raw in item.get("entries", []):
            key = (row, column)
            coefficient = Fraction(raw)
            if key in matrix or not coefficient:
                raise ValueError("duplicate or zero coefficient")
            matrix[key] = coefficient
        output[index] = matrix
    return output


def decode_local(value: Mapping[str, Any]) -> Operator:
    matrix: Sparse = {}
    for item in value.get("entries", []):
        key = (item["target"], item["source"])
        coefficient = Fraction(item["coefficient"])
        if key in matrix or not coefficient:
            raise ValueError("duplicate or zero local-map coefficient")
        matrix[key] = coefficient
    return {ZERO: matrix}


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
    return add({}, operator, coefficient)


def sparse_product(left: Sparse, right: Sparse) -> Sparse:
    right_by_row: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), value in right.items():
        right_by_row.setdefault(row, []).append((column, value))
    output: Sparse = {}
    for (row, middle), value in left.items():
        for column, other in right_by_row.get(middle, ()):
            key = (row, column)
            output[key] = output.get(key, Fraction()) + value * other
    return {key: value for key, value in output.items() if value}


def compose(left: Operator, right: Operator) -> tuple[Operator, int]:
    output: Operator = {}
    forbidden = 0
    for left_index, left_matrix in left.items():
        for right_index, right_matrix in right.items():
            product = sparse_product(left_matrix, right_matrix)
            if not product:
                continue
            if sum(left_index) and sum(right_index):
                forbidden += len(product)
                continue
            index = tuple(a + b for a, b in zip(left_index, right_index, strict=True))
            output = add(output, {index: product})
    return output, forbidden


def safe(left: Operator, right: Operator, label: str) -> Operator:
    output, forbidden = compose(left, right)
    if forbidden:
        raise ValueError(f"{label}: {forbidden} uncertified derivative products")
    return output


def identity(size: int) -> Operator:
    return {ZERO: {(row, row): Fraction(1) for row in range(size)}}


def remap(
    operator: Operator,
    old_sources: Sequence[int],
    new_sources: Sequence[int],
    old_targets: Sequence[int],
    new_targets: Sequence[int],
) -> Operator:
    sources = dict(zip(old_sources, new_sources, strict=True))
    targets = dict(zip(old_targets, new_targets, strict=True))
    return {
        index: {(targets[row], sources[column]): value for (row, column), value in matrix.items()}
        for index, matrix in operator.items()
    }


def block_indices(pairing: Mapping[str, Any]) -> dict[str, list[int]]:
    output: dict[str, list[int]] = {}
    for row in pairing["component_basis"]["rows"]:
        output.setdefault(row["block"], []).append(row["index"])
    return output


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
    omega_r = safe(omega, suspension, "Omega R")
    signed_q = {
        index: {(row, column): degree_sign[row] * value for (row, column), value in matrix.items()}
        for index, matrix in differential.items()
    }
    return add(
        safe(formal_transpose(differential), omega_r, "q transpose Omega R"),
        safe(omega_r, signed_q, "Omega R signed q"),
        -1,
    )


def coefficient_count(operator: Operator) -> int:
    return sum(len(matrix) for matrix in operator.values())


def defect_count(left: Operator, right: Operator) -> int:
    return sum(
        len(set(left.get(index, {})) | set(right.get(index, {})))
        for index in set(left) | set(right)
        if left.get(index, {}) != right.get(index, {})
    )


def table_metadata_ok(
    item: Mapping[str, Any],
    expected: Operator,
    source: Sequence[int],
    target: Sequence[int],
) -> bool:
    return (
        item.get("shape") == [len(target), len(source)]
        and item.get("degree") == 1
        and item.get("source_global_indices") == list(source)
        and item.get("target_global_indices") == list(target)
        and item.get("orientation") == "entry[target_global_index,source_global_index]"
        and item.get("maximum_order") == max(map(sum, expected), default=0)
        and item.get("coefficient_multiindices") == len(expected)
        and item.get("nonzero_coefficients") == coefficient_count(expected)
        and item.get("sha256") == digest(item.get("coefficients", []))
    )


def map_metadata_ok(item: Mapping[str, Any], expected: Operator, shape: Sequence[int], degree: int) -> bool:
    return (
        item.get("shape") == list(shape)
        and item.get("degree") == degree
        and item.get("orientation") == "entry[target_global_index,source_global_index]"
        and item.get("maximum_order") == max(map(sum, expected), default=0)
        and item.get("coefficient_multiindices") == len(expected)
        and item.get("nonzero_coefficients") == coefficient_count(expected)
        and item.get("sha256")
        == digest({"shape": list(shape), "degree": degree, "coefficients": item.get("coefficients", [])})
    )


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    q1, pairing, local_sdr, shear, substitution, kernel, core_chain = (
        load(path) for path in (Q1, PAIRING, LOCAL_SDR, SHEAR, SUBSTITUTION, KERNEL, CORE_CHAIN)
    )
    errors: list[str] = []
    if (
        value.get("result_id") != "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1"
        or value.get("result_state") != "GRAPH_Q1_SDR_AND_SUSPENSION_SERIALIZED_REPRESENTED_GREEN_ACTIONS_OPEN"
        or value.get("lifecycle") != "CLASSIFIED"
    ):
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    try:
        by_block = block_indices(pairing)
        split_tables = q1["q1_serialization"]["tables"]
        split = {item["table_id"]: decode(item) for item in split_tables}
        forward = {
            item["table_id"]: decode(item)
            for item in shear["canonical_transform"]["forward"]["tables"]
        }
        inverse = {
            item["table_id"]: decode(item)
            for item in shear["canonical_transform"]["inverse"]["tables"]
        }

        def moved(
            table: str, source_old: str, source_new: str, target_old: str, target_new: str
        ) -> Operator:
            return remap(
                forward[table], by_block[source_old], by_block[source_new],
                by_block[target_old], by_block[target_new],
            )

        central = safe(
            safe(forward["A_PRIMAL"], split["ENDPOINT_M_TO_E"], "A Eaux"),
            forward["A_FORCED_PARTNER"],
            "A Eaux Asharp",
        )
        specs = (
            ("GRAPH_Y_ID_SHARP_TO_ENDPOINT_G", "CONE_Y_ID_SHARP", "ENDPOINT_G", moved("B_FORCED_PARTNER", "CONE_X_ID_SHARP", "CONE_Y_ID_SHARP", "ENDPOINT_G", "ENDPOINT_G"), "-Bsharp"),
            ("GRAPH_Y_EQ_SHARP_TO_ENDPOINT_M", "CONE_Y_EQ_SHARP", "ENDPOINT_M", moved("A_FORCED_PARTNER", "CONE_X_EQ_SHARP", "CONE_Y_EQ_SHARP", "ENDPOINT_M", "ENDPOINT_M"), "-Asharp"),
            ("GRAPH_Y_U_SHARP_TO_ENDPOINT_E", "CONE_Y_U_SHARP", "ENDPOINT_E", moved("T_FORCED_PARTNER", "CONE_X_U_SHARP", "CONE_Y_U_SHARP", "ENDPOINT_E", "ENDPOINT_E"), "-Tsharp"),
            ("GRAPH_ENDPOINT_M_TO_Y_U", "ENDPOINT_M", "CONE_Y_U", scale(moved("T_PRIMAL", "ENDPOINT_M", "ENDPOINT_M", "CONE_X_U", "CONE_Y_U"), -1), "-T"),
            ("GRAPH_ENDPOINT_E_TO_Y_EQ", "ENDPOINT_E", "CONE_Y_EQ", scale(moved("A_PRIMAL", "ENDPOINT_E", "ENDPOINT_E", "CONE_X_EQ", "CONE_Y_EQ"), -1), "-A"),
            ("GRAPH_ENDPOINT_I_TO_Y_ID", "ENDPOINT_I", "CONE_Y_ID", scale(moved("B_PRIMAL", "ENDPOINT_I", "ENDPOINT_I", "CONE_X_ID", "CONE_Y_ID"), -1), "-B"),
            ("GRAPH_X_EQ_SHARP_TO_X_EQ", "CONE_X_EQ_SHARP", "CONE_X_EQ", central, "-A Eaux Asharp"),
            ("GRAPH_Y_U_SHARP_TO_X_EQ", "CONE_Y_U_SHARP", "CONE_X_EQ", moved("FORWARD_CROSS_A_TSHARP", "CONE_X_U_SHARP", "CONE_Y_U_SHARP", "CONE_X_EQ", "CONE_X_EQ"), "-A Tsharp"),
            ("GRAPH_X_EQ_SHARP_TO_Y_U", "CONE_X_EQ_SHARP", "CONE_Y_U", remap(inverse["INVERSE_CROSS_T_ASHARP"], by_block["CONE_X_EQ_SHARP"], by_block["CONE_X_EQ_SHARP"], by_block["CONE_X_U"], by_block["CONE_Y_U"]), "-T Asharp"),
        )
    except (KeyError, TypeError, ValueError) as error:
        errors.append("source reconstruction: " + str(error))
        return errors

    serialization = value.get("graph_q1_serialization", {})
    actual_tables = serialization.get("tables", [])
    if actual_tables[:18] != split_tables:
        errors.append("split table byte projection")
    graph_tables = actual_tables[18:]
    if len(graph_tables) != 9:
        errors.append("graph table inventory")
    expected_graph: list[Operator] = []
    for actual, (table_id, source_block, target_block, expected, word) in zip(
        graph_tables, specs, strict=False
    ):
        expected_graph.append(expected)
        try:
            actual_operator = decode(actual)
        except (TypeError, ValueError) as error:
            errors.append(f"{table_id} decoding: {error}")
            continue
        if (
            actual.get("table_id") != table_id
            or actual.get("source_block") != source_block
            or actual.get("target_block") != target_block
            or actual.get("formal_word") != word
            or not table_metadata_ok(actual, expected, by_block[source_block], by_block[target_block])
        ):
            errors.append(table_id + " metadata/hash")
        if actual_operator != expected:
            errors.append(table_id + " coefficients")

    q_graph: Operator = {}
    try:
        for table in actual_tables:
            q_graph = add(q_graph, decode(table))
    except (TypeError, ValueError) as error:
        errors.append("graph q decoding: " + str(error))
        return errors
    counts = serialization.get("counts", {})
    expected_counts = {
        "operator_tables": 27,
        "split_operator_tables": 18,
        "graph_attachment_tables": 9,
        "coefficient_multiindex_tables": sum(item["coefficient_multiindices"] for item in actual_tables),
        "combined_derivative_multiindices": len(q_graph),
        "nonzero_rational_coefficients": sum(item["nonzero_coefficients"] for item in actual_tables),
    }
    if (
        counts != expected_counts
        or counts["coefficient_multiindex_tables"] != 317
        or counts["combined_derivative_multiindices"] != 70
        or counts["nonzero_rational_coefficients"] != 4374
        or serialization.get("maximum_order") != 4
    ):
        errors.append("graph q inventory/counts")

    try:
        h = decode_local(local_sdr["component_maps"]["H_alg"])
        i_graph = {ZERO: {(row, row): Fraction(1) for row in range(30)}}
        for name in ("T_PRIMAL", "A_PRIMAL", "B_PRIMAL"):
            i_graph = add(i_graph, forward[name])
        p_graph = {ZERO: {(row, row): Fraction(1) for row in range(30)}}
        for name in ("INVERSE_T_FORCED_PARTNER", "INVERSE_A_FORCED_PARTNER", "INVERSE_B_FORCED_PARTNER"):
            p_graph = add(p_graph, inverse[name])
        p_end = safe(i_graph, p_graph, "i p")
        p_alg = add(identity(386), p_end, -1)
        expected_maps = {
            "H_alg_graph": (h, (386, 386), -1),
            "i_end_graph": (i_graph, (386, 30), 0),
            "p_end_graph": (p_graph, (30, 386), 0),
            "P_end_graph": (p_end, (386, 386), 0),
            "P_alg_graph": (p_alg, (386, 386), 0),
        }
        maps = value.get("graph_sdr_component_maps", {})
        for name, (expected, shape, degree) in expected_maps.items():
            actual = maps.get(name, {})
            if decode(actual) != expected:
                errors.append(name + " coefficients")
            if not map_metadata_ok(actual, expected, shape, degree):
                errors.append(name + " metadata/hash")

        qh = add(safe(q_graph, h, "q H"), safe(h, q_graph, "H q"))
        pi = safe(p_graph, i_graph, "p i")
        side = {
            "H_squared_defects": defect_count(safe(h, h, "H squared"), {}),
            "H_i_graph_defects": defect_count(safe(h, i_graph, "H i"), {}),
            "p_graph_H_defects": defect_count(safe(p_graph, h, "p H"), {}),
            "P_end_squared_defects": defect_count(safe(p_end, p_end, "P end squared"), p_end),
            "P_alg_squared_defects": defect_count(safe(p_alg, p_alg, "P alg squared"), p_alg),
            "P_end_P_alg_defects": defect_count(safe(p_end, p_alg, "P end P alg"), {}),
            "P_alg_P_end_defects": defect_count(safe(p_alg, p_end, "P alg P end"), {}),
        }

        shear_forward = identity(386)
        shear_inverse = identity(386)
        for item in shear["canonical_transform"]["forward"]["tables"]:
            shear_forward = add(shear_forward, decode(item))
        for item in shear["canonical_transform"]["inverse"]["tables"]:
            shear_inverse = add(shear_inverse, decode(item))
        split_r = {ZERO: {
            (row, row): Fraction(raw)
            for row, raw in enumerate(pairing["suspension_serialization"]["R_diagonal"])
        }}
        graph_r = safe(safe(shear_forward, split_r, "S R"), shear_inverse, "S R S inverse")
        actual_r = maps.get("R_graph", {})
        if decode(actual_r) != graph_r:
            errors.append("R_graph coefficients")
        if not map_metadata_ok(actual_r, graph_r, (386, 386), 0):
            errors.append("R_graph metadata/hash")
        r_squared = safe(graph_r, graph_r, "R graph squared")

        omega = {ZERO: {
            (item["left_index"], item["right_index"]): Fraction(item["coefficient"])
            for item in pairing["pairing_serialization"]["entries"]
        }}
        signs = [-1 if row["degree"] % 2 else 1 for row in pairing["component_basis"]["rows"]]
        old_r_defect = cyclic_defect(q_graph, omega, split_r, signs)
        graph_r_defect = cyclic_defect(q_graph, omega, graph_r, signs)
        raw_chain = add(
            safe(split["CONE_X_EQ_TO_X_ID"], forward["A_PRIMAL"], "N A"),
            safe(forward["B_PRIMAL"], split["ENDPOINT_E_TO_I"], "B C"),
            -1,
        )
        omega_h = safe(omega, h, "Omega H")
        signed_omega_h = {
            index: {(row, column): signs[row] * coefficient for (row, column), coefficient in matrix.items()}
            for index, matrix in omega_h.items()
        }
        h_cyclic = add(safe(formal_transpose(h), omega, "H transpose Omega"), signed_omega_h, -1)
    except (KeyError, TypeError, ValueError) as error:
        errors.append("map/identity reconstruction: " + str(error))
        return errors

    replay = value.get("exact_replay", {})
    expected_replay = {
        "qH_plus_Hq_equals_P_alg_graph": True,
        "qH_plus_Hq_defects": defect_count(qh, p_alg),
        "derivative_multiindices_checked": len(q_graph),
        "p_graph_i_graph_identity_defects": defect_count(pi, identity(30)),
        "i_graph_p_graph_equals_P_end_defects": defect_count(p_end, safe(i_graph, p_graph, "repeat i p")),
        **side,
        "H_alg_graph_cyclicity_defects": coefficient_count(h_cyclic),
        "R_graph_squared_defects": defect_count(r_squared, identity(386)),
        "untransported_diagonal_R_cyclicity_defects": coefficient_count(old_r_defect),
        "transported_R_raw_parallel_cyclicity_residual_coefficients": coefficient_count(graph_r_defect),
        "raw_N_A_minus_B_C_parallel_residual_coefficients": coefficient_count(raw_chain),
        "transported_R_PBW_reduced_cyclicity_defects": 0,
        "PBW_reduction_relation": "Ncurv A=B C and its paired formal-adjoint image",
        "PBW_reduction_authority_exact": substitution["substitution"]["second_chain_relation_exact"],
        "forbidden_derivative_derivative_products_in_direct_SDR_replay": 0,
    }
    if replay != expected_replay:
        errors.append("exact replay projection")
    if (
        expected_replay["qH_plus_Hq_defects"]
        or expected_replay["p_graph_i_graph_identity_defects"]
        or any(side.values())
        or expected_replay["H_alg_graph_cyclicity_defects"]
        or expected_replay["R_graph_squared_defects"]
        or expected_replay["untransported_diagonal_R_cyclicity_defects"] != 8
        or expected_replay["transported_R_raw_parallel_cyclicity_residual_coefficients"] != 32
        or expected_replay["raw_N_A_minus_B_C_parallel_residual_coefficients"] != 16
        or set(graph_r_defect) != set(raw_chain)
    ):
        errors.append("independent exact identity replay")

    formal = value.get("formal_transport_replay", {})
    expected_formal_scalars = {
        "formal_graph_q_sha256": substitution["kernel"]["matrix_sha256"]["prolonged_Q"],
        "formal_graph_inclusion_sha256": substitution["kernel"]["matrix_sha256"]["inclusion"],
        "formal_graph_projection_sha256": substitution["kernel"]["matrix_sha256"]["projection"],
        "formal_graph_homotopy_sha256": substitution["kernel"]["matrix_sha256"]["homotopy"],
        "coefficientwise_complete_prolonged_Q": True,
        "all_16_blocks_q_squared_checked": True,
        "all_16_blocks_graph_SDR_checked": True,
        "formal_adjoint_tables_generated_from_primal_tables": True,
        "surviving_attachment_block_count": 9,
        "graph_q1_squared_zero": True,
        "graph_inclusion_chain_map": True,
        "graph_projection_chain_map": True,
    }
    for key, expected in expected_formal_scalars.items():
        if formal.get(key) != expected:
            errors.append("formal transport " + key)
    if (
        substitution.get("coefficientwise_complete_prolonged_Q") is not True
        or substitution.get("kernel", {}).get("all_16_blocks_Q_squared_checked") is not True
        or substitution.get("kernel", {}).get("all_16_blocks_graph_SDR_checked") is not True
        or substitution.get("substitution", {}).get("second_chain_relation_exact") is not True
        or kernel.get("schema") != "pure-weyl-curvature-mapping-cylinder-kernel-v1"
        or core_chain.get("schema") != "pure-weyl-curved-core-curvature-chain-map-v1"
    ):
        errors.append("formal source authority")
    expected_block_projection = [
        {"table_id": item.get("table_id"), "source": item.get("source_block"), "target": item.get("target_block"), "formal_word": item.get("formal_word")}
        for item in graph_tables
    ]
    if formal.get("surviving_attachment_blocks") != expected_block_projection:
        errors.append("formal graph block projection")

    support = value.get("support_and_foundations", {})
    if (
        support.get("maximum_differential_order") != 4
        or support.get("finite_differential_orders_only") is not True
        or support.get("support_local") is not True
        or support.get("Green_operator_used") is not False
        or support.get("choice_operation_added") is not False
        or support.get("analytic_green_theorem_used") is not False
    ):
        errors.append("support/foundational boundary")
    gate = value.get("gate_disposition", {})
    if (
        gate.get("graph_coordinate_q1_component_replay_complete") is not True
        or gate.get("graph_coordinate_sdr_component_replay_complete") is not True
        or gate.get("transported_graph_suspension_serialized") is not True
        or gate.get("represented_advanced_retarded_actions_bound") is not False
        or gate.get("one_common_gate_a_snapshot_accepted") is not False
        or gate.get("classical_import_gate_a_status") != "FAIL_CLOSED"
    ):
        errors.append("Gate-A firewall")
    flags = value.get("claim_flags", {})
    for key in (
        "STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED",
        "STRICT_386_GRAPH_Q1_SQUARED_ZERO_REPLAYED",
        "STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED",
        "STRICT_386_GRAPH_SDR_IDENTITIES_REPLAYED",
        "STRICT_386_GRAPH_SDR_CYCLICITY_REPLAYED",
        "STRICT_386_GRAPH_SUSPENSION_TRANSPORTED",
    ):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in (
        "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "STRICT_386_LOCAL_D_CERTIFIED",
        "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED",
        "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED",
        "LORENTZIAN_QUANTUM_THEORY",
    ):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)

    maps = value.get("graph_sdr_component_maps", {})
    snapshot = value.get("graph_snapshot", {})
    expected_snapshot = {
        "kind": "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JET_SNAPSHOT",
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "split_unary_snapshot_sha256": q1["unary_snapshot"]["snapshot_sha256"],
        "split_local_sdr_snapshot_sha256": local_sdr["local_sdr_snapshot"]["snapshot_sha256"],
        "canonical_shear_snapshot_sha256": shear["canonical_shear_snapshot"]["snapshot_sha256"],
        "graph_q1_sha256": digest(serialization),
        "graph_map_sha256": {name: item.get("sha256") for name, item in maps.items()},
    }
    expected_snapshot["snapshot_sha256"] = digest(expected_snapshot)
    if snapshot != expected_snapshot:
        errors.append("snapshot binding")
    canonical = value.get("canonical_hashes", {})
    expected_canonical = {
        "graph_q1_serialization_sha256": digest(serialization),
        "graph_sdr_component_maps_sha256": digest(maps),
        "formal_transport_replay_sha256": digest(formal),
        "exact_replay_sha256": digest(replay),
        "graph_snapshot_sha256": snapshot.get("snapshot_sha256"),
    }
    if canonical != expected_canonical:
        errors.append("canonical hashes")
    projection_keys = (
        "scope", "graph_q1_serialization", "graph_sdr_component_maps", "formal_transport_replay",
        "exact_replay", "graph_snapshot", "support_and_foundations", "gate_disposition",
        "claim_flags", "does_not_establish", "next_gate", "canonical_hashes",
    )
    try:
        expected_digest = digest({key: value[key] for key in projection_keys})
    except KeyError as error:
        errors.append("canonical projection missing " + str(error))
    else:
        if value.get("independent_checker", {}).get("expected_digest") != expected_digest:
            errors.append("canonical digest")

    expected_inputs = (Q1, PAIRING, LOCAL_SDR, SHEAR, SUBSTITUTION, KERNEL, CORE_CHAIN)
    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(expected_inputs):
        errors.append("provenance inventory")
    for item, expected_path in zip(provenance, expected_inputs, strict=False):
        if item.get("path") != str(expected_path.relative_to(ROOT)) or item.get("sha256") != sha(expected_path):
            errors.append("provenance " + str(item.get("path")))
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
