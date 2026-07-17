"""Fail-closed algebraic consumer for the retained Berger stationary carrier.

The four imported 104-row matrices are exact PBW differential-operator
matrices.  This module replays the finite algebraic identities.  Spectral
isolation of zero belongs to a later closed-realization theorem and is not
inferred from these coefficient tables.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from jsonschema import Draft202012Validator
import sympy as sp

from local_bv.schema_validation import validate_instance
from transfer.berger_gauge_fixed_nonminimal_import import (
    _adjoint_transpose,
    _identity,
    _is_zero,
    _matrix_add,
    _multiply,
    _subtract,
    _zero,
)
from transfer.berger_retained_q1_import import _parse_coefficient


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT_SCHEMA = HERE / "schema/berger-retained-stationary-generator-input-v1.schema.json"
MATRIX_SCHEMA = HERE / "schema/berger-retained-stationary-carrier-matrix-v1.schema.json"
PREFLIGHT = HERE / "certificates/BERGER_A104_CAUCHY_OPERATOR_PREFLIGHT.json"

ARTIFACT_IDS = (
    "A104",
    "q_Cauchy_104",
    "G_Cauchy_104",
    "real_structure_104",
)
MAXIMUM_ORDERS = {
    "A104": 2,
    "q_Cauchy_104": 1,
    "G_Cauchy_104": 0,
    "real_structure_104": 0,
}


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git_prefix() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()


@lru_cache(maxsize=None)
def _git_blob(commit: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing stationary-carrier artifact at {commit}: {relative}")
    return result.stdout


def _git_json(commit: str, relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(commit, relative))
    if not isinstance(value, dict):
        raise ValueError(f"stationary-carrier JSON is not an object: {relative}")
    return value


def _expected_row_ids() -> list[str]:
    value = json.loads(PREFLIGHT.read_text())
    rows = value["Cauchy_row_ledger"]["rows"]
    if [row["index"] for row in rows] != list(range(104)):
        raise ValueError("frozen Cauchy row ledger drifted")
    return [row["row_id"] for row in rows]


def _validate_manifest(manifest: Mapping[str, Any]) -> None:
    schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(manifest)
    commit = manifest["classical_commit"]
    paths: set[str] = set()
    for artifact_id in ARTIFACT_IDS:
        reference = manifest["artifacts"][artifact_id]
        path = reference["path"]
        if path in paths or not path.startswith("d_quotient_classical/"):
            raise ValueError("stationary-carrier artifact path is duplicate or out of scope")
        paths.add(path)
        if _sha256(_git_blob(commit, path)) != reference["sha256"]:
            raise ValueError(f"stationary-carrier blob hash drifted: {artifact_id}")


def _load_matrix_record(
    payload: Mapping[str, Any], artifact_id: str, expected_rows: list[str]
) -> list[list[dict[tuple[int, ...], sp.Expr]]]:
    if payload.get("artifact_id") != artifact_id:
        raise ValueError(f"stationary artifact identity drifted: {artifact_id}")
    if payload.get("shape") != [104, 104]:
        raise ValueError(f"stationary artifact shape drifted: {artifact_id}")
    if payload.get("row_ids") != expected_rows or payload.get("column_ids") != expected_rows:
        raise ValueError(f"stationary artifact ordering drifted: {artifact_id}")
    body = {
        "artifact_id": payload["artifact_id"],
        "shape": payload["shape"],
        "row_ids": payload["row_ids"],
        "column_ids": payload["column_ids"],
        "entries": payload["entries"],
    }
    if payload.get("sha256") != _canonical_hash(body):
        raise ValueError(f"stationary artifact internal hash drifted: {artifact_id}")

    matrix = _zero(104, 104)
    seen: set[tuple[int, int]] = set()
    maximum_order = 0
    for row, column, terms in payload["entries"]:
        if (row, column) in seen:
            raise ValueError(f"duplicate stationary matrix coordinate: {artifact_id}")
        seen.add((row, column))
        operator: dict[tuple[int, ...], sp.Expr] = {}
        for exponents, coefficient in terms:
            word = tuple(
                axis
                for axis, multiplicity in enumerate(exponents)
                for _ in range(multiplicity)
            )
            if word in operator:
                raise ValueError(f"duplicate stationary PBW monomial: {artifact_id}")
            operator[word] = _parse_coefficient(coefficient)
            maximum_order = max(maximum_order, len(word))
        matrix[row][column] = operator
    if maximum_order > MAXIMUM_ORDERS[artifact_id]:
        raise ValueError(f"stationary artifact differential order drifted: {artifact_id}")
    return matrix


def _constant_rank(matrix: list[list[dict[tuple[int, ...], sp.Expr]]]) -> int:
    if any(word for row in matrix for operator in row for word in operator):
        raise ValueError("expected an order-zero stationary carrier")
    return sp.MutableSparseMatrix(
        len(matrix),
        len(matrix[0]),
        {
            (row, column): operator[()]
            for row, values in enumerate(matrix)
            for column, operator in enumerate(values)
            if operator
        },
    ).rank()


def evaluate_matrices(
    matrices: Mapping[str, list[list[dict[tuple[int, ...], sp.Expr]]]]
) -> dict[str, bool]:
    """Replay exact carrier identities; exposed for small mutation fixtures."""

    A = matrices["A104"]
    q = matrices["q_Cauchy_104"]
    G = matrices["G_Cauchy_104"]
    real = matrices["real_structure_104"]
    rank = len(A)
    if not rank or any(
        len(matrix) != rank or any(len(row) != rank for row in matrix)
        for matrix in (A, q, G, real)
    ):
        raise ValueError("stationary carrier matrices do not share a square shape")
    identity = _identity(rank)
    q_adjoint = _adjoint_transpose(q)
    A_adjoint = _adjoint_transpose(A)
    real_adjoint = _adjoint_transpose(real)
    return {
        "q_Cauchy_squared_zero": _is_zero(_multiply(q, q)),
        "A104_supercommutes_with_q_Cauchy": _is_zero(
            _subtract(_multiply(A, q), _multiply(q, A))
        ),
        "G_Cauchy_nondegenerate": _constant_rank(G) == rank,
        "G_Cauchy_BRST_compatible": _is_zero(
            _matrix_add(_multiply(q_adjoint, G), _multiply(G, q))
        ),
        "A104_Krein_skew_adjoint": _is_zero(
            _matrix_add(_multiply(A_adjoint, G), _multiply(G, A))
        ),
        "real_structure_is_involution": _is_zero(
            _subtract(_multiply(real, real), identity)
        ),
        "real_structure_intertwines_A104": _is_zero(
            _subtract(_multiply(real, A), _multiply(A, real))
        ),
        "real_structure_intertwines_q_Cauchy": _is_zero(
            _subtract(_multiply(real, q), _multiply(q, real))
        ),
        "real_structure_preserves_G_Cauchy": _is_zero(
            _subtract(_multiply(_multiply(real_adjoint, G), real), G)
        ),
    }


def evaluate(manifest: Mapping[str, Any]) -> dict[str, Any]:
    _validate_manifest(manifest)
    commit = manifest["classical_commit"]
    matrix_schema = json.loads(MATRIX_SCHEMA.read_text())
    Draft202012Validator.check_schema(matrix_schema)
    expected_rows = _expected_row_ids()
    matrices = {}
    artifact_hashes = {}
    for artifact_id in ARTIFACT_IDS:
        reference = manifest["artifacts"][artifact_id]
        payload = _git_json(commit, reference["path"])
        errors = validate_instance(payload, matrix_schema)
        if errors:
            raise ValueError(
                f"strict stationary matrix schema failure ({artifact_id}): "
                + "; ".join(errors)
            )
        if payload.get("source_commit") != commit:
            raise ValueError(f"stationary matrix source commit drifted: {artifact_id}")
        matrices[artifact_id] = _load_matrix_record(payload, artifact_id, expected_rows)
        artifact_hashes[artifact_id] = {
            "blob_sha256": reference["sha256"],
            "matrix_sha256": payload["sha256"],
        }
    checks = evaluate_matrices(matrices)
    return {
        "manifest_canonical_sha256": _canonical_hash(manifest),
        "classical_commit": commit,
        "artifact_hashes": artifact_hashes,
        "exact_checks": checks,
        "verdict": (
            "ACCEPTED_EXACT_STATIONARY_CARRIER"
            if all(checks.values())
            else "REJECTED_EXACT_STATIONARY_CARRIER_DEFECT"
        ),
        "analytic_zero_spectrum_status": "NOT_DECIDED_BY_ALGEBRAIC_IMPORT",
    }
