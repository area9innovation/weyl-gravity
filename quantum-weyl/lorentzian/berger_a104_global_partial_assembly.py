"""Globally indexed partial assembly contract for the Berger Cauchy operator.

The metric and metric-antifield Cauchy operators are already exact, but their
artifacts use sector-local coordinates.  This module embeds them into the
frozen 104-row Cauchy ordering, records every known zero, and leaves exactly
the ghost and identity 12-by-12 diagonal blocks unresolved.  It also freezes
the endpoint-factor and Cauchy-BRST package that can close those slots.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from transfer.berger_gauge_fixed_nonminimal_import import _zero

from .berger_a104_cauchy_operator_preflight import (
    GENERATED as LOCAL_GENERATED,
    _matrix_record,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFLIGHT = HERE / "certificates/BERGER_A104_CAUCHY_OPERATOR_PREFLIGHT.json"
COMPANION = HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"
GENERATED = HERE / "generated/berger_a104_global_partial_assembly"
ENDPOINT_EXPORT_SCHEMA = HERE / "schema/berger-endpoint-a24-cauchy-export-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    identity = payload.get("result_id") or payload.get("schema")
    if not isinstance(identity, str) or not identity:
        raise ValueError(f"dependency identity missing: {path}")
    return {"artifact_id": identity, "sha256": _sha256(path)}


def _internal_hash(body: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _artifact_text(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _artifact_reference(name: str, payload: dict[str, Any], fmt: str) -> dict[str, str]:
    return {
        "format": fmt,
        "path": (
            "quantum-weyl/lorentzian/generated/"
            f"berger_a104_global_partial_assembly/{name}.json"
        ),
        "sha256": hashlib.sha256(_artifact_text(payload).encode()).hexdigest(),
    }


def _load_sparse_operator(path: Path, shape: tuple[int, int]) -> list[list[dict]]:
    payload = json.loads(path.read_text())
    if payload.get("shape") != list(shape):
        raise ValueError(f"operator shape drifted: {path.name}")
    body = {"shape": payload["shape"], "entries": payload["entries"]}
    if payload.get("sha256") != _internal_hash(body):
        raise ValueError(f"operator internal hash drifted: {path.name}")
    matrix = _zero(*shape)
    seen: set[tuple[int, int]] = set()
    for row, column, terms in payload["entries"]:
        coordinate = (row, column)
        if coordinate in seen or not (0 <= row < shape[0] and 0 <= column < shape[1]):
            raise ValueError(f"operator coordinate drifted: {path.name}")
        seen.add(coordinate)
        operator = {}
        for exponents, coefficient in terms:
            if len(exponents) != 4 or any(type(value) is not int or value < 0 for value in exponents):
                raise ValueError(f"operator exponent drifted: {path.name}")
            word = tuple(axis for axis, count in enumerate(exponents) for _ in range(count))
            operator[word] = coefficient
        matrix[row][column] = operator
    return matrix


def _sector_indices(rows: list[dict[str, Any]], sector: str) -> list[int]:
    if sector == "metric":
        allowed = {"metric_primary", "metric_auxiliary"}
    elif sector == "metric_antifield":
        allowed = {"metric_antifield_primary", "metric_antifield_auxiliary"}
    else:
        raise ValueError(f"unknown sector: {sector}")
    indices = [row["index"] for row in rows if row["block"] in allowed]
    if len(indices) != 40:
        raise ValueError(f"{sector} global index count drifted")
    return indices


def _embed_indices(target, source, indices: list[int]) -> None:
    if len(source) != len(indices) or any(len(row) != len(indices) for row in source):
        raise ValueError("local/global embedding rank mismatch")
    for local_row, global_row in enumerate(indices):
        for local_column, global_column in enumerate(indices):
            target[global_row][global_column] = source[local_row][local_column]


def _mask_record(rows: list[dict[str, Any]]) -> dict[str, Any]:
    degree_indices = {
        str(degree): [row["index"] for row in rows if row["degree"] == degree]
        for degree in (-1, 0, 1, 2)
    }
    status_matrix = []
    degrees = ["-1", "0", "1", "2"]
    for row_degree in degrees:
        status_row = []
        for column_degree in degrees:
            if row_degree != column_degree:
                status = "KNOWN_ZERO_DEGREE_OFF_DIAGONAL"
            elif row_degree in {"0", "1"}:
                status = "KNOWN_EXACT_OPERATOR"
            else:
                status = "UNKNOWN_ENDPOINT_A12"
            status_row.append(status)
        status_matrix.append(status_row)
    ranks = {degree: len(indices) for degree, indices in degree_indices.items()}
    unknown = ranks["-1"] ** 2 + ranks["2"] ** 2
    body = {
        "shape": [104, 104],
        "degree_order": degrees,
        "degree_indices": degree_indices,
        "status_matrix": status_matrix,
        "known_coordinate_count": 104**2 - unknown,
        "unknown_coordinate_count": unknown,
        "known_exact_operator_coordinate_count": ranks["0"] ** 2 + ranks["1"] ** 2,
        "known_structural_zero_coordinate_count": 104**2 - sum(rank**2 for rank in ranks.values()),
        "unknown_blocks": ["ghost_A12", "identity_A12"],
    }
    body["sha256"] = _internal_hash(body)
    return body


def _slot(rows: list[dict[str, Any]], degree: int, name: str) -> dict[str, Any]:
    indices = [row["index"] for row in rows if row["degree"] == degree]
    row_ids = [row["row_id"] for row in rows if row["degree"] == degree]
    if len(indices) != 12:
        raise ValueError(f"{name} insertion rank drifted")
    return {
        "block_id": name,
        "shape": [12, 12],
        "global_row_indices": indices,
        "global_column_indices": indices,
        "local_ordering": row_ids,
        "required_artifact_format": "JSON_EXACT_SPARSE_OPERATOR",
        "insertion_rule": "A104[global_row_indices,global_column_indices]=A12[0:12,0:12]",
    }


def _endpoint_contract(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "FROZEN_NOT_POPULATED",
        "accepted_export_schema": {
            "schema_id": "quantum-weyl-berger-endpoint-a24-cauchy-export-v1",
            "path": "quantum-weyl/lorentzian/schema/berger-endpoint-a24-cauchy-export-v1.schema.json",
            "sha256": _sha256(ENDPOINT_EXPORT_SCHEMA),
        },
        "coefficient_ring": "EXACT_RATIONAL_OR_DECLARED_EXACT_ALGEBRAIC_EXTENSION",
        "differential_axis_order": ["t", "berger_frame_1", "berger_frame_2", "berger_frame_3"],
        "factor_records": [
            {
                "factor_record_id": factor_id,
                "shape": [3, 3],
                "required_fields": [
                    "factor_record_id", "shape", "row_ids", "column_ids",
                    "entries", "sha256", "source_commit",
                ],
            }
            for factor_id in (
                "F_spatial_K_spatial",
                "Box_1_spatial_covector",
                "F_spatial_K_spatial_formal_adjoint",
                "Box_1_spatial_covector_formal_adjoint",
            )
        ],
        "derived_block_slots": [
            _slot(rows, -1, "ghost_A12"),
            _slot(rows, 2, "identity_A12"),
        ],
        "required_exact_checks": [
            "factor_record_internal_hashes",
            "factor_row_and_column_orderings_match_retained_layout",
            "ghost_factor_composition_reconstructs_retained_endpoint",
            "identity_factor_composition_reconstructs_retained_endpoint",
            "formal_adjoint_factor_relations",
            "second_order_graph_companions_reconstruct_factor_products",
            "temporal_leading_matrices_are_two_sided_invertible",
            "derived_A12_blocks_have_spatial_order_at_most_two",
        ],
    }


def _q_cauchy_contract(rows: list[dict[str, Any]]) -> dict[str, Any]:
    configuration = [row["row_id"] for row in rows[:52]]
    cauchy = [row["row_id"] for row in rows]
    return {
        "status": "FROZEN_NOT_POPULATED",
        "source_operator": "retained classical_unary_q1 on the 26-row complex",
        "required_artifacts": {
            "q52_companion": {
                "shape": [52, 52],
                "ordering": configuration,
                "format": "JSON_EXACT_SPARSE_OPERATOR",
            },
            "q_Cauchy_104": {
                "shape": [104, 104],
                "ordering": cauchy,
                "format": "JSON_EXACT_SPARSE_OPERATOR",
            },
        },
        "required_exact_checks": [
            "q52_has_degree_plus_one",
            "q52_squared_zero",
            "q52_intertwines_companion_inclusion_projection_and_homotopy",
            "q_Cauchy_has_degree_plus_one",
            "q_Cauchy_squared_zero",
            "q_Cauchy_is_the_exact_first_jet_prolongation_of_q52",
            "full_A104_supercommutes_with_q_Cauchy",
        ],
        "commutator_check_requires": "full_A104_after_both_A12_slots_are_populated",
    }


@lru_cache(maxsize=1)
def build() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    preflight = json.loads(PREFLIGHT.read_text())
    companion = json.loads(COMPANION.read_text())
    if preflight.get("result_state") != "METRIC_A80_EXACT_ENDPOINT_A24_AND_CAUCHY_BRST_PAIRING_OPEN":
        raise ValueError("A104 preflight boundary drifted")
    if companion.get("exact_checks", {}).get("retained_P26_is_degree_block_diagonal") is not True:
        raise ValueError("retained degree block diagonality is not certified")
    rows = preflight["Cauchy_row_ledger"]["rows"]
    if [row["index"] for row in rows] != list(range(104)):
        raise ValueError("global Cauchy ordering drifted")

    global_operator = _zero(104, 104)
    embeddings = {}
    for sector in ("metric", "metric_antifield"):
        local_path = LOCAL_GENERATED / f"{sector}_A40.json"
        local = _load_sparse_operator(local_path, (40, 40))
        indices = _sector_indices(rows, sector)
        _embed_indices(global_operator, local, indices)
        embeddings[sector] = {
            "local_artifact": {
                "path": f"quantum-weyl/lorentzian/generated/berger_a104_cauchy_operator_preflight/{sector}_A40.json",
                "sha256": _sha256(local_path),
            },
            "local_shape": [40, 40],
            "local_to_global_indices": indices,
            "ordering_check": "EXACT",
        }

    operator_record = _matrix_record(global_operator)
    mask_record = _mask_record(rows)
    artifacts = {
        "global_A104_partial": operator_record,
        "global_A104_known_entry_mask": mask_record,
    }
    result = {
        "schema": "quantum-weyl-berger-a104-global-partial-assembly-v1",
        "result_id": "BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY",
        "result_state": "GLOBAL_A104_104_BY_104_KNOWN_MASK_EXACT_TWO_A12_SLOTS_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "classical_commit": preflight["classical_commit"],
        "setting_id": preflight["setting_id"],
        "dependency_refs": {
            "A104_Cauchy_preflight": _dependency(PREFLIGHT),
            "retained_biwave_companion": _dependency(COMPANION),
        },
        "global_ordering": {
            "shape": [104, 104],
            "row_ids": [row["row_id"] for row in rows],
            "degree_ranks": [12, 40, 40, 12],
            "degree_block_diagonal": True,
        },
        "sector_embeddings": embeddings,
        "partial_operator": _artifact_reference(
            "global_A104_partial", operator_record, "JSON_EXACT_SPARSE_OPERATOR"
        ),
        "known_entry_mask": _artifact_reference(
            "global_A104_known_entry_mask", mask_record, "JSON_EXACT_KNOWN_ENTRY_MASK"
        ),
        "coverage": {
            "total_coordinates": 104**2,
            "known_coordinates": mask_record["known_coordinate_count"],
            "unknown_coordinates": mask_record["unknown_coordinate_count"],
            "known_nonzero_sparse_entries": len(operator_record["entries"]),
            "unresolved_blocks": ["ghost_A12", "identity_A12"],
        },
        "endpoint_A24_import_contract": _endpoint_contract(rows),
        "q_Cauchy_import_contract": _q_cauchy_contract(rows),
        "claim_flags": {
            "BERGER_GLOBAL_PARTIAL_A104": True,
            "BERGER_A104_KNOWN_ENTRY_MASK": True,
            "BERGER_ENDPOINT_A24_INSERTION_CONTRACT": True,
            "BERGER_Q_CAUCHY_IMPORT_CONTRACT": True,
            "BERGER_FULL_A104_CAUCHY_OPERATOR": False,
            "BERGER_Q_CAUCHY_104": False,
            "BERGER_A104_Q_CAUCHY_COMPATIBLE": False,
            "BERGER_CAUCHY_KREIN_FORM": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_ENDPOINT_A24_EXPORT_AND_GLOBAL_INSERTION",
        "provenance": {
            "preflight_result_id": preflight["result_id"],
            "degree_block_diagonal_result_id": companion["result_id"],
        },
        "claim_boundary": (
            "Embeds the exact metric and metric-antifield A40 operators into the frozen "
            "104-row ordering and certifies 10528 of 10816 matrix coordinates, including "
            "all degree-off-diagonal structural zeros. Exactly two diagonal 12-by-12 "
            "endpoint slots, 288 coordinates total, remain unresolved. It freezes but "
            "does not populate the endpoint-factor or q_Cauchy contracts, assemble full "
            "A104, construct a Cauchy pairing, prove closedness or construct Hadamard data."
        ),
    }
    validate(result)
    return result, artifacts


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY"
        or result.get("result_state")
        != "GLOBAL_A104_104_BY_104_KNOWN_MASK_EXACT_TWO_A12_SLOTS_OPEN"
        or result.get("coverage", {}).get("total_coordinates") != 10816
        or result.get("coverage", {}).get("known_coordinates") != 10528
        or result.get("coverage", {}).get("unknown_coordinates") != 288
    ):
        raise ValueError("global partial A104 identity or coverage drifted")
    slots = result.get("endpoint_A24_import_contract", {}).get("derived_block_slots", [])
    if [slot.get("block_id") for slot in slots] != ["ghost_A12", "identity_A12"]:
        raise ValueError("endpoint insertion slots drifted")
    if any(slot.get("shape") != [12, 12] for slot in slots):
        raise ValueError("endpoint insertion shape drifted")
    flags = result.get("claim_flags", {})
    required_false = (
        "BERGER_FULL_A104_CAUCHY_OPERATOR", "BERGER_Q_CAUCHY_104",
        "BERGER_A104_Q_CAUCHY_COMPATIBLE", "BERGER_CAUCHY_KREIN_FORM",
        "BERGER_HADAMARD_DATA", "QUANTUM_CLAIM",
    )
    if any(flags.get(flag) is not False for flag in required_false):
        raise ValueError("full A104, BRST, pairing, Hadamard or quantum claim over-promoted")
    if result.get("endpoint_A24_import_contract", {}).get("status") != "FROZEN_NOT_POPULATED":
        raise ValueError("endpoint contract was over-promoted")
    if result.get("q_Cauchy_import_contract", {}).get("status") != "FROZEN_NOT_POPULATED":
        raise ValueError("q_Cauchy contract was over-promoted")
