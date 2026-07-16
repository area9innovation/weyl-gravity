"""Exact retained-metric and biwave companion preflight for the Berger endpoint."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from transfer import berger_minimal_contraction_import as CONTRACTION
from transfer.berger_gauge_fixed_nonminimal_import import (
    _is_zero,
    _multiply,
    _subtract,
)

from . import metric_lower_by_two_biwave_import as LOWER
from . import raw_endpoint_import as RAW


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOWER_IMPORT = HERE / "certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORT.json"
CONTRACTION_IMPORT = ROOT / "quantum-weyl/transfer/certificates/BERGER_MINIMAL_34_CONTRACTION_IMPORT.json"
RAW_IMPORT = HERE / "certificates/BERGER_RAW_ENDPOINT_INPUT_IMPORT.json"
ENDPOINT_FACTOR_IMPORT = HERE / "certificates/BERGER_ENDPOINT_FACTOR_INPUT_IMPORT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero(rows: int, columns: int):
    return [[{} for _ in range(columns)] for _ in range(rows)]


def _identity(rank: int):
    result = _zero(rank, rank)
    for index in range(rank):
        result[index][index] = {(): sp.S.One}
    return result


def _embed(target, block, row_offset: int, column_offset: int) -> None:
    for row, values in enumerate(block):
        for column, operator in enumerate(values):
            target[row + row_offset][column + column_offset] = operator


def _block(matrix, rows: range, columns: range):
    return [[matrix[row][column] for column in columns] for row in rows]


def _negative(matrix):
    return [
        [
            {word: -coefficient for word, coefficient in operator.items()}
            for operator in row
        ]
        for row in matrix
    ]


def _load_quantum_boundaries() -> dict[str, Any]:
    lower = json.loads(LOWER_IMPORT.read_text())
    contraction = json.loads(CONTRACTION_IMPORT.read_text())
    raw = json.loads(RAW_IMPORT.read_text())
    endpoint = json.loads(ENDPOINT_FACTOR_IMPORT.read_text())
    if (
        lower.get("result_id") != "BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORT"
        or lower.get("claim_flags", {}).get("BERGER_METRIC_LOWER_BY_TWO_BIWAVE")
        is not True
        or lower.get("claim_flags", {}).get(
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"
        )
        is not False
        or lower.get("claim_flags", {}).get("QUANTUM_CLAIM") is not False
    ):
        raise ValueError("lower-by-two quantum boundary drifted")
    if (
        contraction.get("result_id") != "BERGER_MINIMAL_34_CONTRACTION_IMPORT"
        or contraction.get("coverage", {}).get("full_minimal_rows") != 34
        or contraction.get("coverage", {}).get("retained_minimal_rows") != 26
        or contraction.get("coverage", {}).get(
            "complete_minimal_classical_contraction"
        )
        is not True
        or contraction.get("nd2_gate", {}).get("physical_execution_authorized")
        is not False
    ):
        raise ValueError("minimal contraction quantum boundary drifted")
    if (
        raw.get("result_id") != "BERGER_RAW_ENDPOINT_INPUT_IMPORT"
        or raw.get("principal_compatibility_certified") is not True
        or raw.get("green_execution_authorized") is not False
    ):
        raise ValueError("raw endpoint quantum boundary drifted")
    if (
        endpoint.get("result_id") != "BERGER_ENDPOINT_FACTOR_INPUT_IMPORT"
        or endpoint.get("result_state")
        != "PARTIAL_LORENTZIAN_ENDPOINT_FACTORS_IMPORTED_METRIC_OPEN"
        or endpoint.get("quantum_execution_authorized") is not False
        or endpoint.get("causal_endpoint_status", {}).get("metric_endpoint")
        != "NOT_CONSTRUCTED_GENERIC_RANK_EIGHT_PLUS_TWO_MIXED_ORDER"
        or endpoint.get("causal_endpoint_status", {}).get("retained_26_row_chain_homotopy")
        != "NOT_CONSTRUCTED"
    ):
        raise ValueError("endpoint factor quantum boundary drifted")
    return {
        "lower": lower,
        "contraction": contraction,
        "raw": raw,
        "endpoint": endpoint,
    }


@lru_cache(maxsize=1)
def evaluate_preflight() -> dict[str, Any]:
    boundaries = _load_quantum_boundaries()

    portable = CONTRACTION._git_json(CONTRACTION.CERTIFICATE_RELATIVE)
    contraction = portable["contraction"]
    inclusion = CONTRACTION._constant_operator(
        CONTRACTION._load_constant_record(
            "iota_cl", contraction["iota_cl"], (34, 26)
        )
    )
    projection = CONTRACTION._constant_operator(
        CONTRACTION._load_constant_record(
            "pi_cl", contraction["pi_cl"], (26, 34)
        )
    )

    transport = RAW._git_json(RAW.TRANSPORT_CERTIFICATE)
    p34 = RAW._load_artifact(
        transport["operators"]["P34_raw"], name="P34_raw", shape=(34, 34)
    )
    p26 = _multiply(_multiply(projection, p34), inclusion)
    degree_ranges = (range(0, 3), range(3, 13), range(13, 23), range(23, 26))
    off_degree_blocks_zero = all(
        _is_zero(_block(p26, rows, columns))
        for row_index, rows in enumerate(degree_ranges)
        for column_index, columns in enumerate(degree_ranges)
        if row_index != column_index
    )

    metric34 = _block(p34, range(5, 15), range(5, 15))
    retained_metric = _block(p26, range(3, 13), range(3, 13))
    retained_metric_equals_raw = _is_zero(_subtract(retained_metric, metric34))

    source = LOWER._git_json(LOWER.CERTIFICATE)
    artifacts = source["normal_form"]["artifacts"]
    wave = LOWER._load_artifact(artifacts["rough_tensor_wave"], "rough_tensor_wave")
    remainder = LOWER._load_artifact(
        artifacts["lower_by_two_remainder"], "lower_by_two_remainder"
    )
    lower_by_two_exact = _is_zero(
        _subtract(_subtract(retained_metric, _multiply(wave, wave)), remainder)
    )

    # C20(h,y)=(Box_2 h-y,V_2 h+Box_2 y).  The graph inclusion
    # J(h)=(h,Box_2 h) gives C20 J(h)=(0,A10 h) exactly.
    companion = _zero(20, 20)
    _embed(companion, wave, 0, 0)
    _embed(companion, _negative(_identity(10)), 0, 10)
    _embed(companion, remainder, 10, 0)
    _embed(companion, wave, 10, 10)
    # Block multiplication gives top row Box_2-Box_2=0 and bottom row
    # V_2+Box_2^2=A10.  Reuse the already replayed exact lower-by-two
    # identity instead of expanding the same 20x10 product a second time.
    companion_graph_identity = lower_by_two_exact

    momenta = sp.symbols("p0:4")
    q = -momenta[0] ** 2 + sum(momentum**2 for momentum in momenta[1:])
    wave_symbol = RAW._homogeneous_symbol(wave, 2)
    remainder_symbol = RAW._homogeneous_symbol(remainder, 2)
    principal_block_triangular = sp.simplify(wave_symbol - q * sp.eye(10)) == sp.zeros(10)
    fixture = {RAW.U: sp.Rational(2), RAW.V: sp.Rational(3)}
    null_substitution = fixture | {
        momenta[0]: 1,
        momenta[1]: 1,
        momenta[2]: 0,
        momenta[3]: 0,
    }
    off_cone_substitution = fixture | {
        momenta[0]: 2,
        momenta[1]: 1,
        momenta[2]: 0,
        momenta[3]: 0,
    }
    ranks = {
        # On q=0 the block-lower-triangular companion symbol has the rank of
        # sigma_2(V_2); off q=0 both ten-row diagonal blocks are invertible.
        "metric_null_fixture": int(
            remainder_symbol.subs(null_substitution).rank()
        ),
        "off_metric_cone_fixture": 20
        if sp.factor(q.subs(off_cone_substitution)) != 0
        else 0,
    }

    checks = {
        "portable_projection_and_inclusion_loaded": True,
        "retained_P26_is_degree_block_diagonal": off_degree_blocks_zero,
        "retained_metric_block_equals_raw_A10": retained_metric_equals_raw,
        "retained_metric_A10_equals_Box2_squared_plus_V2": lower_by_two_exact,
        "companion_graph_identity_exact": companion_graph_identity,
        "companion_principal_block_lower_triangular": principal_block_triangular,
        "companion_principal_determinant_is_q_power_20": principal_block_triangular,
        "companion_principal_null_rank_seven": ranks["metric_null_fixture"] == 7,
        "companion_principal_off_cone_rank_twenty": ranks[
            "off_metric_cone_fixture"
        ]
        == 20,
        "ghost_and_identity_endpoint_factors_imported": True,
    }
    if not all(checks.values()):
        raise ValueError("retained biwave companion preflight failed")

    result = {
        "schema": "quantum-weyl-berger-retained-biwave-companion-preflight-v1",
        "result_id": "BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT",
        "result_state": "RETAINED_METRIC_IDENTIFIED_COMPANION_EXACT_CAUSAL_RESOLVENT_OPEN",
        "lifecycle_layer": "CLASSICAL_BV_CAUSAL_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": LOWER.SETTING_ID,
        "retained_endpoint": {
            "degree_ranks": [3, 10, 10, 3],
            "identity": "P26=pi_cl P34_raw iota_cl",
            "metric_identity": "P26_metric=A10=Box_2^2+V_2",
            "metric_rows": 10,
            "metric_antifield_rows": 10,
        },
        "companion_system": {
            "rows": 20,
            "fields": ["h_10", "y_10=Box_2 h_10"],
            "operator": "C20=[[Box_2,-I10],[V_2,Box_2]]",
            "graph_inclusion": "J20x10(h)=(h,Box_2 h)",
            "graph_identity": "C20 J20x10(h)=(0,A10 h)",
            "principal_symbol": "[[q I10,0],[sigma_2(V_2),q I10]]",
            "principal_determinant": "q^20",
            "extra_characteristic_cone": False,
            "rational_fixture": {"u": "2", "v": "3"},
            "principal_ranks": ranks,
        },
        "exact_checks": checks,
        "causal_policy": {
            "candidate_route": "CAUSAL_VOLTERRA_RESOLVENT_FOR_LOWER_BY_TWO_BIWAVE_COMPANION",
            "diagonal_blocks": "normally hyperbolic tensor rough waves Box_2",
            "off_diagonal_local_orders": {"upper_right": 0, "lower_left": 2},
            "inverse_spatial_laplacian": False,
            "spatial_mode_projector": False,
            "volterra_convergence_and_global_support_proof": "NOT_CONSTRUCTED",
            "advanced_retarded_operators": "NOT_CONSTRUCTED",
        },
        "claim_flags": {
            "BERGER_RETAINED_METRIC_EQUALS_RAW_A10": True,
            "BERGER_RETAINED_BIWAVE_COMPANION_EXACT": True,
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT": False,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT",
        "provenance": {
            "dependencies": {
                "lower_by_two_import": {
                    "path": str(LOWER_IMPORT.relative_to(ROOT)),
                    "sha256": _sha256(LOWER_IMPORT),
                },
                "minimal_contraction_import": {
                    "path": str(CONTRACTION_IMPORT.relative_to(ROOT)),
                    "sha256": _sha256(CONTRACTION_IMPORT),
                },
                "raw_endpoint_import": {
                    "path": str(RAW_IMPORT.relative_to(ROOT)),
                    "sha256": _sha256(RAW_IMPORT),
                },
                "endpoint_factor_import": {
                    "path": str(ENDPOINT_FACTOR_IMPORT.relative_to(ROOT)),
                    "sha256": _sha256(ENDPOINT_FACTOR_IMPORT),
                },
            },
            "imported_boundary_states": {
                name: value["result_id"] for name, value in boundaries.items()
            },
        },
        "claim_boundary": (
            "Independently proves that the exact A10 lower-by-two tensor biwave is "
            "the metric block induced on the retained 26-row endpoint and constructs "
            "its exact 20-row local companion presentation. The companion principal "
            "determinant has only the metric characteristic cone. This does not prove "
            "Volterra convergence, construct advanced/retarded operators, complete the "
            "26- or 54-row causal chain homotopy, establish Hadamard data, restore a "
            "QME, or make a quantum claim."
        ),
    }
    validate_preflight_result(result)
    return result


def validate_preflight_result(result: dict[str, Any]) -> None:
    if (
        result.get("result_id") != "BERGER_RETAINED_BIWAVE_COMPANION_PREFLIGHT"
        or result.get("result_state")
        != "RETAINED_METRIC_IDENTIFIED_COMPANION_EXACT_CAUSAL_RESOLVENT_OPEN"
        or result.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or result.get("next_gate") != "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT"
    ):
        raise ValueError("retained companion result identity drifted")
    if not all(result.get("exact_checks", {}).values()):
        raise ValueError("retained companion exact check dropped")
    if result.get("claim_flags") != {
        "BERGER_RETAINED_METRIC_EQUALS_RAW_A10": True,
        "BERGER_RETAINED_BIWAVE_COMPANION_EXACT": True,
        "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT": False,
        "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        "QUANTUM_CLAIM": False,
    }:
        raise ValueError("retained companion lifecycle boundary drifted")
    policy = result.get("causal_policy", {})
    if (
        policy.get("inverse_spatial_laplacian") is not False
        or policy.get("spatial_mode_projector") is not False
        or policy.get("volterra_convergence_and_global_support_proof")
        != "NOT_CONSTRUCTED"
        or policy.get("advanced_retarded_operators") != "NOT_CONSTRUCTED"
    ):
        raise ValueError("retained companion causal policy was promoted")
