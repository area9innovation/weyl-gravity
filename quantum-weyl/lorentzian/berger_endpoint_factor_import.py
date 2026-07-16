"""Import and independently replay the certified Berger causal endpoint factors.

The classical certificate proves Green hyperbolicity only for the retained
ghost and identity endpoint blocks.  This consumer pins that result, rebuilds
all four degreewise ``QW+WQ`` blocks from the exported PBW matrices, and
rechecks the exact biwave symbol and the rank-eight-plus-two metric boundary.
It deliberately does not promote the full retained Green homotopy.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp

try:
    from transfer.berger_gauge_fixed_nonminimal_import import (
        _identity,
        _is_zero,
        _load_record,
        _matrix_add,
        _multiply,
    )
    from transfer.berger_retained_q1_import import ALPHA_B, U, V
except ImportError:
    from ..transfer.berger_gauge_fixed_nonminimal_import import (
        _identity,
        _is_zero,
        _load_record,
        _matrix_add,
        _multiply,
    )
    from ..transfer.berger_retained_q1_import import ALPHA_B, U, V


LORENTZIAN_ROOT = Path(__file__).resolve().parent
ROOT = LORENTZIAN_ROOT.parents[1]
CLASSICAL_COMMIT = "b6caaddde5bce3480ef4d91e6b0c2824b98050dd"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"

Q1_CERTIFICATE = "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CERTIFICATE = "d_quotient_classical/certificates/BERGER_CAUSAL_WITNESS_PREFLIGHT.json"
SCHEMA = "d_quotient_classical/schema/berger-causal-witness-preflight-v1.schema.json"
PRODUCER = "d_quotient_classical/backreacted_clock/berger_causal_witness_preflight.py"
VERIFIER = "d_quotient_classical/backreacted_clock/verify_berger_causal_witness_preflight.py"
TEST = "d_quotient_classical/backreacted_clock/tests/test_berger_causal_witness_preflight.py"
REPORT = "d_quotient_classical/reports/berger-causal-witness-preflight.md"
SOURCE_ARTIFACTS = (Q1_CERTIFICATE, CERTIFICATE, SCHEMA, PRODUCER, VERIFIER, TEST, REPORT)

PAIRS = tuple((first, second) for first in range(4) for second in range(first, 4))
ETA = sp.diag(-1, 1, 1, 1)


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
        raise ValueError(f"missing pinned Berger endpoint artifact: {relative}")
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


def _symbol(matrix: list[list[dict[tuple[int, ...], sp.Expr]]], order: int) -> sp.Matrix:
    momenta = sp.symbols("p0:4")
    return sp.Matrix(
        len(matrix), len(matrix[0]),
        lambda row, column: sp.factor(sum(
            coefficient * sp.prod(momenta[axis] for axis in word)
            for word, coefficient in matrix[row][column].items()
            if len(word) == order
        )),
    )


def _validate_source(payload: dict[str, Any], schema: dict[str, Any], q1: dict[str, Any]) -> None:
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-causal-witness-preflight-v1.schema.json"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("classical endpoint schema identity or strictness drifted")
    expected_fields = {
        "schema", "result_id", "setting_id", "claim_status", "dependency_tags",
        "q1_ref", "companion_definition", "witness_blocks", "degreewise_P_blocks",
        "endpoint_factorization", "metric_mixed_order_boundary", "exact_checks",
        "flags", "next_gate", "claim_boundary",
    }
    if set(payload) != expected_fields:
        raise ValueError("classical endpoint payload fields drifted")
    if (
        payload.get("schema") != "pure-weyl-berger-causal-witness-preflight-v1"
        or payload.get("result_id") != "BERGER_CAUSAL_WITNESS_PREFLIGHT"
        or payload.get("setting_id") != SETTING_ID
        or payload.get("claim_status") != "CERTIFIED_ENDPOINT_FACTORS_METRIC_OPEN"
        or payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise ValueError("classical endpoint result identity drifted")
    if q1.get("result_id") != "BERGER_RETAINED_MINIMAL_OPERATOR" or q1.get("setting_id") != SETTING_ID:
        raise ValueError("retained q1 identity drifted")
    if payload.get("q1_ref") != {
        "result_id": "BERGER_RETAINED_MINIMAL_OPERATOR",
        "sha256": hashlib.sha256(_git_blob(Q1_CERTIFICATE)).hexdigest(),
    }:
        raise ValueError("retained q1 dependency drifted")

    endpoint = payload.get("endpoint_factorization", {})
    if endpoint != {
        "advanced_retarded_recursive_inverse_exists": True,
        "factor_1_principal": "zeta^2 I_3",
        "factor_2_principal": "zeta^2 I_3",
        "ghost": "alpha_B Box_1 o (F_spatial K_spatial)",
        "identity": "formal adjoint of the ghost factorization",
    }:
        raise ValueError("endpoint factor theorem drifted")
    boundary = payload.get("metric_mixed_order_boundary", {})
    if (
        boundary.get("fourth_order_rank") != 8
        or boundary.get("fourth_order_kernel_dimension") != 2
        or boundary.get("green_realization_constructed") is not False
        or boundary.get("kernel_generators") != [
            "K_temporal(zeta)",
            "zeta^2 g + K_spatial(zeta)(zeta_spatial)",
        ]
    ):
        raise ValueError("metric mixed-order boundary drifted")
    flags = payload.get("flags", {})
    if not (
        flags.get("BERGER_GHOST_ENDPOINT_GREEN_HYPERBOLIC") is True
        and flags.get("BERGER_IDENTITY_ENDPOINT_GREEN_HYPERBOLIC") is True
        and flags.get("BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION") is False
        and flags.get("BERGER_CAUSAL_GREEN_HOMOTOPY") is False
        and flags.get("BERGER_NONMINIMAL_COMPLETION") is False
        and flags.get("BERGER_ARITY_TWO_D_CARTAN") is False
        and payload.get("next_gate") == "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION"
    ):
        raise ValueError("classical causal claim boundary drifted")


def _replay(payload: dict[str, Any], q1: dict[str, Any]) -> dict[str, bool]:
    qblocks = q1["q1_blocks"]
    gauge = _load_record("K_spatial", qblocks["K_spatial"], (10, 3))
    hessian = _load_record("H_retained", qblocks["H_retained"], (10, 10))
    noether = _load_record("minus_K_spatial_sharp", qblocks["minus_K_spatial_sharp"], (3, 10))
    witness = payload["witness_blocks"]
    companion = _load_record("M_to_G", witness["M_to_G"], (3, 10))
    middle = _load_record("E_to_M", witness["E_to_M"], (10, 10))
    companion_adjoint = _load_record("I_to_E", witness["I_to_E"], (10, 3))
    blocks = payload["degreewise_P_blocks"]
    ghost = _load_record("ghost", blocks["ghost"], (3, 3))
    metric = _load_record("metric", blocks["metric"], (10, 10))
    metric_antifield = _load_record("metric_antifield", blocks["metric_antifield"], (10, 10))
    identity = _load_record("identity", blocks["identity"], (3, 3))

    expected_ghost = _multiply(companion, gauge)
    expected_metric = _matrix_add(hessian, _multiply(gauge, companion))
    expected_metric_antifield = _matrix_add(hessian, _multiply(companion_adjoint, noether))
    expected_identity = _multiply(noether, companion_adjoint)

    momenta = sp.symbols("p0:4")
    zeta2 = -momenta[0] ** 2 + sum(momenta[index] ** 2 for index in range(1, 4))
    ghost4 = _symbol(ghost, 4)
    metric4 = _symbol(metric, 4)
    k_spatial = _symbol(gauge, 1)
    k_temporal = sp.zeros(10, 1)
    metric_trace = sp.zeros(10, 1)
    for row, (first, second) in enumerate(PAIRS):
        k_temporal[row, 0] = (
            (momenta[first] if second == 0 else 0)
            + (momenta[second] if first == 0 else 0)
        )
        metric_trace[row, 0] = ETA[first, second]
    weyl_carrier = zeta2 * metric_trace + k_spatial * sp.Matrix(momenta[1:4])
    carriers = k_temporal.row_join(weyl_carrier)
    fixture = {
        momenta[0]: 2, momenta[1]: 1, momenta[2]: 3, momenta[3]: 4,
        U: 1, V: 5, ALPHA_B: 7,
    }

    checks = {
        "middle_witness_identity": middle == _identity(10),
        "ghost_block_reconstructed": _is_zero(_matrix_add(ghost, [[
            {word: -coefficient for word, coefficient in entry.items()}
            for entry in row
        ] for row in expected_ghost])),
        "metric_block_reconstructed": metric == expected_metric,
        "metric_antifield_block_reconstructed": metric_antifield == expected_metric_antifield,
        "identity_block_reconstructed": identity == expected_identity,
        "ghost_biwave_principal_symbol": sp.simplify(
            ghost4 - ALPHA_B * zeta2**2 * sp.eye(3)
        ) == sp.zeros(3),
        "metric_kernel_carriers_exact": sp.simplify(metric4 * carriers) == sp.zeros(10, 2),
        "metric_rank_eight_at_exact_fixture": metric4.subs(fixture).rank() == 8,
        "metric_kernel_rank_two_at_exact_fixture": carriers.subs(fixture).rank() == 2,
    }
    checks["generic_metric_rank_eight"] = (
        checks["metric_kernel_carriers_exact"]
        and checks["metric_rank_eight_at_exact_fixture"]
        and checks["metric_kernel_rank_two_at_exact_fixture"]
    )
    if not all(checks.values()):
        failures = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"independent endpoint replay failed: {failures}")
    return checks


def validate_import(
    payload: dict[str, Any], schema: dict[str, Any], q1: dict[str, Any]
) -> dict[str, Any]:
    _validate_source(payload, schema, q1)
    checks = _replay(payload, q1)
    return {
        "schema": "quantum-weyl-berger-endpoint-factor-import-v1",
        "result_id": "BERGER_ENDPOINT_FACTOR_INPUT_IMPORT",
        "result_state": "PARTIAL_LORENTZIAN_ENDPOINT_FACTORS_IMPORTED_METRIC_OPEN",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
        "coverage": {
            "retained_rows": 26,
            "ghost_rows": 3,
            "metric_rows": 10,
            "metric_antifield_rows": 10,
            "identity_rows": 3,
        },
        "independent_exact_checks": checks,
        "causal_endpoint_status": {
            "ghost_endpoint": "GREEN_HYPERBOLIC_BY_TWO_NORMALLY_HYPERBOLIC_FACTORS",
            "identity_endpoint": "GREEN_HYPERBOLIC_BY_FORMAL_ADJOINT_FACTORIZATION",
            "metric_endpoint": "NOT_CONSTRUCTED_GENERIC_RANK_EIGHT_PLUS_TWO_MIXED_ORDER",
            "metric_antifield_endpoint": "NOT_CONSTRUCTED_GENERIC_RANK_EIGHT_PLUS_TWO_MIXED_ORDER",
            "retained_26_row_chain_homotopy": "NOT_CONSTRUCTED",
            "gauge_fixed_54_row_chain_homotopy": "NOT_CONSTRUCTED",
            "hadamard_data": "NOT_CONSTRUCTED",
        },
        "metric_boundary": {
            "generic_fourth_order_rank": 8,
            "polynomial_kernel_dimension": 2,
            "rank_certificate": (
                "two exact polynomial null carriers give rank at most eight; "
                "an exact nonzero rank-eight fixture gives generic rank at least eight"
            ),
            "characteristic_rank_stratification": "NOT_CLASSIFIED",
            "rank_drop_on_characteristic_covectors_excluded": False,
            "kernel_field_content": ["temporal_diffeomorphism_clock", "weyl_constraint"],
            "negative_physical_direction_introduced": False,
            "interpretation": "principal clock/constraint carriers, not residual particle states",
        },
        "green_endpoint_contract_update": "PARTIAL_INPUT_ONLY_FULL_26_ROW_EXPORT_STILL_BLOCKED",
        "quantum_execution_authorized": False,
        "next_gate": "BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "artifacts": [_artifact(path) for path in SOURCE_ARTIFACTS],
        },
        "claim_boundary": (
            "Imports and independently replays the certified ghost and identity endpoint "
            "factor theorem in the compact positive Berger reduced mode. It does not "
            "construct the metric or metric-antifield Green operators, the retained "
            "26-row or lifted 54-row causal chain homotopy, Hadamard data, renormalized "
            "time-ordered products, or a full Lorentzian quantum theory."
        ),
    }


def build_import() -> dict[str, Any]:
    return validate_import(_git_json(CERTIFICATE), _git_json(SCHEMA), _git_json(Q1_CERTIFICATE))
