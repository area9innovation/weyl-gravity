"""Pinned exact import of the Berger rank-one scalar-wave prolongation."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from local_bv.schema_validation import validate_instance
from transfer.berger_gauge_fixed_nonminimal_import import (
    _identity,
    _is_zero,
    _multiply,
    _subtract,
    _zero,
)

from . import raw_endpoint_import as RAW


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "34c184591956aafe97b0728f065b7d044b729f46"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"
CERTIFICATE = "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION.json"
SCHEMA = "d_quotient_classical/schema/berger-raw-endpoint-rank-one-wave-extension-v1.schema.json"
TRANSPORT = "d_quotient_classical/certificates/BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT.json"
PREFLIGHT = "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT.json"
SOURCE_FILES = (
    CERTIFICATE,
    SCHEMA,
    TRANSPORT,
    PREFLIGHT,
    "d_quotient_classical/backreacted_clock/berger_raw_endpoint_rank_one_wave_extension.py",
    "d_quotient_classical/backreacted_clock/verify_berger_raw_endpoint_rank_one_wave_extension.py",
    "d_quotient_classical/backreacted_clock/tests/test_berger_raw_endpoint_rank_one_wave_extension.py",
    "d_quotient_classical/reports/berger-raw-endpoint-rank-one-wave-extension.md",
)
RAW_IMPORT = HERE / "certificates/BERGER_RAW_ENDPOINT_INPUT_IMPORT.json"


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT, check=False, capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned rank-one extension artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _artifact(relative: str) -> dict[str, str]:
    return {"path": relative, "commit": CLASSICAL_COMMIT, "sha256": _sha256_bytes(_git_blob(relative))}


def _load_artifact(reference: object, name: str, shape: tuple[int, int]):
    if not isinstance(reference, dict) or set(reference) != {"format", "path", "sha256"}:
        raise ValueError(f"{name} artifact fields drifted")
    if reference["format"] != "JSON_EXACT_SPARSE_OPERATOR":
        raise ValueError(f"{name} artifact format drifted")
    body = _git_blob(reference["path"])
    if _sha256_bytes(body) != reference["sha256"]:
        raise ValueError(f"{name} artifact hash mismatch")
    return RAW._load_rational_record(name, json.loads(body), shape)


def _block(matrix, rows: range, columns: range):
    return [[matrix[row][column] for column in columns] for row in rows]


def _maximum_order(matrix) -> int:
    return max((len(word) for row in matrix for entry in row for word in entry), default=0)


def validate_import(source: dict[str, Any], schema: dict[str, Any], raw_import: dict[str, Any]) -> dict[str, bool]:
    errors = validate_instance(source, schema)
    if errors:
        raise ValueError(f"rank-one extension source schema validation failed: {errors}")
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("additionalProperties") is not False
        or source.get("result_id") != "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION"
        or source.get("claim_status") != "CERTIFIED_LOCAL_WAVE_PROLONGATION_GREEN_OPEN"
        or source.get("setting_id") != SETTING_ID
        or source.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise ValueError("rank-one extension source identity drifted")
    expected_refs = {
        "raw_witness_transport": {"result_id": "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT", "sha256": _sha256_bytes(_git_blob(TRANSPORT))},
        "raw_endpoint_preflight": {"result_id": "BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT", "sha256": _sha256_bytes(_git_blob(PREFLIGHT))},
    }
    if source.get("dependency_refs") != expected_refs:
        raise ValueError("rank-one extension dependency hashes drifted")
    if source.get("flags") != {
        "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS": False,
        "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION": True,
    } or source.get("next_gate") != "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS":
        raise ValueError("rank-one extension lifecycle boundary drifted")
    if (
        raw_import.get("result_id") != "BERGER_RAW_ENDPOINT_INPUT_IMPORT"
        or raw_import.get("principal_compatibility_certified") is not True
        or raw_import.get("green_execution_authorized") is not False
    ):
        raise ValueError("raw endpoint quantum dependency drifted")

    artifacts = source["prolongation"]["artifacts"]
    f2 = _load_artifact(artifacts["modulus_seed_F2"], "F2", (1, 10))
    l13 = _load_artifact(artifacts["prolonged_L13"], "L13", (13, 13))
    u13 = _load_artifact(artifacts["field_shear_U13"], "U13", (13, 13))
    e13 = _load_artifact(artifacts["equation_shear_E13"], "E13", (13, 13))

    transport = RAW._git_json(RAW.TRANSPORT_CERTIFICATE)
    p34 = RAW._load_artifact(transport["operators"]["P34_raw"], name="P34_raw", shape=(34, 34))
    q34 = RAW._load_artifact(transport["operators"]["q34_raw"], name="q34_raw", shape=(34, 34))
    l12 = _block(p34, range(5, 17), range(5, 17))
    k12 = _block(q34, range(5, 17), range(0, 5))
    pghost = _block(p34, range(0, 5), range(0, 5))

    c13 = _identity(13)
    for column in range(10):
        c13[12][column] = {word: -coefficient for word, coefficient in u13[12][column].items()}
    diagonal = _zero(13, 13)
    for row in range(12):
        for column in range(12):
            diagonal[row][column] = l12[row][column]
    diagonal[12][12] = {(): 1}
    kclock = _block(k12, range(10, 12), range(0, 5))
    defect = _subtract(_multiply(kclock, pghost), kclock)
    defect_entries = sum(bool(entry) for row in defect for entry in row)
    checks = {
        "F2_order_two": _maximum_order(f2) == 2,
        "prolonged_operator_order_four": _maximum_order(l13) == 4,
        "field_shear_support_local_inverse": _is_zero(_subtract(_multiply(u13, c13), _identity(13))),
        "prolonged_direct_sum_equivalence": _is_zero(_subtract(_multiply(_multiply(e13, l13), c13), diagonal)),
        "endpoint_chain_commutation": _is_zero(_subtract(_multiply(l12, k12), _multiply(k12, pghost))),
        "fixed_incidence_defect_nonzero": not _is_zero(defect),
        "fixed_incidence_defect_count_eight": defect_entries == 8,
    }
    factorization = source["exact_factorization"]
    if factorization != {
        "C_R_order": 4,
        "F2": "(Box_0 tr-double_divergence)/6",
        "F2_order": 2,
        "modulus_row": "C_R=-Box_0 F2",
        "order_six_outer_product": "(BC)_6=B_R^(2) C_R^(4)",
        "outer_product_rank": 1,
        "scalar_wave_order": 2,
        "wave_factor_carried_by_C_R": True,
    }:
        raise ValueError("rank-one extension factorization ledger drifted")
    if not all(checks.values()):
        raise ValueError("an independent rank-one extension identity failed")
    return checks


def build_import() -> dict[str, Any]:
    source = _git_json(CERTIFICATE)
    raw_import = json.loads(RAW_IMPORT.read_text())
    checks = validate_import(source, _git_json(SCHEMA), raw_import)
    return {
        "schema": "quantum-weyl-berger-rank-one-wave-extension-import-v1",
        "result_id": "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION_IMPORT",
        "result_state": "LOCAL_SCALAR_WAVE_PROLONGATION_IMPORTED_GREEN_OPERATORS_OPEN",
        "lifecycle_layer": "CLASSICAL_BV_CAUSAL_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
        "extension": {
            "rows": 13,
            "new_field": "y",
            "defining_equation": "y-F2(h)=0",
            "modulus_equation": "R-Box_0 y=source_R",
            "maximum_operator_order": 4,
            "triangular_reduction": "E13 L13 U13^{-1}=L12 direct_sum I1",
        },
        "independent_exact_checks": checks,
        "fixed_incidence_no_go": source["fixed_incidence_no_go"],
        "claim_flags": {**source["flags"], "QUANTUM_CLAIM": False},
        "next_gate": "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "classical_sources": {path: _artifact(path) for path in SOURCE_FILES},
            "raw_endpoint_import": {"path": str(RAW_IMPORT.relative_to(ROOT)), "sha256": hashlib.sha256(RAW_IMPORT.read_bytes()).hexdigest()},
            "operator_artifacts": source["prolongation"]["artifacts"],
        },
        "claim_boundary": (
            "Pins and independently replays the support-local 13-row scalar-wave prolongation, "
            "its exact triangular direct-sum reduction, and the fixed-incidence obstruction. "
            "It constructs no advanced/retarded operators, Green-hyperbolicity theorem, retained "
            "26-row causal homotopy, causal D-Cartan realization, Hadamard state, QME, or quantum result."
        ),
    }
