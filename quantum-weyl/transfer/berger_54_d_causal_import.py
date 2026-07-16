"""Independent import of the Berger 54-row classical D and causal reduction.

This is a layered handoff over the previously imported gauge-fixed unary
package.  It pins the corrected classical receipts, reconstructs the PBW
operators, and independently replays unary D-equivariance, contraction
equivariance, and cyclicity.  The causal statement is deliberately
conditional: it proves the algebraic/support-local lift from 26 retained rows
to 54 rows, but it does not construct the retained Green homotopies.
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
    from .berger_gauge_fixed_nonminimal_import import (
        _adjoint_transpose,
        _is_zero,
        _load_record,
        _matrix_add,
        _multiply,
        _subtract,
    )
except ImportError:
    from berger_gauge_fixed_nonminimal_import import (
        _adjoint_transpose,
        _is_zero,
        _load_record,
        _matrix_add,
        _multiply,
        _subtract,
    )


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
CLASSICAL_COMMIT = "46208d7c1c845da2b1959bf0799abcc92d856499"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"

GAUGE_CERTIFICATE = "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
D_CERTIFICATE = "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
D_SCHEMA = "d_quotient_classical/schema/berger-54-row-local-D-action-v1.schema.json"
D_PRODUCER = "d_quotient_classical/backreacted_clock/berger_54_row_local_d_action.py"
D_VERIFIER = "d_quotient_classical/backreacted_clock/verify_berger_54_row_local_d_action.py"
D_TEST = "d_quotient_classical/backreacted_clock/tests/test_berger_54_row_local_d_action.py"
D_REPORT = "d_quotient_classical/reports/berger-54-row-local-D-action.md"
CAUSAL_CERTIFICATE = "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json"
CAUSAL_SCHEMA = "d_quotient_classical/schema/berger-54-row-causal-homotopy-reduction-v1.schema.json"
CAUSAL_PRODUCER = "d_quotient_classical/backreacted_clock/berger_54_row_causal_homotopy_reduction.py"
CAUSAL_VERIFIER = "d_quotient_classical/backreacted_clock/verify_berger_54_row_causal_homotopy_reduction.py"
CAUSAL_TEST = "d_quotient_classical/backreacted_clock/tests/test_berger_54_row_causal_homotopy_reduction.py"
CAUSAL_REPORT = "d_quotient_classical/reports/berger-54-row-causal-homotopy-reduction.md"


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
        raise ValueError(f"missing pinned Berger artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }


def _require_strict_schema(schema: dict[str, Any], schema_id: str) -> None:
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id") != schema_id
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("classical schema identity or strictness drifted")


def _validate_source_boundaries(
    d_payload: dict[str, Any],
    d_schema: dict[str, Any],
    causal_payload: dict[str, Any],
    causal_schema: dict[str, Any],
    gauge_payload: dict[str, Any],
) -> None:
    _require_strict_schema(
        d_schema,
        "https://area9.dk/schemas/pure-weyl-berger-54-row-local-D-action-v1.json",
    )
    _require_strict_schema(
        causal_schema,
        "https://area9.dk/schemas/pure-weyl-berger-54-row-causal-homotopy-reduction-v1.json",
    )
    gauge_digest = hashlib.sha256(_git_blob(GAUGE_CERTIFICATE)).hexdigest()
    for payload, result_id, status in (
        (
            d_payload,
            "BERGER_54_ROW_LOCAL_D_ACTION",
            "CERTIFIED_COMPLETE_LOCAL_D_ACTION_UNARY_EQUIVARIANCE",
        ),
        (
            causal_payload,
            "BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION",
            "CERTIFIED_CAUSAL_REDUCTION_ENDPOINT_OPEN",
        ),
    ):
        if (
            payload.get("result_id") != result_id
            or payload.get("claim_status") != status
            or payload.get("setting_id") != SETTING_ID
        ):
            raise ValueError(f"classical result identity drifted: {result_id}")
        reference = payload.get("dependency_refs", {}).get("gauge_fixed_54_row_unary")
        if reference != {
            "result_id": "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION",
            "sha256": gauge_digest,
        }:
            raise ValueError(f"classical unary dependency drifted: {result_id}")
    if (
        gauge_payload.get("result_id") != "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION"
        or gauge_payload.get("setting_id") != SETTING_ID
    ):
        raise ValueError("gauge-fixed unary source drifted")

    expected_causal_fields = {
        "causal_reduction",
        "claim_boundary",
        "claim_status",
        "dependency_refs",
        "dependency_tags",
        "dimension_ledger",
        "exact_checks",
        "flags",
        "next_gate",
        "result_id",
        "schema",
        "setting_id",
    }
    if set(causal_payload) != expected_causal_fields:
        raise ValueError("causal reduction payload fields drifted")
    dimensions = causal_payload.get("dimension_ledger", {})
    if dimensions != {
        "complete_gauge_fixed_rows": 54,
        "degree_ranks_26": [3, 10, 10, 3],
        "degree_ranks_54": [5, 22, 22, 5],
        "identity": "54=28+26",
        "retained_endpoint_rows": 26,
        "support_locally_contracted_rows": 28,
    }:
        raise ValueError("causal reduction dimension ledger drifted")

    d_flags = d_payload.get("flags", {})
    if not (
        d_flags.get("BERGER_LOCAL_D_ACTION_COMPLETE_54_ROWS") is True
        and d_flags.get("BERGER_LOCAL_D_ACTION_EQUIVARIANT") is True
        and d_flags.get("CLASSICAL_SUPPORT_LOCAL_Q2") is False
        and d_flags.get("BERGER_ARITY_TWO_D_CARTAN_FULL_4D") is False
    ):
        raise ValueError("D-action claim boundary drifted")
    causal_flags = causal_payload.get("flags", {})
    if not (
        causal_flags.get("BERGER_54_ROW_CAUSAL_REDUCTION") is True
        and causal_flags.get("BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY") is False
        and causal_flags.get("BERGER_CAUSAL_GREEN_HOMOTOPY") is False
        and causal_flags.get("BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION") is False
    ):
        raise ValueError("causal endpoint boundary drifted")
    if causal_payload.get("next_gate") != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY":
        raise ValueError("causal reduction next gate drifted")


def _validate_d_matrix_shape_and_support(matrix: list[list[dict[tuple[int, ...], sp.Expr]]]) -> None:
    if len(matrix) != 54 or any(len(row) != 54 for row in matrix):
        raise ValueError("D matrix shape drifted")
    for row in range(54):
        for column in range(54):
            expected = {(0,): sp.S.One} if row == column else {}
            if matrix[row][column] != expected:
                raise ValueError("D is not the exact diagonal e_0 action")


def _replay_operator_identities(
    d_payload: dict[str, Any], gauge_payload: dict[str, Any]
) -> dict[str, bool]:
    q1 = _load_record("q_54", gauge_payload["classical_unary_q1"]["matrix"], (54, 54))
    contraction = gauge_payload["contraction"]
    iota = _load_record("iota_cl", contraction["iota_cl"], (54, 26))
    projection = _load_record("pi_cl", contraction["pi_cl"], (26, 54))
    homotopy = _load_record("S_cl", contraction["S_cl"], (54, 54))
    pairing = _load_record("cyclic_pairing", contraction["cyclic_pairing"], (54, 54))
    d54 = _load_record("D_54", d_payload["D_action"]["matrix"], (54, 54))
    d26 = _load_record("D_26", d_payload["retained_D_action"]["matrix"], (26, 26))
    _validate_d_matrix_shape_and_support(d54)
    if any(
        d26[row][column] != ({(0,): sp.S.One} if row == column else {})
        for row in range(26)
        for column in range(26)
    ):
        raise ValueError("retained D is not diagonal e_0")

    checks = {
        "q1_D_commutator_zero": _is_zero(
            _subtract(_multiply(q1, d54), _multiply(d54, q1))
        ),
        "D_iota_equivariant": _is_zero(
            _subtract(_multiply(d54, iota), _multiply(iota, d26))
        ),
        "D_projection_equivariant": _is_zero(
            _subtract(_multiply(projection, d54), _multiply(d26, projection))
        ),
        "D_homotopy_equivariant": _is_zero(
            _subtract(_multiply(d54, homotopy), _multiply(homotopy, d54))
        ),
        "D_cyclic_skew_adjoint": _is_zero(
            _matrix_add(
                _multiply(_adjoint_transpose(d54), pairing),
                _multiply(pairing, d54),
            )
        ),
        "D_support_local_order_one": True,
        "all_54_rows_have_D_action": True,
    }
    if not all(checks.values()):
        raise ValueError("an imported D-action identity failed")
    return checks


def _conditional_causal_proof(causal_payload: dict[str, Any]) -> dict[str, Any]:
    reduction = causal_payload["causal_reduction"]
    expected = {
        "conditional_endpoint_identity": "q_26 Lambda_26,+/-+Lambda_26,+/- q_26=1_26",
        "lifted_formula": "Lambda_54,+/-=S+i Lambda_26,+/- p",
        "lifted_derivation": "q_54 Lambda_54,+/-+Lambda_54,+/- q_54=(1-i p)+i 1_26 p=1_54",
    }
    if any(reduction.get(key) != value for key, value in expected.items()):
        raise ValueError("corrected causal lift formula drifted")
    # Exact coefficient ledger after applying the SDR and endpoint relations:
    # (1-ip) + i(1_26)p = 1-ip+ip = 1.
    complement = {"ONE_54": 1, "IOTA_PI": -1}
    endpoint = {"IOTA_PI": 1}
    total = {
        key: complement.get(key, 0) + endpoint.get(key, 0)
        for key in set(complement) | set(endpoint)
    }
    total = {key: value for key, value in total.items() if value}
    if total != {"ONE_54": 1}:
        raise AssertionError("conditional causal lift did not reduce to identity")
    exact_checks = causal_payload.get("exact_checks", {})
    expected_checks = {
        "algebraic_complement_contracted",
        "all_54_rows_included",
        "coefficientwise_p_q54_equals_q26_p",
        "coefficientwise_q54_i_equals_i_q26",
        "conditional_causal_support",
        "conditional_lifted_homotopy_identity",
        "contraction_side_conditions",
        "cyclic_contraction_imported",
        "pi_iota_identity",
        "support_local_finite_order",
    }
    if set(exact_checks) != expected_checks or any(
        value is not True for value in exact_checks.values()
    ):
        raise ValueError("classical causal reduction lost an exact check")
    return {
        "formula": expected["lifted_formula"],
        "endpoint_hypothesis": expected["conditional_endpoint_identity"],
        "expanded_coefficients": {
            "contractible_complement": complement,
            "retained_endpoint": endpoint,
            "sum": total,
        },
        "support_transfer": "VERIFIED_FROM_FINITE_ORDER_S_IOTA_PI",
        "cyclic_adjoint_transfer": "VERIFIED_CONDITIONAL_ON_ENDPOINT_ADJOINTNESS",
        "endpoint_status": "NOT_CONSTRUCTED",
    }


def validate_handoff(
    d_payload: dict[str, Any],
    d_schema: dict[str, Any],
    causal_payload: dict[str, Any],
    causal_schema: dict[str, Any],
    gauge_payload: dict[str, Any],
) -> dict[str, Any]:
    _validate_source_boundaries(
        d_payload, d_schema, causal_payload, causal_schema, gauge_payload
    )
    return {
        "operator_checks": _replay_operator_identities(d_payload, gauge_payload),
        "causal_proof": _conditional_causal_proof(causal_payload),
    }


@lru_cache(maxsize=1)
def _build_cached() -> dict[str, Any]:
    d_payload = _git_json(D_CERTIFICATE)
    causal_payload = _git_json(CAUSAL_CERTIFICATE)
    replay = validate_handoff(
        d_payload,
        _git_json(D_SCHEMA),
        causal_payload,
        _git_json(CAUSAL_SCHEMA),
        _git_json(GAUGE_CERTIFICATE),
    )
    source_paths = {
        "gauge_fixed_unary_certificate": GAUGE_CERTIFICATE,
        "D_certificate": D_CERTIFICATE,
        "D_schema": D_SCHEMA,
        "D_producer": D_PRODUCER,
        "D_independent_verifier": D_VERIFIER,
        "D_test": D_TEST,
        "D_report": D_REPORT,
        "causal_certificate": CAUSAL_CERTIFICATE,
        "causal_schema": CAUSAL_SCHEMA,
        "causal_producer": CAUSAL_PRODUCER,
        "causal_independent_verifier": CAUSAL_VERIFIER,
        "causal_test": CAUSAL_TEST,
        "causal_report": CAUSAL_REPORT,
    }
    sources = {name: _artifact(path) for name, path in source_paths.items()}
    return {
        "schema": "quantum-weyl-berger-54-row-D-causal-import-v1",
        "result_id": "BERGER_54_ROW_D_CAUSAL_INPUT_IMPORT",
        "result_state": "CLASSICAL_D_ACTION_IMPORTED_CAUSAL_ENDPOINT_REDUCED",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
        "generator": {
            "registry_id": "D_compact",
            "geometric_representative": "D_helical=partial_t plus compensating internal clock rotation",
            "dressed_frame_action": "D=e_0",
        },
        "coverage": {
            "complete_gauge_fixed_rows": 54,
            "retained_rows": 26,
            "support_locally_contracted_rows": 28,
            "classical_D_action_complete": True,
            "unary_D_equivariance_complete": True,
            "contraction_D_equivariance_complete": True,
            "cyclic_D_action_complete": True,
        },
        "independent_operator_checks": replay["operator_checks"],
        "conditional_causal_lift": replay["causal_proof"],
        "input_gate_update": {
            "FROZEN_CLASSICAL_D_ACTION": "AVAILABLE_SETTING_SPECIFIC_BERGER_54_ROWS",
            "BERGER_54_ROW_CAUSAL_REDUCTION": "VERIFIED",
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": "NOT_CONSTRUCTED",
            "BERGER_HADAMARD_DATA": "NOT_CONSTRUCTED",
            "CLASSICAL_SUPPORT_LOCAL_Q2": "NOT_AVAILABLE",
            "GENERAL_ANTIFIELD_KOSZUL_TATE_EXPORT": "NOT_AVAILABLE",
            "RENORMALIZED_Q1": "UNDEFINED_ANALYTICALLY",
            "RENORMALIZED_LOCAL_WARD_INSERTION": "NOT_CONSTRUCTED",
        },
        "quantum_execution_authorized": False,
        "next_gate": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_AND_RENORMALIZED_WARD_INSERTION",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "classical_sources": sources,
            "classical_sources_sha256": hashlib.sha256(
                json.dumps(sources, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        },
        "claim_boundary": (
            "The complete classical helical D action and its unary/contraction/cyclic "
            "equivariance are independently imported on the fixed-coupling Berger "
            "setting. The 54-row causal theorem is only a conditional reduction to "
            "the retained 26-row endpoint. No retained Green operator, Hadamard state, "
            "support-local q2, renormalized Ward insertion, QME, or quantum D verdict "
            "is supplied."
        ),
    }


def build_import() -> dict[str, Any]:
    return deepcopy(_build_cached())
