"""Exact screen of the equal-connection Berger metric factor ansatz.

This module consumes the dedicated pinned lower-by-two import, the raw metric
endpoint, and the scalar wave from the rank-one prolongation. It tests a deliberately narrow Green
architecture: two invariant-coefficient, scalar-principal second-order
factors with the same first-order (connection) part and arbitrary order-zero
potentials.  Failure of this screen is not a no-go for unequal connections,
first-order reductions, auxiliary fields, or Green hyperbolicity itself.
"""

from __future__ import annotations

import hashlib
from functools import lru_cache
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp

from transfer.berger_gauge_fixed_nonminimal_import import _multiply, _subtract

from . import rank_one_wave_extension_import as EXTENSION
from . import raw_endpoint_import as RAW


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"
CLASSICAL_COMMIT = "db099319b79b7fa9e107347fe24fc534a104c09c"
CLASSICAL_CERTIFICATE = "d_quotient_classical/certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE.json"
METRIC_CONE_COMMIT = "d6c64253442811dcb57df979a6bc3cb4f77e940c"
METRIC_CONE_CERTIFICATE = "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO.json"
METRIC_CONE_SOURCES = (
    METRIC_CONE_CERTIFICATE,
    "d_quotient_classical/backreacted_clock/berger_raw_endpoint_metric_cone_no_go.py",
    "d_quotient_classical/backreacted_clock/tests/test_berger_raw_endpoint_metric_cone_no_go.py",
    "d_quotient_classical/reports/berger-raw-endpoint-metric-cone-no-go.md",
)
CLASSICAL_SOURCES = (
    CLASSICAL_CERTIFICATE,
    "d_quotient_classical/backreacted_clock/berger_metric_lower_by_two_biwave.py",
    "d_quotient_classical/backreacted_clock/tests/test_berger_metric_lower_by_two_biwave.py",
    "d_quotient_classical/reports/berger-metric-lower-by-two-biwave.md",
)
RAW_IMPORT = HERE / "certificates/BERGER_RAW_ENDPOINT_INPUT_IMPORT.json"
EXTENSION_IMPORT = HERE / "certificates/BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION_IMPORT.json"
LOWER_BY_TWO_IMPORT = HERE / "certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORT.json"
PAIR_LABELS = ("h00", "h01", "h02", "h03", "h11", "h12", "h13", "h22", "h23", "h33")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    return _git_blob_at(CLASSICAL_COMMIT, relative)


def _git_blob_at(commit: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{_git_prefix()}{relative}"],
        cwd=ROOT, check=False, capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned lower-by-two artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned lower-by-two JSON is not an object: {relative}")
    return value


def _source_artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }


def _metric_cone_artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": METRIC_CONE_COMMIT,
        "sha256": hashlib.sha256(_git_blob_at(METRIC_CONE_COMMIT, relative)).hexdigest(),
    }


def _load_source_operator(reference: object, name: str) -> list[list[dict[tuple[int, ...], sp.Expr]]]:
    if not isinstance(reference, dict) or set(reference) != {"format", "path", "sha256"}:
        raise ValueError(f"{name} artifact fields drifted")
    body = _git_blob(reference["path"])
    if (
        reference["format"] != "JSON_EXACT_SPARSE_OPERATOR"
        or hashlib.sha256(body).hexdigest() != reference["sha256"]
    ):
        raise ValueError(f"{name} artifact hash or format drifted")
    return RAW._load_rational_record(name, json.loads(body), (10, 10))


def _block(matrix: list[list[Any]], rows: range, columns: range) -> list[list[Any]]:
    return [[matrix[row][column] for column in columns] for row in rows]


def _diagonal(operator: dict[tuple[int, ...], sp.Expr], rank: int) -> list[list[dict[tuple[int, ...], sp.Expr]]]:
    return [
        [dict(operator) if row == column else {} for column in range(rank)]
        for row in range(rank)
    ]


def _polynomial_divide(value: sp.Expr, divisor: sp.Expr, momenta: tuple[sp.Symbol, ...]) -> tuple[sp.Expr, sp.Expr]:
    quotient, remainder = sp.div(
        sp.Poly(sp.factor(value), *momenta, domain="EX"),
        sp.Poly(divisor, *momenta, domain="EX"),
    )
    return sp.factor(quotient.as_expr()), sp.factor(remainder.as_expr())


def _linear_operator_from_symbol(value: sp.Expr, momenta: tuple[sp.Symbol, ...]) -> dict[tuple[int, ...], sp.Expr]:
    polynomial = sp.Poly(value, *momenta, domain="EX")
    if polynomial.total_degree() > 1:
        raise ValueError("subprincipal quotient is not first order")
    output: dict[tuple[int, ...], sp.Expr] = {}
    for monomial, coefficient in polynomial.terms():
        degree = sum(monomial)
        if degree == 0:
            word: tuple[int, ...] = ()
        elif degree == 1 and 1 in monomial:
            word = (monomial.index(1),)
        else:
            raise ValueError("subprincipal quotient is not a linear PBW symbol")
        coefficient = sp.factor(coefficient)
        if coefficient:
            output[word] = coefficient
    return output


@lru_cache(maxsize=1)
def evaluate_screen() -> dict[str, Any]:
    """Return the exact normalized obstruction and its pinned provenance."""

    raw_source = RAW._git_json(RAW.TRANSPORT_CERTIFICATE)
    p34 = RAW._load_artifact(
        raw_source["operators"]["P34_raw"], name="P34_raw", shape=(34, 34)
    )
    metric = _block(p34, range(5, 15), range(5, 15))

    dedicated_import = json.loads(LOWER_BY_TWO_IMPORT.read_text(encoding="utf-8"))
    if (
        dedicated_import.get("result_id") != "BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORT"
        or dedicated_import.get("result_state")
        != "LOWER_BY_TWO_TENSOR_BIWAVE_IMPORTED_CAUSAL_RESOLVENT_OPEN"
        or dedicated_import.get("provenance", {}).get("classical_commit") != CLASSICAL_COMMIT
        or dedicated_import.get("claim_flags", {}).get("BERGER_METRIC_LOWER_BY_TWO_BIWAVE") is not True
        or dedicated_import.get("claim_flags", {}).get("BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS") is not False
        or dedicated_import.get("claim_flags", {}).get("QUANTUM_CLAIM") is not False
        or not all(dedicated_import.get("independent_exact_replay", {}).get("checks", {}).values())
        or dedicated_import.get("next_gate") != "BERGER_LOWER_BY_TWO_CAUSAL_RESOLVENT"
    ):
        raise ValueError("dedicated lower-by-two quantum import drifted")

    classical = _git_json(CLASSICAL_CERTIFICATE)
    if (
        classical.get("schema") != "pure-weyl-berger-metric-lower-by-two-biwave-v1"
        or classical.get("result_id") != "BERGER_METRIC_LOWER_BY_TWO_BIWAVE"
        or classical.get("setting_id") != SETTING_ID
        or classical.get("claim_status")
        != "CERTIFIED_EXACT_NORMAL_FORM_CANONICAL_FACTOR_NO_GO_GREEN_OPEN"
        or classical.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or not all(classical.get("exact_checks", {}).values())
        or classical.get("flags")
        != {
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
            "BERGER_CANONICAL_ROUGH_WAVE_FACTOR_NO_GO": True,
            "BERGER_METRIC_LOWER_BY_TWO_BIWAVE": True,
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS": False,
        }
        or classical.get("next_gate") != "BERGER_LOWER_BY_TWO_CAUSAL_RESOLVENT"
    ):
        raise ValueError("classical lower-by-two identity or claim boundary drifted")
    normal_form = classical.get("normal_form", {})
    if (
        normal_form.get("identity") != "A10=Box_2^2+V_2"
        or normal_form.get("maximum_order_A10") != 4
        or normal_form.get("maximum_order_V2") != 2
        or normal_form.get("order_four_defect") != 0
        or normal_form.get("order_three_defect") != 0
        or normal_form.get("degree_two_symbol_ranks")
        != {"generic": 10, "null": 7, "spacelike": 10, "timelike": 9}
    ):
        raise ValueError("classical lower-by-two normal form drifted")
    obstruction = classical.get("canonical_factor_obstruction", {})
    if (
        obstruction.get("nonzero_degree_two_entries") != 92
        or obstruction.get("nondivisible_degree_two_entries") != 92
        or obstruction.get("left_factorization_ruled_out") != "A10=Box_2 V"
        or obstruction.get("right_factorization_ruled_out") != "A10=V Box_2"
    ):
        raise ValueError("classical canonical-factor obstruction drifted")
    rough_wave = _load_source_operator(normal_form["artifacts"]["rough_tensor_wave"], "Box_2")
    source_remainder = _load_source_operator(
        normal_form["artifacts"]["lower_by_two_remainder"], "V_2"
    )
    if not RAW._is_zero(
        _subtract(_subtract(metric, _multiply(rough_wave, rough_wave)), source_remainder)
    ):
        raise ValueError("pinned A10=Box_2^2+V_2 identity failed")

    extension_source = EXTENSION._git_json(EXTENSION.CERTIFICATE)
    l13 = EXTENSION._load_artifact(
        extension_source["prolongation"]["artifacts"]["prolonged_L13"],
        "L13", (13, 13),
    )
    scalar_wave = {word: -coefficient for word, coefficient in l13[10][12].items()}
    if scalar_wave != {(0, 0): -1, (1, 1): 1, (2, 2): 1, (3, 3): 1}:
        raise ValueError("pinned prolongation scalar wave drifted")

    momenta = sp.symbols("p0:4")
    wave_symbol = -momenta[0] ** 2 + sum(momentum**2 for momentum in momenta[1:])
    scalar_biwave = _multiply([[scalar_wave]], [[scalar_wave]])[0][0]
    metric_minus_biwave = _subtract(metric, _diagonal(scalar_biwave, 10))
    cubic = RAW._homogeneous_symbol(metric_minus_biwave, 3)

    connection = [[{} for _ in range(10)] for _ in range(10)]
    cubic_quotients = sp.zeros(10)
    for row in range(10):
        for column in range(10):
            value = cubic[row, column]
            if value == 0:
                continue
            quotient, remainder = _polynomial_divide(value, 2 * wave_symbol, momenta)
            if remainder != 0:
                raise ValueError("cubic symbol has no equal-connection split")
            connection[row][column] = _linear_operator_from_symbol(quotient, momenta)
            cubic_quotients[row, column] = quotient

    laplace_type = _diagonal(scalar_wave, 10)
    for row in range(10):
        for column in range(10):
            for word, coefficient in connection[row][column].items():
                laplace_type[row][column][word] = sp.factor(
                    laplace_type[row][column].get(word, 0) + coefficient
                )
    quadratic_remainder = _subtract(metric, _multiply(laplace_type, laplace_type))
    if RAW._maximum_order(quadratic_remainder) != 2:
        raise ValueError("equal-connection square did not remove all cubic terms")
    quadratic_symbol = RAW._homogeneous_symbol(quadratic_remainder, 2)
    source_quadratic_symbol = RAW._homogeneous_symbol(source_remainder, 2)
    fixture_values = {
        "timelike": (1, 0, 0, 0),
        "spacelike": (0, 1, 0, 0),
        "null": (1, 1, 0, 0),
        "generic": (2, 3, 5, 7),
    }
    source_ranks = {
        name: int(source_quadratic_symbol.subs(dict(zip(momenta, values, strict=True))).rank())
        for name, values in fixture_values.items()
    }
    if source_ranks != {"timelike": 9, "spacelike": 10, "null": 7, "generic": 10}:
        raise ValueError("independent lower-by-two rank replay failed")
    source_nonzero = [value for value in source_quadratic_symbol if value != 0]
    if len(source_nonzero) != 92 or any(
        sp.rem(sp.factor(value), wave_symbol, momenta[0]) == 0 for value in source_nonzero
    ):
        raise ValueError("independent canonical-factor divisibility replay failed")

    nondivisible_entries: list[dict[str, Any]] = []
    for row in range(10):
        for column in range(10):
            value = quadratic_symbol[row, column]
            if value == 0:
                continue
            _, remainder = _polynomial_divide(value, wave_symbol, momenta)
            if remainder != 0:
                nondivisible_entries.append(
                    {
                        "row": PAIR_LABELS[row],
                        "column": PAIR_LABELS[column],
                        "remainder": str(remainder),
                    }
                )

    witness_entry = sp.factor(quadratic_symbol[0, 3])
    expected_entry = -RAW.U**2 * momenta[0] * momenta[3]
    if witness_entry != expected_entry:
        raise ValueError("normalized h00-to-h03 obstruction entry drifted")
    _, witness_remainder = _polynomial_divide(witness_entry, wave_symbol, momenta)
    normalized_value = sp.factor(
        -sp.Poly(witness_remainder, *momenta, domain="EX").coeff_monomial(
            momenta[0] * momenta[3]
        ) / RAW.U**2
    )
    if normalized_value != 1:
        raise ValueError("dual obstruction witness is not normalized")
    if sp.factor(source_quadratic_symbol[0, 3] - witness_entry) != 0:
        raise ValueError("classical and downstream normalized witnesses disagree")

    metric_cone = json.loads(_git_blob_at(METRIC_CONE_COMMIT, METRIC_CONE_CERTIFICATE))
    if (
        not isinstance(metric_cone, dict)
        or metric_cone.get("schema") != "pure-weyl-berger-raw-endpoint-metric-cone-no-go-v1"
        or metric_cone.get("result_id") != "BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO"
        or metric_cone.get("setting_id") != SETTING_ID
        or metric_cone.get("claim_status")
        != "CERTIFIED_FULL_ENDPOINT_METRIC_CAUSAL_INVERSE_NO_GO_HYBRID_CHAIN_ROUTE_OPEN"
        or metric_cone.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or not all(metric_cone.get("exact_checks", {}).values())
        or metric_cone.get("flags")
        != {
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS": False,
            "BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO": True,
        }
        or metric_cone.get("next_gate")
        != "BERGER_HYBRID_RETAINED_CAUSAL_CHAIN_HOMOTOPY"
    ):
        raise ValueError("metric-cone no-go identity or boundary drifted")
    expected_dependencies = {
        "rank_one_extension": {
            "result_id": "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION",
            "sha256": hashlib.sha256(
                _git_blob_at(METRIC_CONE_COMMIT, EXTENSION.CERTIFICATE)
            ).hexdigest(),
        },
        "metric_normal_form": {
            "result_id": "BERGER_METRIC_LOWER_BY_TWO_BIWAVE",
            "sha256": hashlib.sha256(
                _git_blob_at(METRIC_CONE_COMMIT, CLASSICAL_CERTIFICATE)
            ).hexdigest(),
        },
    }
    if metric_cone.get("dependency_refs") != expected_dependencies:
        raise ValueError("metric-cone no-go dependencies drifted")

    fixture = {
        RAW.U: 3 * sp.sqrt(10) / 20,
        RAW.V: 2 * sp.sqrt(10) / 3,
        RAW.ALPHA_B: 5,
    }
    spatial_norm = sum(momentum**2 for momentum in momenta[1:])
    extra_cone = momenta[0] ** 2 - 2 * spatial_norm
    b = RAW._homogeneous_symbol([[l13[row][11]] for row in range(10)], 1).subs(fixture)
    d = RAW._homogeneous_symbol([[l13[row][10]] for row in range(10)], 2).subs(fixture)
    c = RAW._homogeneous_symbol([[l13[11][column] for column in range(10)]], 3).subs(fixture)
    f = RAW._homogeneous_symbol([[l13[12][column] for column in range(10)]], 2).subs(fixture)
    contractions = {
        "c_b": sp.factor((c * b)[0]),
        "f_d": sp.factor((f * d)[0]),
        "f_b": sp.factor((f * b)[0]),
        "c_d": sp.factor((c * d)[0]),
    }
    bracket = sp.factor(
        (wave_symbol**2 - contractions["c_b"]) * contractions["f_d"]
        + contractions["f_b"] * contractions["c_d"]
    )
    if sp.expand(bracket - sp.Rational(3, 100) * wave_symbol**3 * extra_cone) != 0:
        raise ValueError("independent metric-cone bordered determinant replay failed")
    column_weights = [4] * 10 + [2, 1, 2]
    row_weights = [0] * 10 + [0, 1, 2]
    principal = sp.zeros(13)
    for row in range(13):
        for column in range(13):
            order = column_weights[column] - row_weights[row]
            principal[row, column] = sp.factor(sum(
                coefficient.subs(fixture)
                * sp.prod(momenta[axis] for axis in word)
                for word, coefficient in l13[row][column].items()
                if len(word) == order
            ))
    rank_extra = int(principal.subs({
        momenta[0]: sp.sqrt(2), momenta[1]: 1, momenta[2]: 0, momenta[3]: 0,
    }).rank())
    rank_off = int(principal.subs({
        momenta[0]: 2, momenta[1]: 1, momenta[2]: 0, momenta[3]: 0,
    }).rank())
    if (rank_extra, rank_off) != (12, 13):
        raise ValueError("independent extra-cone rank replay failed")
    if not nondivisible_entries:
        raise ValueError("equal-connection obstruction unexpectedly vanished")

    return {
        "coefficient_domain": "Q(alpha_B,u,v)_PBW",
        "scalar_wave": "Box_0=-e0^2+e1^2+e2^2+e3^2",
        "metric_rows": list(PAIR_LABELS),
        "equal_connection_nonzero_entries": sum(
            bool(entry) for row in connection for entry in row
        ),
        "quadratic_remainder_nondivisible_entry_count": len(nondivisible_entries),
        "normalized_dual_witness": {
            "functional": "-u^-2 coefficient_of(p0*p3) in row h00, column h03",
            "target_space": "quadratic_symbols modulo (zeta^2)*Mat10",
            "representative": str(witness_remainder),
            "value": str(normalized_value),
            "field_content": {"equation_row": "h00", "input_field": "h03"},
            "derivative_content": "one temporal and one e3 derivative",
        },
        "exact_checks": {
            "classical_export_identity_and_boundary_pinned": True,
            "dedicated_lower_by_two_quantum_import_bound": True,
            "classical_artifact_hashes_match": True,
            "A10_equals_Box2_squared_plus_V2": True,
            "source_degree_two_rank_ledger_replayed": True,
            "all_92_source_degree_two_entries_nondivisible": True,
            "metric_cone_export_identity_and_boundary_pinned": True,
            "metric_cone_bordered_determinant_replayed": True,
            "metric_cone_rank_12_off_metric_cone_replayed": True,
            "pinned_scalar_wave_exact": True,
            "metric_principal_equals_scalar_biwave_I10": sp.simplify(
                RAW._homogeneous_symbol(metric, 4) - wave_symbol**2 * sp.eye(10)
            ) == sp.zeros(10),
            "cubic_symbol_has_unique_equal_split": True,
            "equal_connection_square_leaves_order_two": True,
            "quadratic_remainder_not_wave_divisible": True,
            "dual_witness_normalized": True,
        },
        "provenance": {
            "lower_by_two_classical_commit": CLASSICAL_COMMIT,
            "lower_by_two_quantum_import_path": str(LOWER_BY_TWO_IMPORT.relative_to(ROOT)),
            "lower_by_two_quantum_import_sha256": _sha256(LOWER_BY_TWO_IMPORT),
            "lower_by_two_classical_sources": {
                path: _source_artifact(path) for path in CLASSICAL_SOURCES
            },
            "metric_cone_classical_commit": METRIC_CONE_COMMIT,
            "metric_cone_classical_sources": {
                path: _metric_cone_artifact(path) for path in METRIC_CONE_SOURCES
            },
            "raw_classical_commit": RAW.CLASSICAL_COMMIT,
            "extension_classical_commit": EXTENSION.CLASSICAL_COMMIT,
            "raw_operator_sha256": raw_source["operators"]["P34_raw"]["sha256"],
            "extension_operator_sha256": extension_source["prolongation"]["artifacts"]["prolonged_L13"]["sha256"],
            "raw_import_sha256": _sha256(RAW_IMPORT),
            "extension_import_sha256": _sha256(EXTENSION_IMPORT),
        },
    }
