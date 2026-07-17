#!/usr/bin/env python3
"""Independent verifier for the globally indexed partial Berger A104."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from local_bv.schema_validation import validate_instance

from .berger_a104_global_partial_assembly import COMPANION, PREFLIGHT, validate
from .berger_a104_global_partial_assembly_certificate import HERE, OUTPUT


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_reference(reference: dict) -> dict:
    path = HERE.parents[1] / reference["path"]
    if _sha256(path) != reference["sha256"]:
        raise ValueError(f"artifact file hash mismatch: {path.name}")
    return json.loads(path.read_text())


def _operator_coordinates(payload: dict) -> dict[tuple[int, int], object]:
    if payload.get("shape") != [104, 104]:
        raise ValueError("global partial operator shape drifted")
    body = {"shape": payload["shape"], "entries": payload["entries"]}
    internal = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if payload.get("sha256") != internal:
        raise ValueError("global partial operator internal hash mismatch")
    coordinates = {}
    for row, column, terms in payload["entries"]:
        coordinate = (row, column)
        if coordinate in coordinates:
            raise ValueError("duplicate global sparse coordinate")
        coordinates[coordinate] = terms
    return coordinates


def _local_coordinates(reference: dict) -> dict[tuple[int, int], object]:
    path = HERE.parents[1] / reference["path"]
    if _sha256(path) != reference["sha256"]:
        raise ValueError("local A40 artifact hash mismatch")
    payload = json.loads(path.read_text())
    if payload.get("shape") != [40, 40]:
        raise ValueError("local A40 shape drifted")
    return {(row, column): terms for row, column, terms in payload["entries"]}


def verify() -> dict:
    certificate = json.loads(OUTPUT.read_text())
    schema = json.loads(
        (HERE / "schema/berger-a104-global-partial-assembly-v1.schema.json").read_text()
    )
    errors = validate_instance(certificate, schema)
    if errors:
        raise ValueError("strict schema failure: " + "; ".join(errors))
    validate(certificate)

    dependencies = {
        "A104_Cauchy_preflight": PREFLIGHT,
        "retained_biwave_companion": COMPANION,
    }
    for name, path in dependencies.items():
        if certificate["dependency_refs"][name]["sha256"] != _sha256(path):
            raise ValueError(f"dependency hash mismatch: {name}")

    global_coordinates = _operator_coordinates(
        _load_reference(certificate["partial_operator"])
    )
    expected_coordinates = {}
    for embedding in certificate["sector_embeddings"].values():
        local = _local_coordinates(embedding["local_artifact"])
        indices = embedding["local_to_global_indices"]
        for (local_row, local_column), terms in local.items():
            coordinate = (indices[local_row], indices[local_column])
            if coordinate in expected_coordinates:
                raise ValueError("sector embeddings overlap")
            expected_coordinates[coordinate] = terms
    if global_coordinates != expected_coordinates:
        raise ValueError("global partial operator embedding mismatch")

    mask = _load_reference(certificate["known_entry_mask"])
    mask_body = {key: value for key, value in mask.items() if key != "sha256"}
    if mask.get("sha256") != hashlib.sha256(
        json.dumps(mask_body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest():
        raise ValueError("known-entry mask internal hash mismatch")
    if (
        mask.get("known_coordinate_count") != 10528
        or mask.get("unknown_coordinate_count") != 288
        or mask.get("known_structural_zero_coordinate_count") != 7328
        or mask.get("known_exact_operator_coordinate_count") != 3200
    ):
        raise ValueError("known-entry mask count mismatch")
    degrees = mask["degree_order"]
    statuses = mask["status_matrix"]
    for row_index, row_degree in enumerate(degrees):
        for column_index, column_degree in enumerate(degrees):
            status = statuses[row_index][column_index]
            if row_degree != column_degree and status != "KNOWN_ZERO_DEGREE_OFF_DIAGONAL":
                raise ValueError("off-degree structural-zero mask drifted")
            if row_degree == column_degree and row_degree in {"-1", "2"} and status != "UNKNOWN_ENDPOINT_A12":
                raise ValueError("endpoint unknown mask drifted")

    slots = certificate["endpoint_A24_import_contract"]["derived_block_slots"]
    export_schema = certificate["endpoint_A24_import_contract"]["accepted_export_schema"]
    export_schema_path = HERE.parents[1] / export_schema["path"]
    if _sha256(export_schema_path) != export_schema["sha256"]:
        raise ValueError("accepted endpoint export schema hash mismatch")
    exported_schema = json.loads(export_schema_path.read_text())
    if exported_schema.get("$id") != export_schema["schema_id"]:
        raise ValueError("accepted endpoint export schema identity mismatch")
    if set(slots[0]["global_row_indices"]) & set(slots[1]["global_row_indices"]):
        raise ValueError("endpoint insertion slots overlap")
    unknown_coordinates = sum(len(slot["global_row_indices"]) ** 2 for slot in slots)
    if unknown_coordinates != certificate["coverage"]["unknown_coordinates"]:
        raise ValueError("endpoint insertion slots do not cover unknown mask")

    for section, key, value in (
        ("endpoint_A24_import_contract", "status", "POPULATED"),
        ("q_Cauchy_import_contract", "status", "POPULATED"),
        ("claim_flags", "BERGER_FULL_A104_CAUCHY_OPERATOR", True),
        ("claim_flags", "BERGER_Q_CAUCHY_104", True),
        ("claim_flags", "BERGER_HADAMARD_DATA", True),
    ):
        mutant = deepcopy(certificate)
        mutant[section][key] = value
        try:
            validate(mutant)
        except ValueError:
            pass
        else:
            raise ValueError(f"overclaim mutation accepted: {section}.{key}")
    return certificate


def main() -> int:
    verify()
    print("BERGER GLOBAL PARTIAL A104 independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
