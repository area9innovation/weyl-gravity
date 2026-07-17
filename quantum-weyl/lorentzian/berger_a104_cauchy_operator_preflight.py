"""Coefficientwise Cauchy-operator preflight for the Berger hybrid companion.

The retained metric and metric-antifield endpoints have portable exact
second-order companion coefficients.  The ghost and identity endpoints have
an exact factorization theorem, but their four factor matrices are not yet
exported.  This module therefore constructs the two exact rank-40 Cauchy
operators and proves a minimal missing-carrier theorem for the remaining 24
Cauchy components.  It does not synthesize classical factor data.
"""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from transfer.berger_gauge_fixed_nonminimal_import import (
    _adjoint_transpose,
    _embed,
    _identity,
    _is_zero,
    _multiply,
    _subtract,
    _zero,
)
from transfer.berger_retained_q1_import import _normalize

from . import metric_lower_by_two_biwave_import as LOWER


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATIONARY = HERE / "certificates/BERGER_RETAINED_26_STATIONARY_SPECTRAL_PREFLIGHT.json"
LOWER_IMPORT = HERE / "certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORT.json"
ENDPOINT_IMPORT = HERE / "certificates/BERGER_ENDPOINT_FACTOR_INPUT_IMPORT.json"
ENDPOINT_CONTRACT = HERE / "certificates/BERGER_26_ROW_GREEN_HADAMARD_ENDPOINT_CONTRACT.json"
LAYOUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json"
GENERATED = HERE / "generated/berger_a104_cauchy_operator_preflight"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    artifact_id = payload.get("result_id") or payload.get("schema")
    if not isinstance(artifact_id, str) or not artifact_id:
        raise ValueError(f"dependency has no stable identity: {path}")
    return {"artifact_id": artifact_id, "sha256": _sha256(path)}


def _negative(matrix):
    return [
        [
            {word: -coefficient for word, coefficient in operator.items()}
            for operator in row
        ]
        for row in matrix
    ]


def _companion(wave, remainder):
    result = _zero(20, 20)
    _embed(result, wave, 0, 0)
    _embed(result, _negative(_identity(10)), 0, 10)
    _embed(result, remainder, 10, 0)
    _embed(result, wave, 10, 10)
    return result


def _split_temporal(matrix):
    pieces = [_zero(len(matrix), len(matrix[0])) for _ in range(3)]
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            accumulators: list[dict[tuple[int, ...], sp.Expr]] = [{}, {}, {}]
            for word, coefficient in operator.items():
                temporal_order = word.count(0)
                if temporal_order > 2:
                    raise ValueError("second-order companion contains temporal order >2")
                spatial_word = tuple(axis for axis in word if axis != 0)
                accumulator = accumulators[temporal_order]
                accumulator[spatial_word] = (
                    accumulator.get(spatial_word, sp.S.Zero) + coefficient
                )
            for order, accumulator in enumerate(accumulators):
                pieces[order][row][column] = _normalize(accumulator)
    return tuple(pieces)


def _restore_temporal(pieces):
    result = _zero(len(pieces[0]), len(pieces[0][0]))
    for order, matrix in enumerate(pieces):
        for row, values in enumerate(matrix):
            for column, operator in enumerate(values):
                combined = dict(result[row][column])
                for word, coefficient in operator.items():
                    restored = (0,) * order + word
                    combined[restored] = combined.get(restored, 0) + coefficient
                result[row][column] = _normalize(combined)
    return result


def _constant_inverse(matrix):
    rank = len(matrix)
    coefficients = sp.zeros(rank)
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            if set(operator) - {()}:
                raise ValueError("temporal leading coefficient is not order zero")
            coefficients[row, column] = operator.get((), sp.S.Zero)
    inverse = sp.simplify(coefficients.inv())
    result = _zero(rank, rank)
    for row in range(rank):
        for column in range(rank):
            coefficient = sp.factor(inverse[row, column])
            if coefficient != 0:
                result[row][column] = {(): coefficient}
    return result, coefficients


def _cauchy_generator(pieces):
    K0, K1, K2 = pieces
    K2_inverse, leading = _constant_inverse(K2)
    rank = len(K0)
    generator = _zero(2 * rank, 2 * rank)
    _embed(generator, _identity(rank), 0, rank)
    _embed(generator, _negative(_multiply(K2_inverse, K0)), rank, 0)
    _embed(generator, _negative(_multiply(K2_inverse, K1)), rank, rank)
    return generator, K2_inverse, leading


def _matrix_record(matrix) -> dict[str, Any]:
    entries = []
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            if not operator:
                continue
            terms = []
            for word, coefficient in sorted(operator.items()):
                exponents = [word.count(axis) for axis in range(4)]
                terms.append([exponents, str(sp.factor(coefficient))])
            entries.append([row, column, terms])
    body = {"shape": [len(matrix), len(matrix[0])], "entries": entries}
    body["sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return body


def _artifact_text(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _artifact_reference(name: str, payload: dict[str, Any]) -> dict[str, str]:
    content = _artifact_text(payload).encode()
    return {
        "format": "JSON_EXACT_SPARSE_OPERATOR",
        "path": f"quantum-weyl/lorentzian/generated/berger_a104_cauchy_operator_preflight/{name}.json",
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _maximum_spatial_order(matrix) -> int:
    return max(
        (len(word) for row in matrix for operator in row for word in operator),
        default=-1,
    )


def metric_cauchy_replay() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Build the metric and metric-antifield graph Cauchy generators exactly."""

    receipt = LOWER.fast_receipt()
    if not all(receipt["checks"].values()):
        raise ValueError("lower-by-two fast receipt drifted")
    source = LOWER._git_json(LOWER.CERTIFICATE)
    references = source["normal_form"]["artifacts"]
    wave = LOWER._load_artifact(references["rough_tensor_wave"], "rough_tensor_wave")
    remainder = LOWER._load_artifact(
        references["lower_by_two_remainder"], "lower_by_two_remainder"
    )
    sectors = {
        "metric": _companion(wave, remainder),
        "metric_antifield": _companion(
            _adjoint_transpose(wave), _adjoint_transpose(remainder)
        ),
    }
    artifacts: dict[str, dict[str, Any]] = {}
    ledgers: dict[str, Any] = {}
    for name, companion in sectors.items():
        pieces = _split_temporal(companion)
        generator, K2_inverse, leading = _cauchy_generator(pieces)
        K0, K1, K2 = pieces
        identity20 = _identity(20)
        lower_left = [row[:20] for row in generator[20:]]
        lower_right = [row[20:] for row in generator[20:]]
        checks = {
            "temporal_split_reconstructs_companion": _is_zero(
                _subtract(_restore_temporal(pieces), companion)
            ),
            "K2_rank_20": int(leading.rank()) == 20,
            "K2_inverse_left": _is_zero(
                _subtract(_multiply(K2_inverse, K2), identity20)
            ),
            "K2_inverse_right": _is_zero(
                _subtract(_multiply(K2, K2_inverse), identity20)
            ),
            "first_order_equation_reconstructs_second_order": _is_zero(
                _subtract(
                    _subtract(
                        _negative(_multiply(K2, lower_left)), K0
                    ),
                    _zero(20, 20),
                )
            )
            and _is_zero(
                _subtract(
                    _subtract(
                        _negative(_multiply(K2, lower_right)), K1
                    ),
                    _zero(20, 20),
                )
            ),
            "A40_spatial_order_at_most_two": _maximum_spatial_order(generator)
            <= 2,
        }
        if not all(checks.values()):
            raise ValueError(f"{name} Cauchy replay failed")
        records = {
            "K0": _matrix_record(K0),
            "K1": _matrix_record(K1),
            "K2": _matrix_record(K2),
            "K2_inverse": _matrix_record(K2_inverse),
            "A40": _matrix_record(generator),
        }
        for label, payload in records.items():
            artifacts[f"{name}_{label}"] = payload
        ledgers[name] = {
            "second_order_companion_rank": 20,
            "first_order_Cauchy_rank": 40,
            "Cauchy_ordering": "(configuration20,partial_t configuration20)",
            "endpoint_operator": (
                "A10=Box_2^2+V_2"
                if name == "metric"
                else "A10^sharp=(Box_2^sharp)^2+V_2^sharp"
            ),
            "graph_companion": (
                "[[Box_2,-I10],[V_2,Box_2]]"
                if name == "metric"
                else "[[Box_2^sharp,-I10],[V_2^sharp,Box_2^sharp]]"
            ),
            "temporal_leading_rank": int(leading.rank()),
            "maximum_spatial_order_A40": _maximum_spatial_order(generator),
            "artifacts": {
                label: _artifact_reference(f"{name}_{label}", payload)
                for label, payload in records.items()
            },
            "checks": checks,
        }
    return ledgers, artifacts


def _load_boundaries() -> dict[str, Any]:
    stationary = json.loads(STATIONARY.read_text())
    lower = json.loads(LOWER_IMPORT.read_text())
    endpoint = json.loads(ENDPOINT_IMPORT.read_text())
    contract = json.loads(ENDPOINT_CONTRACT.read_text())
    layout = json.loads(LAYOUT.read_text())
    if stationary.get("claim_flags", {}).get(
        "BERGER_RETAINED_FIRST_ORDER_CAUCHY_TARGET_A104"
    ) is not True:
        raise ValueError("stationary A104 target drifted")
    if lower.get("claim_flags", {}).get("BERGER_METRIC_LOWER_BY_TWO_BIWAVE") is not True:
        raise ValueError("metric lower-by-two input drifted")
    if endpoint.get("result_id") != "BERGER_ENDPOINT_FACTOR_INPUT_IMPORT":
        raise ValueError("endpoint factor import drifted")
    partial = contract.get("partial_input", {})
    required = [
        "F_spatial_K_spatial",
        "Box_1_spatial_covector",
        "F_spatial_K_spatial_formal_adjoint",
        "Box_1_spatial_covector_formal_adjoint",
    ]
    if (
        partial.get("explicit_factor_records")
        != "REQUESTED_FROM_CLASSICAL_SOURCE_NOT_YET_EXPORTED"
        or partial.get("required_factor_record_ids") != required
    ):
        raise ValueError("endpoint missing-factor boundary drifted")
    if layout.get("result_id") != "BERGER_RETAINED_MINIMAL_LAYOUT":
        raise ValueError("retained row layout drifted")
    return {
        "stationary": stationary,
        "lower": lower,
        "endpoint": endpoint,
        "contract": contract,
        "layout": layout,
    }


def cauchy_row_ledger(layout: dict[str, Any]) -> dict[str, Any]:
    by_degree: dict[int, list[dict[str, Any]]] = {}
    for row in layout["component_rows"]:
        by_degree.setdefault(int(row["degree"]), []).append(row)
    specifications = (
        (-1, "primary", "ghost_primary", "s+1"),
        (-1, "auxiliary", "ghost_auxiliary", "s"),
        (0, "primary", "metric_primary", "s+1"),
        (0, "auxiliary", "metric_auxiliary", "s"),
        (1, "primary", "metric_antifield_primary", "s+1"),
        (1, "auxiliary", "metric_antifield_auxiliary", "s"),
        (2, "primary", "identity_primary", "s+1"),
        (2, "auxiliary", "identity_auxiliary", "s"),
    )
    configuration = []
    for degree, role, block, exponent in specifications:
        for source in by_degree[degree]:
            row_id = source["row_id"] if role == "primary" else f"aux[{source['row_id']}]"
            configuration.append(
                {
                    "index": len(configuration),
                    "row_id": row_id,
                    "origin_row_id": source["row_id"],
                    "block": block,
                    "role": role,
                    "degree": degree,
                    "parity": source["parity"],
                    "Sobolev_exponent": exponent,
                }
            )
    velocity = [
        {
            **row,
            "index": row["index"] + 52,
            "row_id": f"partial_t[{row['row_id']}]",
            "role": f"velocity_of_{row['role']}",
            "Sobolev_exponent": "s" if row["role"] == "primary" else "s-1",
        }
        for row in configuration
    ]
    rows = configuration + velocity
    checks = {
        "configuration_rows_52": len(configuration) == 52,
        "Cauchy_rows_104": len(rows) == 104,
        "indices_contiguous": [row["index"] for row in rows] == list(range(104)),
        "row_ids_unique": len({row["row_id"] for row in rows}) == 104,
        "degrees_inherited": {
            str(degree): sum(row["degree"] == degree for row in rows)
            for degree in (-1, 0, 1, 2)
        }
        == {"-1": 12, "0": 40, "1": 40, "2": 12},
    }
    if not all(checks.values()):
        raise ValueError("Cauchy row ledger failed")
    return {
        "rows": rows,
        "degree_ranks": [12, 40, 40, 12],
        "pairing_partner_status": "NOT_DERIVED_REQUIRES_CAUCHY_LAGRANGE_FORM",
        "checks": checks,
    }


@lru_cache(maxsize=1)
def build() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    inputs = _load_boundaries()
    metric, artifacts = metric_cauchy_replay()
    rows = cauchy_row_ledger(inputs["layout"])
    paths = {
        "stationary_spectral_preflight": STATIONARY,
        "metric_lower_by_two_import": LOWER_IMPORT,
        "endpoint_factor_import": ENDPOINT_IMPORT,
        "endpoint_contract": ENDPOINT_CONTRACT,
        "retained_layout": LAYOUT,
    }
    result = {
        "schema": "quantum-weyl-berger-a104-cauchy-operator-preflight-v1",
        "result_id": "BERGER_A104_CAUCHY_OPERATOR_PREFLIGHT",
        "result_state": "METRIC_A80_EXACT_ENDPOINT_A24_AND_CAUCHY_BRST_PAIRING_OPEN",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "classical_commit": inputs["stationary"]["classical_commit"],
        "setting_id": inputs["stationary"]["setting_id"],
        "dependency_refs": {name: _dependency(path) for name, path in paths.items()},
        "Cauchy_row_ledger": rows,
        "metric_Cauchy_operators": metric,
        "partial_A104_assembly": {
            "certified_Cauchy_components": 80,
            "certified_sectors": ["metric_A40", "metric_antifield_A40"],
            "missing_Cauchy_components": 24,
            "missing_sectors": ["ghost_A12", "identity_A12"],
            "full_A104_status": "NOT_ASSEMBLED",
        },
        "minimal_missing_endpoint_carrier": {
            "status": "EXACTLY_IDENTIFIED",
            "required_factor_record_ids": inputs["contract"]["partial_input"][
                "required_factor_record_ids"
            ],
            "required_format": "JSON_EXACT_SPARSE_OPERATOR_WITH_SHAPE_ENTRIES_SHA256",
            "why_required": "the factorization theorem fixes names and principal symbols but does not export the lower-order coefficient matrices needed for ghost_A12 and identity_A12",
            "forbidden_fallback": "do not reconstruct the four factors independently from classical geometry inside quantum-weyl",
        },
        "BRST_and_pairing_gate": {
            "q26_input": "AVAILABLE",
            "q52_companion_prolongation": "NOT_EXPORTED",
            "q_Cauchy_104": "NOT_CONSTRUCTED",
            "A104_q_Cauchy_commutator": "NOT_COMPUTED",
            "spacetime_BV_pairing": "AVAILABLE",
            "Cauchy_Lagrange_form": "NOT_CONSTRUCTED",
            "Krein_skew_adjointness_A104": "NOT_COMPUTED",
        },
        "analytic_gate": {
            "closed_generator_theorem_authorized": False,
            "reason": "the full coefficientwise A104, q_Cauchy and Cauchy boundary form must precede domain equality or Krein spectral claims",
            "eventual_route": "identify the explicit A104 on a smooth core with the stationary C0 evolution, prove Dom(A104)=E_(s+1), then use a nonempty resolvent and compact embedding",
        },
        "claim_flags": {
            "BERGER_METRIC_A40_CAUCHY_OPERATOR": True,
            "BERGER_METRIC_ANTIFIELD_A40_CAUCHY_OPERATOR": True,
            "BERGER_CAUCHY_ROW_LEDGER_104": True,
            "BERGER_FULL_A104_CAUCHY_OPERATOR": False,
            "BERGER_Q_CAUCHY_104": False,
            "BERGER_CAUCHY_KREIN_FORM": False,
            "BERGER_A104_CLOSED_GENERATOR": False,
            "BERGER_A104_ZERO_ISOLATED": False,
            "BERGER_HADAMARD_DATA": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_ENDPOINT_FACTOR_OPERATOR_EXPORT_AND_CAUCHY_BRST_PROLONGATION",
        "provenance": {
            "stationary_result_id": inputs["stationary"]["result_id"],
            "lower_result_id": inputs["lower"]["result_id"],
            "endpoint_result_id": inputs["endpoint"]["result_id"],
        },
        "claim_boundary": "Constructs exact coefficientwise rank-40 Cauchy operators for the metric endpoint and an independent graph companion for its formal-adjoint endpoint, covering 80 of 104 Cauchy components. It freezes the inherited 104-row grading and Sobolev ledger and proves that four unexported endpoint factor matrices are the minimal carrier for the remaining 24 components. It does not assemble full A104, construct q_Cauchy or a Cauchy pairing, prove closedness, isolate zero, split frequencies, construct Hadamard data, restore a QME or make a quantum claim.",
    }
    validate(result)
    return result, artifacts


def validate(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_A104_CAUCHY_OPERATOR_PREFLIGHT"
        or result.get("result_state")
        != "METRIC_A80_EXACT_ENDPOINT_A24_AND_CAUCHY_BRST_PAIRING_OPEN"
        or result.get("next_gate")
        != "BERGER_ENDPOINT_FACTOR_OPERATOR_EXPORT_AND_CAUCHY_BRST_PROLONGATION"
    ):
        raise ValueError("A104 Cauchy preflight identity drifted")
    if not all(result.get("Cauchy_row_ledger", {}).get("checks", {}).values()):
        raise ValueError("Cauchy row ledger dropped")
    for sector in ("metric", "metric_antifield"):
        if not all(
            result.get("metric_Cauchy_operators", {})
            .get(sector, {})
            .get("checks", {})
            .values()
        ):
            raise ValueError(f"{sector} exact Cauchy operator dropped")
    partial = result.get("partial_A104_assembly", {})
    if (
        partial.get("certified_Cauchy_components") != 80
        or partial.get("missing_Cauchy_components") != 24
        or partial.get("full_A104_status") != "NOT_ASSEMBLED"
        or result.get("BRST_and_pairing_gate", {}).get("q_Cauchy_104")
        != "NOT_CONSTRUCTED"
        or result.get("analytic_gate", {}).get("closed_generator_theorem_authorized")
        is not False
    ):
        raise ValueError("full A104 or analytic theorem was over-promoted")
    true_flags = {
        key for key, value in result.get("claim_flags", {}).items() if value is True
    }
    if true_flags != {
        "BERGER_METRIC_A40_CAUCHY_OPERATOR",
        "BERGER_METRIC_ANTIFIELD_A40_CAUCHY_OPERATOR",
        "BERGER_CAUCHY_ROW_LEDGER_104",
    }:
        raise ValueError("A104, BRST, pairing, Hadamard or quantum claim over-promoted")
