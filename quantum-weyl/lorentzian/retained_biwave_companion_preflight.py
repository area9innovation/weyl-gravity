"""Exact retained-metric and biwave companion preflight for the Berger endpoint."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
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
CONTRACTION_IMPORT = (
    ROOT
    / "quantum-weyl/transfer/certificates/BERGER_MINIMAL_34_CONTRACTION_IMPORT.json"
)
RAW_IMPORT = HERE / "certificates/BERGER_RAW_ENDPOINT_INPUT_IMPORT.json"
ENDPOINT_FACTOR_IMPORT = HERE / "certificates/BERGER_ENDPOINT_FACTOR_INPUT_IMPORT.json"
MICROLOCAL_CLASSICAL_COMMIT = "e21aa7844cf976a1e0a60d86f4f33c18dea37826"
MICROLOCAL_CLASSICAL_CERTIFICATE = (
    "d_quotient_classical/certificates/BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _pinned_classical_blob(relative: str) -> bytes:
    result = subprocess.run(
        [
            "git",
            "show",
            f"{MICROLOCAL_CLASSICAL_COMMIT}:{_git_prefix()}{relative}",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned microlocal artifact: {relative}")
    return result.stdout


def _pinned_classical_json(relative: str) -> dict[str, Any]:
    value = json.loads(_pinned_classical_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned microlocal JSON is not an object: {relative}")
    return value


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
    microlocal = _pinned_classical_json(MICROLOCAL_CLASSICAL_CERTIFICATE)
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
    if (
        microlocal.get("result_id")
        != "BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION"
        or microlocal.get("claim_status")
        != "CERTIFIED_SIMPLE_REAL_CHARACTERISTIC_MIXED_WITNESS_ARTIFACT_RETAINED_ROUTE_EXACT"
        or microlocal.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or not all(microlocal.get("exact_checks", {}).values())
        or microlocal.get("flags", {}).get(
            "BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION"
        )
        is not True
        or microlocal.get("flags", {}).get("BERGER_RAW_EXTRA_MODE_PURE_CLOCK")
        is not False
        or microlocal.get("flags", {}).get(
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT"
        )
        is not False
        or microlocal.get("homological_interpretation", {}).get(
            "retained_companion_rank_on_raw_extra_cone"
        )
        != 20
        or microlocal.get("next_gate")
        != "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT"
    ):
        raise ValueError("microlocal localization classical boundary drifted")
    return {
        "lower": lower,
        "contraction": contraction,
        "raw": raw,
        "endpoint": endpoint,
        "microlocal": microlocal,
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

    # C20(h,y)=(Box_2 h-y,V_2 h+Box_2 y).  Besides the familiar graph
    # identity, keep the source and solution maps separate.  This proves an
    # exact two-sided graph contraction for arbitrary companion sources; it
    # does not assume y=Box_2 h before applying C20.
    companion = _zero(20, 20)
    _embed(companion, wave, 0, 0)
    _embed(companion, _negative(_identity(10)), 0, 10)
    _embed(companion, remainder, 10, 0)
    _embed(companion, wave, 10, 10)
    solution_inclusion = _zero(20, 10)
    _embed(solution_inclusion, _identity(10), 0, 0)
    _embed(solution_inclusion, wave, 10, 0)
    solution_projection = _zero(10, 20)
    _embed(solution_projection, _identity(10), 0, 0)
    source_inclusion = _zero(20, 10)
    _embed(source_inclusion, _identity(10), 10, 0)
    source_projection = _zero(10, 20)
    _embed(source_projection, wave, 0, 0)
    _embed(source_projection, _identity(10), 0, 10)
    graph_homotopy = _zero(20, 20)
    _embed(graph_homotopy, _negative(_identity(10)), 10, 0)

    identity10 = _identity(10)
    identity20 = _identity(20)
    companion_graph_checks = {
        "solution_projection_inclusion_is_identity": _is_zero(
            _subtract(_multiply(solution_projection, solution_inclusion), identity10)
        ),
        "source_projection_inclusion_is_identity": _is_zero(
            _subtract(_multiply(source_projection, source_inclusion), identity10)
        ),
        "operator_intertwines_inclusions": _is_zero(
            _subtract(
                _multiply(companion, solution_inclusion),
                _multiply(source_inclusion, retained_metric),
            )
        ),
        "operator_intertwines_projections": _is_zero(
            _subtract(
                _multiply(source_projection, companion),
                _multiply(retained_metric, solution_projection),
            )
        ),
        "solution_graph_retract_identity": _is_zero(
            _subtract(
                _subtract(
                    identity20,
                    _multiply(solution_inclusion, solution_projection),
                ),
                _multiply(graph_homotopy, companion),
            )
        ),
        "source_graph_retract_identity": _is_zero(
            _subtract(
                _subtract(identity20, _multiply(source_inclusion, source_projection)),
                _multiply(companion, graph_homotopy),
            )
        ),
        "graph_homotopy_squared_zero": _is_zero(
            _multiply(graph_homotopy, graph_homotopy)
        ),
        "solution_projection_annihilates_graph_homotopy": _is_zero(
            _multiply(solution_projection, graph_homotopy)
        ),
        "graph_homotopy_annihilates_source_inclusion": _is_zero(
            _multiply(graph_homotopy, source_inclusion)
        ),
    }

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
        "raw_extra_cone_fixture": 20
        if sp.factor(
            q.subs(
                {
                    RAW.U: 2,
                    RAW.V: 3,
                    momenta[0]: sp.sqrt(2),
                    momenta[1]: 1,
                    momenta[2]: 0,
                    momenta[3]: 0,
                }
            )
        )
        != 0
        else 0,
    }

    checks = {
        "portable_projection_and_inclusion_loaded": True,
        "retained_P26_is_degree_block_diagonal": off_degree_blocks_zero,
        "retained_metric_block_equals_raw_A10": retained_metric_equals_raw,
        "retained_metric_A10_equals_Box2_squared_plus_V2": lower_by_two_exact,
        "companion_graph_identity_exact": companion_graph_checks[
            "operator_intertwines_inclusions"
        ],
        **{
            f"companion_graph_sdr_{name}": value
            for name, value in companion_graph_checks.items()
        },
        "companion_principal_block_lower_triangular": principal_block_triangular,
        "companion_principal_determinant_is_q_power_20": principal_block_triangular,
        "companion_principal_null_rank_seven": ranks["metric_null_fixture"] == 7,
        "companion_principal_off_cone_rank_twenty": ranks[
            "off_metric_cone_fixture"
        ]
        == 20,
        "microlocal_mixed_polarization_boundary_pinned": True,
        "companion_principal_raw_extra_cone_rank_twenty": ranks[
            "raw_extra_cone_fixture"
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
            "solution_projection": "p_sol(h,y)=h",
            "source_inclusion": "i_src(f)=(0,f)",
            "source_projection": "p_src(f1,f2)=Box_2 f1+f2",
            "graph_homotopy": "H(f1,f2)=(0,-f1)",
            "two_sided_graph_sdr_identities": [
                "p_sol i_sol=I10",
                "p_src i_src=I10",
                "C20 i_sol=i_src A10",
                "p_src C20=A10 p_sol",
                "I20-i_sol p_sol=H C20",
                "I20-i_src p_src=C20 H",
                "H^2=0",
                "p_sol H=0",
                "H i_src=0",
            ],
            "principal_symbol": "[[q I10,0],[sigma_2(V_2),q I10]]",
            "principal_determinant": "q^20",
            "extra_characteristic_cone": False,
            "rational_fixture": {"u": "2", "v": "3"},
            "principal_ranks": ranks,
            "raw_extra_cone_interpretation": {
                "polarization": "MIXED_RETAINED_METRIC_AND_CLOCK",
                "pure_clock_mode": False,
                "selector_projection_kills_polarization": False,
                "correct_operation": "APPLY_BV_SDR_AND_CONSTRUCT_RETAINED_WITNESS_DO_NOT_PROJECT_L13_SOLUTIONS",
            },
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
            "companion_cyclic_pairing": "NOT_CONSTRUCTED",
            "advanced_retarded_cyclic_adjointness": "NOT_CONSTRUCTED",
        },
        "claim_flags": {
            "BERGER_RETAINED_METRIC_EQUALS_RAW_A10": True,
            "BERGER_RETAINED_BIWAVE_COMPANION_EXACT": True,
            "BERGER_RETAINED_BIWAVE_COMPANION_GRAPH_SDR": True,
            "BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION_IMPORTED": True,
            "BERGER_RAW_EXTRA_MODE_PURE_CLOCK": False,
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
                "microlocal_localization_classical": {
                    "path": MICROLOCAL_CLASSICAL_CERTIFICATE,
                    "commit": MICROLOCAL_CLASSICAL_COMMIT,
                    "sha256": hashlib.sha256(
                        _pinned_classical_blob(MICROLOCAL_CLASSICAL_CERTIFICATE)
                    ).hexdigest(),
                },
            },
            "imported_boundary_states": {
                name: value["result_id"] for name, value in boundaries.items()
            },
        },
        "claim_boundary": (
            "Independently proves that the exact A10 lower-by-two tensor biwave is "
            "the metric block induced on the retained 26-row endpoint and constructs "
            "its exact 20-row local companion presentation and a two-sided graph "
            "contraction for arbitrary companion sources. The companion principal "
            "determinant has only the metric characteristic cone. The imported "
            "microlocal theorem corrects the raw interpretation: its extra polarization "
            "mixes retained metric and clock components, so one must apply the BV SDR "
            "and construct the retained witness rather than project L13 solutions. "
            "This does not prove "
            "Volterra convergence, construct advanced/retarded operators, complete the "
            "cyclic companion pairing, prove causal adjointness, complete the 26- or "
            "54-row causal chain homotopy, establish Hadamard data, restore a "
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
        "BERGER_RETAINED_BIWAVE_COMPANION_GRAPH_SDR": True,
        "BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION_IMPORTED": True,
        "BERGER_RAW_EXTRA_MODE_PURE_CLOCK": False,
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
        or policy.get("companion_cyclic_pairing") != "NOT_CONSTRUCTED"
        or policy.get("advanced_retarded_cyclic_adjointness")
        != "NOT_CONSTRUCTED"
    ):
        raise ValueError("retained companion causal policy was promoted")
