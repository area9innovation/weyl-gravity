"""Independent import of the portable 34-row minimal Berger contraction.

The classical export combines the retained PBW-valued unary differential with
eight temporal-diffeomorphism/Weyl clock rows and supplies explicit order-zero
``iota_cl``, ``pi_cl``, and ``S_cl`` matrices.  This consumer pins the final
portable artifact and reconstructs its exact chain and cyclic identities
without importing the classical producer implementation.

Only the minimal unary contraction is accepted here.  No ``q2``, local
``D`` action, nonminimal completion, admissibility policy, or physical ND2
execution is inferred.
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
    from .berger_retained_q1_import import (
        OperatorMatrix,
        _add,
        _adjoint,
        _canonical_hash,
        _load_record,
        _multiply,
        validate_classical_retained_q1,
    )
except ImportError:
    from berger_retained_q1_import import (
        OperatorMatrix,
        _add,
        _adjoint,
        _canonical_hash,
        _load_record,
        _multiply,
        validate_classical_retained_q1,
    )


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
EXPORT_COMMIT = "7ddcaaf32185583d47510b4b528b67dde1e3064d"
PORTABLE_COMMIT = "9278ba7dffa2e8d85292c2a8cc25b03f0ca47847"

CERTIFICATE_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
)
SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/berger-minimal-34-portable-contraction-v1.schema.json"
)
PRODUCER_RELATIVE = (
    "d_quotient_classical/backreacted_clock/berger_minimal_34_portable_contraction.py"
)
INDEPENDENT_VERIFIER_RELATIVE = (
    "d_quotient_classical/backreacted_clock/verify_berger_minimal_34_portable_contraction.py"
)
TEST_RELATIVE = (
    "d_quotient_classical/backreacted_clock/tests/"
    "test_berger_minimal_34_portable_contraction.py"
)
REPORT_RELATIVE = (
    "d_quotient_classical/reports/berger-minimal-34-portable-contraction.md"
)
Q1_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
)
Q1_SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/berger-retained-minimal-operator-v1.schema.json"
)
LAYOUT_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json"
)
CLOCK_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json"
)

SCHEMA_ID = "quantum-weyl-berger-minimal-34-contraction-import-v1"
RETAINED_TO_FULL = (
    0, 1, 2,
    5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
    17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
    29, 30, 31,
)
CLOCK_ROWS = (3, 4, 15, 16, 27, 28, 32, 33)
FULL_ROWS = (
    "c_spatial_1", "c_spatial_2", "c_spatial_3", "tau", "sigma",
    "h_hat_00", "h_hat_01", "h_hat_02", "h_hat_03", "h_hat_11",
    "h_hat_12", "h_hat_13", "h_hat_22", "h_hat_23", "h_hat_33",
    "R", "Theta",
    "h_hat_star_00", "h_hat_star_01", "h_hat_star_02", "h_hat_star_03",
    "h_hat_star_11", "h_hat_star_12", "h_hat_star_13", "h_hat_star_22",
    "h_hat_star_23", "h_hat_star_33", "R_star", "Theta_star",
    "c_spatial_star_1", "c_spatial_star_2", "c_spatial_star_3",
    "tau_star", "sigma_star",
)


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str, *, commit: str = PORTABLE_COMMIT) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise ValueError(f"missing pinned contraction artifact {relative} at {commit}")
    return result.stdout


def _git_json(relative: str, *, commit: str = PORTABLE_COMMIT) -> dict[str, Any]:
    try:
        payload = json.loads(_git_blob(relative, commit=commit))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid pinned contraction JSON: {relative}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"pinned contraction JSON is not an object: {relative}")
    return payload


def _artifact(relative: str, *, commit: str = PORTABLE_COMMIT) -> dict[str, str]:
    return {
        "path": relative,
        "commit": commit,
        "sha256": hashlib.sha256(_git_blob(relative, commit=commit)).hexdigest(),
    }


def _require_fields(value: object, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label} has the wrong field set")
    return value


def _validate_schema(schema: dict[str, Any]) -> None:
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-minimal-34-portable-contraction-v1.schema.json"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("portable contraction schema identity or strictness drifted")
    definitions = schema.get("$defs")
    required = {
        "operator34x34",
        "operator34x26",
        "operator26x34",
        "pbwOperatorRecord",
        "pbwMatrixEntry",
        "pbwTerm",
    }
    if not isinstance(definitions, dict) or required - set(definitions):
        raise ValueError("portable contraction schema lacks strict operator definitions")


def _load_constant_record(
    name: str,
    record: object,
    expected_shape: tuple[int, int],
) -> sp.Matrix:
    value = _require_fields(record, {"shape", "entries", "sha256"}, name)
    if value["shape"] != list(expected_shape):
        raise ValueError(f"{name} shape drifted")
    body = {"shape": value["shape"], "entries": value["entries"]}
    if value["sha256"] != _canonical_hash(body):
        raise ValueError(f"{name} record hash mismatch")
    entries = value["entries"]
    if not isinstance(entries, list):
        raise ValueError(f"{name} entries are not a list")
    output = sp.zeros(*expected_shape)
    seen: set[tuple[int, int]] = set()
    for entry in entries:
        if not isinstance(entry, list) or len(entry) != 3:
            raise ValueError(f"{name} contains a malformed entry")
        row, column, terms = entry
        if (
            type(row) is not int
            or type(column) is not int
            or not 0 <= row < expected_shape[0]
            or not 0 <= column < expected_shape[1]
            or (row, column) in seen
            or not isinstance(terms, list)
            or len(terms) != 1
        ):
            raise ValueError(f"{name} entry support is invalid")
        exponents, coefficient = terms[0]
        if exponents != [0, 0, 0, 0] or not isinstance(coefficient, str):
            raise ValueError(f"{name} is not an order-zero exact matrix")
        try:
            scalar = sp.Rational(coefficient)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} coefficient is not rational") from exc
        if scalar == 0:
            raise ValueError(f"{name} retains an explicit zero")
        output[row, column] = scalar
        seen.add((row, column))
    return output


def _operator_zero(rows: int, columns: int) -> OperatorMatrix:
    return [[{} for _ in range(columns)] for _ in range(rows)]


def _constant_operator(matrix: sp.Matrix) -> OperatorMatrix:
    return [
        [({(): matrix[row, column]} if matrix[row, column] != 0 else {})
         for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _embed(
    target: OperatorMatrix,
    block: OperatorMatrix,
    row_offset: int,
    column_offset: int,
) -> None:
    for row, values in enumerate(block):
        for column, operator in enumerate(values):
            target[row + row_offset][column + column_offset] = operator


def _matrix_add(left: OperatorMatrix, right: OperatorMatrix) -> OperatorMatrix:
    if len(left) != len(right) or len(left[0]) != len(right[0]):
        raise ValueError("operator matrix addition shape mismatch")
    return [
        [_add(left[row][column], right[row][column]) for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def _identity_operator(dimension: int) -> OperatorMatrix:
    value = _operator_zero(dimension, dimension)
    for index in range(dimension):
        value[index][index] = {(): sp.S.One}
    return value


def _adjoint_transpose(matrix: OperatorMatrix) -> OperatorMatrix:
    return [
        [_adjoint(matrix[column][row]) for column in range(len(matrix))]
        for row in range(len(matrix[0]))
    ]


def _expected_rows() -> list[dict[str, object]]:
    degrees = [-1] * 5 + [0] * 12 + [1] * 12 + [2] * 5
    return [
        {"index": index, "row_id": row_id, "degree": degree}
        for index, (row_id, degree) in enumerate(zip(FULL_ROWS, degrees, strict=True))
    ]


def validate_portable_contraction(
    payload: dict[str, Any],
    schema: dict[str, Any],
    retained_q1: dict[str, Any],
    retained_schema: dict[str, Any],
    retained_layout: dict[str, Any],
    clock_sdr: dict[str, Any],
) -> dict[str, object]:
    """Validate the final portable payload and independently replay its identities."""

    _validate_schema(schema)
    _require_fields(
        payload,
        {
            "schema", "result_id", "setting_id", "claim_status",
            "dependency_tags", "dependency_refs", "operator_semantics",
            "row_layout", "classical_unary_q1", "contraction", "exact_checks",
            "flags", "next_gate", "claim_boundary",
        },
        "portable contraction",
    )
    if (
        payload["schema"] != "pure-weyl-berger-minimal-34-portable-contraction-v1"
        or payload["result_id"] != "BERGER_MINIMAL_34_PORTABLE_CONTRACTION"
        or payload["setting_id"]
        != "compact_positive_berger_clock_fixed_coupling_linearized"
        or payload["claim_status"]
        != "CERTIFIED_COMPLETE_MINIMAL_UNARY_CONTRACTION"
        or payload["dependency_tags"] != ["LOCAL-ALGEBRAIC"]
    ):
        raise ValueError("portable contraction identity or scope drifted")

    references = _require_fields(
        payload["dependency_refs"],
        {"retained_classical_unary_q1", "clock_sdr", "retained_layout"},
        "portable contraction dependencies",
    )
    dependencies = {
        "retained_classical_unary_q1": (Q1_RELATIVE, retained_q1),
        "clock_sdr": (CLOCK_RELATIVE, clock_sdr),
        "retained_layout": (LAYOUT_RELATIVE, retained_layout),
    }
    for name, (relative, dependency) in dependencies.items():
        reference = _require_fields(
            references[name], {"result_id", "sha256"}, f"{name} reference"
        )
        if reference["result_id"] != dependency["result_id"]:
            raise ValueError(f"{name} result identity drifted")
        if reference["sha256"] != hashlib.sha256(_git_blob(relative)).hexdigest():
            raise ValueError(f"{name} dependency hash drifted")

    exact_checks = payload["exact_checks"]
    expected_checks = {
        "all_34_minimal_rows_enumerated", "classical_unary_q1_squared_zero",
        "iota_cl_chain_map", "pi_cl_chain_map", "pi_cl_iota_cl_identity",
        "all_row_contraction_identity", "complementary_chain_projectors",
        "contraction_side_conditions", "support_local_order_zero",
        "clock_homotopy_cyclic",
    }
    if (
        not isinstance(exact_checks, dict)
        or set(exact_checks) != expected_checks
        or any(value is not True for value in exact_checks.values())
    ):
        raise ValueError("portable contraction exact-check ledger drifted")
    flags = _require_fields(
        payload["flags"],
        {
            "BERGER_MINIMAL_34_PORTABLE_CONTRACTION",
            "BERGER_COMBINED_MINIMAL_CONTRACTION_ALL_34_ROWS",
            "BERGER_NONMINIMAL_COMPLETION", "CLASSICAL_SUPPORT_LOCAL_Q2",
            "BERGER_LOCAL_D_ACTION_EQUIVARIANT",
            "BERGER_GENERAL_KOSZUL_TATE_EXPORT",
            "BERGER_CURVED_CLOCK_REATTACHED_WITNESS",
            "BERGER_CAUSAL_GREEN_HOMOTOPY", "BERGER_HADAMARD_DATA",
            "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT",
        },
        "portable contraction flags",
    )
    proved = {
        "BERGER_MINIMAL_34_PORTABLE_CONTRACTION",
        "BERGER_COMBINED_MINIMAL_CONTRACTION_ALL_34_ROWS",
    }
    if any(flags[name] is not True for name in proved) or any(
        flags[name] is not False for name in set(flags) - proved
    ):
        raise ValueError("portable contraction flags crossed their boundary")
    semantics = payload["operator_semantics"]
    if (
        not isinstance(semantics, dict)
        or semantics.get("portable_name") != "classical_unary_q1"
        or semantics.get("mathematical_name") != "ell_1_cl"
        or semantics.get("not_quantum_loop_operator") is not True
    ):
        raise ValueError("portable classical unary semantics drifted")

    layout = _require_fields(
        payload["row_layout"],
        {
            "total_rows", "degree_ranks", "component_rows",
            "retained_row_indices", "clock_row_indices", "field_clock_order",
            "ghost_clock_order",
        },
        "portable contraction row layout",
    )
    if (
        layout["total_rows"] != 34
        or layout["degree_ranks"] != [5, 12, 12, 5]
        or layout["component_rows"] != _expected_rows()
        or layout["retained_row_indices"] != list(RETAINED_TO_FULL)
        or layout["clock_row_indices"] != list(CLOCK_ROWS)
        or layout["field_clock_order"] != ["R", "Theta"]
        or layout["ghost_clock_order"] != ["tau", "sigma"]
    ):
        raise ValueError("portable contraction row layout drifted")

    unary = _require_fields(
        payload["classical_unary_q1"],
        {"retained_blocks_ref", "full_shape", "degree_ranks", "assembly", "clock_extension"},
        "portable classical unary q1",
    )
    if (
        unary["retained_blocks_ref"]
        != "dependency_refs.retained_classical_unary_q1"
        or unary["full_shape"] != [34, 34]
        or unary["degree_ranks"] != [5, 12, 12, 5]
    ):
        raise ValueError("portable classical unary q1 layout drifted")
    assembly = _require_fields(
        unary["assembly"],
        {
            "K_spatial_embedding", "H_retained_embedding",
            "minus_K_spatial_sharp_embedding", "clock_extension_meaning",
        },
        "portable q1 assembly",
    )
    if assembly != {
        "K_spatial_embedding": {"row_offset": 5, "column_offset": 0},
        "H_retained_embedding": {"row_offset": 17, "column_offset": 5},
        "minus_K_spatial_sharp_embedding": {"row_offset": 29, "column_offset": 17},
        "clock_extension_meaning": [
            "ell_1 sigma=-R", "ell_1 tau=Theta",
            "ell_1 Theta_star=-tau_star", "ell_1 R_star=sigma_star",
        ],
    }:
        raise ValueError("portable q1 assembly convention drifted")

    contraction = _require_fields(
        payload["contraction"],
        {
            "iota_cl", "pi_cl", "S_cl", "P_retained", "P_clock",
            "identity", "side_conditions", "support_local",
            "maximum_differential_order", "cyclic",
        },
        "portable contraction maps",
    )
    iota = _load_constant_record("iota_cl", contraction["iota_cl"], (34, 26))
    projection = _load_constant_record("pi_cl", contraction["pi_cl"], (26, 34))
    homotopy = _load_constant_record("S_cl", contraction["S_cl"], (34, 34))
    retained_projector = _load_constant_record(
        "P_retained", contraction["P_retained"], (34, 34)
    )
    clock_projector = _load_constant_record(
        "P_clock", contraction["P_clock"], (34, 34)
    )
    clock_extension = _load_constant_record(
        "clock_extension", unary["clock_extension"], (34, 34)
    )
    if (
        contraction["support_local"] is not True
        or contraction["maximum_differential_order"] != 0
        or contraction["cyclic"] is not True
    ):
        raise ValueError("portable contraction locality or cyclicity was promoted")

    validate_classical_retained_q1(
        retained_q1, retained_schema, retained_layout
    )

    gauge, _ = _load_record("K_spatial", retained_q1["q1_blocks"]["K_spatial"])
    hessian, _ = _load_record("H_retained", retained_q1["q1_blocks"]["H_retained"])
    noether, _ = _load_record(
        "minus_K_spatial_sharp",
        retained_q1["q1_blocks"]["minus_K_spatial_sharp"],
    )
    q_retained = _operator_zero(26, 26)
    _embed(q_retained, gauge, 3, 0)
    _embed(q_retained, hessian, 13, 3)
    _embed(q_retained, noether, 23, 13)
    q_full = _operator_zero(34, 34)
    _embed(q_full, gauge, 5, 0)
    _embed(q_full, hessian, 17, 5)
    _embed(q_full, noether, 29, 17)
    q_full = _matrix_add(q_full, _constant_operator(clock_extension))

    iota_op = _constant_operator(iota)
    projection_op = _constant_operator(projection)
    homotopy_op = _constant_operator(homotopy)
    retained_projector_op = _constant_operator(retained_projector)
    clock_projector_op = _constant_operator(clock_projector)
    if _multiply(q_full, q_full) != _operator_zero(34, 34):
        raise ValueError("portable classical unary q1 is not nilpotent")
    if _multiply(q_full, iota_op) != _multiply(iota_op, q_retained):
        raise ValueError("portable iota_cl is not a chain map")
    if _multiply(projection_op, q_full) != _multiply(q_retained, projection_op):
        raise ValueError("portable pi_cl is not a chain map")
    if _multiply(projection_op, iota_op) != _identity_operator(26):
        raise ValueError("portable pi_cl iota_cl is not the identity")
    if _multiply(iota_op, projection_op) != retained_projector_op:
        raise ValueError("portable retained projector is inconsistent")
    contraction_boundary = _matrix_add(
        _multiply(q_full, homotopy_op), _multiply(homotopy_op, q_full)
    )
    if contraction_boundary != clock_projector_op:
        raise ValueError("portable all-row contraction identity failed")
    if _matrix_add(retained_projector_op, clock_projector_op) != _identity_operator(34):
        raise ValueError("portable complementary projectors do not sum to identity")
    if _multiply(homotopy_op, homotopy_op) != _operator_zero(34, 34):
        raise ValueError("portable S_cl is not square zero")
    if _multiply(projection_op, homotopy_op) != _operator_zero(26, 34):
        raise ValueError("portable pi_cl S_cl side condition failed")
    if _multiply(homotopy_op, iota_op) != _operator_zero(34, 26):
        raise ValueError("portable S_cl iota_cl side condition failed")

    pairing = sp.zeros(34)
    pairing[0:5, 29:34] = sp.eye(5)
    pairing[29:34, 0:5] = -sp.eye(5)
    pairing[5:17, 17:29] = sp.eye(12)
    pairing[17:29, 5:17] = -sp.eye(12)
    residual_pairing = iota.T * pairing * iota
    if pairing.rank() != 34 or residual_pairing.rank() != 26:
        raise ValueError("portable BV pairing or retained pairing is degenerate")
    if homotopy.T * pairing + pairing * homotopy != sp.zeros(34):
        raise ValueError("portable S_cl is not cyclic")
    if residual_pairing * projection != iota.T * pairing:
        raise ValueError("portable projection is not pairing-compatible")
    pairing_op = _constant_operator(pairing)
    q_cyclicity = _matrix_add(
        _multiply(_adjoint_transpose(q_full), pairing_op),
        _multiply(pairing_op, q_full),
    )
    if q_cyclicity != _operator_zero(34, 34):
        raise ValueError("portable full classical unary q1 is not cyclic")

    return {
        "map_hashes": {
            name: contraction[name]["sha256"]
            for name in ("iota_cl", "pi_cl", "S_cl", "P_retained", "P_clock")
        },
        "clock_extension_sha256": unary["clock_extension"]["sha256"],
        "full_pairing_rank": 34,
        "retained_pairing_rank": 26,
    }


@lru_cache(maxsize=1)
def _build_import_cached() -> dict[str, Any]:
    payload = _git_json(CERTIFICATE_RELATIVE)
    schema = _git_json(SCHEMA_RELATIVE)
    retained_q1 = _git_json(Q1_RELATIVE)
    retained_schema = _git_json(Q1_SCHEMA_RELATIVE)
    retained_layout = _git_json(LAYOUT_RELATIVE)
    clock_sdr = _git_json(CLOCK_RELATIVE)
    summary = validate_portable_contraction(
        payload, schema, retained_q1, retained_schema, retained_layout, clock_sdr
    )
    sources = {
        "portable_certificate": _artifact(CERTIFICATE_RELATIVE),
        "portable_schema": _artifact(SCHEMA_RELATIVE),
        "classical_producer": _artifact(PRODUCER_RELATIVE),
        "classical_independent_verifier": _artifact(INDEPENDENT_VERIFIER_RELATIVE),
        "classical_test": _artifact(TEST_RELATIVE),
        "classical_report": _artifact(REPORT_RELATIVE),
        "retained_q1_dependency": _artifact(Q1_RELATIVE),
        "clock_sdr_dependency": _artifact(CLOCK_RELATIVE),
        "retained_layout_dependency": _artifact(LAYOUT_RELATIVE),
    }
    return {
        "schema": SCHEMA_ID,
        "result_id": "BERGER_MINIMAL_34_CONTRACTION_IMPORT",
        "result_state": "COMPLETE_34_ROW_MINIMAL_UNARY_CONTRACTION_IMPORTED_ND2_NONLINEAR_INPUT_BLOCKED",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "classical_result": {
            "result_id": payload["result_id"],
            "claim_status": payload["claim_status"],
            "export_commit": EXPORT_COMMIT,
            "portable_commit": PORTABLE_COMMIT,
            "certificate_sha256": sources["portable_certificate"]["sha256"],
            "schema_sha256": sources["portable_schema"]["sha256"],
        },
        "coverage": {
            "full_minimal_rows": 34,
            "retained_minimal_rows": 26,
            "contracted_clock_rows": 8,
            "complete_minimal_classical_contraction": True,
            "nonminimal_rows_complete": False,
        },
        "maps": {
            "coefficient_domain": "Q embedded in Q[alpha_B,u,v] tensor U(e_Berger)",
            "maximum_differential_order": 0,
            "support_local": True,
            "cyclic": True,
            **summary,
        },
        "independent_checks": {
            "strict_portable_schema_subset": True,
            "dependency_hashes": True,
            "authoritative_34_row_layout": True,
            "exact_order_zero_map_records": True,
            "retained_q1_independently_reverified": True,
            "classical_unary_q1_squared_zero": True,
            "full_classical_unary_q1_cyclic": True,
            "iota_cl_chain_map": True,
            "pi_cl_chain_map": True,
            "pi_cl_iota_cl_identity": True,
            "all_row_contraction_identity": True,
            "complementary_chain_projectors": True,
            "contraction_side_conditions": True,
            "homotopy_cyclic": True,
            "full_pairing_nondegenerate": True,
            "retained_pairing_nondegenerate": True,
            "projection_pairing_compatible": True,
            "retained_complex_cohomology_preserved_by_SDR": True,
        },
        "nd2_gate": {
            "classical_contraction_artifact_satisfied": True,
            "support_local_q1_q2_D": "NOT_AVAILABLE",
            "D_equivariance": "NOT_COMPUTED",
            "admissibility_policy": "NOT_AVAILABLE",
            "compatible_cartan_coefficient_domain": "NOT_AVAILABLE",
            "physical_execution_authorized": False,
            "next_gate": "SUPPORT_LOCAL_Q2_D_ADMISSIBILITY_AND_COMPATIBLE_CARTAN_ASSEMBLY",
        },
        "classical_freeze_gate": {
            "status": "FAIL_CLOSED",
            "reason": "minimal unary contraction only; nonlinear, D-equivariant, nonminimal, and admissibility inputs remain open",
        },
        "provenance": {
            "classical_sources": sources,
            "classical_sources_sha256": _canonical_hash(sources),
        },
        "claim_boundary": (
            "The exact support-local cyclic contraction of the complete 34-row "
            "minimal Berger unary complex onto its retained 26-row complex is "
            "independently imported. This satisfies the standalone ND2 classical-"
            "contraction artifact only. It supplies no q2, local D action or "
            "equivariance, nonminimal completion, admissibility policy, causal or "
            "Hadamard structure, physical Cartan assembly, or quantum result."
        ),
    }


def build_import() -> dict[str, Any]:
    return deepcopy(_build_import_cached())
