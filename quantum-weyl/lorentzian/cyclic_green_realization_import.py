"""Pinned independent import of the 36-row cyclic Berger Green realization."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from local_bv.schema_validation import validate_instance
from transfer.berger_gauge_fixed_nonminimal_import import (
    _adjoint_transpose,
    _identity,
    _is_zero,
    _multiply,
    _subtract,
)

from . import rank_one_wave_extension_import as EXTENSION
from . import raw_endpoint_import as RAW


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "e415ba39c102ede59300cac64c44a2a1a298c88e"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"
CERTIFICATE = "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION.json"
SCHEMA = "d_quotient_classical/schema/berger-raw-endpoint-cyclic-green-realization-v1.schema.json"
TRANSPORT = "d_quotient_classical/certificates/BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT.json"
EXTENSION_CERTIFICATE = "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION.json"
SOURCE_FILES = (
    CERTIFICATE,
    SCHEMA,
    TRANSPORT,
    EXTENSION_CERTIFICATE,
    "d_quotient_classical/backreacted_clock/berger_raw_endpoint_cyclic_green_realization.py",
    "d_quotient_classical/backreacted_clock/verify_berger_raw_endpoint_cyclic_green_realization.py",
    "d_quotient_classical/backreacted_clock/tests/test_berger_raw_endpoint_cyclic_green_realization.py",
    "d_quotient_classical/reports/berger-raw-endpoint-cyclic-green-realization.md",
)
QUANTUM_EXTENSION_IMPORT = HERE / "certificates/BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION_IMPORT.json"


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
    if result.returncode:
        raise ValueError(f"missing pinned cyclic-realization artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _artifact(relative: str) -> dict[str, str]:
    return {"path": relative, "commit": CLASSICAL_COMMIT, "sha256": _sha256_bytes(_git_blob(relative))}


def _load_artifact(reference: object, name: str, shape: tuple[int, int]):
    if not isinstance(reference, dict) or set(reference) != {"format", "path", "sha256"}:
        raise ValueError(f"{name} artifact fields drifted")
    body = _git_blob(reference["path"])
    if reference["format"] != "JSON_EXACT_SPARSE_OPERATOR" or _sha256_bytes(body) != reference["sha256"]:
        raise ValueError(f"{name} artifact hash or format drifted")
    return RAW._load_rational_record(name, json.loads(body), shape)


def _block(matrix, rows: range, columns: range):
    return [[matrix[row][column] for column in columns] for row in rows]


def _constant_rank(matrix) -> int:
    import sympy as sp
    if any(word for row in matrix for entry in row for word in entry):
        raise ValueError("analytic pairing is not order zero")
    return sp.Matrix([[entry.get((), 0) for entry in row] for row in matrix]).rank()


def validate_import(source: dict[str, Any], schema: dict[str, Any], extension_import: dict[str, Any]) -> dict[str, bool]:
    errors = validate_instance(source, schema)
    if errors:
        raise ValueError(f"cyclic realization source schema validation failed: {errors}")
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("additionalProperties") is not False
        or source.get("result_id") != "BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION"
        or source.get("claim_status") != "CERTIFIED_CYCLIC_ANALYTIC_REALIZATION_GREEN_OPEN"
        or source.get("setting_id") != SETTING_ID
        or source.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise ValueError("cyclic realization source identity drifted")
    expected_refs = {
        "raw_witness_transport": {"result_id": "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT", "sha256": _sha256_bytes(_git_blob(TRANSPORT))},
        "rank_one_wave_extension": {"result_id": "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION", "sha256": _sha256_bytes(_git_blob(EXTENSION_CERTIFICATE))},
    }
    if source.get("dependency_refs") != expected_refs:
        raise ValueError("cyclic realization dependency hashes drifted")
    if source.get("flags") != {
        "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        "BERGER_ARITY_TWO_CAUSAL_D_CARTAN": False,
        "BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION": True,
        "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS": False,
    } or source.get("next_gate") != "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS":
        raise ValueError("cyclic realization lifecycle boundary drifted")
    if (
        extension_import.get("result_id") != "BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION_IMPORT"
        or extension_import.get("claim_flags", {}).get("BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION") is not True
        or extension_import.get("claim_flags", {}).get("BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS") is not False
    ):
        raise ValueError("rank-one extension quantum dependency drifted")

    artifacts = source["artifacts"]
    shapes = {
        "analytic_P36": (36, 36), "analytic_pairing36": (36, 36),
        "field_solution_inclusion": (13, 12), "field_solution_projection": (12, 13),
        "field_source_inclusion": (13, 12), "field_source_projection": (12, 13),
        "graph_homotopy_H13": (13, 13), "metric_antifield_L13_sharp": (13, 13),
    }
    matrices = {name: _load_artifact(artifacts[name], name, shape) for name, shape in shapes.items()}
    extension_source = EXTENSION._git_json(EXTENSION.CERTIFICATE)
    l13 = EXTENSION._load_artifact(
        extension_source["prolongation"]["artifacts"]["prolonged_L13"],
        "L13", (13, 13),
    )
    transport = RAW._git_json(RAW.TRANSPORT_CERTIFICATE)
    p34 = RAW._load_artifact(transport["operators"]["P34_raw"], name="P34_raw", shape=(34, 34))
    l12 = _block(p34, range(5, 17), range(5, 17))
    i_sol, p_sol = matrices["field_solution_inclusion"], matrices["field_solution_projection"]
    i_src, p_src = matrices["field_source_inclusion"], matrices["field_source_projection"]
    homotopy = matrices["graph_homotopy_H13"]
    p36, pairing36 = matrices["analytic_P36"], matrices["analytic_pairing36"]
    checks = {
        "solution_identity": _is_zero(_subtract(_multiply(p_sol, i_sol), _identity(12))),
        "source_identity": _is_zero(_subtract(_multiply(p_src, i_src), _identity(12))),
        "solution_intertwining": _is_zero(_subtract(_multiply(l13, i_sol), _multiply(i_src, l12))),
        "source_intertwining": _is_zero(_subtract(_multiply(p_src, l13), _multiply(l12, p_sol))),
        "field_graph_homotopy": _is_zero(_subtract(_subtract(_identity(13), _multiply(i_sol, p_sol)), _multiply(homotopy, l13))),
        "source_graph_homotopy": _is_zero(_subtract(_subtract(_identity(13), _multiply(i_src, p_src)), _multiply(l13, homotopy))),
        "metric_antifield_formal_adjoint": _is_zero(_subtract(matrices["metric_antifield_L13_sharp"], _adjoint_transpose(l13))),
        "analytic_pairing_nondegenerate": _constant_rank(pairing36) == 36,
        "analytic_P36_cyclic": _is_zero(_subtract(_multiply(_adjoint_transpose(p36), pairing36), _multiply(pairing36, p36))),
        "authoritative_ghost_block_unchanged": _is_zero(_subtract(_block(p36, range(0, 5), range(0, 5)), _block(p34, range(0, 5), range(0, 5)))),
        "authoritative_identity_block_unchanged": _is_zero(_subtract(_block(p36, range(31, 36), range(31, 36)), _block(p34, range(29, 34), range(29, 34)))),
    }
    if not all(checks.values()):
        raise ValueError("an independent cyclic realization identity failed")
    policy = source["causal_policy"]
    if (
        policy.get("spatial_zero_mode_projector") is not False
        or policy.get("conditional_green_formula") != "G13_pm=C13 (G12_pm direct_sum I1) E13"
        or policy.get("conditional_pullback_formula") != "G12_pm=p_sol G13_pm i_src"
    ):
        raise ValueError("cyclic realization causal policy drifted")
    return checks


def build_import() -> dict[str, Any]:
    source = _git_json(CERTIFICATE)
    extension_import = json.loads(QUANTUM_EXTENSION_IMPORT.read_text())
    checks = validate_import(source, _git_json(SCHEMA), extension_import)
    return {
        "schema": "quantum-weyl-berger-cyclic-green-realization-import-v1",
        "result_id": "BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION_IMPORT",
        "result_state": "CYCLIC_36_ROW_ANALYTIC_REALIZATION_IMPORTED_GREEN_OPERATORS_OPEN",
        "lifecycle_layer": "CLASSICAL_BV_CAUSAL_PREFLIGHT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
        "row_layout": source["row_layout"],
        "graph_SDR": source["graph_SDR"],
        "cyclic_green_target": {
            "pairing": source["cyclic_realization"]["pairing"],
            "adjoint_identity": source["cyclic_realization"]["green_adjoint_target"],
            "spatial_zero_mode_projector": False,
        },
        "independent_exact_checks": checks,
        "claim_flags": {**source["flags"], "QUANTUM_CLAIM": False},
        "next_gate": "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "classical_sources": {path: _artifact(path) for path in SOURCE_FILES},
            "rank_one_extension_import": {"path": str(QUANTUM_EXTENSION_IMPORT.relative_to(ROOT)), "sha256": hashlib.sha256(QUANTUM_EXTENSION_IMPORT.read_bytes()).hexdigest()},
            "operator_artifacts": source["artifacts"],
        },
        "claim_boundary": (
            "Pins and independently replays the 36-row cyclic analytic realization, its field/source "
            "graph SDR, formal-adjoint antifield block, nondegenerate pairing, and cyclic analytic "
            "operator. The added y,y* rows are analytic graph variables, not new BV cohomology. "
            "No advanced/retarded inverse, causal homotopy, Hadamard state, D-Cartan realization, QME, or quantum result is constructed."
        ),
    }
