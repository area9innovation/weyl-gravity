"""Independent quantum-side import of the complete Berger classical unary BV package.

This consumer pins the 54-row gauge-fixed classical artifact and replays its
PBW nilpotency, canonical-shear, and contraction identities without importing
the classical producer.  It deliberately leaves Gate A and ND2 fail-closed:
``classical_binary_q2`` and the local D action/equivariance are still absent.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp

try:
    from .berger_retained_q1_import import _add, _adjoint, _canonical_hash, _compose, _parse_coefficient
except ImportError:
    from berger_retained_q1_import import _add, _adjoint, _canonical_hash, _compose, _parse_coefficient


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
CLASSICAL_COMMIT = "445e26663d06764bc858ff0a004ba6178acce75f"
CERTIFICATE_RELATIVE = "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
SCHEMA_RELATIVE = "d_quotient_classical/schema/berger-gauge-fixed-nonminimal-completion-v1.schema.json"
PRODUCER_RELATIVE = "d_quotient_classical/backreacted_clock/berger_gauge_fixed_nonminimal_completion.py"
VERIFIER_RELATIVE = "d_quotient_classical/backreacted_clock/verify_berger_gauge_fixed_nonminimal_completion.py"
TEST_RELATIVE = "d_quotient_classical/backreacted_clock/tests/test_berger_gauge_fixed_nonminimal_completion.py"
REPORT_RELATIVE = "d_quotient_classical/reports/berger-gauge-fixed-nonminimal-completion.md"
UNFIXED_RELATIVE = "d_quotient_classical/certificates/BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION.json"
MINIMAL_RELATIVE = "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
RETAINED_RELATIVE = "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
SCHEMA_ID = "quantum-weyl-berger-gauge-fixed-nonminimal-import-v1"

ScalarOperator = dict[tuple[int, ...], sp.Expr]
OperatorMatrix = list[list[ScalarOperator]]


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
    if result.returncode != 0:
        raise ValueError(f"missing pinned classical artifact {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {"path": relative, "commit": CLASSICAL_COMMIT, "sha256": hashlib.sha256(_git_blob(relative)).hexdigest()}


def _zero(rows: int, columns: int) -> OperatorMatrix:
    return [[{} for _ in range(columns)] for _ in range(rows)]


def _identity(rank: int) -> OperatorMatrix:
    value = _zero(rank, rank)
    for index in range(rank):
        value[index][index] = {(): sp.S.One}
    return value


def _negative(matrix: OperatorMatrix) -> OperatorMatrix:
    return [[{word: -coefficient for word, coefficient in entry.items()} for entry in row] for row in matrix]


def _matrix_add(left: OperatorMatrix, right: OperatorMatrix) -> OperatorMatrix:
    return [[_add(left[row][column], right[row][column]) for column in range(len(left[0]))] for row in range(len(left))]


def _subtract(left: OperatorMatrix, right: OperatorMatrix) -> OperatorMatrix:
    return _matrix_add(left, _negative(right))


def _multiply(outer: OperatorMatrix, inner: OperatorMatrix) -> OperatorMatrix:
    output = _zero(len(outer), len(inner[0]))
    support = {middle: [(column, entry) for column, entry in enumerate(row) if entry] for middle, row in enumerate(inner)}
    for row, entries in enumerate(outer):
        for middle, left in enumerate(entries):
            if left:
                for column, right in support[middle]:
                    output[row][column] = _add(output[row][column], _compose(left, right))
    return output


def _adjoint_transpose(matrix: OperatorMatrix) -> OperatorMatrix:
    return [[_adjoint(matrix[column][row]) for column in range(len(matrix))] for row in range(len(matrix[0]))]


def _embed(target: OperatorMatrix, block: OperatorMatrix, row_offset: int, column_offset: int) -> None:
    for row, values in enumerate(block):
        for column, operator in enumerate(values):
            target[row + row_offset][column + column_offset] = operator


def _load_record(name: str, record: object, shape: tuple[int, int]) -> OperatorMatrix:
    if not isinstance(record, dict) or set(record) != {"shape", "entries", "sha256"}:
        raise ValueError(f"{name} record fields drifted")
    if record["shape"] != list(shape):
        raise ValueError(f"{name} shape drifted")
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _canonical_hash(body):
        raise ValueError(f"{name} record hash mismatch")
    output = _zero(*shape)
    seen: set[tuple[int, int]] = set()
    entries = record["entries"]
    if not isinstance(entries, list):
        raise ValueError(f"{name} entries are not a list")
    for item in entries:
        if not isinstance(item, list) or len(item) != 3:
            raise ValueError(f"{name} malformed entry")
        row, column, terms = item
        if (
            type(row) is not int
            or type(column) is not int
            or not 0 <= row < shape[0]
            or not 0 <= column < shape[1]
            or (row, column) in seen
            or not isinstance(terms, list)
            or not terms
        ):
            raise ValueError(f"{name} duplicate or out-of-range entry")
        operator: ScalarOperator = {}
        for term in terms:
            if not isinstance(term, list) or len(term) != 2:
                raise ValueError(f"{name} malformed PBW term")
            exponents, coefficient = term
            if (
                not isinstance(exponents, list)
                or len(exponents) != 4
                or any(type(count) is not int or count < 0 for count in exponents)
                or not isinstance(coefficient, str)
            ):
                raise ValueError(f"{name} malformed PBW monomial")
            word = tuple(axis for axis, count in enumerate(exponents) for _ in range(count))
            if word in operator:
                raise ValueError(f"{name} repeats a PBW monomial")
            operator[word] = _parse_coefficient(coefficient)
        output[row][column] = operator
        seen.add((row, column))
    return output


def _is_zero(matrix: OperatorMatrix) -> bool:
    return all(not entry for row in matrix for entry in row)


def validate_import(payload: dict[str, Any], schema: dict[str, Any]) -> dict[str, object]:
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-gauge-fixed-nonminimal-completion-v1.schema.json"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("classical gauge-fixed schema identity or strictness drifted")
    if set(payload) != {
        "schema", "result_id", "setting_id", "claim_status", "dependency_tags",
        "dependency_refs", "operator_semantics", "row_layout", "gauge_fermion",
        "classical_unary_q1", "contraction", "exact_checks", "flags",
        "quantum_handoff", "next_gate", "claim_boundary",
    }:
        raise ValueError("classical gauge-fixed payload fields drifted")
    if (
        payload.get("schema")
        != "pure-weyl-berger-gauge-fixed-nonminimal-completion-v1"
        or payload.get("result_id") != "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION"
        or payload.get("claim_status")
        != "CERTIFIED_COMPLETE_GAUGE_FIXED_UNARY_CONTRACTION"
        or payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
    ):
        raise ValueError("classical gauge-fixed result identity drifted")
    refs = payload["dependency_refs"]
    if not isinstance(refs, dict) or set(refs) != {"minimal_34", "unfixed_nonminimal"}:
        raise ValueError("classical gauge-fixed dependency inventory drifted")
    for name, relative, result_id in (
        ("minimal_34", MINIMAL_RELATIVE, "BERGER_MINIMAL_34_PORTABLE_CONTRACTION"),
        ("unfixed_nonminimal", UNFIXED_RELATIVE, "BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION"),
    ):
        reference = refs[name]
        if (
            not isinstance(reference, dict)
            or set(reference) != {"result_id", "sha256"}
            or reference["result_id"] != result_id
            or reference["sha256"] != hashlib.sha256(_git_blob(relative)).hexdigest()
        ):
            raise ValueError(f"classical gauge-fixed dependency drifted: {name}")
    semantics = payload["operator_semantics"]
    if semantics["portable_name"] != "classical_unary_q1" or semantics["not_quantum_loop_operator"] is not True:
        raise ValueError("classical unary operator was conflated with quantum Q1")
    rows = payload["row_layout"]
    if rows["total_rows"] != 54 or rows["degree_ranks"] != [5, 22, 22, 5] or sorted(row["index"] for row in rows["component_rows"]) != list(range(54)):
        raise ValueError("54-row classical layout drifted")

    flags = payload["flags"]
    if not all(flags[key] is True for key in ("BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM", "BERGER_NONMINIMAL_COMPLETION", "BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT")):
        raise ValueError("classical unary completion flags drifted")
    for key in ("CLASSICAL_SUPPORT_LOCAL_Q2", "BERGER_LOCAL_D_ACTION_EQUIVARIANT", "BERGER_GENERAL_KOSZUL_TATE_EXPORT", "BERGER_CAUSAL_GREEN_HOMOTOPY", "BERGER_HADAMARD_DATA", "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT"):
        if flags[key] is not False:
            raise ValueError("classical downstream boundary was crossed")

    # Validate the largest record digest before allocating the other PBW
    # matrices, so tampering fails cheaply and deterministically.
    q1 = _load_record("classical_unary_q1", payload["classical_unary_q1"]["matrix"], (54, 54))

    nilpotent = _load_record("canonical shear N", payload["gauge_fermion"]["canonical_shear_nilpotent_part"], (54, 54))
    identity = _identity(54)
    shear = _matrix_add(identity, nilpotent)
    inverse = _subtract(identity, nilpotent)
    if not _is_zero(_multiply(nilpotent, nilpotent)) or not _is_zero(_subtract(_multiply(shear, inverse), identity)):
        raise ValueError("canonical shear algebra failed")
    contraction = payload["contraction"]
    omega = _load_record("cyclic pairing", contraction["cyclic_pairing"], (54, 54))
    if not _is_zero(_subtract(_multiply(_multiply(_adjoint_transpose(shear), omega), shear), omega)):
        raise ValueError("canonical shear does not preserve the cyclic pairing")

    iota = _load_record("iota_cl", contraction["iota_cl"], (54, 26))
    projection = _load_record("pi_cl", contraction["pi_cl"], (26, 54))
    homotopy = _load_record("S_cl", contraction["S_cl"], (54, 54))
    if not _is_zero(_multiply(q1, q1)):
        raise ValueError("imported classical_unary_q1 is not nilpotent")
    if not _is_zero(_matrix_add(_multiply(_adjoint_transpose(q1), omega), _multiply(omega, q1))):
        raise ValueError("imported classical_unary_q1 is not cyclic")
    retained = _git_json(RETAINED_RELATIVE)
    gauge = _load_record("retained K_spatial", retained["q1_blocks"]["K_spatial"], (10, 3))
    hessian = _load_record("retained H", retained["q1_blocks"]["H_retained"], (10, 10))
    noether = _load_record("retained minus_K_sharp", retained["q1_blocks"]["minus_K_spatial_sharp"], (3, 10))
    q_retained = _zero(26, 26)
    _embed(q_retained, gauge, 3, 0)
    _embed(q_retained, hessian, 13, 3)
    _embed(q_retained, noether, 23, 13)
    if not _is_zero(_subtract(_multiply(q1, iota), _multiply(iota, q_retained))):
        raise ValueError("imported iota_cl is not a chain map")
    if not _is_zero(_subtract(_multiply(projection, q1), _multiply(q_retained, projection))):
        raise ValueError("imported pi_cl is not a chain map")
    if not _is_zero(_subtract(_multiply(projection, iota), _identity(26))):
        raise ValueError("imported pi_cl iota_cl identity failed")
    boundary = _matrix_add(_multiply(q1, homotopy), _multiply(homotopy, q1))
    if not _is_zero(_subtract(boundary, _subtract(identity, _multiply(iota, projection)))):
        raise ValueError("imported contraction identity failed")
    if not _is_zero(_multiply(homotopy, homotopy)) or not _is_zero(_multiply(projection, homotopy)) or not _is_zero(_multiply(homotopy, iota)):
        raise ValueError("imported contraction side condition failed")
    if not _is_zero(_matrix_add(_multiply(_adjoint_transpose(homotopy), omega), _multiply(omega, homotopy))):
        raise ValueError("imported S_cl is not cyclic")

    return {
        "q1_sha256": payload["classical_unary_q1"]["matrix"]["sha256"],
        "iota_sha256": contraction["iota_cl"]["sha256"],
        "pi_sha256": contraction["pi_cl"]["sha256"],
        "S_sha256": contraction["S_cl"]["sha256"],
        "pairing_sha256": contraction["cyclic_pairing"]["sha256"],
        "maximum_differential_order": contraction["maximum_differential_order"],
        "retained_q1_sha256": hashlib.sha256(_git_blob(RETAINED_RELATIVE)).hexdigest(),
    }


@lru_cache(maxsize=1)
def _build_cached() -> dict[str, Any]:
    payload = _git_json(CERTIFICATE_RELATIVE)
    schema = _git_json(SCHEMA_RELATIVE)
    summary = validate_import(payload, schema)
    sources = {name: _artifact(path) for name, path in {
        "classical_certificate": CERTIFICATE_RELATIVE,
        "classical_schema": SCHEMA_RELATIVE,
        "classical_producer": PRODUCER_RELATIVE,
        "classical_independent_verifier": VERIFIER_RELATIVE,
        "classical_test": TEST_RELATIVE,
        "classical_report": REPORT_RELATIVE,
    }.items()}
    return {
        "schema": SCHEMA_ID,
        "result_id": "BERGER_GAUGE_FIXED_NONMINIMAL_IMPORT",
        "result_state": "COMPLETE_CLASSICAL_UNARY_PACKAGE_IMPORTED_NONLINEAR_INPUT_BLOCKED",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_id": payload["setting_id"],
        "classical_result": {"result_id": payload["result_id"], "claim_status": payload["claim_status"], "commit": CLASSICAL_COMMIT, "certificate_sha256": sources["classical_certificate"]["sha256"]},
        "coverage": {"total_rows": 54, "minimal_rows": 34, "nonminimal_rows": 20, "retained_rows": 26, "gauge_fixed_classical_unary_complete": True, "support_local_contraction_complete": True, "cyclic_pairing_complete": True},
        "map_hashes": summary,
        "independent_checks": {"strict_classical_schema": True, "classical_dependency_hashes": True, "all_54_rows_typed": True, "PBW_record_hashes": True, "canonical_shear_nilpotent_and_invertible": True, "canonical_shear_pairing_preserving": True, "classical_unary_q1_squared_zero": True, "classical_unary_q1_cyclic": True, "iota_cl_chain_map": True, "pi_cl_chain_map": True, "pi_cl_iota_cl_identity": True, "all_row_contraction_identity": True, "contraction_side_conditions": True, "homotopy_cyclic": True, "retained_complex_cohomology_preserved_by_SDR": True},
        "classical_freeze_gate": {"status": "FAIL_CLOSED", "reason": "complete unary/nonminimal prerequisite imported; support-local q2 and local D action/equivariance are still absent"},
        "nd2_gate": {"unary_nonminimal_prerequisite_satisfied": True, "support_local_classical_binary_q2": "NOT_AVAILABLE", "local_D_action_and_equivariance": "NOT_AVAILABLE", "general_nonlinear_Koszul_Tate": "NOT_AVAILABLE", "causal_green_hadamard": "NOT_AVAILABLE", "physical_execution_authorized": False, "next_gate": "IMPORT_SUPPORT_LOCAL_Q2_AND_D_ACTION"},
        "provenance": {"classical_sources": {**sources, "retained_q1_dependency": _artifact(RETAINED_RELATIVE)}, "classical_sources_sha256": _canonical_hash({**sources, "retained_q1_dependency": _artifact(RETAINED_RELATIVE)})},
        "claim_boundary": "The complete gauge-fixed 54-row classical_unary_q1, cyclic pairing, and support-local contraction are independently imported. This is classical unary evidence, not hbar Q1. No nonlinear q2, local D-equivariance, nonlinear Koszul-Tate, causal/Hadamard, ND2 physical, or quantum claim is authorized.",
    }


def build_import() -> dict[str, Any]:
    return deepcopy(_build_cached())
