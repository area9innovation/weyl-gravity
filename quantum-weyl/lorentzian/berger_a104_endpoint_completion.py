"""Insert the classical endpoint A12 blocks into the global Berger A104."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from transfer.berger_gauge_fixed_nonminimal_import import _zero
from transfer.berger_retained_q1_import import _normalize

from .berger_a104_cauchy_operator_preflight import _matrix_record


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARTIAL_CERT = HERE / "certificates/BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY.json"
PARTIAL_OPERATOR = HERE / "generated/berger_a104_global_partial_assembly/global_A104_partial.json"
KNOWN_MASK = HERE / "generated/berger_a104_global_partial_assembly/global_A104_known_entry_mask.json"
CLASSICAL_EXPORT = ROOT / "d_quotient_classical/certificates/BERGER_ENDPOINT_A24_CAUCHY_EXPORT.json"
EXPORT_SCHEMA = HERE / "schema/berger-endpoint-a24-cauchy-export-v1.schema.json"
SCHEMA = HERE / "schema/berger-a104-endpoint-completion-v1.schema.json"
OUTPUT = HERE / "certificates/BERGER_A104_ENDPOINT_COMPLETION.json"
GENERATED = HERE / "generated/berger_a104_endpoint_completion"
REPORT = ROOT / "quantum-weyl/reports/berger-a104-endpoint-completion.md"
SOURCE_PATHS = (
    "quantum-weyl/lorentzian/berger_a104_endpoint_completion.py",
    "quantum-weyl/lorentzian/berger_a104_endpoint_completion_certificate.py",
    "quantum-weyl/lorentzian/verify_berger_a104_endpoint_completion.py",
    "quantum-weyl/lorentzian/schema/berger-a104-endpoint-completion-v1.schema.json",
    "quantum-weyl/lorentzian/tests/test_berger_a104_endpoint_completion.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(body: object) -> str:
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    identity = payload.get("result_id") or payload.get("schema")
    if not isinstance(identity, str):
        raise ValueError("dependency identity missing")
    return {
        "artifact_id": identity,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _load_record(record: dict[str, Any], shape: tuple[int, int]):
    if record.get("shape") != list(shape):
        raise ValueError("operator shape drifted")
    matrix = _zero(*shape)
    seen: set[tuple[int, int]] = set()
    for row, column, terms in record.get("entries", []):
        coordinate = (row, column)
        if coordinate in seen or not (0 <= row < shape[0] and 0 <= column < shape[1]):
            raise ValueError("operator coordinate drifted")
        seen.add(coordinate)
        operator: dict[tuple[int, ...], sp.Expr] = {}
        for exponents, coefficient_text in terms:
            if len(exponents) != 4 or any(type(value) is not int or value < 0 for value in exponents):
                raise ValueError("operator exponent drifted")
            word = tuple(
                axis for axis, count in enumerate(exponents) for _ in range(count)
            )
            coefficient = sp.sympify(coefficient_text)
            operator[word] = operator.get(word, sp.S.Zero) + coefficient
        matrix[row][column] = _normalize(operator)
    return matrix


def _load_hashed_operator(path: Path, shape: tuple[int, int]):
    record = json.loads(path.read_text())
    body = {"shape": record.get("shape"), "entries": record.get("entries")}
    if record.get("sha256") != _digest(body):
        raise ValueError("operator artifact internal hash drifted")
    return _load_record(record, shape)


def _verify_export_hash(record: dict[str, Any]) -> None:
    body = {key: value for key, value in record.items() if key != "sha256"}
    if record.get("sha256") != _digest(body):
        raise ValueError("classical endpoint export internal hash drifted")


def _artifact_text(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _artifact_reference(payload: dict[str, Any]) -> dict[str, str]:
    return {
        "format": "JSON_EXACT_SPARSE_OPERATOR",
        "path": "quantum-weyl/lorentzian/generated/berger_a104_endpoint_completion/global_A104.json",
        "sha256": hashlib.sha256(_artifact_text(payload).encode()).hexdigest(),
    }


def _source_manifest() -> dict[str, str]:
    return {path: _sha256(ROOT / path) for path in SOURCE_PATHS}


@lru_cache(maxsize=1)
def build() -> tuple[dict[str, Any], dict[str, Any]]:
    partial_cert = json.loads(PARTIAL_CERT.read_text())
    mask = json.loads(KNOWN_MASK.read_text())
    export = json.loads(CLASSICAL_EXPORT.read_text())
    Draft202012Validator(json.loads(EXPORT_SCHEMA.read_text())).validate(export)

    if partial_cert.get("result_state") != "GLOBAL_A104_104_BY_104_KNOWN_MASK_EXACT_TWO_A12_SLOTS_OPEN":
        raise ValueError("partial A104 state drifted")
    if export.get("result_state") != "ENDPOINT_FACTORS_AND_DERIVED_A24_EXACT":
        raise ValueError("classical endpoint export state drifted")
    if export.get("classical_commit") != partial_cert.get("classical_commit"):
        raise ValueError("classical endpoint snapshot mismatch")
    if mask.get("unknown_blocks") != ["ghost_A12", "identity_A12"]:
        raise ValueError("partial A104 unknown-block mask drifted")

    for record in export["factor_records"].values():
        _verify_export_hash(record)
    for record in export["derived_A12_blocks"].values():
        _verify_export_hash(record)

    global_operator = _load_hashed_operator(PARTIAL_OPERATOR, (104, 104))
    partial_sparse_entries = _matrix_record(global_operator)["entries"]
    partial_sparse_coordinates = {
        (row, column) for row, column, _terms in partial_sparse_entries
    }
    slots = partial_cert["endpoint_A24_import_contract"]["derived_block_slots"]
    inserted_coordinates: set[tuple[int, int]] = set()
    insertion_ledger = []
    for slot in slots:
        block_id = slot["block_id"]
        record = export["derived_A12_blocks"][block_id]
        if record["local_ordering"] != slot["local_ordering"]:
            raise ValueError(f"{block_id} local ordering mismatch")
        local = _load_record(record, (12, 12))
        row_indices = slot["global_row_indices"]
        column_indices = slot["global_column_indices"]
        for local_row, global_row in enumerate(row_indices):
            for local_column, global_column in enumerate(column_indices):
                coordinate = (global_row, global_column)
                if coordinate in inserted_coordinates:
                    raise ValueError("endpoint insertion overlap")
                if coordinate in partial_sparse_coordinates:
                    raise ValueError("endpoint insertion overlaps a certified nonzero")
                inserted_coordinates.add(coordinate)
                global_operator[global_row][global_column] = local[local_row][
                    local_column
                ]
        insertion_ledger.append(
            {
                "block_id": block_id,
                "local_shape": [12, 12],
                "global_row_indices": row_indices,
                "global_column_indices": column_indices,
                "inserted_coordinates": 144,
                "inserted_nonzero_sparse_entries": len(record["entries"]),
                "source_block_sha256": record["sha256"],
            }
        )

    expected_unknown = mask["unknown_coordinate_count"]
    if len(inserted_coordinates) != expected_unknown:
        raise ValueError("endpoint insertion did not cover the full unknown mask")

    full_record = _matrix_record(global_operator)
    full_entry_map = {
        (row, column): terms for row, column, terms in full_record["entries"]
    }
    partial_preserved = all(
        full_entry_map.get((row, column)) == terms
        for row, column, terms in partial_sparse_entries
    )
    if not partial_preserved:
        raise ValueError("previously certified A104 coefficient changed")
    source_manifest = _source_manifest()
    result = {
        "schema": "quantum-weyl-berger-a104-endpoint-completion-v1",
        "result_id": "BERGER_A104_ENDPOINT_COMPLETION",
        "result_state": "FULL_A104_104_BY_104_COEFFICIENTWISE_ASSEMBLED_Q_CAUCHY_PAIRING_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "classical_commit": partial_cert["classical_commit"],
        "setting_id": partial_cert["setting_id"],
        "dependency_refs": {
            "partial_A104": _dependency(PARTIAL_CERT),
            "known_entry_mask": {
                "artifact_id": "global_A104_known_entry_mask",
                "path": str(KNOWN_MASK.relative_to(ROOT)),
                "sha256": _sha256(KNOWN_MASK),
            },
            "classical_endpoint_A24_export": _dependency(CLASSICAL_EXPORT),
        },
        "global_ordering": partial_cert["global_ordering"],
        "endpoint_insertion_ledger": insertion_ledger,
        "full_operator": _artifact_reference(full_record),
        "coverage": {
            "total_coordinates": 104**2,
            "known_coordinates": 104**2,
            "unknown_coordinates": 0,
            "known_nonzero_sparse_entries": len(full_record["entries"]),
            "closed_blocks": ["ghost_A12", "identity_A12"],
        },
        "exact_checks": {
            "classical_export_strict_schema_valid": True,
            "classical_snapshot_matches_partial_A104": True,
            "all_factor_and_A12_internal_hashes_valid": True,
            "both_local_orderings_match_frozen_slots": True,
            "endpoint_slots_disjoint": True,
            "all_288_unknown_coordinates_populated": True,
            "partial_10528_coordinates_preserved": partial_preserved,
            "full_A104_has_no_unknown_coordinates": True,
        },
        "remaining_stationary_carrier": {
            "q52_companion": "NOT_CONSTRUCTED",
            "q_Cauchy_104": "NOT_CONSTRUCTED",
            "G_Cauchy_104": "NOT_CONSTRUCTED",
            "real_structure_104": "NOT_CONSTRUCTED",
            "A104_q_Cauchy_commutator": "NOT_COMPUTED",
            "A104_Krein_skew_adjointness": "NOT_COMPUTED",
        },
        "claim_flags": {
            "BERGER_FULL_A104_CAUCHY_OPERATOR": True,
            "BERGER_Q_CAUCHY_104": False,
            "BERGER_CAUCHY_KREIN_FORM": False,
            "BERGER_STATIONARY_GENERATOR_ACCEPTED": False,
            "BERGER_A104_CLOSED_GENERATOR": False,
            "BERGER_A104_ZERO_ISOLATED": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_Q52_Q_CAUCHY_104_AND_CAUCHY_KREIN_FORM",
        "provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _digest(source_manifest),
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus LORENTZIAN-CAUSAL composition imports the exact "
            "classical ghost and identity A12 blocks into the frozen global ordering and "
            "assembles every coefficient of A104. It does not construct q_Cauchy, the "
            "Cauchy/Krein form or real structure, prove closedness or isolate zero, split "
            "frequencies, construct a covariance or Hadamard state, restore a QME or make "
            "an interacting quantum claim."
        ),
    }
    validate(result)
    return result, full_record


def validate(result: dict[str, Any]) -> None:
    if result.get("result_state") != "FULL_A104_104_BY_104_COEFFICIENTWISE_ASSEMBLED_Q_CAUCHY_PAIRING_OPEN":
        raise ValueError("A104 completion state drifted")
    coverage = result.get("coverage", {})
    if coverage.get("known_coordinates") != 10816 or coverage.get(
        "unknown_coordinates"
    ) != 0:
        raise ValueError("A104 coverage drifted")
    if not all(result.get("exact_checks", {}).values()):
        raise ValueError("A104 endpoint completion exact check dropped")
    flags = result.get("claim_flags", {})
    if flags.get("BERGER_FULL_A104_CAUCHY_OPERATOR") is not True:
        raise ValueError("full A104 flag dropped")
    for key in (
        "BERGER_Q_CAUCHY_104",
        "BERGER_CAUCHY_KREIN_FORM",
        "BERGER_STATIONARY_GENERATOR_ACCEPTED",
        "BERGER_A104_CLOSED_GENERATOR",
        "BERGER_A104_ZERO_ISOLATED",
        "BERGER_HADAMARD_DATA",
        "QUANTUM_CLAIM",
    ):
        if flags.get(key) is not False:
            raise ValueError(f"A104 completion over-promoted {key}")


def artifact_text(payload: object) -> str:
    return _artifact_text(payload)
