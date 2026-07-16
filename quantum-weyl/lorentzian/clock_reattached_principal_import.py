"""Independent import of the Berger clock-reattached principal witness.

This consumer pins the authoritative classical theorem but reconstructs the
five-generator gauge symbol and normalized companion without importing the
classical producer.  It proves the two scalar-biwave principal identities and
keeps the curved lower-order and causal stages fail-closed.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp

from transfer.berger_gauge_fixed_nonminimal_import import _load_record
from transfer.berger_retained_q1_import import ALPHA_B


LORENTZIAN_ROOT = Path(__file__).resolve().parent
ROOT = LORENTZIAN_ROOT.parents[1]
CLASSICAL_COMMIT = "5744d923b898a49bea884e5127768e05cb574b94"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"

CERTIFICATE = "d_quotient_classical/certificates/BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS.json"
SCHEMA = "d_quotient_classical/schema/berger-clock-reattached-principal-witness-v1.schema.json"
PRODUCER = "d_quotient_classical/backreacted_clock/berger_clock_reattached_principal_witness.py"
VERIFIER = "d_quotient_classical/backreacted_clock/verify_berger_clock_reattached_principal_witness.py"
TEST = "d_quotient_classical/backreacted_clock/tests/test_berger_clock_reattached_principal_witness.py"
REPORT = "d_quotient_classical/reports/berger-clock-reattached-principal-witness.md"
Q1_CERTIFICATE = "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CLOCK_CERTIFICATE = "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json"
SOURCE_ARTIFACTS = (
    CERTIFICATE, SCHEMA, PRODUCER, VERIFIER, TEST, REPORT, Q1_CERTIFICATE, CLOCK_CERTIFICATE,
)

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
        raise ValueError(f"missing pinned clock-reattached artifact: {relative}")
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


def _full_gauge(momenta: tuple[sp.Symbol, ...]) -> sp.Matrix:
    gauge = sp.zeros(10, 5)
    for row, (first, second) in enumerate(PAIRS):
        for spatial in range(1, 4):
            gauge[row, spatial - 1] = (
                momenta[first] * (1 if second == spatial else 0)
                + momenta[second] * (1 if first == spatial else 0)
            )
        gauge[row, 3] = (
            (momenta[first] if second == 0 else 0)
            + (momenta[second] if first == 0 else 0)
        )
        gauge[row, 4] = 2 * ETA[first, second]
    return gauge


def _normalized_companion(
    momenta: tuple[sp.Symbol, ...], wave: sp.Expr
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    trace = sp.Matrix([[ETA[first, second] for first, second in PAIRS]])
    divergence = sp.zeros(4, 10)
    for mu in range(4):
        for column, (first, second) in enumerate(PAIRS):
            divergence[mu, column] = sum(
                ETA[axis, axis] * momenta[axis]
                for axis in range(4)
                if tuple(sorted((axis, mu))) == (first, second)
            )
    double_divergence = sp.zeros(1, 10)
    for mu in range(4):
        double_divergence += ETA[mu, mu] * momenta[mu] * divergence[mu, :]
    diffeomorphism = sp.zeros(4, 10)
    for mu in range(4):
        diffeomorphism[mu, :] = (
            wave * divergence[mu, :]
            - sp.Rational(1, 6) * wave * momenta[mu] * trace
            - sp.Rational(1, 3) * momenta[mu] * double_divergence
        )
    companion = sp.zeros(5, 10)
    companion[:3, :] = diffeomorphism[1:4, :]
    companion[3, :] = diffeomorphism[0, :]
    companion[4, :] = (
        sp.Rational(1, 6) * wave**2 * trace
        - sp.Rational(1, 6) * wave * double_divergence
    )
    return companion, diffeomorphism, trace


def _validate_source(
    payload: dict[str, Any], schema: dict[str, Any], q1: dict[str, Any], clock: dict[str, Any]
) -> None:
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-clock-reattached-principal-witness-v1.schema.json"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("clock-reattached source schema identity or strictness drifted")
    if (
        payload.get("result_id") != "BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS"
        or payload.get("claim_status") != "CERTIFIED_PRINCIPAL_COMPLETION_CURVED_OPEN"
        or payload.get("setting_id") != SETTING_ID
        or payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise ValueError("clock-reattached source identity drifted")
    if payload.get("dependency_refs") != {
        "retained_q1": {
            "result_id": "BERGER_RETAINED_MINIMAL_OPERATOR",
            "sha256": hashlib.sha256(_git_blob(Q1_CERTIFICATE)).hexdigest(),
        },
        "clock_sdr": {
            "result_id": "BERGER_MINIMAL_BV_CLOCK_SDR",
            "sha256": hashlib.sha256(_git_blob(CLOCK_CERTIFICATE)).hexdigest(),
        },
    }:
        raise ValueError("clock-reattached dependencies drifted")
    if q1.get("result_id") != "BERGER_RETAINED_MINIMAL_OPERATOR":
        raise ValueError("retained q1 dependency identity drifted")
    if (
        clock.get("result_id") != "BERGER_MINIMAL_BV_CLOCK_SDR"
        or clock.get("flags", {}).get("support_local_clock_SDR_exact") is not True
    ):
        raise ValueError("support-local clock SDR dependency drifted")
    layout = payload.get("reattached_layout", {})
    if layout != {
        "clock_rows_remain_contractible": True,
        "degree_ranks": [5, 12, 12, 5],
        "gauge_order": ["xi_1", "xi_2", "xi_3", "tau", "sigma"],
        "gauge_rank": 5,
        "metric_rank": 10,
        "support_local": True,
        "total_minimal_rows": 34,
    }:
        raise ValueError("clock-reattached layout drifted")
    flags = payload.get("flags", {})
    if not (
        flags.get("BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS") is True
        and flags.get("BERGER_FULL_METRIC_BIWAVE_PRINCIPAL") is True
        and flags.get("BERGER_FULL_GHOST_BIWAVE_PRINCIPAL") is True
        and flags.get("BERGER_CURVED_CLOCK_REATTACHED_WITNESS") is False
        and flags.get("BERGER_CAUSAL_GREEN_HOMOTOPY") is False
        and flags.get("BERGER_ARITY_TWO_D_CARTAN") is False
        and payload.get("next_gate") == "BERGER_CURVED_CLOCK_REATTACHED_WITNESS"
    ):
        raise ValueError("clock-reattached claim boundary drifted")


def _replay(payload: dict[str, Any], q1: dict[str, Any]) -> dict[str, bool]:
    hessian = _load_record("H_retained", q1["q1_blocks"]["H_retained"], (10, 10))
    hessian4 = _symbol(hessian, 4)
    p = sp.symbols("p0:4")
    wave = -p[0] ** 2 + p[1] ** 2 + p[2] ** 2 + p[3] ** 2
    gauge = _full_gauge(p)
    companion, diffeomorphism, trace = _normalized_companion(p, wave)
    raised = sp.diag(*[
        sp.Rational(
            1,
            (1 if first == second else 2) * ETA[first, first] * ETA[second, second],
        )
        for first, second in PAIRS
    ])
    fibre = sp.Rational(4, 1) / ALPHA_B * raised
    symbols = {f"p{index}": p[index] for index in range(4)}
    frozen_companion = sp.Matrix([
        [sp.sympify(value, locals=symbols) for value in row]
        for row in payload["normalized_witness"]["companion_matrix"]
    ])
    frozen_metric = sp.Matrix([
        [sp.sympify(value, locals=symbols) for value in row]
        for row in payload["principal_identities"]["metric_matrix"]
    ])
    frozen_ghost = sp.Matrix([
        [sp.sympify(value, locals=symbols) for value in row]
        for row in payload["principal_identities"]["ghost_matrix"]
    ])
    checks = {
        "support_local_clock_reattachment": payload["reattached_layout"]["support_local"] is True,
        "clock_rows_remain_contractible": payload["reattached_layout"]["clock_rows_remain_contractible"] is True,
        "full_five_generator_gauge_reconstructed": gauge.shape == (10, 5),
        "normalized_companion_reconstructed": sp.simplify(frozen_companion - companion) == sp.zeros(5, 10),
        "metric_scalar_biwave_identity": sp.simplify(
            fibre * hessian4 + gauge * companion - wave**2 * sp.eye(10)
        ) == sp.zeros(10),
        "ghost_scalar_biwave_identity": sp.simplify(
            companion * gauge - wave**2 * sp.eye(5)
        ) == sp.zeros(5),
        "frozen_metric_matrix_replayed": sp.simplify(
            frozen_metric - wave**2 * sp.eye(10)
        ) == sp.zeros(10),
        "frozen_ghost_matrix_replayed": sp.simplify(
            frozen_ghost - wave**2 * sp.eye(5)
        ) == sp.zeros(5),
        "fibre_identification_nondegenerate": sp.factor(raised.det()) != 0,
        "diffeomorphism_weyl_cross_terms_zero": (
            sp.simplify(diffeomorphism * (2 * trace.T)) == sp.zeros(4, 1)
            and sp.simplify(companion[4, :] * gauge[:, :4]) == sp.zeros(1, 4)
        ),
    }
    if not all(checks.values()):
        failures = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"clock-reattached principal replay failed: {failures}")
    return checks


def validate_import(
    payload: dict[str, Any], schema: dict[str, Any], q1: dict[str, Any], clock: dict[str, Any]
) -> dict[str, Any]:
    _validate_source(payload, schema, q1, clock)
    checks = _replay(payload, q1)
    return {
        "schema": "quantum-weyl-berger-clock-reattached-principal-import-v1",
        "result_id": "BERGER_CLOCK_REATTACHED_PRINCIPAL_INPUT_IMPORT",
        "result_state": "PRINCIPAL_WITNESS_IMPORTED_CURVED_LOWER_ORDERS_OPEN",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
        "coverage": {
            "retained_rows": 26,
            "clock_reattached_minimal_rows": 34,
            "degree_ranks": [5, 12, 12, 5],
            "metric_rank": 10,
            "gauge_rank": 5,
        },
        "independent_exact_checks": checks,
        "preferred_realization": {
            "kind": "CLOCK_REATTACHED_SUPPORT_LOCAL_SDR",
            "principal_metric_operator": "(zeta^2)^2 I_10",
            "principal_ghost_operator": "(zeta^2)^2 I_5",
            "scalar_characteristic_set": "zeta^2=0",
            "retained_rank_eight_interpretation": "PRESENTATION_EFFECT_RESOLVED_UPSTAIRS",
            "transport_target": "retained_26_row_complex",
        },
        "input_gate_update": {
            "BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS": "IMPORTED_AND_REPLAYED",
            "BERGER_CURVED_CLOCK_REATTACHED_WITNESS": "NOT_CONSTRUCTED",
            "BERGER_CAUSAL_GREEN_HOMOTOPY": "NOT_CONSTRUCTED",
            "BERGER_HADAMARD_DATA": "NOT_CONSTRUCTED",
        },
        "quantum_execution_authorized": False,
        "next_gate": "BERGER_CURVED_CLOCK_REATTACHED_WITNESS",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "artifacts": [_artifact(path) for path in SOURCE_ARTIFACTS],
        },
        "claim_boundary": (
            "Imports and independently replays the scalar-biwave principal completion "
            "on the support-locally clock-reattached 34-row minimal presentation. It "
            "does not construct the curved lower-order QW+WQ witness, advanced or "
            "retarded Green operators, the transported 26-row homotopy, Hadamard data, "
            "or a Lorentzian quantum theory."
        ),
    }


def build_import() -> dict[str, Any]:
    return validate_import(
        _git_json(CERTIFICATE), _git_json(SCHEMA),
        _git_json(Q1_CERTIFICATE), _git_json(CLOCK_CERTIFICATE),
    )
