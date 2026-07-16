"""Pinned import of the complete support-local Berger 54-row D action."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from .berger_gauge_fixed_nonminimal_import import (
        _adjoint_transpose,
        _git_prefix,
        _is_zero,
        _load_record,
        _matrix_add,
        _multiply,
        _subtract,
    )
    from .berger_retained_q1_import import _canonical_hash
except ImportError:
    from berger_gauge_fixed_nonminimal_import import (
        _adjoint_transpose,
        _git_prefix,
        _is_zero,
        _load_record,
        _matrix_add,
        _multiply,
        _subtract,
    )
    from berger_retained_q1_import import _canonical_hash


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
CLASSICAL_COMMIT = "90bd7d3f3d2b13573ef527400ecd731096babbe3"
CERTIFICATE_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
)
SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/berger-54-row-local-D-action-v1.schema.json"
)
PRODUCER_RELATIVE = (
    "d_quotient_classical/backreacted_clock/berger_54_row_local_d_action.py"
)
VERIFIER_RELATIVE = (
    "d_quotient_classical/backreacted_clock/verify_berger_54_row_local_d_action.py"
)
TEST_RELATIVE = (
    "d_quotient_classical/backreacted_clock/tests/test_berger_54_row_local_d_action.py"
)
REPORT_RELATIVE = "d_quotient_classical/reports/berger-54-row-local-D-action.md"
GAUGE_FIXED_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
)
SCHEMA_ID = "quantum-weyl-berger-54-row-local-d-import-v1"


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned Berger D-action artifact {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned Berger D-action JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }


def validate_import(
    payload: dict[str, Any],
    schema: dict[str, Any],
    gauge_fixed: dict[str, Any],
) -> dict[str, str]:
    """Recompute the PBW equivariance, contraction, and cyclic identities."""

    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-54-row-local-D-action-v1.json"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("classical 54-row D-action schema identity drifted")
    if set(payload) != {
        "schema",
        "result_id",
        "setting_id",
        "claim_status",
        "dependency_tags",
        "dependency_refs",
        "geometric_definition",
        "row_layout",
        "D_action",
        "retained_D_action",
        "exact_checks",
        "flags",
        "next_gate",
        "claim_boundary",
    }:
        raise ValueError("classical 54-row D-action payload fields drifted")
    if (
        payload.get("schema") != "pure-weyl-berger-54-row-local-D-action-v1"
        or payload.get("result_id") != "BERGER_54_ROW_LOCAL_D_ACTION"
        or payload.get("claim_status")
        != "CERTIFIED_COMPLETE_LOCAL_D_ACTION_UNARY_EQUIVARIANCE"
        or payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
    ):
        raise ValueError("classical 54-row D-action identity drifted")

    dependency = payload.get("dependency_refs", {}).get(
        "gauge_fixed_54_row_unary", {}
    )
    expected_gauge_hash = hashlib.sha256(_git_blob(GAUGE_FIXED_RELATIVE)).hexdigest()
    if (
        dependency.get("result_id")
        != "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION"
        or dependency.get("sha256") != expected_gauge_hash
    ):
        raise ValueError("classical 54-row D-action dependency drifted")
    if gauge_fixed.get("result_id") != dependency["result_id"]:
        raise ValueError("pinned gauge-fixed dependency identity drifted")

    layout = payload["row_layout"]
    gauge_rows = gauge_fixed["row_layout"]["component_rows"]
    if (
        layout.get("total_rows") != 54
        or layout.get("degree_ranks") != [5, 22, 22, 5]
        or layout.get("row_ids") != [row["row_id"] for row in gauge_rows]
        or layout.get("all_rows_have_D_action") is not True
    ):
        raise ValueError("classical 54-row D-action row ledger drifted")
    geometry = payload["geometric_definition"]
    if (
        geometry.get("maximum_differential_order") != 1
        or geometry.get("support_local") is not True
        or geometry.get("background_stationary") is not True
        or geometry.get("invariant_frame_commutators") != "[e_0,e_i]=0"
    ):
        raise ValueError("classical 54-row D-action geometry drifted")

    d54 = _load_record("D_action", payload["D_action"]["matrix"], (54, 54))
    d26 = _load_record(
        "retained_D_action", payload["retained_D_action"]["matrix"], (26, 26)
    )
    q1 = _load_record(
        "classical_unary_q1",
        gauge_fixed["classical_unary_q1"]["matrix"],
        (54, 54),
    )
    contraction = gauge_fixed["contraction"]
    iota = _load_record("iota_cl", contraction["iota_cl"], (54, 26))
    projection = _load_record("pi_cl", contraction["pi_cl"], (26, 54))
    homotopy = _load_record("S_cl", contraction["S_cl"], (54, 54))
    pairing = _load_record("cyclic_pairing", contraction["cyclic_pairing"], (54, 54))

    identities = (
        (_subtract(_multiply(q1, d54), _multiply(d54, q1)), "[q1,D]"),
        (_subtract(_multiply(d54, iota), _multiply(iota, d26)), "D iota"),
        (
            _subtract(_multiply(projection, d54), _multiply(d26, projection)),
            "pi D",
        ),
        (
            _subtract(_multiply(d54, homotopy), _multiply(homotopy, d54)),
            "[D,S]",
        ),
        (_matrix_add(_adjoint_transpose(d54), d54), "D formal adjoint"),
        (
            _matrix_add(
                _multiply(_adjoint_transpose(d54), pairing),
                _multiply(pairing, d54),
            ),
            "D cyclicity",
        ),
    )
    for defect, name in identities:
        if not _is_zero(defect):
            raise ValueError(f"classical 54-row D-action identity failed: {name}")

    checks = payload["exact_checks"]
    if set(checks) != {
        "all_54_rows_included",
        "D_support_local_order_one",
        "q1_D_commutator_zero_coefficientwise",
        "D_iota_equivariant",
        "D_projection_equivariant",
        "D_homotopy_equivariant",
        "D_formally_skew_adjoint",
        "D_preserves_cyclic_pairing",
    } or any(value is not True for value in checks.values()):
        raise ValueError("classical 54-row D-action exact checks drifted")
    flags = payload["flags"]
    for name in (
        "BERGER_LOCAL_D_ACTION_COMPLETE_54_ROWS",
        "BERGER_LOCAL_D_ACTION_EQUIVARIANT",
    ):
        if flags.get(name) is not True:
            raise ValueError("classical 54-row D-action positive claim dropped")
    for name in (
        "CLASSICAL_SUPPORT_LOCAL_Q2",
        "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT",
        "BERGER_ARITY_TWO_D_CARTAN_FULL_4D",
    ):
        if flags.get(name) is not False:
            raise ValueError("classical 54-row D-action claim boundary drifted")
    if payload.get("next_gate") != "CLASSICAL_SUPPORT_LOCAL_Q2":
        raise ValueError("classical 54-row D-action next gate drifted")

    return {
        "D54_sha256": payload["D_action"]["matrix"]["sha256"],
        "D26_sha256": payload["retained_D_action"]["matrix"]["sha256"],
        "gauge_fixed_54_row_sha256": expected_gauge_hash,
        "q1_sha256": gauge_fixed["classical_unary_q1"]["matrix"]["sha256"],
        "iota_sha256": contraction["iota_cl"]["sha256"],
        "pi_sha256": contraction["pi_cl"]["sha256"],
        "S_sha256": contraction["S_cl"]["sha256"],
        "pairing_sha256": contraction["cyclic_pairing"]["sha256"],
    }


@lru_cache(maxsize=1)
def _build_cached() -> dict[str, Any]:
    payload = _git_json(CERTIFICATE_RELATIVE)
    schema = _git_json(SCHEMA_RELATIVE)
    gauge_fixed = _git_json(GAUGE_FIXED_RELATIVE)
    hashes = validate_import(payload, schema, gauge_fixed)
    sources = {
        name: _artifact(relative)
        for name, relative in (
            ("classical_certificate", CERTIFICATE_RELATIVE),
            ("classical_schema", SCHEMA_RELATIVE),
            ("classical_producer", PRODUCER_RELATIVE),
            ("classical_independent_verifier", VERIFIER_RELATIVE),
            ("classical_test", TEST_RELATIVE),
            ("classical_report", REPORT_RELATIVE),
            ("gauge_fixed_54_row_dependency", GAUGE_FIXED_RELATIVE),
        )
    }
    return {
        "schema": SCHEMA_ID,
        "result_id": "BERGER_54_ROW_LOCAL_D_ACTION_IMPORT",
        "result_state": "COMPLETE_54_ROW_LOCAL_D_ACTION_IMPORTED_SUPPORT_LOCAL_Q2_BLOCKED",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_id": payload["setting_id"],
        "classical_result": {
            "result_id": payload["result_id"],
            "claim_status": payload["claim_status"],
            "commit": CLASSICAL_COMMIT,
            "certificate_sha256": sources["classical_certificate"]["sha256"],
        },
        "coverage": {
            "total_rows": 54,
            "retained_rows": 26,
            "support_local_order": 1,
            "local_D_action_complete": True,
            "unary_equivariance_complete": True,
            "contraction_equivariance_complete": True,
            "cyclicity_complete": True,
            "support_local_q2_available": False,
        },
        "operator_hashes": hashes,
        "independent_checks": {
            "strict_classical_schema_identity": True,
            "classical_dependency_hash": True,
            "all_54_rows_match_gauge_fixed_layout": True,
            "PBW_record_hashes": True,
            "q1_D_commutator_zero": True,
            "D_iota_equivariant": True,
            "D_projection_equivariant": True,
            "D_homotopy_equivariant": True,
            "D_formally_skew_adjoint": True,
            "D_preserves_cyclic_pairing": True,
            "claim_boundary_fail_closed": True,
        },
        "generality_assessment": {
            "target": "G2_FULL_SUPPORT_LOCAL_LOW_ARITY_COMPLEX_ON_ONE_BACKGROUND",
            "achieved": "G2_PREREQUISITE_COMPLETE_54_ROW_LOCAL_D_ACTION",
            "promotion_to_G2_authorized": False,
            "missing_for_promotion": "complete support-local four-dimensional q2 and arity-two identities",
        },
        "nd2_gate": {
            "unary_nonminimal_prerequisite_satisfied": True,
            "local_D_action_and_unary_equivariance": "AVAILABLE",
            "support_local_classical_binary_q2": "NOT_AVAILABLE",
            "arity_two_D_derivation_test": "INPUT_BLOCKED",
            "arity_two_Cartan_source": "INPUT_BLOCKED",
            "physical_execution_authorized": False,
            "next_gate": "IMPORT_COMPLETE_SUPPORT_LOCAL_Q2",
        },
        "provenance": {
            "classical_sources": sources,
            "classical_sources_sha256": _canonical_hash(sources),
        },
        "claim_boundary": "This pinned LOCAL-ALGEBRAIC consumer independently imports the complete support-local order-one helical D action on all 54 gauge-fixed Berger BV rows and verifies unary, contraction, and cyclic equivariance in the exact PBW algebra. It is only a G2 prerequisite: the full four-dimensional support-local q2, its arity-two D-derivation identity, the interacting Cartan source, causal propagation, and quantum corrections remain unavailable.",
    }


def build_import() -> dict[str, Any]:
    return deepcopy(_build_cached())
