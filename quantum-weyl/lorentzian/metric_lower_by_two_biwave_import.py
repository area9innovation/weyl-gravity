"""Pinned import of the exact lower-by-two Berger metric biwave normal form."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp

from transfer.berger_gauge_fixed_nonminimal_import import (
    _is_zero,
    _multiply,
    _subtract,
)

from . import raw_endpoint_import as RAW


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "db099319b79b7fa9e107347fe24fc534a104c09c"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"
CERTIFICATE = "d_quotient_classical/certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE.json"
TRANSPORT = "d_quotient_classical/certificates/BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT.json"
PRODUCER = "d_quotient_classical/backreacted_clock/berger_metric_lower_by_two_biwave.py"
SOURCE_TEST = "d_quotient_classical/backreacted_clock/tests/test_berger_metric_lower_by_two_biwave.py"
SOURCE_REPORT = "d_quotient_classical/reports/berger-metric-lower-by-two-biwave.md"
SOURCE_FILES = (CERTIFICATE, TRANSPORT, PRODUCER, SOURCE_TEST, SOURCE_REPORT)


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned lower-by-two artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": _sha256_bytes(_git_blob(relative)),
    }


def _require_fields(value: object, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{label} fields drifted")
    return value


def _validate_source(source: dict[str, Any]) -> None:
    _require_fields(
        source,
        {
            "schema",
            "result_id",
            "setting_id",
            "claim_status",
            "dependency_tags",
            "dependency_refs",
            "normal_form",
            "canonical_factor_obstruction",
            "exact_checks",
            "flags",
            "next_gate",
            "claim_boundary",
        },
        "lower-by-two source",
    )
    if (
        source["schema"] != "pure-weyl-berger-metric-lower-by-two-biwave-v1"
        or source["result_id"] != "BERGER_METRIC_LOWER_BY_TWO_BIWAVE"
        or source["setting_id"] != SETTING_ID
        or source["claim_status"]
        != "CERTIFIED_EXACT_NORMAL_FORM_CANONICAL_FACTOR_NO_GO_GREEN_OPEN"
        or source["dependency_tags"] != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise ValueError("lower-by-two source identity drifted")
    if source["dependency_refs"] != {
        "raw_witness_transport": {
            "result_id": "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT",
            "sha256": _sha256_bytes(_git_blob(TRANSPORT)),
        }
    }:
        raise ValueError("lower-by-two source dependency drifted")
    expected_checks = {
        "canonical_left_factor_obstructed",
        "canonical_right_factor_obstructed",
        "complete_PBW_metric_block_imported",
        "lower_by_two_remainder_exact",
        "null_remainder_rank_seven",
        "order_four_coefficients_cancel",
        "order_three_coefficients_cancel",
        "rough_tensor_wave_constructed_covariantly",
    }
    if set(source["exact_checks"]) != expected_checks or not all(
        value is True for value in source["exact_checks"].values()
    ):
        raise ValueError("lower-by-two source exact-check ledger drifted")
    if source["flags"] != {
        "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        "BERGER_CANONICAL_ROUGH_WAVE_FACTOR_NO_GO": True,
        "BERGER_METRIC_LOWER_BY_TWO_BIWAVE": True,
        "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS": False,
    } or source["next_gate"] != "BERGER_LOWER_BY_TWO_CAUSAL_RESOLVENT":
        raise ValueError("lower-by-two lifecycle boundary drifted")

    normal = _require_fields(
        source["normal_form"],
        {
            "identity",
            "Box_2",
            "maximum_order_A10",
            "maximum_order_V2",
            "order_four_defect",
            "order_three_defect",
            "remainder_nonzero_matrix_entries",
            "remainder_entries_by_order",
            "degree_two_symbol_ranks",
            "artifacts",
        },
        "normal form",
    )
    if (
        normal["identity"] != "A10=Box_2^2+V_2"
        or normal["Box_2"]
        != "covariant rough wave on the full symmetric-two-tensor bundle"
        or normal["maximum_order_A10"] != 4
        or normal["maximum_order_V2"] != 2
        or normal["order_four_defect"] != 0
        or normal["order_three_defect"] != 0
        or normal["remainder_nonzero_matrix_entries"] != 98
        or normal["remainder_entries_by_order"]
        != {"0": 22, "1": 40, "2": 92, "3": 0, "4": 0}
        or normal["degree_two_symbol_ranks"]
        != {"timelike": 9, "spacelike": 10, "null": 7, "generic": 10}
    ):
        raise ValueError("lower-by-two normal-form ledger drifted")
    expected_artifact_paths = {
        "rough_tensor_wave": "d_quotient_classical/generated/berger_metric_lower_by_two_biwave/rough_tensor_wave.json",
        "lower_by_two_remainder": "d_quotient_classical/generated/berger_metric_lower_by_two_biwave/lower_by_two_remainder.json",
    }
    if set(normal["artifacts"]) != set(expected_artifact_paths) or any(
        normal["artifacts"][name].get("path") != path
        for name, path in expected_artifact_paths.items()
    ):
        raise ValueError("lower-by-two artifact inventory drifted")
    obstruction = _require_fields(
        source["canonical_factor_obstruction"],
        {
            "scope",
            "left_factorization_ruled_out",
            "right_factorization_ruled_out",
            "reason",
            "nonzero_degree_two_entries",
            "nondivisible_degree_two_entries",
            "not_ruled_out",
        },
        "canonical factor obstruction",
    )
    if (
        obstruction["scope"]
        != "same 10-component symmetric-tensor bundle with one factor fixed to the certified covariant rough wave Box_2 and the other having scalar wave-leading symbol"
        or obstruction["left_factorization_ruled_out"] != "A10=Box_2 V"
        or obstruction["right_factorization_ruled_out"] != "A10=V Box_2"
        or obstruction["reason"]
        != "absence of order-three defect forces V-Box_2 to be order zero, but every nonzero entry of sigma_2(V_2) is nondivisible by the scalar wave polynomial"
        or obstruction["nonzero_degree_two_entries"] != 92
        or obstruction["nondivisible_degree_two_entries"] != 92
        or obstruction["not_ruled_out"]
        != [
            "mixed-bundle factorization",
            "first-order-corrected factors not fixing Box_2",
            "higher-rank local prolongation",
            "causal Volterra or Levi construction",
        ]
    ):
        raise ValueError("canonical factor obstruction scope drifted")


def _load_artifact(reference: object, name: str):
    value = _require_fields(reference, {"format", "path", "sha256"}, name)
    if value["format"] != "JSON_EXACT_SPARSE_OPERATOR":
        raise ValueError(f"{name} artifact format drifted")
    body = _git_blob(value["path"])
    if _sha256_bytes(body) != value["sha256"]:
        raise ValueError(f"{name} artifact hash drifted")
    return RAW._load_rational_record(name, json.loads(body), (10, 10))


def _maximum_order(matrix) -> int:
    return max(
        (len(word) for row in matrix for operator in row for word in operator),
        default=-1,
    )


def _entry_counts(matrix) -> tuple[int, dict[str, int]]:
    nonzero = sum(bool(operator) for row in matrix for operator in row)
    by_order = {
        str(order): sum(
            any(len(word) == order for word in operator)
            for row in matrix
            for operator in row
        )
        for order in range(5)
    }
    return nonzero, by_order


def _degree_two_matrix(matrix):
    return [
        [
            {word: coefficient for word, coefficient in operator.items() if len(word) == 2}
            for operator in row
        ]
        for row in matrix
    ]


def _is_scalar_wave_multiple(operator) -> bool:
    if not operator:
        return True
    allowed = {(0, 0), (1, 1), (2, 2), (3, 3)}
    if set(operator) - allowed:
        return False
    scale = operator.get((1, 1), sp.S.Zero)
    expected = {
        (0, 0): -scale,
        (1, 1): scale,
        (2, 2): scale,
        (3, 3): scale,
    }
    return all(
        sp.factor(operator.get(word, sp.S.Zero) - coefficient) == 0
        for word, coefficient in expected.items()
    )


@lru_cache(maxsize=1)
def fast_receipt() -> dict[str, Any]:
    """Validate the pinned boundary and serialized operators without rebuilding geometry."""

    source = _git_json(CERTIFICATE)
    _validate_source(source)
    artifacts = source["normal_form"]["artifacts"]
    wave = _load_artifact(artifacts["rough_tensor_wave"], "rough_tensor_wave")
    remainder = _load_artifact(
        artifacts["lower_by_two_remainder"], "lower_by_two_remainder"
    )
    nonzero, by_order = _entry_counts(remainder)
    degree_two = _degree_two_matrix(remainder)
    degree_two_nonzero = [operator for row in degree_two for operator in row if operator]
    nondivisible = sum(not _is_scalar_wave_multiple(operator) for operator in degree_two_nonzero)
    checks = {
        "rough_tensor_wave_order_two": _maximum_order(wave) == 2,
        "remainder_order_two": _maximum_order(remainder) == 2,
        "remainder_entry_count_98": nonzero == 98,
        "remainder_order_ledger_reproduced": by_order
        == {"0": 22, "1": 40, "2": 92, "3": 0, "4": 0},
        "degree_two_entries_92": len(degree_two_nonzero) == 92,
        "degree_two_entries_all_nondivisible_by_scalar_wave": nondivisible == 92,
    }
    if not all(checks.values()):
        raise ValueError("fast lower-by-two artifact receipt failed")
    return {
        "checks": checks,
        "operator_hashes": {
            name: artifacts[name]["sha256"]
            for name in ("rough_tensor_wave", "lower_by_two_remainder")
        },
        "source_claim_status": source["claim_status"],
        "next_gate": source["next_gate"],
    }


@lru_cache(maxsize=1)
def replay_receipt() -> dict[str, Any]:
    """Replay the exact normal form and inexpensive rational rank fixtures."""

    source = _git_json(CERTIFICATE)
    _validate_source(source)
    artifacts = source["normal_form"]["artifacts"]
    wave = _load_artifact(artifacts["rough_tensor_wave"], "rough_tensor_wave")
    remainder = _load_artifact(
        artifacts["lower_by_two_remainder"], "lower_by_two_remainder"
    )
    transport = _git_json(TRANSPORT)
    p34 = RAW._load_rational_record(
        "P34_raw",
        json.loads(_git_blob(transport["operators"]["P34_raw"]["path"])),
        (34, 34),
    )
    if _sha256_bytes(_git_blob(transport["operators"]["P34_raw"]["path"])) != transport[
        "operators"
    ]["P34_raw"]["sha256"]:
        raise ValueError("pinned P34_raw artifact hash drifted")
    metric = [[p34[row][column] for column in range(5, 15)] for row in range(5, 15)]
    normal_form_exact = _is_zero(
        _subtract(_subtract(metric, _multiply(wave, wave)), remainder)
    )

    symbol = RAW._homogeneous_symbol(remainder, 2)
    p = sp.symbols("p0:4")
    # The source theorem proves the symbolic ranks.  These independent exact
    # rational fixtures guard the serialized operator without incurring the
    # symbolic-factorization blowup of the geometric producer.
    background = {RAW.U: sp.Rational(2), RAW.V: sp.Rational(3)}
    fixtures = {
        "timelike": (1, 0, 0, 0),
        "spacelike": (0, 1, 0, 0),
        "null": (1, 1, 0, 0),
        "generic": (2, 3, 5, 7),
    }
    ranks = {
        name: int(symbol.subs(background | dict(zip(p, values, strict=True))).rank())
        for name, values in fixtures.items()
    }
    checks = {
        "exact_A10_equals_Box2_squared_plus_V2": normal_form_exact,
        "order_four_and_three_defects_zero": normal_form_exact
        and _maximum_order(remainder) == 2,
        "rational_fixture_rank_ledger_reproduced": ranks
        == {"timelike": 9, "spacelike": 10, "null": 7, "generic": 10},
    }
    if not all(checks.values()):
        raise ValueError("exact lower-by-two replay failed")
    return {
        "checks": checks,
        "rational_background_fixture": {"u": "2", "v": "3"},
        "degree_two_symbol_ranks": ranks,
    }


def build_import() -> dict[str, Any]:
    source = _git_json(CERTIFICATE)
    receipt = fast_receipt()
    replay = replay_receipt()
    dynamic_sources = tuple(
        reference["path"] for reference in source["normal_form"]["artifacts"].values()
    )
    return {
        "schema": "quantum-weyl-berger-metric-lower-by-two-biwave-import-v1",
        "result_id": "BERGER_METRIC_LOWER_BY_TWO_BIWAVE_IMPORT",
        "result_state": "LOWER_BY_TWO_TENSOR_BIWAVE_IMPORTED_CAUSAL_RESOLVENT_OPEN",
        "lifecycle_layer": "CLASSICAL_BV_CAUSAL_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
        "normal_form": source["normal_form"],
        "canonical_factor_obstruction": source["canonical_factor_obstruction"],
        "fast_receipt": receipt,
        "independent_exact_replay": replay,
        "claim_flags": {**source["flags"], "QUANTUM_CLAIM": False},
        "next_gate": "BERGER_LOWER_BY_TWO_CAUSAL_RESOLVENT",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "source_contract_mode": "STRICT_CONSUMER_FIELD_SET",
            "classical_sources": {
                path: _artifact(path) for path in (*SOURCE_FILES, *dynamic_sources)
            },
        },
        "claim_boundary": (
            "Pins and independently replays the exact ten-row identity "
            "A10=Box_2^2+V_2, the order-two remainder ledger, exact rational rank "
            "fixtures, and the scoped obstruction to a fixed canonical rough-wave "
            "factor. It does not construct a causal resolvent, invert the coupled "
            "clock endpoint, produce advanced/retarded Green operators, establish "
            "Hadamard data, restore a QME, or make a quantum claim."
        ),
    }
