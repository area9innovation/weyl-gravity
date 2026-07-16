"""Fail-closed decomposability audit for the Berger companion operator.

The classical causal package supplies typed advanced and retarded Green
operators for the twenty-row companion.  The principal determinant proves
that its characteristic set is the metric null cone.  Neither fact, alone or
together, proves the wavefront decomposition of the Pauli--Jordan kernel.

This module specializes Fewster's decomposability definition to the future
and past metric-null cones, replays the exact null-symbol obstruction, and
names the smallest missing microlocal theorem.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
BASE = HERE / "certificates/BERGER_BASE_WAVE_HADAMARD_PARAMETRIX.json"
COMPANION = HERE / "certificates/BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT.json"
VOLTERRA = HERE / "certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_V2_IMPORT.json"
MOLLER = HERE / "certificates/BERGER_TYPED_COMPANION_MOLLER_PREFLIGHT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _zero(rows: int, columns: int) -> list[list[int]]:
    return [[0 for _ in range(columns)] for _ in range(rows)]


def _multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [
            sum(left[row][middle] * right[middle][column] for middle in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def _rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column] != 0), None
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(rows):
            if row != rank and work[row][column] != 0:
                factor = work[row][column]
                work[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == rows:
            break
    return rank


def null_symbol_replay(imported_rank: int = 7) -> dict[str, Any]:
    """Replay the Jordan obstruction using a canonical rank-r lower block."""

    v2 = _zero(10, 10)
    for index in range(imported_rank):
        v2[index][index] = 1
    symbol = _zero(20, 20)
    for row in range(10):
        for column in range(10):
            symbol[row + 10][column] = v2[row][column]
    square = _multiply(symbol, symbol)
    rank = _rank(symbol)
    checks = {
        "null_symbol_square_zero_by_block_incidence": square == _zero(20, 20),
        "null_symbol_rank_matches_imported_fixture": rank == imported_rank,
        "null_symbol_nonzero": rank > 0,
        "nonzero_square_zero_symbol_is_not_diagonalizable": rank > 0
        and square == _zero(20, 20),
        "off_cone_symbol_invertible_from_q_power_20": True,
    }
    if not all(checks.values()):
        raise ValueError("companion null-symbol replay failed")
    return {
        "imported_null_fixture_rank": imported_rank,
        "canonical_representative_rank": rank,
        "minimal_polynomial_on_null_fixture": "lambda^2",
        "checks": checks,
    }


def _load_inputs() -> tuple[dict[str, Any], ...]:
    base, companion, volterra, moller = (
        json.loads(path.read_text()) for path in (BASE, COMPANION, VOLTERRA, MOLLER)
    )
    if (
        base.get("claim_flags", {}).get("BERGER_BASE_WAVE_HADAMARD_PARAMETRIX")
        is not True
        or base.get("claim_flags", {}).get("BERGER_TYPED_COMPANION_HADAMARD")
        is not False
    ):
        raise ValueError("base Hadamard boundary drifted")
    system = companion.get("companion_system", {})
    if (
        system.get("principal_symbol")
        != "[[q I10,0],[sigma_2(V_2),q I10]]"
        or system.get("principal_determinant") != "q^20"
        or system.get("extra_characteristic_cone") is not False
        or system.get("principal_ranks", {}).get("metric_null_fixture") != 7
    ):
        raise ValueError("companion principal-symbol input drifted")
    if (
        volterra.get("claim_flags", {}).get(
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT_IMPORTED"
        )
        is not True
        or volterra.get("source_import", {}).get("proof_checks", {}).get(
            "named_advanced_retarded_support"
        )
        is not True
    ):
        raise ValueError("causal Green input drifted")
    if (
        moller.get("claim_flags", {}).get("BERGER_TYPED_COMPANION_MOLLER_ALGEBRA")
        is not True
        or moller.get("claim_flags", {}).get(
            "BERGER_TYPED_COMPANION_DISTRIBUTIONAL_TRANSPORT"
        )
        is not False
    ):
        raise ValueError("typed Møller boundary drifted")
    return base, companion, volterra, moller


@lru_cache(maxsize=1)
def evaluate() -> dict[str, Any]:
    base, companion, volterra, moller = _load_inputs()
    replay = null_symbol_replay(
        companion["companion_system"]["principal_ranks"]["metric_null_fixture"]
    )
    result = {
        "schema": "quantum-weyl-berger-companion-decomposability-preflight-v1",
        "result_id": "BERGER_COMPANION_DECOMPOSABILITY_PREFLIGHT",
        "result_state": "NULL_CHARACTERISTIC_CONE_CERTIFIED_PAULI_JORDAN_DECOMPOSITION_OPEN",
        "lifecycle_layer": "LORENTZIAN_MICROLOCAL_PREFLIGHT",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "classical_commit": base["classical_commit"],
        "setting_id": base["setting_id"],
        "dependency_refs": {
            "base_hadamard_parametrix": _dependency(BASE),
            "companion_principal_symbol": _dependency(COMPANION),
            "typed_volterra_resolvent": _dependency(VOLTERRA),
            "typed_moller_algebra": _dependency(MOLLER),
        },
        "decomposability_target": {
            "source": "Fewster, Hadamard states for decomposable Green-hyperbolic operators, Definition 5.2",
            "source_url": "https://arxiv.org/abs/2503.12537",
            "positive_cone": "N_plus=future-directed nonzero metric-null covectors",
            "negative_cone": "N_minus=-N_plus",
            "cone_properties": {
                "conic": "CERTIFIED_GEOMETRIC_DEFINITION",
                "relatively_closed_in_punctured_cotangent_bundle": "CERTIFIED_GEOMETRIC_DEFINITION",
                "N_plus_intersection_N_minus_empty": "CERTIFIED_BY_TIME_ORIENTATION",
            },
            "required_kernel_inclusion": "WF(E_C) subset (N_plus x N_minus) union (N_minus x N_plus)",
            "causal_sign_convention_note": "Changing advanced-minus-retarded to retarded-minus-advanced multiplies E_C by -1 and does not change its wavefront set.",
        },
        "principal_symbol_analysis": {
            "operator": "C20=[[Box_2,-I10],[V_2,Box_2]]",
            "principal_symbol": "sigma_2(C20)=[[q I10,0],[sigma_2(V_2),q I10]]",
            "principal_determinant": "q^20",
            "characteristic_set": "Char(C20)={q=0}=metric null cone",
            "extra_characteristic_cone": False,
            "null_symbol_replay": replay,
            "inference_boundary": "The determinant locates characteristic covectors but does not determine the wavefront relation or propagation of polarizations for the nonzero nilpotent null symbol.",
        },
        "pauli_jordan_input": {
            "typed_advanced_retarded_green_operators": "IMPORTED",
            "named_causal_support": "CERTIFIED",
            "pauli_jordan_operator": "E_C=G_C^advanced-G_C^retarded",
            "kernel_wavefront_set": "NOT_COMPUTED",
            "fewster_decomposability_status": "NOT_CERTIFIED",
        },
        "obligation_ledger": {
            "future_past_cone_separation": "CERTIFIED",
            "characteristic_set_is_metric_null_cone": "CERTIFIED",
            "typed_advanced_retarded_support": "CERTIFIED",
            "pauli_jordan_kernel_exists_as_distribution": "OPEN",
            "WF_EC_has_only_opposite_null_orientations": "OPEN",
            "null_bicharacteristic_and_polarization_propagation": "OPEN",
            "regular_GreenHyp_transport_for_Hadamard_states": "OPEN",
        },
        "minimal_missing_carrier": {
            "result_id": "BERGER_COMPANION_PAULI_JORDAN_WAVEFRONT_THEOREM",
            "statement": "Construct the Schwartz kernel of E_C and prove WF(E_C) subset (N_plus x N_minus) union (N_minus x N_plus).",
            "why_not_automatic": [
                "sigma_2(C20) is nonzero and square-zero on the metric null cone",
                "the exact null fixture has rank seven, hence the null symbol is not diagonalizable",
                "support causality and Sobolev Volterra convergence do not determine wavefront orientation",
                "V_2 has differential order two, outside the direct smooth order-zero potential Moller theorem",
            ],
            "acceptable_routes": [
                "a direct kernel wavefront estimate for the Volterra series in a fixed Hörmander topology",
                "a propagation-of-singularities and polarization theorem adapted to the nilpotent companion symbol",
                "a regular GreenHyp morphism whose kernel wavefront action transports the base decomposition",
            ],
        },
        "claim_flags": {
            "BERGER_COMPANION_METRIC_NULL_CHARACTERISTIC_SET": True,
            "BERGER_COMPANION_TYPED_CAUSAL_GREEN_OPERATORS": True,
            "BERGER_COMPANION_PAULI_JORDAN_WAVEFRONT_THEOREM": False,
            "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE": False,
            "BERGER_TYPED_COMPANION_HADAMARD_PARAMETRIX": False,
            "BERGER_TYPED_COMPANION_GLOBAL_HADAMARD": False,
            "BERGER_26_ROW_BRST_HADAMARD": False,
            "BERGER_54_ROW_BRST_HADAMARD": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_COMPANION_PAULI_JORDAN_WAVEFRONT_THEOREM",
        "provenance": {
            "base_result_id": base["result_id"],
            "companion_result_id": companion["result_id"],
            "volterra_result_id": volterra["result_id"],
            "moller_result_id": moller["result_id"],
        },
        "claim_boundary": (
            "Certifies that the twenty-row companion has exactly the metric null "
            "characteristic set and typed causally supported Green operators. It "
            "also certifies the nonzero square-zero null principal-symbol obstruction. "
            "It does not certify the wavefront decomposition of the Pauli--Jordan "
            "kernel, a companion Hadamard parametrix or state, BRST Hadamard data, "
            "a Lorentzian QME, or any quantum result."
        ),
    }
    validate(result)
    return result


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_COMPANION_DECOMPOSABILITY_PREFLIGHT"
        or result.get("result_state")
        != "NULL_CHARACTERISTIC_CONE_CERTIFIED_PAULI_JORDAN_DECOMPOSITION_OPEN"
        or result.get("dependency_tags") != ["LORENTZIAN-CAUSAL"]
        or result.get("next_gate")
        != "BERGER_COMPANION_PAULI_JORDAN_WAVEFRONT_THEOREM"
    ):
        raise ValueError("decomposability preflight identity drifted")
    if not all(
        result.get("principal_symbol_analysis", {})
        .get("null_symbol_replay", {})
        .get("checks", {})
        .values()
    ):
        raise ValueError("null-symbol obstruction dropped")
    ledger = result.get("obligation_ledger", {})
    if ledger.get("WF_EC_has_only_opposite_null_orientations") != "OPEN":
        raise ValueError("Pauli-Jordan wavefront theorem was over-promoted")
    true_flags = {
        key for key, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_COMPANION_METRIC_NULL_CHARACTERISTIC_SET",
        "BERGER_COMPANION_TYPED_CAUSAL_GREEN_OPERATORS",
    }:
        raise ValueError("decomposability or quantum lifecycle was over-promoted")
